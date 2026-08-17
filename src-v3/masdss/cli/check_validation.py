"""WP2 / T2.9 — Do do dung cua bo nhan do mo hinh sinh, doi chieu voi con nguoi.

Day la Gate G2 THAT. Gate G2 chay truoc do — kappa giua hai ban sao cua cung mot
dau ra mo hinh — cho 0,957 va con so do khong do gi ca (xem L26).

BA KIEM TRA, theo thu tu. Kiem tra dau la quan trong nhat.

  1. DOC LAP     — hai ban gan phai KHAC nhau du de tin la hai phan doan rieng.
                   Ghi chu trung nhau qua nhieu la dau hieu chung nguon.
  2. DO DUNG     — kappa giua NGUOI va MO HINH tren mau doc lap. Day moi la con
                   so duoc phep dua vao Chuong 4.
  3. HUONG LECH  — mo hinh quy ket nhieu hon hay it hon con nguoi, va o nhan nao.
                   Mot chenh lech co huong noi nhieu hon mot con so kappa tron.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from masdss.config import CONFIG
from masdss.goldset.agreement import (ALL_LABEL_COLUMNS as LABEL_COLUMNS,
                                      MIN_POSITIVES_FOR_KAPPA, agreement_report,
                                      validate_annotation)

# Tren co mau nay, ty le ghi chu trung khop cao hon nguong nay khong the giai thich
# bang viec hai ben cung nhin mot cau. No chi giai thich duoc bang chung nguon.
IDENTICAL_NOTE_LIMIT = 0.30


def independence_check(human: pd.DataFrame, model: pd.DataFrame) -> tuple[bool, str]:
    """Chan dung cai sai da xay ra o vong 3: hai cot den tu cung mot quy trinh.

    Kappa gia dinh hai nguoi do DOC LAP. Neu gia dinh do sai thi kappa khong con
    y nghia, va no van cho ra mot con so dep — do la ly do phai kiem tra truoc.
    """
    problems = []
    for column in ("notes", "confidence"):
        if column not in human.columns or column not in model.columns:
            continue
        a = human[column].fillna("").astype(str).str.strip()
        b = model[column].fillna("").astype(str).str.strip()
        both = (a != "") & (b != "")
        if not both.any():
            continue
        rate = float((a[both] == b[both]).mean())
        if rate > IDENTICAL_NOTE_LIMIT:
            problems.append(f"cot `{column}` trung khop {rate:.1%} "
                            f"(nguong {IDENTICAL_NOTE_LIMIT:.0%})")

    identical_rows = float((human[list(LABEL_COLUMNS)].values
                            == model[list(LABEL_COLUMNS)].values).all(axis=1).mean())
    if identical_rows > 0.97:
        problems.append(f"hang nhan trung khop hoan toan {identical_rows:.1%} — "
                        "cao bat thuong voi hai phan doan doc lap")

    if problems:
        return False, ("KHONG DOC LAP: " + " · ".join(problems)
                       + "\n  Kappa tinh tren hai ban khong doc lap KHONG do do dung. "
                         "Phai gan lai theo dung thu tu: nguoi truoc, mo hinh sau.")
    return True, f"Doc lap: hang nhan trung khop {identical_rows:.1%} — hop ly"


def direction_report(human: pd.DataFrame, model: pd.DataFrame) -> pd.DataFrame:
    """Mo hinh quy ket nhieu hay it hon nguoi, tach theo tung nhan.

    Mot kappa tron che mat huong lech. Neu mo hinh quy ket nhieu hon nguoi mot
    cach he thong thi gold set bi thoi phong recall, va macro-F1 cua RQ3 se do
    tren mot su that nen rong hon thuc te.
    """
    rows = []
    for label in LABEL_COLUMNS:
        h = human[label].fillna(0).astype(int)
        m = model[label].fillna(0).astype(int)
        rows.append({
            "nhan": label.replace("cause_", ""),
            "nguoi_gan": int(h.sum()),
            "mo_hinh_gan": int(m.sum()),
            "mo_hinh_them": int(((m == 1) & (h == 0)).sum()),
            "mo_hinh_bo_sot": int(((m == 0) & (h == 1)).sum()),
            "du_duong_cho_kappa": bool(((h == 1) | (m == 1)).sum() >= MIN_POSITIVES_FOR_KAPPA),
        })
    return pd.DataFrame(rows)


def main() -> None:
    goldset = CONFIG.paths.derived / "goldset"
    parser = argparse.ArgumentParser(description="Gate G2 that — do dung cua nhan")
    parser.add_argument("--human", type=Path, default=goldset / "validation_human.csv")
    parser.add_argument("--model", type=Path, default=goldset / "validation_model.csv")
    args = parser.parse_args()

    for path in (args.human, args.model):
        if not path.exists():
            print(f"Thieu tep: {path}")
            print("Chay truoc: python -m masdss.cli.build_validation_sample")
            return

    human = pd.read_csv(args.human).sort_values("sample_id").reset_index(drop=True)
    model = pd.read_csv(args.model).sort_values("sample_id").reset_index(drop=True)
    if list(human["sample_id"]) != list(model["sample_id"]):
        print("Hai tep khong cung tap sample_id — khong so sanh duoc.")
        return

    print(f"Mau kiem chung: {len(human)} dong\n")

    print("=== Buoc 1: dinh dang ===")
    stop = False
    for name, frame in (("NGUOI", human), ("MO HINH", model)):
        report = validate_annotation(frame, require_complete=True)
        print(f"  {name}: {report.describe() if hasattr(report, 'describe') else report}")
        if getattr(report, "problems", None):
            stop = True
    if stop:
        print("\nSua dinh dang truoc khi di tiep.")
        return

    print("\n=== Buoc 2: kiem tra DOC LAP (quan trong nhat) ===")
    independent, message = independence_check(human, model)
    print(f"  {message}")
    if not independent:
        return

    print("\n=== Buoc 3: do dung — kappa NGUOI vs MO HINH ===")
    report = agreement_report(human, model)
    print(report.to_string(index=False))

    mean_row = report[report["label"].str.startswith("TRUNG BINH")]
    kappa = float(mean_row["cohen_kappa"].iloc[0]) if len(mean_row) else float("nan")
    passed = kappa >= 0.6
    print(f"\n  => Gate G2 THAT: {'DAT' if passed else 'CHUA DAT'} "
          f"— kappa nguoi/mo hinh = {kappa:.3f}")
    if passed:
        print("     Bo nhan 250 dong duoc chap nhan lam su that nen, VOI DIEU KIEN")
        print("     Chuong 4 khai bao dung phuong phap: nhan do mo hinh sinh, nguoi")
        print("     ra soat, do dung kiem chung tren mau doc lap.")
    else:
        print("     Chua du de dung 250 dong lam su that nen cho RQ3.")

    print("\n=== Buoc 4: huong lech ===")
    direction = direction_report(human, model)
    print(direction.to_string(index=False))
    thieu = direction[~direction["du_duong_cho_kappa"]]["nhan"].tolist()
    if thieu:
        print(f"\n  Khong du duong de tinh kappa tin cay: {thieu} — bao cao la khong tin cay,")
        print(f"  can it nhat {MIN_POSITIVES_FOR_KAPPA} duong moi nhan (loi L19).")

    out = goldset / "validation_report.csv"
    report.to_csv(out, index=False, encoding="utf-8-sig")
    direction.to_csv(goldset / "validation_direction.csv", index=False, encoding="utf-8-sig")
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
