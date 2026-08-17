# Kiến trúc MAS-DSS *(bản v1 — LỖI THỜI)*

> ## ⛔ TÀI LIỆU LỖI THỜI — KHÔNG SỬ DỤNG, KHÔNG TRÍCH DẪN, KHÔNG CÀI ĐẶT THEO
>
> Tài liệu này mô tả kiến trúc **năm tầng của codebase `src/mas_dss/` đã đóng băng**. Nó **không mô tả
> hệ thống đang chạy** (`src-v3/masdss/`) và mâu thuẫn với mã nguồn ở gần như mọi điểm.
>
> **Nguồn chuẩn thay thế:**
>
> | Cần gì | Đọc ở đâu |
> |---|---|
> | Kiến trúc, phân tầng, năm giao diện, danh sách tác tử | [technical-plan-v3.md](technical-plan-v3.md) §3, §4, §5, §A.2 |
> | Trình bày cho luận văn: 10 tác tử, giao thức, bề mặt hỏng | [thesis/ch4-thiet-ke-hien-thuc.md](thesis/ch4-thiet-ke-hien-thuc.md) §4.2–4.4 |
> | Ràng buộc dữ liệu, hai mốc quyết định, hệ phân loại nguyên nhân | [thesis/ch3-phuong-phap.md](thesis/ch3-phuong-phap.md) |
>
> **Năm điểm sai nếu đọc file này như tài liệu hiện hành:**
>
> | Bản này nói | Thực tế `src-v3/` |
> |---|---|
> | Năm tầng: Ingestion → Orchestration → Analytics → Decision → Presentation | Tám tầng phụ thuộc một chiều: `data` → `core` → `runtime` → `capabilities` → `agents` → `system`/`baselines` → `evaluation`/`chaos` → `cli` |
> | Mọi agent nhận và trả `list[OrderCase]` | Mọi tác tử nhận và trả **`Message`**; trạng thái case nằm ở `Blackboard`, và **nhật ký message là nguồn sự thật** |
> | Có Ingestion Agent, Preprocessing, Feature Store, Streamlit dashboard | Không có tác tử nào trong số đó. Dashboard **cố ý không xây** — không câu hỏi nghiên cứu nào đo giao diện |
> | `review_score <= 3` = không hài lòng | Ngưỡng đã chốt là **1–2★**; độ nhạy `≤2` so với `≤3` là một phân tích riêng ở Chương 5 |
> | Root Cause Agent đơn lẻ, weak label bằng từ khóa | **Ba analyst chuyên biệt** đấu thầu qua Contract Net hai pha; weak label chỉ dùng để pre-train, đánh giá **chỉ trên gold set** |
>
> Giữ file này **chỉ làm hồ sơ lịch sử thiết kế**, song song với
> [technical-design-v2.md](technical-design-v2.md) và [mas-redesign-plan.md](mas-redesign-plan.md).

## Luồng dữ liệu

```
Olist CSV (9 bảng)
      │
      ▼  ┌──────────────────────── LAYER 1: DATA INTEGRATION ───────────────────────┐
      └─▶│ 1.1 Ingestion Agent    validate schema, null, duplicate                  │
         │ 1.2 Preprocessing      join 7 bảng → 1 dòng/đơn; sinh delay, freight     │
         │                        ratio, review lag…                                │
         │ 1.3 Feature Store      order_cases.parquet (curated ODS)                 │
         └────────────────────────────────┬────────────────────────────────────────┘
                                          │ list[OrderCase]
         ┌──────────────────── LAYER 2: ORCHESTRATION ─────────────────────────────┐
         │ 2.1 Coordinator  mini-batch → route → retry/timeout → trace latency     │
         └────────────────────────────────┬────────────────────────────────────────┘
                                          │
         ┌────────────── LAYER 3: ANALYTICS & INTELLIGENCE ────────────────────────┐
         │ 3.1 Analytics       → OrderCase.analytics   (anomaly flags, seller/cat)  │
         │ 3.2 Prediction      → OrderCase.prediction  (risk_score, risk_level)     │
         │ 3.3 Root Cause      → OrderCase.root_cause  (cause_label, probability)   │
         │ 3.4 Recommendation  → OrderCase.candidates  (action candidates + score)  │
         └────────────────────────────────┬────────────────────────────────────────┘
                                          │
         ┌────────────────── LAYER 4: DECISION SUPPORT ────────────────────────────┐
         │ 4.1 DSS Rule Engine → OrderCase.decision (actions, severity, escalation) │
         │ 4.2 Explanation     → OrderCase.trace    (features→pred→cause→action)    │
         │ 4.3 Case Manager    → intervention_cases.csv (monitor/urgent/resolved)   │
         └────────────────────────────────┬────────────────────────────────────────┘
                                          │
         ┌──────────── LAYER 5: PRESENTATION & EVALUATION ─────────────────────────┐
         │ 5.1 Manager Dashboard (Streamlit)                                        │
         │ 5.2 Evaluation: MAS-DSS vs MIS vs single-ML + ablation                   │
         └─────────────────────────────────────────────────────────────────────────┘
```

## Nguyên tắc thiết kế

**Một contract duy nhất.** Mọi agent nhận `list[OrderCase]` và trả `list[OrderCase]`, chỉ *thêm*
chứ không ghi đè khối của agent khác. Nhờ vậy Coordinator có thể route/retry/đo latency mà không
cần biết agent làm gì, và decision trace luôn tái lập được từ chính object đó.

**Tách "AI đề xuất" khỏi "doanh nghiệp quyết định".** Recommendation Agent (3.4) chỉ sinh *ứng viên*
có chấm điểm; quyền chốt thuộc DSS Rule Engine (4.1) nơi chính sách kinh doanh nằm trong YAML.
Đổi chính sách không phải huấn luyện lại mô hình.

**Ablation là công dân hạng nhất.** `CoordinatorAgent(disabled_agents=[...])` cho phép tắt từng
agent để đo mức suy giảm — đây là hạ tầng cho causal claims, không phải code thí nghiệm ăn theo.

**Không rò rỉ nhãn.** Analytics Agent học thống kê seller/category từ *tập train* rồi chỉ tra cứu khi
chạy; split train/test theo thời gian mua hàng, không random.

## Các quyết định cần biện luận trong luận văn

| Quyết định | Lý do | Rủi ro cần nêu ở Threats to validity |
|---|---|---|
| `review_score <= 3` = không hài lòng | Điểm 3 trong Olist đã đi kèm khiếu nại rõ rệt | Ngưỡng khác cho kết quả khác — nên báo cáo độ nhạy |
| Nhãn nguyên nhân bằng weak supervision (từ khóa review) | Olist không có nhãn nguyên nhân sẵn | Nhãn giả có nhiễu; nên có một mẫu được gán tay để kiểm định |
| Gộp đơn nhiều item về item đắt nhất | Item chi phối trải nghiệm & khiếu nại | Mất thông tin ở đơn hỗn hợp nhiều seller |
| Chỉ giữ đơn `delivered` | Nhãn hài lòng chỉ có nghĩa sau khi nhận hàng | Bỏ qua đơn hủy — vốn cũng là một dạng bất mãn |
