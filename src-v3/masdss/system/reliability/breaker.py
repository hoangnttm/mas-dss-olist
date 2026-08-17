"""WP8 / T8.3, T8.4 — Circuit breaker va chinh sach thu lai.

Phuc vu: RQ1(c) — muc suy giam chat luong quyet dinh, va RQ1(d) — chi phi.

CIRCUIT BREAKER giai quyet mot van de cu the: khi mot thanh phan da hong, moi case
sau do van goi no, van cho het han chot, roi van that bai. Voi 14.475 case, do la
hang gio dong ho lang phi va hang nghin dong nhat ky vo nghia.

    CLOSED    -> chay binh thuong
    OPEN      -> dung fallback NGAY, khong phi thoi gian cho
    HALF_OPEN -> sau cooldown, thu lai dung MOT lan

CHINH SACH THU LAI, va day la cho ban v0 sai:

    v0 retry cung batch, cung input, tren mot model tat dinh — loi lap lai y het ba
    lan roi bi bo qua. Thu lai chi co nghia voi loi NHAT THOI. Model chet thi thu
    ba lan cung chet ba lan, va ba lan do chi lam cham them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from masdss.core.errors import DeterministicError, TransientError


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    """Bo ngat mach cho mot thanh phan."""

    component: str
    failure_threshold: int = 5
    cooldown_calls: int = 50

    state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    calls_since_open: int = 0
    opened_count: int = 0

    def allow(self) -> bool:
        """Co duoc phep goi thanh phan nay khong."""
        if self.state is CircuitState.CLOSED:
            return True
        if self.state is CircuitState.OPEN:
            self.calls_since_open += 1
            if self.calls_since_open >= self.cooldown_calls:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        return True  # HALF_OPEN: cho dung mot lan thu

    def record_success(self) -> None:
        self.consecutive_failures = 0
        if self.state is CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.calls_since_open = 0

    def record_failure(self) -> None:
        self.consecutive_failures += 1
        if self.state is CircuitState.HALF_OPEN:
            self._open()
        elif self.consecutive_failures >= self.failure_threshold:
            self._open()

    def _open(self) -> None:
        self.state = CircuitState.OPEN
        self.calls_since_open = 0
        self.opened_count += 1


@dataclass
class Supervisor:
    """Cay giam sat: quan ly breaker cho tung thanh phan va chinh sach thu lai."""

    failure_threshold: int = 5
    cooldown_calls: int = 50
    max_transient_retries: int = 2

    breakers: dict[str, CircuitBreaker] = field(default_factory=dict)
    skipped_calls: int = 0

    def breaker(self, component: str) -> CircuitBreaker:
        if component not in self.breakers:
            self.breakers[component] = CircuitBreaker(
                component=component,
                failure_threshold=self.failure_threshold,
                cooldown_calls=self.cooldown_calls,
            )
        return self.breakers[component]

    def should_retry(self, error: Exception, attempt: int) -> bool:
        """Chi thu lai loi NHAT THOI. Loi tat dinh thi thu lai la vo nghia."""
        if isinstance(error, DeterministicError):
            return False
        if isinstance(error, TransientError):
            return attempt < self.max_transient_retries
        return False

    def report(self) -> list[dict]:
        return [
            {"component": name, "state": b.state.value,
             "opened_count": b.opened_count,
             "consecutive_failures": b.consecutive_failures}
            for name, b in sorted(self.breakers.items())
        ]
