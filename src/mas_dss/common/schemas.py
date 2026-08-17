"""Contract dữ liệu giữa các agent.

`OrderCase` là đơn vị nghiệp vụ chảy xuyên suốt 5 lớp: Layer 1 tạo ra nó, các agent ở
Layer 3 làm giàu thêm từng khối (analytics -> prediction -> root_cause -> recommendation),
Layer 4 đọc toàn bộ để sinh quyết định và decision trace. Vì mọi agent chỉ *thêm* chứ
không ghi đè, trace luôn tái lập được: features -> prediction -> cause -> action.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CauseLabel(str, Enum):
    DELIVERY = "delivery"
    PRODUCT_QUALITY = "product_quality"
    CUSTOMER_SERVICE = "customer_service"
    PRICE = "price"
    UNKNOWN = "unknown"


class Severity(str, Enum):
    NONE = "none"
    MONITOR = "monitor"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class CaseStatus(str, Enum):
    MONITOR = "monitor"
    URGENT = "urgent"
    RESOLVED = "resolved"


class OrderFeatures(BaseModel):
    """Đặc trưng dẫn xuất do Preprocessing Agent (1.2) tạo ra."""

    price: float = 0.0
    freight_value: float = 0.0
    freight_ratio: float = 0.0
    payment_value: float = 0.0
    payment_installments: int = 0
    n_items: int = 0
    n_sellers: int = 0
    product_category: str = "unknown"
    product_weight_g: float = 0.0
    product_photos_qty: int = 0
    description_length: int = 0
    delivery_days: float = 0.0          # purchase -> delivered
    estimated_delivery_days: float = 0.0
    delivery_delay_days: float = 0.0    # actual - estimated; dương = trễ hẹn
    approval_lag_hours: float = 0.0
    carrier_handover_days: float = 0.0
    review_lag_days: float = 0.0        # delivered -> review created
    customer_state: str = "unknown"
    seller_state: str = "unknown"
    same_state: int = 0


class AnalyticsContext(BaseModel):
    """Chỉ báo ngữ cảnh do Analytics Agent (3.1) bổ sung."""

    is_late: bool = False
    is_slow_shipping: bool = False
    is_high_freight: bool = False
    seller_late_rate: float = 0.0
    seller_avg_review: float = 0.0
    category_complaint_rate: float = 0.0
    anomaly_flags: list[str] = Field(default_factory=list)


class Prediction(BaseModel):
    """Đầu ra Prediction Agent (3.2)."""

    predicted_score: float = 0.0        # review score dự báo (1-5)
    risk_score: float = 0.0             # P(không hài lòng)
    risk_level: RiskLevel = RiskLevel.LOW
    confidence: float = 0.0
    model_name: str = ""


class RootCause(BaseModel):
    """Đầu ra Root Cause Analysis Agent (3.3)."""

    cause_label: CauseLabel = CauseLabel.UNKNOWN
    cause_probability: float = 0.0
    cause_distribution: dict[str, float] = Field(default_factory=dict)
    evidence: list[str] = Field(default_factory=list)


class ActionCandidate(BaseModel):
    """Đề xuất thô từ Recommendation Agent (3.4), trước khi qua Rule Engine."""

    action: str
    severity: Severity = Severity.NONE
    score: float = 0.0
    source: str = "recommendation_agent"


class Decision(BaseModel):
    """Quyết định cuối cùng do DSS Rule Engine (4.1) chốt."""

    matched_rules: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    severity: Severity = Severity.NONE
    escalate_to: str = "none"
    case_status: CaseStatus = CaseStatus.MONITOR


class DecisionTrace(BaseModel):
    """Vết suy luận do Explanation Agent (4.2) sinh ra: vì sao có khuyến nghị này."""

    steps: list[dict[str, Any]] = Field(default_factory=list)
    narrative: str = ""


class OrderCase(BaseModel):
    """Bản ghi nghiệp vụ chuẩn hóa — đơn vị xử lý của toàn hệ thống."""

    order_id: str
    customer_id: str = ""
    seller_id: str = ""
    order_purchase_ts: datetime | None = None
    order_delivered_ts: datetime | None = None
    order_estimated_delivery_ts: datetime | None = None

    features: OrderFeatures = Field(default_factory=OrderFeatures)
    analytics: AnalyticsContext | None = None
    prediction: Prediction | None = None
    root_cause: RootCause | None = None
    candidates: list[ActionCandidate] = Field(default_factory=list)
    decision: Decision | None = None
    trace: DecisionTrace | None = None

    # Nhãn thực tế — chỉ dùng để đánh giá (Layer 5), agent không được đọc.
    review_score: int | None = None
    is_dissatisfied: int | None = None

    def rule_namespace(self) -> dict[str, Any]:
        """Namespace phẳng để Rule Engine đánh giá biểu thức `when`."""
        ns: dict[str, Any] = self.features.model_dump()
        if self.analytics:
            ns.update(self.analytics.model_dump())
        if self.prediction:
            p = self.prediction.model_dump()
            p["risk_level"] = self.prediction.risk_level.value
            ns.update(p)
        if self.root_cause:
            c = self.root_cause.model_dump()
            c["cause_label"] = self.root_cause.cause_label.value
            ns.update(c)
        ns["order_id"] = self.order_id
        return ns


class AgentResult(BaseModel):
    """Kết quả một lần chạy agent — Coordinator dùng để log latency và retry."""

    agent: str
    ok: bool = True
    latency_ms: float = 0.0
    error: str | None = None
    n_cases: int = 0
