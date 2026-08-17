"""WP0 — Tac tu khung cho lat cat doc (Dot 0).

Phuc vu: kiem chung nam giao dien o technical-plan-v3.md §5 TRUOC khi xay bat ky
mo hinh hoc may nao.

Ba tac tu nay se bi thay o Dot 2 boi agents/analytics.py, agents/prediction.py,
agents/rule_agent.py. Chung ton tai de chung minh mot dieu duy nhat: chuoi
core -> runtime -> orchestrator -> message_log -> explain da noi dung.

Moi tac tu duoi ~80 dong va KHONG chua logic hoc may — do la rang buoc thiet ke,
khong phai vi day la ban khung.
"""

from __future__ import annotations

from masdss.capabilities.base import StubContext, StubRisk
from masdss.core.message import Message, Performative
from masdss.core.ontology import Cause, RiskLevel
from masdss.runtime.actor import Agent, Policy


class AnalyticsAgent(Agent):
    """Chi bao ngu canh. Luon chay vi re."""

    agent_id = "Analytics"
    cost_class = "cheap"

    def __init__(self) -> None:
        super().__init__()
        self.capability = StubContext()
        self.cost_ms = self.capability.cost_ms

    async def act(self, message: Message) -> Message:
        context = self.capability.run(message.payload)
        return message.reply(
            sender=self.agent_id,
            performative=Performative.INFORM,
            content={"context": context},
            ontology="context",
        )


class PredictionAgent(Agent):
    """Du bao rui ro. Phat REFUSE khi dac trung nam ngoai phan phoi (DP3)."""

    agent_id = "Prediction"
    cost_class = "cheap"

    def __init__(self, ood_case_ids: frozenset[str] = frozenset()) -> None:
        super().__init__()
        self.capability = StubRisk()
        self.cost_ms = self.capability.cost_ms
        self._ood = ood_case_ids

    def decide_policy(self, message: Message) -> Policy:
        case = message.payload
        return Policy.REFUSE if case.case_id in self._ood else Policy.ACT

    def refusal_reason(self, message: Message) -> str:
        return "dac trung nam ngoai phan phoi huan luyen (OOD)"

    async def act(self, message: Message) -> Message:
        score = self.capability.run(message.payload)
        level = RiskLevel.HIGH if score >= 0.7 else (
            RiskLevel.MEDIUM if score >= 0.4 else RiskLevel.LOW
        )
        return message.reply(
            sender=self.agent_id,
            performative=Performative.INFORM,
            content={"risk_score": score, "risk": int(level)},
            ontology="prediction",
        )


class RuleAgent(Agent):
    """Chot hanh dong. Cuong che DP1: he suy giam thi bat buoc chuyen cho nguoi."""

    agent_id = "RuleAgent"
    cost_class = "cheap"

    async def act(self, message: Message) -> Message:
        risk = message.content.get("risk", int(RiskLevel.LOW))
        causes = message.content.get("causes", [])
        degradation = message.content.get("degradation_level", 0)
        at_t4 = message.content.get("decision_point") == "T4"

        # DP1: he suy giam thi bat buoc chuyen giao.
        # Rieng o T4, quy ket that bai (khong nguyen nhan nao) cung phai chuyen giao.
        if degradation > 0 or (at_t4 and not causes):
            action = "escalate_to_human"
        elif risk >= int(RiskLevel.HIGH):
            action = "proactive_apology_with_coupon"
        elif risk >= int(RiskLevel.MEDIUM):
            action = "preemptive_ticket_open"
        else:
            action = "no_action"

        return message.reply(
            sender=self.agent_id,
            performative=Performative.INFORM,
            content={"action": action, "cause_count": len(causes) or 0,
                     "unknown": Cause.UNKNOWN.value if not causes else None},
            ontology="decision",
        )
