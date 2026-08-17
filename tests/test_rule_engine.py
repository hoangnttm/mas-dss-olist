"""Rule Engine là nơi chính sách kinh doanh được mã hóa — nếu nó sai, mọi khuyến nghị
đều sai. Test ở đây khóa lại hành vi của từng luật quan trọng và của phần ưu tiên."""

from __future__ import annotations

import pytest

from mas_dss.common.config import load_config
from mas_dss.common.schemas import (
    AnalyticsContext,
    CauseLabel,
    CaseStatus,
    OrderCase,
    OrderFeatures,
    Prediction,
    RiskLevel,
    RootCause,
    Severity,
)
from mas_dss.layer4_decision_support.rule_engine import DSSRuleEngine


@pytest.fixture(scope="module")
def engine() -> DSSRuleEngine:
    return DSSRuleEngine(load_config())


def make_case(
    risk: RiskLevel,
    cause: CauseLabel,
    cause_p: float = 0.8,
    delay: float = 0.0,
    freight_ratio: float = 0.1,
    seller_late_rate: float = 0.0,
) -> OrderCase:
    return OrderCase(
        order_id="test-order",
        features=OrderFeatures(delivery_delay_days=delay, freight_ratio=freight_ratio, price=100.0),
        analytics=AnalyticsContext(is_late=delay > 0, seller_late_rate=seller_late_rate),
        prediction=Prediction(risk_score=0.9, risk_level=risk, confidence=0.8),
        root_cause=RootCause(cause_label=cause, cause_probability=cause_p),
    )


def test_severe_delay_escalates_to_logistics(engine):
    d = engine.decide(make_case(RiskLevel.HIGH, CauseLabel.DELIVERY, delay=10))
    assert "R01" in d.matched_rules
    assert d.actions[0] == "expedite_shipment_and_notify_customer"
    assert d.severity == Severity.URGENT
    assert d.escalate_to == "logistics_manager"
    assert d.case_status == CaseStatus.URGENT


def test_low_risk_yields_no_action(engine):
    d = engine.decide(make_case(RiskLevel.LOW, CauseLabel.UNKNOWN, cause_p=0.9))
    assert d.actions == ["no_action"]
    assert d.severity == Severity.NONE
    assert d.case_status == CaseStatus.MONITOR


def test_product_quality_routes_to_seller_team(engine):
    d = engine.decide(make_case(RiskLevel.HIGH, CauseLabel.PRODUCT_QUALITY, cause_p=0.7))
    assert "R03" in d.matched_rules
    assert d.escalate_to == "seller_quality_team"


def test_uncertain_cause_falls_back_to_human_review(engine):
    """Rủi ro cao nhưng không biết nguyên nhân => phải đẩy cho người, không tự hành động."""
    d = engine.decide(make_case(RiskLevel.HIGH, CauseLabel.UNKNOWN, cause_p=0.2))
    assert "R06" in d.matched_rules
    assert "assign_case_to_customer_service_review" in d.actions


def test_actions_are_capped(engine):
    cfg = load_config()
    d = engine.decide(
        make_case(RiskLevel.HIGH, CauseLabel.DELIVERY, delay=12, seller_late_rate=0.6)
    )
    assert len(d.actions) <= cfg["dss"]["max_actions_per_case"]


def test_broken_rule_does_not_crash_pipeline(engine):
    engine.rules.insert(0, {"id": "RX", "when": "nonexistent_var > 1", "action": "x",
                            "severity": "high", "escalate_to": "none", "priority": 999})
    try:
        d = engine.decide(make_case(RiskLevel.LOW, CauseLabel.UNKNOWN))
        assert "RX" not in d.matched_rules      # luật lỗi bị bỏ qua, không làm sập
    finally:
        engine.rules.pop(0)
