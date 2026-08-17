"""WP7 — Policy Critic va Arbiter: chuoi tranh bien co can cu.

Phuc vu: RQ2 (chuoi ra quyet dinh), RQ1 (mot nhanh ablation).

KHAC BIET VE MAT TRI THUC LUAN, day la diem quan trong nhat cua hai lop nay:

    Critic KHONG tuyen bo "hanh dong nay se khong hieu qua". No khong biet duoc —
    Olist khong ghi nhan hanh dong nao da duoc ap dung, nen khong ton tai bien
    treatment de uoc luong hieu qua (rang buoc C1).

    Critic tuyen bo "hanh dong nay VI PHAM RANG BUOC X, do duoc ngay bay gio".
    Yeu hon mot engine huu dung ky vong, nhung DUNG — va van ablation duoc: tat
    Critic di roi do ty le can thiep thua tang bao nhieu.

Arbiter phan xu bang THU TU UU TIEN KHAI BAO TRONG YAML, khong bang ham huu dung
ky vong, vi cung khong uoc luong duoc trong so bang tien.
"""

from __future__ import annotations

from masdss.core.message import Message, Performative
from masdss.core.ontology import RiskLevel
from masdss.runtime.actor import Agent, Policy


class PolicyCriticAgent(Agent):
    """Kiem tra rang buoc tren de xuat cua Recommendation."""

    agent_id = "PolicyCritic"
    cost_class = "cheap"
    cost_ms = 0.1

    def __init__(self, engine) -> None:
        super().__init__()
        self.engine = engine
        self.constraints = {c["id"]: c for c in getattr(engine, "constraints", [])}

    def decide_policy(self, message: Message) -> Policy:
        return Policy.ACT if message.content.get("proposal") else Policy.REFUSE

    def refusal_reason(self, message: Message) -> str:
        return "khong co de xuat nao de phan bien"

    async def act(self, message: Message) -> Message:
        violated = self._check(message.content, message.payload)
        performative = Performative.CHALLENGE if violated else Performative.INFORM
        return message.reply(
            sender=self.agent_id,
            performative=performative,
            content={"challenged": bool(violated), "violated": violated},
            ontology="critique",
        )

    def _check(self, content: dict, case) -> list[str]:
        violated: list[str] = []
        proposal = content.get("proposal") or {}
        action = proposal.get("candidate_action")

        if content.get("degradation_level", 0) > 0:
            violated.append("degraded_system")

        risk = content.get("risk") or 0
        if risk >= int(RiskLevel.HIGH) and not proposal.get("causes"):
            violated.append("internal_contradiction")

        rule = self.constraints.get("cost_exceeds_order_value")
        if rule and action:
            order_value = float(case.features.get("price") or 0) + \
                float(case.features.get("freight_value") or 0)
            cost = self.engine.cost_of(action)
            if order_value > 0 and cost > order_value * float(rule["max_cost_ratio"]):
                violated.append("cost_exceeds_order_value")

        rule = self.constraints.get("weak_evidence")
        if rule:
            strongest = float(proposal.get("max_probability") or 0.0)
            if proposal.get("causes") and strongest < float(rule["min_cause_probability"]):
                violated.append("weak_evidence")

        return violated


class ArbiterAgent(Agent):
    """Phan xu bat dong Recommendation <-> Critic.

    Chi so sinh ra tu day: ty le Arbiter dung ve phia Critic — cho biet Critic co
    dang phan bien CO LY hay chi on ao.
    """

    agent_id = "Arbiter"
    cost_class = "cheap"
    cost_ms = 0.05

    def __init__(self, engine) -> None:
        super().__init__()
        self.priority = tuple(getattr(engine, "arbitration_priority", ()))

    def decide_policy(self, message: Message) -> Policy:
        return Policy.ACT if message.content.get("violated") else Policy.REFUSE

    def refusal_reason(self, message: Message) -> str:
        return "khong co bat dong nao can phan xu"

    async def act(self, message: Message) -> Message:
        violated = list(message.content.get("violated", []))
        decisive = next((c for c in self.priority if c in violated), violated[0])
        # Moi vi pham trong danh sach uu tien deu du nghiem trong de chuyen giao.
        return message.reply(
            sender=self.agent_id,
            performative=Performative.INFORM,
            content={"sided_with": "critic", "decisive_constraint": decisive,
                     "override_action": "escalate_to_human"},
            ontology="arbitration",
        )
