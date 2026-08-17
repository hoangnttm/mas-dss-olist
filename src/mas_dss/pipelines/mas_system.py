"""Lắp ráp hệ MAS-DSS hoàn chỉnh (Layer 2 → 4).

Tách riêng khỏi các script chạy để cả `run_pipeline` lẫn `run_evaluation` (kể cả các biến
thể ablation) đều dựng hệ thống theo cùng một cách — không có chuyện hai đường chạy khác
nhau âm thầm dùng cấu hình khác nhau.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import joblib

from mas_dss.common.config import PROJECT_ROOT
from mas_dss.common.schemas import OrderCase
from mas_dss.layer2_orchestration.coordinator import CoordinatorAgent
from mas_dss.layer3_analytics.analytics_agent import AnalyticsAgent
from mas_dss.layer3_analytics.prediction_agent import PredictionAgent
from mas_dss.layer3_analytics.recommendation_agent import RecommendationAgent
from mas_dss.layer3_analytics.root_cause_agent import RootCauseAgent
from mas_dss.layer4_decision_support.case_manager import CaseManager
from mas_dss.layer4_decision_support.explanation_agent import ExplanationAgent
from mas_dss.layer4_decision_support.rule_engine import DSSRuleEngine

# Tên ablation -> agent bị tắt (mục 3.2.5b, causal validity).
ABLATIONS: dict[str, tuple[str, ...]] = {
    "full": (),
    "no_root_cause_agent": ("root_cause_agent",),
    "no_recommendation_agent": ("recommendation_agent",),
    "no_analytics_features": ("analytics_agent",),
}


@dataclass
class MASSystem:
    coordinator: CoordinatorAgent
    case_manager: CaseManager

    def run(self, cases: list[OrderCase]) -> list[OrderCase]:
        return self.coordinator.run(cases)


def build_mas_system(cfg: dict[str, Any], disabled: Iterable[str] = ()) -> MASSystem:
    models = PROJECT_ROOT / cfg["paths"]["models"]

    analytics = AnalyticsAgent(cfg)
    stats = joblib.load(models / "analytics_stats.pkl")
    analytics.seller_stats = stats["seller_stats"]
    analytics.category_stats = stats["category_stats"]
    analytics.global_complaint_rate = stats["global_complaint_rate"]

    prediction = PredictionAgent(cfg).load(models / "prediction_agent.pkl")
    root_cause = RootCauseAgent(cfg).load(models / "root_cause_agent.pkl")
    recommendation = RecommendationAgent(cfg)

    rule_engine = DSSRuleEngine(cfg)
    explanation = ExplanationAgent(cfg, rule_engine)
    case_manager = CaseManager(cfg)

    coordinator = CoordinatorAgent(
        cfg,
        agents=[
            analytics,       # 3.1
            prediction,      # 3.2
            root_cause,      # 3.3
            recommendation,  # 3.4
            rule_engine,     # 4.1
            explanation,     # 4.2
            case_manager,    # 4.3
        ],
        disabled_agents=disabled,
    )
    return MASSystem(coordinator=coordinator, case_manager=case_manager)
