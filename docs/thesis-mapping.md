# Ánh xạ luận văn ↔ mã nguồn

> ## ❌ **LỖI THỜI — đừng trích, đừng đồng bộ số hiệu**
>
> File này ánh xạ **đề cương gốc 5 câu hỏi** *(RQ1 kiến trúc · RQ2 phối hợp · RQ3 tốt hơn MIS ·
> RQ4 bối cảnh)* vào **`src/mas_dss/` — codebase v1 đã đóng băng**. Cả hai đầu của phép ánh xạ đều
> không còn hiệu lực:
>
> - Câu hỏi nghiên cứu nay còn **ba**, đánh số khác hẳn → [research-questions-objectives.md](research-questions-objectives.md)
> - Mã nguồn đang hoạt động là **`src-v3/`** → [technical-plan-v3.md](technical-plan-v3.md)
>
> Số hiệu RQ ở đây **cố ý giữ nguyên** vì chúng thuộc một sơ đồ đánh số khác. Đổi chúng theo bảng
> hoán vị 12/08 sẽ tạo ra một ánh xạ sai mà không ai phát hiện được.

## Theo chương

| Chương / mục | Nội dung | Nơi hiện thực |
|---|---|---|
| 2.2 Kiến trúc MAS | 5 tác tử chính | [docs/architecture.md](architecture.md), `src/mas_dss/layer2..4/` |
| 3.2.3 Thiết kế & phát triển | Prototype đầy đủ | toàn bộ `src/mas_dss/` |
| 3.2.4 Demonstration | Chạy end-to-end trên Olist | `pipelines/run_pipeline.py` → `reports/results/intervention_cases.csv` |
| 3.2.5a Criterion validity | So sánh với MIS & single-ML | `pipelines/run_evaluation.py`, `layer5.../baselines.py` |
| 3.2.5b Causal validity | Ablation từng agent | `CoordinatorAgent(disabled_agents=...)`, `ABLATIONS` trong `pipelines/mas_system.py` |
| 3.2.5c Context validity | Lát cắt theo category / bang | tab "MAS-DSS vs MIS" + KPI trong dashboard |
| 3.3 Thiết kế kiến trúc | Vào/ra từng agent | `common/schemas.py` (`OrderCase`) |
| Ch. 4 Phương pháp đánh giá | Bộ chỉ số | `layer5_presentation/evaluation/metrics.py` |
| Ch. 5 Kết quả thực nghiệm | Bảng số liệu | `reports/results/benchmark.md` (sinh tự động, dán thẳng vào chương) |

## Theo câu hỏi nghiên cứu

**RQ1 — Kiến trúc MAS cần thiết kế thế nào?**
Trả lời bằng artifact: kiến trúc 5 lớp + contract `OrderCase` + Coordinator có retry/timeout/trace.
Bằng chứng vận hành: `reports/results/latency_by_agent.json`.

**RQ2 — Phân công và phối hợp các tác tử ra sao?**
Bốn agent Layer 3 nối tiếp nhau làm giàu cùng một `OrderCase`; Layer 4 chốt quyết định. Bằng chứng
phối hợp hiệu quả: `pipeline_completeness` và `action_cause_fit` trong `metrics.py` — đo tỷ lệ đơn
bất mãn thật được đi trọn chuỗi phát hiện → phân loại → đề xuất *đúng nhóm nguyên nhân*.

**RQ3 — MAS-DSS có tốt hơn MIS và single-ML không?**
`run_evaluation.py` sinh bảng so sánh. Lưu ý khi viết Chương 5: về thuần accuracy/F1, MAS-DSS và
single-model dùng *cùng một* mô hình dự báo nên sẽ xấp xỉ nhau — **đó là kết quả đúng, không phải
lỗi**. Điểm khác biệt phải lập luận nằm ở ba chỗ: (1) MIS chỉ phát hiện sau khi đã trễ, recall thấp
và không chủ động; (2) single-model dừng ở xác suất, `pipeline_completeness = 0` vì không sinh được
hành động; (3) chỉ MAS-DSS cho ra hành động gắn nguyên nhân kèm decision trace. Đừng cố chứng minh
MAS thắng ở accuracy — hãy chứng minh nó thắng ở *chất lượng chuỗi quyết định*.

**RQ4 — Bối cảnh nào phát huy hiệu quả?**
Phân tích theo lát cắt (nhóm hàng, khoảng cách địa lý, seller) + thảo luận mở rộng CRM/supply chain.

## Trạng thái hiện tại

Đã có: toàn bộ khung 5 lớp chạy được, 12 test pass, ablation infrastructure, bộ chỉ số, dashboard.

Còn phải làm trước khi có số cho Chương 5:
1. Tải dataset Olist vào `data/raw/` (9 file CSV).
2. Chạy `build_dataset` → `train_models` → `run_pipeline` → `run_evaluation`.
3. Gán tay nhãn nguyên nhân cho một mẫu ~200 đơn để kiểm định độ chính xác của weak labels —
   nếu không, phần Root-Cause Agent sẽ bị phản biện là "tự chấm điểm bằng nhãn do chính mình sinh ra".
4. Chạy nhiều seed / nhiều ngưỡng `dissatisfied_threshold` để báo cáo độ nhạy.
