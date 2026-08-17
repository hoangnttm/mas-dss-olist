"""WP2 / T2.8 — Sinh tep gan nhan vong 3: tieng Bo goc + cot tieng Anh + cot nhan.

Chay:
    python -m masdss.cli.build_annotation_en

Sinh ra trong data/v3/goldset/:
    gold_annotation_A_en.csv
    gold_annotation_B_en.csv

MOT TEP DUY NHAT cho ca ba viec: dich, doi chieu, gan nhan. Nguoi gan dien cot
`review_content_en` bang cong thuc dich, roi gan nhan ngay tren cung dong.

THU TU COT LA CO CHU DICH:

    review_title / review_content       — ban goc tieng Bo, GIU NGUYEN
    review_title_en / review_content_en — de trong, dien bang cong thuc dich
    ... bang chung cau truc ...
    cause_*, confidence, notes          — cot gan nhan

Ban goc dat TRUOC ban dich de cong thuc `=GOOGLETRANSLATE(F2; "pt"; "en")` tro toi o
ngay ben trai, va de nguoi gan luon nhin thay ban goc khi doi chieu (QT5 cua codebook).

VI SAO GIU BAN GOC. Nhan phai neo vao VAN BAN GOC, khong vao ban dich. Ban dich la
cong cu doc, khong phai su that. Neu chi hien tieng Anh, mot cau dich sai se tao ra
nhan sai ma khong ai biet — va nhan do lai duoc dung de cham diem mot mo hinh doc
tieng Bo (BERTimbau, T3.4).

PHAM VI: chi 250 dong TANG A. Tang B (150 dong, khong co van ban) giu nguyen nhan
vong 1 — no khong phu thuoc ngon ngu va da dat dong thuan tuyet doi 0/150.

TEP DE MU: khong chua nhan vong 1 cua bat ky ai. Nhin thay nhan cu se neo phan doan
va lam kappa vong nay cao mot cach gia tao (loi L20 trong methodology-log).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from masdss.config import CONFIG

COLUMN_ORDER = [
    "sample_id", "order_id", "tier", "rating",
    # --- ban goc tieng Bo, giu nguyen ---
    "review_title", "review_content",
    # --- ban dich, de trong ---
    "review_title_en", "review_content_en",
    # --- bang chung cau truc ---
    "category", "delivery_delay_days", "delivery_days", "carrier_handover_days",
    "price", "freight_value", "freight_ratio", "n_items",
]
TRANSLATION_COLUMNS = ["review_title_en", "review_content_en"]
LABEL_COLUMNS = ["cause_delivery", "cause_quality", "cause_service",
                 "cause_unknown", "confidence", "notes"]


def build(gold: pd.DataFrame, tier: str = "A") -> pd.DataFrame:
    subset = gold[gold["tier"] == tier].copy()
    for column in TRANSLATION_COLUMNS:
        subset[column] = ""
    frame = subset[[c for c in COLUMN_ORDER if c in subset.columns]].copy()
    for column in LABEL_COLUMNS:
        frame[column] = ""
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(description="Sinh tep gan nhan vong 3 (co cot tieng Anh)")
    default_dir = CONFIG.paths.derived / "goldset"
    parser.add_argument("--dir", type=Path, default=default_dir)
    parser.add_argument("--tier", default="A", choices=["A", "B", "all"])
    args = parser.parse_args()

    gold = pd.read_csv(args.dir / "gold_annotator_A.csv", encoding="utf-8-sig")
    frame = (build(gold, args.tier) if args.tier != "all"
             else build(gold.assign(tier="A"), "A"))

    for who in ("A", "B"):
        path = args.dir / f"gold_annotation_{who}_en.csv"
        frame.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"  -> {path}  ({len(frame)} dong)")

    n_title = int(gold[gold["tier"] == "A"]["review_title"].notna().sum())
    excluded = len(gold) - len(frame)
    print(f"\nTang A: {len(frame)} dong ({n_title} dong co tieu de)")
    print(f"Tang B: {excluded} dong — KHONG gan lai, giu nhan vong 1")
    print("        (khong co van ban nen khong phu thuoc ngon ngu; da dong thuan 0/150)")

    columns = list(frame.columns)
    letter = lambda name: chr(ord("A") + columns.index(name))  # noqa: E731
    print("\n--- Cach dien cot tieng Anh trong Google Sheets ---")
    print(f"  cot {letter('review_title_en')}2 : =GOOGLETRANSLATE({letter('review_title')}2; \"pt\"; \"en\")")
    print(f"  cot {letter('review_content_en')}2 : =GOOGLETRANSLATE({letter('review_content')}2; \"pt\"; \"en\")")
    print("  Keo het cot, roi DAN GIA TRI (Ctrl+Shift+V) truoc khi luu CSV.")
    print("  Neu khong dan gia tri, o cong thuc se xuat ra RONG va buoc kiem tra se chan lai.")

    print("\n--- Sau khi dich va gan nhan xong ---")
    print("  python -m masdss.cli.freeze_translations   # dong bang ban dich thanh artifact")
    print("  python -m masdss.cli.check_goldset --require-complete \\")
    print("      --a data/v3/goldset/gold_annotation_A_en.csv \\")
    print("      --b data/v3/goldset/gold_annotation_B_en.csv")


if __name__ == "__main__":
    main()
