"""Huấn luyện Prediction Agent + Root-Cause Agent + thống kê Analytics Agent.

Split theo *thời gian mua hàng* chứ không random: hệ thống thật luôn dự báo đơn tương lai
bằng dữ liệu quá khứ, split ngẫu nhiên sẽ thổi phồng kết quả.

Chạy: python -m mas_dss.pipelines.train_models
"""

from __future__ import annotations

import joblib
import pandas as pd

from mas_dss.common.config import PROJECT_ROOT, load_config
from mas_dss.common.logging_utils import get_logger
from mas_dss.layer1_data_integration.feature_store import FeatureStore
from mas_dss.layer3_analytics.analytics_agent import AnalyticsAgent
from mas_dss.layer3_analytics.prediction_agent import PredictionAgent
from mas_dss.layer3_analytics.root_cause_agent import RootCauseAgent

log = get_logger("train_models")


def temporal_split(df: pd.DataFrame, test_size: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df.sort_values("order_purchase_timestamp")
    cut = int(len(df) * (1 - test_size))
    train, test = df.iloc[:cut], df.iloc[cut:]
    log.info(
        "split thời gian: train %d (đến %s) | test %d (từ %s)",
        len(train),
        train["order_purchase_timestamp"].max().date(),
        len(test),
        test["order_purchase_timestamp"].min().date(),
    )
    return train, test


def main() -> None:
    cfg = load_config()
    models_dir = PROJECT_ROOT / cfg["paths"]["models"]
    models_dir.mkdir(parents=True, exist_ok=True)

    df = FeatureStore(cfg).load_frame()
    train, test = temporal_split(df, cfg["prediction"]["test_size"])

    test_ids = set(test["order_id"])
    joblib.dump(test_ids, models_dir / "test_order_ids.pkl")

    analytics = AnalyticsAgent(cfg).fit(train)
    joblib.dump(
        {
            "seller_stats": analytics.seller_stats,
            "category_stats": analytics.category_stats,
            "global_complaint_rate": analytics.global_complaint_rate,
        },
        models_dir / "analytics_stats.pkl",
    )

    PredictionAgent(cfg).fit(train).save(models_dir / "prediction_agent.pkl")
    RootCauseAgent(cfg).fit(train).save(models_dir / "root_cause_agent.pkl")
    log.info("đã lưu toàn bộ model vào %s", models_dir)


if __name__ == "__main__":
    main()
