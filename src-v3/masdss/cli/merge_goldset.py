"""WP2 — Hop nhat hai ban gan nhan DOC LAP thanh mot bo nhan chuan.

Chay:
    python -m masdss.cli.merge_goldset --a <A>.csv --b <B>.csv --rule union

Phuc vu: RQ3 (moi con so quy ket deu cham diem tren dau ra cua buoc nay).

VI SAO BUOC NAY TON TAI RIENG. `build_goldset` nhan DUNG MOT tep va chuan hoa no.
Truoc 13/08 dieu do la dung: hai tep `_A_en` va `_B_en` cua vong 3 co CUNG NGUON
(L26) nen gop chung lai chi tao ve ngoai cua hai y kien doc lap. Voi bo `v3_final`
thi khac — `check_validation` da xac nhan chung DOC LAP (hang nhan trung khop
77,7%, so voi 96,4% cua vong 3 da bi chan). Da doc lap thi phai hop nhat, va phep
hop nhat phai la mot artifact tai lap duoc chu khong phai vai dong go tay.

HAI QUY TAC, va viec chon quy tac nao la QUYET DINH PHUONG PHAP phai khai bao o
Chuong 4 chu khong phai chi tiet cai dat:

    union (HOP)  nhan duong neu IT NHAT MOT nguoi danh dau
    inter (GIAO) nhan duong chi khi CA HAI danh dau

CAN CU CHON `union` cho bo v3_final — do tren chinh 67 dong bat dong:

    mot ben `unknown`, ben kia tim ra nguyen nhan   36 (53,7%)
    cung huong, khac so luong nhan                  29 (43,3%)
    quy ket KHAC HAN nhau                            2 ( 3,0%)

    Chi 3,0% la xung dot that. 97% con lai la mot nguoi THAY thu nguoi kia khong
    thay, va do la che do hong da biet cua nhiem vu nay: codebook §1.2 canh bao
    dung dieu do — *"quet het cau truoc khi ket luan unknown"* — sau khi vong 1 phat
    hien 23,7% dong duoc CA HAI cung gan `unknown` trong khi van ban co nguyen nhan
    neu tuong minh.

    Voi mot nhiem vu ma che do hong chinh la BO SOT chu khong phai gan thua, hop
    la uoc luong su that tot hon giao.

GIOI HAN PHAI GHI VAO THREATS TO VALIDITY: voi 2 dong xung dot that, `union` gan
CA HAI nhan mau thuan. Con so do nho (0,67% bo nhan) nhung phai duoc neu chu khong
duoc lam tron xuong khong.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from masdss.config import CONFIG
from masdss.data.labels import CAUSE_COLUMNS

KEY = "order_id"
ALL_LABELS = (*CAUSE_COLUMNS, "cause_unknown")


class MergeError(RuntimeError):
    """Hai ban gan nhan khong ghep duoc — phai sua truoc khi hop nhat."""


def _doc(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, encoding="utf-8-sig")
    thieu = {KEY, *ALL_LABELS} - set(frame.columns)
    if thieu:
        raise MergeError(f"{path.name} thieu cot {sorted(thieu)}")
    return frame.set_index(KEY).sort_index()


def phan_loai_bat_dong(a: pd.DataFrame, b: pd.DataFrame) -> dict:
    """Ban chat cua tung dong bat dong — quyet dinh phai sua QUY TRINH hay CODEBOOK.

    Vong 1 cho 75,2% / 17,8% / 6,9%. Ty le "quy ket khac han" thap nghia la dinh
    nghia nguyen nhan vung; ty le "bo sot" cao nghia la quy trinh doc con so ho.
    """
    cols = list(CAUSE_COLUMNS)
    ca, cb = a[cols].astype(int), b[cols].astype(int)
    khac = (a[list(ALL_LABELS)].astype(int) != b[list(ALL_LABELS)].astype(int)).any(axis=1)
    na, nb = ca.sum(axis=1), cb.sum(axis=1)
    chung = (ca & cb).sum(axis=1)
    return {
        "n_dong": int(len(a)),
        "n_bat_dong": int(khac.sum()),
        "ty_le_bat_dong": round(float(khac.mean()), 4),
        "bo_sot_bang_chung": int((khac & (((na == 0) & (nb > 0)) | ((nb == 0) & (na > 0)))).sum()),
        "cung_huong_khac_so_luong": int((khac & (na > 0) & (nb > 0) & (chung > 0)).sum()),
        "quy_ket_khac_han": int((khac & (na > 0) & (nb > 0) & (chung == 0)).sum()),
    }


def hop_nhat(a: pd.DataFrame, b: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Hop nhat hai ban. `cause_unknown` duoc TINH LAI, khong hop truc tiep.

    Hop `cause_unknown` truc tiep se sinh ra dong vua co nguyen nhan vua `unknown` —
    mot trang thai vo nghia. No la HE QUA (khong nhan nao duong), khong phai mot
    nhan doc lap.
    """
    cols = list(CAUSE_COLUMNS)
    ca, cb = a[cols].astype(bool), b[cols].astype(bool)
    if rule == "union":
        out = (ca | cb).astype(int)
    elif rule == "inter":
        out = (ca & cb).astype(int)
    else:
        raise MergeError(f"quy tac khong biet: {rule!r}")
    out["cause_unknown"] = (out[cols].sum(axis=1) == 0).astype(int)

    giu = [c for c in ("sample_id", "tier", "rating") if c in a.columns]
    return a[giu].join(out).reset_index()


def main() -> None:
    goldset = CONFIG.paths.derived / "goldset"
    ap = argparse.ArgumentParser(description="Hop nhat hai ban gan nhan doc lap")
    ap.add_argument("--a", type=Path, required=True)
    ap.add_argument("--b", type=Path, required=True)
    ap.add_argument("--rule", default="union", choices=["union", "inter"])
    ap.add_argument("--out", type=Path, default=goldset / "gold_merged.csv")
    args = ap.parse_args()

    a, b = _doc(args.a), _doc(args.b)
    if len(a) != len(b) or not (a.index == b.index).all():
        raise MergeError("hai ban khong cung tap `order_id` — khong ghep duoc")

    bao_cao = phan_loai_bat_dong(a, b)
    merged = hop_nhat(a, b, args.rule)
    merged.to_csv(args.out, index=False, encoding="utf-8-sig")

    meta = {
        "nguon_a": args.a.name, "nguon_b": args.b.name,
        "quy_tac": args.rule,
        "bat_dong": bao_cao,
        "tong_nhan": {c: int(merged[c].sum()) for c in ALL_LABELS},
        "da_nguyen_nhan": int((merged[list(CAUSE_COLUMNS)].sum(axis=1) >= 2).sum()),
        "canh_bao": (
            f"{bao_cao['quy_ket_khac_han']} dong la XUNG DOT THAT; voi quy tac "
            f"`{args.rule}` chung nhan " +
            ("CA HAI nhan mau thuan" if args.rule == "union" else "KHONG nhan nao") +
            ". Phai neu o Threats to Validity."),
    }
    (args.out.with_name(args.out.stem + "_meta.json")).write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Hai ban: {bao_cao['n_dong']} dong · bat dong {bao_cao['n_bat_dong']} "
          f"({bao_cao['ty_le_bat_dong']:.1%})")
    print(f"  bo sot bang chung        : {bao_cao['bo_sot_bang_chung']}")
    print(f"  cung huong khac so luong : {bao_cao['cung_huong_khac_so_luong']}")
    print(f"  quy ket KHAC HAN         : {bao_cao['quy_ket_khac_han']}  <-- xung dot that")
    print(f"\nQuy tac `{args.rule}` -> {meta['tong_nhan']}")
    print(f"  da nguyen nhan: {meta['da_nguyen_nhan']}")
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
