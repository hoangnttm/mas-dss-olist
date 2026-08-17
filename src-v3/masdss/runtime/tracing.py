"""WP0 / T5.7 — Do span thu cong. 1 trace = 1 case, 1 span = 1 message.

Phuc vu: RQ1 ve (d) — chi phi phai tra cho kha nang chiu loi.

LUU Y VE TINH TAT DINH: file nay la cho DUY NHAT trong logic he thong duoc phep
doc dong ho (perf_counter), vi do tre la thu can do. De khong pha vo dieu kien tai
lap, ket qua do KHONG duoc dua vao tep dau ra chinh tac:

    decisions.jsonl   -> tat dinh, la doi tuong cua test tai lap
    spans.sqlite      -> co do tre, KHONG so sanh giua hai lan chay

Xem tests-v3/test_determinism.py.
"""

from __future__ import annotations

import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

_SCHEMA = """
CREATE TABLE IF NOT EXISTS spans (
    span_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id    TEXT NOT NULL,
    name        TEXT NOT NULL,
    agent_id    TEXT,
    duration_ms REAL NOT NULL,
    ok          INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_trace ON spans(trace_id);
"""


@dataclass
class Span:
    trace_id: str
    name: str
    agent_id: str | None
    duration_ms: float
    ok: bool


class SpanRecorder:
    """Ghi do tre theo tung buoc. Khong phai he truy vet phan tan — khong can."""

    def __init__(self, path: Path | str | None = None) -> None:
        self.spans: list[Span] = []
        self.path = Path(path) if path else None
        self._conn: sqlite3.Connection | None = None
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self.path)
            self._conn.executescript(_SCHEMA)
            self._conn.commit()

    @contextmanager
    def span(self, trace_id: str, name: str, agent_id: str | None = None) -> Iterator[None]:
        start = time.perf_counter()
        ok = True
        try:
            yield
        except Exception:
            ok = False
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000.0
            self._record(Span(trace_id, name, agent_id, duration_ms, ok))

    def _record(self, span: Span) -> None:
        self.spans.append(span)
        if self._conn is not None:
            self._conn.execute(
                "INSERT INTO spans (trace_id, name, agent_id, duration_ms, ok) VALUES (?,?,?,?,?)",
                (span.trace_id, span.name, span.agent_id, span.duration_ms, int(span.ok)),
            )
            self._conn.commit()

    def percentile(self, q: float, name: str | None = None) -> float:
        """p50 / p95 cho bao cao chi phi kien truc (RQ1 ve d)."""
        values = sorted(s.duration_ms for s in self.spans if name is None or s.name == name)
        if not values:
            return 0.0
        index = min(int(q * len(values)), len(values) - 1)
        return values[index]

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
