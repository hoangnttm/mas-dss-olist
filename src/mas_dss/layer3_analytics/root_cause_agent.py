"""3.3 Root Cause Analysis Agent.

Phân loại nguyên nhân bất mãn thành 4 nhóm: delivery / product_quality /
customer_service / price.

Olist không có nhãn nguyên nhân sẵn, nên ta dùng **weak supervision**: hàm gán nhãn
(`label_causes`) sinh nhãn giả từ từ khóa trong bình luận review (tiếng Bồ Đào Nha) kết
hợp tín hiệu định lượng (trễ hẹn, freight ratio). Nhãn giả đó huấn luyện một classifier
chỉ dùng *đặc trưng có sẵn tại thời điểm dự báo* — nhờ vậy khi chạy online, agent không
cần bình luận review (vốn chỉ xuất hiện sau khi khách đã bất mãn).

Hạn chế của cách gán nhãn này phải được nêu rõ trong phần Threats to validity của luận văn.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from mas_dss.common.base_agent import BaseAgent
from mas_dss.common.schemas import CauseLabel, OrderCase, RootCause

from .prediction_agent import CATEGORICAL_FEATURES, NUMERIC_FEATURES, build_pipeline

# Từ khóa tiếng Bồ Đào Nha trong review Olist, theo từng nhóm nguyên nhân.
CAUSE_KEYWORDS: dict[str, list[str]] = {
    "delivery": [
        "entrega", "atraso", "atrasado", "prazo", "chegou", "nao chegou", "não chegou",
        "demorou", "correio", "transportadora", "frete demorado",
    ],
    "product_quality": [
        "quebrado", "danificado", "defeito", "qualidade", "ruim", "estragado",
        "diferente", "errado", "nao funciona", "não funciona", "falsificado",
    ],
    "customer_service": [
        "atendimento", "resposta", "contato", "suporte", "reclamacao", "reclamação",
        "nao responde", "não responde", "descaso",
    ],
    "price": [
        "caro", "preco", "preço", "frete caro", "cobrado", "valor", "cobranca", "cobrança",
    ],
}


def label_causes(df: pd.DataFrame, min_conf: float = 0.4) -> pd.Series:
    """Sinh nhãn nguyên nhân yếu (weak label) cho các đơn bất mãn.

    Đơn hài lòng -> NaN (không tham gia huấn luyện). Ưu tiên bằng chứng văn bản; khi
    bình luận rỗng hoặc không khớp từ khóa, quay về tín hiệu định lượng.
    """
    text = (
        df.get("review_comment_message", pd.Series("", index=df.index)).fillna("")
        + " "
        + df.get("review_comment_title", pd.Series("", index=df.index)).fillna("")
    ).str.lower()

    scores = pd.DataFrame(
        {
            cause: text.apply(lambda t, kws=kws: sum(kw in t for kw in kws))
            for cause, kws in CAUSE_KEYWORDS.items()
        },
        index=df.index,
    )

    labels = pd.Series(np.nan, index=df.index, dtype=object)
    dissatisfied = df["is_dissatisfied"] == 1

    has_text = scores.sum(axis=1) > 0
    labels[dissatisfied & has_text] = scores[dissatisfied & has_text].idxmax(axis=1)

    # Fallback định lượng cho đơn bất mãn không có bình luận hữu ích.
    fallback = dissatisfied & ~has_text
    labels[fallback & (df["delivery_delay_days"] > 0)] = "delivery"
    labels[fallback & (df["delivery_delay_days"] <= 0) & (df["freight_ratio"] >= 0.25)] = "price"
    labels[labels.isna() & fallback] = "product_quality"
    return labels


class RootCauseAgent(BaseAgent):
    name = "root_cause_agent"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.cfg = config["root_cause"]
        self.seed = config["project"]["random_seed"]
        self.pipeline = None
        self.classes_: list[str] = []

    def fit(self, train_df: pd.DataFrame) -> "RootCauseAgent":
        labels = label_causes(train_df, self.cfg["min_confidence"])
        mask = labels.notna()
        sub = train_df[mask]
        y = labels[mask].astype(str)
        self.log.info(
            "weak labels: %d mẫu — phân bố %s",
            len(sub),
            y.value_counts(normalize=True).round(3).to_dict(),
        )

        self.pipeline = build_pipeline("random_forest", self.seed)
        self.pipeline.fit(sub[NUMERIC_FEATURES + CATEGORICAL_FEATURES], y)
        self.classes_ = list(self.pipeline.named_steps["clf"].classes_)
        return self

    def process(self, cases: list[OrderCase]) -> list[OrderCase]:
        assert self.pipeline is not None, "RootCauseAgent chưa được huấn luyện/nạp."
        df = pd.DataFrame([c.features.model_dump() for c in cases])
        probs = self.pipeline.predict_proba(df[NUMERIC_FEATURES + CATEGORICAL_FEATURES])

        for case, row in zip(cases, probs):
            dist = {cls: float(p) for cls, p in zip(self.classes_, row)}
            best = max(dist, key=dist.get)
            conf = dist[best]
            label = (
                CauseLabel(best) if conf >= self.cfg["min_confidence"] else CauseLabel.UNKNOWN
            )
            case.root_cause = RootCause(
                cause_label=label,
                cause_probability=conf,
                cause_distribution=dist,
                evidence=self._evidence(case),
            )
        return cases

    @staticmethod
    def _evidence(case: OrderCase) -> list[str]:
        """Bằng chứng người-đọc-được, đi thẳng vào decision trace (4.2)."""
        ev: list[str] = []
        f = case.features
        if f.delivery_delay_days > 0:
            ev.append(f"Giao trễ hẹn {f.delivery_delay_days:.1f} ngày")
        if f.freight_ratio >= 0.25:
            ev.append(f"Phí ship chiếm {f.freight_ratio:.0%} giá trị hàng")
        if case.analytics:
            ev.extend(case.analytics.anomaly_flags)
        return ev

    def save(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"pipeline": self.pipeline, "classes": self.classes_}, path)

    def load(self, path: str | Path) -> "RootCauseAgent":
        blob = joblib.load(path)
        self.pipeline = blob["pipeline"]
        self.classes_ = blob["classes"]
        return self
