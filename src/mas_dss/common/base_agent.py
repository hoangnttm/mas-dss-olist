"""Lớp cơ sở cho mọi agent.

Mọi agent nhận một danh sách `OrderCase` và trả về danh sách đã được làm giàu. Ký hiệu
chung này là thứ cho phép Coordinator (2.1) route, retry và đo latency mà không cần biết
agent làm gì bên trong.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any

from mas_dss.common.logging_utils import get_logger
from mas_dss.common.schemas import AgentResult, OrderCase


class BaseAgent(ABC):
    name: str = "base_agent"

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.log = get_logger(self.name)

    @abstractmethod
    def process(self, cases: list[OrderCase]) -> list[OrderCase]:
        """Làm giàu và trả lại các case. Được phép raise — Coordinator sẽ retry."""

    def run(self, cases: list[OrderCase]) -> tuple[list[OrderCase], AgentResult]:
        t0 = time.perf_counter()
        try:
            out = self.process(cases)
            latency = (time.perf_counter() - t0) * 1000
            return out, AgentResult(
                agent=self.name, ok=True, latency_ms=latency, n_cases=len(out)
            )
        except Exception as exc:  # Coordinator quyết định retry hay bỏ qua
            latency = (time.perf_counter() - t0) * 1000
            self.log.exception("agent failed: %s", exc)
            return cases, AgentResult(
                agent=self.name,
                ok=False,
                latency_ms=latency,
                error=f"{type(exc).__name__}: {exc}",
                n_cases=len(cases),
            )
