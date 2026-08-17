"""WP6 / T6.5, T6.7 — Analytics, Prediction, Recommendation, RuleAgent, CaseManager.

Phuc vu: RQ2 (chuoi quyet dinh), RQ1 (cuong che DP1).

Moi tac tu duoi ~80 dong va khong chua logic hoc may — do la rang buoc thiet ke
(technical-plan-v3.md §3), khong phai vi chung don gian.
"""

from __future__ import annotations

from masdss.core.message import Message, Performative
from masdss.core.ontology import Cause, RiskLevel
from masdss.runtime.actor import Agent, Policy


def _so(value) -> float | None:
    """Ep ve float JSON hoa duoc. NaN va thieu deu tra None.

    Dac trung den tu mot dong pandas nen chung la scalar numpy; `json.dumps` tu choi
    kieu do, va `NaN` thi sinh ra JSON khong hop le. Nhat ky message phai doc lai
    duoc nen phep ep nay la bat buoc, khong phai lam dep.
    """
    if value is None:
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return None if out != out else out


class AnalyticsAgent(Agent):
    """Chi bao ngu canh. Re, luon chay.

    DAU RA CUA TAC TU NAY DUOC TANG QUYET DINH DUNG THAT — no di vao `content` cua
    message va tu do vao `facts_from()`. Truoc 13/08 no chi duoc ghi vao blackboard
    roi khong ai doc, nen Analytics chay ma dong gop bang khong.

    `is_late` PHAI KHOA THEO MOC. `delivery_delay_days` la dac trung T4; o T3 no
    khong duoc cap nen co do luon False — sai im lang tren 300/300 don. Tai T3, thu
    quan sat duoc la `days_to_deadline`: am nghia la DA qua han ngay tai luc ra
    quyet dinh.
    """

    agent_id = "Analytics"
    cost_class = "cheap"
    cost_ms = 0.2

    async def act(self, message: Message) -> Message:
        case = message.payload
        f = case.features
        d2d = _so(f.get("days_to_deadline"))
        delay = _so(f.get("delivery_delay_days"))       # chi co o T4

        if delay is not None:
            is_late = delay > 0                          # T4: ket cuc da biet
        else:
            is_late = d2d is not None and d2d < 0        # T3: tien do quan sat duoc

        return message.reply(
            sender=self.agent_id,
            performative=Performative.INFORM,
            content={"context": {
                "tier": "A" if case.has_text_evidence else "B",
                "category": str(f.get("category", "unknown")),
                "is_late": bool(is_late),
                "delivery_state": _so(f.get("delivery_state")),
                "days_to_deadline": d2d,
                "order_value": round((_so(f.get("price")) or 0.0)
                                     + (_so(f.get("freight_value")) or 0.0), 2),
            }},
            ontology="context",
        )


class PredictionAgent(Agent):
    """Du bao rui ro. Phat REFUSE khi dac trung nam ngoai phan phoi huan luyen.

    Quyen tu choi o day la DP3: mot du bao tu tin tren du lieu chua tung thay gay
    hai hon la khong du bao.
    """

    agent_id = "Prediction"
    cost_class = "cheap"

    def __init__(self, risk_model, ood_detector=None) -> None:
        super().__init__()
        self.risk_model = risk_model
        self.ood = ood_detector
        self.cost_ms = risk_model.cost_ms

    def decide_policy(self, message: Message) -> Policy:
        case = message.payload
        if not self.risk_model.can_handle(case):
            return Policy.REFUSE
        if self.ood is not None and self.ood.can_handle(case) and self.ood.run(case):
            return Policy.REFUSE
        return Policy.ACT

    def refusal_reason(self, message: Message) -> str:
        return "dac trung nam ngoai phan phoi huan luyen (OOD)"

    async def act(self, message: Message) -> Message:
        score = self.risk_model.run(message.payload)
        level = self.risk_model.to_risk_level(score)
        # `risk_thresholds` di kem vi HAI ly do doc lap, va ca hai deu quan trong.
        #
        #   1. DP4 — nhat ky phai tu giai thich duoc. Muc `risk` la mot gia tri SUY RA
        #      tu `risk_score`; khong co nguong thi mot nguoi doc nhat ky khong kiem
        #      tra lai duoc phep suy do.
        #
        #   2. Tinh CONG BANG cua phep tiem loi. `risk_score` va `risk` la nguon va
        #      dan xuat cua cung mot dai luong. Bo tiem Byzantine dau doc `risk_score`;
        #      neu `risk` khong duoc suy lai thi loi KHONG toi duoc duong quyet dinh
        #      cua MAS-DSS, trong khi voi doi chung don khoi no toi — vi o do phep suy
        #      xay ra SAU diem tiem. Khi ay ty le "hong am tham 0,0%" cua MAS o nhom
        #      byzantine khong do kha nang chiu loi, no chi phan anh CHO DAT BO TIEM.
        #      Do dung la loi L12 ma nghien cuu da cam ket tranh.
        #
        # Do duoc truoc khi sua, 200 case, kich ban `byz_gross_k2`, tang chiu loi TAT:
        #     phan bo muc rui ro cua MAS  {0: 122, 1: 50, 2: 28}  — Y HET duong khoe
        #     phan bo muc rui ro cua Mono {2: 200}                — hong toan bo
        low, high = self.risk_model.risk_thresholds
        return message.reply(
            sender=self.agent_id,
            performative=Performative.INFORM,
            content={"risk_score": round(float(score), 6), "risk": int(level),
                     "risk_thresholds": [round(float(low), 6), round(float(high), 6)]},
            ontology="prediction",
        )


class RecommendationAgent(Agent):
    """Sinh ung vien hanh dong tu tap nguyen nhan da duoc chap nhan.

    KHONG tuyen bo hanh dong se hieu qua — Olist khong co bien treatment (rang
    buoc C1). No chi de xuat hanh dong PHU HOP voi nguyen nhan.
    """

    agent_id = "Recommendation"
    cost_class = "cheap"
    cost_ms = 0.1

    def __init__(self, engine) -> None:
        super().__init__()
        self.engine = engine

    def decide_policy(self, message: Message) -> Policy:
        return Policy.ACT if message.content.get("causes") else Policy.REFUSE

    def refusal_reason(self, message: Message) -> str:
        return "chua co nguyen nhan nao vuot nguong — khong co co so de de xuat"

    async def act(self, message: Message) -> Message:
        from masdss.capabilities.rules import facts_from

        content = message.content
        causes = list(content.get("causes", []))

        # Chay thu rule engine de co HANH DONG UNG VIEN. Critic can biet hanh dong
        # cu the thi moi kiem tra duoc rang buoc chi phi so voi gia tri don.
        candidate = self.engine.decide(facts_from(
            risk=content.get("risk") or 0,
            causes=causes,
            degradation_level=content.get("degradation_level", 0),
            decision_point=content.get("decision_point", "T4"),
            context=content.get("context"),
        )).action

        return message.reply(
            sender=self.agent_id,
            performative=Performative.INFORM,
            content={"proposal": {
                "causes": causes,
                "n_causes": len(set(causes)),
                "candidate_action": candidate,
                "max_probability": content.get("max_cause_probability", 0.0),
            }},
            ontology="proposal",
        )


class RuleAgent(Agent):
    """Chot hanh dong bang rule engine dung chung voi baseline.

    Rule engine tu no cuong che DP1: luat `degraded_system_must_escalate` duoc xet
    truoc moi luat nghiep vu va khong the bi ghi de.
    """

    agent_id = "RuleAgent"
    cost_class = "cheap"
    cost_ms = 0.05

    def __init__(self, engine) -> None:
        super().__init__()
        self.engine = engine

    async def act(self, message: Message) -> Message:
        from masdss.capabilities.rules import facts_from

        content = message.content
        facts = facts_from(
            risk=content.get("risk") or 0,
            causes=list(content.get("causes", [])),
            degradation_level=content.get("degradation_level", 0),
            decision_point=content.get("decision_point", "T4"),
            context=content.get("context"),
        )
        outcome = self.engine.decide(facts)
        return message.reply(
            sender=self.agent_id,
            performative=Performative.INFORM,
            content={"action": outcome.action, "rule_id": outcome.rule_id,
                     "reason": outcome.reason, "enforced": outcome.enforced},
            ontology="decision",
        )


class CaseManagerAgent(Agent):
    """Tao ho so can thiep. O Dot nay chi ghi nhan; saga rollback thuoc WP8."""

    agent_id = "CaseManager"
    cost_class = "cheap"
    cost_ms = 0.05

    def decide_policy(self, message: Message) -> Policy:
        action = message.content.get("action")
        return Policy.ACT if action and action != "no_action" else Policy.REFUSE

    def refusal_reason(self, message: Message) -> str:
        return "khong co hanh dong nao can mo ho so"

    async def act(self, message: Message) -> Message:
        return message.reply(
            sender=self.agent_id,
            performative=Performative.INFORM,
            content={"case_opened": True, "for_action": message.content.get("action")},
            ontology="case",
        )


__all__ = [
    "AnalyticsAgent", "PredictionAgent", "RecommendationAgent",
    "RuleAgent", "CaseManagerAgent", "Cause", "RiskLevel",
]
