"""WP2 / T2.8 — Dong bang ban dich thanh artifact co nguon goc.

Chay sau khi da dien xong hai cot tieng Anh:
    python -m masdss.cli.freeze_translations

Sinh ra:
    translations.csv        -> ban dich DA DONG BANG
    translations_meta.json  -> nguon goc + checksum + canh bao

VI SAO PHAI DONG BANG.

    Ban dich duoc tao ben ngoai (cong thuc dich trong bang tinh) nen KHONG tai tao
    duoc bang mot lenh. No la mot CONG CU DO moi, va neu chi noi "chung toi dung dich
    may" thi no lap lai dung loi ma ban phan bien da chi ra voi bo tu khoa: mot cong
    cu do khong duoc kiem dinh.

    Vi vay ban dich duoc doi xu nhu MOT ARTIFACT — co checksum, co ghi chu nguon goc,
    va duoc nhac lai trong Threats to Validity. Neu ai do dich lai bang cong cu khac,
    checksum doi va moi ket qua downstream truy nguyen duoc ve dung ban dich nao.

BON PHEP KIEM TRA truoc khi dong bang, moi phep chan mot loi that:

    thieu cot          — file sai dinh dang
    thieu dong         — dich sot
    ban dich rong      — QUEN DAN GIA TRI, loi hay gap nhat
    trung y het goc    — cong thuc chua chay
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from masdss.config import CONFIG

SOURCE_COLUMN = "review_content"
TARGET_COLUMN = "review_content_en"
IDENTICAL_TOLERANCE = 0.10   # duoi muc nay coi la binh thuong (van ban mot tu)


def _checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def validate(frame: pd.DataFrame) -> list[str]:
    """Kiem tra ban dich TRONG chinh tep gan nhan."""
    problems: list[str] = []

    missing = {"sample_id", SOURCE_COLUMN, TARGET_COLUMN} - set(frame.columns)
    if missing:
        problems.append(f"thieu cot: {sorted(missing)}")
        return problems

    source = frame[SOURCE_COLUMN].fillna("").astype(str).str.strip()
    target = frame[TARGET_COLUMN].fillna("").astype(str).str.strip()
    has_source = source.str.len() > 0

    blank = frame.loc[has_source & (target.str.len() == 0), "sample_id"]
    if len(blank):
        problems.append(
            f"{len(blank)} dong co van ban goc nhung ban dich rong "
            f"(vi du: {blank.head(5).tolist()}) — co the quen DAN GIA TRI"
        )

    identical = frame.loc[has_source & (source == target), "sample_id"]
    if len(identical) > IDENTICAL_TOLERANCE * max(int(has_source.sum()), 1):
        problems.append(
            f"{len(identical)}/{int(has_source.sum())} dong co ban dich trung y het "
            f"ban goc — nghi cong thuc chua chay"
        )
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description="Dong bang ban dich thanh artifact")
    default_dir = CONFIG.paths.derived / "goldset"
    parser.add_argument("--dir", type=Path, default=default_dir)
    parser.add_argument("--from", dest="source", type=Path, default=None,
                        help="mac dinh: gold_annotation_A_en.csv")
    parser.add_argument("--note", default="dich may bang cong thuc GOOGLETRANSLATE trong bang tinh",
                        help="ghi chu nguon goc, di thang vao Threats to Validity")
    args = parser.parse_args()

    path = args.source or (args.dir / "gold_annotation_A_en.csv")
    frame = pd.read_csv(path, encoding="utf-8-sig")
    print(f"Doc {len(frame)} dong tu {path.name}")

    problems = validate(frame)
    if problems:
        print("\nCO VAN DE — sua truoc khi dong bang:")
        for problem in problems:
            print(f"  - {problem}")
        raise SystemExit(1)
    print("  ban dich hop le")

    keep = ["sample_id", "review_title", "review_content",
            "review_title_en", "review_content_en"]
    frozen = frame[[c for c in keep if c in frame.columns]].copy()
    frozen_path = args.dir / "translations.csv"
    frozen.to_csv(frozen_path, index=False, encoding="utf-8-sig")

    source = frame[SOURCE_COLUMN].fillna("").astype(str).str.strip()
    target = frame[TARGET_COLUMN].fillna("").astype(str).str.strip()
    shorter = int(((target.str.len() > 0) & (source.str.len() > 0)
                   & (target.str.len() < 0.6 * source.str.len())).sum())

    meta = {
        "n_rows": int(len(frozen)),
        "source_file": str(path),
        "source_sha256_16": _checksum(path),
        "frozen_sha256_16": _checksum(frozen_path),
        "provenance": args.note,
        "scope": "chi tang A (don co review_content); tang B khong co van ban de dich",
        "suspicious_short_translations": shorter,
        "caveat": (
            "Ban dich tao ben ngoai nen khong tai tao duoc bang mot lenh. No la mot "
            "cong cu do CHUA DUOC KIEM DINH — phai doi chieu it nhat 50 mau voi nguoi "
            "biet tieng Bo, uu tien cau co phu dinh va viet tat, roi ghi ty le dich sai "
            "vao Threats to Validity."
        ),
    }
    (args.dir / "translations_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"  -> {frozen_path}  (sha256 {meta['frozen_sha256_16']})")
    print(f"  -> {args.dir / 'translations_meta.json'}")
    if shorter:
        print(f"\n  {shorter} dong co ban dich NGAN HON 60% ban goc — nghi bi rot menh de.")
        print("  Day la nhung dong nen uu tien khi doi chieu voi nguoi biet tieng Bo.")


if __name__ == "__main__":
    main()
