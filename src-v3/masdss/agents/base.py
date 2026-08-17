"""WP6 — Lop nen cho Analyst.

Phuc vu: RQ3 (dau thau kem bang chung, co quyen tu choi).

VO MONG: agent chi lam ba viec — quyet dinh ACT hay REFUSE, goi capability, dong
goi ket qua thanh message. Moi logic hoc may nam o `capabilities/`.

Rang buoc do la ly do ba Analyst chia se DUNG mot lop nen: neu logic quy ket nam
trong agent, moi analyst se dan trong theo mot huong khac nhau va phien dau thau
mat tinh so sanh duoc.
"""

from __future__ import annotations

from typing import Protocol

from masdss.config import CONFIG
from masdss.core.message import Message, Performative
from masdss.core.ontology import Cause, Declaration, Evidence, OrderCase
from masdss.runtime.actor import Agent, Policy


class Signal(Protocol):
    """Capability sinh bid cho mot nguyen nhan cu the."""

    name: str
    cost_ms: float
    prior_confidence: float

    def can_handle(self, case: OrderCase) -> bool: ...

    def refusal_reason(self, case: OrderCase) -> str: ...

    def run(self, case: OrderCase) -> tuple[float, tuple[Evidence, ...]]: ...


class DeclaringAgent:
    """Phan chung cua pha 1 Contract Net: khai bao nang luc ma KHONG chay capability.

    Day la ranh gioi quan trong nhat cua giao thuc. Neu `declare()` lo goi `run()`,
    pha tham do khong con re nua va toan bo bai toan phan bo tro nen vo nghia — ta
    da tra gia truoc khi quyet dinh co tra gia hay khong.

    `test_declaration_never_runs_the_capability` canh dung dieu do.
    """

    def declare(self, message: Message) -> Declaration:
        raise NotImplementedError


class AnalystAgent(Agent):
    """Tac tu chuyen biet dau thau cho DUNG MOT nguyen nhan.

    Mot analyst khong bao gio bid cho nguyen nhan khac. Do la thu lam cho `bid_entropy`
    co nghia: hai analyst cung tu tin nghia la don co hai nguyen nhan that, chu khong
    phai mot mo hinh dang lung tung giua hai lop.
    """

    cause: Cause = Cause.UNKNOWN

    # DUONG ABLATION CUA DP3 — "tu choi thay vi doan".
    #
    # `allow_refuse=False` cam analyst phat REFUSE: no buoc phai tra loi ke ca khi
    # khong co bang chung. Day khong phai mot che do van hanh — no ton tai DUY NHAT
    # de do cai gia cua viec bo quyen tu choi, tuc de DP3 duoc kiem chung chu khong
    # chi duoc phat bieu.
    #
    # Khi bi ep, analyst bid o dung nguong `tau_cause`: muc thap nhat van duoc tinh
    # la mot quy ket. Bid 0,0 se bi loc o arbiter va bien ablation thanh vo nghia.
    allow_refuse: bool = True

    def __init__(self, signal: Signal, *, allow_refuse: bool = True) -> None:
        super().__init__()
        self.signal = signal
        self.cost_ms = signal.cost_ms
        self.allow_refuse = allow_refuse

    def decide_policy(self, message: Message) -> Policy:
        if not self.allow_refuse:
            return Policy.ACT
        case = message.payload
        return Policy.ACT if self.signal.can_handle(case) else Policy.REFUSE

    def refusal_reason(self, message: Message) -> str:
        return self.signal.refusal_reason(message.payload)

    def declare(self, message: Message) -> Declaration:
        """Pha 1: khai bao nang luc. KHONG goi `signal.run()`."""
        case = message.payload
        can = self.signal.can_handle(case)
        return Declaration(
            agent_id=self.agent_id,
            expected_confidence=getattr(self.signal, "prior_confidence", 0.5) if can else 0.0,
            cost_ms=self.cost_ms,
            has_evidence=can,
            reason="" if can else self.signal.refusal_reason(case),
        )

    async def handle(self, message: Message) -> Message:
        """Phan nhanh theo performative — day la co che hai pha cua Contract Net.

        CFP  -> khai bao nang luc, KHONG chay capability
        khac -> chay capability that (chi den duoc day khi da thang thau)
        """
        if message.performative is Performative.CFP:
            declaration = self.declare(message)
            return message.reply(
                sender=self.agent_id, performative=Performative.PROPOSE,
                content={"declaration": {
                    "agent_id": declaration.agent_id,
                    "expected_confidence": round(declaration.expected_confidence, 6),
                    "cost_ms": declaration.cost_ms,
                    "has_evidence": declaration.has_evidence,
                    "reason": declaration.reason,
                }},
                ontology="declaration",
            )
        return await super().handle(message)

    async def act(self, message: Message) -> Message:
        confidence, evidence = self.signal.run(message.payload)

        # Khong co bang chung thi tu choi, khong bid con so 0 — mot bid rong van
        # chiem cho trong phien dau thau va lam nhieu bid_entropy.
        if confidence <= 0.0 or not evidence:
            if self.allow_refuse:
                return message.reply(
                    sender=self.agent_id,
                    performative=Performative.REFUSE,
                    content={"reason": "khong tim thay bang chung vuot nguong"},
                    ontology="refusal",
                )
            # Ablation DP3: bi cam tu choi thi phai doan. Bang chung ghi ro day la
            # mot phong doan bi ep, de trace khong noi doi ve co so cua quyet dinh.
            confidence = CONFIG.tau_cause
            evidence = (Evidence(kind="forced_guess",
                                 detail="ablation DP3: bi cam phat REFUSE, khong co bang chung",
                                 value=None),)

        return message.reply(
            sender=self.agent_id,
            performative=Performative.PROPOSE,
            content={
                "cause": self.cause.value,
                "confidence": round(float(confidence), 6),
                "cost_ms": self.cost_ms,
                "evidence": [
                    {"kind": e.kind, "detail": e.detail, "value": e.value} for e in evidence
                ],
            },
            ontology="bid",
        )


class TextAnalystAgent(AnalystAgent):
    """Analyst doc van ban. Chi khac o cho capability la `CauseHead`.

    Tang B (25,23% don bat man) khong co van ban nen hai analyst nay luon REFUSE o
    do — day chinh la tinh huong kho (b) cua RQ3, va la noi DP3 duoc kiem chung.
    """

    def __init__(self, head, *, allow_refuse: bool = True) -> None:  # head: CauseHead
        Agent.__init__(self)
        self.head = head
        self.cost_ms = head.cost_ms
        self.allow_refuse = allow_refuse

    def decide_policy(self, message: Message) -> Policy:
        if not self.allow_refuse:      # ablation DP3
            return Policy.ACT
        return Policy.ACT if self.head.can_handle(message.payload) else Policy.REFUSE

    def refusal_reason(self, message: Message) -> str:
        return "don khong co binh luan — khong co bang chung van ban (tang B)"

    def declare(self, message: Message) -> Declaration:
        """Pha 1: chi kiem tra CO VAN BAN HAY KHONG — khong chay encoder.

        Day la cho ranh gioi quan trong nhat: `can_handle` cua `CauseHead` chi doc
        `case.has_text_evidence`, mot phep kiem tra chuoi rong. Encoder chi chay o
        pha 2, va chi khi analyst nay thang thau.
        """
        case = message.payload
        can = self.head.can_handle(case)
        return Declaration(
            agent_id=self.agent_id,
            expected_confidence=getattr(self.head, "prior_confidence", 0.5) if can else 0.0,
            cost_ms=self.cost_ms,
            has_evidence=can,
            reason="" if can else "khong co bang chung van ban (tang B)",
        )

    async def act(self, message: Message) -> Message:
        confidence, evidence = self.head.score(message.payload, self.cause)
        if confidence <= 0.0 or not evidence:
            if self.allow_refuse:
                return message.reply(
                    sender=self.agent_id,
                    performative=Performative.REFUSE,
                    content={"reason": f"van ban khong co tin hieu {self.cause.value}"},
                    ontology="refusal",
                )
            # Ablation DP3 — o tang B day la truong hop dat gia nhat: khong co van
            # ban nao ca, va he thong van buoc phai quy ket.
            confidence = CONFIG.tau_cause
            evidence = (Evidence(kind="forced_guess",
                                 detail="ablation DP3: bi cam phat REFUSE, khong co bang chung",
                                 value=None),)
        return message.reply(
            sender=self.agent_id,
            performative=Performative.PROPOSE,
            content={
                "cause": self.cause.value,
                "confidence": round(float(confidence), 6),
                "cost_ms": self.cost_ms,
                "evidence": [
                    {"kind": e.kind, "detail": e.detail, "value": e.value} for e in evidence
                ],
            },
            ontology="bid",
        )
