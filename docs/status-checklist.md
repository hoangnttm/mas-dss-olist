# Checklist trạng thái — đối chiếu với mục tiêu nghiên cứu

> **Một trang duy nhất trả lời: mục tiêu nào đã đạt, bằng chứng nằm ở đâu, còn thiếu gì.**
>
> Cập nhật **15/08/2026** · **303 test xanh** · **6/6 cổng đạt** · **47 lỗi phương pháp** đã ghi.
>
> Ký hiệu: ✅ đạt · 🟡 đạt một phần · ⛔ ngoài phạm vi · ⬜ chưa làm

**Ba tài liệu chuyên trách, đọc thay vì tra ở đây:**

| Câu hỏi | Tài liệu |
|---|---|
| Artifact nào phục vụ câu hỏi nào, bằng chứng ở tệp nào | [artifact-register.md](artifact-register.md) |
| Chỉ số này đo gì, tính thế nào, **có trích được không** | [evaluation-handbook.md](evaluation-handbook.md) |
| Phát biểu gốc của mục tiêu, câu hỏi, giả thuyết | [research-questions-objectives.md](research-questions-objectives.md) |

---

## 0. Tóm tắt một bảng

| Mục tiêu | Câu hỏi | Trạng thái | Ghi chú |
|---|---|---|---|
| **MT1** chịu lỗi + chi phí *(trục chính)* | RQ1 | ✅ **đạt trên bề mặt dùng chung** | Bề mặt chỉ-MAS **đặt ngoài phạm vi**, có ghi hồ sơ |
| **MT2** thiết kế + 4 nguyên lý | RQ2 | ✅ **đạt đủ** | Bốn nguyên lý đều có cơ chế cưỡng chế **và** ablation `citable` |
| **MT3** prototype + gold set | RQ3 | ✅ **đạt** | κ = 0,784 · số quy kết lần đầu `citable = True` |

**Sáu cổng:** M0 ✅ · G1 ✅ · G2 ✅ *(κ = 0,784)* · G3 ✅ · G4 ✅ · **G5 ✅** *(sha256 trùng khớp)*.

---

## 1. MT1 → RQ1 — Chịu lỗi và chi phí *(trục chính)*

### 1.1 Bốn hệ thống *(A6)* ✅

| Tiêu chí | Trạng thái |
|---|---|
| Bốn hệ chạy trên cùng dữ liệu, cùng phép chia tập | ✅ |
| Đơn khối dùng **chung đối tượng** mô hình, head, tập luật | ✅ kiểm bằng so sánh định danh (`is`) |
| Không bị làm yếu có chủ ý | ✅ đa nhãn, không `argmax` *(quét AST)*, cùng ngưỡng |

### 1.2 Chaos harness *(A4)* ✅ — **đóng góp phương pháp**

16 kịch bản = 5 nhóm × 3 mức + đường khỏe. 200 case mỗi kịch bản.

| Nhóm | Ném ngoại lệ | MAS âm thầm | Đơn khối | Khác biệt |
|---|---|---|---|---|
| crash 1·2·3 | ✔ | **0,0%** | **0,0%** | ⚪ **không** |
| hang 1·2·3 | ✔ | **0,0%** | **0,0%** | ⚪ **không** *(xem cảnh báo dưới)* |
| **byzantine 1·2·3** | ✘ | **5,0%** | **84,5 → 99,0%** | ✅ **lớn nhất** |
| **bias 1·2·3** | ✘ | **8,5 → 21,0%** | 25,0 → 84,5% | ✅ |
| **drift 1·2·3** | ✘ | 2,5 → 5,0% | 3,5 → 6,5% | ⚠️ **cả hai gần mù** |

Đường khỏe: **0,0%** suy giảm · **0** guard chặn · báo động giả **0** — điều kiện để mọi số trên có nghĩa.

**Ưu thế nằm trọn ở nhóm lỗi KHÔNG ném ngoại lệ.** Lỗi biết `raise` thì `try/except` là đủ; lỗi trả về
giá trị hợp lệ nhưng sai mới cần thang suy giảm.

> ⚠️ **Ba con số ở byzantine và bias đã đổi sau khi sửa L43.** Trước đó cả hai cho MAS = **0,0%**, và
> con số ấy phản ánh **chỗ đặt bộ tiêm** chứ không phản ánh kiến trúc: bộ tiêm đầu độc `risk_score`
> trong khi quyết định của MAS đọc `risk`. Phát biểu đúng là *"giảm đáng kể"*, **không phải** *"miễn
> nhiễm"*.
>
> ⚠️ **Nhóm `hang`:** đơn khối cho 0,0% đầu ra đổi vì nó **không có hạn chót** — chỉ chạy chậm hơn rồi
> cho cùng kết quả. Phép đo **không nắm bắt được thiệt hại thật** của nó ở nhóm này.

### 1.3 Chi phí ✅ *(báo cáo mô tả — mệnh đề về chi phí đã gỡ khỏi bộ giả thuyết)*

| | MAS-DSS | Đơn khối |
|---|---|---|
| **Bề mặt hỏng** *(thước đo chính)* | **10** thành phần | **5** |
| **ms mỗi case** *(wall-clock, cả hai vế)* | **114,6** *(khoảng 115–130)* | **9,2** *(khoảng 6,8–9,2)* |
| — trong đó ghi nhật ký message | ~65,7 | 0 |
| phút mỗi lô 75.480 đơn | 144 | 11,6 → **chậm hơn 12,5–17,9 lần** |
| Dòng mã tầng chịu lỗi · phối hợp | **447** · **671** | 0 · 0 |
| Tác tử · loại message · tầng | 10 · 10 · 5 | 0 · 0 · 2 |

🔴 **L46 — số cũ *(10,96 vs 10,82 → +10,5 giây/lô)* đã bị rút.** Hai vế khi đó đo bằng hai cơ sở khác
nhau: MAS lấy `sum(span)` *(bỏ qua glue + ghi nhật ký)*, đơn khối lấy wall-clock của một vòng lặp
**chạy ba baseline** cộng phần serialize. Cả hai sai lệch đều có lợi cho MAS. Nay cả hai đo bằng
wall-clock trong cùng tiến trình; canh bằng `test_hai_ve_do_tre_phai_CUNG_MOT_CO_SO_do`.

**Hơn nửa chi phí MAS là ghi nhật ký, không phải kiến trúc:** 21,16 message/case × `commit` từng
message. Giữ nguyên có chủ đích — thí nghiệm crash ở §5.8 cần nhật ký bền vững theo từng message.

---

## 2. MT2 → RQ2 — Thiết kế và tri thức thiết kế

### 2.1 Ontology và giao thức *(A1)* ✅

10 performative · 4 mức suy giảm · 3 bất biến cưỡng chế trong `__post_init__` *(dataclass, không
Pydantic — tiêu chí phát biểu theo **thuộc tính cần đạt**, không theo công cụ)*.

### 2.2 Kiến trúc tham chiếu *(A2)* ✅

| Cơ chế điều phối | Trạng thái |
|---|---|
| Định tuyến động theo trạng thái case | ✅ `Step.on` |
| Contract Net hai pha có ràng buộc ngân sách | ✅ — **tắt trong cấu hình báo cáo**, xem §2.4 |
| Blackboard dùng chung | ✅ |
| Cây giám sát | ✅ 6 module · 447 dòng |

### 2.3 Bốn nguyên lý ✅ — **4/4 có ablation `citable`**

| DP | Cơ chế cưỡng chế | Chỉ số | Có | Gỡ |
|---|---|---|---|---|
| **DP1** suy giảm minh bạch | `degradation_level` không có mặc định | hỏng âm thầm dưới byzantine | **5,0%** | **34,0%** |
| **DP2** đa nhãn, cạnh tranh khi thẩm quyền chồng lấn | cấm `argmax` *(quét AST)* | số ô bất đồng | 0 | 0 |
| **DP3** từ chối thay vì đoán | `REFUSE` · OOD | quy kết sai khi người bỏ trống | **0,5000** | **1,0000** |
| **DP4** nguồn gốc từ giao tiếp | Explainer chỉ đọc nhật ký | độ phân kỳ | 0,0 | **0,4061** |

**DP3 — cái giá của việc bỏ quyền từ chối.** Ép trả lời: độ phủ 0,7533 → 1,0, nhưng macro-F1
**0,6862 → 0,4827** và precision của `quality` **0,92 → 0,27**. Kết quả ngược chiều ở lát đa nguyên
nhân *(từng thấy ở bản trước)* **đã biến mất** sau khi gỡ ngân sách — nó là hệ quả của tham số, không
phải của nguyên lý.

**DP2 — kết quả âm đã dẫn tới việc sửa chính nguyên lý.** Vế *"đấu thầu tốt hơn bộ phân loại đa nhãn"*
bị bác bỏ; bản sửa nêu điều kiện biên: **các tác tử phải tranh chấp cùng một phần bằng chứng, không
phân chia nó**.

### 2.4 ⚠️ Ràng buộc ngân sách tắt trong cấu hình báo cáo

Đo được trên gold set: bật ngân sách làm macro-F1 **0,6862 → 0,5862**, và thiệt hại **nằm trọn** trong
hai tầng bị cắt *(tầng trung bình và cao mất đúng 0,0000)*. Đổi lại chỉ tiết kiệm **0,77 ms/case**.

Hệ quả phải nói thẳng ở Chương 4 và §5.7: `allocate()` suy biến thành hàm hằng · pha 1 tốn
**6/21,16** message mỗi case mà **không quyết định gì**.

⚠️ `REJECT_PROPOSAL` **không biến mất** — nó không xuất hiện ở đường khỏe, nhưng dưới tiêm lỗi vẫn
được phát **1.200 lần**, tập trung ở `crash_k2/k3` và `hang_k2/k3`. Cơ chế: analyst hỏng ngay trong
pha 1 nên không khai báo, còn vòng trao thầu duyệt theo **danh sách tác tử** chứ không theo danh sách
bản khai. Performative này vì vậy **đổi vai** — từ *thua thầu tài nguyên* sang *không khai báo được*.

---

## 3. MT3 → RQ3 — Prototype và gold set

### 3.1 Prototype *(A5)* ✅

88 tệp · 12.725 dòng · 10 tác tử · 5 tầng. Trace dựng lại **chỉ từ nhật ký message** — cổng G4.

### 3.2 Gold set *(A3)* ✅ — **cổng G2 đạt**

| | |
|---|---|
| Nguồn | 300 dòng, hai người gán độc lập, chỉ kỳ kiểm thử |
| **Tính độc lập** | **77,7%** *(vòng trước 96,4% và đã bị chặn)* |
| **κ trung bình** | **0,784** — delivery 0,774 · quality 0,873 · service 0,801 · unknown 0,688 |
| Đủ dương để tin cậy | **4/4 nhãn** |
| Quy tắc hợp nhất | **HỢP (OR)** — 3,0% xung đột thật |

### 3.3 Kết quả quy kết tại T₄ ✅ `citable = True`

| Nhãn | MAS-DSS | Đơn khối |
|---|---|---|
| `delivery` | 0,7302 | 0,7302 |
| `quality` | 0,6667 | 0,6667 |
| `service` | 0,6618 | 0,6618 |
| **macro-F1** | **0,6862** | **0,6862** |

**0 ô bất đồng trên 900.** Đây là **đẳng thức đại số** *(L27)*, không phải kết quả thống kê: ba tác tử
độc quyền ba nhãn rời nhau, chung head, chung ngưỡng. McNemar trở thành tautology và được ghi nhận
đúng như vậy.

### 3.4 Tầng xử lý văn bản 🟡

| Tiêu chí | Trạng thái |
|---|---|
| Head đa nhãn vận hành ở T₄ | ✅ `TfidfCauseHead` |
| BERTimbau encoder | ⬜ **chưa cài** — hệ quả: `cost_ms` 1,3 thay vì ~45 ⟹ ngân sách yếu hơn thiết kế |
| Weak label **chỉ** dùng ở pre-train | ✅ cưỡng chế bằng kiểu (`WeakLabelInEvaluation`) |
| `BidCalibrator` nối vào đường chạy chính | ⬜ **chưa** — Chương 4 **không được viết** *"bid đã được hiệu chuẩn"* |

---

## 4. Ba giả thuyết

| # | Phán quyết | Loại bằng chứng |
|---|---|---|
| **H1** tương đương độ chính xác | ✅ **tương đương ở cả hai mốc** — 0/900 ô bất đồng | ❌ **kiểm tra đặc tả** — chung một đối tượng mô hình |
| **H2** *(bản sửa 14/08)* hỏng âm thầm thấp hơn trên **bề mặt dùng chung** | ✅ **được ủng hộ** ở nhóm lỗi không ném ngoại lệ | ✅ thực nghiệm cho **đơn khối**; ❌ đặc tả cho MAS |
| **H3** phát hiện drift sớm | ❌ **bác bỏ** — không phát hiện ở cả ba mức | ✅ thực nghiệm |

> ⚠️ **H2 đã bị sửa sau khi thấy kết quả** — vế *"toàn bộ bề mặt hỏng"* bị gỡ. Phát biểu gốc giữ nguyên
> văn kèm hồ sơ sửa đổi tại `research-questions-objectives.md` §3. **Bản sửa dễ thỏa mãn hơn bản gốc**,
> và Chương 5 nói đúng như vậy.
>
> *(Hồ sơ bộ năm giả thuyết của các bản trước — đã lỗi thời, giữ làm hồ sơ, **không trích** — nằm ở
> `research-questions-objectives.md` §3.1.)*

---

## 5. Danh mục artifact

Bảng đầy đủ kèm tiêu chí hoàn thành nguyên văn, đường dẫn bằng chứng và lệnh tái lập:
**[artifact-register.md](artifact-register.md)**.

| ID | Artifact | Phục vụ | Trạng thái |
|---|---|---|---|
| **A4** | Chaos harness — **đóng góp phương pháp** | RQ1 | ✅ trên bề mặt dùng chung |
| **A1** | Ontology + giao thức | RQ2 | ✅ |
| **A2** | Kiến trúc + 4 nguyên lý | RQ2 | ✅ |
| **A3** | Gold set do người gán | RQ3 | ✅ κ = 0,784 |
| **A5** | Prototype | RQ1, RQ2, RQ3 | ✅ |
| **A6** | Khung đánh giá + 4 đối chứng | RQ1, RQ3 | ✅ |
| *(A7)* | Đánh giá chuyên gia | — | ⬜ không thực hiện |

---

## 6. Số nào được trích vào luận văn

> ⛔ **Bảng liệt kê số của mục này đã bị gỡ ngày 14/08.** Nó chứa PR-AUC 0,3993 · ECE 0,0133→0,0072 ·
> ngưỡng 0,167 · đơn khối 16–100% · +6,7% · 1.080 dòng — **toàn bộ đo ở mốc T₃ cũ và trước khi vá rò
> rỉ**, tức đều sai.
>
> **Nguồn chuẩn duy nhất** nay là [evaluation-handbook.md](evaluation-handbook.md), nơi mỗi chỉ số đi
> kèm tệp sinh ra nó, lệnh tái lập, và nhãn *kiểm tra đặc tả / kết quả thực nghiệm*. Không duy trì hai
> danh sách song song — chính cơ chế đó đã sinh ra bẫy trích dẫn phải rào lại.

### Ba ranh giới phải giữ khi trích

| Ranh giới | Nội dung |
|---|---|
| **`citable`** | Số quy kết chỉ trích được khi bảng mang `citable = True`. Phép thử ngược: truyền gold set tạm ⟹ **mọi** bảng phải lật `False` |
| **Đặc tả ↔ thực nghiệm** | Hỏng âm thầm của **MAS** và **H1** là *đặc tả*. Hỏng âm thầm của **đơn khối** và hai nhóm `designed_for = False` là *thực nghiệm* |
| **Cổng G5** | Không số chaos nào vào luận văn trước khi hai lượt chạy trùng `sha256` — **đã đạt** |

---

## 7. Việc còn lại

| # | Việc | Chặn cái gì |
|---|---|---|
| 1 | **Viết Chương 6 và danh mục tài liệu tham khảo** — hai tệp chưa tồn tại/còn trống | nộp luận văn |
| 2 | **Đối chiếu trích dẫn Chương 2 với bản gốc** — khối *"xóa trước khi nộp"* còn nguyên | nộp luận văn |
| 3 | IMP-4 → IMP-7 trong `methodology-log.md` | kỷ luật phương pháp, không chặn kết quả |
| 4 | Dọn ~45 thư mục chạy thử trong `data/v3/runs/` | vệ sinh kho |

**Không còn hạng mục nào chặn số liệu.** Bốn việc trên thuộc phần viết và vệ sinh, không thuộc phần đo.
