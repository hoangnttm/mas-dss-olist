"""Layer 1 end-to-end: ingest -> preprocess -> feature store.

Chạy: python -m mas_dss.pipelines.build_dataset
"""

from __future__ import annotations

import json

from mas_dss.common.config import PROJECT_ROOT, load_config
from mas_dss.common.logging_utils import get_logger
from mas_dss.layer1_data_integration.feature_store import FeatureStore
from mas_dss.layer1_data_integration.ingestion_agent import DataIngestionAgent
from mas_dss.layer1_data_integration.preprocessing_agent import DataPreprocessingAgent

log = get_logger("build_dataset")


def main() -> None:
    cfg = load_config()

    ingestion = DataIngestionAgent(cfg)
    tables = ingestion.load_all()

    preprocessing = DataPreprocessingAgent(cfg)
    order_cases = preprocessing.build_order_cases(tables)

    store = FeatureStore(cfg)
    store.save(order_cases)

    dq_path = PROJECT_ROOT / "reports/results/data_quality_report.json"
    dq_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dq_path, "w", encoding="utf-8") as f:
        json.dump(dict(ingestion.report), f, indent=2, ensure_ascii=False)
    log.info("báo cáo chất lượng dữ liệu -> %s", dq_path)


if __name__ == "__main__":
    main()
