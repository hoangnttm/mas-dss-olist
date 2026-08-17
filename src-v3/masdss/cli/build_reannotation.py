"""WP2 / T2.5b — Sinh tep gan lai cho vong hai.

Chay:
    python -m masdss.cli.build_reannotation

Chi lay nhung dong HAI NGUOI BAT DONG o vong mot. Dong da dong thuan giu nguyen —
gan lai chung khong them thong tin gi ma chi ton thoi gian.

QUYET DINH QUAN TRONG: TEP GAN LAI PHAI MU.

    No KHONG chua nhan cua vong mot, khong cua chinh nguoi do, cang khong cua nguoi
    kia. Ly do: neu nguoi gan nhin thay nguoi kia da chon gi, ho se hoi tu ve phia
    nhau, va kappa vong hai se cao mot cach GIA TAO — ta se do duoc suc ep tuan thu
    xa hoi thay vi do do ro rang cua dinh nghia.

    Muc dich cua vong hai la kiem tra xem CODEBOOK BAN 2 co lam cho hai nguoi hoi tu
    hay khong. Chi mot phep do mu moi tra loi duoc cau hoi do.

    Anh xa sang nhan vong mot duoc giu rieng trong `reannotate_manifest.csv` de phan
    tich ve sau — no khong den tay nguoi gan.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from masdss.config import CONFIG
from masdss.data.labels import CAUSE_COLUMNS

ALL_LABELS = (*CAUSE_COLUMNS, "cause_unknown")

EVIDENCE_COLUMNS = [
    "sample_id", "order_id", "tier", "rating",
    "review_title", "review_content",
    "category", "delivery_delay_days", "delivery_days", "carrier_handover_days",
    "price", "freight_value", "freight_ratio", "n_items",
]
FILL_COLUMNS = [*ALL_LABELS, "confidence", "notes"]


def _labels(frame: pd.DataFrame) -> pd.DataFrame:
    return (frame.set_index("sample_id")[list(ALL_LABELS)]
            .apply(pd.to_numeric, errors="coerce").fillna(0).astype(int))


def find_disagreements(a: pd.DataFrame, b: pd.DataFrame) -> list[str]:
    """Dong co bat ky nhan nao khac nhau giua hai nguoi."""
    la, lb = _labels(a), _labels(b)
    common = la.index.intersection(lb.index)
    differs = (la.loc[common] != lb.loc[common]).any(axis=1)
    return sorted(common[differs])


def main() -> None:
    parser = argparse.ArgumentParser(description="Sinh tep gan lai cho vong hai")
    default_dir = CONFIG.paths.derived / "goldset"
    parser.add_argument("--dir", type=Path, default=default_dir)
    args = parser.parse_args()

    a = pd.read_csv(args.dir / "gold_annotator_A.csv", encoding="utf-8-sig")
    b = pd.read_csv(args.dir / "gold_annotator_B.csv", encoding="utf-8-sig")

    disputed = find_disagreements(a, b)
    print(f"Vong mot: {len(a)} dong, {len(disputed)} dong bat dong "
          f"({100 * len(disputed) / len(a):.1f}%)")

    subset = a[a["sample_id"].isin(disputed)][EVIDENCE_COLUMNS].copy()
    for column in FILL_COLUMNS:
        subset[column] = ""

    for who in ("A", "B"):
        path = args.dir / f"reannotate_{who}.csv"
        subset.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"  -> {path}  ({len(subset)} dong, MU — khong chua nhan vong mot)")

    # Ho so rieng de phan tich ve sau. KHONG den tay nguoi gan.
    la, lb = _labels(a), _labels(b)
    manifest = pd.DataFrame({
        "sample_id": disputed,
        "round1_A": [",".join(c[6:] for c in ALL_LABELS if la.loc[s, c] == 1) for s in disputed],
        "round1_B": [",".join(c[6:] for c in ALL_LABELS if lb.loc[s, c] == 1) for s in disputed],
    })
    manifest.to_csv(args.dir / "reannotate_manifest.csv", index=False, encoding="utf-8-sig")
    print(f"  -> {args.dir / 'reannotate_manifest.csv'}  (ho so noi bo, khong dua cho nguoi gan)")

    print("\nBat dong theo tung nhan:")
    for column in ALL_LABELS:
        n = int((la.loc[disputed, column] != lb.loc[disputed, column]).sum())
        print(f"  {column:16s} {n:4d}")


if __name__ == "__main__":
    main()
