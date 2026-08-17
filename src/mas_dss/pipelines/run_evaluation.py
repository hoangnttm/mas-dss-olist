"""Thí nghiệm trung tâm: MAS-DSS vs MIS vs single-ML, cộng các biến thể ablation.

Sinh ra `reports/results/benchmark.{json,md}` — bảng số liệu để đưa thẳng vào Chương 5.

* criterion validity  -> so sánh MAS-DSS với hai baseline trên cùng tập test.
* causal validity     -> các dòng ablation (tắt Root-Cause / Recommendation / Analytics).
* context validity    -> phân tích theo lát cắt (category, bang) trong dashboard.

Chạy: python -m mas_dss.pipelines.run_evaluation
"""

from __future__ import annotations

import json
import time

import joblib

from mas_dss.common.config import PROJECT_ROOT, load_config
from mas_dss.common.logging_utils import get_logger
from mas_dss.common.schemas import RiskLevel
from mas_dss.layer1_data_integration.feature_store import FeatureStore
from mas_dss.layer5_presentation.evaluation.baselines import MISBaseline, SingleModelBaseline
from mas_dss.layer5_presentation.evaluation.metrics import (
    classification_metrics,
    decision_pipeline_quality,
    intervention_metrics,
    latency_metrics,
    summarize,
    to_markdown_table,
)
from mas_dss.pipelines.mas_system import ABLATIONS, build_mas_system
from mas_dss.pipelines.train_models import temporal_split

log = get_logger("run_evaluation")


def evaluate_mas(cfg, store, test_df, ablation: str) -> dict:
    cases = [store.row_to_case(r) for r in test_df.to_dict(orient="records")]
    system = build_mas_system(cfg, disabled=ABLATIONS[ablation])

    t0 = time.perf_counter()
    cases = system.run(cases)
    elapsed = (time.perf_counter() - t0) * 1000

    y_true = [c.is_dissatisfied for c in cases]
    y_score = [c.prediction.risk_score if c.prediction else 0.0 for c in cases]
    y_pred = [
        int(c.prediction.risk_level != RiskLevel.LOW) if c.prediction else 0 for c in cases
    ]

    name = "mas_dss" if ablation == "full" else f"mas_dss[-{ablation}]"
    return summarize(
        name,
        [
            classification_metrics(y_true, y_pred, y_score),
            intervention_metrics(cases),
            decision_pipeline_quality(cases),
            latency_metrics(elapsed, len(cases)),
            {"produces_actions": True},
        ],
    )


def evaluate_baselines(cfg, train_df, test_df) -> list[dict]:
    y_true = test_df["is_dissatisfied"].tolist()
    rows = []

    mis = MISBaseline(cfg)
    y_pred = mis.flag(test_df)
    rows.append(
        summarize(
            "mis",
            [
                classification_metrics(y_true, y_pred, mis.score(test_df)),
                latency_metrics(mis.latency_ms, len(test_df)),
                # MIS chỉ hiển thị số liệu — không có nguyên nhân, không có hành động.
                {
                    "detection_rate": round(
                        float(((y_pred == 1) & (test_df["is_dissatisfied"] == 1)).sum())
                        / max(int(test_df["is_dissatisfied"].sum()), 1),
                        4,
                    ),
                    "pipeline_completeness": 0.0,
                    "action_cause_fit": 0.0,
                    "produces_actions": False,
                },
            ],
        )
    )

    single = SingleModelBaseline(cfg).fit(train_df)
    scores = single.score(test_df)
    preds = (scores >= cfg["prediction"]["risk_bands"]["low"]).astype(int)
    rows.append(
        summarize(
            "single_model",
            [
                classification_metrics(y_true, preds, scores),
                latency_metrics(single.latency_ms, len(test_df)),
                {
                    "detection_rate": round(
                        float(((preds == 1) & (test_df["is_dissatisfied"] == 1)).sum())
                        / max(int(test_df["is_dissatisfied"].sum()), 1),
                        4,
                    ),
                    "pipeline_completeness": 0.0,   # không phân loại nguyên nhân
                    "action_cause_fit": 0.0,        # không sinh hành động
                    "produces_actions": False,
                },
            ],
        )
    )
    return rows


def main() -> None:
    cfg = load_config()
    store = FeatureStore(cfg)
    df = store.load_frame()
    train_df, _ = temporal_split(df, cfg["prediction"]["test_size"])

    test_ids = joblib.load(PROJECT_ROOT / cfg["paths"]["models"] / "test_order_ids.pkl")
    test_df = df[df["order_id"].isin(test_ids)].reset_index(drop=True)
    log.info("đánh giá trên %d đơn test", len(test_df))

    rows = [evaluate_mas(cfg, store, test_df, "full")]
    rows += evaluate_baselines(cfg, train_df, test_df)
    for ablation in cfg["evaluation"]["ablations"]:
        log.info("ablation: %s", ablation)
        rows.append(evaluate_mas(cfg, store, test_df, ablation))

    out_dir = PROJECT_ROOT / "reports/results"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "benchmark.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    key_cols = [
        "system",
        "accuracy",
        "macro_f1",
        "recall",
        "roc_auc",
        "detection_rate",
        "pipeline_completeness",
        "action_cause_fit",
        "latency_per_case_ms",
        "throughput_cases_per_s",
    ]
    table = to_markdown_table([{k: r.get(k, "—") for k in key_cols} for r in rows])
    with open(out_dir / "benchmark.md", "w", encoding="utf-8") as f:
        f.write("# Kết quả benchmark MAS-DSS\n\n" + table + "\n")

    print("\n" + table + "\n")
    log.info("kết quả -> %s", out_dir / "benchmark.md")


if __name__ == "__main__":
    main()
