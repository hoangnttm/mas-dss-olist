"""WP0 / T6.3 — Bo thuc thi ke hoach.  [technical-plan-v3.md §5.5]

Phuc vu: RQ2 (dinh tuyen dong), RQ1 (kiem soat tron vong thuc thi).

Day la file hien thuc hoa quyet dinh "tu viet orchestrator" o §2.2. Ba rang buoc
bat buoc, moi rang buoc phuc vu mot muc dich cu the:

  1. `plan` la du lieu thuan  -> ke hoach kiem tra duoc, in ra duoc vao phu luc.
  2. Moi loi goi tac tu di qua `invoke_fn` truyen tu ngoai vao
                                -> chaos harness khong can sua orchestrator.
  3. File nay KHONG import gi tu agents/, chaos/, evaluation/
                                -> doi engine sau nay chi can mot adapter.

Rang buoc 3 duoc cuong che boi tests-v3/test_layering.py::test_orchestrator_is_isolated.
"""

from __future__ import annotations

from typing import Awaitable, Callable, Mapping, Protocol
from uuid import UUID

from masdss.core.errors import DeterministicError, TransientError
from masdss.core.message import Message, Performative, new_request
from masdss.core.ontology import OrderCase
from masdss.system.blackboard import Blackboard
from masdss.system.plan import Plan, Step


class Handler(Protocol):
    agent_id: str

    async def handle(self, message: Message) -> Message: ...


InvokeFn = Callable[[Handler, Message], Awaitable[Message]]
Reducer = Callable[[Blackboard, str, Message], None]
ContentFn = Callable[[Blackboard, Step], dict]


def default_content(bb: Blackboard, step: Step) -> dict:
    """Noi dung NGU NGHIA cua mot yeu cau — bat buoc tuan tu hoa duoc sang JSON.

    Day la thu duoc ghi vao nhat ky, nen no phai du de dung lai trace ma khong
    can nhin vao blackboard (DP4).
    """
    return {
        "case_id": bb.case.case_id,
        "step": step.name,
        "decision_point": bb.case.decision_point.value,
        "risk": int(bb.risk) if bb.risk is not None else None,
        # Bo chi bao ngu canh do Analytics ghi. KHONG co truong nay thi tang quyet
        # dinh o T3 chi nhin thay DUNG MOT bien la `risk`, va moi luat T3 deu khong
        # the phat bieu duoc — do la tinh trang truoc 13/08.
        "context": dict(bb.context),
        "causes": [c.cause.value for c in bb.causes],
        "max_cause_probability": (
            round(max((c.probability for c in bb.causes), default=0.0), 6)
        ),
        "proposal": bb.proposal,
        "violated": list(bb.critique.violated_constraints) if bb.critique else [],
        "degradation_level": bb.degradation_level,
        "budget_ms": bb.budget_ms_left,
    }


class Registry:
    """Anh xa ten trong ke hoach -> tac tu (hoac nhom tac tu).

    Orchestrator chi biet TEN, khong biet lop cu the. Nho vay no khong phai import
    gi tu `agents/` (rang buoc 3).
    """

    def __init__(
        self,
        agents: Mapping[str, Handler],
        pools: Mapping[str, tuple[Handler, ...]] | None = None,
    ) -> None:
        self._agents = dict(agents)
        self._pools = dict(pools or {})

    def agent(self, name: str) -> Handler:
        return self._agents[name]

    def pool(self, name: str) -> tuple[Handler, ...]:
        return self._pools[name]

    def has(self, name: str) -> bool:
        return name in self._agents or name in self._pools


async def execute(
    plan: Plan,
    case: OrderCase,
    invoke_fn: InvokeFn,
    registry: Registry,
    reducer: Reducer,
    conversation_id: UUID,
    on_message: Callable[[Message], None] | None = None,
    content_fn: ContentFn = default_content,
) -> Blackboard:
    """Chay mot case qua mot ke hoach, tra ve blackboard cuoi cung.

    Chinh sach loi (RQ1):
      TransientError     -> ghi nhan, ha mot bac suy giam, di tiep
      DeterministicError -> KHONG retry, ha hai bac suy giam, di tiep
      REFUSE             -> khong phai loi; la hanh vi dung cua DP3
    """
    bb = Blackboard(case=case)
    seq = 0

    for step in plan:
        if not step.should_run(bb):
            bb.record_step(step.name, "skipped")
            continue

        if step.budget is not None:
            bb.budget_ms_left = step.budget(bb)

        if step.fanout and step.protocol == "contract_net":
            seq = await _contract_net_session(
                step, bb, registry, invoke_fn, reducer, conversation_id,
                content_fn, on_message, seq,
            )
            continue

        targets = (
            registry.pool(step.fanout) if step.fanout else (registry.agent(step.agent),)
        )

        for handler in targets:
            seq += 1
            request = new_request(
                conversation_id=conversation_id,
                sender="Orchestrator",
                receiver=handler.agent_id,
                content=content_fn(bb, step),
                ontology="order_case",
                seq=seq,
                deadline_ms=step.deadline_ms,
                payload=case,  # tham chieu trong tien trinh, KHONG ghi vao nhat ky
            )
            if on_message:
                on_message(request)

            try:
                reply = await invoke_fn(handler, request)
            except TransientError as exc:
                bb.degrade(1, f"{step.name}/{handler.agent_id}: transient: {exc}")
                bb.record_step(step.name, "transient_error")
                continue
            except DeterministicError as exc:
                # Khong retry: model chet thi thu ba lan cung chet ba lan.
                bb.degrade(2, f"{step.name}/{handler.agent_id}: deterministic: {exc}")
                bb.record_step(step.name, "deterministic_error")
                continue

            if on_message:
                on_message(reply)

            if reply.performative is Performative.REFUSE:
                bb.record_step(step.name, "refused")
                bb.notes.append(f"{handler.agent_id} REFUSE: {reply.content.get('reason', '')}")
                continue

            reducer(bb, step.name, reply)
            bb.record_step(step.name, "ok")

    return bb


async def _contract_net_session(step: Step, bb: Blackboard, registry: "Registry",
                                invoke_fn: InvokeFn, reducer: Reducer,
                                conversation_id: UUID, content_fn: ContentFn,
                                on_message, seq: int) -> int:
    """Phien Contract Net hai pha.  [T7.1, T7.2]

    PHA 1 gui `CFP` toi moi analyst va nhan ve BAN KHAI NANG LUC. Ban khai duoc sinh
    ra ma khong chay capability dat — do la ranh gioi lam cho pha tham do re.

    PHA 2 giai bai toan knapsack duoi rang buoc ngan sach, roi gui `ACCEPT_PROPOSAL`
    cho ben thang thau va `REJECT_PROPOSAL` cho ben thua. CHI ben thang moi chay
    capability dat.

    Ca hai pha deu di qua `invoke_fn`, nen chung chiu tang guard va bo tiem loi y het
    moi loi goi khac — mot analyst chet o pha tham do se bi loai khoi phien dau thau
    thay vi lam sap ca phien.
    """
    from masdss.core.ontology import Declaration
    from masdss.system.contract_net import allocate, budget_binds

    pool = registry.pool(step.fanout)
    declarations: list[Declaration] = []

    # --- PHA 1: tham do ---
    for handler in pool:
        seq += 1
        cfp = new_request(
            conversation_id=conversation_id, sender="Orchestrator",
            receiver=handler.agent_id, content=content_fn(bb, step),
            ontology="cfp", seq=seq, deadline_ms=step.deadline_ms,
            payload=bb.case, performative=Performative.CFP,
        )
        if on_message:
            on_message(cfp)
        try:
            reply = await invoke_fn(handler, cfp)
        except (TransientError, DeterministicError) as exc:
            bb.degrade(1, f"{step.name}/{handler.agent_id}: pha tham do that bai: {exc}")
            continue
        if on_message:
            on_message(reply)
        spec = reply.content.get("declaration")
        if spec:
            declarations.append(Declaration(**spec))

    if not declarations:
        bb.record_step(step.name, "no_declaration")
        return seq

    # --- PHA 2: phan bo duoi rang buoc ngan sach ---
    allocation = allocate(declarations, bb.budget_ms_left)
    bb.allocation = {
        **allocation.to_row(),
        "n_declared": len(declarations),
        # Ghi lai ngan sach co THUC SU rang buoc khong. Neu khong bao gio rang buoc
        # thi giao thuc chay nhung khong quyet dinh gi, va moi con so ve "phan bo
        # tinh toan" tro nen rong — phai bao cao trung thuc dieu do.
        "budget_binds": budget_binds(declarations, bb.budget_ms_left),
    }

    for handler in pool:
        accepted = handler.agent_id in allocation.accepted
        seq += 1
        decision = new_request(
            conversation_id=conversation_id, sender="Orchestrator",
            receiver=handler.agent_id,
            content={**content_fn(bb, step),
                     "allocation": "accepted" if accepted else "rejected"},
            ontology="award", seq=seq, deadline_ms=step.deadline_ms,
            payload=bb.case,
            performative=(Performative.ACCEPT_PROPOSAL if accepted
                          else Performative.REJECT_PROPOSAL),
        )
        if on_message:
            on_message(decision)
        if not accepted:
            continue   # ben thua thau KHONG chay capability — do la muc dich cua giao thuc

        try:
            reply = await invoke_fn(handler, decision)
        except TransientError as exc:
            bb.degrade(1, f"{step.name}/{handler.agent_id}: transient: {exc}")
            continue
        except DeterministicError as exc:
            bb.degrade(2, f"{step.name}/{handler.agent_id}: deterministic: {exc}")
            continue

        if on_message:
            on_message(reply)
        if reply.performative is Performative.REFUSE:
            bb.notes.append(f"{handler.agent_id} REFUSE: {reply.content.get('reason', '')}")
            continue
        reducer(bb, step.name, reply)

    bb.record_step(step.name, "ok")
    return seq


def resume_filter(done_case_ids: set[str]) -> Callable[[OrderCase], bool]:
    """Thay cho checkpoint: bo qua case da hoan tat khi chay lai.

    Moi case doc lap nen "resume" chi la mot phep loc — khong can co che thuc thi
    ben vung cua mot engine ben ngoai (technical-plan-v3.md §2.2a).
    """
    return lambda case: case.case_id not in done_case_ids
