# Thiết kế nghiên cứu v2 — Câu hỏi nghiên cứu và Artifact khả thi

Viết lại từ đề cương gốc (`context/250104007_...pdf`) sau bản phản biện
[adversarial-review.md](adversarial-review.md).

> **Con trỏ nguồn chuẩn:** phần **RQ, mục tiêu, giả thuyết, phạm vi** của file này đã được tổng hợp và
> **thu gọn từ 5 câu hỏi xuống 3** tại [research-questions-objectives.md](research-questions-objectives.md)
> — dùng file đó khi viết mục 1.2 / 1.3 / 1.4.2 của luận văn.
>
> **⚠️ Số hiệu RQ trong file này là hệ 5 câu hỏi, không phải hệ đang dùng.**
>
> Toàn bộ phần thân *(§RQ1–RQ5, bảng ánh xạ validity, ma trận truy vết)* giữ nguyên hệ 5 câu của bản
> v2 làm **hồ sơ quá trình**. Khi trích vào luận văn phải quy đổi hai bước:
>
> | Hệ 5 câu — **file này** | Hệ 3 câu *(trước 12/08)* | **Hệ hiện hành** *(từ 12/08)* |
> |---|---|---|
> | RQ1 — thiết kế / truy vết được | RQ1 | **RQ2** — thiết kế |
> | RQ2 — phối hợp, quy kết cạnh tranh | RQ2 | **RQ3** — điều kiện kiểm soát |
> | RQ4 — chịu lỗi | RQ3 | **RQ1** — trục chính của luận văn |
> | RQ3 — giá trị *(đánh giá chuyên gia)* | tách ba: giải thích được · độ trễ · **đánh giá chuyên gia thành nhánh tùy chọn** | — |
> | RQ5 — bối cảnh | hấp thụ: không bình luận → tình huống (b) · T₂/T₃ → phân tích độ nhạy | — |
>
> **Phần còn hiệu lực của file này là danh mục artifact A1–A7** — đó là lý do nó vẫn nằm trong bản đồ
> tài liệu. Mọi phát biểu về RQ, mục tiêu, giả thuyết và phạm vi lấy từ
> [research-questions-objectives.md](research-questions-objectives.md).
>
> File này giữ quyền nguồn chuẩn cho **danh mục artifact A1–A7 (Phần 5)**, **lý do viết lại từng RQ
> (Phần 1)**, và làm **hồ sơ bản 5 câu hỏi**.

Nguyên tắc: **mỗi câu hỏi phải trả lời được bằng dữ liệu bạn thực sự có, và phải có khả năng cho ra
câu trả lời "không".** Một câu hỏi mà kết quả đã biết trước, hoặc không thể sai, không phải câu hỏi
nghiên cứu.

---

## Phần 1 — Vì sao bộ câu hỏi cũ phải sửa

| RQ gốc | Vấn đề | Mức |
|---|---|---|
| **RQ1** — "Kiến trúc MAS cần thiết kế thế nào để phù hợp với HTTT doanh nghiệp… dữ liệu lớn, đa nguồn, biến động nhanh?" | Quá rộng và không kiểm chứng được. "Phù hợp" nghĩa là gì? Đo bằng gì? Ngoài ra **"biến động nhanh / thời gian thực" bạn không hề kiểm chứng** — toàn bộ hệ chạy batch offline trên parquet | Phải viết lại |
| **RQ2** — "Các tác tử phân công và phối hợp ra sao… tương ứng với từng nhóm nguyên nhân rủi ro?" | Hướng đúng, nhưng phụ thuộc hoàn toàn vào **nhãn nguyên nhân do chính bạn sinh ra** → vòng tròn. Và câu hỏi ở dạng mô tả ("ra sao"), không dạng so sánh → **không thể sai** | Phải làm sắc lại |
| **RQ3** — "MAS + DSS rule-based có cải thiện **độ chính xác dự báo**… so với MIS và ML đơn lẻ không?" | **Tự đặt bẫy.** MAS và single-ML dùng **chung một LightGBM** → accuracy/F1 sẽ bằng nhau. Bạn đang hỏi một câu mà câu trả lời gần như chắc chắn là **"không"**, ở đúng chỗ bạn muốn nói "có". Thêm nữa "hiệu quả hỗ trợ quyết định" chưa được thao tác hóa, và **không đo được** vì Olist không có biến hành động | **Nguy hiểm nhất — phải viết lại** |
| **RQ4** — "Trong bối cảnh nào MAS-DSS phát huy tốt nhất, và mở rộng sang CRM/chuỗi cung ứng thế nào?" | **Không kiểm chứng được với một dataset.** Bạn không có dữ liệu CRM, không có dữ liệu chuỗi cung ứng, không có dataset TMĐT thứ hai. Đây là suy đoán, không phải nghiên cứu | Phải thay bằng câu hỏi có dữ liệu |
| *(thiếu)* | **Không câu hỏi nào phụ trách chịu lỗi / suy giảm** — trong khi đó chính là đóng góp thật của luận văn | Phải bổ sung |

Tóm lại: bộ câu hỏi cũ **hỏi sai chỗ mạnh và hỏi vào chỗ không có dữ liệu**.

---

## Phần 2 — Bộ câu hỏi nghiên cứu mới

Năm câu, ánh xạ sạch vào khung Validity in Design Science (Larsen et al., 2025) mà bạn đã trích ở
Chương 2 — nên phần lý thuyết không phải viết lại.

### RQ1 — Câu hỏi thiết kế *(prescriptive)*

> **Một kiến trúc hệ thống thông tin đa tác tử cần được thiết kế như thế nào để chuỗi ra quyết định
> phát hiện → quy kết nguyên nhân → đề xuất hành động vẫn tạo ra quyết định *truy vết được* và *trung
> thực về mức độ tin cậy*, kể cả khi một hoặc nhiều tác tử lỗi hoặc suy giảm chất lượng?**

**Vì sao câu này tốt hơn:** nó không hỏi "phù hợp thế nào" (mơ hồ) mà hỏi một thuộc tính **cụ thể,
quan sát được**: *quyết định có truy vết được không*, *hệ thống có trung thực khi nó đang hỏng không*.

**Trả lời bằng:** kiến trúc + **4 Design Principles** (Artifact A2) + prototype chứng minh
(Artifact A5).
**Loại validity:** đây là phần *thiết kế*, được biện minh bằng demonstration, không phải bằng test
thống kê.

---

### RQ2 — Câu hỏi phối hợp *(criterion validity)*

> **Cơ chế quy kết nguyên nhân bằng nhiều tác tử chuyên biệt cạnh tranh (đấu thầu kèm bằng chứng, có
> quyền từ chối) có cho kết quả tốt hơn một bộ phân loại đa lớp đơn khối hay không — xét trên tập nhãn
> chuẩn do người gán, và đặc biệt trong hai tình huống khó: (a) đơn có nhiều nguyên nhân đồng thời,
> (b) đơn không có bằng chứng văn bản?**

**Vì sao câu này tốt hơn:**
- Đo trên **gold set do người gán**, không phải nhãn tự sinh → thoát vòng tròn.
- Ở dạng **so sánh** → có thể cho kết quả "không tốt hơn", tức là **có thể sai**.
- Nêu đích danh hai tình huống mà cơ chế cạnh tranh *lẽ ra* phải thắng: đa nguyên nhân (argmax làm mất
  thông tin) và thiếu bằng chứng (nơi quyền `REFUSE` có giá trị). Nếu thắng ở đó → lập luận rất mạnh.
  Nếu không thắng → cũng là một phát hiện trung thực đáng viết.

---

### RQ3 — Câu hỏi giá trị *(criterion validity)*

> **So với ba phương án thay thế — báo cáo kiểu MIS, mô hình học máy đơn lẻ, và một hệ đơn khối có đầy
> đủ chức năng — kiến trúc MAS-DSS khác biệt thế nào về (a) chất lượng khuyến nghị theo đánh giá của
> chuyên gia, (b) tính giải thích được của quyết định, (c) độ trễ xử lý end-to-end?**

**Ba thay đổi then chốt so với RQ3 cũ:**

1. **Bỏ hẳn "độ chính xác dự báo" khỏi câu hỏi.** Thay vào đó, tuyên bố trước trong Chương 4:
   *"MAS-DSS và mô hình đơn lẻ dùng chung một mô hình dự báo; do đó nghiên cứu **không kỳ vọng và không
   tuyên bố** khác biệt về accuracy/F1. Sự tương đương này được kiểm chứng và báo cáo như một **điều
   kiện kiểm soát** (control condition), nhằm bảo đảm mọi khác biệt quan sát được ở các chỉ số khác
   không đến từ năng lực dự báo."*
   → Đây là chuyển một **điểm yếu** thành một **thiết kế thí nghiệm chặt chẽ**. Hội đồng sẽ đánh giá cao.

2. **Thêm baseline thứ tư: Monolithic-Complete** — hệ đơn khối làm *đủ mọi việc* (dự báo + quy kết +
   cùng tập luật sinh hành động), chỉ thiếu message passing, đấu thầu, giám sát, suy giảm. Không có nó,
   RQ3 chỉ là so với bù nhìn.

3. **"Hiệu quả hỗ trợ quyết định" được thao tác hóa bằng đánh giá chuyên gia**, không phải bằng một
   metric tự bịa. Đây là bằng chứng **không tự tham chiếu** duy nhất bạn có thể có.

---

### RQ4 — Câu hỏi chịu lỗi *(causal validity)* — **câu hỏi mang đóng góp mới**

> **Khi một hoặc nhiều tác tử lỗi (crash) hoặc suy giảm chất lượng mà không lỗi (drift phân phối, mô
> hình mất hiệu chuẩn), kiến trúc MAS-DSS và kiến trúc đơn khối khác nhau thế nào về: (a) tỷ lệ hệ
> thống cho ra quyết định sai mà không cảnh báo (*silent failure*), (b) độ nhạy và độ trễ phát hiện của
> bộ giám sát, (c) mức suy giảm chất lượng quyết định, và (d) chi phí phải trả cho khả năng đó?**

**Vì sao đây là câu hỏi quan trọng nhất:**
- Nó phụ trách **đóng góp thật** của luận văn — thứ hiện đang không có RQ nào bảo vệ.
- Nó **không thể sai một cách tầm thường**: `silent_failure = 0%` là tautology (bạn thiết kế ra nó),
  nhưng **độ nhạy/độ trễ phát hiện drift** và **chi phí overhead** thì hoàn toàn là kết quả thực nghiệm
  — bạn không biết trước.
- Vế (d) buộc bạn phải trung thực: khả năng chịu lỗi **không miễn phí**. Báo cáo cái giá của nó (latency,
  độ phức tạp) làm luận văn đáng tin hơn nhiều so với chỉ khoe ưu điểm.

---

### RQ5 — Câu hỏi bối cảnh *(context validity)* — **thay cho RQ4 cũ về CRM/chuỗi cung ứng**

> **Kiến trúc đề xuất còn giữ được hiệu lực trong những điều kiện thông tin nào — cụ thể: (a) khi thời
> điểm ra quyết định lùi về sớm hơn (lúc bàn giao vận chuyển, thay vì sau khi giao hàng), (b) khi đơn
> hàng không có bằng chứng văn bản (không có bình luận review)?**

**Vì sao phải thay:** câu hỏi cũ ("mở rộng sang CRM/chuỗi cung ứng thế nào?") **không có dữ liệu để trả
lời**. Bạn không có dataset CRM, không có dataset chuỗi cung ứng, không có dataset TMĐT thứ hai. Trả lời
nó = suy đoán.

**Câu hỏi mới thì trả lời được ngay bằng chính Olist**, qua hai thí nghiệm cắt lớp:
- **Cắt theo thời điểm quyết định** (T₂ = lúc bàn giao vận chuyển vs T₃ = sau khi giao hàng): kiến trúc
  hoạt động thế nào khi có ít thông tin hơn? Đây là *context validity* đúng nghĩa.
- **Cắt theo có/không bình luận**: đây chính là điều kiện biên mà quyền `REFUSE` được sinh ra để xử lý.

**Còn CRM/chuỗi cung ứng thì sao?** Chuyển sang **lập luận phân tích** ở Chương 5, dựa trên **4 Design
Principles** (Artifact A2): các DP được phát biểu ở mức trừu tượng, độc lập với miền, nên chúng *có thể
chuyển giao* — và bạn **nói rõ rằng đây là suy luận thiết kế, chưa được kiểm chứng thực nghiệm, và là
hướng nghiên cứu tiếp theo**. Trung thực và vẫn giữ được phần thảo luận có giá trị.

---

### Bảng ánh xạ với khung Validity (Larsen et al., 2025)

| RQ | Loại claim | Loại validity | Bằng chứng |
|---|---|---|---|
| RQ1 | Design | — (demonstration) | Prototype chạy được + 4 DP |
| RQ2 | Criterion | Criterion efficacy | Gold set do người gán, so với classifier đơn khối |
| RQ3 | Criterion | Criterion efficacy | Đánh giá chuyên gia + 4 baseline |
| RQ4 | **Causal** | **Causal validity** | Ablation + fault injection (chaos harness) |
| RQ5 | Context | Context / ecological | Cắt lớp theo decision point và theo bằng chứng |

Ánh xạ này **giữ nguyên cấu trúc Chương 3 và Chương 4** bạn đã viết. Chỉ nội dung câu hỏi thay đổi.

---

## Phần 3 — Giả thuyết (khai báo trước, kể cả giả thuyết vô hiệu)

Khai báo *trước* rằng bạn **kỳ vọng H1 là vô hiệu** — đó là dấu hiệu của một nhà nghiên cứu chững chạc,
không phải một điểm yếu. Nó cũng chặn trước đòn phản biện "anh đang cố chứng minh cái mình muốn tin".

| # | Giả thuyết | Kỳ vọng | Đo bằng |
|---|---|---|---|
| **H1** | MAS-DSS **không** khác biệt có ý nghĩa so với single-ML về accuracy / PR-AUC | **Vô hiệu — và đó là điều mong muốn** (điều kiện kiểm soát) | Kiểm định tương đương (equivalence test), không phải t-test |
| **H2** | Quy kết nguyên nhân bằng đấu thầu cạnh tranh **tốt hơn** classifier đơn khối trên gold set, đặc biệt ở nhóm đa nguyên nhân | Có (nhưng có thể sai) | Macro-F1 đa nhãn trên gold set |
| **H3** | Khuyến nghị của MAS-DSS được chuyên gia đánh giá **phù hợp hơn** so với MIS và Monolithic-Complete | Có | Điểm Likert, kiểm định phi tham số, Krippendorff's α |
| **H4** | Khi tiêm lỗi tác tử, hệ đơn khối có **tỷ lệ hỏng âm thầm cao hơn đáng kể** so với MAS-DSS | Có — và đây là kết quả *thật* (bạn không dàn dựng baseline để hỏng) | Chaos harness |
| **H5** | MAS-DSS chịu **overhead độ trễ cao hơn** hệ đơn khối | **Có — và bạn phải báo cáo** | Latency p50/p95 |
| **H6** | Bộ giám sát phát hiện được drift phân phối trước khi chất lượng quyết định suy giảm quá ngưỡng | Chưa biết — kết quả thực nghiệm thật | Đường cong độ nhạy/độ trễ phát hiện |

H1 và H5 là hai giả thuyết bạn **kỳ vọng "thua"**. Việc khai báo chúng trước làm cho H2, H3, H4 đáng tin
hơn nhiều.

---

## Phần 4 — Mục tiêu nghiên cứu viết lại

Ba mục tiêu gốc giữ nguyên *cấu trúc*, sửa *nội dung*:

| # | Mục tiêu gốc | Mục tiêu v2 |
|---|---|---|
| **MT1** | Đề xuất kiến trúc MAS cho TMĐT theo chu trình thu thập–phân tích–dự báo–đề xuất | Đề xuất kiến trúc MAS-DSS **và rút ra tập Design Principles** cho việc ra quyết định **truy vết được và trung thực về độ tin cậy** trong điều kiện tác tử có thể lỗi |
| **MT2** | Xây prototype trên Olist gồm module phân loại nguyên nhân + DSS rule-based | Hiện thực hóa kiến trúc thành prototype trên Olist, **kèm bộ nhãn chuẩn do người gán** để việc quy kết nguyên nhân đánh giá được **không vòng tròn** |
| **MT3** | Đánh giá định lượng so với MIS và ML đơn lẻ | Đánh giá artifact theo **bốn phương án thay thế** (thêm Monolithic-Complete), **ba nguồn bằng chứng** (chỉ số máy, đánh giá chuyên gia, tiêm lỗi), và **công bố phương pháp chaos harness** như một đóng góp phương pháp luận |

---

## Phần 5 — Danh mục Artifact khả thi

Theo phân loại Hevner (constructs / models / methods / instantiations). **Bảy artifact, tất cả đều làm
được với dữ liệu và thời gian bạn có.**

### A1 — Ontology và giao thức giao tiếp *(construct)*

Tập khái niệm chung mà mọi tác tử dùng để nói chuyện:
- `OrderCase` (đơn vị nghiệp vụ), `Message` (envelope), **10** `Performative`
- `Bid` (kèm `Evidence`), `Declaration` (bản khai năng lực), `Critique`, `Decision`
- **`DegradationLevel`** — đây là construct *mới*: nó buộc mọi quyết định phải mang theo mức độ đáng tin
  của hệ thống tại thời điểm sinh ra nó

**Tính khả thi:** Cao. **Frozen dataclass + bất biến trong `__post_init__`**, ~200 dòng. *(Bản phác thảo
ghi "Pydantic schema"; cài đặt thực tế dùng dataclass để giữ số phụ thuộc ngoài ở mức tối thiểu —
xem `research-questions-objectives.md` MT2.1.)*
**Giá trị:** Construct `DegradationLevel` là một đóng góp khái niệm nhỏ nhưng thật — văn liệu DSS hầu
như không có nó.

---

### A2 — Kiến trúc tham chiếu MAS-DSS + 4 Design Principles *(model)* ← **đóng góp lý thuyết chính**

Kiến trúc 5 lớp, và quan trọng hơn: **bốn nguyên lý thiết kế trừu tượng, chuyển giao được**.

| DP | Phát biểu (theo cấu trúc Gregor, Chandra Kuk & Hevner 2020) |
|---|---|
| **DP1 — Suy giảm minh bạch** | *Để* DSS giữ được lòng tin của nhà quản lý khi thành phần lỗi, *hãy* gắn mức suy giảm vào từng quyết định và bắt buộc con người xem lại khi mức > 0, *bởi vì* một quyết định tự động sinh trên nền năng lực đã suy giảm gây hại hơn là không có quyết định |
| **DP2 — Quy kết bằng cạnh tranh** | *Để* nhận diện tình huống đa nguyên nhân, *hãy* để nhiều tác tử chuyên biệt đấu thầu kèm bằng chứng thay vì dùng một bộ phân loại đa lớp, *bởi vì* độ đồng thuận giữa các bid mang thông tin mà argmax làm mất |
| **DP3 — Từ chối thay vì đoán** | *Để* tránh quyết định tự tin nhưng sai trên dữ liệu ngoài phân phối hoặc thiếu bằng chứng, *hãy* cấp cho tác tử quyền `REFUSE`, *bởi vì* chi phí chuyển giao cho con người thấp hơn nhiều chi phí của một hành động sai |
| **DP4 — Nguồn gốc từ giao tiếp** | *Để* decision trace luôn trung thực với hành vi thực tế, *hãy* dựng nó **từ nhật ký message thật** thay vì viết tay, *bởi vì* trace viết tay có thể phân kỳ với thứ hệ thống thực sự làm |

**Tính khả thi:** Cao — là công việc viết lách + thiết kế, không phải code.
**Giá trị:** Đây là thứ trả lời câu hỏi *"tri thức trừu tượng nào rút ra được?"* và là **cầu nối duy
nhất hợp lệ sang CRM/chuỗi cung ứng** (RQ5). Không có nó, luận văn chỉ là "tôi xây một cái".

---

### A3 — Bộ nhãn chuẩn do người gán *(instantiation / resource)* ← **artifact hữu hình nhất**

- **300–400 đơn bất mãn**, mẫu phân tầng (theo có/không bình luận, theo nhóm hàng, theo mức trễ)
- **Hai annotator độc lập**, codebook rõ ràng, **cho phép đa nhãn**
- Báo cáo **Cohen's κ**; nếu κ < 0.6 → chính định nghĩa nguyên nhân của bạn có vấn đề, **và đó cũng là
  một phát hiện đáng viết**
- Chia đôi: nửa để **đo độ nhiễu của weak label** (báo cáo như một threat được định lượng), nửa làm
  **test set thật**

**Tính khả thi:** Trung bình. Rào cản là tiếng Bồ. Ba cách vượt: (a) dịch máy + người thứ hai kiểm chứng
mẫu dịch, ghi rõ trong Threats to Validity; (b) thuê 1 annotator biết tiếng Bồ trên Prolific/Upwork cho
400 mẫu — chi phí rất thấp; (c) dùng annotator biết tiếng Anh trên bản dịch, và kiểm tra chéo 50 mẫu với
người biết tiếng Bồ.

**Giá trị: rất cao.** Đây là artifact bạn có thể **công bố kèm luận văn** và người khác dùng lại được.
Nó cũng là thứ **duy nhất** phá được vòng tròn đánh giá. **Không có nó, Chương 5 không có giá trị.**

---

### A4 — Phương pháp đánh giá chịu lỗi cho DSS (Chaos Harness) *(method)* ← **đóng góp phương pháp**

Một quy trình có thể tái sử dụng để định lượng khả năng chịu lỗi của một hệ hỗ trợ quyết định:

1. **Phân loại lỗi**: crash fault vs Byzantine/quality fault (drift, mất hiệu chuẩn, bid lệch hệ thống)
2. **Quy trình tiêm lỗi**: tiêm lỗi có kiểm soát theo từng tác tử, từng mức độ
3. **Bộ chỉ số**: silent-failure rate, độ nhạy/độ đặc hiệu của guard, độ trễ phát hiện, phân bố mức suy
   giảm, chi phí overhead
4. **Giao thức so sánh**: chạy cùng kịch bản lỗi trên MAS-DSS và trên hệ đơn khối

**Tính khả thi:** Cao — chỉ là code test + kịch bản.
**Giá trị: cao.** Văn liệu MAS-DSS hầu như **không đánh giá khả năng chịu lỗi** — họ chỉ báo accuracy.
Đây là khoảng trống thật, hẹp, và bạn lấp được. **Đây là chỗ novelty của bạn nằm.**

---

### A5 — Prototype MAS-DSS *(instantiation)*

Hiện thực hóa A1 + A2 trên Olist: **orchestrator tự viết** + message layer + Contract Net hai pha +
blackboard + supervisor + circuit breaker + output guard + degradation ladder + rule engine.

**Tính khả thi:** Trung bình-cao (phần lớn đã có; xem plan kiến trúc).
**Giá trị:** Là bằng chứng cho RQ1 *(câu hỏi thiết kế của hệ 5 câu — nay là **RQ2**)*, và là nền cho
mọi thí nghiệm.

> **Hai thay đổi so với phác thảo, đã chốt ở `technical-plan-v3.md §2.2 và §9`:** (a) **không dùng
> LangGraph** — vòng thực thi là nơi lỗi được tiêm và xử lý nên phải nằm trong phạm vi khảo sát chứ
> không nằm trong một thư viện; (b) **không làm dashboard** — không câu hỏi nghiên cứu nào đo giao diện.

---

### A6 — Bộ khung đánh giá và tập baseline *(method + instantiation)*

Bốn phương án thay thế, chạy trên cùng dữ liệu, cùng split thời gian:

| Baseline | Dự báo | Nguyên nhân | Hành động | Giải thích | Chịu lỗi |
|---|---|---|---|---|---|
| MIS (báo cáo mô tả + ngưỡng) | ✗ | ✗ | ✗ | ✗ | ✗ |
| Single-ML | ✓ | ✗ | ✗ | ✗ | ✗ |
| **Monolithic-Complete** ← mới | ✓ | ✓ | ✓ | một phần | **✗** |
| MAS-DSS | ✓ | ✓ | ✓ | ✓ | **✓** |

**Tính khả thi:** Cao. Monolithic-Complete tái sử dụng chính model và chính tập luật YAML — chỉ bỏ lớp
MAS đi. ~1 ngày làm.
**Giá trị: rất cao.** Không có Monolithic-Complete, RQ3 chỉ là đánh nhau với bù nhìn, và cả Chương 5
mất giá trị.

---

### A7 — Giao thức đánh giá bởi chuyên gia *(method)*

- 100–150 case, mỗi case kèm khuyến nghị từ **ba hệ** (MIS / Monolithic-Complete / MAS-DSS), **trình bày
  ngẫu nhiên và ẩn danh hệ** (blind)
- 3–5 người có kinh nghiệm vận hành TMĐT / CSKH chấm Likert 5 mức: *tính phù hợp*, *tính khả thi*,
  *tính giải thích được*
- Báo cáo **Krippendorff's α**; kiểm định phi tham số (Friedman + post-hoc)

**Tính khả thi:** Trung bình. Rào cản là tìm 3–5 chuyên gia. Có thể dùng người làm TMĐT ở Việt Nam —
tình huống nghiệp vụ (giao trễ, hàng lỗi, phí ship cao) mang tính phổ quát, không phụ thuộc thị trường
Brazil. Ghi rõ điều này trong Threats to Validity.

**Giá trị: rất cao.** Đây là **bằng chứng không tự tham chiếu duy nhất** về chất lượng khuyến nghị. Không
có nó, RQ3 không trả lời được.

---

## Phần 6 — Những gì phải BỎ KHỎI phạm vi (và nói rõ trong Chương 1)

Tuyên bố phạm vi rõ ràng là **áo giáp** khi bảo vệ, không phải sự thú nhận yếu kém.

| Bỏ | Lý do — viết thẳng vào luận văn |
|---|---|
| **Đo hiệu quả thực tế của hành động can thiệp** | Olist **không ghi nhận hành động nào đã được áp dụng** → không có biến treatment → không suy luận nhân quả được. Nghiên cứu đánh giá **chất lượng khuyến nghị** (qua chuyên gia), không phải **hiệu quả can thiệp** |
| **Episodic memory chứa kết quả của hành động** | Cùng lý do — sẽ là bịa dữ liệu |
| **Policy Critic tính hữu dụng kỳ vọng (EV)** | `ΔP(recover \| action)` không ước lượng được. Critic thu hẹp thành **engine kiểm tra ràng buộc** (ngân sách, cooldown, công bằng, bằng chứng yếu, mâu thuẫn) — tất cả đều tính được từ dữ liệu thật |
| **Tuyên bố "thời gian thực"** | Hệ chạy batch offline. Latency đo được nhưng **không được gọi là real-time** |
| **Khái quát hóa sang CRM / chuỗi cung ứng bằng thực nghiệm** | Không có dữ liệu. Chuyển sang **lập luận phân tích qua Design Principles**, và nói rõ là chưa kiểm chứng |
| **LLM agent** (mặc định) | Sẽ **làm nhiễu loạn causal claim** ở RQ4: nếu MAS thắng, không tách được phần nào do kiến trúc, phần nào do LLM. *Nếu còn thời gian*, thêm như **một nhánh thí nghiệm riêng** (xem dưới) |
| **Can thiệp "phòng ngừa sớm"** | Feature mạnh nhất chỉ có sau khi giao hàng. Đổi framing sang **phục hồi dịch vụ trong cửa sổ trước review** |

### Nhánh tùy chọn (chỉ làm nếu dư thời gian)

**RQ-phụ:** *Phản biện dựa trên LLM có cải thiện chất lượng chuỗi quyết định so với phản biện dựa trên
ràng buộc hay không?*
- Điều kiện A: MAS-DSS + Critic ràng buộc (deterministic) ← artifact chính
- Điều kiện B: MAS-DSS + Critic LLM local (temperature = 0, seed cố định)
- Đo bằng: điểm chuyên gia, tỷ lệ can thiệp thừa, độ trễ

Làm thế này thì LLM chuyển từ **nghĩa vụ phải bào chữa** thành **một câu hỏi nghiên cứu có câu trả lời**
— và câu trả lời "không cải thiện" cũng là kết quả có giá trị. Nó cũng khép lại độ lệch với phần
literature review về agentic AI ở Chương 2.

---

## Phần 7 — Ánh xạ RQ → Artifact → Thí nghiệm → Chương

| RQ | Artifact | Thí nghiệm | Chương |
|---|---|---|---|
| RQ1 (design) | A1, A2, A5 | Demonstration: chạy end-to-end trên Olist | 3, 4 |
| RQ2 (phối hợp) | A3, A5, A6 | CNP vs classifier đơn khối, đo trên **gold set**; cắt lớp đa nguyên nhân / không bình luận | 5 |
| RQ3 (giá trị) | A5, A6, A7 | 4 baseline; **đánh giá chuyên gia mù**; latency; kiểm định tương đương cho H1 | 5 |
| RQ4 (chịu lỗi) | A4, A5, A6 | **Chaos harness**: crash fault + drift; MAS vs Monolithic-Complete | 5 |
| RQ5 (bối cảnh) | A5 | Cắt theo decision point (T₂/T₃) và theo có/không bình luận | 5 |
| — | A2 (DP) | Lập luận phân tích về khả năng chuyển giao sang CRM/SCM | 5 (thảo luận) |

**Không có ô trống, không có artifact thừa, không có câu hỏi không trả lời được.**

---

## Phần 8 — Việc phải làm ngay, theo thứ tự

| # | Việc | Vì sao trước tiên |
|---|---|---|
| 1 | **Đếm % đơn bất mãn không có bình luận** trong Olist | Nếu > 40%, "Root Cause Agent" trên phần lớn dữ liệu chỉ là ngưỡng `delivery_delay` đội lốt ML. **Con số này quyết định RQ2 có tồn tại được hay không** |
| 2 | **Xóa `review_lag_days`** khỏi feature set | Rò rỉ nhãn trắng trợn |
| 3 | Chốt **decision point = T₃**, đổi framing sang **service recovery**, sửa tập luật (bỏ `expedite`) | Hệ hiện đang khuyến nghị điều bất khả thi về mặt thời gian |
| 4 | **Bắt đầu gold set ngay** (A3) — mất nhiều thời gian nhất, là đường tới hạn | Không có nó, Chương 5 vô giá trị. Bắt đầu song song với code |
| 5 | Cập nhật Chương 1 (mục tiêu, RQ, phạm vi) và Chương 3 (thêm 4 DP) | Để phần viết không phải làm lại lần hai |
| 6 | Dựng **Monolithic-Complete** baseline (A6) | Rẻ (~1 ngày), nhưng quyết định giá trị của toàn bộ Chương 5 |
