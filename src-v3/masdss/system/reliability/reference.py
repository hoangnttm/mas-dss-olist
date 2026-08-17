"""T7.3a — Dung phan phoi tham chieu cho nhom Analyst.

Phuc vu: RQ1(b) — mo rong pham vi phu cua bo giam sat.

VAN DE DUOC GIAI QUYET. Sau WP8, guard chi phu duoc DUNG MOT thanh phan
(`prediction`), vi do la thanh phan duy nhat co phan phoi tham chieu sach. Gioi han
nay da duoc ghi ro trong build-plan.md §0.8, va no lam hong ca hai phia:

    - `bias:cause_delivery` khong bi phat hien (0 canh bao)
    - moi loi Byzantine tren nhom Analyst deu di qua ma khong ai biet

TACH PHAN KHONG BI CHAN. T7.3 day du (hieu chuan isotonic tung analyst, bao cao
ECE truoc/sau) can gold set — chua co. Nhung thu THUC SU mo khoa giam sat khong
phai hieu chuan, ma la PHAN PHOI THAM CHIEU, va cai do **khong can nhan nao ca**:
chi can chay tung signal tren tap train va ghi lai phan bo do tin cay.

BA RANG BUOC, ca ba deu la bai hoc truc tiep tu cac loi da ghi trong
docs/methodology-log.md:

  1. KHOP TONG THE (bai hoc L15). Luong duoc giam sat o giai doan 2 chi gom don
     BAT MAN, nen tham chieu cung phai lay tu don bat man cua tap train. Lay tu
     toan bo tap train se cho bao dong gia y het loi L15.

  2. CHI LAY BID DA PHAT (bai hoc L15, dang thu hai). Analyst chi gui PROPOSE khi
     vuot nguong; nhung lan tra 0.0 khong bao gio vao luong giam sat. Dua chung
     vao tham chieu se lam lech phan phoi ve phia 0.

  3. TU CHOI DUNG TRAM LANG khi tham chieu qua it mau hoac gan nhu hang so (bai
     hoc L14). Khong co tien de thi khong ket luan. `LexiconCauseHead` tra hang so
     0,55 nen hai analyst van ban VAN chua giam sat duoc — dung, va phai ghi ro.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from masdss.core.components import Component
from masdss.core.ontology import DecisionPoint, OrderCase
from masdss.system.reliability.health import HealthMonitor

MIN_REFERENCE_SAMPLES = 200
MIN_REFERENCE_VARIANCE = 1e-6


@dataclass(frozen=True)
class ReferenceCoverage:
    """Bao cao thanh phan nao duoc giam sat, thanh phan nao khong, va vi sao."""

    component: str
    metric: str
    n_samples: int
    variance: float
    installed: bool
    reason: str

    def describe(self) -> str:
        mark = "co" if self.installed else "KHONG"
        return (f"  {self.component:16s}.{self.metric:12s} {mark:>5s} giam sat  "
                f"(n={self.n_samples:5d}, var={self.variance:.5f}) — {self.reason}")


def _signal_confidences(signal, frame: pd.DataFrame, feature_columns: list[str]) -> np.ndarray:
    """Chay mot signal tren tap train, chi giu nhung lan THUC SU phat bid."""
    values: list[float] = []
    for _, row in frame.iterrows():
        case = OrderCase(
            case_id=str(row["order_id"]),
            decision_point=DecisionPoint.T4,
            features={c: row[c] for c in feature_columns if c in row},
            review_text=(None if pd.isna(row.get("review_content"))
                         else str(row.get("review_content"))),
        )
        if not signal.can_handle(case):
            continue
        confidence = signal.run(case)[0]
        if confidence > 0.0:  # rang buoc 2: chi bid da phat moi vao tham chieu
            values.append(float(confidence))
    return np.asarray(values, dtype=float)


def install_references(health: HealthMonitor, capabilities, train: pd.DataFrame,
                       feature_columns: list[str], *, stage: int = 2,
                       max_rows: int = 3000) -> list[ReferenceCoverage]:
    """Nap phan phoi tham chieu cho moi thanh phan co the giam sat duoc.

    Tra ve bao cao pham vi phu — thanh phan nao duoc giam sat, thanh phan nao khong,
    va ly do cu the. Bao cao nay phai duoc dua vao Chuong 5: mot bo giam sat chi phu
    duoc mot phan he thong thi ket qua do nhay chi noi ve phan do.
    """
    # Rang buoc 1: khop tong the voi luong duoc giam sat.
    pool = train[train["is_dissatisfied"]] if stage == 2 else train
    pool = pool.head(max_rows)

    coverage: list[ReferenceCoverage] = []

    # --- prediction: da co san predict_proba theo lo ---
    scores = capabilities.risk_model.predict_proba(pool)
    coverage.append(_install(health, Component.PREDICTION.value, "risk_score", scores))

    # --- nhom analyst cau truc ---
    for component, signal in (
        (Component.CAUSE_DELIVERY.value, capabilities.delivery),
    ):
        values = _signal_confidences(signal, pool, feature_columns)
        coverage.append(_install(health, component, "confidence", values))

    # --- nhom analyst van ban ---
    # `LexiconCauseHead` tra do tin cay HANG SO nen khong dung lam tham chieu duoc.
    # Day khong phai thieu sot cai dat ma la he qua cua ban tam thoi: mot dai luong
    # hang so khong mang thong tin de phat hien bat thuong. Se thay doi o T3.4.
    for component in (Component.CAUSE_QUALITY.value, Component.CAUSE_SERVICE.value):
        head = capabilities.cause_head
        if getattr(head, "is_placeholder", False):
            coverage.append(ReferenceCoverage(
                component, "confidence", 0, 0.0, False,
                "cause_head la ban tam thoi tra hang so — cho T3.4 (BERTimbau)",
            ))
        else:  # pragma: no cover — se dung khi T3.4 xong
            coverage.append(ReferenceCoverage(
                component, "confidence", 0, 0.0, False,
                "chua cai dat lay tham chieu cho head that",
            ))

    return coverage


def _install(health: HealthMonitor, component: str, metric: str,
             values: np.ndarray) -> ReferenceCoverage:
    """Nap mot tham chieu, hoac tu choi kem ly do."""
    n = len(values)
    variance = float(np.var(values)) if n else 0.0

    if n < MIN_REFERENCE_SAMPLES:
        return ReferenceCoverage(component, metric, n, variance, False,
                                 f"chi co {n} mau (< {MIN_REFERENCE_SAMPLES})")
    if variance < MIN_REFERENCE_VARIANCE:
        return ReferenceCoverage(component, metric, n, variance, False,
                                 "tham chieu gan nhu hang so — khong co tien de de ket luan")

    health.set_reference(component, metric, values)
    return ReferenceCoverage(component, metric, n, variance, True, "da nap tham chieu")
