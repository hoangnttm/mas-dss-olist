"""WP2 / T2.8 — Rut mau KIEM CHUNG cho bo nhan do mo hinh sinh.

VI SAO CAN MODULE NAY.

    250 dong tang A cua vong 3 duoc gan bang mot mo hinh ngon ngu, sau do nguoi
    nghien cuu ra soat lai. Do la mot phuong phap hop le, nhung no KHONG phai
    "hai nguoi gan doc lap", nen he so Cohen's kappa tinh giua hai ban sao cua
    cung mot dau ra khong do duoc gi — no chi xac nhan quy trinh do tat dinh.

    Van de con lai la DO DUNG cua nhan, va cach duy nhat do duoc do la doi chieu
    voi phan doan cua con nguoi tren mot mau DOC LAP.

VI SAO PHAI LAY MAU MOI, KHONG DUNG LAI 250 DONG CU.

    Nguoi nghien cuu da doc ca 250 dong SAU KHI thay nhan cua mo hinh. Phan doan
    tren chinh nhung dong do da bi NEO — hoi lai cung nhung dong ay chi do duoc
    muc dong y voi mot cau tra loi da biet, khong do duoc phan doan doc lap.

    Vi vay mau kiem chung duoc rut tu phan dan so CHUA AI DUNG TOI (10.573 dong
    tang A con lai), va thu tu bat buoc la: NGUOI GAN TRUOC, MO HINH CHAY SAU.

CO MAU.

    Mac dinh 150 dong. Voi ty le duong quan sat duoc o 250 dong hien co, con so
    nay cho khoang 87 duong `delivery`, 52 `quality`, 27 `service` — deu vuot
    nguong 20 duong cua `MIN_POSITIVES_FOR_KAPPA`. Hai nhan `price` (~7) va
    `unknown` (~11) se KHONG du va se bi danh dau khong tin cay, dung co che da
    co san. Do la gioi han phai bao cao, khong phai thu de che di.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from masdss.config import CONFIG

# Cac cot bang chung cau truc, giu dung thu tu nhu phieu gan nhan chinh.
EVIDENCE_COLUMNS = (
    "category", "delivery_delay_days", "delivery_days", "carrier_handover_days",
    "price", "freight_value", "freight_ratio", "n_items",
)
LABEL_COLUMNS = ("cause_delivery", "cause_quality", "cause_service",
                 "cause_unknown")


def build(n: int, seed: int, exclude: set[str]) -> pd.DataFrame:
    from masdss.data.export import load_stage

    # Mau kiem chung lay tu ky TEST cua tong the T4 — cung ho voi gold set, neu
    # khong hai bo nhan se noi ve hai tong the khac nhau.
    orders = load_stage("t4", "test", labels=("is_dissatisfied", "tier"))
    pool = orders[(orders["is_dissatisfied"]) & (orders["tier"] == "A")]
    pool = pool[~pool["order_id"].isin(exclude)]

    # Ngau nhien don gian, KHONG phan tang. Phan tang theo nhan cua mo hinh se
    # lam meo uoc luong do dung: no chon truoc nhung dong ma mo hinh tu tin.
    sample = pool.sample(n=min(n, len(pool)), random_state=seed).reset_index(drop=True)

    frame = pd.DataFrame({
        "sample_id": [f"V{i:04d}" for i in range(1, len(sample) + 1)],
        "order_id": sample["order_id"],
        "rating": sample["rating"],
        "review_title": sample.get("review_title"),
        "review_content": sample["review_content"],
        "review_title_en": "",
        "review_content_en": "",
    })
    for column in EVIDENCE_COLUMNS:
        if column in sample.columns:
            frame[column] = sample[column]
    for column in LABEL_COLUMNS:
        frame[column] = ""
    frame["confidence"] = ""
    frame["notes"] = ""
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rut mau kiem chung doc lap cho bo nhan do mo hinh sinh")
    parser.add_argument("--n", type=int, default=150)
    parser.add_argument("--seed", type=int, default=CONFIG.seed + 1)
    parser.add_argument("--out", type=Path,
                        default=CONFIG.paths.derived / "goldset" / "validation_human.csv")
    args = parser.parse_args()

    existing = CONFIG.paths.derived / "goldset" / "gold_annotation_A_en.csv"
    exclude: set[str] = set()
    if existing.exists():
        exclude = set(pd.read_csv(existing)["order_id"])

    frame = build(args.n, args.seed, exclude)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.out, index=False, encoding="utf-8-sig")

    print(f"Rut {len(frame)} dong tang A tu phan dan so chua dung "
          f"(loai tru {len(exclude)} dong da co)")
    print(f"-> {args.out}")
    print()
    print("THU TU BAT BUOC — dao thu tu nay lam mat hieu luc cua phep do:")
    print("  1. Dich hai cot _en (cung cach nhu truoc).")
    print("  2. NGUOI gan nhan, KHONG chay cong cu, KHONG xem nhan cua mo hinh.")
    print("  3. Chay cong cu tren cung file da dich -> validation_model.csv")
    print("  4. python -m masdss.cli.check_validation")


if __name__ == "__main__":
    main()
