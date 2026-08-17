# Trạng thái phiên làm việc — điểm nối để tiếp tục

> **Đọc file này trước tiên khi quay lại.** Nó ghi lại: đang ở đâu, việc gì đang chờ ai, làm gì tiếp
> theo, và những con số nào **chưa được phép** trích vào luận văn.
>
> Cập nhật: **15/08/2026.** **303 test xanh · 6/6 cổng đạt · không hạng mục nào chặn số
> liệu.**
>
> ### 🔴 Vào lại thì đọc **§13e** trước — hai việc đang chờ quyết, cả hai chỉ là viết
>
> 1. **LangGraph** — đã phân tích xong, **kết luận KHÔNG chuyển**. Còn hai việc đề xuất *(A: bảng đo
>    cho §2.2f · B: một đoạn Chương 6)*
> 2. **Cái giá của hiệu chuẩn** — phát hiện isotonic gộp **11.288 → 93** mức phân giải, **chưa có trong
>    luận văn**. Đề xuất ba dòng vào §A.6.2 và một câu vào ch5 §5.3
>
> | Phiên | Mục | Nội dung |
> |---|---|---|
> | 14/08 khuya | **§13** | Phụ lục A · độ quan trọng đặc trưng · ảnh chụp ma trận · L44–L45 |
> | 14/08 tối | §12 | Thu gọn phạm vi · sửa 4 khiếm khuyết phương pháp · **cổng G5 đạt** · Chương 5 |
> | 14/08 sáng | §11 | Gold set về · κ = 0,784 |
> | 13/08 | §10 | Sửa rò rỉ khoảng cách ly · đường vào dữ liệu |
>
> ### 🔴 Ba tài liệu chuyên trách — tra ở đó thay vì tra file này
>
> | Câu hỏi | Tài liệu |
> |---|---|
> | Artifact nào phục vụ câu hỏi nào, bằng chứng ở tệp nào, lệnh tái lập | [artifact-register.md](artifact-register.md) |
> | Chỉ số này đo gì, tính thế nào, **có trích được không** | [evaluation-handbook.md](evaluation-handbook.md) |
> | Mục tiêu nào đạt, còn thiếu gì | [status-checklist.md](status-checklist.md) *(đã viết lại 14/08)* |
>
> **Mọi bảng số trong file này từ §11 trở về trước là HỒ SƠ.** Số hiện hành nằm ở `data/v3/evaluation/`.

---

## 🔴 Phiên 12/08 — năm thay đổi làm mọi con số trước đó hết hiệu lực

| # | Thay đổi | Hệ quả |
|---|---|---|
| 1 | **Số hiệu RQ/MT hoán vị vòng** — chịu lỗi lên RQ1 | mọi tài liệu và 153 tham chiếu mã nguồn đã đồng bộ; `methodology-log.md` và `thesis-mapping.md` **cố ý giữ số cũ** kèm bảng tra |
| 2 | **T₃ = ngày mua + 7** *(trước: hạn dự kiến + 3)* | mốc cũ đặt T₃ **sau** T₄ với **97,6%** đơn — mọi số dự báo trước đây đo trên cấu hình hỏng. Xem **L33** |
| 3 | **Tách tệp đặc trưng vật lý** `data/v3/features/` | `load_split()` là đường vào duy nhất; ba bất biến lược đồ + mutation check |
| 4 | **H2 bác bỏ một phần** | guard không phủ lỗi Byzantine trên 4 thành phần chỉ-MAS. Xem **§3.2** tài liệu nguồn và **L36** |
| 5 | **Cách đếm hỏng âm thầm đã sửa** | đối chứng bị tính thiệt: nó **có** `failed_steps` mà phép đếm bỏ qua. *"Mono âm thầm 16–38% dưới crash"* thực ra là **0,0%**. Xem **L37** |

> Kế hoạch được duyệt trước đợt này, kèm biên bản đối chiếu kế hoạch ↔ thực tế:
> [plan-2026-08-12.md](plan-2026-08-12.md).

### Số hiện hành *(303 test xanh · 47 lỗi phương pháp)*

> **Tuyên bố chịu lỗi, phát biểu chính xác:** ưu thế của MAS-DSS nằm **trọn vẹn** ở nhóm lỗi **không
> ném ngoại lệ**. Lỗi biết `raise` thì `try/except` là đủ — kiến trúc nào cũng bắt. Lỗi trả về **giá
> trị hợp lệ nhưng sai** mới cần thang suy giảm và output guard. Hẹp hơn bản cũ nhưng **có cơ chế giải
> thích**, nên mạnh hơn.


> 🔄 **Cập nhật 13/08 sau khi sửa rò rỉ khoảng cách ly.** Mọi số dưới đây nay **tái lập được** bằng
> ba lệnh: `export_features` → `train` → `run_system` → `run_evaluation`. Trước đó chúng đến từ một
> đường ống không tồn tại trong mã nguồn — xem §10.

| | Giá trị |
|---|---|
| Tổng thể **T₃** *(dự báo)* | **75.480** đơn còn kịp can thiệp *(76,5%)* |
| Tổng thể **T₄** *(quy kết)* | **98.673** đơn — **không lọc**, quyết định 13/08. Test: 18.952 đơn, 2.083 bất mãn |
| train / val / test @ T₃ | 52.835 / 9.077 / 11.322 · nền **17,90% → 14,82% → 12,74%** |
| PR-AUC test | **0,2381** [0,2187 – 0,2578] · lift 1,87 |
| Độ nhạy ngưỡng nhãn | `≤2` → 0,2381 · `≤3` → 0,3150 — **không đảo chiều kết luận** |
| Ngưỡng quyết định theo chi phí *(test)* | **0,194** *(không phải 0,5)* |
| **Thang rủi ro** *(suy ra từ val, lưu trong mô hình)* | **0,160 / 0,3103** — thay hai hằng số 0,40/0,70 |
| Phân tầng rủi ro trên test | LOW 68,96% *(bất mãn 9,20%)* · MEDIUM 23,01% *(17,01%)* · HIGH 8,03% *(30,91%)* |
| **Phạm vi T₄** *(quyết định 13/08)* | **CHỈ tầng A** — đơn không có bình luận tách riêng, **ngoài phạm vi đề tài**. Hồ gold set thu từ 2.083 → **1.615 ứng viên** |
| **Gold set** *(14/08)* | **300 dòng · `human_independent` · `citable = True`** · κ = **0,784** · độc lập 77,7% |
| **Quy kết @ T₄ — chấm trên gold set** | macro-F1 MAS **0,5862** · đơn khối **0,6862** · không quy kết 28,3% |
| Quy kết theo nhãn | `delivery` **0,7302 = 0,7302** · `quality` **0,6667 = 0,6667** · `service` MAS **0,3619** vs Mono **0,6618** ❌ |
| **Hành động @ T₃** *(11.322 đơn, rule engine thật)* | can thiệp **3.582 (31,6%)** · bắt **737/1.442 (51,1%)** · precision 0,2058 · chi phí 19.106 |
| Thang hành động T₃ | quá hạn+HIGH → coupon *(4,33×)* · sắp quá hạn+HIGH → coupon *(3,34×)* · quá hạn → callback *(2,19×)* · HIGH → ticket *(2,30×)* · sắp quá hạn → ticket *(2,21×)* · MEDIUM → ticket *(1,25×)* |
| precision@0,5% · @1% | **0,679** *(lift 5,33)* · **0,522** [0,451–0,646] *(lift 4,10)* |
| **Điểm vận hành** *(ngưỡng 0,160 từ val)* | precision **0,206** [0,193–0,220] · recall **0,502** [0,477–0,527] · F1 0,292 |
| ⚠️ **Accuracy thô** | **0,690** — **thua** mốc tầm thường *"đoán tất cả hài lòng"* = **0,873**. **Không được dùng làm chỉ số chính** |
| Brier skill **thô** | **−0,0217** ⚠️ mô hình thô **thua** hằng số nền |
| Brier skill sau isotonic | **+0,0328** · ECE 0,0696 → **0,028** |
| **Chịu lỗi — CÓ ném ngoại lệ** *(crash, hang)* | MAS **0,0%** · Mono **0,0%** — ⚪ không khác biệt *(quyết định đổi 57,0 → 81,5%)* |
| **Chịu lỗi — byzantine thô** | MAS **0,0%** · Mono **84,5 → 99,0%** ✅ · độ trễ phát hiện 20 quan sát |
| **Chịu lỗi — bias** *(guard KHÔNG thiết kế để bắt)* | MAS **0,0%** · Mono **25,0 → 84,5%** ✅ · độ trễ 100 |
| ⚠️ **Chịu lỗi — drift** *(guard KHÔNG thiết kế để bắt)* | MAS **2,5 – 5,0%** · Mono 3,5 – 6,5% — **cả hai gần mù, không phát hiện ở mọi mức** |
| Đường khỏe | 0,0% suy giảm · 0 guard chặn · **báo động giả = 0** |

### Việc tiếp theo, theo thứ tự

| # | Việc | Trạng thái | Ghi chú |
|---|---|---|---|
| **1** | **T9.4 kiểm tái lập** — hai lượt chạy cho `decisions.jsonl` trùng `sha256`; chạy lại **Gate G5** | ⬜ làm được ngay | Chưa chạy lại từ 12/08. **Chưa số chaos nào đủ điều kiện vào luận văn** trước khi phép kiểm này xanh |
| **2** | **Vá lỗ `service`** — MAS 0,3619 vs đơn khối 0,6618, là **toàn bộ** khoảng cách macro-F1 còn lại | ⬜ cần quyết định | Nguyên nhân đã xác định *(xem §11)*. **Đã loại**: sửa `prior_confidence` riêng — chứng minh 0/300 đơn đổi phân bổ |
| **3** | **Mở guard sang 4 thành phần chỉ-MAS** | ⬜ làm được ngay | Là **cải tiến thiết kế**, **không** phải sửa H2. Đo lại rồi báo cáo **cạnh** kết quả hiện tại |
| **4** | **Nối `BidCalibrator` vào đường chạy chính** *(T7.3b)* | ⬜ làm được ngay | Lớp đã cài + có test nhưng **không lời gọi nào ngoài test**; analyst vẫn phát điểm thô |
| 5 | **IMP-4 → IMP-7** trong [methodology-log.md](methodology-log.md) | ⬜ | ~2,5 ngày. Nên bổ sung **L38–L45** của hai phiên 13–14/08 |
| 6 | **WP11** — dựng bảng số Chương 5 | 🔒 việc 1 | Số quy kết đã sẵn sàng và `citable`; chỉ còn chờ số chịu lỗi |

> **Việc 1 trước tiên**: chaos đã chạy lại xong cuối phiên 14/08 và số đã vào bảng trên, nhưng
> **kiểm tái lập chưa chạy** — chưa số chaos nào đủ điều kiện vào luận văn trước khi phép kiểm đó xanh.

### Không được trích vào luận văn

- Mọi con số dự báo/quy kết đo trước 12/08 — chúng ở mốc T₃ cũ.
- `§4` và `§4b` của `status-checklist.md` — bản năm giả thuyết, đã lỗi thời.
- Số từ gold set cũ *(`gold_annotation_*_en.csv`)* — 199/250 dòng nằm trong kỳ train.
- Mọi con số *"đơn khối hỏng âm thầm"* dưới **crash/hang** ở bản trước — đúng giá trị là **0,0%** *(L37)*.

---

> 📋 **Cần bức tranh theo mục tiêu nghiên cứu?** Đọc [status-checklist.md](status-checklist.md) —
> một trang đối chiếu MT1/MT2/MT3, ba giả thuyết, sáu artifact, và bảng *số nào trích được*.
> Tài liệu này ghi **việc đang làm**; tài liệu kia ghi **kết quả đã đạt**.

---

## 1. Tình hình trong một bảng

| Hạng mục | Trạng thái |
|---|---|
| Mã nguồn | `src-v3/masdss/` — **85 tệp, 11.047 dòng** |
| Test | `tests-v3/` — **23 tệp, 274 test xanh**, chạy hết 67 giây |
| Tài liệu | `docs/` — **16 tệp** + `docs/thesis/` **7 tệp** |
| Tiến độ | **~58 / 82 ngày công** |
| Chạy được ngay | `python -m masdss.cli.run_system --stage 2 --n 300`<br>`python -m masdss.cli.run_evaluation --run data/v3/runs/cnp` |

### Gói công việc

| WP | Trạng thái |
|---|---|
| WP0 nền tảng · WP1 dữ liệu · WP4 baselines · WP5 core+runtime · WP6 agents · WP8 chịu lỗi | ✅ **Xong** |
| WP2 gold set | 🟢 **Bộ nhãn tạm 250 dòng — đủ dùng để dựng đường ống.** Bộ nhãn cuối: **300 dòng `goldset_v2`, chỉ từ `t3_test`**, 2 người gán độc lập — **chưa gán** |
| WP3 capabilities | 🟢 **~95%** — **T3.4 xong** (`TfidfCauseHead`); T3.3 BERTimbau vẫn chặn bởi `torch` |
| WP7 Contract Net | 🟡 ~85% — xong T7.1, T7.2, T7.4; **T7.3b `BidCalibrator` đã cài + có test nhưng CHƯA nối vào đường chạy**, và số ECE hiện có đo trên cấu hình 4 analyst với nhãn tạm |
| WP9 chaos | ✅ **Xong T9.2** — 5 nhóm × 3 mức; còn T9.4 |
| WP10 đánh giá | 🟢 **Xong T10.1 → T10.6** — mọi số đều mang cờ `citable=False` cho tới khi có gold set thật |
| WP11 kết quả Chương 5 | ⬜ Chưa bắt đầu |

---

## 1-CHU-TRINH. ✅ Đã chạy trọn vòng T2.7 → T3.4 → T10.2 → T10.3

Anh yêu cầu chạy hết chu trình để kiểm luồng thông tin và artifact. **Đã chạy.** Một lệnh:
`python -m masdss.cli.run_attribution`. Nhãn hiện tại được coi là hợp lệ **tạm thời** — nguồn gốc
`model_assisted_provisional` được cưỡng chế bằng kiểu dữ liệu, nên mọi bảng kết quả đều mang cột
`citable = False` cho tới khi có vòng gán độc lập.

### Đã mở khóa

| Task | Trạng thái |
|---|---|
| **T2.7** artifact gold set | ✅ `gold_labels.csv` + meta ghi nguồn gốc, 1 dòng chuẩn hóa có ghi chép |
| **T3.4** head đa nhãn | ✅ `TfidfCauseHead` — huấn luyện thật, `is_placeholder=False`, không cần `torch` |
| **T10.2** macro-F1 quy kết | ✅ chạy, có cắt lớp |
| **T10.3** selective prediction | ✅ chạy |

### 🔴 Ba lỗi nối ghép lộ ra — đúng mục đích của việc chạy trọn chu trình

**1. `causes` có hai dạng biểu diễn trong cùng một lần chạy.** `decisions.jsonl` ghi
`[{cause, probability}]`, `baselines.jsonl` ghi `["delivery"]`. Bảng T10.2 đầu tiên báo MAS quy kết
**0/250** trong khi thực tế là 97. Đã sửa + test canh.

**2. Ngân sách chưa hiệu chỉnh lại sau khi head đổi giá.** `budget_for` cấp **2,0 ms** cho case rủi ro
thấp; head thật khai **12 ms** ⟹ analyst văn bản không bao giờ mua được suất. **Cổng rủi ro đã gỡ
tường minh khỏi T4 nay quay lại ngầm qua ngân sách.**

**3. Hai kiến trúc giống hệt nhau theo cấu tạo — `0/250` đơn khác biệt.** Xem **L27**.

| hệ số ngân sách | macro-F1 MAS | macro-F1 Mono |
|---|---|---|
| ×1 | **0,2386** | 0,3804 |
| ×10 | 0,3776 | 0,3804 |
| ×25 | **0,3804** | 0,3804 |

Các analyst **phân chia** không gian nhãn chứ không **tranh chấp** nó, dùng chung head và chung ngưỡng
τ ⟹ hai phép toán bằng nhau về đại số. **DP2 nói "cạnh tranh" nhưng cài đặt hiện tại không có cạnh
tranh nào.** H2 ở dạng này *không thể* thắng: hoặc bằng, hoặc kém.

*(Bảng trên đo khi còn **bốn** analyst. `PriceAnalyst` đã gỡ 12/08 — số thay đổi, nhưng lập luận đại số
thì không: nó không phụ thuộc số lượng analyst.)*

**Ba đường xử lý** *(chi tiết ở L27)*, và **kết cục của cả ba đã biết:**

| Đường | Kết cục |
|---|---|
| Báo cáo như phát hiện phủ định | ✅ **Đã chọn.** RQ2 cũ trở thành **RQ3 — điều kiện kiểm soát**; kết quả âm đổi vai trò thay vì bị vứt |
| T7.3b hiệu chuẩn isotonic riêng từng analyst để phá đẳng thức | ❌ **Không phá được, và chứng minh được.** Isotonic **đơn điệu không giảm**, nên đặt ngưỡng τ trên điểm đã hiệu chuẩn **tương đương** đặt một ngưỡng khác trên điểm thô — tập quyết định trùng khớp hoàn toàn |
| Hiệu chỉnh lại ngân sách theo giá thật | 🟡 **Đã làm** *(bội số 0,6/1,0/1,5)*. MAS không còn thua 0,14 mà chỉ cách 0,003 — **nằm trong nhiễu**, không được diễn giải là hơn hay kém |

---

## 1a. ✅ Gold set — QUYẾT ĐỊNH ĐÃ CHỐT, không mở lại

**Quyết định của anh (11/08):** giữ nguyên gold set 250 dòng tầng A hiện có, **kể cả khi cách gán
có khiếm khuyết**. Vòng kiểm chứng độc lập **dời về sau khi hoàn thành project**: hai người khác sẽ
gán **250 dòng KHÁC**, và bộ nhãn đó dùng để đánh giá lại toàn bộ.

**Vì sao quyết định này hợp lý về mặt kỹ thuật.** Nó tách bạch hai việc vốn hay bị trộn:

| | Bộ nhãn hiện tại | Bộ nhãn cuối |
|---|---|---|
| Mục đích | **dựng và gỡ lỗi đường ống** | **sinh kết quả cho Chương 5** |
| Nguồn gốc | `model_assisted_provisional` | `human_independent` |
| Cỡ | 250 dòng tầng A | 250 dòng **khác**, 2 người gán độc lập |
| Số sinh ra | `citable = False` | `citable = True` |
| Thời điểm | ngay bây giờ | sau khi mã nguồn xong |

Dùng một bộ nhãn tạm để phát triển rồi thay bằng bộ nhãn sạch để đo là **thực hành đúng**, miễn là
ranh giới được cưỡng chế chứ không phó mặc trí nhớ. Ranh giới đó **đã được cưỡng chế bằng kiểu dữ
liệu**: `Provenance` không có giá trị mặc định, mọi bảng kết quả mang cột `citable`, và đổi **một
tham số** `--provenance human_independent` là toàn chuỗi tự đổi trạng thái.

**Lợi thế phụ, đáng kể:** vì bộ nhãn cuối nằm trên **250 dòng khác**, nó vừa là gold set vừa là
**tập kiểm thử độc lập** — không dòng nào từng tham gia quá trình phát triển. Điều đó mạnh hơn
phương án gán lại chính 250 dòng cũ, vốn sẽ dính hiệu ứng neo.

**Việc phải làm khi bộ nhãn cuối về:**

```
python -m masdss.cli.check_validation --human <nguoi_1>.csv --model <nguoi_2>.csv
python -m masdss.cli.build_goldset --source <chot>.csv --provenance human_independent
python -m masdss.cli.run_attribution
```

Bước một kiểm **tính độc lập** trước khi tính κ — nó đã chặn đúng hai tệp vòng 3 với lý do ghi chú
trùng 96,4%. `validation_human.csv` (150 dòng) giữ lại làm dự phòng, **không dùng tới** trong phương
án này.

---

## 1b. ⏸️ Chốt phiên 10/08 — hai việc, một cần anh quyết

### ❗ Cần anh quyết trước khi tôi làm tiếp phần tầng B

Rà soát artifact theo RQ/MT hôm nay phát hiện **tầng B của gold set không dùng được như đang có**:

| | |
|---|---|
| Dòng tầng B | 150 |
| Cả hai người cùng gán `unknown` | **149/150** |
| Dòng **thỏa Quy tắc 6** của codebook *(trễ > 3 ngày ⟹ `delivery`)* | **43 (28,7%)**, cao nhất 41,7 ngày |
| Trong 43 dòng đó, được gán `delivery` | **0** |

Codebook bản 3 lấy lý do *"đồng thuận tuyệt đối 0/150"* để miễn gán lại tầng B — **đó là L22 lặp lại**,
và người viết câu đó là tôi. Đã ghi thành **L25** trong [methodology-log.md](methodology-log.md).

Nhưng thủ phạm thật là **Quy tắc 6**: nó suy nhãn vàng từ chính đặc trưng mà `DeliveryAnalyst` cũng
nhìn thấy ⟹ **vòng tròn**. Trực giác của hai người gán — không có văn bản thì không quy kết — là đúng.

**Ba đường, tôi khuyến nghị đường 1:**

| | Đường | Đánh giá |
|---|---|---|
| **1** | **Bỏ Quy tắc 6**; giữ nguyên nhãn tầng B; đổi chỉ số tầng B sang **tỷ lệ quy kết sai khi con người bỏ trống** | ✅ Không phải gán lại · phá vòng tròn · biến DP3 thành câu trả lời thay vì thành thứ bị macro-F1 trừ điểm |
| 2 | Gán lại tầng B theo Quy tắc 6 | ❌ Giữ nguyên vòng tròn |
| 3 | Tuyên bố tầng B không đánh giá được | ⚠️ Mất một nửa RQ3 trong khi vẫn còn phép đo hợp lệ |

*Quyết định này **không** ảnh hưởng việc gán tầng A — cứ tiến hành như kế hoạch.*

### ✅ Đã xong hôm nay

**T10.1 · T10.4 · T10.6** — ba nhóm chỉ số duy nhất không cần gold set. Số liệu đầy đủ ở
[build-plan.md §0.10](build-plan.md); sinh lại bằng một lệnh:
`python -m masdss.cli.run_evaluation --run data/v3/runs/cnp`.

Hai lỗi tự phát hiện khi chạy thật, đã ghi **L23** và **L24**:

- **L23** — đọc điểm dự báo bằng cách tách chuỗi `note` *(đã làm tròn 4 chữ số)* làm điều kiện kiểm
  soát H1 báo sai lệch. Sửa bằng trường số thô `SimpleResult.score`, **không** bằng cách nới ngưỡng.
- **L24** — bộ đếm dòng mã hụt ~26%, **hụt đúng theo hướng làm artifact trông rẻ hơn**. Tầng chịu lỗi
  330 → **448**, phối hợp 503 → **632**.

### 📋 Rà soát artifact theo RQ/MT — kết luận

| | Đáp ứng mục tiêu? |
|---|---|
| **MT2 → RQ2** | ✅ Đáp ứng. Còn thiếu 2 đường ablation (DP3 cấm `REFUSE`, DP4 đo độ phân kỳ trace) |
| **MT1 → RQ1** | 🟡 Một phần — H2 nay đòi cả hai mốc và toàn bộ bề mặt hỏng; H5 đã gỡ |
| **MT3 → RQ3** | ❌ Chưa. Chặn ở gold set, và tầng B cần quyết định ở trên |

~~**Hai tiêu chí hoàn thành trong `research-questions-objectives.md` đã lỗi thời, cần sửa lời văn:**
MT2.1 viết *"đặc tả bằng Pydantic schema"*; MT2.2 yêu cầu *"bảng phân định trách nhiệm giữa LangGraph
và phần tự viết"*.~~ ✅ **Đã sửa** — cả hai nay có đính chính tại chỗ trong
[research-questions-objectives.md](research-questions-objectives.md) §MT2.1 và §MT2.2.

---

## 2. ✅ Vòng 3 — ĐÃ XONG (giữ lại để tham chiếu)

> **Đã hoàn tất 250/250 ngày 11/08.** Việc còn lại không phải gán tiếp mà là **kiểm chứng** —
> xem §1a. Phần dưới giữ nguyên làm hồ sơ phương pháp cho Chương 4.
>
> Kết quả nhãn vòng 3 so với vòng 1: `unknown` **87 → 18**, `price` **3 → 12**,
> `delivery` 109 → 145. Hướng thay đổi khớp đúng điều codebook bản 3 nhắm tới —
> nhưng **hướng đúng không thay cho bằng chứng độ đúng**.

**Vòng 1 (400 dòng) đã lộ ra vấn đề gốc, và nó không phải định nghĩa mà là ngôn ngữ.**

| Bản chất của 102 dòng bất đồng | | |
|---|---|---|
| Một bên nói `unknown`, bên kia tìm ra nguyên nhân | **76 (75,2%)** | **bỏ sót bằng chứng** |
| Cùng hướng, khác số lượng nhãn | 18 (17,8%) | ngưỡng |
| Quy kết khác hẳn nhau | 7 (6,9%) | định nghĩa |

Nghiêm trọng hơn: **59/249 dòng tầng A (23,7%) được cả hai người cùng gán `unknown`**,
trong khi ~6/10 dòng mẫu có nguyên nhân nêu tường minh. Hai người cùng bỏ sót thì κ
vẫn cao — **κ đo độ tin cậy, không đo độ đúng**.

**Ba bước — tất cả trên MỘT file:**

1. **Dịch tại chỗ.** Mở `data/v3/goldset/gold_annotation_A_en.csv` (và `_B_en.csv` —
   hai bản giống hệt, mỗi người một bản). **250 dòng tầng A.**

   | Cột | Nội dung |
   |---|---|
   | E, F | `review_title`, `review_content` — **tiếng Bồ gốc, giữ nguyên** |
   | G, H | `review_title_en`, `review_content_en` — **để trống, anh điền** |
   | I–P | Bằng chứng cấu trúc |
   | Q–W | Cột gán nhãn |

   Trong Google Sheets:
   ```
   G2 : =GOOGLETRANSLATE(E2; "pt"; "en")
   H2 : =GOOGLETRANSLATE(F2; "pt"; "en")
   ```
   Kéo hết cột, rồi **dán giá trị** (Ctrl+Shift+V) trước khi lưu CSV. Quên bước này
   thì ô công thức xuất ra rỗng — bước kiểm tra sẽ chặn lại.

2. **Gán nhãn ngay trên cùng file** — độc lập, mù, không trao đổi.
   Đọc [codebook.md](codebook.md) **bản 3**, đặc biệt **§1.2**: *quét hết câu trước
   khi kết luận `unknown`* — đó là lỗi phổ biến nhất của vòng 1.
   Cột tiếng Bồ nằm ngay bên trái để đối chiếu theo QT5.

3. **Đóng băng bản dịch rồi chạy Gate G2:**
   ```
   python -m masdss.cli.freeze_translations
   python -m masdss.cli.check_goldset --require-complete
   ```
   Lệnh thứ nhất kiểm bản dịch, đóng băng thành artifact có checksum, và **liệt kê
   những dòng có bản dịch ngắn hơn 60% bản gốc** — đó là các dòng nghi bị rớt mệnh đề,
   ưu tiên khi đối chiếu với người biết tiếng Bồ. Lệnh thứ hai tự nhận file vòng 3.

**Tầng B (150 dòng) — anh KHÔNG phải gán lại**, nhưng lý do cũ *("đã đạt đồng thuận
tuyệt đối 0/150")* đã bị bác bỏ: xem **§1b**. Cần anh chọn một trong ba đường ở đó.

**G0062 tự giải quyết** — nó thuộc tầng A nên sẽ được gán lại ở vòng 3.

---

## 3. Việc kế tiếp của tôi

**Đã xong trong lúc chờ gán nhãn:** T9.2 (đủ 5 nhóm lỗi × 3 mức), T7.1/T7.2 (Contract Net hai pha có
ngân sách), và **T10.1 · T10.4 · T10.6** — ba nhóm chỉ số duy nhất **không cần gold set**. Kết quả ở
[build-plan.md §0.10](build-plan.md). Một lệnh sinh lại toàn bộ:
`python -m masdss.cli.run_evaluation --run data/v3/runs/cnp`.

**Kế tiếp, không bị chặn — theo thứ tự ưu tiên cho buổi sau:**

1. **T9.4** — test tái lập chaos, và chạy lại **Gate G5** *(hai lần chạy trùng `sha256`)*. Chưa chạy
   lại sau khi đổi mốc T₃, nên **chưa con số chaos nào đủ điều kiện vào luận văn**.
2. **Nối `BidCalibrator` vào đường chạy chính.** Lớp này đã cài và có test, nhưng **không có lời gọi
   nào ngoài `tests-v3/test_calibration.py`** — analyst khi đấu thầu vẫn phát điểm thô. Đây là khoảng
   cách giữa *"năng lực đã tồn tại"* và *"hệ thống đang dùng"*, phải nói đúng ở Chương 4.
3. **IMP-4 → IMP-7** trong [methodology-log.md](methodology-log.md) (~2,5 ngày).
4. Nếu anh chọn đường 1 ở §1b: cài chỉ số **tỷ lệ quy kết sai khi con người bỏ trống** cho tầng B —
   đây là phần **duy nhất của RQ3 chạy được mà không cần chờ gán nhãn**.

*(Đã xong, gỡ khỏi danh sách: hai đường ablation DP3/DP4 · T7.4 `bid_entropy` · sửa lời văn MT2.1/MT2.2
về Pydantic và LangGraph.)*

**Bị chặn tới khi có gold set:** **T10.2** (macro-F1
quy kết — chỉ số chính của RQ3), **T10.3** (selective prediction), WP11.
T3.3 (BERTimbau) bị chặn bởi quyết định không cài `torch`, **không** bởi gold set — nó không cần nhãn
nào, nên cài trước sẽ rút ngắn đường tới hạn sau khi gold set xong.

---

## 4. ⛔ HỒ SƠ 12/08 — **TOÀN BỘ MỤC NÀY ĐÃ HẾT HIỆU LỰC, ĐỪNG TRÍCH**

> **Rào lại ngày 14/08.** Mục này viết ở mốc T₃ cũ, trước khi vá rò rỉ khoảng cách ly và trước khi có
> gold set thật. Nó **tự mâu thuẫn với bảng "Số hiện hành" ở đầu chính tệp này**, và đó là bẫy chép
> nhầm nguy hiểm nhất trong bộ tài liệu — đoạn cuối mục còn liệt kê một loạt số **sai** dưới nhãn
> *"những con số này đã dùng được"*.
>
> Giữ lại làm hồ sơ thay vì xoá, nhưng **không con số nào ở đây được trích**. Bản hiện hành:
>
> | | Số ở mục này *(SAI)* | Số hiện hành |
> |---|---|---|
> | PR-AUC test | 0,3993 · lift 3,63× | **0,2381** [0,2187 ; 0,2578] · lift **1,87×** |
> | ECE trước → sau | 0,0133 → 0,0072 | **0,0696 → 0,028** |
> | Ngưỡng theo chi phí | 0,167 | **0,194** |
> | Đơn khối hỏng âm thầm | 30,7% | **0,0%** ở crash/hang *(L37)*; chênh lệch nằm ở byzantine và bias |
> | Quy mô mã | 1.080 dòng | **1.118 dòng** *(447 chịu lỗi + 671 phối hợp)* |
> | Overhead độ trễ | +6,7% | đo lại sau khi gỡ ngân sách — xem `cost_2_do_tre_theo_lo.csv` |
>
> Nguồn chuẩn cho mọi con số: `data/v3/evaluation/` và `docs/evaluation-handbook.md`.

Nội dung gốc giữ nguyên bên dưới.

| Con số | Vì sao chưa dùng được | Mở khóa khi |
|---|---|---|
| **Tỷ lệ quy kết được 30,7%** *(92/300 case)* | `LexiconCauseHead` là **bản tạm** dùng bộ từ khóa không kiểm định, recall thấp đúng như dự đoán. Có `is_placeholder = True` và test canh | **T3.4** xong |
| **κ = 0,957 của vòng 3** | **Không đo gì** — hai bản không độc lập, xem L26. Nhãn có thể vẫn tốt, nhưng chưa chứng minh được | `check_validation` đạt |
| **PriceAnalyst 9,3% vs người gán 0%** | **Đã rút lại tạm thời** — con số 0% có thể phản ánh sai sót chung, không phải hệ thống sai | Vòng 3 xong |
| **Mọi chỉ số quy kết nguyên nhân** | Chưa có gold set. `evaluation/attribution.py` **từ chối** weak label bằng exception | **WP2** xong |
| **Nhãn tầng B (150 dòng)** | 43/150 dòng thỏa Quy tắc 6 mà không dòng nào được gán `delivery` — **xem L25**, đang chờ quyết định | Chốt đường ở §1b |
| **Phạm vi giám sát 2/5 thành phần** | Đúng nhưng **bị giới hạn**: `cause_price` thiếu mẫu, hai analyst văn bản chờ T3.4. Mọi con số RQ1(b) phải đi kèm bảng phạm vi phủ | Cải thiện dần |

Thêm hai mục **chưa dùng được** phát sinh từ T10.4:

| Con số | Vì sao chưa dùng được | Mở khóa khi |
|---|---|---|
| **Quy kết / ms = 0,0321** | Biến thay thế: đếm **số** nguyên nhân, không đo **độ đúng**. Hệ thống quy kết bừa sẽ ăn điểm cao | **T10.2** xong |
| **`bid_entropy` 0,9894** | Chỉ tính trên số ít case có ≥2 bid *(1,5% đa nguyên nhân)* — là **chỉ dấu**, chưa phải bằng chứng | Cỡ mẫu lớn hơn sau T3.4 |

~~Ngược lại, **những con số này đã dùng được**: PR-AUC 0,3993 [0,3754 ; 0,4246] trên test, lift 3,63× so
với nền · ECE 0,0133 → 0,0072 · ngưỡng tối ưu theo chi phí 0,167 · hỏng âm thầm MAS 0,0–6,0% so với
Monolithic 30,7% · báo động giả 0/300 · độ trễ phát hiện 20–100 quan sát · overhead độ trễ +6,7% và
1.080 dòng mã.~~

⛔ **Đoạn gạch trên là bộ số SAI nguy hiểm nhất trong bộ tài liệu** — nó tự gắn nhãn *"đã dùng được"*
trong khi mọi con số đều đo ở mốc T₃ cũ và trước khi vá rò rỉ. Xem bảng đối chiếu ở đầu mục.

---

## 5. Bản đồ tài liệu

| Tệp | Vai trò | Hiệu lực |
|---|---|---|
| **session-state.md** *(tệp này)* | Việc đang làm, số hiện hành, số cấm trích | ✅ **Đọc trước tiên** |
| [status-checklist.md](status-checklist.md) | Đối chiếu MT/RQ, ba giả thuyết, artifact, bảng *số nào trích được* | ✅ Kết quả đã đạt |
| [research-questions-objectives.md](research-questions-objectives.md) | **3 RQ / 3 MT**, giả thuyết, phạm vi, bảng tra số hiệu cũ↔mới | ✅ Nguồn chuẩn |
| [technical-plan-v3.md](technical-plan-v3.md) | Kiến trúc, 5 giao diện, 10 tác tử, kỷ luật kỹ thuật | ✅ Nguồn chuẩn kỹ thuật |
| [build-plan.md](build-plan.md) | WBS 12 gói + hồ sơ chạy thử | ✅ Theo dõi tiến độ · ⛔ **§0.6–§0.10 số đã hết hiệu lực** |
| [implementation-plan.md](implementation-plan.md) | Bốn đợt triển khai. **Cây thư mục là bản dự kiến** — bản thực tế ở `technical-plan-v3.md §4` | ✅ |
| [plan-2026-08-12.md](plan-2026-08-12.md) | Kế hoạch đợt 12/08 + biên bản đối chiếu kế hoạch ↔ thực tế | ✅ Hồ sơ |
| [methodology-log.md](methodology-log.md) | **47 lỗi phương pháp + 7 biện pháp cải tiến** | ✅ Nguyên liệu Chương 4–5 · ⚠️ **cố ý giữ số hiệu RQ cũ**, có bảng tra ở đầu tệp |
| [codebook.md](codebook.md) | **Bản 3** — gán trên bản dịch tiếng Anh, quy tắc + ví dụ biên | ✅ Dùng cho bộ nhãn cuối |
| [research-design-v2.md](research-design-v2.md) | Danh mục artifact A1–A7 | ✅ Nguồn chuẩn artifact · ⚠️ **số hiệu RQ theo hệ 5 câu**, có bảng tra ở đầu tệp |
| [thesis-mapping.md](thesis-mapping.md) | Ánh xạ đề cương gốc 5 câu vào codebase v1 | ✅ Hồ sơ · ⚠️ **cố ý giữ số hiệu cũ** |
| [proposal-comparison.md](proposal-comparison.md) | Đối chiếu đề cương gốc | ✅ Chuyển đổi |
| [adversarial-review.md](adversarial-review.md) | Hồ sơ lý do | ✅ Hồ sơ |
| [thesis/](thesis/) | Bản thảo luận văn — 5 chương + mục lục + tài liệu tham khảo | 🟢 Ch1–Ch4 có bản thảo · Ch5 chưa viết |
| ~~architecture.md~~ · ~~technical-design-v2.md~~ · ~~mas-redesign-plan.md~~ | Bản cũ, mâu thuẫn với mã nguồn | ❌ **Lỗi thời** — có biển báo ở đầu mỗi tệp |

---

## 6. Lệnh thường dùng

```bash
# Chạy toàn bộ test (47 giây)
python -m pytest -q

# Chạy hệ thống trên 300 đơn bất mãn
python -m masdss.cli.run_system --stage 2 --n 300

# Tiêm lỗi — cú pháp: kind:component[:field]
python -m masdss.cli.run_system --stage 2 --n 300 --inject crash:prediction
python -m masdss.cli.run_system --stage 2 --n 300 --inject bias:cause_delivery:confidence

# Ablation cho RQ1: tắt tầng chịu lỗi
python -m masdss.cli.run_system --stage 2 --n 300 --no-reliability

# Huấn luyện lại capability + báo cáo hiệu chuẩn
python -m masdss.cli.train

# Sinh lại tệp gán nhãn (tất định — cho đúng mẫu cũ)
python -m masdss.cli.build_goldset

# Sinh tệp gán nhãn vòng 3 (tiếng Bồ + cột tiếng Anh trống, MÙ)
python -m masdss.cli.build_annotation_en

# Đóng băng bản dịch thành artifact có checksum
python -m masdss.cli.freeze_translations

# Kiểm tra gold set + Gate G2 (tự nhận file vòng 3 nếu có)
python -m masdss.cli.check_goldset --require-complete
```

Kịch bản tiêm lỗi: `crash` · `transient` · `constant` · `bias`.
Thành phần: `prediction` · `cause_delivery` · `cause_price` · `cause_quality` · `cause_service` ·
`analytics` · `recommendation` · `critic` · `arbiter` · `rules` · `case_manager`.

---

## 7. Năm quyết định đã chốt, đừng mở lại nếu không có lý do mới

| Quyết định | Lý do | Tiêu chí đảo ngược |
|---|---|---|
| **Tự viết orchestrator**, không dùng LangGraph | RQ1 cần kiểm soát trọn vòng thực thi; tính tất định phải chứng minh được | Mở sang chạy trực tuyến hoặc >15 bước — `technical-plan-v3.md §2.2f` |
| **Parquet + SQLite**, không dịch vụ nền | Không RQ nào cần; mỗi dịch vụ nền làm giảm khả năng tái lập | Như trên |
| **Hai mốc quyết định T₃ / T₄** | Tại T₃ bình luận **chưa tồn tại** (ràng buộc C4) | Không |
| **Monolithic-Complete là đa nhãn** | Nếu đơn nhãn thì MAS thắng tình huống (a) *theo cấu tạo* | Không |
| **3 RQ**, không phải 5 | Giá trị × khả thi; đánh giá chuyên gia thành nhánh tùy chọn | Nếu thầy hướng dẫn yêu cầu giữ tuyên bố về hiệu quả hỗ trợ quyết định → kích hoạt §5.1 |

---

## 8. Nguyên tắc làm việc đã hình thành

Bốn nguyên tắc này đã tự chứng minh giá trị nhiều lần trong phiên vừa rồi:

1. **Chạy sớm trên dữ liệu thật.** Cơ chế phát hiện lỗi hiệu quả nhất — bắt được 6/18 lỗi phương pháp.
   Lỗi thiết kế trông hợp lý trên giấy; chỉ khi có số mới lộ.
2. **Đỏ trước xanh.** Test mới phải được xác nhận **đỏ vì đúng lý do** trước khi tin nó. Chính quy tắc
   này phát hiện T04 — cả một tầng test viết để chặn 4 lỗi mà **không chặn được cái nào**.
3. **Nghi ngờ con số quá đẹp.** ECE = 0,0000 và hỏng âm thầm = 0,0% đều là dấu hiệu của phép đo sai,
   không phải của hệ thống tốt.
4. **Ghi lỗi của chính mình vào tài liệu.** Trong Design Science, quá trình phát hiện và sửa lỗi thiết
   kế **là một phần của đóng góp**. Bốn cái bẫy PSI ở `methodology-log.md §2.6` tự chúng đã là một đóng
   góp phương pháp nhỏ.

---

## 9. Dọn dẹp nhỏ nên làm

`data/v3/runs/` có ~20 thư mục chạy thử tích tụ trong quá trình gỡ lỗi *(`b2`, `c3`, `f0`, `k3`…)*.
Chúng tái tạo được bằng một lệnh nên xóa an toàn; chỉ nên giữ `stage2` và các thư mục có tên gợi nghĩa.
Không có tệp nào trong đó đang được test hay tài liệu tham chiếu tới.

---

## 10. Rà soát tài liệu ↔ mã nguồn *(13/08/2026)*

Đối chiếu toàn bộ `docs/` với `src-v3/` và sửa mọi chỗ lệch. **Tám nhóm lệch** đã xử lý:

| # | Lệch | Xử lý |
|---|---|---|
| 1 | `technical-plan-v3.md` còn dùng **số hiệu RQ cũ** — nó lọt khỏi đợt đồng bộ 12/08 | Đã đổi toàn bộ sang hệ hiện hành, kèm biển báo ở đầu tệp |
| 2 | Tài liệu ghi **4 analyst** gồm `PriceAnalyst`; mã nguồn còn **3** | §A.2, §A.3, §A.6, thang suy giảm, bảng chỉ số đều đã sửa |
| 3 | `architecture.md` mô tả kiến trúc **5 tầng của `src/mas_dss/` đã đóng băng** | Gắn biển ⛔ lỗi thời + bảng năm điểm sai, trỏ sang nguồn chuẩn |
| 4 | Cây thư mục ở `technical-plan-v3.md §4` và `implementation-plan.md §2` **không khớp mã nguồn** | §4 viết lại theo thực tế; `implementation-plan` gắn biển "bản dự kiến" + bảng bốn khác biệt |
| 5 | *"9 performative"*, `reply_by`, `Pydantic`, `LangGraph`, `BERTimbau` | Sửa thành 10 performative · `deadline_ms` · frozen dataclass · orchestrator tự viết · `TfidfCauseHead` |
| 6 | Cặp số **74,71% / 24,6%** trộn hai định nghĩa, còn sót ở 6 chỗ | Thống nhất **74,77% / 25,23%** *(theo `review_content`)* |
| 7 | `build-plan.md` và tệp này **mâu thuẫn nhau** về WP7 và số test *(231 · 211 · 274)* | Đồng bộ theo số đo thật: **274 test xanh**; WP7 🟡 |
| 8 | `build-plan.md §0.6–§0.10` là hồ sơ chạy trước 12/08 nhưng đọc như số hiện hành | Gắn biển ⛔ + bảng *thay đổi nào làm hỏng số nào* |

### ✅ Đã sửa 13/08 — rò rỉ khoảng cách ly và tầng tách dữ liệu không được nối vào

Rà soát phát hiện `data/export.py` *(282 dòng, 3 bất biến)* **đã xây nhưng gần như không gì dùng** —
6/7 điểm chạy vẫn gọi `build_order_table()` + `time_split()` trực tiếp, tức bỏ qua khoảng cách ly và
phép lọc tổng thể. Đo được trên đường cũ: **2.211 dòng val** có đánh giá đến sau `test_start` *(và
isotonic khớp trên chính tập đó)*, **23.193 đơn (23,5%)** không còn kịp can thiệp bị kéo vào huấn
luyện. Cả hai lệch **về phía có lợi cho artifact** — cùng hướng L24 và L37.

| | Trước | Sau |
|---|---|---|
| **PR-AUC test** | 0,3892 · n = 14.801 · nền 10,99% | **0,2381** · n = 11.322 · nền 12,74% |
| `DeliveryAnalyst` khai có bằng chứng | **0/40** | **35/40** |
| Bid thật / case | 0,30 | **0,57** |
| Tỷ lệ đa nguyên nhân | 1,5% | **7,67%** |
| Phạm vi giám sát | 1/4 thành phần | **2/4** |

**Cách sửa:** thêm `load_stage()` làm đường vào chung, chuyển cả 7 điểm chạy sang nó, và **một test
tĩnh chặn đường cũ quay lại** *(`tests-v3/test_data_entrypoint.py`)* — vì ràng buộc này đã được phát
biểu tường minh trong docstring của `export.py` và **vẫn bị vi phạm ở sáu tệp**. Một ràng buộc chỉ tồn
tại trong văn xuôi thì không phải ràng buộc.

**Quyết định kèm theo (13/08):** tổng thể **bất đối xứng** — T₃ lọc `reachable_at_t3`, **T₄ không lọc**.
Lập luận của `chaos/runner.py` đã thắng: điều kiện vào T₄ là *"đã có đánh giá 1–2★"*, không phụ thuộc
T₃ có kịp thấy đơn đó hay không. Lọc cả hai làm mất **1.819/14.475 đơn bất mãn (12,6%)**, và nhóm mất
đi **không ngẫu nhiên**: giao sớm hơn trung bình 13,2 ngày, có văn bản nhiều hơn *(81,6% so với 73,8%)*
— tức phần lớn là khiếu nại **không do giao hàng**. Hồ ứng viên gold set vì vậy rộng từ **1.442 → 2.083**.

### 🔴 Hai phát hiện còn để mở

**1. `BidCalibrator` (T7.3b) đã cài, có test, nhưng KHÔNG có lời gọi nào ngoài `test_calibration.py`.**
Analyst khi đấu thầu vẫn phát **điểm thô**. Hai tài liệu trước đây đọc trái ngược nhau về task này —
một bên ghi ✅ xong, một bên ghi 🔒 bị chặn — và **cả hai đều sai**: năng lực hiệu chuẩn *đã tồn tại*
nhưng hệ thống *chưa dùng*. Chương 4 không được viết "bid đã được hiệu chuẩn".

**2. Nhãn `service` không bao giờ quy kết được — nhưng KHÔNG phải vì cơ chế phối hợp.**

> ⚠️ **Đính chính chẩn đoán ban đầu.** Tôi ghi lỗi này là *"`ServiceAnalyst` không bao giờ thắng thầu
> vì phá thế cân bằng theo bảng chữ cái"*. **Sai.** Sau khi hiệu chỉnh thang rủi ro, đo trên 300 case:
> `ServiceAnalyst` **thắng thầu 92 lần** — và **từ chối cả 92** với lý do *"văn bản không có tín hiệu
> service"*. Cơ chế đấu thầu hoạt động đúng; nút thắt nằm ở **năng lực nền**.

Bộ phân loại `service` của `TfidfCauseHead` gần như không bao giờ vượt `min_confidence = 0,15`. Nguyên
nhân nghi ngờ: `service` là lớp thưa nhất trong weak label *(≈18,8% dương so với 58% của `delivery`)*.

**Việc phải làm:** đo trực tiếp phân bố xác suất đầu ra của head cho `service` trước khi kết luận —
nếu nó thực sự chưa bao giờ vượt ngưỡng thì hoặc ngưỡng đặt sai cho lớp thưa, hoặc weak label cho
`service` quá yếu. **Số của RQ3 chưa dùng được cho tới khi rõ**, kể cả sau khi có gold set.

**3. Tại T₄, bộ OOD từ chối 65/300 case — và 87,7% trong số đó là nhóm mới thêm.**
*(so với 15,7% ở nhóm còn lại)*. Đây là **DP3 hoạt động đúng**: mô hình rủi ro học trên tổng thể T₃
nên những đơn không kịp can thiệp thật sự nằm ngoài phân phối nó đã thấy, và từ chối đúng hơn đoán bừa.

Nhưng nó có hệ quả vận hành phải cân nhắc: `bb.risk = None` ⟹ ngân sách rơi về mức LOW **và**
`build_decision` cưỡng chế `escalate_to_human`. Tức nhóm vừa thêm vào ở quyết định 13/08 phần lớn bị
chuyển giao cho người ngay ở bước dự báo, trước khi tầng quy kết kịp làm gì. Hướng xử lý: ở T₄ **không
chạy bộ dự báo T₃** cho nhóm này, hoặc cấp ngân sách theo một quy tắc riêng của T₄.

### Cố ý KHÔNG sửa

| Tệp | Vì sao giữ nguyên |
|---|---|
| `methodology-log.md`, `thesis-mapping.md` | **Nhật ký và ánh xạ lịch sử** — giữ nguyên văn là đúng; đã có bảng tra số hiệu ở đầu tệp |
| `status-checklist.md §4/§4b` | Bản năm giả thuyết. Viết lại kết luận **trước khi** có số mới là HARKing — đã có biển ❌ |
| `technical-design-v2.md`, `mas-redesign-plan.md` | Đã có biển ⛔ từ trước, giữ làm hồ sơ thiết kế |
| Các bảng số trong `build-plan.md §0.6–§0.10` | Sửa số sẽ **xóa dấu vết** của việc cấu hình đã đổi. Rào lại đúng hơn viết lại |

---

## 11. Phiên 14/08 — 🟢 Gold set về, và bốn thay đổi kéo theo

**295 test xanh.** Lần đầu tiên số quy kết mang `citable = True`.

### 11a. Gold set — cổng G2 ĐẠT

| | |
|---|---|
| Nguồn | `goldset_A_v3_final.csv` + `goldset_B_v3_final.csv`, 300 dòng, hai người gán độc lập |
| **Tính độc lập** | hàng nhãn trùng khớp **77,7%** — *(vòng 3 là 96,4% và đã bị `check_validation` chặn)* |
| **κ trung bình** | **0,784** · delivery 0,774 · quality 0,873 · service 0,801 · unknown 0,688 |
| Đủ dương để tin cậy | **4/4 nhãn** — không nhãn nào rơi vào nghịch lý κ |
| Trùng với vòng 3 | **0 đơn** |
| Bất đồng | 67/300 *(22,3%)* — bỏ sót 53,7% · khác số lượng 43,3% · **xung đột thật 3,0%** |

**Quy tắc hợp nhất: HỢP (OR)**, quyết định của anh. Căn cứ: chỉ 3,0% là xung đột thật; 97% còn lại là
một người thấy thứ người kia không thấy, đúng chế độ hỏng mà codebook §1.2 cảnh báo.
⚠️ **Threats to Validity:** với **2 dòng xung đột thật**, phép hợp gán **cả hai nhãn mâu thuẫn**.

Công cụ mới: `python -m masdss.cli.merge_goldset --a <A> --b <B> --rule union`

### 11b. Bốn thay đổi mã nguồn

| # | Thay đổi | Lý do | Tác động đo được |
|---|---|---|---|
| 1 | **Định tuyến lại lexicon theo codebook** | `faltando` *(thiếu món)* nằm ở `quality` trong khi Quy tắc 1 nói `delivery`. Gold xác nhận **12/12 = 100% delivery** | head macro-F1 **0,6639 → 0,6937**; `quality` precision 0,852 → **0,920** |
| 2 | **`quebrad` theo Ví dụ 12** | Vỡ **trong lúc giao** → `delivery` + `quality`. Chỉ cụm **có ngữ cảnh vận chuyển**; `quebrad` trần giữ ở `quality` *(gold: 7/7 quality, chỉ 2/7 delivery)* | ⚠️ **không kiểm chứng được** — chỉ 1 dòng trong gold set. Train có 92 dòng |
| 3 | **`CombinedDeliverySignal`** — hợp z-score cấu trúc + nhánh văn bản của cause head | Bộ phân loại `delivery` của head đã huấn luyện nhưng **không tác tử nào cắm vào**. Đặt ở `capabilities/` để **cả hai kiến trúc dùng chung** | `delivery` F1 **0,4074 → 0,7302** |
| 4 | **`BUDGET_RATIO["low"]` 0,60 → 0,70** | Xem §11c | `quality` cứu từ 0,2376 về **0,6667** |

### 11c. 🔴 Cái bẫy suýt làm báo cáo sai — L27 lặp lại ở tầng khác

Sau thay đổi 3, `delivery` lên nhưng **`quality` sụp 0,6667 → 0,2376** và macro-F1 tụt 0,4787 → 0,4432.

Nguyên nhân: `delivery` đổi giá 0,3 → 1,6 nên mẫu số `FULL_ANALYST_COST_MS` lên 4,2, và hệ số cũ cho
`0,60 × 4,2 = 2,52 ms` — **không mua nổi** `delivery + một analyst văn bản` *(1,6 + 1,3 = 2,9)*. Mà
chính chú thích của tham số viết *"0,6 → đủ cho analyst giao hàng + đúng một analyst văn bản"*.

> **Tham số đã vi phạm ngữ nghĩa nó tự khai báo.** Hệ số đúng suy từ chính ý định:
> `(1,6 + 1,3) / 4,2 = 0,6905` → **0,70**.
>
> **Bài học:** L27 dạy rằng ngân sách đặt bằng **số tuyệt đối** thì vô nghĩa khi giá đổi, nên chuyển
> sang **tỷ lệ**. Nhưng chính tỷ lệ đó mã hóa *"bao nhiêu analyst được chạy"* — nên khi **cơ cấu chi
> phí** đổi, tỷ lệ vẫn phải tính lại. *Một tham số tự điều chỉnh theo giá vẫn không tự điều chỉnh theo
> cơ cấu.* Nếu không đối chiếu tham số với chú thích của chính nó, phương án (c) đã bị báo cáo là
> **thất bại**.

### 11d. Kết quả T₄ — chấm trên gold set, `citable = True`

| Nhãn | MAS-DSS | Đơn khối |
|---|---|---|
| `delivery` | **0,7302** | 0,7302 — giống hệt |
| `quality` | **0,6667** | 0,6667 — giống hệt |
| **`service`** | **0,3619** | **0,6618** ❌ |
| **macro-F1** | **0,5862** | **0,6862** |

Diễn tiến macro-F1 MAS trong phiên: `0,4724 → 0,4787 → 0,4432 (bẫy) → 0,5862`.
Không quy kết được **54,7% → 28,3%** · đa nguyên nhân **9,3% → 23,3%** · quy kết/ms **0,0578 → 0,0887**.

**Toàn bộ khoảng cách còn lại nằm ở `service`,** và nguyên nhân đã xác định: hai analyst văn bản khai
`prior_confidence` từ **cùng một đối tượng head** nên hòa tuyệt đối; quy tắc phá hòa rơi xuống **thứ tự
bảng chữ cái**, `service` thua **177/300** phiên. **Đã chứng minh sửa `prior_confidence` riêng KHÔNG
giải quyết được: 0/300 đơn đổi phân bổ** — vì `quality` vốn có tiên nghiệm cao hơn *(0,5787 > 0,5562)*.

### 11e. Cố ý KHÔNG làm

| | Vì sao |
|---|---|
| `prior_confidence` riêng từng analyst | Đã đo: **0/300 đơn đổi phân bổ**. Chỉ thay một lý do xấu bằng một lý do đẹp |
| Nâng `BUDGET_RATIO` để `service` luôn chạy | Sẽ kéo `budget_binds_rate` về 0 ⟹ Contract Net chạy mà **không quyết định gì** |
| Chuyển `quebrad` trần sang `delivery` | Gold nói ngược: 7/7 `quality`, chỉ 2/7 `delivery` |

### 11f. Chịu lỗi — đã chạy lại sau khi đổi cơ cấu chi phí *(200 case × 15 kịch bản)*

| Nhóm | Guard *thiết kế để bắt*? | Phát hiện | Trễ | Quyết định **đổi thật** | MAS âm thầm | Đơn khối |
|---|---|---|---|---|---|---|
| crash 1·2·3 | ✅ | ❌ | — | 57,0 → 81,5% | **0,0%** | **0,0%** |
| hang 1·2·3 | ✅ | ❌ | — | 57,0 → 81,5% | **0,0%** | **0,0%** |
| byzantine thô 1·2·3 | ✅ | ✅ | 20 | 49,5% | **0,0%** | **84,5 → 99,0%** |
| **drift** 1·2·3 | ❌ | ❌ | — | 3,5 → 7,5% | **2,5 → 5,0%** | 3,5 → 6,5% |
| **bias** 1·2·3 | ❌ | ✅ | 100 | 20,0% | **0,0%** | 25,0 → 84,5% |

Đường khỏe: **0,0% suy giảm · 0 guard chặn · báo động giả = 0** — điều kiện để mọi số trên có nghĩa.

**Ba điều đọc đúng từ bảng này:**

1. **Ưu thế của MAS nằm trọn ở nhóm lỗi *không ném ngoại lệ*.** `crash`/`hang` cả hai đều 0,0% —
   `try/except` là đủ. Chênh lệch chỉ ở `byzantine` và `bias`: lỗi **trả về giá trị hợp lệ nhưng sai**.
2. **Chỉ hai dòng `designed_for = False` là kết quả thực nghiệm.** `bias` — guard bắt được **dù không
   được thiết kế cho nó** *(0,0% vs 84,5%)*. `drift` — **cả hai gần mù**, đây là giới hạn thật.
3. **Cột "quyết định đổi thật" tách hai thứ mà chỉ số cũ trộn.** Ở `crash` mức 3, **81,5%** quyết định
   thay đổi nhưng âm thầm **0,0%**: hệ bị ảnh hưởng nặng mà **cảnh báo đủ mọi ca**. Đó mới là điều H2
   tuyên bố.

### 11g. Bộ giả thuyết sau phiên này

| | Phát biểu | Phán quyết |
|---|---|---|
| **H1** | Ba kiến trúc **tương đương** độ chính xác | 🔴 **BÁC BỎ ở T₄** — MAS 0,5862 vs đơn khối 0,6862. Tại **T₃ vẫn tương đương** *(khác 4/300 đơn, đúng các ca `REFUSE`)* |
| **H2** | Hỏng âm thầm thấp hơn trên **toàn bộ** bề mặt hỏng | 🟡 **Đúng trên thành phần dùng chung**; nhóm chỉ-MAS chưa đo lại |
| **H3** | Phát hiện drift **trước khi** chất lượng suy giảm | 🔴 **BÁC BỎ** — không phát hiện ở cả ba mức |

### 11h. Artifact sinh ra, tất cả `citable = True`

```
data/v3/goldset/gold_labels.csv · gold_merged.csv + _meta.json
data/v3/goldset/agreement_report_v3.csv · validation_report.csv
data/v3/evaluation/attribution_per_{cause,slice}.csv · selective_summary.csv
data/v3/chaos_v3/{scenarios,sensitivity_curve}.csv
```

**Sinh lại toàn bộ bằng sáu lệnh:**

```bash
python -m masdss.cli.merge_goldset --a data/v3/goldset/goldset_A_v3_final.csv \
                                    --b data/v3/goldset/goldset_B_v3_final.csv --rule union
python -m masdss.cli.build_goldset --source data/v3/goldset/gold_merged.csv \
                                    --provenance human_independent
python -m masdss.cli.export_features
python -m masdss.cli.train
python -m masdss.cli.run_attribution --run data/v3/runs/goldset_v3
python -m masdss.cli.run_chaos --n 200 --out data/v3/chaos_v3
```

---

## 12. Phiên 14/08 tối — thu gọn phạm vi, sửa phương pháp đánh giá, viết Chương 5

**300 test xanh · 6/6 cổng đạt · Chương 5 đã viết (12 mục).**

### 12a. Bốn quyết định phạm vi *(anh quyết)*

| # | Quyết định | Hệ quả lớn nhất |
|---|---|---|
| 1 | Bỏ vế *"toàn bộ bề mặt hỏng"* của H2 | không đo nhóm chỉ-MAS, không mở guard sang 4 thành phần đó |
| 2 | Rút số 11,0% *(`chaos_masonly`)* khỏi luận văn | artifact chuyển sang `data/v3/_ngoai_pham_vi/` kèm README |
| 3 | **Sửa phát biểu H2** cho khớp phạm vi mới | ⚠️ HARKing — giảm rủi ro bằng hồ sơ sửa đổi giữ nguyên văn bản gốc |
| 4 | **Bỏ ràng buộc ngân sách khỏi cấu hình chính** | MAS ≡ Đơn khối = **0,6862** ⟹ H1 đứng vững ở cả hai mốc |

### 12b. 🔴 Bốn khiếm khuyết của phương pháp đánh giá, đã sửa — L38 đến L43

| Mã | Khiếm khuyết | Hậu quả nếu không sửa |
|---|---|---|
| **L38** | `selective_curve.csv` cắt mức phủ theo **thứ tự dòng**, không theo độ tin cậy | tệp vẫn sinh ra và vẫn đọc được như đường risk–coverage — nhưng nó là cắt ngẫu nhiên |
| **L39** | McNemar + KTC bootstrap **chỉ có trong văn bản**, không hàm nào tính | hai con số phán quyết H1 không tái lập được bằng lệnh |
| **L40** | Hai hàm `expected_calibration_error` khác nhau ở biên | điểm bằng đúng 0,0 rơi ngoài mọi bin, bị bỏ qua im lặng |
| **L41** | Sửa L37 chỉ áp ở `chaos/runner.py`, `evaluation/resilience.py` vẫn bản cũ | hai nơi cho hai con số khác nhau trên cùng lần chạy |
| **L42** | `budget=None` bị hiểu là ngân sách **bằng 0** ⟹ từ chối toàn bộ analyst | **0%** case được quy kết, giao thức vẫn chạy đủ hai pha nên không có gì báo |
| **L43** | 🔴 **Bộ tiêm Byzantine không tới đường quyết định của MAS** | *"MAS hỏng âm thầm 0,0%"* ở byzantine/bias **không đo chịu lỗi** — nó phản ánh chỗ đặt bộ tiêm |

**L43 chi tiết.** `PredictionAgent` phát ra `risk_score` *(nguồn)* và `risk` *(dẫn xuất)*; bộ tiêm đầu
độc `risk_score`, quyết định đọc `risk`. Đơn khối thì `guard_call` bọc hàm trả về **số trần** nên bị
thay cả giá trị. Đo trên 200 case, `byz_gross_k2`, tầng chịu lỗi TẮT: mức rủi ro của MAS **y hệt đường
khỏe** *(122/50/28)*, của đơn khối **200× HIGH**.

Sửa: thông điệp mang theo `risk_thresholds` *(cũng phục vụ DP4)*, `_recompute_derived()` suy lại mức
sau khi nguồn bị đầu độc, và test parity canh **cả hai** đường quyết định.

> **L36 · L37 · L43 là ba bản lặp của cùng một cơ chế** — phép đo không đo thứ nó tuyên bố đo. Cả ba
> nghiêng về phía **có lợi cho artifact**, và **không lỗi nào làm chương trình đổ**.

### 12c. Số hiện hành sau khi sửa

**Dự báo T₃** — PR-AUC **0,2381** [0,2187 ; 0,2578] · lift **1,87×** · ngưỡng chi phí **0,194** ·
thang rủi ro **0,160 / 0,3103** · ECE **0,0696 → 0,028** · Brier skill **−0,0217 → +0,0328**.
⚠️ Accuracy thô **0,6902** < mốc tầm thường **0,8726**.

**Quy kết T₄** *(`citable = True`)* — `delivery` **0,7302** · `quality` **0,6667** · `service`
**0,6618** · macro-F1 **0,6862**, **hai hệ trùng khít**, **0/900 ô bất đồng**. Không quy kết 24,67%.
Đa nguyên nhân *(n=71)* **0,7353**. Selective: độ phủ 0,7533 · quy kết sai khi người bỏ trống **0,5**.

**Tập luật** — T₄: 11 tổ hợp luật×nguyên nhân; **24,67%** chuyển giao cho con người. T₃: thang 7 mức,
lift đơn điệu **0,715 → 4,332**; can thiệp 31,64%, bắt 51,11% đơn bất mãn.

**Chịu lỗi** *(200 case × 16 kịch bản, bề mặt dùng chung)*

| Nhóm | Ném ngoại lệ | MAS âm thầm | Đơn khối |
|---|---|---|---|
| crash · hang | ✔ | **0,0%** | **0,0%** |
| **byzantine** | ✘ | **5,0%** | **84,5 → 99,0%** |
| **bias** | ✘ | **8,5 → 21,0%** | 25,0 → 84,5% |
| **drift** | ✘ | 2,5 → 5,0% | 3,5 → 6,5% |

Đường khỏe: 0,0% suy giảm · 0 guard chặn · **báo động giả 0**. **Cổng G5 ĐẠT.**

**Bốn ablation** — DP1 **5,0% ↔ 34,0%** · DP2 **0 ↔ 0** · DP3 **0,5 ↔ 1,0** · DP4 **0 ↔ 0,4061**.

**Chi phí** — bề mặt hỏng **10 vs 5** · **114,6 vs 9,2 ms/case** *(wall-clock cả hai vế; chậm hơn
**12,5–17,9 lần**, trong đó ~65,7 ms là ghi nhật ký)* · **447 + 671 = 1.118 dòng mã** · 21,16
message/case · **1,94 REFUSE/case**.

🔴 **L46 — số cũ *(10,96 vs 10,82 → +10,5 giây/lô)* đã rút.** Hai vế đo bằng hai cơ sở khác nhau, cả
hai sai lệch đều có lợi cho MAS. Lượt chạy nguồn hiện hành: `data/v3/runs/stage2_nobudget`.
🔴 **L47** — `coordination.csv` từng được tính từ `stage2`, lượt chạy **còn bật ngân sách**.

### 12d. Artifact mới sinh

```
docs/artifact-register.md          docs/evaluation-handbook.md
docs/thesis/ch5-ket-qua-ban-luan.md   (12 mục, ~700 dòng)
data/v3/evaluation/attribution_compare.csv      control_condition.csv
data/v3/evaluation/ablations.csv + ablation_dp{1,3,4}_*     gate_g5_tai_lap.json
data/v3/evaluation/rules_{1,2,3}_*.csv
src-v3/masdss/cli/run_ablations.py    run_rules_report.py
```

### 12e. Việc còn lại *(đã cập nhật ở §13e — đọc bản đó)*

---

## 13. Phiên 14/08 khuya — Phụ lục A, và hai câu hỏi kiến trúc

**301 test xanh.** Không hạng mục nào chặn số liệu.

### 13a. Phụ lục A đã viết — `docs/thesis/phu-luc.md`

**11 mục, 22 bảng, ~18 trang.** Đặc tả thuật toán dự báo tại T₃: dữ liệu nguồn · hai vế của mốc quyết
định · **16 đặc trưng kèm công thức** · chia tập và khoảng cách ly · siêu tham số và hiệu chuẩn · **độ
quan trọng đặc trưng** · runbook tái lập · giới hạn · **giao thức thay mô hình**.

Mục dài nhất là **§A.4.2 — kiểm duyệt bên phải**, viết theo trình tự *ý tưởng trước, công thức sau*:
ẩn dụ bức ảnh chụp lúc ngày thứ bảy → hai cách xử lý sai và hậu quả → nguyên tắc chặn dưới → **ba đơn
hàng thật** → công thức.

> **Đơn minh họa đắt giá nhất *(Bảng A.4)*:** tại mốc, hệ thống chỉ biết đơn **đã quá hạn 2,91 ngày**;
> kết cục thật là **7,05 ngày**. Chênh 4,14 ngày ấy chính là thứ không được phép dùng.

### 13b. Ba số đo mới, đáng chú ý

| Phát hiện | Số |
|---|---|
| **Cộng tuyến hai đặc trưng T₃** — `observed_delay_days` ↔ `days_to_deadline` | tương quan **−0,9998** toàn tập; bằng nhau **chính xác** trên **96,68%** số dòng |
| ⟹ T₃ chỉ bổ sung **ba** chiều thông tin mới, không phải bốn | `days_to_deadline` thực chất tính được từ T₁ |
| **Một vùng đặc trưng KHÔNG có dữ liệu huấn luyện** | `days_to_deadline < 0`: **0**/52.835 train · **0**/9.077 val · **159**/11.322 test |
| Khối điểm tại biên | `observed_handover_days = 7,0` trên **13,64%** số dòng |

**Hệ quả của phát hiện thứ hai**, đã ghi vào §A.10.1: mô hình **ngoại suy** ở vùng đó. Hai luật hành
động T₃ phụ thuộc điều kiện này, và luật có lift cao nhất *(4,332)* đo trên **29 đơn** thuộc vùng ấy.

### 13c. Artifact và mã nguồn mới

```
docs/thesis/phu-luc.md                          (Phụ lục A, 11 mục)
src-v3/masdss/cli/feature_importance.py         (gain/split + permutation, tất định)
data/v3/evaluation/feature_importance.csv       (16 đặc trưng × 3 phép đo)
data/v3/features/t3_design_{train,val}.parquet  (ảnh chụp ma trận thiết kế, 16 cột, sha256)
```

`RiskModel.design_matrix()` — phương thức công khai xuất **đúng ma trận mô hình nhìn thấy**. Kèm test
canh trong `test_export.py`: không cột nào có `available_at = T4`. Test **không rỗng** — dùng
`FeatureSet(T4)` thì nó bắt đúng sáu cột.

### 13d. Hai lỗi bước đối chiếu chéo bắt được — L44, L45

| Mã | Lỗi |
|---|---|
| **L44** | `config.py` **vẫn giữ nguyên** khẳng định mà L35 đã ghi nhận là sai — *"+7 · lift 2,19 · đạt đỉnh"*. Đó là nơi phụ lục kỹ thuật sẽ trích, nên nó **suýt đưa một khẳng định đã bị bác bỏ trở lại luận văn**. Đã viết lại theo Bảng 3.5 |
| **L45** | Sau khi hợp nhất hai cài đặt ECE *(L40)*, giá trị đúng đổi **0,0283 → 0,028**, nhưng `train` chưa chạy lại ngay nên ba tài liệu vẫn trích số cũ. Bài học: **sửa một hàm tính thì chạy lại MỌI lệnh sinh số phụ thuộc nó**, không chỉ lệnh gần nhất |

Đồng thời sửa: `manifest` nay ghi **cả hai** con số khoảng cách ly — T₃ `1 + 2.245 = 2.246` và T₄
`1 + 2.351 = 2.352`, kèm nhãn phạm vi. Chênh **106 dòng** đã truy ra: đơn `reachable_at_t3 = False` có
đánh giá đến sau mốc. Cả hai phép trừ nay khớp. Gỡ bí danh `RISK_THRESHOLDS`; sửa chú thích
`train.py:60`; đổi tên `hinh-4-4-be-mat-hong.png` → `hinh-4-3` cho khớp nhãn.

### 13e. 🔴 Hai việc ĐANG CHỜ QUYẾT — làm tiếp từ đây

#### (1) LangGraph — đã phân tích, **kết luận KHÔNG chuyển**

Căn cứ: `technical-plan-v3.md` §2.2(f) đã khai báo trước **bốn tiêu chí đảo ngược**, và **không tiêu chí
nào đúng** — 7 bước *(dưới ngưỡng 15)*, không chu trình, chạy theo lô một tiến trình, không có
human-in-the-loop đồng bộ.

Ba ràng buộc thật sự chặn *(không phải tính truy vết — thứ đó sống sót được)*: vòng thực thi là **dụng
cụ đo** của RQ1 · cổng G5 chuyển từ **bảo đảm** thành **cấu hình** · bề mặt hỏng bị lệch nghĩa. Bằng
chứng mới: **L43** vừa được tìm ra nhờ đọc được toàn bộ đường đi trong vài tệp.

**Hai việc đề xuất, cả hai chỉ là viết:**

| | Việc | Giá trị |
|---|---|---|
| **A** | Chuyển §2.2(f) từ danh sách thành **bảng có số đo** | Biến bốn tiêu chí định tính thành **bằng chứng kiểm được** — đúng thứ hội đồng sẽ hỏi |
| **B** | Một đoạn ở **Chương 6**: kiến trúc và bốn nguyên lý **độc lập với engine điều phối**; hiện thực lại trên LangGraph là **phép kiểm tính chuyển giao** | **Làm mạnh** tuyên bố về Design Principles theo Gregor & Hevner |

#### (2) ⚠️ Cái giá của hiệu chuẩn — phát hiện CHƯA có trong luận văn

Đo được khi giải thích chỉ số ECE:

| | Số giá trị khác nhau |
|---|---|
| Điểm thô | **11.288** / 11.322 |
| Sau isotonic | **93** / 11.322 |

Isotonic là hàm bậc thang: **giữ nguyên thứ tự** *(đã kiểm — đơn điệu không giảm, Spearman 0,9987)*
nhưng **gộp 11.288 mức phân giải xuống 93 bậc**. Hai đơn trước phân biệt được nay bằng điểm nhau.

Hệ quả: PR-AUC **0,2484** *(thô)* → **0,2381** *(hiệu chuẩn)*.

⚠️ **Phát biểu cho đúng mức:** chênh **−0,0103** nằm **gọn trong khoảng tin cậy** [0,2187; 0,2578] nên
**không** kết luận được là suy giảm có ý nghĩa thống kê. Nhưng **cơ chế** thì chắc chắn và đo được — nó
là hệ quả cơ học của việc tạo trùng hạng, không phải nhiễu.

**Phát biểu đúng:** *hiệu chuẩn đổi một phần độ phân giải xếp hạng lấy sự trung thực của xác suất.* Với
hệ này là đánh đổi **đúng** — mọi ngưỡng quyết định *(0,160 · 0,3103 · 0,194)* áp thẳng lên xác suất.
Nhưng nó **là một đánh đổi**, và luận văn hiện trình bày hiệu chuẩn như thuần lợi.

Con số **0,2381** trong Chương 5 là số **sau hiệu chuẩn**, tức đã tính cả cái giá này — **không có gì
sai**, chỉ thiếu một câu giải thích.

**Việc đề xuất:** ba dòng vào **§A.6.2** và một câu vào **ch5 §5.3**. Số đã có sẵn, chỉ là viết.

### 13f. Việc còn lại, theo thứ tự

| # | Việc | Chặn gì |
|---|---|---|
| **1** | **Hai việc chờ quyết ở §13e** *(LangGraph A+B · đánh đổi hiệu chuẩn)* — cả ba chỉ là viết | không chặn gì |
| **2** | **Chương 6** và **danh mục tài liệu tham khảo** — hai tệp chưa tồn tại / còn trống | **nộp luận văn** |
| **3** | **Đối chiếu trích dẫn Chương 2** với bản gốc; gỡ khối *"xóa trước khi nộp"* ở dòng 3–5 | **nộp luận văn** |
| 4 | IMP-4 → IMP-7 trong `methodology-log.md` | kỷ luật phương pháp |
| 5 | Dọn ~45 thư mục chạy thử trong `data/v3/runs/` | vệ sinh kho |

---

## 14. Phiên 15/08 — §5.7 bằng chứng kỹ thuật, và hai lỗi đo nghiêm trọng

### 14a. Chương 5 — đã viết thêm

| Mục | Nội dung |
|---|---|
| **§5.2.5** | Tóm tắt bốn quyết định thiết kế mô hình, trỏ Phụ lục A cho đặc tả đầy đủ |
| **§5.6.5** | Lỗi đo mới *(L46/L47)*; **§5.6.6** đổi *"bốn lỗi"* → **năm lỗi**, *"ba trong bốn"* → **bốn trong năm** |
| **§5.7** | Viết lại toàn bộ, tám tiểu mục: **Hình 5.1** sơ đồ tuần tự · **Bảng 5.15** trường phong bì + JSON thật · **Bảng 5.16** tần suất mười performative · **Bảng 5.17** một phiên trọn vẹn · **§5.7.5** quy trình tái hiện + **Bảng 5.18** artifact · **Bảng 5.19** bốn ràng buộc kỹ thuật · **Bảng 5.20** số liệu phối hợp · **§5.7.8** điều phải nói thẳng |
| **§5.9** | Tách **§5.9.1/§5.9.2**; §5.9.2 là phần đính chính độ trễ |
| **§5.10.4** | Sửa ví dụ: bản trước mô tả một phiên vừa có `REFUSE` vừa có `CHALLENGE` — nhật ký cho thấy **không phiên nào** như vậy *(phiên 22 tin không bao giờ có chất vấn; phiên có chất vấn là 24 tin)* |

Số bảng: **29**, không trùng. Đối chiếu chéo **30/30 đạt** *(script trong lịch sử phiên)*.

### 14b. 🔴 L46 — hai vế của một phép so sánh đo bằng hai cơ sở khác nhau

Hàng *"thời gian xử lý mỗi case"* so `sum(span.duration_ms)` của MAS với **wall-clock của một vòng lặp
chạy cả ba baseline** cộng `json.dumps`. Một vế bị **hạ thấp** *(span bỏ qua glue + toàn bộ phần ghi
nhật ký)*, một vế bị **nâng cao**. **Cả hai sai lệch đều có lợi cho MAS.**

| | Số công bố cũ | Số đúng |
|---|---|---|
| MAS-DSS | 10,96 ms | **114,6 ms** *(khoảng 115–130 qua bốn lượt)* |
| Đơn khối | 10,82 ms | **9,2 ms** *(khoảng 6,8–9,2)* |
| Chênh | +10,5 giây/lô *(+1,3%)* | **chậm hơn 12,5–17,9 lần** — 144 phút so với 11,6 phút |

**Phân rã:** ~65,7 ms/case *(≈53%)* là nhật ký `commit` **từng thông điệp** — 6.348 lần commit tốn
19,7 giây, gộp một lần chỉ 23 ms. Đây là chi phí **hiện thực**, không phải kiến trúc. **Giữ nguyên có
chủ đích**: thí nghiệm crash ở §5.8 cần từng thông điệp bền vững trước khi tiến trình chết. Trừ hẳn
phần này, MAS vẫn chậm hơn **~5 lần**.

**Đã sửa:** `run_system.py` đo wall-clock cho **cả hai** trong cùng tiến trình, đồng hồ baseline chỉ ôm
`mono.run`; `cost.latency()` lấy `ms_moi_case` từ báo cáo cho cả hai vế, `sum_span` xuống cột riêng ở
vai **chặn dưới**. Canh bằng hai test mới *(đã kiểm đỏ-trước)*.

**Kết luận bị đổi:** mệnh đề *"cái giá về thời gian không có ý nghĩa vận hành"* **không còn đứng vững**.
Đã rút ở ch5 §5.9.2, sổ tay đánh giá §6, `status-checklist` §1.3, `research-questions-objectives` H5.

### 14c. 🔴 L47 — artifact báo cáo tính từ lượt chạy sai cấu hình

`coordination.csv` *(nguồn Bảng 5.20)* được tính từ `data/v3/runs/stage2` — lượt chạy **còn bật ngân
sách** *(`budget_ms = 1,74`, phát **223** `REJECT_PROPOSAL`, chỉ trao **677/900** thầu)*. Nhưng §5.7.8
khẳng định *"tỷ lệ bị loại 0,0%"*. Hai bảng cạnh nhau mô tả **hai cấu hình khác nhau**.

Phát hiện nhờ: 19,38 tin/case của bảng **không khớp** 21,30 của nhật ký goldset.

**Lượt chạy nguồn chính tắc nay là `data/v3/runs/stage2_nobudget`**, ghi rõ trong sổ tay đánh giá.

### 14d. Sửa kèm

- `REJECT_PROPOSAL` **không chết** — không xuất hiện ở đường khỏe nhưng phát **1.200 lần** dưới tiêm lỗi
  *(`crash_k2` 200 · `crash_k3` 400 · `hang_k2` 200 · `hang_k3` 400)*. Cơ chế: analyst hỏng trong pha 1
  nên không khai báo, vòng trao thầu duyệt theo **danh sách tác tử** chứ không theo danh sách bản khai.
  Đã sửa ở **bốn nơi**: ch5 §5.7.3, Phụ lục B §B.5.1, `status-checklist` §2.4, `plan.py`.
- `FAILURE` và `NOT_UNDERSTOOD` **chưa bao giờ được phát** trên cả 16 kịch bản — báo cáo nguyên trạng.
- Số đếm lỗi phương pháp lệch nhau ở bốn tài liệu *(37 / 43 / 45)* — thực tế **L01–L47 = 47**, đã đồng bộ.
- Bảng 5.28: hàng *"Chất vấn"* 226 thực ra là **43 chất vấn + 183 thông qua**; đã sửa nhãn.
- **Giới hạn mới nêu ở §5.7.4:** hành động cuối *(`escalate_to_human`)* khác thông điệp cuối của tác tử
  Luật *(`return_replacement_offer`)* — phép biến đổi nằm ở `build_decision`, **không phải một thông
  điệp**. Nhật ký là bản ghi đầy đủ của *quá trình phối hợp*, không của *toàn bộ đường tới hành động*.

**303 test xanh** *(thêm 2)*.

### 13g. Lệnh sinh lại toàn bộ số của tầng dự báo

```bash
python -m masdss.cli.export_features       # 9 parquet + manifest
python -m masdss.cli.train                 # model + 2 ảnh chụp + 4 báo cáo
python -m masdss.cli.run_evaluation        # forecasting, control_condition, cost
python -m masdss.cli.feature_importance    # độ quan trọng đặc trưng
```
