"""1.1 Data Ingestion Agent.

Trách nhiệm: đọc 9 bảng Olist thô, validate schema / null / duplicate, và trả về dict
DataFrame đã sạch ở mức bảng. Agent này KHÔNG join — việc đó thuộc về Preprocessing Agent.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from mas_dss.common.config import PROJECT_ROOT
from mas_dss.common.logging_utils import get_logger

# Khóa chính dùng để loại bản ghi trùng. Bảng nào không liệt kê ở đây (order_items,
# order_payments, geolocation) vốn có nhiều dòng trên mỗi order — không dedupe.
PRIMARY_KEYS = {
    "orders": ["order_id"],
    "products": ["product_id"],
    "customers": ["customer_id"],
    "sellers": ["seller_id"],
    "order_reviews": ["review_id"],
}

DATE_COLUMNS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_reviews": ["review_creation_date", "review_answer_timestamp"],
    "order_items": ["shipping_limit_date"],
}


class DataQualityReport(dict):
    """Báo cáo chất lượng dữ liệu — cũng là bằng chứng cho phần Demonstration (3.2.4)."""


class DataIngestionAgent:
    name = "ingestion_agent"

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.cfg = config["ingestion"]
        self.raw_dir = PROJECT_ROOT / config["paths"]["raw"]
        self.log = get_logger(self.name)
        self.report = DataQualityReport()

    def load_all(self) -> dict[str, pd.DataFrame]:
        tables: dict[str, pd.DataFrame] = {}
        for name, filename in self.cfg["tables"].items():
            path = self.raw_dir / filename
            if not path.exists():
                msg = f"Thiếu bảng '{name}' tại {path}. Tải dataset Olist vào data/raw/."
                if self.cfg["validation"]["fail_on_missing_table"]:
                    raise FileNotFoundError(msg)
                self.log.warning(msg)
                continue
            tables[name] = self._load_one(name, path)
        self.log.info("đã nạp %d bảng", len(tables))
        return tables

    def _load_one(self, name: str, path: Path) -> pd.DataFrame:
        df = pd.read_csv(path, parse_dates=DATE_COLUMNS.get(name, []))
        before = len(df)

        keys = PRIMARY_KEYS.get(name)
        if keys and self.cfg["validation"]["drop_duplicate_keys"]:
            df = df.drop_duplicates(subset=keys, keep="first")

        null_ratio = df.isna().mean()
        sparse = null_ratio[null_ratio > self.cfg["validation"]["max_null_ratio"]]
        if len(sparse):
            self.log.warning("%s: cột nhiều null %s", name, dict(sparse.round(3)))

        self.report[name] = {
            "rows_raw": before,
            "rows_clean": len(df),
            "duplicates_dropped": before - len(df),
            "columns": list(df.columns),
            "null_ratio": null_ratio.round(4).to_dict(),
        }
        self.log.info("%-22s %7d dòng (bỏ %d trùng)", name, len(df), before - len(df))
        return df
