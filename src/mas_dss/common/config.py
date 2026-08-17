"""Nạp cấu hình YAML và giải các đường dẫn theo project root."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]


@lru_cache(maxsize=8)
def load_config(path: str | Path = "config/config.yaml") -> dict[str, Any]:
    cfg_path = PROJECT_ROOT / path if not Path(path).is_absolute() else Path(path)
    with open(cfg_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg["_root"] = str(PROJECT_ROOT)
    return cfg


def resolve(cfg: dict[str, Any], key: str) -> Path:
    """`resolve(cfg, "feature_store")` -> đường dẫn tuyệt đối, tự tạo thư mục cha."""
    p = PROJECT_ROOT / cfg["paths"][key]
    p.parent.mkdir(parents=True, exist_ok=True)
    return p
