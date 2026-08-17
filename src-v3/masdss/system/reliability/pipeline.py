"""WP8 — Boc tang chiu loi quanh lop goi tac tu.

Phuc vu: RQ1.

DIEM THIET KE DANG CHU Y: khong mot dong nao trong `orchestrator.py` phai sua de
tang nay hoat dong. Ly do la `GuardViolation` von la mot `DeterministicError`, ma
orchestrator da co san chinh sach cho loai loi do — ha hai bac suy giam va di tiep.

Nho vay:
  - Bat/tat tang chiu loi la mot tham so, khong phai mot nhanh ma nguon.
  - Ablation "tat guard roi chay lai chaos" tro thanh mot lan doi cau hinh.
  - Orchestrator van giu duoc rang buoc khong import gi tu `agents/`, `chaos/`.

THU TU KIEM TRA, va thu tu nay quan trong:

    1. Breaker OPEN  -> khong goi nua, phat loi ngay (tiet kiem thoi gian cho)
    2. Goi tac tu    -> co the raise
    3. Guard         -> kiem tra ket qua tra ve
    4. Ghi nhan      -> cap nhat breaker

Guard chay SAU khi goi, vi loi Byzantine chi nhin thay duoc o ket qua.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from masdss.core.components import component_of
from masdss.core.errors import DeterministicError, GuardViolation, TransientError
from masdss.core.message import Message
from masdss.system.reliability.breaker import Supervisor
from masdss.system.reliability.guards import GuardChain


@dataclass
class ReliabilityLayer:
    """Boc mot `invoke_fn` bang breaker, chinh sach thu lai, va output guard."""

    guards: GuardChain
    supervisor: Supervisor = field(default_factory=Supervisor)
    enabled: bool = True

    def wrap(self, invoke_fn):
        """Tra ve mot `invoke_fn` moi da duoc boc.

        `enabled=False` tra ve nguyen ham goc — day la duong ablation cho RQ1.
        """
        if not self.enabled:
            return invoke_fn

        async def guarded(handler, message: Message) -> Message:
            component = component_of(handler.agent_id)
            breaker = self.supervisor.breaker(component)

            if not breaker.allow():
                self.supervisor.skipped_calls += 1
                raise DeterministicError(
                    f"[breaker] {component}: mach dang OPEN — dung fallback, "
                    f"khong phi thoi gian cho"
                )

            attempt = 0
            while True:
                try:
                    reply = await invoke_fn(handler, message)
                    self.guards.check(component, reply)
                except GuardViolation:
                    breaker.record_failure()
                    raise
                except (TransientError, DeterministicError) as exc:
                    if self.supervisor.should_retry(exc, attempt):
                        attempt += 1
                        continue
                    breaker.record_failure()
                    raise

                breaker.record_success()
                return reply

        return guarded

    def report(self) -> dict:
        return {
            "guard_violations": self.guards.report(),
            "breakers": self.supervisor.report(),
            "skipped_calls": self.supervisor.skipped_calls,
        }
