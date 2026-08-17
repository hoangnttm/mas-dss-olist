"""4.3 Alert & Case Management.

Tạo intervention case cho các đơn rủi ro, gán trạng thái monitor / urgent / resolved và
kết xuất ra CSV cho dashboard. Đây là đầu ra nghiệp vụ cuối cùng của hệ thống — thứ nhà
quản lý thực sự cầm để hành động, và là căn cứ so sánh với báo cáo tĩnh của MIS.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from mas_dss.common.base_agent import BaseAgent
from mas_dss.common.config import PROJECT_ROOT
from mas_dss.common.schemas import CaseStatus, OrderCase, Severity


class CaseManager(BaseAgent):
    name = "case_manager"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.cases: dict[str, dict[str, Any]] = {}

    def process(self, cases: list[OrderCase]) -> list[OrderCase]:
        for case in cases:
            if not case.decision or case.decision.severity == Severity.NONE:
                continue
            self.cases[case.order_id] = {
                "order_id": case.order_id,
                "seller_id": case.seller_id,
                "customer_id": case.customer_id,
                "risk_score": case.prediction.risk_score if case.prediction else None,
                "risk_level": case.prediction.risk_level.value if case.prediction else None,
                "predicted_score": case.prediction.predicted_score if case.prediction else None,
                "cause_label": case.root_cause.cause_label.value if case.root_cause else None,
                "cause_probability": case.root_cause.cause_probability if case.root_cause else None,
                "actions": "|".join(case.decision.actions),
                "matched_rules": "|".join(case.decision.matched_rules),
                "severity": case.decision.severity.value,
                "escalate_to": case.decision.escalate_to,
                "status": case.decision.case_status.value,
                "narrative": case.trace.narrative if case.trace else "",
                "product_category": case.features.product_category,
                "delivery_delay_days": case.features.delivery_delay_days,
                # Nhãn thật — chỉ để Layer 5 chấm điểm, dashboard không hiển thị.
                "actual_review_score": case.review_score,
                "actual_dissatisfied": case.is_dissatisfied,
            }
        return cases

    def resolve(self, order_id: str) -> None:
        if order_id in self.cases:
            self.cases[order_id]["status"] = CaseStatus.RESOLVED.value

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(list(self.cases.values()))

    def save(self, path: str | Path = "reports/results/intervention_cases.csv") -> Path:
        out = PROJECT_ROOT / path
        out.parent.mkdir(parents=True, exist_ok=True)
        df = self.to_frame()
        df.to_csv(out, index=False, encoding="utf-8-sig")
        urgent = int((df["status"] == CaseStatus.URGENT.value).sum()) if len(df) else 0
        self.log.info("đã tạo %d case (%d urgent) -> %s", len(df), urgent, out)
        return out
