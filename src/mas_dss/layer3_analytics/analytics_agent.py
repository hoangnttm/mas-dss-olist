"""3.1 Analytics Agent.

Thống kê mô tả + phát hiện mẫu bất thường, rồi gắn các chỉ báo ngữ cảnh vào `OrderCase`.
Các thống kê theo seller/category được tính sẵn từ tập huấn luyện (`fit`) để tránh rò rỉ
nhãn: khi chạy trên đơn mới, agent chỉ *tra cứu*, không tính lại từ nhãn của chính đơn đó.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from mas_dss.common.base_agent import BaseAgent
from mas_dss.common.schemas import AnalyticsContext, OrderCase


class AnalyticsAgent(BaseAgent):
    name = "analytics_agent"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.cfg = config["analytics"]
        self.seller_stats: dict[str, dict[str, float]] = {}
        self.category_stats: dict[str, float] = {}
        self.global_complaint_rate: float = 0.0

    def fit(self, train_df: pd.DataFrame) -> "AnalyticsAgent":
        late = train_df["delivery_delay_days"] > self.cfg["late_delivery_days"]
        by_seller = train_df.assign(is_late=late).groupby("seller_id").agg(
            late_rate=("is_late", "mean"), avg_review=("review_score", "mean")
        )
        self.seller_stats = by_seller.to_dict(orient="index")
        self.category_stats = (
            train_df.groupby("product_category")["is_dissatisfied"].mean().to_dict()
        )
        self.global_complaint_rate = float(train_df["is_dissatisfied"].mean())
        self.log.info(
            "đã học thống kê cho %d seller, %d category",
            len(self.seller_stats),
            len(self.category_stats),
        )
        return self

    def process(self, cases: list[OrderCase]) -> list[OrderCase]:
        for case in cases:
            f = case.features
            flags: list[str] = []

            is_late = f.delivery_delay_days > self.cfg["late_delivery_days"]
            is_slow = f.delivery_days > self.cfg["slow_shipping_days"]
            is_high_freight = f.freight_ratio >= self.cfg["high_freight_ratio"]

            if is_late:
                flags.append(f"late_delivery(+{f.delivery_delay_days:.1f}d)")
            if is_slow:
                flags.append(f"slow_shipping({f.delivery_days:.1f}d)")
            if is_high_freight:
                flags.append(f"high_freight_ratio({f.freight_ratio:.2f})")

            seller = self.seller_stats.get(case.seller_id, {})
            seller_late_rate = float(seller.get("late_rate", 0.0))
            seller_avg_review = float(seller.get("avg_review", 0.0))
            if seller_late_rate >= 0.3:
                flags.append(f"seller_late_rate({seller_late_rate:.2f})")

            cat_rate = float(
                self.category_stats.get(f.product_category, self.global_complaint_rate)
            )
            if cat_rate > self.global_complaint_rate * 1.25:
                flags.append(f"high_complaint_category({cat_rate:.2f})")

            case.analytics = AnalyticsContext(
                is_late=bool(is_late),
                is_slow_shipping=bool(is_slow),
                is_high_freight=bool(is_high_freight),
                seller_late_rate=seller_late_rate,
                seller_avg_review=seller_avg_review,
                category_complaint_rate=cat_rate,
                anomaly_flags=flags,
            )
        return cases

    def kpi_summary(self, df: pd.DataFrame) -> dict[str, float]:
        """KPI mô tả cho dashboard và cho MIS baseline."""
        return {
            "n_orders": len(df),
            "dissatisfaction_rate": float(df["is_dissatisfied"].mean()),
            "avg_review_score": float(df["review_score"].mean()),
            "late_delivery_rate": float((df["delivery_delay_days"] > 0).mean()),
            "avg_delivery_days": float(df["delivery_days"].mean()),
            "avg_freight_ratio": float(df["freight_ratio"].mean()),
        }
