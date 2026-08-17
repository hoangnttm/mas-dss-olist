"""WP0 — Giao dien Capability.  [technical-plan-v3.md §5.2]

Phuc vu: RQ3, RQ1 (tinh cong bang cua phep so sanh).

Tang nay la BIEU HIEN KIEN TRUC cua yeu cau cong bang: vi baseline va MAS-DSS
cung `import` tu day, khong ton tai kha nang "vo tinh cho MAS mo hinh tot hon".
Day khong phai quy uoc dao duc nghien cuu — day la rang buoc do cau truc ma nguon
ap dat, va duoc kiem tra boi tests-v3/test_layering.py.

Capability la HAM THUAN: khong side effect, khong biet gi ve agent.

O Dot 0, moi cai dat o day deu la GIA va chi tra hang so. Cam viet mo hinh that
trong Dot 0 (implementation-plan.md §7) — capability that thuoc Dot 1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from masdss.core.ontology import OrderCase


@runtime_checkable
class Capability(Protocol):
    """Nang luc nen: mo hinh ML, tap luat, hoac engine tinh toan."""

    name: str
    cost_ms: float

    def can_handle(self, case: OrderCase) -> bool:
        """Co so KIEM CHUNG DUOC cua quyen REFUSE (DP3)."""

    def run(self, case: OrderCase) -> Any:
        """Thuc hien. Thuan, tat dinh, khong side effect."""


@dataclass(frozen=True)
class StubRisk:
    """[GIA - Dot 0] Tra rui ro co dinh theo hash cua case_id.

    Tat dinh theo case_id nen hai lan chay cho cung ket qua. Se bi thay boi
    capabilities/risk_model.py (LightGBM + isotonic) o Dot 1 / T3.1.
    """

    name: str = "stub_risk"
    cost_ms: float = 0.5

    def can_handle(self, case: OrderCase) -> bool:
        return True

    def run(self, case: OrderCase) -> float:
        digits = sum(ord(ch) for ch in case.case_id)
        return round((digits % 100) / 100.0, 4)


@dataclass(frozen=True)
class StubContext:
    """[GIA - Dot 0] Chi bao ngu canh. Se bi thay o Dot 1."""

    name: str = "stub_context"
    cost_ms: float = 0.2

    def can_handle(self, case: OrderCase) -> bool:
        return True

    def run(self, case: OrderCase) -> dict:
        return {
            "has_text_evidence": case.has_text_evidence,
            "tier": "A" if case.has_text_evidence else "B",
        }
