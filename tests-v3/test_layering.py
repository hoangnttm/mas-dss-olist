"""WP0 / T0.3 — Kiem tra rang buoc phan tang.

Phuc vu: RQ3, RQ1 (tinh cong bang cua phep so sanh).

Tang `capabilities/` duoc MAS-DSS va moi baseline dung chung. Neu no biet gi ve
`agents/`, `system/` hay `chaos/` thi khong the dung chung, va phep so sanh mat
tinh cong bang ngay tu kien truc.

Xem technical-plan-v3.md §3, §5.2.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src-v3" / "masdss"

# Tang duoi khong duoc biet gi ve tang tren.
FORBIDDEN: dict[str, set[str]] = {
    "capabilities": {"agents", "system", "chaos", "evaluation", "baselines", "cli"},
    "core": {"agents", "system", "chaos", "evaluation", "baselines", "cli", "capabilities",
             "runtime", "data"},
    "runtime": {"agents", "system", "chaos", "evaluation", "baselines", "cli", "capabilities"},
    "data": {"agents", "system", "chaos", "evaluation", "baselines", "cli", "capabilities"},
}


def _imported_subpackages(path: Path) -> set[str]:
    """Tra ve tap sub-package cua masdss ma file nay import."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("masdss."):
                    found.add(alias.name.split(".")[1])
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # import tuong doi: .x / ..x
                continue
            if node.module and node.module.startswith("masdss."):
                found.add(node.module.split(".")[1])
    return found


def _files_of(subpackage: str) -> list[Path]:
    return sorted((SRC / subpackage).rglob("*.py"))


@pytest.mark.parametrize("subpackage", sorted(FORBIDDEN))
def test_layer_does_not_import_upper_layers(subpackage: str) -> None:
    violations: list[str] = []
    for file in _files_of(subpackage):
        for imported in _imported_subpackages(file) & FORBIDDEN[subpackage]:
            violations.append(f"{file.relative_to(SRC)} -> masdss.{imported}")
    assert not violations, (
        f"Tang '{subpackage}' import tang tren:\n  " + "\n  ".join(violations)
    )


def test_orchestrator_is_isolated() -> None:
    """WP0 / T6.3 — bo thuc thi phai co lap de doi engine chi can mot adapter.

    Xem technical-plan-v3.md §5.5.
    """
    orchestrator = SRC / "system" / "orchestrator.py"
    if not orchestrator.exists():
        pytest.skip("orchestrator.py chua duoc tao")
    forbidden = {"agents", "chaos", "evaluation", "baselines"}
    leaked = _imported_subpackages(orchestrator) & forbidden
    assert not leaked, f"orchestrator.py khong duoc import: {sorted(leaked)}"
