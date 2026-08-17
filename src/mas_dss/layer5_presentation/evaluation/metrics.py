"""5.2 Logging & Evaluation — bộ chỉ số.

Ba nhóm chỉ số, tương ứng ba nhóm claim trong khung Validity in Design Science:

* Chất lượng dự báo — accuracy, macro F1, precision, recall, ROC-AUC.
* Hiệu năng vận hành — latency end-to-end, throughput, phân rã latency theo agent.
* Chất lượng chuỗi quyết định — tỷ lệ đơn rủi ro thực sự nhận được hành động đúng
  (`decision_pipeline_quality`). Chỉ số này là thứ MIS và single-model *không thể* đạt,
  vì chúng không sinh ra hành động — nên nó là bằng chứng chính cho criterion claim.
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from mas_dss.common.schemas import CauseLabel, OrderCase, Severity

# Hành động nào được coi là "đúng loại" cho từng nguyên nhân — dùng để chấm chất lượng
# chuỗi phát hiện → phân loại → đề xuất.
CAUSE_ACTION_FIT: dict[str, set[str]] = {
    "delivery": {
        "expedite_shipment_and_notify_customer",
        "proactive_delay_apology_and_tracking_update",
        "audit_seller_fulfillment_sla",
    },
    "product_quality": {
        "inspect_seller_and_flag_product_listing",
        "offer_return_or_replacement",
    },
    "customer_service": {
        "open_support_ticket_and_contact_customer",
        "assign_case_to_customer_service_review",
    },
    "price": {
        "review_freight_pricing_and_offer_voucher",
        "compensate_customer_with_discount",
    },
}


def classification_metrics(
    y_true: Sequence[int], y_pred: Sequence[int], y_score: Sequence[float] | None = None
) -> dict[str, float]:
    m = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
    }
    if y_score is not None and len(set(y_true)) > 1:
        m["roc_auc"] = float(roc_auc_score(y_true, y_score))
    return m


def latency_metrics(total_ms: float, n_cases: int) -> dict[str, float]:
    return {
        "latency_total_ms": round(total_ms, 2),
        "latency_per_case_ms": round(total_ms / max(n_cases, 1), 4),
        "throughput_cases_per_s": round(n_cases / max(total_ms / 1000, 1e-9), 1),
    }


def intervention_metrics(cases: Sequence[OrderCase]) -> dict[str, float]:
    """Khả năng phát hiện case cần can thiệp: hệ có tạo case cho đúng đơn bất mãn không."""
    y_true = [c.is_dissatisfied for c in cases]
    y_pred = [
        int(bool(c.decision and c.decision.severity not in (Severity.NONE, Severity.MONITOR)))
        for c in cases
    ]
    m = classification_metrics(y_true, y_pred)
    return {f"intervention_{k}": v for k, v in m.items()}


def decision_pipeline_quality(cases: Sequence[OrderCase]) -> dict[str, float]:
    """Chất lượng chuỗi phát hiện → phân loại → đề xuất, chỉ tính trên đơn bất mãn thật.

    Một case được coi là *xử lý trọn vẹn* khi: (1) hệ thống có gắn cờ can thiệp,
    (2) có gán nguyên nhân với độ tin cậy đủ, (3) hành động đề xuất khớp nhóm nguyên nhân.
    """
    truly_bad = [c for c in cases if c.is_dissatisfied == 1]
    if not truly_bad:
        return {"pipeline_completeness": 0.0, "action_cause_fit": 0.0, "n_dissatisfied": 0}

    detected = 0
    complete = 0
    fit = 0
    for c in truly_bad:
        flagged = bool(
            c.decision and c.decision.severity not in (Severity.NONE, Severity.MONITOR)
        )
        if not flagged:
            continue
        detected += 1

        cause = c.root_cause.cause_label if c.root_cause else CauseLabel.UNKNOWN
        actions = set(c.decision.actions) if c.decision else set()
        if cause != CauseLabel.UNKNOWN and actions:
            complete += 1
            if actions & CAUSE_ACTION_FIT.get(cause.value, set()):
                fit += 1

    n = len(truly_bad)
    return {
        "n_dissatisfied": n,
        "detection_rate": round(detected / n, 4),
        "pipeline_completeness": round(complete / n, 4),
        "action_cause_fit": round(fit / max(detected, 1), 4),
    }


def summarize(name: str, blocks: Sequence[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {"system": name}
    for b in blocks:
        out.update(b)
    return out


def to_markdown_table(rows: Sequence[dict[str, Any]]) -> str:
    """Bảng so sánh sẵn để dán vào Chương 5."""
    if not rows:
        return ""
    cols = list(dict.fromkeys(k for r in rows for k in r))
    head = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    body = [
        "| "
        + " | ".join(
            f"{r[c]:.4f}" if isinstance(r.get(c), float) else str(r.get(c, "—"))
            for c in cols
        )
        + " |"
        for r in rows
    ]
    return "\n".join([head, sep, *body])
