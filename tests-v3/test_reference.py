"""T7.3a — Phan phoi tham chieu cho nhom Analyst.

Phuc vu: RQ1(b) — pham vi phu cua bo giam sat.

Ba rang buoc duoc kiem tra o day deu la bai hoc truc tiep tu docs/methodology-log.md:
khop tong the (L15), chi lay bid da phat (L15), va tu choi khi khong co tien de (L14).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from masdss.capabilities.cause_head import LexiconCauseHead
from masdss.capabilities.delivery_signal import DeliverySignal
from masdss.capabilities.price_signal import PriceSignal
from masdss.core.components import Component
from masdss.system.reliability.health import HealthMonitor
from masdss.system.reliability.reference import (
    MIN_REFERENCE_SAMPLES,
    install_references,
    _install,
)

FEATURES = ["category", "freight_ratio", "delivery_delay_days", "price", "freight_value"]


def _frame(n: int = 1200) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "order_id": [f"o{i:05d}" for i in range(n)],
        "category": ["toys"] * n,
        "freight_ratio": rng.normal(0.2, 0.06, n),
        "delivery_delay_days": rng.normal(0.0, 12.0, n),
        "price": rng.normal(120.0, 40.0, n),
        "freight_value": rng.normal(15.0, 5.0, n),
        "review_content": [None] * n,
        "is_dissatisfied": [True] * n,
    })


class _Caps:
    def __init__(self, frame: pd.DataFrame) -> None:
        class Risk:
            cost_ms = 0.5

            def predict_proba(self, df):
                rng = np.random.default_rng(1)
                return rng.beta(2, 5, len(df))

        self.risk_model = Risk()
        self.delivery = DeliverySignal().fit(frame)
        self.price = PriceSignal().fit(frame)
        self.cause_head = LexiconCauseHead()


# --- Nap tham chieu ---

def test_reference_is_installed_for_components_with_enough_data() -> None:
    frame = _frame()
    health = HealthMonitor()
    coverage = install_references(health, _Caps(frame), frame, FEATURES)

    installed = {c.component for c in coverage if c.installed}
    assert Component.PREDICTION.value in installed
    assert Component.CAUSE_DELIVERY.value in installed


def test_placeholder_head_is_refused_with_an_explicit_reason() -> None:
    """Bai hoc L14: khong co tien de thi khong ket luan, va phai noi ro vi sao.

    `LexiconCauseHead` tra do tin cay hang so nen khong the lam tham chieu. Day
    khong phai thieu sot cai dat — day la gioi han that, va no phai duoc bao cao
    chu khong duoc lang le bo qua.
    """
    frame = _frame()
    coverage = install_references(HealthMonitor(), _Caps(frame), frame, FEATURES)
    text = {c.component: c for c in coverage
            if c.component in (Component.CAUSE_QUALITY.value, Component.CAUSE_SERVICE.value)}
    assert len(text) == 2
    for entry in text.values():
        assert not entry.installed
        assert "tam thoi" in entry.reason


def test_thin_reference_is_refused() -> None:
    """Duoi nguong mau thi tu choi, khong nap tham chieu keo."""
    health = HealthMonitor()
    result = _install(health, "cause_service", "confidence",
                      np.linspace(0.4, 0.9, MIN_REFERENCE_SAMPLES - 1))
    assert not result.installed
    assert "mau" in result.reason


def test_constant_reference_is_refused() -> None:
    """Bai hoc L14 o dang truc tiep nhat."""
    result = _install(HealthMonitor(), "cause_quality", "confidence",
                      np.full(MIN_REFERENCE_SAMPLES + 50, 0.55))
    assert not result.installed
    assert "hang so" in result.reason


def test_coverage_report_explains_every_component() -> None:
    """Bao cao phai giai thich TUNG thanh phan, ke ca thanh phan khong giam sat duoc.

    Mot bo giam sat chi phu duoc mot phan he thong thi ket qua do nhay chi noi ve
    phan do. Bao cao nay phai di kem moi con so RQ1(b) trong Chuong 5.
    """
    frame = _frame()
    coverage = install_references(HealthMonitor(), _Caps(frame), frame, FEATURES)
    # 4 thanh phan: prediction + ba analyst. Truoc 12/08 la 5 — `cause_price` da bi go.
    assert len(coverage) == 4
    for entry in coverage:
        assert entry.reason, f"{entry.component} khong co ly do"


# --- Rang buoc khop tong the (bai hoc L15) ---

def test_reference_matches_the_monitored_population() -> None:
    """Giai doan 2 chi giam sat don bat man, nen tham chieu cung phai la don bat man."""
    frame = _frame()
    frame.loc[frame.index[:600], "is_dissatisfied"] = False

    health = HealthMonitor()
    install_references(health, _Caps(frame), frame, FEATURES, stage=2)

    state = health._state(Component.PREDICTION.value, "risk_score")
    assert state.reference is not None
    assert len(state.reference) == 600, "tham chieu phai chi gom don bat man"


def test_reference_only_contains_emitted_bids() -> None:
    """Analyst chi gui PROPOSE khi vuot nguong; lan tra 0.0 khong vao luong giam sat.

    Dua chung vao tham chieu se lam lech phan phoi ve phia 0 va tao bao dong gia.
    """
    frame = _frame()
    health = HealthMonitor()
    install_references(health, _Caps(frame), frame, FEATURES)

    state = health._state(Component.CAUSE_DELIVERY.value, "confidence")
    assert state.reference is not None
    assert float(state.reference.min()) > 0.0
    assert len(state.reference) < len(frame), "khong phai case nao cung phat bid"
