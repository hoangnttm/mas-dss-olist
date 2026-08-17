# Luận văn — mục lục, ngân sách trang và bảng truy nguồn

> **Đây là file điều phối, không phải nội dung luận văn.** Nó trả lời ba câu: mỗi chương nằm ở đâu,
> mỗi chương dài bao nhiêu, và **mỗi con số trong luận văn lấy từ đâu**.
>
> Cập nhật: **12/08/2026**

---

## 1. Danh sách file

| Chương | File | Trang dự kiến | Trạng thái |
|---|---|---|---|
| **1** | [ch1-gioi-thieu.md](ch1-gioi-thieu.md) | 14 | ✅ bản thảo đầy đủ |
| **2** | [ch2-co-so-ly-thuyet.md](ch2-co-so-ly-thuyet.md) | 22 | 🟡 bản thảo đầy đủ · **trích dẫn chưa đối chiếu bản gốc** |
| **3** | [ch3-phuong-phap.md](ch3-phuong-phap.md) | 24 | ✅ bản thảo đầy đủ |
| **4** | [ch4-thiet-ke-hien-thuc.md](ch4-thiet-ke-hien-thuc.md) | 26 | ✅ bản thảo đầy đủ *(đã đồng bộ số 14/08)* |
| **4?** | [ch4-phuong-phap-danh-gia.md](ch4-phuong-phap-danh-gia.md) | 16 | 🟡 **bản thảo mới 17/08 — CHƯA tích hợp.** Chương "Phương pháp đánh giá" đứng riêng, biên tập từ ch3 §3.6–§3.11 + evaluation-handbook. Nếu nhận làm Chương 4 thì hai chương sau phải đánh số lại; nếu không, dùng làm nguồn thay thế cho các mục tương ứng của ch3 |
| **5** | [ch5-ket-qua-ban-luan.md](ch5-ket-qua-ban-luan.md) | 22 | 🟡 **đang viết** |
| **6** | [ch6-ket-luan.md](ch6-ket-luan.md) | 8 | ⬜ **chưa tạo tệp** |
| — | [tai-lieu-tham-khao.md](tai-lieu-tham-khao.md) | 4 | ⬜ **trống** |
| — | [phu-luc.md](phu-luc.md) | 42 | 🟡 **A + B + C xong** — A: thuật toán dự báo tại T₃ · B: kiến trúc phối hợp và tính truy vết · C: dữ liệu *(bản thảo 17/08 — khai phá, đặc trưng T₃/T₄, quy tắc gán nhãn; người yêu cầu gọi là "Phụ lục 2")* |
| | | **≈ 120** | |

*Quy đổi: 1 trang A4 ≈ 400 từ tiếng Việt, cỡ chữ 13, giãn dòng 1,5; bảng và hình tính riêng.*
*Khung cho phép 70–120 trang; bản này nhắm cận trên vì phần phản tư phương pháp và phần kết quả âm
đều cần trình bày đầy đủ mới có giá trị.*

---

## 2. Nguồn của mỗi con số

**Nguyên tắc: không con số nào trong luận văn được gõ tay.** Mỗi số phải truy được về một tệp sinh ra
bởi mã nguồn, hoặc một mục trong nhật ký phương pháp. Bảng này là hợp đồng đó.

| Nhóm số liệu | Nguồn chuẩn | Sinh lại bằng |
|---|---|---|
| Thống kê mô tả M0 | `research-questions-objectives.md` §0.1 | `masdss.data.load.describe_m0()` |
| Tổng thể T₃, chia tập, tỷ lệ nền | `data/v3/features/manifest.json` | `python -m masdss.cli.export_features` |
| Chỉ số dự báo *(PR-AUC, precision@k, hiệu chuẩn)* | `data/v3/evaluation/forecasting.csv` | `python -m masdss.cli.run_evaluation` |
| Điều kiện kiểm soát H1 + TOST | `data/v3/evaluation/control_condition.csv` | `python -m masdss.cli.run_evaluation` |
| **Quy kết nguyên nhân** | `data/v3/evaluation/attribution_per_{cause,slice}.csv` | `python -m masdss.cli.run_attribution` |
| **Đối đầu hai kiến trúc** *(McNemar + KTC)* | `data/v3/evaluation/attribution_compare.csv` | `python -m masdss.cli.run_attribution` |
| **Selective prediction** | `data/v3/evaluation/selective_{curve,summary}.csv` | `python -m masdss.cli.run_attribution` |
| **Tập luật hỗ trợ quyết định** | `data/v3/evaluation/rules_{1,2,3}_*.csv` | `python -m masdss.cli.run_rules_report` |
| **Bốn ablation cho bốn nguyên lý** | `data/v3/evaluation/ablations.csv` | `python -m masdss.cli.run_ablations` |
| **Độ quan trọng đặc trưng** *(Phụ lục A)* | `data/v3/evaluation/feature_importance.csv` | `python -m masdss.cli.feature_importance` |
| **Ảnh chụp ma trận thiết kế** *(Phụ lục A)* | `data/v3/features/t3_design_{train,val}.parquet` | `python -m masdss.cli.train` |
| Kết quả chaos — bề mặt dùng chung | `data/v3/chaos_v3/{scenarios,sensitivity_curve}.csv` | `python -m masdss.cli.run_chaos` |
| Chi phí *(bề mặt hỏng, giây mỗi lô, quy mô mã)* | `data/v3/evaluation/cost_*.csv` | `python -m masdss.cli.run_evaluation` |
| Phối hợp tác tử | `data/v3/evaluation/coordination{,_detail}.csv` | `python -m masdss.cli.run_evaluation` |
| Đồng thuận hai người gán | `data/v3/goldset/agreement_report_v3.csv` | `python -m masdss.cli.check_goldset` |
| **Cổng G5 — tái lập** | `data/v3/evaluation/gate_g5_tai_lap.json` | hai lượt `run_system`, đối chiếu `sha256` |
| Nhật ký lỗi phương pháp | `methodology-log.md` | — |

**Định nghĩa từng chỉ số, ràng buộc cưỡng chế nó, và nhãn *kiểm tra đặc tả / kết quả thực nghiệm***:
[evaluation-handbook.md](../evaluation-handbook.md). Đó là nguồn chuẩn duy nhất cho câu hỏi *"số này
có trích được không"* — không duy trì danh sách thứ hai.

---

## 3. Trạng thái số liệu — điều phải kiểm trước khi nộp

*Cập nhật 14/08/2026 — sau khi gold set về và ràng buộc ngân sách được gỡ khỏi cấu hình báo cáo.*

| | Trạng thái |
|---|---|
| Thống kê mô tả · chia tập · tổng thể | ✅ **hiện hành** |
| Tầng dự báo tại T₃ | ✅ **hiện hành** *(mốc ngày mua + 7)* |
| Điều kiện kiểm soát H1 + TOST | ✅ **hiện hành** — *kiểm tra đặc tả, không phải kết quả thực nghiệm* |
| **Quy kết nguyên nhân tại T₄** | ✅ **hiện hành** · `citable = True` |
| **Cohen's κ giữa hai người gán** | ✅ **κ = 0,784**, 4/4 nhãn đủ tin cậy — cổng G2 đạt |
| **Tập luật hỗ trợ quyết định** | ✅ **hiện hành** — ba bảng, cả hai mốc |
| **Bốn ablation cho bốn nguyên lý** | ✅ **hiện hành** · `citable = True` |
| Chịu lỗi — **bề mặt dùng chung** | ✅ **hiện hành** *(sau khi sửa L37 và gỡ ngân sách)* |
| Chịu lỗi — bề mặt chỉ-MAS | ⛔ **ngoài phạm vi** — xem `research-questions-objectives.md` §3, hồ sơ sửa H2 |
| Chi phí · phối hợp | ✅ **hiện hành** |
| **Cổng G5 — tái lập từng byte** | ✅ **ĐẠT** — hai lượt chạy trùng `sha256` |

**Không còn ô chờ nào.** Điều kiện để mọi số ở trên có nghĩa: cổng G5 đã xanh, và đường chạy khỏe cho
0% suy giảm · 0 guard chặn · báo động giả bằng 0.

---

## 4. Bảng ký hiệu — tra cứu mọi mã hiệu

> **Nguyên tắc viết đã áp dụng:** mỗi lần nhắc tới một câu hỏi, giả thuyết, ràng buộc hay nguyên lý,
> văn bản ghi **tên mô tả của nó**, kèm mã hiệu trong ngoặc và mục chứa phát biểu gốc. Mã hiệu trần
> *(kiểu "xem C5", "phục vụ RQ2")* **không** được dùng trong văn xuôi — người đọc không phải nhớ bảng
> mã để theo dõi lập luận. Bảng dưới là lưới an toàn khi mã hiệu xuất hiện trong bảng biểu.

### Câu hỏi nghiên cứu

| Mã | Tên gọi trong văn bản | Nội dung | Phát biểu gốc |
|---|---|---|---|
| **RQ1** | **câu hỏi chịu lỗi** | hai kiến trúc khác nhau thế nào khi thành phần lỗi | [§1.4](ch1-gioi-thieu.md) |
| **RQ2** | **câu hỏi thiết kế** | thiết kế thế nào để quyết định truy vết được và trung thực về độ tin cậy | [§1.4](ch1-gioi-thieu.md) |
| **RQ3** | **câu hỏi điều kiện kiểm soát** | đạt các thuộc tính đó mà không đánh đổi độ chính xác? | [§1.4](ch1-gioi-thieu.md) |

### Mục tiêu

| Mã | Tên gọi | Phục vụ |
|---|---|---|
| **MT1** | phát triển phương pháp đánh giá khả năng chịu lỗi | câu hỏi chịu lỗi |
| **MT2** | thiết kế kiến trúc tham chiếu và bốn nguyên lý | câu hỏi thiết kế |
| **MT3** | hiện thực prototype và điều kiện so sánh không thiên lệch | câu hỏi điều kiện kiểm soát |

### Giả thuyết khai báo trước

| Mã | Tên gọi trong văn bản | Phán quyết |
|---|---|---|
| **H1** | giả thuyết **tương đương độ chính xác** | ✅ **tương đương ở cả hai mốc** — 0/300 đơn khác nhau; là **kiểm tra đặc tả**, không phải kết quả thực nghiệm |
| **H2** | giả thuyết **hỏng âm thầm thấp hơn** *(bản sửa 14/08 — thu về bề mặt dùng chung)* | ✅ **được ủng hộ trên bề mặt dùng chung** · ⚠️ phát biểu đã bị thu hẹp sau thực nghiệm — hồ sơ sửa đổi ở `research-questions-objectives.md` §3 |
| **H3** | giả thuyết **phát hiện drift sớm** | ❌ **bác bỏ** — không phát hiện ở cả ba mức |

### Ràng buộc dữ liệu

| Mã | Tên gọi trong văn bản |
|---|---|
| **C1** | không có biến treatment |
| **C2** | nhãn nguyên nhân không có sẵn |
| **C3** | kết cục giao hàng không dùng để dự báo được |
| **C4** | văn bản xuất hiện cùng lúc với nhãn |
| **C5** | không quan sát được chất lượng trước khi đánh giá được viết |

### Nguyên lý thiết kế

| Mã | Tên gọi trong văn bản | Mục |
|---|---|---|
| **DP1** | **suy giảm minh bạch** | [§4.5.1](ch4-thiet-ke-hien-thuc.md) |
| **DP2** | **đa nhãn, và cạnh tranh chỉ khi thẩm quyền chồng lấn** | [§4.5.2](ch4-thiet-ke-hien-thuc.md) |
| **DP3** | **từ chối thay vì đoán** | [§4.5.3](ch4-thiet-ke-hien-thuc.md) |
| **DP4** | **nguồn gốc từ giao tiếp** | [§4.5.4](ch4-thiet-ke-hien-thuc.md) |

### Artifact

| Mã | Tên gọi | Loại |
|---|---|---|
| **A1** | ontology và giao thức giao tiếp | construct |
| **A2** | kiến trúc tham chiếu và bốn nguyên lý | model |
| **A3** | bộ nhãn chuẩn do người gán | instantiation |
| **A4** | **chaos harness** | method |
| **A5** | prototype trên dữ liệu Olist | instantiation |
| **A6** | khung đánh giá và bốn kiến trúc đối chứng | method + instantiation |

### Mốc quyết định

| Mã | Nghĩa |
|---|---|
| **T₁** | lúc đặt hàng |
| **T₃** | **ngày mua + 7** — mốc dự báo rủi ro |
| **T₄** | khi đánh giá 1–2★ đã về — mốc quy kết nguyên nhân |

### Lỗi phương pháp được nhắc tới trong luận văn

| Mã | Nội dung tóm tắt |
|---|---|
| **L30** | mốc T₃ bị hiểu là *sự kiện* thay vì *mốc thời gian* |
| **L33** | mốc T₃ đặt **sau** mốc T₄ với 97,6% số đơn |
| **L34** | thao tác thay thế chuỗi làm hỏng một tài liệu nghiên cứu |
| **L35** | con số biện minh cho mốc T₃ không khớp phép đo |
| **L36** | phép thử Byzantine trên bề mặt riêng có **không tiêm được gì** |
| **L37** | đối chứng bị tính là hỏng âm thầm trong khi nó **có** báo lỗi |

Danh mục đầy đủ 37 mục: [methodology-log.md](../methodology-log.md).

---

## 5. Quy ước văn phong và trình bày

### 5.1 Văn phong: báo cáo khoa học, không phải tài liệu kỹ thuật

Đây là ràng buộc chi phối toàn bộ cách viết. Bản thảo đầu tiên được viết theo lối tài liệu kỹ thuật —
bảng dày đặc, gạch đầu dòng thay cho câu, khối cảnh báo — và đã được viết lại. Bảng dưới đối chiếu hai
lối viết để giữ nhất quán cho phần còn lại.

| Khía cạnh | Tài liệu kỹ thuật *(tránh)* | Báo cáo khoa học *(áp dụng)* |
|---|---|---|
| Đơn vị lập luận | gạch đầu dòng, mệnh đề rời | **đoạn văn liền mạch**, mỗi đoạn một luận điểm |
| Vai trò của bảng | chứa lập luận | chỉ chứa **dữ liệu**; lập luận nằm trong văn xuôi |
| Cách dẫn bảng | bảng đứng một mình | **đánh số và có chú thích**, được dẫn từ trong câu văn |
| Nhấn mạnh | biểu tượng cảnh báo, chữ đậm dày | **cấu trúc câu** và vị trí trong đoạn |
| Chuyển ý | tiêu đề mục | **câu chuyển tiếp** giữa các mục |
| Ngôi | mệnh lệnh, ngôi thứ nhất | **phi ngôi**: *nghiên cứu này*, *luận văn* |

Quy tắc thực hành: **một mục không được mở đầu bằng bảng hoặc danh sách**. Mỗi bảng phải có ít nhất
một đoạn văn phía trước giải thích nó trả lời câu hỏi gì, và ít nhất một câu phía sau rút ra điều gì
từ nó.

### 5.2 Đánh số bảng và hình

Bảng đánh số theo chương: **Bảng 3.2** là bảng thứ hai của Chương 3. Chú thích đặt **phía trên** bảng.
Hình đánh số tương tự, chú thích đặt **phía dưới**. Mọi bảng và hình phải được dẫn ít nhất một lần
trong văn bản: *"Bảng 3.2 trình bày…"*, không để bảng đứng trơ.

### 5.3 Quy ước chữ và số

Số thập phân dùng **dấu phẩy** theo chuẩn tiếng Việt — `0,2455` chứ không `0.2455`; trong khối mã
nguồn giữ nguyên dấu chấm. Tên định danh kỹ thuật như `degradation_level`, `PR-AUC` hay `REFUSE` giữ
nguyên dạng gốc và không dịch. Thuật ngữ tiếng Anh khi xuất hiện lần đầu được đặt trong ngoặc sau
thuật ngữ tiếng Việt tương ứng.

Trong bảng trạng thái, các dấu ✅ ⬜ ⚠️ ❌ lần lượt chỉ *đã đo và trích được*, *chờ dữ liệu đầu vào*,
*có cảnh báo phải đọc kèm*, và *bị bác bỏ*. Các dấu này **chỉ dùng trong bảng**, không dùng trong văn
xuôi.

---

## 6. Tài liệu nền — nguồn chuẩn cho từng nội dung

| Nội dung | Tài liệu |
|---|---|
| Mục tiêu, câu hỏi, giả thuyết, phạm vi | [research-questions-objectives.md](../research-questions-objectives.md) |
| Kiến trúc, quyết định công nghệ, cấu trúc mã | [technical-plan-v3.md](../technical-plan-v3.md) |
| Nhật ký lỗi phương pháp *(nguyên liệu Chương 5 và 6)* | [methodology-log.md](../methodology-log.md) |
| Danh mục artifact A1–A7 | [research-design-v2.md](../research-design-v2.md) |
| Kế hoạch đã duyệt + biên bản thi công | [plan-2026-08-12.md](../plan-2026-08-12.md) |
| Trạng thái theo mục tiêu | [status-checklist.md](../status-checklist.md) |

---

## 7. Ba điều tuyệt đối không được làm khi viết

1. **Không trích số từ bộ nhãn `model_assisted_provisional`.** Cờ `citable = False` được cưỡng chế
   bằng kiểu dữ liệu (`data/labels.py::Provenance`) chính vì lý do này.
2. **Không sửa phát biểu giả thuyết cho khớp kết quả.** Phát biểu giữ nguyên văn; chỉ ghi thêm phán
   quyết. Bản đầy đủ năm giả thuyết các bản trước lưu ở §3.1 tài liệu nguồn.
3. **Không trình bày kiểm tra đặc tả như phát hiện thực nghiệm.** Bảng phân biệt hai loại nằm ở §2.1
   tài liệu nguồn và phải được giữ nguyên khi viết Chương 5.
