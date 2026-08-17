"""3.2 Prediction Agent.

Dự báo rủi ro không hài lòng cho từng đơn: P(review_score <= 3). Đầu ra gồm
`predicted_score`, `risk_score`, `risk_level` và `confidence` — chính là input cho
Root-Cause Agent và cho DSS Rule Engine.

Cùng một class model được dùng lại cho single-model baseline (Layer 5), nhưng ở baseline
nó chạy *không có* AnalyticsContext và không có bước phân loại nguyên nhân — đó là điểm
khác biệt mà thí nghiệm so sánh muốn đo.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from mas_dss.common.base_agent import BaseAgent
from mas_dss.common.schemas import OrderCase, Prediction, RiskLevel

NUMERIC_FEATURES = [
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
    "same_state",
]
CATEGORICAL_FEATURES = ["product_category", "customer_state", "seller_state"]


def build_estimator(name: str, seed: int):
    if name == "lightgbm":
        try:
            from lightgbm import LGBMClassifier

            return LGBMClassifier(
                n_estimators=400,
                learning_rate=0.05,
                num_leaves=48,
                class_weight="balanced",
                random_state=seed,
                verbose=-1,
            )
        except ImportError:  # lightgbm là optional — không có thì lùi về RF
            name = "random_forest"
    if name == "random_forest":
        return RandomForestClassifier(
            n_estimators=300,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=seed,
            n_jobs=-1,
        )
    return LogisticRegression(max_iter=1000, class_weight="balanced", random_state=seed)


def build_pipeline(model_name: str, seed: int) -> Pipeline:
    pre = ColumnTransformer(
        [
            ("num", StandardScaler(), NUMERIC_FEATURES),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", min_frequency=20),
                CATEGORICAL_FEATURES,
            ),
        ]
    )
    return Pipeline([("pre", pre), ("clf", build_estimator(model_name, seed))])


class PredictionAgent(BaseAgent):
    name = "prediction_agent"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.cfg = config["prediction"]
        self.seed = config["project"]["random_seed"]
        self.model_name = self.cfg["model"]
        self.pipeline: Pipeline | None = None

    def fit(self, train_df: pd.DataFrame) -> "PredictionAgent":
        self.pipeline = build_pipeline(self.model_name, self.seed)
        self.pipeline.fit(
            train_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES], train_df["is_dissatisfied"]
        )
        self.log.info("đã huấn luyện %s trên %d mẫu", self.model_name, len(train_df))
        return self

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        assert self.pipeline is not None, "Model chưa được huấn luyện/nạp."
        return self.pipeline.predict_proba(df[NUMERIC_FEATURES + CATEGORICAL_FEATURES])[:, 1]

    def process(self, cases: list[OrderCase]) -> list[OrderCase]:
        df = pd.DataFrame([c.features.model_dump() for c in cases])
        probs = self.predict_proba(df)
        for case, p in zip(cases, probs):
            case.prediction = Prediction(
                predicted_score=self._to_review_score(p),
                risk_score=float(p),
                risk_level=self._to_risk_level(p),
                # Xa 0.5 = mô hình dứt khoát; gần 0.5 = mơ hồ. Rule R06 dùng chính điều này.
                confidence=float(abs(p - 0.5) * 2),
                model_name=self.model_name,
            )
        return cases

    def _to_risk_level(self, p: float) -> RiskLevel:
        bands = self.cfg["risk_bands"]
        if p >= bands["medium"]:
            return RiskLevel.HIGH
        if p >= bands["low"]:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    @staticmethod
    def _to_review_score(p: float) -> float:
        """Quy đổi xác suất bất mãn về thang review 1-5 để nhà quản lý dễ đọc."""
        return float(round(5.0 - 4.0 * p, 2))

    def save(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"pipeline": self.pipeline, "model_name": self.model_name}, path)
        self.log.info("đã lưu model -> %s", path)

    def load(self, path: str | Path) -> "PredictionAgent":
        blob = joblib.load(path)
        self.pipeline = blob["pipeline"]
        self.model_name = blob["model_name"]
        return self
