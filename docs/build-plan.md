# Kế hoạch thi công prototype — phân rã công việc

> **Nguồn:** [technical-plan-v3.md](technical-plan-v3.md) (kiến trúc, giao diện, lộ trình M0–M7) và
> [research-questions-objectives.md](research-questions-objectives.md) (RQ, MT, tiêu chí đánh giá).
>
> Tài liệu này chuyển kiến trúc thành **danh sách công việc có thể giao và nghiệm thu**. Mỗi công việc
> có đầu ra cụ thể, tiêu chí nghiệm thu kiểm tra được, phụ thuộc, và ước lượng ngày công.
>
> **Cách đưa vào mã nguồn:** [implementation-plan.md](implementation-plan.md) — bố trí `src-v3/` theo
> từng file, cấu hình packaging, và **bốn đợt triển khai** mở đầu bằng một *walking skeleton* để kiểm
> chứng sớm ba rủi ro lớn nhất.

---

## Trạng thái tiến độ

Cập nhật lần cuối: **13/08/2026** — sau đợt đổi mốc T₃, gỡ nhãn `price`, và đo đủ bốn ô của H2.

| WP | Trạng thái | Task đã xong | Còn lại |
|---|---|---|---|
| **WP0** — Nền tảng | ✅ **Xong** | T0.1 → T0.4 | — |
| **WP1** — Dữ liệu | ✅ **Xong** | T1.1 → T1.6 | — |
| **WP2** — Gold set | 🟢 **Bộ tạm đủ dùng** | T2.1, T2.2, T2.4, **T2.7 artifact + nguồn gốc** | **Gán 300 dòng `goldset_v2`** — 2 người độc lập. **Đường tới hạn** |
| **WP3** — Capabilities | 🟢 **~95%** | T3.1, T3.2, T3.5, T3.6, tín hiệu giao hàng, **T3.4 `TfidfCauseHead`** | T3.3 BERTimbau *(chặn: quyết định không cài `torch`)* |
| **WP4** — Baselines | ✅ **Xong** | T4.1 → T4.4 | — |
| **WP5** — Core + runtime | ✅ **Xong** | T5.1 → T5.7 | — |
| **WP6** — Agents + orchestrator | ✅ **Xong** | T6.1 → T6.8 | — |
| **WP7** — Contract Net | 🟡 **~85%** | Critic + Arbiter, T7.1, T7.2, T7.3a, T7.4 | **T7.3b hiệu chuẩn isotonic riêng từng analyst** *(chặn: gold set)* |
| **WP8** — Tầng chịu lỗi | ✅ **Xong** | T8.1 → T8.5 | — |
| **WP9** — Chaos | 🟢 **~85%** | T9.1, T9.2 đủ 5×3, T9.3 | **T9.4 test tái lập** — chưa chạy lại sau khi đổi mốc T₃ |
| **WP10** — Đánh giá | 🟢 **Xong T10.1 → T10.6** | Cả sáu; mọi số mang cờ `citable=False` cho tới khi có gold set thật | Chạy lại sau khi có bộ nhãn cuối |
| WP11 | ⬜ Chưa bắt đầu | — | — |

**Đã tiêu:** khoảng 58 ngày công / 82. **Kiểm chứng bằng: 274 test xanh (67 giây)** — `python -m pytest -q`.

> **Bảng này và `session-state.md` từng lệch nhau** *(WP7 "xong" ở đây, "85%" ở kia; 231 so với 274
> test)*. Đã đồng bộ theo số đo thật ngày 13/08. Khi hai tài liệu lệch, **`session-state.md` là bản
> mới hơn** — nó ghi việc đang làm, còn tài liệu này ghi phân rã công việc.

### Gate đã qua

| Gate | Kết quả |
|---|---|
| **G1** — thống kê khớp M0 | ✅ **Đạt.** Chi tiết ở §0.5 dưới đây |
| **G3** — mô hình rủi ro đủ tốt để có ý nghĩa nghiệp vụ | ✅ **Đạt.** Chi tiết ở §0.6 |
| **G4** (bản thu nhỏ, trên khung) | ✅ Trace dựng lại được chỉ từ `conversation_id` |
| **G5** (bản thu nhỏ, trên khung) | ⏳ **Phải chạy lại.** Đã đạt trước 12/08, nhưng chưa kiểm lại sau khi đổi mốc T₃ — xem T9.4 |
| **G2** — κ ≥ 0,6 | ⏳ **Chờ bộ nhãn cuối.** κ hiện tại không hợp lệ *(L26)*; công cụ đã sẵn: `check_validation` kiểm tính độc lập trước khi tính κ |

### Việc kế tiếp, theo thứ tự

1. **Gán 300 dòng `goldset_v2_A.csv` / `_B.csv`** — hai người độc lập. Đây là **đường tới hạn**: T7.3b,
   T10.2, T10.3 và toàn bộ RQ3 đều chờ nó.
2. **Mở guard sang 4 thành phần chỉ-MAS** — đây là **cải tiến thiết kế** *(sửa DP1 hoặc thêm DP mới)*,
   **không** phải sửa H2. Đo lại rồi báo cáo **cạnh** kết quả hiện tại, không thay thế.
3. **T9.4** — test tái lập chaos, và chạy lại Gate G5 sau khi đổi mốc T₃.
4. **IMP-4 → IMP-7** trong `methodology-log.md` — bốn biện pháp còn lại, ~2,5 ngày.
5. **WP11** — dựng bảng số Chương 5 từ các CSV đã sinh.
6. **T3.3 BERTimbau** nếu quyết định cài `torch` — không cần nhãn nào, nên làm được bất cứ lúc nào; và
   nó sẽ **khôi phục ràng buộc ngân sách** của Contract Net vốn đang yếu vì cause head quá rẻ.

---

## Phần 0 — Quy ước và giả định

### 0.1 Đơn vị ước lượng

Ước lượng theo **ngày công** (person-day) — một ngày làm việc tập trung khoảng 6 giờ hiệu quả. Tổng
khối lượng khoảng **80 ngày công**, tương đương **16 tuần** nếu làm 5 ngày/tuần, hoặc **7–8 tháng** nếu
làm bán thời gian 2–3 ngày/tuần. §7 nêu đường cắt giảm xuống còn ~55 ngày công nếu tiến độ không kịp.

Ước lượng đã tính cả thời gian viết test, **không** tính thời gian viết luận văn.

### 0.2 Định nghĩa "xong"

Một công việc chỉ được coi là xong khi đủ **bốn** điều kiện:

1. Mã nguồn chạy được và có test bao phủ đường chính.
2. Tiêu chí nghiệm thu ở cột tương ứng được thỏa mãn, kiểm tra được bằng lệnh chạy.
3. Không vi phạm bốn kỷ luật kỹ thuật ở `technical-plan-v3.md §8`.
4. Kết quả tái lập: chạy hai lần cùng cấu hình cho cùng đầu ra.

### 0.3 Hai luồng chạy song song

| Luồng | Nội dung | Ràng buộc |
|---|---|---|
| **Luồng A — Mã nguồn** | WP0 → WP11, tuần tự theo phụ thuộc | Chiếm phần lớn ngày công |
| **Luồng B — Gold set** | WP2, khởi động **từ tuần 1** và chạy suốt | Là **đường tới hạn thật**: nó phụ thuộc vào thời gian của con người, không rút ngắn được bằng cách làm nhanh hơn |

Sai lầm phổ biến nhất và cũng nguy hiểm nhất: để luồng B đến cuối mới bắt đầu. Khi đó nếu κ thấp thì
không còn thời gian sửa codebook và gán lại.

### 0.4 Sơ đồ phụ thuộc giữa các gói công việc

```
WP0 nền tảng
 └─▶ WP1 dữ liệu ──┬──▶ WP3 capabilities ──┬──▶ WP4 baselines ──┐
                   │                        │                    │
                   └──▶ WP2 gold set ───────┘                    │
                        (luồng song song)                        │
                                                                  ▼
        WP5 core + runtime ──▶ WP6 agents + orchestrator ──▶ WP7 contract net
                                                                  │
                                                                  ▼
                                             WP8 reliability ──▶ WP9 chaos
                                                                  │
                                                                  ▼
                                                          WP10 evaluation
                                                                  │
                                                                  ▼
                                                    WP11 kết quả Chương 5
```

**Đường tới hạn:** WP0 → WP1 → WP3 → WP5 → WP6 → WP8 → WP9 → WP10 → WP11, chạy song song với WP2.

### 0.5 Gate G1 — đối chiếu với bảng M0 *(đã chạy trên dữ liệu thật)*

Bảng M0 đếm trên **dòng đánh giá thô**. Bảng đơn hàng chuẩn hóa đếm trên **case đơn hàng** — đơn vị
phân tích thật của nghiên cứu. Chênh lệch được giải thích trọn vẹn, không còn phần dư nào:

| Chỉ tiêu | M0 *(dòng đánh giá)* | Bảng chuẩn hóa *(case đơn hàng)* | Giải thích chênh lệch |
|---|---|---|---|
| Số đánh giá | 99.224 | **98.673** | 551 đơn có nhiều hơn một bản ghi đánh giá; khử trùng giữ bản sớm nhất |
| Bất mãn (1–2★) | 14.575 — 14,69% | **14.475 — 14,67%** | Cùng nguyên nhân khử trùng |
| Tầng A — có `review_content` | 10.889 — 74,71% | **10.823 — 74,77%** | Tỷ lệ **khớp** |
| Tầng B — không có `review_content` | *(suy ra)* 3.686 | **3.652 — 25,23%** | — |
| Không một chữ nào *(kể cả tiêu đề)* | 3.581 — 24,6% | **3.547 — 24,50%** | — |

Không đánh giá nào bị mất do ghép bảng (0 bản ghi không khớp `order_id`). Sai lệch lớn nhất là **0,56%**,
dưới ngưỡng dừng 1% → **Gate G1 đạt**.

**Một đính chính cần mang vào Chương 5.** Cặp số "74,71% / 24,6%" ở các bản tài liệu trước trộn hai
định nghĩa khác nhau: 74,71% tính theo `review_content`, còn 24,6% tính theo *không có cả nội dung lẫn
tiêu đề*. Hai con số này không bù nhau. Định nghĩa thống nhất được chốt là **theo `review_content`**,
nên cặp đúng là **74,77% / 25,23%**, và 24,50% được báo cáo riêng như một chỉ tiêu phụ.

Phân bố hình chữ U tái lập chính xác: 1★ 76,60% · 2★ 68,13% · 3★ 43,58% · 4★ 31,22% · **5★ 35,86%**.

> ## ⛔ §0.6 → §0.10 là HỒ SƠ CÁC LƯỢT CHẠY TRƯỚC 12/08 — KHÔNG TRÍCH SỐ VÀO LUẬN VĂN
>
> Giữ nguyên văn làm hồ sơ quá trình *(Design Science: việc phát hiện và sửa lỗi thiết kế là một phần
> của đóng góp)*. Nhưng **bốn thay đổi ngày 12/08 làm mọi con số dưới đây hết hiệu lực**:
>
> | Thay đổi | Làm hỏng số nào |
> |---|---|
> | **T₃ = ngày mua + 7** *(trước: hạn dự kiến + 3)* | mốc cũ đặt T₃ **sau** T₄ với 97,6% đơn ⟹ mọi số dự báo ở §0.6 và §0.10-T10.1 đo trên cấu hình hỏng |
> | **`PriceAnalyst` và nhãn `price` bị gỡ** | §0.7 trace mẫu, §0.9 dòng `cause_price`, và **§0.10 mọi chỉ số phối hợp** — 22,89 message/case và 4,00 bản khai/case đo trên cấu hình **bốn** analyst |
> | **`LexiconCauseHead` → `TfidfCauseHead`** | §0.7 tỷ lệ quy kết 30,7%; §0.9 hai dòng `cause_quality`/`cause_service` bằng 0 |
> | **Sửa cách đếm hỏng âm thầm (L37)** | §0.8 — đối chứng **có** điền `failed_steps` mà phép đếm bỏ qua; *"Mono hỏng âm thầm 30,7%"* thực ra là **0,0%** |
>
> **Số hiện hành nằm ở [session-state.md](session-state.md) §"Số hiện hành".** Sinh lại toàn bộ bằng
> `python -m masdss.cli.run_evaluation --run data/v3/runs/cnp`.
>
> *(§0.5 **không** thuộc phạm vi cảnh báo này — nó là thống kê mô tả dữ liệu, không phụ thuộc mốc T₃.)*

### 0.6 Gate G3 — mô hình rủi ro *(đã huấn luyện trên dữ liệu thật)* ⛔ *số đã hết hiệu lực*

Chia tập theo thời gian: train 69.071 · val 14.801 · test 14.801.

| Chỉ số | val *(in-sample)* | **test** *(dùng để báo cáo)* |
|---|---|---|
| PR-AUC — chính | 0,4123 | **0,3993** |
| ROC-AUC — phụ | 0,7464 | **0,7281** |
| Brier trước → sau hiệu chuẩn | 0,0858 → 0,0843 | **0,0791 → 0,0789** |
| ECE trước → sau hiệu chuẩn | 0,0132 → 0,0000 ⚠️ | **0,0133 → 0,0072** |

PR-AUC 0,3993 trên nền tỷ lệ dương 14,67% là **lift ≈ 2,7 lần** — đủ ý nghĩa nghiệp vụ để đi tiếp.

> ⚠️ **Một cái bẫy đã tránh được, cần nhớ khi viết Chương 5.** ECE sau hiệu chuẩn trên tập val bằng
> 0,0000 **không phải** thành tích: bộ hiệu chuẩn isotonic được khớp trên chính tập đó, nên con số ấy
> là in-sample và vô nghĩa. Con số dùng để báo cáo là **0,0133 → 0,0072 trên tập test** — cải thiện
> khoảng 46%. `CalibrationReport` có trường `in_sample` gắn nhãn `[IN-SAMPLE]` vào tên chỉ số để không
> ai trích nhầm về sau.

**Kết quả phụ, đều là số thật:**

| Hạng mục | Kết quả |
|---|---|
| Price Analyst | 58/72 nhóm hàng đủ điều kiện z-score → **`REFUSE` trên 19,4% nhóm hàng**. Đây là DP3 vận hành, không phải câu từ chối cho có |
| Bộ phát hiện OOD | train 1,00% · test 1,11% · nhiễu loạn 1σ **2,68%** · 2σ **3,95%** · 4σ **99,23%** |

Đường cong OOD là **kết quả thực nghiệm chưa biết trước**, đúng loại bằng chứng RQ1 cần: bộ phát hiện
chỉ bắt chắc nhiễu loạn lớn, còn ở mức 1–2σ độ nhạy rất thấp. Đây là số liệu nền để so với đường cong
độ nhạy của output guard ở WP8, và phải được báo cáo trung thực chứ không giấu.

### 0.7 Chạy thử giai đoạn 2 @ T₄ trên 300 đơn bất mãn *(tập test)* ⛔ *số đã hết hiệu lực*

| Chỉ tiêu | MAS-DSS | Monolithic-Complete |
|---|---|---|
| Quy kết được ít nhất một nguyên nhân | 92 (30,7%) | 92 |
| Đa nguyên nhân | 6 | 6 |
| Không quy kết được → chuyển giao | 208 (69,3%) | — *(không có khái niệm)* |
| Hỏng âm thầm khi tiêm lỗi | 0 | **chưa đo được** |

**Ba phát hiện, mỗi cái là một lỗi thiết kế đã sửa:**

1. **Cổng rủi ro chặn nhầm việc quy kết nguyên nhân.** Bản đầu của `STAGE2_PLAN` chỉ mở phiên đấu thầu
   khi `risk >= MEDIUM`. Nhưng tại T₄ đơn **đã có** đánh giá 1–2★ — sự bất mãn là sự kiện đã xảy ra,
   không còn là thứ cần dự báo. Chặn quy kết sau một dự báo PR-AUC 0,40 khiến **94,7% số case không bao
   giờ được phân tích**, và RQ3 mất đối tượng nghiên cứu. Đã bỏ cổng; ngân sách tính toán vẫn thay đổi
   theo mức rủi ro nên Contract Net không mất tính phân bổ tài nguyên. "Đường tắt cho case rủi ro thấp"
   thuộc **giai đoạn 1 @ T₃** — nơi hệ thống thực sự đang dự báo.

2. **Luật sinh ra `no_action` ở T₄ dù đã tìm ra nguyên nhân.** Luật `low_risk_default` chỉ ràng buộc
   `risk == 0`, nên một đơn có nguyên nhân giao hàng rõ ràng nhưng điểm rủi ro thấp lại rơi vào "không
   can thiệp". Đã thêm ràng buộc `n_causes == 0`: **đã quy kết được nguyên nhân thì không được phép
   không làm gì**, bất kể điểm dự báo.

3. **Tỷ lệ hỏng âm thầm của Monolithic hiện CHƯA phải kết quả.** Bộ tiêm lỗi cắm vào seam
   `runtime/faults.py`, mà seam đó chỉ bao bọc lời gọi **tác tử**. Monolithic gọi capability trực tiếp
   nên không đi qua đó. Con số 0% vì vậy chỉ nói rằng nó *chưa bị tiêm lỗi*, không nói gì về khả năng
   chịu lỗi. Việc cho hai kiến trúc chịu **cùng một kịch bản lỗi** là **T9.3**, và cho tới lúc đó không
   được trích con số này. CLI đã in cảnh báo tại chỗ để tránh trích nhầm.

**Tỷ lệ không quy kết được 69,3% là do `LexiconCauseHead` — bản tạm thời.** Bộ từ khóa không được kiểm
định có recall thấp đúng như dự đoán. Con số này sẽ đổi khi T3.4 (BERTimbau + head đa nhãn) hoàn thành,
và **không được đưa vào Chương 5** ở dạng hiện tại. Thuộc tính `is_placeholder = True` tồn tại để ràng
buộc đó kiểm tra được bằng mã nguồn.

Một trace thật, cho thấy chuỗi phối hợp đầy đủ trên một case tầng A:

```
Orchestrator -> Analytics       [REQUEST]  buoc 'analytics'
  Analytics -> Orchestrator     [INFORM]   context
Orchestrator -> Prediction      [REQUEST]  buoc 'prediction'
  Prediction -> Orchestrator    [INFORM]   risk, risk_score
Orchestrator -> DeliveryAnalyst [REQUEST]  buoc 'contract_net'
  DeliveryAnalyst               [PROPOSE]  bid delivery conf=0.463 cost=0.3ms
Orchestrator -> PriceAnalyst    [REQUEST]  buoc 'contract_net'
  PriceAnalyst                  [REFUSE]   khong tim thay bang chung vuot nguong
Orchestrator -> QualityAnalyst  [REQUEST]  buoc 'contract_net'
  QualityAnalyst                [PROPOSE]  bid quality conf=0.550 cost=0.4ms
Orchestrator -> ServiceAnalyst  [REQUEST]  buoc 'contract_net'
  ServiceAnalyst                [REFUSE]   van ban khong co tin hieu service
Orchestrator -> Recommendation  [REQUEST]  buoc 'recommend'
  Recommendation                [INFORM]   proposal
Orchestrator -> PolicyCritic    [REQUEST]  buoc 'critique'
  PolicyCritic                  [CHALLENGE] challenged, violated
Orchestrator -> Arbiter         [REQUEST]  buoc 'arbitrate'
  Arbiter                       [INFORM]   sided_with=critic, override=escalate
Orchestrator -> RuleAgent       [REQUEST]  buoc 'rules'
  RuleAgent                     [INFORM]   action, rule_id, reason
```

Đây là bằng chứng vận hành cho RQ2: hai analyst đấu thầu kèm bằng chứng, hai analyst từ chối với lý do
kiểm chứng được, Critic phản biện, Arbiter phân xử — và toàn bộ dựng lại được **chỉ từ nhật ký message**.

### 0.8 WP8 — kết quả tầng chịu lỗi *(300 đơn bất mãn, tập test)* ⛔ *số đã hết hiệu lực — xem L37*

Cùng kịch bản lỗi áp lên cả hai kiến trúc qua định danh **thành phần logic** (T9.3).

| Kịch bản | MAS-DSS suy giảm | **MAS-DSS hỏng âm thầm** | **Monolithic hỏng âm thầm** | Độ trễ phát hiện |
|---|---|---|---|---|
| *(không tiêm lỗi)* | **0 / 300** | — *(không có lỗi)* | — | — |
| `crash:prediction` | 300 / 300 | **0,0%** | **30,7%** | tức thì *(exception)* |
| `transient:prediction` | 300 / 300 | **0,0%** | **30,7%** | tức thì |
| `constant` — Byzantine thô | 281 / 300 | **0,7%** | **30,7%** | **20 quan sát** |
| `bias +0,15` — Byzantine tinh vi | 198 / 300 | **6,0%** | **30,7%** | **100 quan sát** |

**Tỷ lệ báo động giả trên lượt chạy khỏe: 0/300.**

Trước WP8, MAS-DSS hỏng âm thầm **18,0%** dưới lỗi Byzantine. Con số "trước" đó được đo *trước khi*
xây guard, nên mức giảm 18,0% → 0,7% / 6,0% là **đóng góp đo được của tầng chịu lỗi**, chứng minh bằng
thực nghiệm chứ không phải theo cấu tạo.

Gradient độ nhạy là kết quả thật, không biết trước: crash bắt tức thì, Byzantine thô sau 20 quan sát,
Byzantine tinh vi sau 100 quan sát và vẫn còn 6% rò rỉ.

#### Bốn lỗi phương pháp phát hiện khi xây WP8

Cả bốn đều làm guard *có vẻ* hoạt động trong khi thực ra vô dụng. Chúng đáng viết vào Chương 5 vì đây
là những cái bẫy mà bất kỳ ai xây bộ giám sát drift cũng sẽ gặp.

| # | Lỗi | Triệu chứng | Sửa |
|---|---|---|---|
| 1 | **Cảnh báo chỉ phát một lần** | Guard chặn đúng case đầu tiên rồi im; 299 case sau hỏng âm thầm y nguyên. Silent failure chỉ giảm 18,0% → 17,7% | Tách *cảnh báo* (một lần, để đo độ trễ) khỏi *trạng thái sức khỏe* (bền vững, chặn cho tới khi khôi phục) |
| 2 | **Phương sai bằng 0 bị coi là bằng chứng hỏng** | `LexiconCauseHead` trả hằng số **do thiết kế** → bị đánh dấu hỏng → **93,7% báo động giả** trên lượt chạy khỏe | Phép kiểm tra chỉ áp dụng khi có tham chiếu chứng tỏ đại lượng *đáng lẽ phải biến thiên* |
| 3 | **Tham chiếu PSI lấy sai tổng thể** | Tham chiếu từ *toàn bộ* val, luồng giám sát chỉ có đơn *bất mãn* → PSI = 0,807 trên dữ liệu hoàn toàn khỏe | Tham chiếu phải lấy từ **cùng một tổng thể** với luồng được giám sát |
| 4 | **PSI trên cửa sổ nhỏ, khoảng chia cố định** | 50 quan sát trên 10 khoảng đều nhau → PSI = **2,911** trên dữ liệu khỏe. Bất ổn mẫu nhỏ, không phải drift | Chia khoảng theo **phân vị của tham chiếu**; yêu cầu ≥ 100 quan sát; chặn dưới theo cỡ mẫu |

**Ngưỡng PSI được hiệu chuẩn, không lấy theo quy ước.** Quy ước ngành là 0,25; ngưỡng đó cho 66% báo
động giả ở đây vì giữa val và test có dịch chuyển tổng thể theo thời gian thật. Quy trình hiệu chuẩn:
chạy khỏe → PSI = 0,466; chạy có lệch hệ thống → PSI = 2,512; đặt ngưỡng ở giữa → **1,0**. Đây không
phải vòng tròn: ngưỡng chọn từ đường chạy *khỏe*, rồi đo độ nhạy trên các đường *có lỗi*.

#### Giới hạn phủ của bộ giám sát — đã thu hẹp ở T7.3a *(xem §0.9)*

Ngay sau WP8, guard chỉ phủ được **một** thành phần (`prediction`) vì đó là thành phần duy nhất có
phân phối tham chiếu sạch. T7.3a đã mở rộng lên **hai**, và ghi rõ lý do từ chối ba thành phần còn lại.

### 0.9 T7.3a — mở rộng phạm vi giám sát sang nhóm Analyst ⛔ *số đã hết hiệu lực*

**Tách phần không bị chặn.** T7.3 đầy đủ (hiệu chuẩn isotonic từng analyst, báo cáo ECE trước/sau) cần
gold set — chưa có. Nhưng thứ *thực sự* mở khóa giám sát không phải hiệu chuẩn mà là **phân phối tham
chiếu**, và cái đó **không cần nhãn nào**: chỉ cần chạy từng signal trên tập train và ghi lại phân bố
độ tin cậy.

| Thành phần | Giám sát? | n mẫu | Lý do |
|---|---|---|---|
| `prediction` | ✅ | 1.749 | Đã nạp tham chiếu |
| `cause_delivery` | ✅ | 457 | Đã nạp tham chiếu |
| `cause_price` | ❌ | 153 | Dưới ngưỡng 200 mẫu |
| `cause_quality` | ❌ | 0 | `cause_head` là bản tạm trả hằng số — chờ T3.4 |
| `cause_service` | ❌ | 0 | Cùng lý do |

**Phủ 2/5, và ba lần từ chối đều có lý do cụ thể.** Báo cáo phạm vi phủ này phải đi kèm mọi con số
RQ1(b) trong Chương 5: một bộ giám sát chỉ phủ được một phần hệ thống thì kết quả độ nhạy chỉ nói về
phần đó.

**Kết quả mới trên thành phần vừa được phủ:**

| Kịch bản | Trước T7.3a | Sau T7.3a |
|---|---|---|
| `constant:cause_delivery` | không phát hiện | **phát hiện sau 20 quan sát** |
| `bias:cause_delivery` *(300 case)* | không phát hiện | vẫn không — chỉ có ~45 quan sát |
| `bias:cause_delivery` *(1.200 case)* | không phát hiện | **phát hiện sau 100 quan sát**, PSI = 1,206 |

**Một phát hiện định lượng mới về độ trễ phát hiện.** `DeliveryAnalyst` chỉ phát bid trên khoảng 15%
số case, nên 100 quan sát của *thành phần* tương đương khoảng **670 case** của *hệ thống*. Độ trễ phát
hiện vì vậy **tỷ lệ nghịch với tần suất kích hoạt** của thành phần — thành phần càng ít nói, càng lâu
mới phát hiện được nó nói sai. Đây là kết quả chưa biết trước và nên đưa vào Chương 5.

Ba ràng buộc khi dựng tham chiếu, cả ba là bài học trực tiếp từ `methodology-log.md`:
khớp tổng thể *(L15)* · chỉ lấy bid đã phát, không lấy lần trả 0 *(L15)* · từ chối khi tham chiếu quá
ít mẫu hoặc gần như hằng số *(L14)*.

#### Một chi tiết kiến trúc đáng ghi nhận

Toàn bộ tầng chịu lỗi cắm vào hệ thống mà **không sửa một dòng nào trong `orchestrator.py`**. Lý do:
`GuardViolation` kế thừa `DeterministicError`, mà orchestrator đã có sẵn chính sách cho loại lỗi đó —
hạ hai bậc suy giảm và đi tiếp. Nhờ vậy bật/tắt tầng chịu lỗi là **một tham số** (`--no-reliability`),
không phải một nhánh mã nguồn, và đường ablation cho RQ1 là một lần đổi cấu hình.

### 0.10 T10.1 · T10.4 · T10.6 — ba nhóm chỉ số **không cần gold set** ⛔ *số đã hết hiệu lực*

Ba nhóm này chạy được ngay trong khi vòng gán nhãn còn dang dở, nên chúng được làm trước.
Một lệnh sinh toàn bộ: `python -m masdss.cli.run_evaluation --run data/v3/runs/cnp`.

**T10.1 — dự báo (RQ3 *điều kiện kiểm soát*, H1).** Điều kiện kiểm soát **đã kiểm chứng**: hai kiến trúc cho
điểm dự báo giống nhau từng bit. Nó được ghi rõ là *kiểm tra đặc tả*, không phải kết quả
thực nghiệm — TOST trên hai dãy số giống hệt nhau là tautology *(xem L23 về lần nó suýt
báo sai)*.

| Chỉ số | Giá trị | KTC 95% |
|---|---|---|
| PR-AUC *(chính)* | 0,3993 | [0,3754 ; 0,4246] |
| ROC-AUC *(phụ)* | 0,7281 | [0,7129 ; 0,7438] |
| tỷ lệ dương (nền) | 0,1099 | — |
| **lift trên nền** | **3,63×** | — |

Hai điểm phải nêu trong Chương 5. **(a) Độ nhạy ngưỡng nhãn:** `rating ≤ 3` cho PR-AUC
cao hơn (0,4249) nhưng ROC-AUC thấp hơn (0,6758) — kết luận không đảo chiều theo lựa chọn
ngưỡng, và đó là điều cần chứng minh chứ không phải khẳng định suông. **(b) Ngưỡng quyết
định theo chi phí là 0,167, không phải 0,5** — mặc định 0,5 ngầm giả định hai loại sai giá
bằng nhau và lớp cân bằng, cả hai đều sai ở đây.

Tỷ lệ dương trên tập test là **10,99%**, thấp hơn mức 14,67% của toàn bộ; tập test nằm ở
cuối trục thời gian nên chênh lệch này tự nó là một quan sát về **dịch chuyển theo thời
gian**, cần nhắc khi diễn giải PR-AUC.

**T10.4 — phối hợp (RQ3).** Mọi chỉ số tính **từ nhật ký message**, không cắm thêm đường
đo nào — đó là hệ quả kiểm chứng được của DP4. Báo cáo cả hai vế:

| Cái giá | | Lợi ích | |
|---|---|---|---|
| message / case | 22,89 | bản khai / case *(pha 1)* | 4,00 |
| chi phí điều phối / case | 9,50 ms | bid thật / case *(pha 2)* | 0,30 |
| độ sâu cây hội thoại | 1,00 | `bid_entropy` TB *(case ≥2 bid)* | 0,9894 |
| | | REFUSE / case | 3,23 |

Ba điều đáng nói. **(a) Độ sâu bằng 1 là hệ quả của thiết kế**, không phải phát hiện: mọi
trao đổi đều qua orchestrator nên cây hội thoại có dạng hình sao. Nêu như đặc điểm kiến
trúc, không nêu như chỉ số. **(b) `bid_entropy` ≈ 0,99** — khi có từ hai analyst cùng phát
bid thì chúng gần như tự tin ngang nhau, đúng tình huống (a) của RQ3 mà `argmax` của một
bộ phân loại đơn khối sẽ xóa mất; nhưng cỡ mẫu nhỏ *(chỉ 1,5% số đơn đa nguyên nhân)* nên
đây mới là **chỉ dấu**, chưa phải bằng chứng.

**(c) Một giới hạn thiết kế lộ ra từ chính con số này — 4,00 bản khai nhưng chỉ 0,30 bid
thật.** Ở pha 1 của Contract Net, analyst khai "có bằng chứng", nhưng `expected_confidence`
trong bản khai là một **tiên nghiệm của tổng thể**, không phải ước lượng cho *đơn hàng cụ
thể này*. Vì vậy khai "tôi *có thể* tìm" chứ không phải "tôi *sẽ* tìm ra", và phần lớn
analyst được cấp ngân sách rồi vẫn REFUSE ở pha 2. Hệ quả: bài toán phân bổ đang tối ưu
trên một tín hiệu yếu. Đây là **giới hạn phải nêu ở Threats to Validity**, và hướng cải
tiến rõ ràng là một proxy rẻ tính theo từng case ở pha 1.

Chỉ số *quy kết / ms* = 0,0321 **không được trích vào Chương 5 ở dạng hiện tại**: nó đếm
**số** nguyên nhân, không đo **độ đúng**; một hệ thống quy kết bừa sẽ ăn điểm cao. Chỉ số
thật cần gold set (T10.2).

**T10.6 — cái giá của kiến trúc (H5, khai báo trước là *kỳ vọng thua*).**

| | MAS-DSS | Monolithic |
|---|---|---|
| ms / case | 9,50 | 8,90 |
| p50 / p95 mỗi lời gọi | 0,15 / 7,39 ms | — |
| dòng mã tầng chịu lỗi | **448** *(6 module)* | 0 |
| dòng mã tầng phối hợp | **632** *(9 module)* | 0 |
| số tác tử · loại message · tầng | 11 · 10 · 5 | 0 · 0 · 2 |

Overhead độ trễ **+6,7%** — nhỏ hơn dự kiến, nhưng cái giá thật nằm ở **1.080 dòng mã**
tồn tại chỉ để chịu lỗi và phối hợp. Đó là con số trả lời câu hỏi *"phải viết thêm bao
nhiêu để có được tỷ lệ hỏng âm thầm 0%"*. Số dòng đếm bằng `ast`, đã loại docstring —
*(xem L24: bản đếm đầu tiên hụt ~26%, và hụt đúng theo hướng làm artifact trông rẻ hơn)*.

**Còn bị chặn bởi gold set:** T10.2 *(macro-F1 quy kết)*, T10.3 *(selective prediction)*.

---

## WP0 — Nền tảng dự án · 2 ngày công

Không có gì thú vị, nhưng bỏ qua thì bốn kỷ luật kỹ thuật không cưỡng chế được và mọi thứ sau đó trôi.

| ID | Công việc | Đầu ra | Tiêu chí nghiệm thu | Ngày |
|---|---|---|---|---|
| ✅ T0.1 | Khởi tạo repo, `pyproject.toml`, ghim phiên bản mọi phụ thuộc | Cây thư mục theo `technical-plan-v3.md §4` | `pip install -e .` chạy sạch trên máy trống | 0.5 |
| ✅ T0.2 | Module cấu hình tập trung + quản lý seed toàn cục | `masdss/config.py` | Mọi nguồn ngẫu nhiên (numpy, sklearn, torch, injector) nhận seed từ một chỗ | 0.5 |
| ✅ T0.3 | Khung test + **test đồ thị phụ thuộc** | `tests-v3/test_layering.py` | Test **thất bại** khi `capabilities/` import bất cứ thứ gì từ `agents/`, `system/`, `chaos/` | 0.5 |
| ✅ T0.4 | Kiểm tra tính tất định | `tests-v3/test_determinism.py` | Chạy hai lần cùng cấu hình → hai tệp đầu ra giống nhau đến từng byte | 0.5 |

> T0.3 và T0.4 phải làm **trước** khi có mã nghiệp vụ. Thêm chúng vào sau thì luôn phát hiện ra vi phạm
> đã tồn tại và phải sửa ngược.

---

## WP1 — Tầng dữ liệu · 4 ngày công · *phụ thuộc WP0*

| ID | Công việc | Đầu ra | Tiêu chí nghiệm thu | Ngày |
|---|---|---|---|---|
| ✅ T1.1 | Nạp và ghép 9 bảng Olist thành bảng đơn hàng chuẩn hóa | `data/load.py`, parquet trung gian | Thống kê khớp bảng M0 trong sai số 1% — xem §0.5 | 1 |
| ✅ T1.2 | Khai báo đặc trưng kèm `available_at ∈ {T1,T2,T3,T4}` | `data/features.py` | **Mọi** cột đều có `available_at`; không cột nào thiếu | 1 |
| ✅ T1.3 | `FeatureSet(decision_point)` lọc theo mốc | `data/featureset.py` | `FeatureSet("T3")` không chứa cột nào có `available_at="T4"` | 0.5 |
| ✅ T1.4 | **Test chống rò rỉ** | `tests-v3/test_leakage.py` | Test thất bại nếu `review_lag_days` tồn tại, hoặc `has_comment` lọt vào T₂/T₃ | 0.5 |
| ✅ T1.5 | Nhãn bất mãn + weak label nguyên nhân *(chỉ để pre-train)* | `data/labels.py` | Weak label được đánh dấu bằng kiểu riêng để `evaluation/` từ chối nhận | 0.5 |
| ✅ T1.6 | Chia tập **theo thời gian**, không ngẫu nhiên | `data/splits.py` | Không đơn hàng nào ở tập train có ngày đặt sau đơn sớm nhất của tập test | 0.5 |

**Gate G1 — sau WP1.** Thống kê mô tả trên tập đã dựng phải khớp bảng M0 ở `technical-plan-v3.md §0`.
Lệch quá 1% thì dừng lại tìm nguyên nhân trước khi đi tiếp.

---

## WP2 — Gold set · 3 ngày công xây + 5 ngày công gán nhãn · *luồng song song, bắt đầu tuần 1*

Đây là **đường tới hạn thật của toàn bộ luận văn**. Không có nó thì RQ3 không trả lời được và Chương 5
mất phần lớn giá trị.

| ID | Công việc | Đầu ra | Tiêu chí nghiệm thu | Ngày |
|---|---|---|---|---|
| ✅ T2.1 | Bộ lấy mẫu phân tầng **không cân xứng 250 tầng A / 150 tầng B** | `goldset/sample.py` | Mẫu phủ đủ ba chiều: tầng A/B × nhóm hàng × mức trễ; có seed cố định | 1 |
| ✅ T2.2 | **Codebook** định nghĩa 4 nguyên nhân, quy tắc đa nhãn, ví dụ biên | `docs/codebook.md` | Có ít nhất 3 ví dụ biên cho mỗi nguyên nhân, gồm cả trường hợp đa nhãn và trường hợp không quy kết được | 1 |
| ⬜ T2.3 | ~~Giao diện gán nhãn tối giản~~ — **không xây** | — | Thay bằng gán nhãn trên CSV/Google Sheets: `build_annotation_en` sinh tệp, `freeze_translations` đóng băng bản dịch có checksum, `check_goldset` kiểm | 0.5 |
| ✅ T2.4 | Script tính Cohen's κ và đo độ nhiễu weak label | `goldset/agreement.py`, `goldset/weak_noise.py` | Xuất được κ tổng và κ theo từng nguyên nhân | 0.5 |
| T2.5 | **Gán nhãn vòng thử — 30 đơn**, hai người | Kết quả κ thử | κ thử tính được; nếu < 0.6 thì **sửa codebook rồi gán lại**, không đi tiếp | 0.5 |
| T2.6 | Gán nhãn chính thức 400 đơn, hai người độc lập | `data/gold/*.parquet` | Hoàn tất 100% mẫu; báo cáo κ chính thức | 4 |
| T2.7 | Đối chiếu bất đồng và chốt nhãn cuối | Gold set đã chốt | Mọi bất đồng đều được ghi lại, không im lặng ghi đè | 0.5 |

**Gate G2 — sau T2.5.** Nếu κ thử < 0.6, vấn đề nằm ở **định nghĩa nguyên nhân**, không phải ở người gán.
Sửa codebook và làm lại vòng thử. Đây cũng là một phát hiện đáng viết vào Chương 5.

**Rào cản tiếng Bồ:** dùng dịch máy cho toàn bộ, và nhờ một người biết tiếng Bồ kiểm chứng chéo 50 mẫu
dịch. Ghi rõ vào Threats to Validity. Phương án thay thế: thuê một annotator biết tiếng Bồ cho 400 mẫu.

---

## WP3 — Tầng capabilities · 11 ngày công · *phụ thuộc WP1*

Tầng này **dùng chung** giữa MAS-DSS và mọi baseline. Không import gì từ `agents/` hay `system/`.

| ID | Công việc | Đầu ra | Tiêu chí nghiệm thu | Ngày |
|---|---|---|---|---|
| ✅ T3.1 | Mô hình rủi ro LightGBM + hiệu chuẩn isotonic | `capabilities/risk_model.py` | Báo cáo PR-AUC, ROC-AUC, **ECE trước và sau hiệu chuẩn** trên tập validation | 2 |
| ✅ T3.2 | Bộ phát hiện ngoài phân phối | `capabilities/ood.py` | Trên dữ liệu nhiễu loạn nhân tạo, tỷ lệ phát hiện cao hơn rõ rệt so với dữ liệu bình thường | 1 |
| ⬜ T3.3 | BERTimbau encoder đóng băng + **đệm embedding ra đĩa** | `capabilities/text_encoder.py` *(chưa tồn tại)* | **Chặn bởi quyết định không cài `torch`.** Thay thế đang dùng: `TfidfCauseHead` — macro-F1 0,4730 so với 0,2196 của bản lexicon | 2 |
| T3.4 | Head phân loại **đa nhãn** 4 nguyên nhân | `capabilities/cause_head.py` | Đầu ra 4 sigmoid độc lập; pre-train bằng weak label, tinh chỉnh và đánh giá trên gold set | 3 |
| ✅ T3.5 | Tín hiệu giá: z-score theo nhóm hàng | `capabilities/price_signal.py` | Trả `REFUSE` khi nhóm hàng có dưới N mẫu | 1 |
| ✅ T3.6 | Rule engine đọc YAML + tập hành động phục hồi dịch vụ | `capabilities/rules.py`, `config/rules.yaml` | Không còn `expedite_shipment`; có đủ 7 hành động theo `technical-plan-v3.md §A.9` | 2 |

**Gate G3 — sau WP3.** Nếu PR-AUC của mô hình rủi ro quá thấp để có ý nghĩa nghiệp vụ, phải xử lý ngay
ở đây — mọi thứ phía sau đều đứng trên nó. T3.4 chỉ hoàn tất được khi WP2 có ít nhất một phần gold set.

---

## WP4 — Baselines · 4 ngày công · *phụ thuộc WP3*

Xây **trước** hệ MAS-DSS. Lý do: baseline dùng chung capabilities, nên xây trước sẽ ép tầng
`capabilities/` phải thật sự độc lập với tầng agent ngay từ đầu.

| ID | Công việc | Đầu ra | Tiêu chí nghiệm thu | Ngày |
|---|---|---|---|---|
| ✅ T4.1 | MIS — báo cáo mô tả theo ngưỡng | `baselines/simple.py::MISBaseline` | Sinh được danh sách đơn cần chú ý theo ngưỡng trễ, không dùng mô hình | 1 |
| ✅ T4.2 | Single-ML — chỉ dự báo | `baselines/simple.py::SingleMLBaseline` | Dùng đúng `capabilities/risk_model.py`, không sao chép mã | 0.5 |
| ✅ T4.3 | **Monolithic-Complete — đa nhãn** | `baselines/monolithic.py` | Dùng chung mô hình, chung head **đa nhãn**, chung YAML; quy trình tuần tự, gặp exception thì ghi log rồi đi tiếp | 2 |
| ✅ T4.4 | Test công bằng | `tests-v3/test_baseline_parity.py` | Test thất bại nếu baseline và MAS-DSS không dùng cùng một đối tượng capability | 0.5 |

> T4.3 **bắt buộc là đa nhãn**. Nếu để đơn nhãn dùng `argmax`, MAS-DSS thắng ở tình huống (a) của RQ3
> theo cấu tạo, và cả Chương 5 mất giá trị.

---

## WP5 — Core và runtime · 6,5 ngày công · *phụ thuộc WP0*

| ID | Công việc | Đầu ra | Tiêu chí nghiệm thu | Ngày |
|---|---|---|---|---|
| ✅ T5.1 | Ontology: `Cause`, `Evidence`, `Bid`, `Declaration`, `Critique`, `Action` | `core/ontology.py` | **Frozen dataclass + bất biến trong `__post_init__`** *(không dùng Pydantic — xem MT2.1)*; bid có nguyên nhân cụ thể bắt buộc kèm bằng chứng | 1 |
| ✅ T5.2 | `Message` envelope + **10** performative | `core/message.py` | Đủ trường theo `technical-plan-v3.md §A.1`; `deadline_ms` là **thời lượng**; `payload` không bao giờ ghi nhật ký | 1 |
| ✅ T5.3 | `Decision` với `degradation_level` **bắt buộc, không mặc định** | `core/decision.py` | Bất biến lúc khởi tạo: `degradation_level > 0` ⟹ `needs_human_review = True`; property-based test | 1 |
| ✅ T5.4 | Phân loại lỗi transient / deterministic | `core/errors.py` | Hai nhánh riêng biệt, chính sách retry đọc theo loại | 0.5 |
| ✅ T5.5 | Actor: hộp thư, chính sách `ACT`/`REFUSE` | `runtime/actor.py` | Hộp thư có giới hạn, có backpressure | 1 |
| ✅ T5.6 | **Seam tiêm lỗi** `invoke()` | `runtime/faults.py` | Mọi lời gọi tác tử đi qua đúng hàm này; timeout thật bằng `asyncio.wait_for` **hủy** task | 1 |
| ✅ T5.7 | Đo span thủ công | `runtime/tracing.py` | 1 trace = 1 case, 1 span = 1 message; ghi vào SQLite | 1 |

> T5.6 là công việc quan trọng nhất trong gói này. Nếu seam không đặt đúng chỗ ngay từ đầu, WP9 sẽ phải
> sửa ngược khắp nơi và thí nghiệm chaos mất tính tái lập.

---

## WP6 — Agents và orchestrator · 13 ngày công · *phụ thuộc WP3, WP5*

| ID | Công việc | Đầu ra | Tiêu chí nghiệm thu | Ngày |
|---|---|---|---|---|
| ✅ T6.1 | Nhật ký message bền vững, append-only | `runtime/message_log.py` + schema SQLite | Truy vấn được theo `conversation_id`; không có đường ghi đè | 2 |
| ✅ T6.2 | Kế hoạch **dạng dữ liệu**: `STAGE1_PLAN`, `STAGE2_PLAN` | `system/plan.py` | Kế hoạch là danh sách `Step` thuần dữ liệu, in ra được vào phụ lục luận văn | 1 |
| ✅ T6.3 | Bộ thực thi `execute(plan, case, invoke_fn)` | `system/orchestrator.py` | Không import gì từ `agents/`, `chaos/`, `evaluation/`; bỏ qua được case đã hoàn tất khi chạy lại | 3 |
| ✅ T6.4 | Blackboard — working memory của case | `system/blackboard.py` | Agent đọc được kết quả của nhau; không có nguồn trạng thái thứ hai | 1 |
| ✅ T6.5 | Agents giai đoạn 1: Analytics, Prediction | `agents/` | Mỗi agent dưới ~80 dòng; mọi logic học máy nằm ở `capabilities/` | 1 |
| ✅ T6.6 | Analyst pool: **Delivery, Quality, Service** *(`Price` đã gỡ 12/08 cùng nhãn `price`)* | `agents/analysts/pool.py` | Mỗi analyst có `cost_class` và **điều kiện `REFUSE` kiểm chứng được** | 2 |
| ✅ T6.7 | Recommendation, Rule Agent, Case Manager | `agents/core_agents.py` | Sinh được hành động phục hồi dịch vụ từ `causes[]`. ⚠️ `CaseManager` **không nằm trong kế hoạch nào** nên không bao giờ được gọi — bề mặt hỏng *gọi được* là **9**, không phải 10 | 1 |
| ✅ T6.8 | Explanation Agent — **chỉ nhận `conversation_id`** | `system/explain.py` | Chữ ký hàm không nhận `case`, không nhận `blackboard`; test chặn vi phạm | 2 |

**Gate G4 — sau WP6.** Một case đi trọn chuỗi, và **decision trace dựng lại được hoàn toàn từ nhật ký
message**. Đây là bằng chứng cho RQ2 — nếu chưa đạt thì không đi tiếp sang WP7.

---

## WP7 — Contract Net có ngân sách · 6 ngày công · *phụ thuộc WP6*

| ID | Công việc | Đầu ra | Tiêu chí nghiệm thu | Ngày |
|---|---|---|---|---|
| ✅ T7.1 | CFP hai pha: bản khai năng lực rồi mới chạy capability đắt | `system/orchestrator.py::_contract_net_session` | Analyst thua thầu **không** chạy capability đắt; `declare()` không được gọi `run()` — `test_declaration_never_runs_the_capability` canh | 2 |
| ✅ T7.2 | Phân bổ ngân sách bằng knapsack nhỏ **vét cạn** | `system/contract_net.py` | Nghiệm tối ưu và tất định; có quy tắc phá thế cân bằng; `budget_binds` báo cáo ngân sách có **thực sự** ràng buộc không | 1 |
| 🟡 T7.3 | **Hiệu chuẩn bid riêng từng analyst** (isotonic) | `capabilities/calibration.py` | T7.3a nạp tham chiếu ✅ · T7.3b `BidCalibrator` **đã cài + có test**, đo ngoài mẫu bằng K-fold ✅ · **chưa nối vào đường chạy chính** ⬜ *(`BidCalibrator` không có lời gọi nào ngoài test)* · **số ECE hiện có đo trên cấu hình 4 analyst và trên nhãn tạm** ⬜ | 2 |
| ✅ T7.4 | Đa nhãn theo ngưỡng τ + `bid_entropy` + cờ `multi_cause` | `system/app.py::reduce_reply` | **Test tĩnh chặn `argmax`/`idxmax`** trong `agents/analysts/` và `baselines/monolithic.py`; `multi_cause` cưỡng chế trong `Decision.__post_init__` | 1 |

---

## WP8 — Tầng chịu lỗi · 10 ngày công · *phụ thuộc WP6*

Đây là nơi đóng góp chính của luận văn nằm. Không được cắt.

| ID | Công việc | Đầu ra | Tiêu chí nghiệm thu | Ngày |
|---|---|---|---|---|
| ✅ T8.1 | Output guard 4 tầng: schema, sanity, calibration, consistency | `system/reliability/guards.py` | Mỗi guard có test riêng với ca vi phạm dựng sẵn | 3 |
| ✅ T8.2 | Health monitor: heartbeat, PSI, phát hiện drift | `system/reliability/health.py` | Phát hiện được drift nhân tạo ở mức 20% | 2 |
| ✅ T8.3 | Circuit breaker | `system/reliability/breaker.py` | Chuyển trạng thái đúng: CLOSED → OPEN → HALF_OPEN → CLOSED | 1 |
| ✅ T8.4 | Supervisor: quản lý breaker theo thành phần, chính sách retry | `system/reliability/breaker.py::Supervisor` | **Không** retry lỗi deterministic; chỉ retry lỗi transient, tối đa 2 lần | 2 |
| ✅ T8.5 | Thang suy giảm + cưỡng chế `needs_human_review` | `system/blackboard.py::degrade` + `core/decision.py::__post_init__` | Test bao phủ bất biến: **không quyết định tự động nào** khi `degradation_level > 0`. ⚠️ Các mức fallback trung gian (L1/L2) **chưa cài** — hệ nhảy thẳng từ L0 sang hành vi L3 | 2 |

---

## WP9 — Chaos harness · 6 ngày công · *phụ thuộc WP4, WP8*

| ID | Công việc | Đầu ra | Tiêu chí nghiệm thu | Ngày |
|---|---|---|---|---|
| ✅ T9.1 | Phân loại lỗi + bộ tiêm có seed | `chaos/injector.py` + `chaos/scenarios.py::DESIGNED_FOR` | Cắm vào `runtime/faults.py`; không sửa mã hệ thống khi tiêm lỗi. *(Không tách `taxonomy.py` riêng — phân loại là trường `group`/`designed_for` của chính kịch bản)* | 2 |
| T9.2 | 5 nhóm lỗi × 3 mức nhiễu loạn | `chaos/scenarios.py` | Đủ crash, Byzantine thô, và **3 loại Byzantine tinh vi** theo `technical-plan-v3.md §A.7` | 2 |
| ✅ T9.3 | Runner chạy **cùng kịch bản** trên MAS-DSS và Monolithic-Complete | `chaos/runner.py` | Hai kiến trúc nhận đúng cùng chuỗi lỗi với cùng seed | 1.5 |
| T9.4 | Kiểm chứng tái lập | `tests-v3/test_chaos_repro.py` | Hai lần chạy cùng seed cho kết quả trùng khớp đến từng byte | 0.5 |

**Gate G5 — sau T9.4.** Nếu kết quả chaos chưa tái lập được thì **không được đưa số nào vào luận văn**.
Đây là điều kiện tiên quyết, không phải mong muốn.

---

## WP10 — Đánh giá · 11 ngày công · *phụ thuộc WP2, WP4, WP7, WP9*

| ID | Công việc | Đầu ra | Tiêu chí nghiệm thu | Phục vụ | Ngày |
|---|---|---|---|---|---|
| ✅ T10.1 | Dự báo: PR-AUC, ROC-AUC, **kiểm định tương đương** | `evaluation/forecasting.py` | Dùng equivalence test, không phải t-test | H1 | 2 |
| T10.2 | Quy kết: macro-F1 đa nhãn, **chỉ nhận gold set** | `evaluation/attribution.py` | Truyền weak label vào phải **raise** — có test khẳng định | RQ3, H1 *(vế quy kết)* | 2 |
| T10.3 | **Selective prediction**: đường cong risk–coverage cho tầng B | `evaluation/selective.py` | So hai hệ ở **cùng mức độ phủ** | RQ3 | 2 |
| ✅ T10.4 | Phối hợp: số message, `bid_entropy`, đường tắt, chất lượng/ms | `evaluation/coordination.py` | Tính được từ nhật ký message, không cần đo thêm | RQ3 | 2 |
| T10.5 | Chịu lỗi: độ nhạy guard, độ trễ phát hiện, báo động giả, hỏng âm thầm | `evaluation/resilience.py` | Tách bạch rõ chỉ số nào là kết quả thật, chỉ số nào là kiểm tra đặc tả | RQ1, H2, H3 | 2 |
| ✅ T10.6 | Chi phí: latency p50/p95, số thành phần, quy mô mã tầng chịu lỗi | `evaluation/cost.py` | Có bảng đối chiếu MAS-DSS ↔ Monolithic-Complete | RQ1(d) — **báo cáo mô tả**, H5 đã gỡ | 1 |

---

## WP11 — Kết quả cho Chương 5 · 5 ngày công · *phụ thuộc WP10*

| ID | Công việc | Đầu ra | Tiêu chí nghiệm thu | Ngày |
|---|---|---|---|---|
| T11.1 | Pipeline sinh toàn bộ bảng số bằng **một lệnh** | `cli/run_evaluation.py` | Chạy một lệnh ra đủ bảng và hình cho Chương 5 | 2 |
| T11.2 | Phân tích độ nhạy: **T₃ ↔ T₄** (chính), T₂ ↔ T₃ (bổ sung), ngưỡng `≤2` ↔ `≤3` | Bảng kết quả | Chỉ đổi cấu hình, không sửa mã | 1.5 |
| T11.3 | Ablation: tắt CNP, tắt guard, cấm `REFUSE` | Bảng kết quả | Mỗi Design Principle có đúng một ablation tương ứng | 1.5 |

---

## Phần 6 — Lịch theo tuần *(giả định 5 ngày/tuần)*

| Tuần | Luồng A — mã nguồn | Luồng B — gold set |
|---|---|---|
| 1 | WP0 · WP1 bắt đầu | T2.1, T2.2 — sampler và codebook |
| 2 | WP1 xong · **Gate G1** · WP3 bắt đầu | T2.3, T2.4, **T2.5 vòng thử → Gate G2** |
| 3–4 | WP3 capabilities | Gán nhãn — đợt 1 (~150 đơn) |
| 5 | WP3 xong · **Gate G3** · WP4 baselines | Gán nhãn — đợt 2 (~150 đơn) |
| 6 | WP5 core và runtime | Gán nhãn — đợt 3 (~100 đơn) |
| 7–8 | WP5 xong · WP6 bắt đầu | T2.7 đối chiếu, chốt gold set |
| 9 | WP6 · **Gate G4** | — |
| 10 | WP7 contract net | — |
| 11–12 | WP8 tầng chịu lỗi | — |
| 13 | WP9 chaos · **Gate G5** | — |
| 14–15 | WP10 đánh giá | — |
| 16 | WP11 kết quả Chương 5 | — |

Tổng ~80 ngày công. Nếu làm bán thời gian 2,5 ngày/tuần thì khoảng 32 tuần.

---

## Phần 7 — Đường cắt giảm nếu tiến độ không kịp

Cắt theo **đúng thứ tự** này, không đảo. Mỗi mức ghi rõ cái mất đi.

| Thứ tự cắt | Nội dung | Tiết kiệm | Mất gì |
|---|---|---|---|
| 1 | Bộ nhớ tiền lệ (`memory/precedent.py`) | 4 ngày | Một ablation bổ sung. Không RQ nào phụ thuộc |
| 2 | Policy Critic và Arbiter | 5 ngày | Một ablation về can thiệp thừa. Chuỗi quyết định vẫn đủ cho RQ2 |
| 3 | Gold set hạ từ 400 xuống **200 đơn** | 2,5 ngày | Khoảng tin cậy rộng hơn ở RQ3. **Vẫn báo cáo được** — 200 đơn có κ tốt hơn 400 đơn không đo được κ |
| 4 | Baseline MIS | 1 ngày | Một cột trong bảng so sánh. Monolithic-Complete mới là baseline quan trọng |
| 5 | Byzantine tinh vi giảm từ 3 mức xuống 2 mức | 1 ngày | Đường cong độ nhạy guard thưa hơn |

**Tuyệt đối không cắt:** WP2 (gold set), T4.3 (Monolithic-Complete), WP8 (tầng chịu lỗi), WP9 (chaos
harness). Bốn hạng mục này là thứ giữ cho Chương 5 có giá trị.

---

## Phần 8 — Năm điểm quyết định

| Gate | Sau công việc | Câu hỏi | Nếu không đạt |
|---|---|---|---|
| **G1** | WP1 | Thống kê mô tả có khớp bảng M0 không? | Dừng, tìm lỗi ghép bảng trước khi đi tiếp |
| **G2** | T2.5 | κ vòng thử ≥ 0,6? | **Sửa codebook và gán lại** — vấn đề nằm ở định nghĩa nguyên nhân, không ở người gán |
| **G3** | WP3 | Mô hình rủi ro có đủ tốt để có ý nghĩa nghiệp vụ? | Xử lý ngay tại đây; mọi thứ phía sau đứng trên nó |
| **G4** | WP6 | Decision trace dựng lại được hoàn toàn từ nhật ký message? | Sửa ngay — đây là bằng chứng của RQ2, không phải chi tiết cài đặt |
| **G5** | WP9 | Kết quả chaos tái lập được với cùng seed? | **Không đưa số nào vào luận văn** cho tới khi đạt |

---

## Phần 9 — Rủi ro tiến độ

| Rủi ro | Mức | Xử lý |
|---|---|---|
| Gold set trượt tiến độ | **Cao nhất** | Khởi động tuần 1; chia làm ba đợt gán nhãn để phát hiện chậm trễ sớm; có phương án hạ xuống 200 đơn |
| κ vòng thử thấp | Trung bình | Đã có Gate G2 và ngân sách sửa codebook. Bản thân κ thấp cũng là phát hiện đáng viết |
| BERTimbau làm chậm mọi thí nghiệm | Trung bình | T3.3 đệm embedding ra đĩa ngay từ đầu; chaos chỉ tiêm lỗi ở tầng head, không chạy lại encoder |
| WP6 vượt ước lượng 13 ngày | Trung bình | Giữ agent thật mỏng (dưới ~80 dòng); mọi logic học máy nằm ở WP3 đã xong trước đó |
| Seam tiêm lỗi đặt sai chỗ, phát hiện muộn ở WP9 | Trung bình | Viết một kịch bản chaos tối giản ngay sau T5.6 để kiểm chứng seam, không đợi tới WP9 |
| Phát sinh yêu cầu ngoài kế hoạch | Trung bình | Đối chiếu `technical-plan-v3.md §7` — danh sách những gì cố ý không xây |
