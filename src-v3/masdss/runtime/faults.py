"""WP0 / T5.6 — SEAM TIEM LOI. Day la file quan trong nhat cua Dot 0.

Phuc vu: RQ1 (dong gop chinh cua luan van).

MOI loi goi tac tu — cua MAS-DSS lan cua Monolithic-Complete — di qua dung ham
`invoke()` o day. Nho vay giao thuc so sanh cua RQ1 ("chay CUNG kich ban loi tren
hai kien truc") dung theo CAU TRUC, khong theo loi hua.

Ba diem tiem loi:
  before  : crash, treo qua han chot, cham
  timeout : huy task that bang asyncio.wait_for — KHONG do sau khi chay xong
  after   : Byzantine — ket qua hop le ve kieu nhung sai ve chat

Neu seam nay dat sai cho, WP9 se phai sua nguoc khap noi va thi nghiem chaos mat
tinh tai lap (build-plan.md §9).
"""

from __future__ import annotations

import asyncio
import time
from typing import Protocol, runtime_checkable

from masdss.core.errors import AgentTimeout
from masdss.core.message import Message


@runtime_checkable
class Injector(Protocol):
    """Giao dien ma `chaos/injector.py` cai dat.

    Tham so dau tien la TEN THANH PHAN LOGIC, khong phai agent_id — de cung mot
    kich ban loi ap duoc len ca MAS-DSS lan Monolithic-Complete (chaos/components.py).

    O ban binh thuong, `invoke()` nhan injector=None va khong co chi phi nao.
    """

    def before(self, component: str, message: Message | None = None) -> None:
        """Duoc goi truoc khi thanh phan chay. Duoc phep raise."""

    def after(self, component: str, result):
        """Duoc goi sau khi thanh phan tra ket qua. Duoc phep bien doi ket qua."""

    def delay_ms(self, component: str) -> float:
        """Do tre nhan tao, tinh bang mili giay.

        Duoc ap BEN TRONG pham vi `asyncio.wait_for`, nen mot do tre vuot han chot
        sinh ra `AgentTimeout` THAT — task bi huy, khong phai do sau khi chay xong.
        Do la khac biet voi ban v0 va la thu can chung minh o RQ1.
        """


@runtime_checkable
class Handler(Protocol):
    """Thu gi co the xu ly mot message. Agent cai dat giao dien nay."""

    agent_id: str

    async def handle(self, message: Message) -> Message: ...


async def invoke(
    handler: Handler,
    message: Message,
    *,
    injector: Injector | None = None,
) -> Message:
    """Goi mot tac tu, co cuong che han chot va co diem tiem loi.

    Han chot lay tu `message.deadline_ms` — la THOI LUONG, khong phai dau thoi
    gian tuyet doi, de noi dung message khong keo dong ho he thong vao (tinh tai
    lap, xem core/message.py).
    """
    from masdss.core.components import component_of

    agent_id = handler.agent_id
    component = component_of(agent_id)

    if injector is not None:
        injector.before(component, message)

    timeout_s = message.deadline_ms / 1000.0

    async def _run():
        # Do tre nam BEN TRONG pham vi wait_for, nen no sinh ra timeout that.
        delay = getattr(injector, "delay_ms", None)
        if delay is not None:
            ms = delay(component)
            if ms > 0:
                await asyncio.sleep(ms / 1000.0)
        return await handler.handle(message)

    try:
        result = await asyncio.wait_for(_run(), timeout=timeout_s)
    except asyncio.TimeoutError as exc:
        # Task da bi HUY. Day la khac biet voi ban v0: v0 do latency SAU khi tac tu
        # chay xong, nen tac tu treo lam treo ca pipeline vinh vien.
        raise AgentTimeout(
            f"{agent_id} khong tra loi trong {message.deadline_ms:.0f}ms"
        ) from exc

    if injector is not None:
        result = injector.after(component, result)

    return result


def guard_call(component: str, fn, *args, injector: Injector | None = None, **kwargs):
    """Seam DONG BO cho ma khong chay qua tac tu.

    Ton tai de Monolithic-Complete chiu duoc CUNG kich ban loi voi MAS-DSS (T9.3).

    LUU Y VE TINH CONG BANG: ham nay chi TIEM loi, no khong xu ly loi. Monolithic
    van khong co guard, khong co thang suy giam, khong co truong nao bao rang mot
    phan he thong da hong. Them seam vao lam cho no CHIU duoc loi de do, chu khong
    lam cho no CHIU DUNG duoc loi.
    """
    if injector is not None:
        injector.before(component, None)
        # Do tre cung phai ap len kien truc doi chung, neu khong kich ban `hang` chi
        # tac dong len mot ben va hai con so khong so sanh duoc (T9.3).
        #
        # Khac biet dang chu y: Monolithic KHONG co co che han chot nao, nen no chi
        # cham di chu khong bi huy. Do la mot that bai ve TINH SONG (liveness), khong
        # phai mot quyet dinh sai — va vi vay no khong duoc tinh la hong am tham.
        delay = getattr(injector, "delay_ms", None)
        if delay is not None:
            ms = delay(component)
            if ms > 0:
                time.sleep(ms / 1000.0)
    result = fn(*args, **kwargs)
    if injector is not None:
        result = injector.after(component, result)
    return result
