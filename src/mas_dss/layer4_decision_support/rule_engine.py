"""4.1 DSS Rule Engine.

Áp tập luật nghiệp vụ (config/dss_rules.yaml) lên đầu ra của các agent, ưu tiên hành động
theo severity + priority + confidence, và chốt quyết định cuối cùng.

Biểu thức `when` được đánh giá bằng `eval` với `__builtins__` bị vô hiệu hóa và namespace
chỉ chứa các trường của OrderCase. Luật là do người quản trị hệ thống viết (trusted input),
không phải người dùng cuối — nhưng vẫn hạn chế phạm vi để tránh tai nạn.
"""

from __future__ import annotations

from typing import Any

import yaml

from mas_dss.common.base_agent import BaseAgent
from mas_dss.common.config import PROJECT_ROOT
from mas_dss.common.schemas import CaseStatus, Decision, OrderCase, Severity

SEVERITY_RANK = {
    Severity.NONE: 0,
    Severity.MONITOR: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.URGENT: 4,
}


class DSSRuleEngine(BaseAgent):
    name = "dss_rule_engine"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.cfg = config["dss"]
        with open(PROJECT_ROOT / self.cfg["rules_file"], encoding="utf-8") as f:
            self.rules = sorted(
                yaml.safe_load(f)["rules"], key=lambda r: r["priority"], reverse=True
            )
        self.log.info("đã nạp %d luật DSS", len(self.rules))

    def process(self, cases: list[OrderCase]) -> list[OrderCase]:
        for case in cases:
            case.decision = self.decide(case)
        return cases

    def decide(self, case: OrderCase) -> Decision:
        ns = case.rule_namespace()
        matched = [r for r in self.rules if self._evaluate(r, ns)]

        if not matched:
            return Decision(case_status=CaseStatus.MONITOR)

        actions, seen = [], set()
        for r in matched[: self.cfg["max_actions_per_case"]]:
            if r["action"] not in seen:
                actions.append(r["action"])
                seen.add(r["action"])

        top = max(matched, key=lambda r: SEVERITY_RANK[Severity(r["severity"])])
        severity = Severity(top["severity"])

        return Decision(
            matched_rules=[r["id"] for r in matched],
            actions=actions,
            severity=severity,
            escalate_to=top["escalate_to"],
            case_status=self._status(severity),
        )

    def _evaluate(self, rule: dict[str, Any], ns: dict[str, Any]) -> bool:
        try:
            return bool(eval(rule["when"], {"__builtins__": {}}, ns))  # noqa: S307
        except Exception as exc:
            # Luật lỗi (sai tên biến) không được phép làm sập pipeline — bỏ qua và ghi log.
            self.log.warning("luật %s lỗi: %s", rule["id"], exc)
            return False

    @staticmethod
    def _status(severity: Severity) -> CaseStatus:
        if severity in (Severity.URGENT, Severity.HIGH):
            return CaseStatus.URGENT
        return CaseStatus.MONITOR

    def rule_by_id(self, rule_id: str) -> dict[str, Any] | None:
        return next((r for r in self.rules if r["id"] == rule_id), None)
