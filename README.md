# MAS-DSS for E-Commerce Management

Prototype hiện thực hóa artifact của luận văn **"Thiết kế và đánh giá hệ thống hỗ trợ ra quyết định
dựa trên kiến trúc AI đa tác tử cho quản lý thương mại điện tử"** (Design Science Research, dữ liệu
Brazilian E-Commerce Public Dataset by Olist).

Hệ thống tổ chức theo chu trình **thu thập → phân tích → dự báo → giải thích nguyên nhân → đề xuất
hành động**, và được đánh giá định lượng so với hai baseline: **MIS truyền thống** (báo cáo mô tả)
và **mô hình học máy đơn lẻ** (single-model, không có agent orchestration).

## Kiến trúc 5 lớp

| Lớp | Thành phần | Module |
|---|---|---|
| 1. Data Integration | Ingestion Agent, Preprocessing Agent, Feature Store | `src/mas_dss/layer1_data_integration/` |
| 2. Orchestration | Coordinator Agent (routing, retry, timeout, tracing) | `src/mas_dss/layer2_orchestration/` |
| 3. Analytics & Intelligence | Analytics, Prediction, Root-Cause, Recommendation Agent | `src/mas_dss/layer3_analytics/` |
| 4. Decision Support | DSS Rule Engine, Explanation Agent, Case Management | `src/mas_dss/layer4_decision_support/` |
| 5. Presentation & Evaluation | Manager Dashboard, Logging & Evaluation | `src/mas_dss/layer5_presentation/` |

Đơn vị dữ liệu chảy xuyên suốt các lớp là **`OrderCase`** (`src/mas_dss/common/schemas.py`) — mỗi
agent chỉ làm giàu (enrich) object này, nên decision trace luôn tái lập được.

## Cài đặt

```bash
python -m venv .venv && .venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

Tải dataset Olist từ Kaggle và giải nén 9 file CSV vào `data/raw/`:
<https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce>

## Chạy

```bash
python -m mas_dss.pipelines.build_dataset      # L1: ingest → preprocess → feature store
python -m mas_dss.pipelines.train_models       # huấn luyện Prediction + Root-Cause model
python -m mas_dss.pipelines.run_pipeline       # L2-L4: chạy MAS-DSS end-to-end, sinh cases
python -m mas_dss.pipelines.run_evaluation     # L5: benchmark MAS-DSS vs MIS vs single-ML
streamlit run src/mas_dss/layer5_presentation/dashboard/app.py
```

## Ánh xạ sang luận văn

Xem [docs/thesis-mapping.md](docs/thesis-mapping.md) — mỗi chương/claim (criterion, causal, context)
được nối tới module và experiment tương ứng. Kiến trúc chi tiết: [docs/architecture.md](docs/architecture.md).
