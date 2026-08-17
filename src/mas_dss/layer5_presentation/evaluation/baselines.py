"""Hai chuẩn tham chiếu cho criterion validity (mục 3.2.5a).

MISBaseline mô phỏng MIS truyền thống: chỉ tổng hợp và hiển thị dữ liệu quá khứ, không dự
báo. Nó "phát hiện" đơn cần can thiệp bằng ngưỡng mô tả cố định (đơn đã trễ hẹn) — tức là
phản ứng *sau khi* sự cố đã xảy ra, không chủ động.

SingleModelBaseline là một mô hình ML đơn lẻ dự báo bất mãn: có năng lực dự báo ngang
Prediction Agent, nhưng thiếu Analytics context, thiếu phân loại nguyên nhân và thiếu
Rule Engine — nên nó dừng ở con số xác suất, không sinh ra được hành động quản trị.

Đối chiếu ba hệ này chính là thí nghiệm trung tâm của luận văn.
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np
import pandas as pd

from mas_dss.common.logging_utils import get_logger
from mas_dss.layer3_analytics.prediction_agent import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    build_pipeline,
)


class MISBaseline:
    """MIS truyền thống: báo cáo mô tả + ngưỡng thủ công."""

    name = "mis"

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.log = get_logger(self.name)
        self.latency_ms = 0.0

    def report(self, df: pd.DataFrame) -> dict[str, Any]:
        """Báo cáo định kỳ điển hình của MIS — thứ nhà quản lý nhận được hôm nay."""
        return {
            "orders": len(df),
            "avg_review_score": float(df["review_score"].mean()),
            "dissatisfaction_rate": float(df["is_dissatisfied"].mean()),
            "late_rate": float((df["delivery_delay_days"] > 0).mean()),
            "by_category": df.groupby("product_category")["is_dissatisfied"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .to_dict(),
            "by_state": df.groupby("customer_state")["is_dissatisfied"].mean().to_dict(),
        }

    def flag(self, df: pd.DataFrame) -> np.ndarray:
        """Cờ 'cần can thiệp' theo luật mô tả: đơn đã giao trễ hẹn.

        Cố ý *không* dùng mô hình — đây đúng là điểm hạn chế của MIS mà luận văn muốn đo:
        chỉ nhận ra vấn đề sau khi nó đã hiện ra trong dữ liệu quá khứ.
        """
        t0 = time.perf_counter()
        flags = (df["delivery_delay_days"] > 0).astype(int).to_numpy()
        self.latency_ms = (time.perf_counter() - t0) * 1000
        return flags

    def score(self, df: pd.DataFrame) -> np.ndarray:
        """MIS không có xác suất — quy cờ nhị phân thành pseudo-score để tính AUC."""
        return self.flag(df).astype(float)


class SingleModelBaseline:
    """Một mô hình ML đơn lẻ, không có agent orchestration."""

    name = "single_model"

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.seed = config["project"]["random_seed"]
        self.threshold = config["prediction"]["risk_bands"]["medium"]
        self.pipeline = build_pipeline(config["prediction"]["model"], self.seed)
        self.log = get_logger(self.name)
        self.latency_ms = 0.0

    def fit(self, train_df: pd.DataFrame) -> "SingleModelBaseline":
        self.pipeline.fit(
            train_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES], train_df["is_dissatisfied"]
        )
        return self

    def score(self, df: pd.DataFrame) -> np.ndarray:
        t0 = time.perf_counter()
        probs = self.pipeline.predict_proba(
            df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
        )[:, 1]
        self.latency_ms = (time.perf_counter() - t0) * 1000
        return probs

    def flag(self, df: pd.DataFrame) -> np.ndarray:
        return (self.score(df) >= self.threshold).astype(int)
