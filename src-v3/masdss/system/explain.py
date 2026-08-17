"""WP0 / T6.8 — Dung decision trace CHI tu nhat ky message.  [DP4]

Phuc vu: RQ2 (truy vet duoc).

DP4: "De decision trace luon trung thuc voi hanh vi thuc te, hay dung no tu nhat
ky message that thay vi viet tay, boi vi trace viet tay co the phan ky voi thu he
thong thuc su lam."

CACH CUONG CHE: `Explainer.build()` nhan DUNG MOT tham so du lieu la
`conversation_id`. No khong nhan `case`, khong nhan `blackboard`, khong nhan
`decision`. Rang buoc chu ky ham nay CHINH LA DP4 — neu trace dung duoc chi tu
nhat ky thi no khong the phan ky voi hanh vi that.

CANH BOI HAI TEST, ca hai o `tests-v3/test_skeleton_e2e.py`:
  - `test_explainer_build_accepts_only_conversation_id` — dung `inspect.signature`,
    khang dinh danh sach tham so DUNG BANG ["self", "conversation_id"]
  - `test_trace_is_rebuilt_from_log_alone` — dung trace that chi tu conversation_id

(Ban truoc cua docstring nay tro toi `tests-v3/test_explain_signature.py`, mot tep
KHONG TON TAI. Guard van chay dung, nhung mot nguoi di kiem chung theo docstring se
khong tim thay gi va ket luan nham la claim khong co bang chung.)
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from masdss.core.message import Message, Performative
from masdss.runtime.message_log import MessageLog


@dataclass(frozen=True)
class TraceNode:
    depth: int
    sender: str
    receiver: str
    performative: Performative
    summary: str


@dataclass(frozen=True)
class DecisionTrace:
    conversation_id: str
    nodes: tuple[TraceNode, ...]

    @property
    def depth(self) -> int:
        """Do sau cay hoi thoai — mot chi so phoi hop (RQ3)."""
        return max((n.depth for n in self.nodes), default=0)

    def render(self) -> str:
        lines = [f"Trace {self.conversation_id}"]
        for node in self.nodes:
            indent = "  " * node.depth
            lines.append(
                f"{indent}{node.sender} -> {node.receiver} "
                f"[{node.performative.value}] {node.summary}"
            )
        return "\n".join(lines)


class Explainer:
    """Dung trace tu nhat ky. Khong co duong vao du lieu nao khac."""

    def __init__(self, log: MessageLog) -> None:
        self._log = log

    def build(self, conversation_id: UUID | str) -> DecisionTrace:
        """Tham so du lieu duy nhat: conversation_id.  <-- DP4"""
        messages = self._log.conversation(conversation_id)
        depth_of: dict[str, int] = {}
        nodes: list[TraceNode] = []

        for msg in messages:
            parent = str(msg.in_reply_to) if msg.in_reply_to else None
            depth = depth_of.get(parent, -1) + 1 if parent else 0
            depth_of[str(msg.msg_id)] = depth
            nodes.append(
                TraceNode(
                    depth=depth,
                    sender=msg.sender,
                    receiver=msg.receiver,
                    performative=msg.performative,
                    summary=_summarize(msg),
                )
            )

        return DecisionTrace(conversation_id=str(conversation_id), nodes=tuple(nodes))


def _summarize(message: Message) -> str:
    content = message.content
    if message.performative is Performative.REFUSE:
        return f"tu choi: {content.get('reason', '')}"
    # Khoa theo ONTOLOGY chu khong theo PERFORMATIVE: Contract Net dung `PROPOSE`
    # cho ca ban khai nang luc (pha 1) lan bid that (pha 2).
    if message.ontology == "declaration":
        spec = content.get("declaration", {})
        if not spec.get("has_evidence"):
            return f"khai bao: khong co bang chung ({spec.get('reason', '')})"
        return (f"khai bao: ky vong {spec.get('expected_confidence')} "
                f"gia {spec.get('cost_ms')}ms")
    if message.ontology == "award":
        return f"trao thau: {content.get('allocation')}"
    if message.performative is Performative.PROPOSE:
        return (
            f"bid {content.get('cause')} conf={content.get('confidence')} "
            f"cost={content.get('cost_ms')}ms"
        )
    if message.performative is Performative.REQUEST:
        return f"buoc '{content.get('step', '')}'"
    keys = ", ".join(sorted(content)[:4])
    return keys or message.ontology
