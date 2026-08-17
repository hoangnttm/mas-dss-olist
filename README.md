# MAS-DSS for E-Commerce Management

Prototype hiện thực hóa artifact của luận văn **"Thiết kế và đánh giá hệ thống hỗ trợ ra quyết định
dựa trên kiến trúc AI đa tác tử cho quản lý thương mại điện tử"** (Design Science Research, dữ liệu
Brazilian E-Commerce Public Dataset by Olist).

Hệ thống ra quyết định tại **hai mốc thời gian**:

- **T₃ = ngày mua + 7 ngày** — *dự báo* rủi ro bất mãn khi còn kịp can thiệp (coupon, callback, ticket);
- **T₄ = khi đánh giá đã về** — *quy kết* nguyên nhân bất mãn (delivery / quality / service / price)
  từ văn bản đánh giá.

Kiến trúc đa tác tử (MAS) gồm orchestrator tự viết, Contract Net hai pha có ngân sách, tầng chịu lỗi
(circuit breaker, output guard, thang suy giảm), và được so sánh định lượng với baseline **đơn khối**
(monolithic, cùng năng lực nền nhưng không có phối hợp đa tác tử).

## Cấu trúc repository

| Đường dẫn | Vai trò |
| --- | --- |
| `src-v3/masdss/` | **Codebase v3 — đang hiệu lực.** Toàn bộ thực nghiệm chạy từ đây |
| `tests-v3/` | Bộ test của v3 (~303 test, chạy hết ~67 giây) |
| `src/mas_dss/` | Codebase v1 — **đóng băng**, giữ làm hồ sơ, không sửa |
| `tests/` | Test của v1 |
| `data/splits/` | **Dữ liệu train/val/test đã xuất sẵn** cho T₃, T₄ (kèm sha256 trong `manifest.json`) |
| `config/v3/rules.yaml` | Danh mục luật của rule engine |
| `pyproject.toml` | Khai báo package `mas_dss` (v1) và `masdss` (v3) |

## Yêu cầu

- Python **≥ 3.10**
- Không cần GPU. `torch`/BERTimbau là tùy chọn (xem chú thích trong `requirements.txt`), mặc định
  hệ thống dùng `TfidfCauseHead` — không cần cài.
- Khoảng 2 GB dung lượng trống nếu tái lập từ dữ liệu gốc Kaggle.

## 1. Cài đặt

```bash
git clone https://github.com/hoangnttm/mas-dss-olist.git
cd mas-dss-olist

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

pip install -r requirements.txt
pip install -e .                # đăng ký package masdss (v3) và mas_dss (v1)
```

## 2. Chuẩn bị dữ liệu — chọn một trong hai phương án

Mọi mô hình chỉ đọc qua **một đường vào duy nhất** `masdss.data.export.load_stage()`, nạp từ thư mục
phẳng `data/v3/features/`. Repo không chứa thư mục đó (gitignore) nhưng chứa bản sao đã kiểm checksum
ở `data/splits/`.

### Phương án A — dùng dữ liệu có sẵn trong repo (nhanh, khuyến nghị)

Copy các tệp trong `data/splits/` về lại layout phẳng mà pipeline yêu cầu:

```bash
# Linux / macOS
mkdir -p data/v3/features
cp data/splits/T3/*.parquet data/splits/T4/*.parquet data/splits/labels/*.parquet \
   data/splits/manifest.json data/splits/goldset_pool.parquet data/v3/features/
```

```powershell
# Windows PowerShell
New-Item -ItemType Directory -Force data\v3\features | Out-Null
Copy-Item data\splits\T3\*.parquet, data\splits\T4\*.parquet, data\splits\labels\*.parquet, `
          data\splits\manifest.json, data\splits\goldset_pool.parquet data\v3\features\
```

Chi tiết từng tệp (số dòng, số cột, sha256, khoảng cách ly, seed): xem
[data/splits/README.md](data/splits/README.md) và [data/splits/manifest.json](data/splits/manifest.json).

### Phương án B — tái lập từ dữ liệu gốc Kaggle

1. Tải **Brazilian E-Commerce Public Dataset by Olist**:
   <https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce>
2. Giải nén **9 file CSV** vào `data/raw/`.
3. Sinh tệp đặc trưng:

```bash
python -m masdss.cli.export_features
```

Lệnh này ghi `data/v3/features/` kèm `manifest.json` có sha256 từng tệp. Đối chiếu với
`data/splits/manifest.json` trong repo để xác nhận tái lập đúng từng byte (seed cố định `20260809`).

## 3. Chạy thực nghiệm chính

Chuỗi tái lập đầy đủ gồm ba bước, chạy theo đúng thứ tự:

```bash
# (1) Huấn luyện capability: mô hình rủi ro LightGBM + hiệu chuẩn isotonic + báo cáo
python -m masdss.cli.train                    # ghi models/v3/risk_model.joblib

# (2) Chạy hệ thống MAS + baseline đơn khối trên 300 đơn bất mãn (giai đoạn 2 = T4)
python -m masdss.cli.run_system --stage 2 --n 300       # ghi data/v3/runs/stage2/

# (3) Tính toàn bộ chỉ số đánh giá (bootstrap 1000 lượt)
python -m masdss.cli.run_evaluation --run data/v3/runs/stage2   # ghi data/v3/evaluation/*.csv
```

Đầu ra chính:

- `data/v3/runs/stage2/decisions.jsonl` — vết quyết định từng đơn của MAS (tái lập được từng byte);
- `data/v3/runs/stage2/baselines.jsonl` — kết quả baseline trên cùng tập đơn;
- `data/v3/evaluation/*.csv` — dự báo (PR-AUC, hiệu chuẩn), phối hợp, chi phí, luật hành động,
  selective prediction.

### Kiểm tính tất định (Gate G5)

Toàn bộ codebase cấm `uuid4()` và đồng hồ hệ thống trong logic nghiệp vụ; hai lần chạy cùng cấu hình
phải cho `decisions.jsonl` trùng sha256:

```bash
python -m masdss.cli.run_system --stage 2 --n 300 --out data/v3/runs/rep1
python -m masdss.cli.run_system --stage 2 --n 300 --out data/v3/runs/rep2
# So sánh:
#   Linux/macOS : sha256sum  data/v3/runs/rep{1,2}/decisions.jsonl
#   PowerShell  : Get-FileHash data\v3\runs\rep1\decisions.jsonl, data\v3\runs\rep2\decisions.jsonl
```

## 4. Thực nghiệm mở rộng

```bash
# Tiêm lỗi đơn lẻ — cú pháp kind:component[:field]
# kind ∈ {crash, transient, constant, bias} · component ∈ {prediction, cause_delivery,
#   cause_price, cause_quality, cause_service, analytics, recommendation, critic,
#   arbiter, rules, case_manager}
python -m masdss.cli.run_system --stage 2 --n 300 --inject crash:prediction
python -m masdss.cli.run_system --stage 2 --n 300 --inject bias:cause_delivery:confidence

# Ablation cho RQ1: tắt tầng chịu lỗi
python -m masdss.cli.run_system --stage 2 --n 300 --no-reliability

# Bộ chaos đầy đủ: 5 nhóm lỗi × 3 mức, chạy cả MAS lẫn đơn khối
python -m masdss.cli.run_chaos                # ghi data/v3/chaos/
```

**Quy kết nguyên nhân trên gold set** (`python -m masdss.cli.run_attribution`) cần các tệp nhãn do
con người gán trong `data/v3/goldset/` — **không kèm trong repo** vì chứa vòng gán nhãn thủ công.
Các thực nghiệm còn lại không phụ thuộc gold set.

## 5. Kiểm thử

```bash
python -m pytest -q        # ~303 test, ~67 giây
```

Bộ test bao phủ các bất biến quan trọng: lược đồ dữ liệu (tệp T₃ không được chứa cột kết cục T₄),
chống rò rỉ nhãn, tính tất định end-to-end, bất biến Decision (property-based với Hypothesis),
Contract Net, tầng chịu lỗi, và chặn đường nạp dữ liệu cũ (`test_data_entrypoint.py`).

## 6. Codebase v1 (đóng băng)

`src/mas_dss/` là bản 5 tầng ban đầu, giữ nguyên làm hồ sơ so sánh. Các lệnh của nó vẫn chạy được
nhưng **không phải** đối tượng đánh giá hiện hành:

```bash
python -m mas_dss.pipelines.build_dataset
python -m mas_dss.pipelines.train_models
python -m mas_dss.pipelines.run_pipeline
python -m mas_dss.pipelines.run_evaluation
streamlit run src/mas_dss/layer5_presentation/dashboard/app.py
```

## Ghi chú tái lập

- Seed toàn cục **20260809** (`src-v3/masdss/config.py`), gán qua `CONFIG.seed_everything()`.
- Mọi UUID sinh bằng `uuid5` trên namespace cố định — `uuid4()` bị cấm trong toàn codebase.
- Mọi mốc thời gian lấy từ dữ liệu, không từ đồng hồ hệ thống.
- Chia tập theo **thời gian mua hàng** (không ngẫu nhiên), có khoảng cách ly tại
  `2018-05-31 16:39:30` giữa val và test — chi tiết trong `data/splits/manifest.json`.
