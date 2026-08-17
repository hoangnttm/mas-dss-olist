"""WP8 / T8.1–T8.5 — Tang chiu loi.

Phuc vu: RQ1(a) hong am tham, RQ1(b) do nhay va do tre phat hien.
"""

from __future__ import annotations

import numpy as np
import pytest

from masdss.core.errors import DeterministicError, GuardViolation, TransientError
from masdss.core.message import Message, Performative
from masdss.config import deterministic_uuid
from masdss.system.reliability.breaker import CircuitState, Supervisor
from masdss.system.reliability.guards import (
    GuardChain,
    SchemaGuard,
    StatisticalGuard,
    default_chain,
)
from masdss.system.reliability.health import HealthMonitor

CONV = deterministic_uuid("test", "reliability")


def _reply(**content) -> Message:
    return Message(
        msg_id=deterministic_uuid("m", str(content)), conversation_id=CONV, trace_id=CONV,
        sender="Prediction", receiver="Orchestrator",
        performative=Performative.INFORM, ontology="prediction", content=content,
    )


# =============== T8.1 Schema guard ===============

def test_schema_guard_rejects_out_of_range_probability() -> None:
    guard = SchemaGuard()
    assert guard.check("prediction", _reply(risk_score=0.5)).ok
    assert not guard.check("prediction", _reply(risk_score=1.7)).ok
    assert not guard.check("prediction", _reply(risk_score="cao")).ok


def test_schema_guard_rejects_invalid_risk_level() -> None:
    assert not SchemaGuard().check("prediction", _reply(risk=9)).ok


def test_schema_guard_rejects_bid_without_evidence() -> None:
    """Mot bid tran khong kiem chung duoc — no khong duoc phep vao blackboard."""
    bid = Message(
        msg_id=deterministic_uuid("m", "bid"), conversation_id=CONV, trace_id=CONV,
        sender="DeliveryAnalyst", receiver="Orchestrator",
        performative=Performative.PROPOSE, ontology="bid",
        content={"cause": "delivery", "confidence": 0.8, "evidence": []},
    )
    assert not SchemaGuard().check("cause_delivery", bid).ok


# =============== T8.2 Health monitor ===============

def test_variance_check_requires_a_reference() -> None:
    """Mot dai luong hang so DO THIET KE khong phai la loi.

    Truoc khi co rang buoc nay, guard danh dau `LexiconCauseHead` (tra ve hang so
    0,55) la hong, va 93,7% case tren lan chay khoe bi suy giam.
    """
    health = HealthMonitor()
    alerts = []
    for _ in range(60):
        alerts += health.observe("cause_quality", "confidence", 0.55)
    assert not alerts, "khong co tham chieu thi khong duoc ket luan gi"


def test_variance_check_fires_when_reference_says_it_should_vary() -> None:
    health = HealthMonitor()
    health.set_reference("prediction", "risk_score", np.linspace(0.0, 1.0, 500))
    alerts = []
    for _ in range(60):
        alerts += health.observe("prediction", "risk_score", 0.5)
    assert alerts
    assert "dung yen bat thuong" in alerts[0].detail


def test_psi_needs_enough_observations() -> None:
    """Cua so nho lam PSI bung no — day la nguyen nhan cua 2,911 tren du lieu khoe."""
    health = HealthMonitor()
    rng = np.random.default_rng(0)
    health.set_reference("prediction", "risk_score", rng.beta(2, 5, 2000))
    alerts = []
    for value in rng.beta(2, 5, 50):
        alerts += health.observe("prediction", "risk_score", value)
    assert not alerts, "50 quan sat la qua it de ket luan ve phan phoi"


def test_psi_stays_quiet_on_the_same_distribution() -> None:
    health = HealthMonitor()
    rng = np.random.default_rng(1)
    health.set_reference("prediction", "risk_score", rng.beta(2, 5, 3000))
    alerts = []
    for value in rng.beta(2, 5, 300):
        alerts += health.observe("prediction", "risk_score", value)
    assert not alerts, "cung phan phoi ma van bao dong -> bao dong gia"


def test_psi_detects_a_shifted_distribution() -> None:
    health = HealthMonitor()
    rng = np.random.default_rng(2)
    health.set_reference("prediction", "risk_score", rng.beta(2, 5, 3000))
    alerts = []
    for value in rng.beta(5, 2, 300):  # lech han sang phia cao
        alerts += health.observe("prediction", "risk_score", value)
    assert alerts
    assert "PSI" in alerts[0].detail


def test_detection_delay_is_recorded() -> None:
    """Do tre phat hien la mot trong ba con so RQ1 goi la ket qua thuc nghiem that."""
    health = HealthMonitor()
    health.set_reference("prediction", "risk_score", np.linspace(0.0, 1.0, 500))
    for _ in range(60):
        health.observe("prediction", "risk_score", 0.5)
    assert health.detection_delay("prediction") == 20
    assert health.detection_delay("cause_service") is None


# =============== Trang thai suc khoe la ben vung ===============

def test_unhealthy_component_stays_blocked() -> None:
    """Canh bao phat mot lan (de do do tre), nhung chan thi phai chan mai.

    Neu guard chi chan dung case dau tien, 299 case sau van hong am tham y nguyen.
    """
    health = HealthMonitor()
    health.set_reference("prediction", "risk_score", np.linspace(0.0, 1.0, 500))
    guard = StatisticalGuard(health)

    blocked = sum(0 if guard.check("prediction", _reply(risk_score=0.5)).ok else 1
                  for _ in range(60))
    assert blocked >= 40, "thanh phan da bi ket luan hong phai bi chan lien tuc"


# =============== T8.3, T8.4 Breaker va retry ===============

def test_breaker_opens_after_threshold() -> None:
    supervisor = Supervisor(failure_threshold=3, cooldown_calls=5)
    breaker = supervisor.breaker("prediction")
    for _ in range(3):
        assert breaker.allow()
        breaker.record_failure()
    assert breaker.state is CircuitState.OPEN
    assert not breaker.allow(), "mach mo thi khong duoc goi nua"


def test_breaker_half_opens_after_cooldown_then_closes_on_success() -> None:
    supervisor = Supervisor(failure_threshold=2, cooldown_calls=3)
    breaker = supervisor.breaker("prediction")
    breaker.record_failure()
    breaker.record_failure()
    for _ in range(3):
        breaker.allow()
    assert breaker.state is CircuitState.HALF_OPEN
    breaker.record_success()
    assert breaker.state is CircuitState.CLOSED


def test_deterministic_errors_are_never_retried() -> None:
    """Model chet thi thu ba lan cung chet ba lan — day la loi cua ban v0."""
    supervisor = Supervisor(max_transient_retries=3)
    assert not supervisor.should_retry(DeterministicError("model hong"), attempt=0)


def test_transient_errors_are_retried_up_to_a_limit() -> None:
    supervisor = Supervisor(max_transient_retries=2)
    assert supervisor.should_retry(TransientError("I/O"), attempt=0)
    assert supervisor.should_retry(TransientError("I/O"), attempt=1)
    assert not supervisor.should_retry(TransientError("I/O"), attempt=2)


# =============== Chuoi guard ===============

def test_guard_violation_is_a_deterministic_error() -> None:
    """Nho quan he thua ke nay ma orchestrator khong phai sua mot dong nao.

    Orchestrator da co san chinh sach cho `DeterministicError`: ha hai bac suy giam
    va di tiep. `GuardViolation` thua ke tu do nen tang chiu loi cam vao duoc ma
    khong dung toi lop dieu phoi.
    """
    assert issubclass(GuardViolation, DeterministicError)


def test_guard_chain_records_violations() -> None:
    chain = GuardChain(guards=(SchemaGuard(),))
    with pytest.raises(GuardViolation):
        chain.check("prediction", _reply(risk_score=5.0))
    assert len(chain.report()) == 1
    assert chain.report()[0]["guard"] == "schema"


def test_default_chain_passes_healthy_output() -> None:
    chain = default_chain(HealthMonitor())
    for value in np.linspace(0.1, 0.9, 30):
        chain.check("prediction", _reply(risk_score=float(value)))
    assert chain.report() == []
