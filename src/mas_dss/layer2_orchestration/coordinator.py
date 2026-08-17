"""2.1 Coordinator / Orchestrator Agent.

Nhận mini-batch `OrderCase`, route lần lượt qua chuỗi agent chuyên biệt, quản lý retry /
timeout / logging và đo end-to-end processing time. Coordinator không biết agent làm gì —
nó chỉ biết mọi agent tuân theo giao diện `BaseAgent.run()`.

`disabled_agents` là cơ chế phục vụ thí nghiệm ablation (causal validity, mục 3.2.5b):
tắt Root-Cause hoặc Recommendation Agent rồi đo mức suy giảm của hệ thống.
"""

from __future__ import annotations

import time
from typing import Any, Iterable, Sequence

from mas_dss.common.base_agent import BaseAgent
from mas_dss.common.logging_utils import TraceWriter, get_logger
from mas_dss.common.schemas import AgentResult, OrderCase


class CoordinatorAgent:
    name = "coordinator"

    def __init__(
        self,
        config: dict[str, Any],
        agents: Sequence[BaseAgent],
        disabled_agents: Iterable[str] = (),
    ):
        self.config = config
        self.cfg = config["orchestration"]
        self.disabled = set(disabled_agents)
        self.agents = [a for a in agents if a.name not in self.disabled]
        self.trace = TraceWriter(config["orchestration"]["trace_log"])
        self.log = get_logger(self.name)
        self.results: list[AgentResult] = []
        self.pipeline_latency_ms: float = 0.0

        if self.disabled:
            self.log.warning("ablation — đã tắt agent: %s", sorted(self.disabled))

    def run(self, cases: list[OrderCase]) -> list[OrderCase]:
        """Chạy toàn bộ tập case theo mini-batch."""
        t0 = time.perf_counter()
        batch_size = self.cfg["batch_size"]
        out: list[OrderCase] = []
        for i in range(0, len(cases), batch_size):
            out.extend(self.run_batch(cases[i : i + batch_size], batch_no=i // batch_size))
        self.pipeline_latency_ms = (time.perf_counter() - t0) * 1000
        self.log.info(
            "pipeline xong: %d case trong %.0f ms (%.1f case/s)",
            len(out),
            self.pipeline_latency_ms,
            len(out) / max(self.pipeline_latency_ms / 1000, 1e-9),
        )
        return out

    def run_batch(self, batch: list[OrderCase], batch_no: int = 0) -> list[OrderCase]:
        for agent in self.agents:
            batch, result = self._run_with_retry(agent, batch)
            self.results.append(result)
            self.trace.write(
                {
                    "event": "agent_run",
                    "batch": batch_no,
                    "agent": result.agent,
                    "ok": result.ok,
                    "latency_ms": round(result.latency_ms, 2),
                    "n_cases": result.n_cases,
                    "error": result.error,
                }
            )
        return batch

    def _run_with_retry(
        self, agent: BaseAgent, batch: list[OrderCase]
    ) -> tuple[list[OrderCase], AgentResult]:
        attempts = self.cfg["max_retries"] + 1
        timeout_ms = self.cfg["agent_timeout_s"] * 1000
        result = AgentResult(agent=agent.name, ok=False, error="not run")

        for attempt in range(attempts):
            out, result = agent.run(batch)
            if result.ok and result.latency_ms <= timeout_ms:
                return out, result
            if result.ok:
                # Vượt timeout: vẫn nhận kết quả nhưng đánh dấu để Layer 5 thống kê.
                result.ok = False
                result.error = f"timeout: {result.latency_ms:.0f}ms > {timeout_ms:.0f}ms"
                self.log.warning("%s vượt timeout", agent.name)
                return out, result
            self.log.warning(
                "%s lỗi (lần %d/%d): %s", agent.name, attempt + 1, attempts, result.error
            )
        return batch, result

    def latency_by_agent(self) -> dict[str, float]:
        """Tổng latency theo agent — dùng cho biểu đồ phân rã thời gian ở Layer 5."""
        agg: dict[str, float] = {}
        for r in self.results:
            agg[r.agent] = agg.get(r.agent, 0.0) + r.latency_ms
        return agg
