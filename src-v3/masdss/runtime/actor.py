"""WP0 / T5.5 — Mo hinh tac tu: hop thu va chinh sach.

Phuc vu: RQ2 (tac tu la thuc the, khong phai ham), RQ3 (quyen tu choi).

Diem mau chot: tac tu CO QUYEN TU CHOI. Day khong phai chi tiet phu — no la DP3.
Mot tac tu thay minh khong co bang chung de ket luan thi phat REFUSE thay vi doan
bua. Chi phi chuyen giao cho nguoi thap hon nhieu chi phi cua mot hanh dong sai.

Tac tu phai MONG. Moi logic hoc may nam o `capabilities/`. Vuot qua ~80 dong thi
gan nhu chac chan co logic dat sai tang (technical-plan-v3.md §3).
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

from masdss.core.message import Message, Performative


class Policy(str, Enum):
    """Quyet dinh cua tac tu khi nhan mot message."""

    ACT = "ACT"
    DEFER = "DEFER"
    DELEGATE = "DELEGATE"
    REFUSE = "REFUSE"


@dataclass
class Mailbox:
    """Hop thu co gioi han va co backpressure."""

    maxsize: int = 128
    _queue: asyncio.Queue = field(init=False)

    def __post_init__(self) -> None:
        self._queue = asyncio.Queue(maxsize=self.maxsize)

    async def put(self, message: Message) -> None:
        await self._queue.put(message)

    async def get(self) -> Message:
        return await self._queue.get()

    def qsize(self) -> int:
        return self._queue.qsize()


class Agent(ABC):
    """Lop nen cua moi tac tu.

    `cost_class` la du lieu van hanh: no la dau vao cua bai toan phan bo ngan sach
    trong Contract Net (technical-plan-v3.md §A.3), khong phai chu thich.
    """

    agent_id: str = "agent"
    cost_class: str = "cheap"  # cheap | very_cheap | expensive
    cost_ms: float = 1.0

    def __init__(self) -> None:
        self.mailbox = Mailbox()

    def decide_policy(self, message: Message) -> Policy:
        """Mac dinh la hanh dong. Tac tu con ghi de de cai dat dieu kien REFUSE."""
        return Policy.ACT

    def refusal_reason(self, message: Message) -> str:
        return "khong du bang chung"

    async def handle(self, message: Message) -> Message:
        policy = self.decide_policy(message)
        if policy is Policy.REFUSE:
            return message.reply(
                sender=self.agent_id,
                performative=Performative.REFUSE,
                content={"reason": self.refusal_reason(message)},
                ontology="refusal",
            )
        return await self.act(message)

    @abstractmethod
    async def act(self, message: Message) -> Message:
        """Thuc hien nhiem vu. Chi goi capability, khong chua logic hoc may."""
