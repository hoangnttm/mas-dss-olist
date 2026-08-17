"""Kiểm tra contract giữa các lớp: OrderCase phải chảy qua agent mà chỉ được *làm giàu*,
và Coordinator phải chịu được agent lỗi. Không cần dataset Olist để chạy các test này."""

from __future__ import annotations

from mas_dss.common.base_agent import BaseAgent
from mas_dss.common.config import load_config
from mas_dss.common.schemas import CauseLabel, OrderCase, OrderFeatures, Prediction, RiskLevel
from mas_dss.layer2_orchestration.coordinator import CoordinatorAgent
from mas_dss.layer3_analytics.recommendation_agent import RecommendationAgent


class ExplodingAgent(BaseAgent):
    name = "exploding_agent"

    def process(self, cases):
        raise RuntimeError("boom")


class TaggingAgent(BaseAgent):
    name = "tagging_agent"

    def process(self, cases):
        for c in cases:
            c.customer_id = "tagged"
        return cases


def make_cases(n: int = 3) -> list[OrderCase]:
    return [
        OrderCase(
            order_id=f"o{i}",
            features=OrderFeatures(price=100.0, delivery_delay_days=5.0),
            prediction=Prediction(risk_score=0.9, risk_level=RiskLevel.HIGH, confidence=0.8),
        )
        for i in range(n)
    ]


def test_rule_namespace_is_flat_and_complete():
    case = make_cases(1)[0]
    ns = case.rule_namespace()
    assert ns["risk_level"] == "high"           # enum đã được flatten thành str
    assert ns["delivery_delay_days"] == 5.0
    assert "price" in ns


def test_recommendation_agent_ranks_candidates_by_score():
    cfg = load_config()
    case = make_cases(1)[0]
    case.root_cause = None
    out = RecommendationAgent(cfg).process([case])
    assert out[0].candidates
    scores = [c.score for c in out[0].candidates]
    assert scores == sorted(scores, reverse=True)


def test_low_risk_case_gets_no_action():
    cfg = load_config()
    case = make_cases(1)[0]
    case.prediction = Prediction(risk_score=0.1, risk_level=RiskLevel.LOW)
    out = RecommendationAgent(cfg).process([case])
    assert [c.action for c in out[0].candidates] == ["no_action"]


def test_coordinator_survives_failing_agent():
    """Một agent chết không được kéo sập cả pipeline — các case vẫn đi tiếp."""
    cfg = load_config()
    coord = CoordinatorAgent(cfg, agents=[ExplodingAgent(cfg), TaggingAgent(cfg)])
    out = coord.run(make_cases(3))

    assert len(out) == 3
    assert all(c.customer_id == "tagged" for c in out)   # agent sau vẫn chạy
    failed = [r for r in coord.results if not r.ok]
    assert failed and failed[0].agent == "exploding_agent"


def test_coordinator_ablation_disables_agent():
    cfg = load_config()
    coord = CoordinatorAgent(
        cfg, agents=[TaggingAgent(cfg)], disabled_agents=["tagging_agent"]
    )
    out = coord.run(make_cases(2))
    assert all(c.customer_id != "tagged" for c in out)


def test_coordinator_records_latency_per_agent():
    cfg = load_config()
    coord = CoordinatorAgent(cfg, agents=[TaggingAgent(cfg)])
    coord.run(make_cases(2))
    assert "tagging_agent" in coord.latency_by_agent()
    assert coord.pipeline_latency_ms > 0
