"""3.4 Recommendation Agent.

Chuyển (prediction + root cause + analytics) thành các *ứng viên* hành động quản trị, có
chấm điểm. Đây mới là đề xuất thô: quyền chốt thuộc về DSS Rule Engine ở Layer 4, nơi
chính sách kinh doanh được áp lên. Tách đôi như vậy để phần "AI đề xuất" và phần "doanh
nghiệp quyết định" có thể thay đổi độc lập.
"""

from __future__ import annotations

from typing import Any

from mas_dss.common.base_agent import BaseAgent
from mas_dss.common.schemas import (
    ActionCandidate,
    CauseLabel,
    OrderCase,
    RiskLevel,
    Severity,
)

# Playbook hành động theo từng nhóm nguyên nhân, xếp theo mức độ can thiệp tăng dần.
PLAYBOOK: dict[CauseLabel, list[tuple[str, Severity]]] = {
    CauseLabel.DELIVERY: [
        ("proactive_delay_apology_and_tracking_update", Severity.MEDIUM),
        ("expedite_shipment_and_notify_customer", Severity.HIGH),
        ("audit_seller_fulfillment_sla", Severity.HIGH),
    ],
    CauseLabel.PRODUCT_QUALITY: [
        ("inspect_seller_and_flag_product_listing", Severity.HIGH),
        ("offer_return_or_replacement", Severity.MEDIUM),
    ],
    CauseLabel.CUSTOMER_SERVICE: [
        ("open_support_ticket_and_contact_customer", Severity.MEDIUM),
        ("assign_case_to_customer_service_review", Severity.HIGH),
    ],
    CauseLabel.PRICE: [
        ("review_freight_pricing_and_offer_voucher", Severity.MEDIUM),
        ("compensate_customer_with_discount", Severity.MEDIUM),
    ],
    CauseLabel.UNKNOWN: [
        ("assign_case_to_customer_service_review", Severity.MEDIUM),
    ],
}

RISK_WEIGHT = {RiskLevel.LOW: 0.2, RiskLevel.MEDIUM: 0.6, RiskLevel.HIGH: 1.0}


class RecommendationAgent(BaseAgent):
    name = "recommendation_agent"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    def process(self, cases: list[OrderCase]) -> list[OrderCase]:
        for case in cases:
            if not case.prediction:
                continue

            risk = case.prediction.risk_level
            cause = case.root_cause.cause_label if case.root_cause else CauseLabel.UNKNOWN
            cause_p = case.root_cause.cause_probability if case.root_cause else 0.0

            if risk == RiskLevel.LOW:
                case.candidates = [
                    ActionCandidate(action="no_action", severity=Severity.NONE, score=0.0)
                ]
                continue

            candidates: list[ActionCandidate] = []
            for action, severity in PLAYBOOK.get(cause, PLAYBOOK[CauseLabel.UNKNOWN]):
                # Điểm = mức rủi ro x độ tin cậy nguyên nhân — càng chắc chắn về cả hai,
                # hành động chuyên biệt càng đáng làm.
                score = RISK_WEIGHT[risk] * max(cause_p, 0.25)
                if severity in (Severity.HIGH, Severity.URGENT) and risk != RiskLevel.HIGH:
                    score *= 0.6  # đừng leo thang khi rủi ro mới ở mức trung bình
                candidates.append(
                    ActionCandidate(action=action, severity=severity, score=round(score, 4))
                )

            candidates.sort(key=lambda c: c.score, reverse=True)
            case.candidates = candidates
        return cases
