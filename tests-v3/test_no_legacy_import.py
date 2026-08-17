"""WP0 — Cam moi tham chieu tu codebase v3 sang codebase cu.

`src/mas_dss/` da DONG BANG (implementation-plan.md §1). Codebase cu mang nhung
thu da bi bac bo: `review_lag_days`, hanh dong `expedite_shipment`, quy ket don
nhan bang argmax. Import lai "cho nhanh" se keo nguyen loi cu vao he moi.

Rui ro nay duoc xep muc CAO trong implementation-plan.md §7.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_V3 = ROOT / "src-v3" / "masdss"

LEGACY_ROOTS = {"mas_dss", "mas_dss_olist"}


def _legacy_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in LEGACY_ROOTS:
                    found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in LEGACY_ROOTS:
                found.add(node.module)
    return found


def test_v3_never_imports_legacy_package() -> None:
    violations: list[str] = []
    for file in sorted(SRC_V3.rglob("*.py")):
        for name in _legacy_imports(file):
            violations.append(f"{file.relative_to(ROOT)} -> {name}")
    assert not violations, (
        "Codebase v3 import codebase cu da dong bang:\n  " + "\n  ".join(violations)
    )


def test_v3_never_writes_to_legacy_artifacts() -> None:
    """Dau ra moi phai di sang data/v3, models/v3, config/v3.

    Ghi de len `data/processed/` hay `config/dss_rules.yaml` lam mat kha nang doi
    chieu "truoc va sau" giua hai kien truc.
    """
    forbidden_literals = ("data/processed", "config/dss_rules.yaml", "config/config.yaml")
    violations: list[str] = []
    for file in sorted(SRC_V3.rglob("*.py")):
        text = file.read_text(encoding="utf-8")
        for literal in forbidden_literals:
            if literal in text:
                violations.append(f"{file.relative_to(ROOT)} nhac toi '{literal}'")
    assert not violations, "\n  ".join(violations)
