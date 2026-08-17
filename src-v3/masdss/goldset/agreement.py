"""WP2 / T2.4 — Cohen's kappa va do nhieu weak label.

Phuc vu: RQ3 (Gate G2 — dieu kien de tiep tuc gan nhan).

BA CHUC NANG:
  1. Kiem tra dinh dang tep da gan nhan — bat loi truoc khi tinh kappa.
  2. Cohen's kappa DA NHAN: tinh rieng cho tung nguyen nhan, roi bao cao trung
     binh. Khong tinh kappa tren "nhan gop" vi lam vay che mat viec hai nguoi bat
     dong o dung nguyen nhan nao.
  3. Do do nhieu cua weak label so voi gold — threat duoc DINH LUONG chu khong
     phai thua nhan chung chung.

GATE G2: kappa < 0.6 thi DUNG LAI. Van de nam o dinh nghia nguyen nhan trong
codebook, khong phai o nguoi gan. Sua codebook roi gan lai vong thu.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from masdss.data.labels import CAUSE_COLUMNS, GoldLabels, WeakLabels

ALL_LABEL_COLUMNS = (*CAUSE_COLUMNS, "cause_unknown")
KAPPA_GATE = 0.6

# So luot gan duong toi thieu de kappa cua mot nhan co y nghia.
#
# NGHICH LY KAPPA. Voi mot nhan cuc hiem, kappa gan nhu vo dinh du hai nguoi dong y
# gan nhu tuyet doi. Vong gan nhan thu nhat cho vi du kinh dien:
#
#     cause_price: dong y 98,7%, nhung kappa = -0,006
#     — vi ca hai nguoi gop lai chi gan duong 5 lan tren 798 luot.
#
# Kappa hieu chinh theo ky vong ngau nhien; khi mot lop chiem ~99% thi ky vong ngau
# nhien da gan bang 1, va tu so (po - pe) tro nen cuc nho va cuc nhieu.
#
# LOI TRONG BAN DAU CUA CHINH CONG CU NAY: no lay TRUNG BINH kappa qua moi nhan, nen
# `cause_price` keo tut con so tong tu ~0,55 xuong 0,436, roi con bi bao la "nguyen
# nhan bat dong nhat" — trong khi no thuc ra la "nguyen nhan hiem nhat". Ket luan sai
# ca ve muc do lan ve dia chi cua van de.
#
# Cach sua: nhan duoi nguong nay van duoc BAO CAO day du, nhung KHONG duoc dua vao
# trung binh va khong duoc chon lam "bat dong nhat". Su hiem cua no la mot phat hien
# rieng, khong phai mot phep do do tin cay.
MIN_POSITIVES_FOR_KAPPA = 20


class AnnotationFormatError(ValueError):
    """Tep gan nhan sai dinh dang — phai sua truoc khi tinh kappa."""


@dataclass(frozen=True)
class ValidationReport:
    n_rows: int
    n_annotated: int
    problems: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.problems


def validate_annotation(frame: pd.DataFrame, *, require_complete: bool = False) -> ValidationReport:
    """Kiem tra tep da gan nhan truoc khi tinh bat cu chi so nao."""
    problems: list[str] = []

    missing = [c for c in ALL_LABEL_COLUMNS if c not in frame.columns]
    if missing:
        raise AnnotationFormatError(f"thieu cot nhan: {missing}")

    labels = frame[list(ALL_LABEL_COLUMNS)].apply(pd.to_numeric, errors="coerce")
    annotated = labels.notna().any(axis=1) & (labels.fillna(0).sum(axis=1) > 0)

    bad_values = labels.stack().dropna()
    invalid = bad_values[~bad_values.isin([0, 1])]
    if len(invalid):
        problems.append(f"{len(invalid)} o co gia tri khac 0/1")

    # `cause_unknown` loai tru voi bon nguyen nhan cu the (quy tac §2 codebook).
    conflict = (labels["cause_unknown"].fillna(0) == 1) & (
        labels[list(CAUSE_COLUMNS)].fillna(0).sum(axis=1) > 0
    )
    if conflict.any():
        ids = frame.loc[conflict, "sample_id"].head(5).tolist()
        problems.append(
            f"{int(conflict.sum())} dong vua danh unknown vua danh nguyen nhan cu the "
            f"(vi du: {ids})"
        )

    if require_complete and not annotated.all():
        pending = frame.loc[~annotated, "sample_id"].head(5).tolist()
        problems.append(f"{int((~annotated).sum())} dong chua gan nhan (vi du: {pending})")

    return ValidationReport(
        n_rows=len(frame), n_annotated=int(annotated.sum()), problems=tuple(problems)
    )


def _cohen_kappa(a: np.ndarray, b: np.ndarray) -> float:
    """Cohen's kappa cho nhan nhi phan. Tra NaN khi khong xac dinh."""
    n = len(a)
    if n == 0:
        return float("nan")
    observed = float((a == b).mean())
    p_a1, p_b1 = a.mean(), b.mean()
    expected = p_a1 * p_b1 + (1 - p_a1) * (1 - p_b1)
    if np.isclose(expected, 1.0):
        # Ca hai nguoi deu gan cung mot gia tri cho moi dong -> kappa khong xac dinh
        return float("nan")
    return (observed - expected) / (1 - expected)


def agreement_report(a: pd.DataFrame, b: pd.DataFrame,
                     key: str = "sample_id") -> pd.DataFrame:
    """Kappa theo tung nguyen nhan giua hai nguoi gan doc lap."""
    merged = a.merge(b, on=key, suffixes=("_a", "_b"))
    if merged.empty:
        raise AnnotationFormatError("hai tep khong co dong nao trung sample_id")

    rows = []
    for column in ALL_LABEL_COLUMNS:
        va = pd.to_numeric(merged[f"{column}_a"], errors="coerce").fillna(0).to_numpy()
        vb = pd.to_numeric(merged[f"{column}_b"], errors="coerce").fillna(0).to_numpy()
        n_positive = int(va.sum() + vb.sum())
        reliable = n_positive >= MIN_POSITIVES_FOR_KAPPA
        rows.append({
            "label": column,
            "n": len(merged),
            "n_positive": n_positive,
            "pct_positive_a": round(100 * va.mean(), 1),
            "pct_positive_b": round(100 * vb.mean(), 1),
            "percent_agreement": round(100 * float((va == vb).mean()), 1),
            "cohen_kappa": round(_cohen_kappa(va, vb), 4),
            # Nhan qua hiem thi kappa vo dinh — bao cao nhung khong tinh vao trung binh.
            "kappa_reliable": reliable,
        })

    report = pd.DataFrame(rows)
    usable = report[report["kappa_reliable"]]
    mean_kappa = usable["cohen_kappa"].mean(skipna=True) if len(usable) else float("nan")
    report.loc[len(report)] = {
        "label": f"TRUNG BINH ({len(usable)}/{len(rows)} nhan)",
        "n": len(merged),
        "n_positive": int(report["n_positive"].sum()),
        "pct_positive_a": np.nan, "pct_positive_b": np.nan,
        "percent_agreement": round(report["percent_agreement"].mean(), 1),
        "cohen_kappa": round(mean_kappa, 4),
        "kappa_reliable": True,
    }
    return report


def gate_g2(report: pd.DataFrame) -> tuple[bool, str]:
    """Quyet dinh cua Gate G2.

    Chi tinh tren nhung nhan co du luot gan duong de kappa co y nghia. Nhan qua hiem
    van duoc bao cao nhung khong tham gia quyet dinh — xem `MIN_POSITIVES_FOR_KAPPA`.
    """
    summary = report[report["label"].str.startswith("TRUNG BINH")]
    if summary.empty:
        return False, "bao cao thieu dong tong hop"
    mean_kappa = float(summary["cohen_kappa"].iloc[0])

    if np.isnan(mean_kappa):
        return False, "khong nhan nao du luot gan duong de tinh kappa"

    per_label = report[~report["label"].str.startswith("TRUNG BINH")]
    rare = per_label[~per_label["kappa_reliable"]]
    note = ""
    if len(rare):
        names = ", ".join(f"{r.label} (n+={r.n_positive})" for r in rare.itertuples())
        note = (f" Khong tinh nhan qua hiem vao trung binh: {names} — "
                f"o tan suat do kappa vo dinh, khong phai do do tin cay.")

    if mean_kappa >= KAPPA_GATE:
        return True, f"kappa trung binh = {mean_kappa:.3f} >= {KAPPA_GATE} — duoc di tiep.{note}"

    usable = per_label[per_label["kappa_reliable"]]
    weakest = usable.iloc[usable["cohen_kappa"].fillna(1).argmin()]["label"] if len(usable) else "?"
    return False, (
        f"kappa trung binh = {mean_kappa:.3f} < {KAPPA_GATE}. Sua dinh nghia trong "
        f"codebook roi gan lai phan bat dong. Nhan can sua truoc: {weakest}.{note}"
    )


def weak_label_noise(gold: GoldLabels, weak: WeakLabels,
                     key: str = "order_id") -> pd.DataFrame:
    """Do do nhieu cua weak label so voi gold — threat duoc DINH LUONG.

    Day la lan duy nhat weak label duoc dat canh gold, va no la de DO NHIEU chu
    khong phai de cham diem he thong.
    """
    merged = gold.frame.merge(weak.frame, on=key, suffixes=("_gold", "_weak"))
    if merged.empty:
        raise AnnotationFormatError(f"khong khop duoc dong nao theo '{key}'")

    rows = []
    for column in ALL_LABEL_COLUMNS:
        g = pd.to_numeric(merged[f"{column}_gold"], errors="coerce").fillna(0).to_numpy()
        w = pd.to_numeric(merged[f"{column}_weak"], errors="coerce").fillna(0).to_numpy()
        tp = float(((g == 1) & (w == 1)).sum())
        fp = float(((g == 0) & (w == 1)).sum())
        fn = float(((g == 1) & (w == 0)).sum())
        precision = tp / (tp + fp) if tp + fp else float("nan")
        recall = tp / (tp + fn) if tp + fn else float("nan")
        f1 = (2 * precision * recall / (precision + recall)
              if precision and recall and not np.isnan(precision) and not np.isnan(recall)
              else float("nan"))
        rows.append({
            "label": column, "n": len(merged),
            "weak_precision": round(precision, 4),
            "weak_recall": round(recall, 4),
            "weak_f1": round(f1, 4),
            "disagreement_pct": round(100 * float((g != w).mean()), 1),
        })
    return pd.DataFrame(rows)
