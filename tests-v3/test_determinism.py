"""WP0 / T0.4 — Tinh tat dinh.

Phuc vu: RQ1 (Gate G5 — ket qua chaos chi co gia tri neu tai lap duoc).

Hai lan chay cung cau hinh phai sinh ra tep `decisions.jsonl` GIONG NHAU DEN TUNG
BYTE. Do la dieu kien de dua so lieu vao luan van, khong phai mong muon.

`spans.sqlite` co do tre nen KHONG nam trong pham vi so sanh — do la ly do hai tep
duoc tach ra ngay tu dau (runtime/tracing.py).
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from masdss.cli.run_system import run
from masdss.config import deterministic_uuid

from conftest import N_CASES


def test_two_runs_are_byte_identical(tmp_path: Path, fixtures) -> None:
    orders, caps = fixtures
    first = asyncio.run(run(tmp_path / "run1", n_cases=N_CASES,
                            orders=orders, capabilities=caps))
    second = asyncio.run(run(tmp_path / "run2", n_cases=N_CASES,
                             orders=orders, capabilities=caps))
    assert first.read_bytes() == second.read_bytes()


def test_deterministic_uuid_is_stable() -> None:
    """uuid4() bi cam trong toan bo codebase — no pha tinh tai lap."""
    a = deterministic_uuid("conv", "case-0001")
    b = deterministic_uuid("conv", "case-0001")
    c = deterministic_uuid("conv", "case-0002")
    assert a == b
    assert a != c


def test_no_uuid4_call_in_codebase() -> None:
    """Quet bang AST, khong quet van ban tho — comment nhac toi uuid4 la hop le."""
    import ast

    src = Path(__file__).resolve().parents[1] / "src-v3" / "masdss"
    offenders: list[str] = []
    for file in src.rglob("*.py"):
        tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if name == "uuid4":
                offenders.append(f"{file.relative_to(src)}:{node.lineno}")
    assert not offenders, f"uuid4() pha tinh tat dinh, dung deterministic_uuid(): {offenders}"


def test_chaos_run_is_reproducible(tmp_path: Path, fixtures) -> None:
    """Cung seed, cung kich ban loi -> cung ket qua. Day la Gate G5 thu nho."""
    orders, caps = fixtures
    first = asyncio.run(run(tmp_path / "c1", n_cases=N_CASES, inject="crash:Prediction",
                            orders=orders, capabilities=caps))
    second = asyncio.run(run(tmp_path / "c2", n_cases=N_CASES, inject="crash:Prediction",
                             orders=orders, capabilities=caps))
    assert first.read_bytes() == second.read_bytes()
