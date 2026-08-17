"""Chạy MAS-DSS end-to-end trên tập test và kết xuất intervention case.

Đây là bước Demonstration (mục 3.2.4 của luận văn).

Chạy: python -m mas_dss.pipelines.run_pipeline
"""

from __future__ import annotations

import argparse
import json

import joblib

from mas_dss.common.config import PROJECT_ROOT, load_config
from mas_dss.common.logging_utils import get_logger
from mas_dss.layer1_data_integration.feature_store import FeatureStore
from mas_dss.pipelines.mas_system import ABLATIONS, build_mas_system

log = get_logger("run_pipeline")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ablation", choices=list(ABLATIONS), default="full")
    ap.add_argument("--limit", type=int, default=None, help="giới hạn số case (debug)")
    args = ap.parse_args()

    cfg = load_config()
    store = FeatureStore(cfg)
    df = store.load_frame()

    test_ids = joblib.load(PROJECT_ROOT / cfg["paths"]["models"] / "test_order_ids.pkl")
    test_df = df[df["order_id"].isin(test_ids)]
    if args.limit:
        test_df = test_df.head(args.limit)
    cases = [store.row_to_case(r) for r in test_df.to_dict(orient="records")]
    log.info("chạy MAS-DSS (%s) trên %d order_case", args.ablation, len(cases))

    system = build_mas_system(cfg, disabled=ABLATIONS[args.ablation])
    system.run(cases)
    system.case_manager.save()

    latency = system.coordinator.latency_by_agent()
    out = PROJECT_ROOT / "reports/results/latency_by_agent.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(
            {
                "ablation": args.ablation,
                "n_cases": len(cases),
                "pipeline_total_ms": round(system.coordinator.pipeline_latency_ms, 2),
                "by_agent_ms": {k: round(v, 2) for k, v in latency.items()},
            },
            f,
            indent=2,
        )
    log.info("phân rã latency -> %s", out)


if __name__ == "__main__":
    main()
