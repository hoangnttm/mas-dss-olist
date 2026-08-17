"""1.2 Data Preprocessing Agent.

Join orders + items + payments + products + sellers + customers + reviews thành một bảng
`order_case` ở mức *một dòng mỗi đơn hàng*, rồi sinh các đặc trưng dẫn xuất (delay, freight
ratio, review lag...). Đây là ranh giới quan trọng: từ sau bước này, các agent phía sau chỉ
làm việc với `OrderCase`, không còn chạm vào bảng thô.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from mas_dss.common.logging_utils import get_logger


class DataPreprocessingAgent:
    name = "preprocessing_agent"

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.cfg = config["preprocessing"]
        self.log = get_logger(self.name)

    def build_order_cases(self, t: dict[str, pd.DataFrame]) -> pd.DataFrame:
        df = t["orders"].copy()

        statuses = self.cfg["keep_order_status"]
        df = df[df["order_status"].isin(statuses)]
        self.log.info("giữ %d đơn có trạng thái %s", len(df), statuses)

        df = df.merge(self._agg_items(t["order_items"]), on="order_id", how="left")
        df = df.merge(self._agg_payments(t["order_payments"]), on="order_id", how="left")
        df = df.merge(self._agg_reviews(t["order_reviews"]), on="order_id", how="left")
        df = df.merge(
            t["customers"][["customer_id", "customer_state"]], on="customer_id", how="left"
        )
        df = df.merge(self._product_attrs(t), on="product_id", how="left")
        df = df.merge(
            t["sellers"][["seller_id", "seller_state"]], on="seller_id", how="left"
        )

        df = self._derive_features(df)
        df = df.dropna(subset=["review_score"])           # không nhãn thì không dùng được
        df["is_dissatisfied"] = (
            df["review_score"] <= self.cfg["dissatisfied_threshold"]
        ).astype(int)

        self.log.info(
            "order_cases: %d dòng, tỷ lệ không hài lòng %.1f%%",
            len(df),
            100 * df["is_dissatisfied"].mean(),
        )
        return df

    # --- các bước join ---------------------------------------------------------
    @staticmethod
    def _agg_items(items: pd.DataFrame) -> pd.DataFrame:
        """Gộp nhiều item về một dòng/đơn; giữ product_id & seller_id của item đắt nhất
        vì đó là item chi phối trải nghiệm và khiếu nại của khách."""
        agg = items.groupby("order_id").agg(
            price=("price", "sum"),
            freight_value=("freight_value", "sum"),
            n_items=("order_item_id", "count"),
            n_sellers=("seller_id", "nunique"),
        )
        dominant = (
            items.sort_values("price", ascending=False)
            .groupby("order_id")[["product_id", "seller_id"]]
            .first()
        )
        return agg.join(dominant).reset_index()

    @staticmethod
    def _agg_payments(payments: pd.DataFrame) -> pd.DataFrame:
        return (
            payments.groupby("order_id")
            .agg(
                payment_value=("payment_value", "sum"),
                payment_installments=("payment_installments", "max"),
                payment_type=("payment_type", "first"),
            )
            .reset_index()
        )

    @staticmethod
    def _agg_reviews(reviews: pd.DataFrame) -> pd.DataFrame:
        """Một đơn có thể có nhiều review — lấy review mới nhất."""
        r = reviews.sort_values("review_creation_date").groupby("order_id").last()
        return r[
            [
                "review_score",
                "review_creation_date",
                "review_comment_title",
                "review_comment_message",
            ]
        ].reset_index()

    @staticmethod
    def _product_attrs(t: dict[str, pd.DataFrame]) -> pd.DataFrame:
        p = t["products"][
            [
                "product_id",
                "product_category_name",
                "product_weight_g",
                "product_photos_qty",
                "product_description_lenght",
            ]
        ].copy()
        if "category_translation" in t:
            p = p.merge(
                t["category_translation"], on="product_category_name", how="left"
            )
            p["product_category"] = p["product_category_name_english"].fillna(
                p["product_category_name"]
            )
        else:
            p["product_category"] = p["product_category_name"]
        p["product_category"] = p["product_category"].fillna("unknown")
        return p[
            [
                "product_id",
                "product_category",
                "product_weight_g",
                "product_photos_qty",
                "product_description_lenght",
            ]
        ].rename(columns={"product_description_lenght": "description_length"})

    # --- đặc trưng dẫn xuất ----------------------------------------------------
    def _derive_features(self, df: pd.DataFrame) -> pd.DataFrame:
        day = np.timedelta64(1, "D")
        hour = np.timedelta64(1, "h")

        df["delivery_days"] = (
            df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
        ) / day
        df["estimated_delivery_days"] = (
            df["order_estimated_delivery_date"] - df["order_purchase_timestamp"]
        ) / day
        # Dương = giao trễ so với hẹn. Đây là tín hiệu mạnh nhất của bất mãn trong Olist.
        df["delivery_delay_days"] = (
            df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]
        ) / day
        df["approval_lag_hours"] = (
            df["order_approved_at"] - df["order_purchase_timestamp"]
        ) / hour
        df["carrier_handover_days"] = (
            df["order_delivered_carrier_date"] - df["order_purchase_timestamp"]
        ) / day
        df["review_lag_days"] = (
            df["review_creation_date"] - df["order_delivered_customer_date"]
        ) / day

        df["freight_ratio"] = df["freight_value"] / df["price"].replace(0, np.nan)
        df["same_state"] = (df["customer_state"] == df["seller_state"]).astype(int)

        numeric = [
            "price",
            "freight_value",
            "freight_ratio",
            "payment_value",
            "payment_installments",
            "n_items",
            "n_sellers",
            "product_weight_g",
            "product_photos_qty",
            "description_length",
            "delivery_days",
            "estimated_delivery_days",
            "delivery_delay_days",
            "approval_lag_hours",
            "carrier_handover_days",
            "review_lag_days",
        ]
        for col in numeric:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        for col in ["customer_state", "seller_state", "product_category"]:
            df[col] = df[col].fillna("unknown")
        return df
