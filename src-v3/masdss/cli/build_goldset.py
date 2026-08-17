"""WP2 / T2.7 — Dung artifact gold set tu phieu gan nhan.

Dau ra: `data/v3/goldset/gold_labels.csv` + `gold_labels_meta.json`.

HAI DIEU MODULE NAY LAM MA MOT LENH `pd.read_csv` KHONG LAM.

  1. GAN NGUON GOC. Tep meta ghi lai nhan nay tu dau ra, va `Provenance` duoc
     truyen xuong moi phep do phia sau. Bo nhan hien tai do mot mo hinh ngon ngu
     sinh va nguoi ra soat, nen no la MODEL_ASSISTED_PROVISIONAL: dung duoc de
     chay het chu trinh, KHONG duoc trich vao Chuong 5 (L26).

     Khi vong gan nhan doc lap 2-3 nguoi xong, doi mot tham so `--provenance`
     la toan bo chuoi phia sau tu doi trang thai. Khong sua mot dong logic nao.

  2. CHUAN HOA CO GHI CHEP. Mot so dong vi pham quy tac dinh dang cua codebook.
     Chung duoc chuan hoa theo luat CO DINH, va moi dong bi dong vao deu duoc
     LIET KE ra man hinh va ghi vao tep meta — khong sua lang le tep goc cua
     nguoi gan.

VE VIEC CHON MOT TRONG HAI TEP. Hai tep `_A_en` va `_B_en` co cung nguon (L26),
nen gop chung lai bang phep hop hay giao deu la tu lua: no tao ve ngoai cua hai
y kien doc lap. Module nay lay MOT tep lam chinh va noi ro dieu do.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from masdss.config import CONFIG
from masdss.data.labels import CAUSE_COLUMNS, Provenance

ALL_LABELS = (*CAUSE_COLUMNS, "cause_unknown")

# Nhan cu, da bi go khoi he phan loai (12/08). Xem `core/ontology.Cause`.
LEGACY_PRICE = "cause_price"


def meta_path(gold_path: Path) -> Path:
    """Duong dan tep meta di kem MOT tep gold set cu the."""
    return gold_path.with_name(gold_path.stem + "_meta.json")


def normalize(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Ap luat chuan hoa co dinh, tra ve ca danh sach dong da dong vao.

    Luat 1 — `unknown` cung voi nguyen nhan cu the thi BO `unknown`.
        Codebook cam to hop nay. Chon bo `unknown` chu khong bo nguyen nhan vi
        nguyen nhan cu the mang nhieu thong tin hon, va vi ghi chu cua chinh dong
        do thuong da neu ten nguyen nhan. Vi du that: G0022.

    Luat 2 — khong nhan nao duoc dat thi dat `unknown = 1`.
        Mot dong trong khong phai "khong co nguyen nhan"; no la "chua quy ket
        duoc", va do dung la nghia cua `unknown`.
    """
    out = frame.copy()
    for column in (*ALL_LABELS, LEGACY_PRICE):
        # Cot vang mat phai duoc dung thanh cot khong, khong duoc de `out.get()` tra
        # `None` roi di tiep: `pd.to_numeric(None)` cho ra mot scalar NaN, va `.fillna`
        # tren scalar la loi. Truong hop nay xay ra that voi moi tep gan nhan sinh sau
        # khi `cause_price` bi go (12/08) — tuc voi MOI bo nhan tu nay ve sau.
        if column not in out.columns:
            out[column] = 0
        out[column] = pd.to_numeric(out[column], errors="coerce").fillna(0).astype(int)

    changes: list[dict] = []

    # --- Luat 0: dinh tuyen `cause_price` cu ---
    #
    # `price` bi go vi he phan loai dat sai, khong vi co mau nho: khach da xac nhan
    # mua nen da dong y voi gia niem yet, va 10/12 dong duoc gan `price` thuc ra than
    # ve PHI VAN CHUYEN — tra tien ship roi van phai tu ra buu dien lay hang.
    #
    # 10/12 dong da co san nhan khac nen chi bo `price` di la du. Hai dong con lai
    # (G0210, G0299) la than phi van chuyen THUAN TUY, khong co nhan nao khac, nen
    # chung ve DELIVERY theo quy tac 7 cua codebook.
    #
    # Dinh tuyen tinh vi hon — phan biet "khong dang tien" (QUALITY) voi "doi hoan
    # phi khong ai tra loi" (SERVICE) — phai do NGUOI GAN doc cau ma quyet, khong the
    # suy tu cot nhan. Vong gan nhan moi da bo han cot `price` nen khong con van de.
    price = out[LEGACY_PRICE] == 1
    orphan = price & (out[list(CAUSE_COLUMNS)].sum(axis=1) == 0)
    for sample_id in out.loc[orphan, "sample_id"]:
        changes.append({"sample_id": str(sample_id), "luat": 0,
                        "mo_ta": "`price` cu, khong co nhan khac -> `delivery` "
                                 "(than phi van chuyen)"})
    out.loc[orphan, "cause_delivery"] = 1
    for sample_id in out.loc[price & ~orphan, "sample_id"]:
        changes.append({"sample_id": str(sample_id), "luat": 0,
                        "mo_ta": "`price` cu, da co nhan khac -> bo `price`"})
    out = out.drop(columns=[LEGACY_PRICE])

    specific = out[list(CAUSE_COLUMNS)].sum(axis=1)
    conflict = (out["cause_unknown"] == 1) & (specific > 0)
    for sample_id in out.loc[conflict, "sample_id"]:
        changes.append({"sample_id": str(sample_id), "luat": 1,
                        "mo_ta": "bo `unknown` vi dong da co nguyen nhan cu the"})
    out.loc[conflict, "cause_unknown"] = 0

    empty = (out[list(ALL_LABELS)].sum(axis=1) == 0)
    for sample_id in out.loc[empty, "sample_id"]:
        changes.append({"sample_id": str(sample_id), "luat": 2,
                        "mo_ta": "dat `unknown` vi dong khong co nhan nao"})
    out.loc[empty, "cause_unknown"] = 1

    return out, changes


def main() -> None:
    goldset = CONFIG.paths.derived / "goldset"
    parser = argparse.ArgumentParser(description="Dung artifact gold set")
    parser.add_argument("--source", type=Path,
                        default=goldset / "gold_annotation_A_en.csv")
    parser.add_argument("--provenance", default=Provenance.MODEL_ASSISTED_PROVISIONAL.value,
                        choices=[p.value for p in Provenance],
                        help="nhan nay tu dau ra — quyet dinh so co trich duoc khong")
    parser.add_argument("--out", type=Path, default=goldset / "gold_labels.csv")
    args = parser.parse_args()

    provenance = Provenance(args.provenance)
    frame = pd.read_csv(args.source, encoding="utf-8-sig")
    normalized, changes = normalize(frame)

    keep = ["sample_id", "order_id", "tier", "rating", *ALL_LABELS]
    if "tier" not in normalized.columns:
        normalized["tier"] = "A"
    normalized[keep].to_csv(args.out, index=False, encoding="utf-8-sig")

    meta = {
        "source_file": args.source.name,
        "provenance": provenance.value,
        "citable": provenance.citable,
        "n_rows": int(len(normalized)),
        "n_normalized": len(changes),
        "normalizations": changes,
        "label_totals": {c: int(normalized[c].sum()) for c in ALL_LABELS},
        "note": (
            "Nguon la ban DA HOP NHAT tu hai nguoi gan doc lap. Tinh doc lap duoc "
            "kiem TRUOC khi tinh kappa bang `check_validation`; quy tac hop nhat va "
            "phan loai bat dong nam o `gold_merged_meta.json`."
            if provenance is Provenance.HUMAN_INDEPENDENT else
            "Hai tep _A_en va _B_en cua vong 3 co CUNG NGUON (L26); chi mot tep duoc "
            "dung lam chinh. Gop chung lai se tao ve ngoai cua hai y kien doc lap "
            "trong khi chung khong doc lap."),
    }
    # Ten tep meta bam theo ten tep gold. Truoc day no bi dat cung la
    # `gold_labels_meta.json`, nen dung `--out` de tao mot gold set thu hai se ghi
    # de meta cua gold set thu nhat — va lan chay sau doc phai nguon goc SAI.
    # Voi co che `Provenance`, mot meta lech nguon goc la loi nguy hiem nhat co the
    # xay ra: no bien so tam thanh so trich dan duoc ma khong ai thay.
    meta_path(args.out).write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Nguon      : {args.source.name}")
    print(f"Nguon goc  : {provenance.value}")
    print(f"  {provenance.banner}")
    print(f"So dong    : {len(normalized)}")
    print(f"Phan bo nhan: " + "  ".join(
        f"{c.replace('cause_','')}={normalized[c].sum()}" for c in ALL_LABELS))
    if changes:
        print(f"\nDa chuan hoa {len(changes)} dong (tep goc KHONG bi sua):")
        for change in changes:
            print(f"  {change['sample_id']}  luat {change['luat']} — {change['mo_ta']}")
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
