"""4.2 Explanation Agent / Decision Trace.

Dựng lại chuỗi suy luận features → prediction → cause → action dưới dạng vừa máy đọc
(`steps`) vừa người đọc (`narrative`). Đây là thành phần trả lời cho yêu cầu "giải thích
được" của DSS: nhà quản lý phải hiểu *vì sao* hệ thống khuyến nghị hành động đó thì mới
tin và mới hành động.
"""

from __future__ import annotations

from typing import Any

from mas_dss.common.base_agent import BaseAgent
from mas_dss.common.schemas import DecisionTrace, OrderCase

from .rule_engine import DSSRuleEngine


class ExplanationAgent(BaseAgent):
    name = "explanation_agent"

    def __init__(self, config: dict[str, Any], rule_engine: DSSRuleEngine):
        super().__init__(config)
        self.rule_engine = rule_engine

    def process(self, cases: list[OrderCase]) -> list[OrderCase]:
        for case in cases:
            case.trace = self._build_trace(case)
        return cases

    def _build_trace(self, case: OrderCase) -> DecisionTrace:
        steps: list[dict[str, Any]] = []
        f = case.features

        steps.append(
            {
                "stage": "features",
                "agent": "preprocessing_agent",
                "detail": {
                    "delivery_delay_days": round(f.delivery_delay_days, 2),
                    "delivery_days": round(f.delivery_days, 2),
                    "freight_ratio": round(f.freight_ratio, 3),
                    "price": round(f.price, 2),
                    "product_category": f.product_category,
                },
            }
        )

        if case.analytics:
            steps.append(
                {
                    "stage": "analytics",
                    "agent": "analytics_agent",
                    "detail": {
                        "anomaly_flags": case.analytics.anomaly_flags,
                        "seller_late_rate": round(case.analytics.seller_late_rate, 3),
                        "category_complaint_rate": round(
                            case.analytics.category_complaint_rate, 3
                        ),
                    },
                }
            )

        if case.prediction:
            steps.append(
                {
                    "stage": "prediction",
                    "agent": "prediction_agent",
                    "detail": {
                        "risk_score": round(case.prediction.risk_score, 3),
                        "risk_level": case.prediction.risk_level.value,
                        "predicted_score": case.prediction.predicted_score,
                        "confidence": round(case.prediction.confidence, 3),
                        "model": case.prediction.model_name,
                    },
                }
            )

        if case.root_cause:
            steps.append(
                {
                    "stage": "root_cause",
                    "agent": "root_cause_agent",
                    "detail": {
                        "cause_label": case.root_cause.cause_label.value,
                        "cause_probability": round(case.root_cause.cause_probability, 3),
                        "evidence": case.root_cause.evidence,
                    },
                }
            )

        if case.decision:
            steps.append(
                {
                    "stage": "decision",
                    "agent": "dss_rule_engine",
                    "detail": {
                        "matched_rules": [
                            {
                                "id": rid,
                                "name": (self.rule_engine.rule_by_id(rid) or {}).get("name"),
                                "rationale": (self.rule_engine.rule_by_id(rid) or {}).get(
                                    "rationale"
                                ),
                            }
                            for rid in case.decision.matched_rules
                        ],
                        "actions": case.decision.actions,
                        "severity": case.decision.severity.value,
                        "escalate_to": case.decision.escalate_to,
                    },
                }
            )

        return DecisionTrace(steps=steps, narrative=self._narrate(case))

    @staticmethod
    def _narrate(case: OrderCase) -> str:
        if not case.prediction or not case.decision:
            return "Chưa đủ thông tin để giải thích."

        p, d = case.prediction, case.decision
        if not d.actions or d.actions == ["no_action"]:
            return (
                f"Đơn {case.order_id}: rủi ro không hài lòng {p.risk_score:.0%} "
                f"(mức {p.risk_level.value}) — không cần can thiệp."
            )

        cause = case.root_cause.cause_label.value if case.root_cause else "chưa xác định"
        cause_p = case.root_cause.cause_probability if case.root_cause else 0.0
        evidence = "; ".join(case.root_cause.evidence) if case.root_cause else ""
        rules = ", ".join(d.matched_rules)

        return (
            f"Đơn {case.order_id} được dự báo rủi ro không hài lòng {p.risk_score:.0%} "
            f"(mức {p.risk_level.value}, độ tin cậy {p.confidence:.0%}). "
            f"Nguyên nhân chính: {cause} ({cause_p:.0%})"
            + (f" — bằng chứng: {evidence}. " if evidence else ". ")
            + f"Luật {rules} được kích hoạt, đề xuất: {', '.join(d.actions)}. "
            f"Chuyển tới: {d.escalate_to}."
        )
