# Dữ liệu train / val / test — hai mốc quyết định T₃ và T₄

Bản sao **byte-identical** (đã đối chiếu sha256 với `manifest.json` lúc commit) của các tệp đặc trưng
trong `data/v3/features/` — nguồn chuẩn mà `masdss.data.export.load_stage()` đọc. Thư mục này chỉ để
chia sẻ dữ liệu qua git; **mã nguồn không đọc từ đây**.

## Cấu trúc

| Thư mục | Nội dung | Tổng thể |
|---|---|---|
| `T3/` | Đặc trưng mốc **T₃ = ngày mua + 7** (dự báo) — 17 cột, KHÔNG chứa cột kết cục T₄ | CHỈ đơn còn kịp can thiệp (`reachable_at_t3`) |
| `T4/` | Đặc trưng mốc **T₄ = khi đánh giá đã về** (quy kết) — 23 cột, gồm kết cục giao hàng + văn bản đánh giá | Đầy đủ, không lọc |
| `labels/` | Nhãn + cột thời gian (`y_*.parquet`, 9 cột, gồm `is_dissatisfied`, `reachable_at_t3`) — dùng chung cho cả hai mốc | Đầy đủ |
| `manifest.json` | Số dòng, số cột, sha256 từng tệp; định nghĩa mốc; khoảng cách ly; seed 20260809 | |

`T3/t3_design_*.parquet` là **ảnh chụp ma trận thiết kế** — đúng ma trận đã đi vào
`LGBMClassifier.fit()` và bước hiệu chuẩn isotonic (16 cột, không có `order_id` trong dữ liệu vào).

## Kích thước các tập

| Tập | T₃ (đơn) | T₄ (đơn) | Kỳ mua hàng |
|---|---|---|---|
| train | 52.835 | 63.986 | 09/2016 → 22/03/2018 |
| val | 9.077 | 13.383 | 22/03/2018 → 29/05/2018 |
| test | 11.322 | 18.952 | 31/05/2018 → 10/2018 |

Chia theo **thời gian** (không ngẫu nhiên), có khoảng cách ly tại mốc `2018-05-31 16:39:30` —
xem `khoang_cach_ly` trong `manifest.json`.

## Tái lập

```bash
python -m masdss.cli.export_features   # sinh lại data/v3/features/ từ data/raw/
```

Đường vào duy nhất cho mô hình là `masdss.data.export.load_stage(stage, split)` —
đọc `data/v3/features/`, KHÔNG đọc thư mục này. Nếu cần nạp trực tiếp từ đây:
`load_stage("t3", "train", base=Path("data/splits/T3"))` sẽ **không** chạy vì layout ở đây
tách theo giai đoạn; hãy copy ngược về một thư mục phẳng kèm `manifest.json` hoặc dùng
`pd.read_parquet` trực tiếp.
