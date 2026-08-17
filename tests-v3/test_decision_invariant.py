"""WP0 / T5.3 — Bat bien DP1 tren Decision.

Phuc vu: RQ2 (trung thuc ve do tin cay), RQ1 (khong hong am tham).

DP1: "He thong khong bao gio duoc im lang cho ra quyet dinh rac."
Cuong che: degradation_level > 0  ==>  needs_human_review is True.
"""

from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

from masdss.config import deterministic_uuid
from masdss.core.decision import DegradedAutonomyError, Decision
from masdss.core.ontology import (
    Action,
    Cause,
    CauseAssignment,
    DecisionPoint,
    Evidence,
    RiskLevel,
)

CONV = deterministic_uuid("test", "conv")
EV = (Evidence(kind="delivery_delay", detail="tre 9 ngay", value=9.0),)
ONE_CAUSE = (CauseAssignment(cause=Cause.DELIVERY, probability=0.8, evidence=EV),)


def _make(**kwargs):
    base = dict(
        case_id="c1",
        decision_point=DecisionPoint.T4,
        risk=RiskLevel.HIGH,
        causes=ONE_CAUSE,
        action=Action(name="preemptive_ticket_open"),
        degradation_level=0,
        needs_human_review=False,
        conversation_id=CONV,
    )
    base.update(kwargs)
    return Decision(**base)


def test_degradation_level_has_no_default() -> None:
    """Nguoi viet ma BUOC PHAI khai bao muc suy giam o moi noi tao Decision."""
    with pytest.raises(TypeError):
        Decision(  # type: ignore[call-arg]
            case_id="c1",
            decision_point=DecisionPoint.T4,
            risk=RiskLevel.HIGH,
            causes=ONE_CAUSE,
            action=Action(name="x"),
            needs_human_review=False,
            conversation_id=CONV,
        )


@given(level=st.integers(min_value=1, max_value=3))
def test_degraded_decision_must_require_human_review(level: int) -> None:
    with pytest.raises(DegradedAutonomyError):
        _make(degradation_level=level, needs_human_review=False)


@given(level=st.integers(min_value=1, max_value=3))
def test_degraded_decision_is_valid_when_escalated(level: int) -> None:
    decision = _make(degradation_level=level, needs_human_review=True)
    assert decision.needs_human_review


def test_no_cause_must_escalate() -> None:
    """cause = unknown la hanh vi DUNG ve tri thuc luan, nhung phai giao cho nguoi."""
    with pytest.raises(DegradedAutonomyError):
        _make(causes=(), needs_human_review=False)


def test_two_causes_require_multi_cause_flag() -> None:
    """DP2: co hai nguyen nhan ma khong gan co la mat thong tin CNP sinh ra de bat."""
    two = ONE_CAUSE + (
        CauseAssignment(
            cause=Cause.QUALITY,
            probability=0.6,
            evidence=(Evidence(kind="text_span", detail="quebrado"),),
        ),
    )
    with pytest.raises(ValueError):
        _make(causes=two, multi_cause=False)
    assert _make(causes=two, multi_cause=True).multi_cause


def test_degradation_level_out_of_range_rejected() -> None:
    with pytest.raises(ValueError):
        _make(degradation_level=4, needs_human_review=True)


def test_canonical_row_has_no_timestamp() -> None:
    """Tep dau ra chinh tac khong duoc chua dau thoi gian hay do tre."""
    row = _make().to_row()
    forbidden = {"timestamp", "created_at", "duration_ms", "latency_ms", "elapsed"}
    assert not (set(row) & forbidden)
