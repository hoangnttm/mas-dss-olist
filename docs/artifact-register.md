# Danh mục artifact — ánh xạ tới mục tiêu, câu hỏi nghiên cứu và bằng chứng

> **Một bảng duy nhất trả lời: artifact nào phục vụ câu hỏi nào, bằng chứng nằm ở tệp nào, tái lập bằng
> lệnh gì, và số của nó có trích được không.** Cập nhật **15/08/2026** · 303 test xanh · cổng G5 đạt.
>
> Thay thế §5 của [status-checklist.md](status-checklist.md). Phân loại theo Hevner
> *(construct / model / method / instantiation)*, số hiệu theo
> [research-questions-objectives.md §7.2](research-questions-objectives.md).
>
> **Quy tắc: không ô nào để trống, và mỗi ✅ phải trỏ tới một tệp tồn tại.**

---

## 0. Ba câu hỏi và ba mục tiêu

| MT | RQ | Loại claim | Giả thuyết | Artifact | Chương |
|---|---|---|---|---|---|
| **MT1** — phát triển phương pháp đánh giá chịu lỗi | **RQ1** *(trục chính)* | Causal | H2, H3 | A4, A5, A6 | 5 |
| **MT2** — thiết kế kiến trúc và rút tri thức thiết kế | **RQ2** | Design *(demonstration)* | — | A1, A2, A5 | 3, 4 |
| **MT3** — prototype và điều kiện so sánh không thiên lệch | **RQ3** *(điều kiện kiểm soát)* | Criterion | H1 | A3, A5, A6 | 4, 5 |

---

## 1. Bảng đăng ký

### A1 — Ontology và giao thức giao tiếp

| | |
|---|---|
| **Loại** | Construct |
| **Phục vụ** | MT2.1 → RQ2 |
| **Tiêu chí hoàn thành** *(nguyên văn MT2.1)* | *"mọi bất biến của ontology được **cưỡng chế lúc khởi tạo đối tượng** … và mỗi bất biến có ít nhất một kiểm thử canh giữ. Ba bất biến bắt buộc: `degradation_level` **không có giá trị mặc định**; suy giảm lớn hơn 0 kéo theo `needs_human_review`; từ hai nguyên nhân trở lên kéo theo `multi_cause`."* |
| **Bằng chứng** | `src-v3/masdss/core/message.py` *(10 performative)* · `core/ontology.py` · `core/decision.py` *(3 bất biến trong `__post_init__`)* |
| **Test canh** | `tests-v3/test_decision_invariant.py` *(Hypothesis property test)* · `test_output_invariants.py::test_len_performative` |
| **Tái lập** | `python -m pytest tests-v3/test_decision_invariant.py` |
| **Trạng thái** | ✅ **đạt** |

### A2 — Kiến trúc tham chiếu và bốn nguyên lý thiết kế

| | |
|---|---|
| **Loại** | Model |
| **Phục vụ** | MT2.2 + MT2.3 → RQ2 |
| **Tiêu chí hoàn thành** *(nguyên văn MT2.2)* | *"**một nguồn sự thật duy nhất về trạng thái** là blackboard, kiểm chứng được bằng việc decision trace dựng lại được trọn vẹn **chỉ từ nhật ký message**; và mọi cơ chế điều phối bật/tắt được **bằng tham số cấu hình**, không bằng nhánh mã nguồn"* |
| | *(MT2.3)* *"mỗi nguyên lý được gắn với một **cơ chế cưỡng chế trong mã nguồn** và một **thí nghiệm ablation** tương ứng"* |
| **Bằng chứng** | `system/plan.py` *(kế hoạch dạng dữ liệu)* · `system/contract_net.py` · `system/blackboard.py` · `system/reliability/` *(6 module, 447 dòng)* |
| **Ablation** | `data/v3/evaluation/ablations.csv` — bốn dòng, một cho mỗi DP |
| **Tái lập** | `python -m masdss.cli.run_ablations` |
| **Trạng thái** | ✅ **đạt** · `citable = True` |

**Bốn nguyên lý và số đo tương ứng:**

| DP | Cơ chế cưỡng chế | Ablation | Chỉ số |
|---|---|---|---|
| **DP1** suy giảm minh bạch | `degradation_level` không có mặc định | `reliability=False` | hỏng âm thầm dưới Byzantine |
| **DP2** đa nhãn, cạnh tranh khi thẩm quyền chồng lấn | cấm `argmax` *(quét AST)* | đối chứng đơn khối đa nhãn | **0** ô bất đồng / 900 |
| **DP3** từ chối thay vì đoán | performative `REFUSE` · OOD | `allow_refuse=False` | quy kết sai khi người bỏ trống **0,5 → 1,0** |
| **DP4** nguồn gốc từ giao tiếp | Explainer chỉ đọc nhật ký | trace viết tay | độ phân kỳ **39,94%** |

### A3 — Bộ nhãn chuẩn do người gán

| | |
|---|---|
| **Loại** | Instantiation / resource — **điều kiện tiên quyết của RQ3** |
| **Phục vụ** | MT3.2 → RQ3 |
| **Tiêu chí hoàn thành** *(nguyên văn MT3.2)* | *"gán nhãn độc lập bởi hai người theo codebook thống nhất, **cho phép đa nhãn** … báo cáo hệ số đồng thuận Cohen's κ"* |
| **Bằng chứng** | `data/v3/goldset/gold_labels.csv` *(300 dòng)* · `gold_merged.csv` + `_meta.json` · `agreement_report_v3.csv` |
| **Số đo** | **κ = 0,784** · độc lập 77,7% · **4/4 nhãn** đủ dương để tin cậy · trùng vòng trước **0 đơn** |
| **Cổng** | **G2 ĐẠT** *(κ ≥ 0,6)* |
| **Tái lập** | `python -m masdss.cli.merge_goldset --a … --b … --rule union` → `build_goldset --provenance human_independent` |
| **Trạng thái** | ✅ **đạt** · `citable = True` |
| **Giới hạn** | **Tầng B *(đơn không có bình luận)* ngoài phạm vi** · 2 dòng xung đột thật được phép hợp OR gán **cả hai nhãn mâu thuẫn** |

### A4 — Chaos harness *(đóng góp phương pháp — trục chính)*

| | |
|---|---|
| **Loại** | Method |
| **Phục vụ** | MT1.2 → RQ1 |
| **Tiêu chí hoàn thành** *(nguyên văn MT1.2)* | *"năm nhóm lỗi được tiêm ở ba mức nhiễu loạn, trong đó nhóm lỗi tinh vi … **không được thiết kế riêng để bộ giám sát bắt được**; **cùng một kịch bản lỗi** được chạy trên cả MAS-DSS lẫn Monolithic-Complete"* |
| **Bằng chứng** | `chaos/scenarios.py` *(16 kịch bản = 5 nhóm × 3 mức + khỏe)* · `chaos/injector.py` · `chaos/runner.py` |
| **Kết quả** | `data/v3/chaos_v3/{scenarios,sensitivity_curve}.csv` |
| **Test parity** | `tests-v3/test_chaos_parity.py` — 12 test, gồm test canh **nhiễu loạn phải tới được đường quyết định của cả hai kiến trúc** |
| **Cổng** | **G5 ĐẠT** — `data/v3/evaluation/gate_g5_tai_lap.json` |
| **Tái lập** | `python -m masdss.cli.run_chaos --n 200 --out data/v3/chaos_v3` |
| **Trạng thái** | ✅ **đạt trên bề mặt dùng chung** |
| **Phạm vi** | ⛔ Bề mặt **chỉ-MAS ngoài phạm vi** — tầng guard chưa bao giờ đăng ký cho bốn thành phần riêng có. Artifact cũ ở `data/v3/_ngoai_pham_vi/chaos_masonly/` |

### A5 — Prototype MAS-DSS trên Olist

| | |
|---|---|
| **Loại** | Instantiation |
| **Phục vụ** | MT3.1 → RQ1, RQ2, RQ3 |
| **Tiêu chí hoàn thành** *(nguyên văn MT3.1)* | *"decision trace của mỗi case **dựng lại được hoàn toàn từ nhật ký message**, không phụ thuộc vào bất kỳ tham số nào nằm ngoài nhật ký đó"* |
| **Bằng chứng** | `src-v3/masdss/` — **88 tệp · 12.725 dòng** · 10 tác tử · 5 tầng |
| **Cổng** | **G4 ĐẠT** — `test_skeleton_e2e.py::test_trace_is_rebuilt_from_log_alone` |
| **Tái lập** | `python -m masdss.cli.run_system --stage 2 --n 300` |
| **Trạng thái** | ✅ **đạt** |
| **Giới hạn** | Encoder là **TF-IDF**, không phải BERTimbau · `BidCalibrator` **chưa nối vào đường chạy chính** · fallback **L1/L2 chưa cài** · `monitoring_coverage` có `installed: false` ở `cause_quality`/`cause_service` |

### A6 — Khung đánh giá và bốn kiến trúc đối chứng

| | |
|---|---|
| **Loại** | Method + instantiation |
| **Phục vụ** | MT1.1 → RQ1, RQ3 |
| **Tiêu chí hoàn thành** *(nguyên văn MT1.1)* | *"Monolithic-Complete sử dụng **chung** mô hình dự báo, **chung** head và **chung** tập luật YAML với MAS-DSS, chỉ khác ở chỗ không có tầng đa tác tử; hệ này được cài đặt theo cách tự nhiên nhất mà một kỹ sư có kinh nghiệm sẽ viết, **không bị làm yếu có chủ ý**"* |
| **Bằng chứng** | `baselines/monolithic.py` · `baselines/simple.py` *(MIS, Single-ML)* · `evaluation/` *(7 module)* |
| **Test parity** | `test_agents_and_baselines.py::test_baseline_shares_the_same_capability_objects` — so sánh bằng **định danh đối tượng** (`is`) · `test_monolithic_is_multi_label` · `test_no_argmax_in_attribution_path` *(quét AST)* |
| **Tái lập** | `python -m masdss.cli.run_attribution` · `run_evaluation` · `run_rules_report` |
| **Trạng thái** | ✅ **đạt** · `citable = True` |

### A7 — Giao thức đánh giá bởi chuyên gia

| | |
|---|---|
| **Loại** | Method |
| **Phục vụ** | nhánh tùy chọn §5.1 |
| **Trạng thái** | ⬜ **không thực hiện** — phụ thuộc việc tuyển được 3–5 chuyên gia, nằm ngoài tầm kiểm soát. Hệ quả đã khai báo: luận văn **không tuyên bố** về hiệu quả hỗ trợ quyết định so với MIS |

---

## 2. Tổng kết theo mục tiêu

| Mục tiêu | Câu hỏi | Trạng thái | Điều còn thiếu |
|---|---|---|---|
| **MT1** chịu lỗi + chi phí *(trục chính)* | RQ1 | ✅ **đạt trên bề mặt dùng chung** | Bề mặt chỉ-MAS **đặt ngoài phạm vi** — không phải thiếu đo, mà là quyết định phạm vi có ghi hồ sơ |
| **MT2** thiết kế + 4 nguyên lý | RQ2 | ✅ **đạt đủ** | Bốn DP đều có cơ chế cưỡng chế **và** ablation `citable` |
| **MT3** prototype + gold set | RQ3 | ✅ **đạt** | Tầng B ngoài phạm vi; BERTimbau và `BidCalibrator` là hạng mục còn mở, đã ghi ở Threats |

**6/6 artifact bắt buộc tồn tại và sinh được số `citable`.**

---

## 3. Sáu cổng

| Cổng | Tiêu chí | Trạng thái | Bằng chứng |
|---|---|---|---|
| **M0** | tỷ lệ đơn bất mãn không có bình luận < 50% | ✅ **25,23%** | `research-questions-objectives.md` §0.1 |
| **G1** | thống kê mô tả khớp bảng M0, lệch < 1% | ✅ | `data/load.describe_m0()` |
| **G2** | κ ≥ 0,6, tính độc lập đạt | ✅ **κ = 0,784** | `agreement_report_v3.csv` |
| **G3** | mô hình rủi ro đủ tốt để có ý nghĩa nghiệp vụ | ✅ PR-AUC 0,2381 · lift 1,87 · precision@0,5% = 0,679 | `forecasting.csv` |
| **G4** | trace dựng lại **chỉ** từ nhật ký message | ✅ | `test_skeleton_e2e.py` |
| **G5** | hai lượt chạy cho `decisions.jsonl` trùng `sha256` | ✅ **ĐẠT** | `gate_g5_tai_lap.json` |

---

## 4. Ba giả thuyết

| # | Phát biểu | Phán quyết | Loại bằng chứng |
|---|---|---|---|
| **H1** | tương đương độ chính xác ở cả hai mốc | ✅ **tương đương** — 0/900 ô bất đồng, chênh lệch macro-F1 = 0,000000 | ❌ **kiểm tra đặc tả** — dùng chung một đối tượng mô hình |
| **H2** *(bản sửa 14/08)* | hỏng âm thầm thấp hơn trên **bề mặt dùng chung**, cả hai mốc | ✅ **được ủng hộ** ở nhóm lỗi không ném ngoại lệ | ✅ thực nghiệm cho **đơn khối**; ❌ đặc tả cho MAS |
| **H3** | phát hiện drift **trước khi** chất lượng suy giảm | ❌ **bác bỏ** — không phát hiện ở cả ba mức | ✅ thực nghiệm — `designed_for = False` |

⚠️ **H2 đã bị sửa sau khi thấy kết quả** — phát biểu gốc giữ nguyên văn kèm hồ sơ sửa đổi tại
[research-questions-objectives.md §3](research-questions-objectives.md). Bản sửa **dễ thỏa mãn hơn**
bản gốc, và Chương 5 phải nói đúng như vậy.

---

## 5. Nơi tra tiếp

| Câu hỏi | Tài liệu |
|---|---|
| Chỉ số này đo gì, tính thế nào, trích được không | [evaluation-handbook.md](evaluation-handbook.md) |
| Phát biểu gốc của mục tiêu, câu hỏi, giả thuyết | [research-questions-objectives.md](research-questions-objectives.md) |
| Nhật ký lỗi phương pháp *(nguyên liệu Chương 5)* | [methodology-log.md](methodology-log.md) |
| Kiến trúc và quyết định công nghệ | [technical-plan-v3.md](technical-plan-v3.md) |
| Việc đang làm, số hiện hành | [session-state.md](session-state.md) |
