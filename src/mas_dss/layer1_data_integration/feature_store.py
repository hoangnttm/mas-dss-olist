"""1.3 Feature Store / Operational Data Store.

Lưu bảng `order_case` đã curate ra Parquet và cung cấp hai chiều đọc:
DataFrame (cho huấn luyện, cho MIS baseline) và list[OrderCase] (cho các agent).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from mas_dss.common.config import resolve
from mas_dss.common.logging_utils import get_logger
from mas_dss.common.schemas import OrderCase, OrderFeatures

FEATURE_FIELDS = set(OrderFeatures.model_fields)


class FeatureStore:
    name = "feature_store"

    def __init__(self, config: dict[str, Any]):
        self.path: Path = resolve(config, "feature_store")
        self.log = get_logger(self.name)

    def save(self, df: pd.DataFrame) -> None:
        df.to_parquet(self.path, index=False)
        self.log.info("đã ghi %d order_case -> %s", len(df), self.path)

    def load_frame(self) -> pd.DataFrame:
        if not self.path.exists():
            raise FileNotFoundError(
                f"Chưa có feature store tại {self.path}. Chạy: python -m mas_dss.pipelines.build_dataset"
            )
        return pd.read_parquet(self.path)

    def load_cases(self, limit: int | None = None) -> list[OrderCase]:
        df = self.load_frame()
        if limit:
            df = df.head(limit)
        return [self.row_to_case(r) for r in df.to_dict(orient="records")]

    @staticmethod
    def row_to_case(row: dict[str, Any]) -> OrderCase:
        features = OrderFeatures(**{k: v for k, v in row.items() if k in FEATURE_FIELDS})
        return OrderCase(
            order_id=row["order_id"],
            customer_id=row.get("customer_id", ""),
            seller_id=row.get("seller_id") or "",
            order_purchase_ts=row.get("order_purchase_timestamp"),
            order_delivered_ts=row.get("order_delivered_customer_date"),
            order_estimated_delivery_ts=row.get("order_estimated_delivery_date"),
            features=features,
            review_score=int(row["review_score"]) if pd.notna(row.get("review_score")) else None,
            is_dissatisfied=int(row["is_dissatisfied"]) if "is_dissatisfied" in row else None,
        )
