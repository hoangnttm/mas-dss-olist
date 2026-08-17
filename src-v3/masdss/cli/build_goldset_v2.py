"""WP2 / T2.10 — Rut mau gan nhan vong CUOI: 300 dong, phan tang, tu ky TEST.

    python -m masdss.cli.build_goldset_v2

BA DIEU KIEN LAY MAU, ca ba deu MIEN PHI neu quyet truoc khi gan, va KHONG SUA
DUOC sau khi da gan xong. Do la ly do tep nay ton tai thay vi mot lenh `sample()`.

  1. CHI LAY TU KY TEST — CUONG CHE BANG TEP, KHONG BANG LOI DAN.
     Bo nhan hien tai co 199/250 dong nam trong ky train, nen mo hinh rui ro la
     TRONG MAU voi chung — danh gia chuoi hai tang dau-cuoi khong hop le.

     Ban truoc cua tep nay tu goi `build_order_table()` roi `time_split()` de lay
     ky test. Cach do dung nhung KHONG cuong che duoc gi: no chi lap lai phep chia,
     va mot thay doi ty le chia o cho khac se lam lech am tham. Nay mau duoc rut tu
     `goldset_pool.parquet` — tep do CHI chua don thuoc `t3_test`, va co mot test
     bat bien kiem `goldset ⊆ t3_test`.

  2. PHAN TANG THEO `delivery_state` TAI MOC MOI.
     O moc `ngay mua + 7`, ho ung vien (bat man, ky test, co van ban) phan bo rat
     lech: 45 / 768 / 295 don. Lay ngau nhien deu se cho khoang 4 don o tang 0.

     Tang 0 — GIAO NHANH MA VAN BAT MAN — la tang thua it nhat nhung mang nhieu
     thong tin nhat: khi hang den dung han ma khach van cham 1-2 sao, nguyen nhan
     gan nhu chac chan KHONG phai giao hang. Do dung la nhom `quality`/`service`
     ma rang buoc C5 noi la khong quan sat truoc T4 duoc. Lay TRON ca 45 don.

  3. KEM TRONG SO.
     Phan tang lam ty le nen trong mau KHAC ty le nen cua tong the. Moi chi so bao
     cao o muc TONG THE phai nhan trong so, neu khong no bi thoi phong. Trong so
     duoc ghi thang vao tep va vao meta.

VE TINH DOC LAP CUA HAI NGUOI GAN (loi L26). Hai tep sinh ra CO CUNG cac dong va
CUNG thu tu, nhung KHONG tep nao duoc dien san nhan, ghi chu hay do tin cay. Vong
truoc that bai vi ca hai tep cung mot nguon: ghi chu trung 96,4%, va kappa 0,957
khong do duoc gi. `cli/check_validation.py` se kiem tinh doc lap TRUOC khi tinh
kappa — no da chan dung hai tep vong truoc.

VE CO MAU. 300 dong cho:

    precision moi nguyen nhan duoc ket nap   ±0,15 voi 43 dong, ±0,10 voi 97
    recall `delivery` / `quality` / `service`  du o muc ±0,15 cho CA BA

Sau khi go `price` (12/08), ca ba nguyen nhan con lai deu co >= 47 mau duong tren
250 dong cu, nen 300 dong la du cho toan bo ke hoach danh gia — khong con hang muc
nao phai bao cao la "khong danh gia duoc".
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from masdss.config import CONFIG

# Phan bo theo tang, hieu chinh cho moc `ngay mua + 7`.
#
# Ho ung vien: 45 / 768 / 295 don. Bon rang buoc dinh ra bo ba duoi day:
#   - tang 0 chi co 45 don      -> lay TRON, khong the lay hon
#   - moi tang can n >= 43      -> du cho uoc luong rieng tung tang
#   - trong so khong duoc lech  -> hieu qua thiet ke 0,914 (n hieu dung ~274/300)
#   - tang 2 gan nhu thuan `delivery` -> lay it hon tang 1 vi it thong tin moi hon
#
# Ban truoc la {0: 140, 1: 90, 2: 70}, hieu chinh cho moc CU (han du kien + 3) noi
# tang 0 con doi dao. O moc moi no doi hoi 140 don tu mot tang chi co 45.
ALLOCATION = {0: 45, 1: 185, 2: 70}

# Trang thai TAI MOC T3 = ngay mua + 7 — day la thu HE THONG nhin thay.
# Ket cuc cuoi cung nam o mot cot rieng: hai thu nay khac nhau, va nguoi gan can
# ca hai. Vi du: mot don "dang van chuyen" tai moc co the ve muon 40 ngay sau, hoac
# khong bao gio ve.
#
# KHONG dung chu "QUA HAN" o day nua. O moc `ngay mua + 7`, chi 0,21% don da qua
# han giao cam ket — nhan cu se noi sai voi nguoi gan ve thu ho dang doc.
STATE_LABEL = {
    0: "da giao xong trong 7 ngay dau",
    1: "chua toi tay khach - da roi kho nguoi ban",
    2: "chua toi tay khach - nguoi ban CHUA gui hang",
}

# Cot bang chung cho nguoi gan. Nguoi gan duoc thay TOAN BO thong tin, ke ca ket
# cuc giao hang — vi nhan vang la "nguyen nhan THAT SU la gi", mot thuoc tinh cua
# don hang. Rang buoc moc quyet dinh ap len HE THONG, khong ap len nguoi gan.
EVIDENCE_COLUMNS = (
    "category", "trang_thai_tai_moc_T3", "ket_cuc_cuoi_cung",
    "delivery_delay_days", "delivery_days",
    "carrier_handover_days", "ships_in_days", "seller_distance_km",
    "price", "freight_value", "freight_ratio", "n_items",
)
# BA nguyen nhan, khong con `cause_price` (go 12/08 — xem `core/ontology.Cause`).
LABEL_COLUMNS = ("cause_delivery", "cause_quality", "cause_service", "cause_unknown")


def candidate_pool(base: Path | None = None) -> pd.DataFrame:
    """Ho ung vien, ghep tu cac TEP DA XUAT chu khong dung lai phep chia.

    `goldset_pool.parquet` chi chua don thuoc `t3_test`, nen rang buoc "chi lay tu
    ky test" duoc bao dam boi CHINH NGUON DU LIEU. Dac trung bang chung lay them
    tu `t3_test` va `t4_test` bang mot phep noi trong.

    Nguoi gan duoc thay CA cot T4 (ket cuc giao hang). Do la co y: nhan vang tra
    loi "nguyen nhan THAT SU la gi", mot thuoc tinh cua don hang. Rang buoc moc
    quyet dinh ap len HE THONG, khong ap len nguoi gan.
    """
    from masdss.data.export import load_split, _features_dir

    ho = pd.read_parquet(_features_dir(base) / "goldset_pool.parquet")
    ket_qua = ho
    for phan in (load_split("t3", "test", base=base), load_split("t4", "test", base=base)):
        # Bo cot da co truoc khi noi. Neu de pandas tu them hau to `_x`/`_y`, moi
        # tham chieu ve sau (`delivery_state`, `review_content`) se gay KeyError —
        # va do la kieu loi chi lo ra luc chay, khong lo ra luc doc ma.
        trung = [c for c in phan.columns if c != "order_id" and c in ket_qua.columns]
        ket_qua = ket_qua.merge(phan.drop(columns=trung), on="order_id", how="inner")
    return ket_qua


def draw(pool: pd.DataFrame, exclude: set[str], seed: int) -> pd.DataFrame:
    """Rut mau phan tang tat dinh, kem trong so."""
    pool = pool[
        pool["review_content"].notna()
        & (pool["review_content"].astype(str).str.strip() != "")
        & ~pool["order_id"].isin(exclude)
    ]

    parts = []
    for state, wanted in ALLOCATION.items():
        stratum = pool[pool["delivery_state"] == state]
        if len(stratum) < wanted:
            raise SystemExit(
                f"tang {state} chi co {len(stratum)} don, can {wanted}. "
                "Giam ALLOCATION hoac mo rong ky lay mau."
            )
        taken = stratum.sample(n=wanted, random_state=seed)
        # Trong so = so don tang do trong TONG THE / so don da lay. Nhan chi so
        # theo trong so nay moi cho uoc luong dung o muc tong the.
        taken = taken.assign(stratum=state, weight=round(len(stratum) / wanted, 4))
        parts.append(taken)

    sample = pd.concat(parts, ignore_index=True)
    # Xao tron TAT DINH: nguoi gan khong duoc thay mot khoi "da giao dung han" roi
    # mot khoi "qua han" — thu tu do tao thien lech he thong trong phan doan.
    sample = sample.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    sample.insert(0, "sample_id", [f"V{i:04d}" for i in range(1, len(sample) + 1)])
    return sample


def to_sheet(sample: pd.DataFrame) -> pd.DataFrame:
    frame = pd.DataFrame({
        "sample_id": sample["sample_id"],
        "order_id": sample["order_id"],
        "stratum": sample["stratum"],
        "weight": sample["weight"],
        "rating": sample["rating"],
        "review_title": sample.get("review_title"),
        "review_content": sample["review_content"],
        "review_title_en": "",
        "review_content_en": "",
    })
    frame["trang_thai_tai_moc_T3"] = sample["delivery_state"].map(STATE_LABEL)

    # KET CUC CUOI CUNG — cot quan trong nhat voi nguoi gan nhan.
    #
    # 77/300 don khong bao gio duoc giao, nen `delivery_delay_days` cua chung la o
    # TRONG. Mot o trong de bi hieu la loi du lieu, va nguoi gan se bo qua dung
    # nhung don nang nhat. Cot nay noi thang bang chu.
    delay = sample["delivery_delay_days"]
    frame["ket_cuc_cuoi_cung"] = [
        "KHONG BAO GIO DUOC GIAO" if pd.isna(v)
        else (f"giao TRE {v:.0f} ngay" if v > 0 else f"giao som {abs(v):.0f} ngay")
        for v in delay
    ]
    for column in EVIDENCE_COLUMNS:
        if column in sample.columns and column not in frame.columns:
            frame[column] = sample[column].round(2) if sample[column].dtype.kind == "f" \
                else sample[column]
    for column in LABEL_COLUMNS:
        frame[column] = ""
    frame["confidence"] = ""
    frame["notes"] = ""
    return frame


def main() -> None:
    goldset = CONFIG.paths.derived / "goldset"
    parser = argparse.ArgumentParser(description="Rut mau gan nhan vong cuoi")
    parser.add_argument("--n", type=int, default=sum(ALLOCATION.values()))
    parser.add_argument("--seed", type=int, default=CONFIG.seed + 2)
    parser.add_argument("--out-dir", type=Path, default=goldset)
    args = parser.parse_args()
    if args.n != sum(ALLOCATION.values()):
        raise SystemExit(f"--n phai bang tong ALLOCATION = {sum(ALLOCATION.values())}")

    CONFIG.seed_everything()
    exclude: set[str] = set()
    for name in ("gold_labels.csv", "gold_annotation_A_en.csv"):
        path = args.out_dir / name
        if path.exists():
            exclude |= set(pd.read_csv(path, encoding="utf-8-sig")["order_id"])

    sample = draw(candidate_pool(), exclude, args.seed)
    sheet = to_sheet(sample)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for who in ("A", "B"):
        sheet.to_csv(args.out_dir / f"goldset_v2_{who}.csv", index=False,
                     encoding="utf-8-sig")

    meta = {
        "n_rows": int(len(sheet)),
        "seed": args.seed,
        "period": "test split only",
        "excluded_order_ids": len(exclude),
        "t3_cutoff_days": CONFIG.t3_cutoff_days,
        "allocation": {str(k): v for k, v in ALLOCATION.items()},
        "weights": {str(int(s)): float(w) for s, w in
                    sample.groupby("stratum")["weight"].first().items()},
        "population_share": {str(int(s)): round(float(v), 4) for s, v in
                             (sample.groupby("stratum")["weight"].first()
                              * pd.Series(ALLOCATION)).pipe(lambda x: x / x.sum()).items()},
        "note": ("Phan tang theo `delivery_state`. Moi chi so bao cao o muc TONG THE "
                 "phai nhan cot `weight`; khong nhan trong so se thoi phong ty le nen "
                 "cua hai nhom qua han."),
    }
    (args.out_dir / "goldset_v2_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Da rut {len(sheet)} dong tu KY TEST (loai tru {len(exclude)} don da dung)\n")
    # KHONG bao cao "ty le bat man" o day: ho ung vien theo dinh nghia da la don bat
    # man, nen con so do luon bang 1 va chi tao cam giac co thong tin.
    print(sample.groupby("stratum").agg(
        so_dong=("order_id", "size"), trong_so=("weight", "first"),
        rating_trung_binh=("rating", "mean"),
        ty_le_1_sao=("rating", lambda r: (r == 1).mean())).round(3).to_string())
    print(f"\n-> {args.out_dir / 'goldset_v2_A.csv'}")
    print(f"-> {args.out_dir / 'goldset_v2_B.csv'}")
    print(f"-> {args.out_dir / 'goldset_v2_meta.json'}")
    print("\nHAI DIEU PHAI GIU (xem L26):")
    print("  1. Hai nguoi gan DOC LAP — khong trao doi, khong dung chung ghi chu.")
    print("  2. Neu dung cong cu ho tro: NGUOI gan truoc, cong cu chay sau.")
    print("\nKiem tra khi xong: python -m masdss.cli.check_validation \\")
    print("      --human goldset_v2_A.csv --model goldset_v2_B.csv")


if __name__ == "__main__":
    main()
