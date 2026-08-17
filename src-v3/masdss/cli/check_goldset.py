"""WP2 / T2.4 — Kiem tra tep da gan nhan va chay Gate G2.

Chay sau khi hai nguoi gan xong vong thu 30 dong:

    python -m masdss.cli.check_goldset \
        --a data/v3/goldset/gold_annotator_A.csv \
        --b data/v3/goldset/gold_annotator_B.csv

Ba buoc, dung ngay o buoc dau tien that bai:
    1. Kiem tra dinh dang ca hai tep.
    2. Tinh Cohen's kappa theo tung nguyen nhan.
    3. Quyet dinh Gate G2 — kappa trung binh >= 0,6 thi duoc di tiep.

Neu Gate G2 khong dat, van de nam o DINH NGHIA NGUYEN NHAN trong codebook, khong
phai o nguoi gan. Sua codebook roi gan lai vong thu.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from masdss.config import CONFIG
from masdss.goldset.agreement import (
    agreement_report,
    gate_g2,
    validate_annotation,
    weak_label_noise,
)


def _load(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, encoding="utf-8-sig")
    print(f"  {path.name}: {len(frame)} dong")
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(description="Kiem tra gold set va chay Gate G2")
    default_dir = CONFIG.paths.derived / "goldset"
    # Uu tien tep vong 3 (co cot tieng Anh) neu no da ton tai.
    round3_a = default_dir / "gold_annotation_A_en.csv"
    round1_a = default_dir / "gold_annotator_A.csv"
    use_round3 = round3_a.exists()
    parser.add_argument("--a", type=Path,
                        default=round3_a if use_round3 else round1_a)
    parser.add_argument("--b", type=Path,
                        default=(default_dir / "gold_annotation_B_en.csv") if use_round3
                        else (default_dir / "gold_annotator_B.csv"))
    parser.add_argument("--limit", type=int, default=None,
                        help="chi xet N dong dau (vong thu dung --limit 30)")
    parser.add_argument("--require-complete", action="store_true",
                        help="bat loi neu con dong chua gan nhan")
    args = parser.parse_args()

    print("Nap tep:")
    a, b = _load(args.a), _load(args.b)
    if args.limit:
        a, b = a.head(args.limit), b.head(args.limit)
        print(f"  -> chi xet {args.limit} dong dau (vong thu)")

    print("\n=== Buoc 1: kiem tra dinh dang ===")
    failed = False
    for name, frame in (("A", a), ("B", b)):
        report = validate_annotation(frame, require_complete=args.require_complete)
        status = "OK" if report.ok else "CO VAN DE"
        print(f"  Nguoi gan {name}: {report.n_annotated}/{report.n_rows} dong da gan — {status}")
        for problem in report.problems:
            print(f"      - {problem}")
            failed = True
    if failed:
        print("\nSua dinh dang truoc khi tinh kappa.")
        sys.exit(1)

    print("\n=== Buoc 2: Cohen's kappa theo tung nguyen nhan ===")
    report = agreement_report(a, b)
    print(report.to_string(index=False))

    out = args.a.parent / "agreement_report.csv"
    report.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\n  -> {out}")

    print("\n=== Buoc 3: Gate G2 ===")
    passed, message = gate_g2(report)
    print(f"  {'DAT' if passed else 'KHONG DAT'}: {message}")

    if passed:
        print("\nBuoc tiep theo: gan chinh thuc 370 dong con lai, chia ba dot.")
        print("Sau khi xong, do do nhieu weak label bang:")
        print("  python -m masdss.cli.check_goldset --noise")
    sys.exit(0 if passed else 2)


if __name__ == "__main__":
    main()
