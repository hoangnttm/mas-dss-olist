"""WP0 / T5.2 — Message envelope va 10 performative.  [Artifact A1]

Phuc vu: RQ2 (nhat ky la nguon su that), RQ3 (CFP/PROPOSE/REFUSE).

Lay cam hung tu FIPA-ACL. Chi 10 performative — du dung, khong co lam day du chuan.

LUU Y KHI DOC NHAT KY: `PROPOSE` mang HAI VAI trong Contract Net hai pha —
ban khai nang luc o pha 1 (`ontology="declaration"`) va bid that o pha 2
(`ontology="bid"`). Guard va bo dung trace deu khoa theo ONTOLOGY chu khong theo
performative; khoa theo performative se chan sach moi ban khai va lam sap phien
dau thau.

MOT SAI KHAC CO Y so voi dac ta o technical-plan-v3.md §A.1: truong `reply_by`
duoc bieu dien bang THOI LUONG (`deadline_ms`) thay vi dau thoi gian tuyet doi.
Ly do: dau thoi gian tuyet doi keo dong ho he thong vao noi dung message, lam hai
lan chay sinh ra hai tep khac nhau va pha vo dieu kien tai lap cua RQ1.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID

from masdss.config import CONFIG, deterministic_uuid


class Performative(str, Enum):
    REQUEST = "REQUEST"
    INFORM = "INFORM"
    CFP = "CFP"
    PROPOSE = "PROPOSE"
    ACCEPT_PROPOSAL = "ACCEPT_PROPOSAL"
    REJECT_PROPOSAL = "REJECT_PROPOSAL"
    CHALLENGE = "CHALLENGE"
    REFUSE = "REFUSE"
    FAILURE = "FAILURE"
    NOT_UNDERSTOOD = "NOT_UNDERSTOOD"


BROADCAST = "*"


@dataclass(frozen=True)
class Message:
    """Don vi giao tiep. Bat bien — da gui thi khong sua.

    `conversation_id` gom moi message cua cung mot case; day la khoa duy nhat ma
    Explanation Agent duoc phep nhan (DP4).

    HAI TRUONG NOI DUNG, tach bach co chu dich:

      content : du lieu NGU NGHIA, bat buoc tuan tu hoa duoc sang JSON. Day la
                thu duoc ghi vao nhat ky va la thu duy nhat Explainer doc. Moi
                dieu can de dung lai trace PHAI nam o day.

      payload : tham chieu doi tuong trong tien trinh (vi du OrderCase). KHONG
                bao gio duoc ghi vao nhat ky. No ton tai de tac tu khoi phai tra
                cuu nguoc du lieu, va vi khong duoc ghi nen no KHONG the tro
                thanh mot duong lach lam trace phan ky voi hanh vi that (DP4).
    """

    msg_id: UUID
    conversation_id: UUID
    trace_id: UUID
    sender: str
    receiver: str
    performative: Performative
    ontology: str
    content: dict = field(default_factory=dict)
    in_reply_to: UUID | None = None
    deadline_ms: float = CONFIG.default_deadline_ms
    cost_hint: float | None = None
    priority: int = 0
    seq: int = 0
    payload: object | None = field(default=None, compare=False, repr=False)

    def reply(
        self,
        *,
        sender: str,
        performative: Performative,
        content: dict,
        ontology: str | None = None,
        seq: int | None = None,
    ) -> "Message":
        """Tao message tra loi, giu nguyen conversation va noi vao cay hoi thoai.

        Cau tra loi KHONG mang payload: du lieu di nguoc len phai la ngu nghia,
        tuan tu hoa duoc, va ghi duoc vao nhat ky.
        """
        next_seq = self.seq + 1 if seq is None else seq
        return Message(
            msg_id=deterministic_uuid(self.conversation_id, sender, performative.value, next_seq),
            conversation_id=self.conversation_id,
            trace_id=self.trace_id,
            sender=sender,
            receiver=self.sender,
            performative=performative,
            ontology=ontology or self.ontology,
            content=content,
            in_reply_to=self.msg_id,
            seq=next_seq,
        )

    def to_row(self) -> dict:
        """Bieu dien de ghi vao nhat ky. Deadline khong ghi vi la tham so van hanh."""
        return {
            "msg_id": str(self.msg_id),
            "conversation_id": str(self.conversation_id),
            "trace_id": str(self.trace_id),
            "in_reply_to": str(self.in_reply_to) if self.in_reply_to else None,
            "sender": self.sender,
            "receiver": self.receiver,
            "performative": self.performative.value,
            "ontology": self.ontology,
            "content_json": json.dumps(self.content, ensure_ascii=False, sort_keys=True),
            "seq": self.seq,
        }

    @staticmethod
    def from_row(row: dict) -> "Message":
        return Message(
            msg_id=UUID(row["msg_id"]),
            conversation_id=UUID(row["conversation_id"]),
            trace_id=UUID(row["trace_id"]),
            in_reply_to=UUID(row["in_reply_to"]) if row["in_reply_to"] else None,
            sender=row["sender"],
            receiver=row["receiver"],
            performative=Performative(row["performative"]),
            ontology=row["ontology"],
            content=json.loads(row["content_json"]),
            seq=row["seq"],
        )


def new_request(
    *,
    conversation_id: UUID,
    sender: str,
    receiver: str,
    content: dict,
    ontology: str = "order_case",
    seq: int = 0,
    deadline_ms: float | None = None,
    payload: object | None = None,
    performative: Performative = Performative.REQUEST,
) -> Message:
    """Tao message goc cua mot buoc trong ke hoach."""
    return Message(
        msg_id=deterministic_uuid(conversation_id, sender, receiver, performative.value, seq),
        conversation_id=conversation_id,
        trace_id=conversation_id,
        sender=sender,
        receiver=receiver,
        performative=performative,
        ontology=ontology,
        content=content,
        deadline_ms=deadline_ms if deadline_ms is not None else CONFIG.default_deadline_ms,
        seq=seq,
        payload=payload,
    )
