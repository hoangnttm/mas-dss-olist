# Sổ tay phương pháp đánh giá

> **Một tài liệu duy nhất trả lời: chỉ số này đo cái gì, tính thế nào, ai canh nó, và có trích được
> vào luận văn không.** Cập nhật **15/08/2026** · 303 test xanh · cổng G5 đạt.
>
> Đây là **nguồn chuẩn duy nhất** cho câu hỏi *"số này trích được không"*. Không duy trì danh sách thứ
> hai ở nơi khác — chính cơ chế hai danh sách song song đã sinh ra bẫy trích dẫn phải rào lại ở
> [session-state.md §4](session-state.md) và [status-checklist.md §6](status-checklist.md).

---

## 0. Ba ranh giới chi phối mọi con số

### 0.1 `citable` — nguồn gốc nhãn

Mọi chỉ số quy kết nguyên nhân chỉ trích được khi bảng mang `citable = True`. Cờ này **không phải quy
ước** mà là hệ quả của kiểu dữ liệu:

```
Provenance.HUMAN_INDEPENDENT  ──> GoldLabels.citable ──> AttributionResult.citable ──> cột trong CSV
```

`Provenance` **không có giá trị mặc định**; mọi nơi tạo `GoldLabels` đều buộc phải khai báo. Truyền
chuỗi tự do vào sẽ `raise TypeError`.

**Phép thử ngược bắt buộc:** truyền một gold set `model_assisted_provisional` vào `run_attribution` và
xác nhận **mọi** bảng lật `citable = False`. Chỉ khi phép thử này xanh thì cờ mới chứng minh được là có
tác dụng — lỗi **L28** từng khiến cờ này sai **theo cả hai chiều** mà không để lại dấu hiệu nào.

### 0.2 Kiểm tra đặc tả ↔ kết quả thực nghiệm

Xoá nhoà ranh giới này là cách dễ nhất để một luận văn tự tô vẽ mà không nói sai câu nào.

| ✅ Kết quả thực nghiệm | ❌ Kiểm tra đặc tả |
|---|---|
| Hỏng âm thầm của **đơn khối** — đối chứng không bị dàn dựng để hỏng | Hỏng âm thầm của **MAS-DSS** — cơ chế được viết ra để bắt đúng lỗi đó |
| Hai nhóm `designed_for = False` *(drift, bias)* | Ba nhóm `designed_for = True` *(crash, hang, byzantine)* |
| Độ trễ phát hiện · tỷ lệ báo động giả | **H1 ở cả hai mốc** — hai kiến trúc dùng **chung một đối tượng** mô hình |
| Toàn bộ chi phí *(bề mặt hỏng, độ trễ, quy mô mã)* | |

Cột `designed_for` có sẵn trong `chaos_v3/sensitivity_curve.csv` — **dùng chính cột đó**, không gõ tay
lại phân loại.

### 0.3 Mô tả ↔ kiểm định

Sau khi ràng buộc ngân sách được gỡ, hai kiến trúc cho kết quả **giống hệt nhau**, nên trong toàn bộ
tầng đánh giá chỉ còn **một** bảng mang tính kiểm định: `attribution_compare.csv`. Mọi bảng còn lại là
**mô tả**.

Phân biệt này quyết định việc có phải hiệu chỉnh đa kiểm định hay không. `attribution.evaluate()` sinh
3 nguyên nhân × 5 lát cắt × 2 hệ thống = **30 con số** cùng lúc; nếu coi tất cả là kiểm định thì phải
áp Holm hoặc Bonferroni. **Nghiên cứu chọn cách khác và ghi rõ ở đây:** các lát cắt là mô tả, không
phải kiểm định, nên không hiệu chỉnh. Chỉ có một kiểm định khẳng định duy nhất — so sánh macro-F1 toàn
bộ giữa hai kiến trúc — và nó cho **0/300 ô bất đồng**, tức một đẳng thức chứ không phải một phép thử.

---

## 1. Tầng dự báo tại T₃

Nguồn: `data/v3/evaluation/forecasting.csv` · `threshold_sensitivity.csv` · `data/v3/calibration_report.csv`
Sinh lại: `python -m masdss.cli.run_evaluation`

| Chỉ số | Giá trị | Cách tính | Loại |
|---|---|---|---|
| **PR-AUC** *(chính)* | **0,2381** [0,2187 ; 0,2578] | `average_precision_score`, KTC **percentile bootstrap** B = 1.000, seed 20260809, α = 0,05 | thực nghiệm |
| ROC-AUC *(phụ)* | 0,6522 [0,6374 ; 0,6667] | `roc_auc_score` | thực nghiệm |
| Tỷ lệ nền | 0,1274 | `y.mean()` trên 11.322 đơn kỳ kiểm thử | mô tả |
| **Lift PR-AUC / nền** | **1,87×** | PR-AUC ÷ tỷ lệ nền | thực nghiệm |
| Ngưỡng tối ưu theo chi phí | **0,194** | cực tiểu chi phí kỳ vọng, FN:FP theo `rules.yaml` | mô tả |
| Thang rủi ro LOW/MED/HIGH | **0,160 / 0,3103** | suy từ **tập kiểm định** lúc fit; lưu trong chính mô hình | mô tả |

**Vì sao PR-AUC là chỉ số chính chứ không phải ROC-AUC.** Lớp dương chiếm 12,74%; ROC-AUC lạc quan giả
trên dữ liệu mất cân bằng vì nó thưởng cho việc xếp hạng đúng phần âm vốn đã áp đảo.

### 1.1 ⚠️ Vì sao **accuracy không được dùng làm chỉ số chính**

| Ngưỡng | Accuracy | Precision | Recall | Tỷ lệ can thiệp |
|---|---|---|---|---|
| 0,160 *(vận hành)* | 0,6902 | 0,2060 | 0,5021 | 31,04% |
| 0,194 *(tối ưu chi phí)* | 0,7591 | 0,2335 | 0,3904 | 21,29% |
| 0,5 *(mặc định)* | 0,8744 | 0,7000 | **0,0243** | 0,44% |
| **Đoán tất cả hài lòng** | **0,8726** | — | 0,0000 | 0% |

Điểm vận hành đạt accuracy **thấp hơn** mốc tầm thường, và ngưỡng 0,5 chỉ vượt mốc tầm thường 0,0018
trong khi **bỏ sót 97,6% số đơn bất mãn**. Một hệ thống phục hồi dịch vụ không can thiệp vào ai thì
không có giá trị nào, dù accuracy đẹp.

### 1.2 Hiệu chuẩn

| Chỉ số | Trước | Sau isotonic |
|---|---|---|
| ECE *(10 bin đều)* | 0,0696 | **0,028** |
| Brier | 0,1136 | 0,1075 |
| **Brier skill** *(so hằng số = tỷ lệ nền)* | **−0,0217** | **+0,0328** |

**Brier skill âm trước hiệu chuẩn là một phát hiện phải báo cáo, không phải một chi tiết kỹ thuật:**
điểm thô **thua một hằng số**. Hiệu chuẩn isotonic vì vậy là **bắt buộc**, không phải tùy chọn. Chỉ báo
cáo Brier thô mà không đặt cạnh hằng số sẽ giấu mất điều này.

Số trên tập kiểm định mang nhãn `[IN-SAMPLE — khong dung de bao cao]` — hiệu chuẩn rồi đo trên chính
tập đã học cho ECE = 0 giả tạo *(lỗi **L04**)*. Cờ `in_sample` chèn thẳng vào tên chỉ số nên không thể
trích nhầm.

### 1.3 Độ nhạy ngưỡng định nghĩa nhãn

| Ngưỡng nhãn | Tỷ lệ dương | PR-AUC | ROC-AUC |
|---|---|---|---|
| `rating ≤ 2` *(dùng)* | 0,1274 | 0,2381 | 0,6522 |
| `rating ≤ 3` | 0,2024 | 0,3150 | 0,6283 |

Kết luận **không đảo chiều** giữa hai định nghĩa — PR-AUC tăng cùng tỷ lệ nền đúng như kỳ vọng, và thứ
hạng giữa hai kiến trúc không đổi.

### 1.4 Điều kiện kiểm soát H1

Nguồn: `control_condition.csv` · `control_condition.txt`

Hai phép đo khác nhau, và cả hai đều cần:

| Phép đo | Câu hỏi nó trả lời |
|---|---|
| `verify_shared_capability` | *"Hai dãy điểm có **giống hệt** nhau không?"* — so sánh từng bit, `atol = 1e-12` |
| **TOST** *(biên ±0,01, khai báo trước)* | *"Chênh lệch có nằm trong biên tương đương đã khai báo không?"* |

**Kiểm định tương đương chứ không phải kiểm định khác biệt** là bắt buộc về mặt logic: giả thuyết cần
chứng minh là *hai kiến trúc không khác nhau*, và việc không bác bỏ được giả thuyết vô hiệu **không
phải** bằng chứng cho sự tương đương — nó chỉ là bằng chứng cho việc thiếu bằng chứng.

⚠️ Khi hai dãy giống hệt nhau, TOST tự đánh dấu `identical = True` kèm ghi chú *"tautology"*. Phải báo
cáo đúng như vậy: đây là **kiểm tra đặc tả**, không phải kết quả thực nghiệm.

---

## 2. Tầng quy kết tại T₄

Nguồn: `attribution_per_cause.csv` · `attribution_per_slice.csv` · `attribution_compare.csv`
Sinh lại: `python -m masdss.cli.run_attribution --run data/v3/runs/goldset_v3`

### 2.1 Macro-F1 — chỉ số chính của RQ3

**Tính trên ba nguyên nhân** `delivery` · `quality` · `service`. **Không tính `unknown`**: nó là *hệ
quả* của việc không quy kết được, không phải một nguyên nhân thứ tư. Đưa vào macro sẽ **thưởng cho hệ
thống nào im lặng nhiều nhất**.

| Nhãn | MAS-DSS | Đơn khối | Precision | Recall |
|---|---|---|---|---|
| `delivery` | 0,7302 | 0,7302 | 0,6647 | 0,8099 |
| `quality` | 0,6667 | 0,6667 | 0,9200 | 0,5227 |
| `service` | 0,6618 | 0,6618 | 0,8654 | 0,5357 |
| **macro-F1** | **0,6862** | **0,6862** | | |

### 2.2 Cắt lớp — bắt buộc, không phải tùy chọn

| Lát cắt | n | macro-F1 | Không quy kết |
|---|---|---|---|
| Toàn bộ | 300 | 0,6862 | 24,67% |
| **(a) đa nguyên nhân** | 71 | **0,7353** | 7,04% |
| Đơn nguyên nhân | 229 | 0,6432 | 30,13% |
| Tầng A — có văn bản | 300 | 0,6862 | 24,67% |
| *(b) tầng B — không văn bản* | — | **ngoài phạm vi** | — |

Macro-F1 gộp che mất đúng hai tình huống khó mà RQ3 nêu đích danh. Tầng B **nằm ngoài phạm vi đề tài**,
nên `do_phu_tang_B` để trống thay vì điền một số vô nghĩa.

### 2.3 Đối đầu hai kiến trúc — bảng kiểm định duy nhất

| Phép | Kết quả |
|---|---|
| Số ô bất đồng | **0** trên 900 ô *(300 đơn × 3 nhãn)* |
| McNemar *(nhị thức chính xác)* | **không áp dụng** — tautology |
| Chênh lệch macro-F1, KTC 95% bootstrap | **0,000000** [0,000000 ; 0,000000], B hiệu dụng 1.000 |

**Đây là một đẳng thức đại số, không phải một kết quả thống kê** *(lỗi **L27**)*. Ba analyst sở hữu ba
nguyên nhân **rời nhau**, dùng **chung** một cause head, và arbiter nhận **mọi** bid vượt **cùng** một
ngưỡng τ. Ghép lại thì MAS-DSS = *"chấm 3 nhãn bằng head chung, giữ nhãn vượt τ"* — đúng bằng định
nghĩa của đối chứng đơn khối. Không cỡ mẫu nào phá được đẳng thức này.

Trước 14/08, hai kiến trúc **có** khác nhau — nhưng khác biệt đó đến từ **ràng buộc ngân sách** chứ
không từ cơ chế đấu thầu, và ràng buộc ấy nay đã được gỡ khỏi cấu hình báo cáo.

### 2.4 Selective prediction — điều kiện để DP3 không tự trừ điểm

| Chỉ số | MAS-DSS | Đơn khối |
|---|---|---|
| Độ phủ | 0,7533 | 0,7533 |
| macro-F1 trên phần đã trả lời | 0,7550 | 0,7550 |
| macro-F1 toàn bộ | 0,6862 | 0,6862 |
| **Giá của im lặng** | 0,0688 | 0,0688 |
| **Quy kết sai khi người gán bỏ trống** | **0,5000** | 0,5000 |

Macro-F1 thuần **phạt** việc từ chối trả lời. Nếu chỉ báo F1, một hệ thống biết im lặng sẽ thua **theo
cấu tạo**, trong khi im lặng mới là hành vi đúng về mặt tri thức luận.

⚠️ **Đường cong risk–coverage đã được sửa ngày 14/08.** Bản trước cắt mức phủ theo **thứ tự dòng trong
DataFrame** — mà khung đã sắp theo `order_id`, nên đó là cắt **ngẫu nhiên có hệ thống**, không phải
selective prediction. Bản sửa sắp theo **độ tin cậy giảm dần**, và cả hai kiến trúc đều phải cung cấp
cột `confidence`; thiếu cột này nay là **lỗi dừng hẳn**, không phải cảnh báo.

---

## 3. Tập luật hỗ trợ quyết định

Nguồn: `rules_1_danh_muc.csv` · `rules_2_t4_theo_luat.csv` · `rules_3_t3_thang_hanh_dong.csv`
Sinh lại: `python -m masdss.cli.run_rules_report`

**Thang hành động tại T₃** — lift là cột quan trọng nhất:

| Luật | Hành động | Độ phủ | Precision | **Lift** |
|---|---|---|---|---|
| `t3_qua_han_rui_ro_cao` | xin lỗi + phiếu giảm giá | 0,26% | 0,5517 | **4,332** |
| `t3_sap_qua_han_rui_ro_cao` | xin lỗi + phiếu giảm giá | 0,48% | 0,4259 | 3,344 |
| `t3_rui_ro_cao` | mở ticket trước | 7,25% | 0,2923 | 2,295 |
| `t3_sap_qua_han` | mở ticket trước | 1,25% | 0,2817 | 2,212 |
| `t3_qua_han` | gọi lại trong 24h | 1,08% | 0,2787 | 2,188 |
| `t3_rui_ro_trung_binh` | mở ticket trước | 21,32% | 0,1591 | 1,249 |
| `no_cause_low_risk` | không can thiệp | 68,36% | 0,0911 | 0,715 |

Thang này **đơn điệu tăng theo mức can thiệp**, và đó là tính chất phải kiểm: một mức can thiệp đắt hơn
mà lift không cao hơn thì nó không chọn lọc được gì.

⚠️ **Ràng buộc C1.** Bảng trên đo **chất lượng khuyến nghị** — hệ thống có đề xuất đúng loại hành động
cho đúng nhóm đơn hay không — chứ **không đo hiệu quả can thiệp**. Olist không có biến treatment và
không có kết cục phản thực. Mọi phát biểu dạng *"hành động này giảm bất mãn X%"* đều vượt quá dữ liệu.

---

## 4. Tầng chịu lỗi — trục chính

Nguồn: `data/v3/chaos_v3/{scenarios,sensitivity_curve}.csv` · Sinh lại: `python -m masdss.cli.run_chaos --n 200 --out data/v3/chaos_v3`

### 4.1 Định nghĩa hỏng âm thầm — ba bước

1. Chạy **đường khỏe**, chụp lại **khóa quyết định** của từng case: *(hành động, tập nguyên nhân, mức rủi ro)*.
2. Dưới mỗi kịch bản lỗi, case **đổi đầu ra** nếu khóa khác đường khỏe.
3. Case là **hỏng âm thầm** nếu nó đổi đầu ra **và** hệ thống không phát tín hiệu nào.

Khóa quyết định **cố ý không chứa** mức suy giảm và cờ chuyển giao — nó phải đo *nội dung quyết định*
tách rời khỏi *việc có cảnh báo hay không*.

**Tín hiệu cảnh báo phải hỏi cùng một câu với cả hai kiến trúc:**

| Kiến trúc | Phát tín hiệu qua |
|---|---|
| MAS-DSS | `degradation_level > 0` · `needs_human_review` · hành động `escalate_to_human` |
| Đơn khối | trường `failed_steps` |

⚠️ **Lỗi L37 đã từng vi phạm điều này**: bản trước coi mọi đầu ra bị đổi của đơn khối là *"âm thầm"*
với lý do *"đơn khối không có cờ suy giảm"* — bỏ qua `failed_steps`. Sai lệch nghiêng về phía **có lợi
cho artifact của chính nghiên cứu**: con số *"16–38% dưới crash"* thực ra là **0,0%**.

### 4.2 Kết quả — bề mặt thành phần dùng chung, 200 case × 16 kịch bản

| Nhóm lỗi | Ném ngoại lệ | `designed_for` | Đầu ra đổi | **MAS âm thầm** | **Đơn khối âm thầm** | Phát hiện |
|---|---|---|---|---|---|---|
| crash 1·2·3 | ✔ | có | 57,5 → 79,5% | **0,0%** | **0,0%** | không |
| hang 1·2·3 | ✔ | có | 57,5 → 79,5% | **0,0%** | **0,0%** | không |
| **byzantine 1·2·3** | ✘ | có | 58,0% | **5,0%** | **84,5 → 99,0%** | sau **20** quan sát |
| **drift 1·2·3** | ✘ | **không** | 3,5 → 7,5% | 2,5 → 5,0% | 3,5 → 6,5% | **không** |
| **bias 1·2·3** | ✘ | **không** | 33,0 → 59,5% | **8,5 → 21,0%** | 25,0 → 84,5% | sau **100** quan sát |

⚠️ **Ba con số ở hai nhóm byzantine và bias đã đổi ngày 14/08** sau khi sửa L43. Trước đó cả hai nhóm
cho MAS = **0,0%**, và con số ấy phản ánh **chỗ đặt bộ tiêm** chứ không phản ánh kiến trúc — lỗi đầu độc
`risk_score` trong khi quyết định đọc `risk`. Phát biểu đúng là *"giảm đáng kể"*, **không phải** *"miễn
nhiễm"*.

⚠️ **Nhóm `hang` có một bất đối xứng phải nêu**: đơn khối cho `mono_changed = 0,0%` vì nó **không có
hạn chót** — nó chỉ chạy chậm hơn rồi cho ra cùng kết quả, trong khi MAS timeout và suy giảm. Trong thí
nghiệm độ trễ tiêm vào là hữu hạn nên đơn khối hoàn thành được; trong vận hành thật một thành phần treo
vô hạn sẽ làm treo cả chuỗi. Phép đo **không nắm bắt được thiệt hại thật** của đơn khối ở nhóm này.

**Đường khỏe: 0,0% suy giảm · 0 guard chặn · báo động giả = 0.** Đây là điều kiện để mọi con số ở trên
có nghĩa — một bộ giám sát kêu suốt ngày thì tỷ lệ phát hiện cao không chứng minh gì.

**Ba điều đọc đúng từ bảng:**

1. **Ưu thế của MAS nằm trọn ở nhóm lỗi *không ném ngoại lệ*.** Với crash và hang, cả hai kiến trúc đều
   0,0% — `try/except` là đủ. Chênh lệch chỉ xuất hiện ở byzantine và bias, tức lỗi **trả về giá trị
   hợp lệ nhưng sai**.
2. **Chỉ hai dòng `designed_for = False` là kết quả thực nghiệm nghiêm ngặt.** `bias` — guard bắt được
   **dù không được thiết kế cho nó**. `drift` — **cả hai gần như mù**, và đây là một giới hạn thật.
3. **Cột "đầu ra đổi" tách hai thứ mà chỉ số cũ trộn lẫn.** Ở crash mức 3, **79,5%** quyết định thay
   đổi nhưng hỏng âm thầm **0,0%**: hệ bị ảnh hưởng nặng mà **cảnh báo đủ mọi ca**.

### 4.3 Phạm vi đã thu hẹp — phải nói rõ

Bảng trên chỉ phủ **bề mặt thành phần dùng chung**. Bốn thành phần riêng có của kiến trúc đa tác tử
*(`analytics`, `recommendation`, `critic`, `arbiter`)* **nằm ngoài phạm vi** — tầng `reliability/` chưa
bao giờ đăng ký guard cho chúng. Hồ sơ sửa phát biểu H2 và lý do đầy đủ:
[research-questions-objectives.md §3](research-questions-objectives.md).

---

## 5. Bốn ablation cho bốn nguyên lý thiết kế

Nguồn: `ablations.csv` + các tệp `ablation_dp*` · Sinh lại: `python -m masdss.cli.run_ablations`

| DP | Cơ chế bị gỡ | Chỉ số | Có cơ chế | Gỡ cơ chế |
|---|---|---|---|---|
| **DP1** suy giảm minh bạch | tầng chịu lỗi | hỏng âm thầm dưới byzantine | **5,0%** | **34,0%** |
| **DP2** đa nhãn, cạnh tranh khi thẩm quyền chồng lấn | so với đối chứng đa nhãn | số ô bất đồng | 0 | 0 |
| **DP3** từ chối thay vì đoán | performative `REFUSE` | quy kết sai khi người bỏ trống | **0,5000** | **1,0000** |
| **DP4** nguồn gốc từ giao tiếp | trace dựng từ `Decision` | độ phân kỳ | 0,0 | **0,4061** |

**DP1 — đọc kỹ cột "quyết định đổi".** Bật tầng chịu lỗi: 116 quyết định đổi, 10 âm thầm *(5,0%)*, 8
lần guard chặn, 174 case bị gắn mức suy giảm. Tắt: 125 quyết định đổi, **68 âm thầm (34,0%)**, 0 guard.
Số quyết định đổi gần bằng nhau ở hai cấu hình nên phép so sánh công bằng — lỗi tới được cả hai ở mức
tương đương, và khác biệt nằm ở chỗ **cái gì xảy ra sau đó**.

### 5.1 DP3 — cái giá của việc bỏ quyền từ chối

| | Có `REFUSE` | Cấm `REFUSE` |
|---|---|---|
| Độ phủ | 0,7533 | **1,0000** |
| macro-F1 toàn bộ | **0,6862** | 0,4827 |
| `delivery` precision · recall | 0,6647 · 0,8099 | 0,5190 · 0,8662 |
| `quality` precision · recall | **0,9200** · 0,5227 | **0,2697** · 0,8182 |
| `service` precision · recall | **0,8654** · 0,5357 | **0,2574** · 0,8333 |
| Quy kết sai khi người bỏ trống | 0,5000 | **1,0000** |
| Lát đa nguyên nhân | 0,7353 | 0,7355 |

Ép trả lời làm **recall tăng** nhưng **precision sụp** — `quality` từ 0,92 xuống 0,27. DP3 được ủng hộ.

📌 **Một kết quả ngược chiều đã biến mất, và điều đó cần ghi lại.** Ở bản đo trước *(còn ràng buộc ngân
sách)*, ép trả lời làm lát đa nguyên nhân **tốt lên** 0,3752 → 0,5033, và điều đó được báo cáo như cái
giá thật của DP3. Sau khi gỡ ngân sách, lát này đứng yên *(0,7353 → 0,7355)*. Vậy kết quả ngược chiều
ấy là **hệ quả của ràng buộc ngân sách**, không phải của quyền từ chối.

### 5.2 DP4 — độ phân kỳ giữa hai cách dựng trace

Trên **300 hội thoại**: **6.390 sự kiện thật** trong nhật ký, trace viết tay từ `Decision` chỉ biểu
diễn được **3.838**. **Độ phân kỳ = 39,94%.**

Bốn loại sự kiện mà trace viết tay **không thể** biểu diễn: `refusal` *(analyst từ chối — và lý do)* ·
`declaration` *(bản khai năng lực ở pha 1)* · `award` *(ai thắng, ai thua thầu)* · `critique` *(phản
bác của critic)*.

Trace viết tay **không sai ở những gì nó nói — nó thiếu ở những gì nó không thể nói.** Với một hệ hỗ
trợ quyết định, *"vì sao KHÔNG chọn Y"* thường đáng giá ngang *"vì sao chọn X"*.

---

## 6. Chi phí của bảo đảm

Nguồn: `cost_1..cost_5*.csv` · `coordination{,_detail}.csv`

| Hạng mục | MAS-DSS | Đơn khối |
|---|---|---|
| **Bề mặt hỏng** *(thước đo chính)* | **10** thành phần | **5** |
| **ms mỗi case** *(wall-clock — CÙNG cơ sở cho cả hai vế)* | **114,615** | **9,199** |
| — khoảng qua bốn lượt đo | 115 – 130 | 6,8 – 9,2 |
| — trong đó: ghi nhật ký message | ~65,7 *(≈53%)* | 0 |
| — trong đó: bên trong các lời gọi năng lực | 12,325 | — |
| giây mỗi lô *(75.480 đơn)* | 8.651 | 694 → **chậm hơn 12,5–17,9 lần** |
| Số tác tử · loại message · tầng | 10 · 10 · 5 | 0 · 0 · 2 |
| Dòng mã tầng chịu lỗi | **447** *(6 module)* | 0 |
| Dòng mã tầng phối hợp | **671** *(9 module)* | 0 |

🔴 **L46 — hàng độ trễ cũ đã bị rút.** Bản trước ghi *"10,959 vs 10,820 → +10,5 giây"*. Hai vế khi đó
đo bằng **hai cơ sở khác nhau**: MAS lấy `sum(span.duration_ms)` — chỉ phần **bên trong** các lời gọi
năng lực, bỏ qua glue điều phối và **toàn bộ** phần ghi nhật ký; đơn khối lấy wall-clock của một vòng
lặp **chạy cả ba baseline** *(`mis`, `single_ml`, `monolithic`)* cộng `json.dumps`. Một vế bị hạ thấp,
một vế bị nâng cao, **cả hai đều có lợi cho MAS**.
Nay: `run_system` đo wall-clock cho **cả hai** trong cùng tiến trình, đồng hồ baseline chỉ ôm
`mono.run`. Canh bằng `test_hai_ve_do_tre_phai_CUNG_MOT_CO_SO_do` và
`test_run_system_do_wall_clock_cho_ca_hai_kien_truc`.

⚠️ **Phân rã trước khi quy kết.** Hơn nửa chi phí MAS đến từ nhật ký gọi `commit` **sau mỗi message**:
6.348 lần `commit` tốn 19,7 giây, gộp một lần chỉ tốn 23 ms. Đây là chi phí của **độ bền nhật ký**, và
nó được **giữ nguyên có chủ đích** — thí nghiệm crash ở §5.8 cần từng message đã bền vững trước khi
tiến trình chết. Trừ hẳn phần này, MAS vẫn chậm hơn khoảng **năm lần**.

⚠️ **Độ trễ đo bằng đồng hồ nên KHÔNG tất định** và không so sánh được giữa hai lần chạy trên máy khác
nhau — vì vậy báo cáo dưới dạng **khoảng qua bốn lượt đo**, không dưới dạng một con số. Nó không nằm
trong tệp đầu ra chính tắc, nên không phá vỡ cổng G5.

⚠️ **Không báo cáo chi phí ở dạng phần trăm** — nhưng lý do đã đổi. Bản trước lập luận rằng *"+10,8%"*
phóng đại một chênh lệch không đáng kể; với số đo đúng, chênh lệch **là** đáng kể *(144 phút so với
11,6 phút mỗi lô)* và lập luận ấy phải rút lại. Mệnh đề về chi phí vẫn nằm ngoài bộ giả thuyết vì nó
không có mốc phán quyết được đặc tả trước — nó là **báo cáo mô tả** dưới RQ1(d), nơi người đọc tự phán
quyết theo bối cảnh vận hành của họ.

**Vì sao bề mặt hỏng là thước đo chính:** mili giây và dòng mã đo *quy mô công việc*; số thành phần có
thể hỏng đo *rủi ro đã tạo thêm*.

### 6.1 Phối hợp — cái giá và lợi ích, báo cáo cùng nhau

> **Lượt chạy nguồn: `data/v3/runs/stage2_nobudget`** *(300 case, ngân sách TẮT — đúng cấu hình báo
> cáo)*. Việc ghi rõ lượt chạy là bắt buộc kể từ L47: bản trước lấy số từ `stage2`, một lượt chạy còn
> **bật** ngân sách, nên bảng này mâu thuẫn với chính cấu hình được công bố.

| Cái giá | | Lợi ích | |
|---|---|---|---|
| message / case | 21,16 | bản khai / case *(pha 1)* | 3,00 |
| độ sâu cây hội thoại | 1,0 | bid thật / case *(pha 2)* | 1,30 |
| thời gian **trong** các lời gọi năng lực | 12,325 ms | `REFUSE` / case | 1,94 |
| | | `bid_entropy` TB | 0,8753 |
| | | tỷ lệ đa nguyên nhân | 33,67% |

⚠️ Hàng thứ ba của cột cái giá là **chặn dưới**, không phải chi phí toàn phần: nó chỉ tính phần nằm
bên trong các lời gọi năng lực. Chi phí toàn phần đo bằng wall-clock nằm ở bảng đầu mục 6, và nó lớn
hơn con số này gần **mười lần** *(L46)*.

⚠️ Chỉ số **quy kết / ms** đếm **số** nguyên nhân, không đo **độ đúng** — một hệ quy kết bừa sẽ ăn điểm
cao. Chuỗi cảnh báo được ghi thẳng trong chính hàm sinh ra nó, và con số này **không được trích**.

---

## 7. Bộ nhãn chuẩn

Nguồn: `agreement_report_v3.csv` · `gold_labels_meta.json` · Sinh lại: `python -m masdss.cli.check_goldset`

| | |
|---|---|
| Cỡ mẫu | **300 dòng**, hai người gán độc lập, chỉ kỳ kiểm thử |
| Tính độc lập | hàng nhãn trùng khớp **77,7%** *(vòng trước 96,4% và đã bị chặn — **L26**)* |
| **κ trung bình** | **0,784** — `delivery` 0,774 · `quality` 0,873 · `service` 0,801 · `unknown` 0,688 |
| Đủ dương để tin cậy | **4/4 nhãn** |
| Quy tắc hợp nhất | **HỢP (OR)** |
| Bất đồng | 67/300 *(22,3%)* — bỏ sót 53,7% · khác số lượng 43,3% · **xung đột thật 3,0%** |

**Nghịch lý κ.** Nhãn có dưới **20** lượt gán dương bị đánh dấu không đáng tin và **loại khỏi trung
bình**, nhưng vẫn được **nêu riêng**. Ẩn đi sẽ tạo vấn đề khác: người đọc không biết có một nhãn không
được đánh giá. Vòng đầu tiên, nhãn `price` có mức đồng ý 98,7% nhưng κ = **−0,006** vì cả hai người
cộng lại chỉ đánh dấu dương năm lần.

⚠️ **Threats to Validity:** với **2 dòng xung đột thật**, phép hợp OR gán **cả hai nhãn mâu thuẫn**.

---

## 8. Guard — cái gì chặn cái gì

| Guard | Chặn lỗi gì |
|---|---|
| `_require_gold()` · `WeakLabelInEvaluation` | Vòng tròn *sinh nhãn → huấn luyện → đánh giá bằng chính nhãn đó* **(C2)**. Hai lối vào đều bị bịt, cưỡng chế **bằng kiểu dữ liệu** |
| `Provenance` → `citable` | Số đo trên nhãn tạm lọt vào Chương 5 **(L28)** |
| `designed_for` | Trình bày kiểm tra đặc tả như phát hiện thực nghiệm |
| `in_sample` | Đo ECE trên chính tập đã hiệu chuẩn **(L04)** |
| `is_placeholder` | Bản tạm được báo cáo như bản thật |
| `exclude_order_ids` | Văn bản của gold set nằm trong tập huấn luyện cause head |
| `test_layering.py` | `capabilities/` · `core/` · `data/` import ngược lên `evaluation/` |
| `meta_path(gold)` | Đường dẫn meta đặt cứng khiến `--gold` không đổi được nguồn gốc **(L28)** |
| `test_data_entrypoint.py` | Nạp dữ liệu thô bỏ qua `load_split()` |
| Cổng **G5** | Số chaos vào luận văn khi kết quả chưa tái lập được |

---

## 9. ⚠️ Sáu giới hạn phải nêu ở Threats to Validity

1. **Accuracy thô thấp hơn mốc tầm thường** — 0,6902 so với 0,8726. Không dùng làm chỉ số chính; lý do
   đầy đủ ở §1.1.
2. **Tầng B *(đơn không có bình luận)* ngoài phạm vi.** Tình huống khó (b) của RQ3 vì vậy **không được
   kiểm định**, và `do_phu_tang_B` để trống.
3. **Vế *"toàn bộ bề mặt hỏng"* của H2 nằm ngoài phạm vi** — bốn thành phần riêng có không được guard
   phủ. Phát biểu H2 đã bị **thu hẹp sau khi thấy kết quả**; hồ sơ sửa đổi giữ nguyên văn bản gốc.
4. **Ràng buộc ngân sách tắt trong cấu hình báo cáo.** Hệ quả: `allocate()` suy biến thành hàm hằng,
   `REJECT_PROPOSAL` không bao giờ được phát, và pha 1 Contract Net tiêu tốn thông điệp mà **không
   quyết định gì**. Phản biện *"đây chỉ là ensemble gắn nhãn giao thức"* **đúng ở chiều phân bổ tài
   nguyên**.
5. **Encoder là TF-IDF, không phải BERTimbau.** Chi phí đo được của analyst văn bản là **1,3 ms** thay
   vì ~45 ms, nên ràng buộc ngân sách **yếu hơn thiết kế** ngay cả khi được bật.
6. **Hai khiếm khuyết cài đặt còn mở:** `monitoring_coverage` ghi `installed: false` cho
   `cause_quality` và `cause_service` — phạm vi giám sát chỉ phủ một phần bề mặt; và **`BidCalibrator`
   chưa được nối vào đường chạy chính**, nên Chương 4 **không được viết** *"bid đã được hiệu chuẩn"* —
   analyst khi đấu thầu vẫn phát điểm thô. Ngoài ra **mức fallback L1/L2 chưa cài**: thang suy giảm
   nhảy thẳng từ L0 sang L3.

### 9.1 Hai ràng buộc dữ liệu **không** được test nào canh

`C2` và `C4` được cưỡng chế bằng mã nguồn. Nhưng **`C1` *(không có biến treatment)* và `C3` *(kết cục
giao hàng không dùng để dự báo)* chỉ tồn tại dưới dạng chú thích rải rác** — không test nào canh chúng.

Không được trình bày như thể cả năm ràng buộc đều được cưỡng chế bằng mã. Với C1, hệ quả thực tế là:
**không có gì trong mã nguồn ngăn một phiên bản sau phát biểu về hiệu quả can thiệp.**

---

## 10. Chi tiết thống kê

| Thành phần | Giá trị |
|---|---|
| Bootstrap | **B = 1.000**, **percentile** *(không BCa)*, α = 0,05 ⟹ KTC 95% |
| Seed | `20260809`, đặt từ một nơi duy nhất qua `CONFIG.seed_everything()` |
| TOST | biên **0,01** khai báo trước, `t.ppf(1−α, df=n−1)` ⟹ khoảng 90% hai phía |
| McNemar | **nhị thức chính xác**, không dùng xấp xỉ chi-bình-phương *(số ô bất đồng thường rất nhỏ)* |
| Bootstrap chênh lệch macro-F1 | lấy mẫu lại **theo đơn, theo cặp** — hai hệ chấm trên cùng đơn nên phải lấy mẫu cùng nhau |
| Cỡ mẫu tối thiểu | κ cần **20** lượt dương · hiệu chuẩn cần **15** dương · PSI cần **100** quan sát |
| Hiệu chỉnh đa kiểm định | **không áp dụng** — chỉ có một kiểm định khẳng định; xem §0.3 |

⚠️ `bootstrap_ci` trong `forecasting.py` **bỏ qua** *(không thay thế)* mẫu bootstrap chỉ có một lớp, nên
số lần lặp hiệu dụng có thể nhỏ hơn 1.000 mà không được ghi lại. `bootstrap_macro_f1_diff` ghi
`n_boot_hieu_dung` để tránh vấn đề này.
