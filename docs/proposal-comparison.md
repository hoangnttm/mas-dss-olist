# So sánh đề cương gốc ↔ bản mới nhất

**Đề cương gốc:** `context/250104007_NguyenTanTruongMinhHoang_Report_L1.pdf` (21 trang, mục 1.2 và 1.3).
**Bản mới nhất:** [research-design-v2.md](research-design-v2.md) (RQ, mục tiêu, phạm vi) +
[technical-plan-v3.md](technical-plan-v3.md) (kiến trúc, thí nghiệm — **thay thế** `technical-design-v2.md`
đã lỗi thời).
**Lý do thay đổi:** [adversarial-review.md](adversarial-review.md).

Tài liệu này chỉ làm một việc: **đối chiếu nguyên văn** và chỉ rõ cái gì đổi, đổi thành gì, vì sao, và
phải sửa ở chương nào.

> ⚠️ **Đánh số RQ trong file này theo bản 5 câu hỏi, đã bị thu gọn còn 3.** Xem
> [research-questions-objectives.md §2.4](research-questions-objectives.md). Quy đổi: **RQ4 → RQ3** ·
> RQ1, RQ2 giữ số · **RQ5(b) không có bình luận → RQ2 tình huống (b)** · **RQ5(a) → phân tích độ nhạy**
> · **RQ3 cũ tách ba**: giải thích được → RQ1, độ trễ → RQ3 vế (d), đánh giá chuyên gia → nhánh tùy chọn.
> Phần đối chiếu với **đề cương gốc** dưới đây vẫn nguyên giá trị.

---

## Phần 1 — Mục tiêu nghiên cứu

### 1.1 Bảng đối chiếu

| # | **Đề cương gốc** (mục 1.2, nguyên văn rút gọn) | **Bản v2** | Mức thay đổi |
|---|---|---|---|
| **MT1** | "Đề xuất một kiến trúc hệ thống thông tin doanh nghiệp dựa trên AI đa tác tử cho bối cảnh thương mại điện tử, trong đó các tác tử phối hợp thực hiện chu trình thu thập, phân tích dữ liệu và dự báo mức độ hài lòng của khách hàng (review score), đồng thời **nhận diện các đơn hàng có nguy cơ không hài lòng cần can thiệp quản trị**" | Đề xuất kiến trúc MAS-DSS **và rút ra tập Design Principles** cho việc ra quyết định **truy vết được và trung thực về độ tin cậy** trong điều kiện **tác tử có thể lỗi hoặc suy giảm** | **Mở rộng** — giữ nguyên phần kiến trúc, thêm hai thứ: (1) DP như tri thức trừu tượng; (2) điều kiện lỗi/suy giảm |
| **MT2** | "Xây dựng một hệ thống thông tin hoàn chỉnh dưới dạng prototype hiện thực hóa kiến trúc đề xuất trên bộ Olist, bao gồm **mô-đun phân loại nguyên nhân rủi ro** liên quan đến chất lượng sản phẩm, giao hàng chậm trễ, chăm sóc khách hàng và giá cả, sau đó tích hợp với một **DSS rule-based** để sinh các hành động quản trị" | Hiện thực hóa kiến trúc thành prototype trên Olist, **kèm bộ nhãn chuẩn do người gán (gold set)** để việc quy kết nguyên nhân đánh giá được **không vòng tròn** | **Bổ sung điều kiện tiên quyết** — prototype giữ nguyên, thêm artifact A3. Không có A3, mô-đun phân loại nguyên nhân không đánh giá được |
| **MT3** | "Đánh giá định lượng hiệu quả của kiến trúc MAS kết hợp DSS rule-based so với **MIS truyền thống và một mô hình học máy đơn lẻ**, thông qua các chỉ số về **độ chính xác dự báo mức độ hài lòng**, khả năng phát hiện các trường hợp cần can thiệp, chất lượng chuỗi xử lý phát hiện–phân loại–đề xuất hành động và tiềm năng cải thiện quá trình ra quyết định" | Đánh giá theo **bốn phương án thay thế** (thêm Monolithic-Complete), **ba nguồn bằng chứng** (chỉ số máy, đánh giá chuyên gia, tiêm lỗi), và **công bố chaos harness như một đóng góp phương pháp luận** | **Viết lại** — đây là mục tiêu thay đổi nhiều nhất. Xem §1.2 |

### 1.2 Vì sao MT3 phải viết lại

Ba lỗi trong MT3 gốc, xếp theo mức nguy hiểm:

| Lỗi | Chi tiết | Hệ quả nếu giữ nguyên |
|---|---|---|
| **Baseline bù nhìn** | MAS-DSS và single-ML dùng **chung một LightGBM** → accuracy/F1 bằng nhau *theo cấu tạo*. MAS "thắng" ở `pipeline_completeness` và `action_cause_fit` — nhưng baseline được *định nghĩa* là bằng 0 ở hai chỉ số đó | Larsen et al. (2025) yêu cầu criterion validity so với **giải pháp hiện có tốt nhất**. So với phiên bản đã bị chặt tay là **tautology, không phải kết quả**. Hội đồng sẽ đánh chỗ này |
| **Đo sai chỗ mạnh** | "Độ chính xác dự báo" đặt ở vị trí trung tâm — đúng chỗ MAS *chắc chắn không thắng* | Luận văn tự đặt bẫy: hỏi một câu mà câu trả lời gần như chắc chắn là "không", ở đúng chỗ muốn nói "có" |
| **"Hiệu quả hỗ trợ quyết định" chưa thao tác hóa** | Đo bằng gì? Chỉ số hiện có (`action_cause_fit`) vòng tròn: bảng ánh xạ nguyên nhân→hành động "đúng" do chính tác giả viết, tập luật sinh hành động cũng do chính tác giả viết | `pipeline_completeness = 0.87` chỉ nói *"hai file YAML tôi viết thì nhất quán với nhau"* |

**Cách xử lý trong v2 — chuyển điểm yếu thành thiết kế thí nghiệm chặt:**

Thay vì né tránh sự tương đương về accuracy, **tuyên bố trước** trong Chương 4:

> *"MAS-DSS và mô hình đơn lẻ dùng chung một mô hình dự báo; do đó nghiên cứu **không kỳ vọng và không
> tuyên bố** khác biệt về accuracy/F1. Sự tương đương này được kiểm chứng và báo cáo như một **điều kiện
> kiểm soát** (control condition), nhằm bảo đảm mọi khác biệt quan sát được ở các chỉ số khác không đến
> từ năng lực dự báo."*

Đây là chuyển một **điểm yếu** thành một **thiết kế thí nghiệm chặt chẽ**. Kèm theo: thêm baseline
Monolithic-Complete, và thao tác hóa "hiệu quả hỗ trợ quyết định" bằng **đánh giá chuyên gia mù** —
bằng chứng không tự tham chiếu duy nhất có thể có.

---

## Phần 2 — Câu hỏi nghiên cứu

### 2.1 Bảng đối chiếu tổng quan

| Gốc | Chủ đề | Số phận | Mới | Chủ đề mới |
|---|---|---|---|---|
| **RQ1** | Kiến trúc MAS thiết kế thế nào để "phù hợp" với HTTT doanh nghiệp | **Viết lại** (thu hẹp, làm cho quan sát được) | **RQ1** | Thiết kế thế nào để quyết định **truy vết được** và **trung thực về độ tin cậy** khi tác tử lỗi |
| **RQ2** | Các tác tử phân công và phối hợp **ra sao** | **Làm sắc lại** (mô tả → so sánh) | **RQ2** | Quy kết bằng **đấu thầu cạnh tranh** có **tốt hơn** classifier đơn khối không, **trên gold set** |
| **RQ3** | Có cải thiện **độ chính xác dự báo**, phát hiện, thời gian xử lý, "hiệu quả hỗ trợ quyết định" không | **Viết lại toàn bộ** | **RQ3** | So với **bốn** phương án: khác biệt về **chất lượng khuyến nghị (chuyên gia)**, **giải thích được**, **độ trễ** |
| **RQ4** | Bối cảnh nào phát huy tốt nhất + mở rộng sang **CRM/chuỗi cung ứng** | **Thay bằng câu trả lời được** | **RQ5** | Còn hiệu lực trong điều kiện thông tin nào: **T₂ vs T₃**, **có/không bình luận** |
| *(không có)* | — | **Bổ sung** | **RQ4** | **Chịu lỗi**: silent failure, độ nhạy/độ trễ phát hiện, mức suy giảm, **và cái giá phải trả** |

**Nhận xét cốt lõi:** bộ câu hỏi gốc **hỏi sai chỗ mạnh và hỏi vào chỗ không có dữ liệu.** RQ3 hỏi
accuracy (chỗ chắc chắn không thắng), RQ4 hỏi CRM/chuỗi cung ứng (không có dataset), và **không câu nào
phụ trách khả năng chịu lỗi** — vốn là đóng góp thật.

### 2.2 Đối chiếu chi tiết từng câu

#### RQ1

| | Nội dung |
|---|---|
| **Gốc** | *"Một kiến trúc AI đa tác tử cần được thiết kế **như thế nào để phù hợp** với yêu cầu của hệ thống thông tin doanh nghiệp hỗ trợ ra quyết định trong bối cảnh thương mại điện tử, nơi dữ liệu lớn, đa nguồn và **biến động nhanh** theo hành vi khách hàng?"* |
| **Vấn đề** | (1) "Phù hợp" là gì? Đo bằng chỉ số nào? Không kiểm chứng được. (2) **"Biến động nhanh / thời gian thực" không hề được kiểm chứng** — toàn bộ hệ chạy batch offline trên parquet |
| **v2** | *"Một kiến trúc HTTT đa tác tử cần được thiết kế như thế nào để chuỗi ra quyết định phát hiện → quy kết nguyên nhân → đề xuất hành động vẫn tạo ra quyết định **truy vết được** và **trung thực về mức độ tin cậy**, kể cả khi một hoặc nhiều tác tử lỗi hoặc suy giảm chất lượng?"* |
| **Cải thiện** | Không hỏi "phù hợp thế nào" (mơ hồ) mà hỏi một thuộc tính **cụ thể, quan sát được**. Bỏ tuyên bố "thời gian thực" không kiểm chứng được |
| **Trả lời bằng** | A1 (ontology) + A2 (4 Design Principles) + A5 (prototype). Loại validity: **demonstration**, không phải test thống kê |

#### RQ2

| | Nội dung |
|---|---|
| **Gốc** | *"Các tác tử trong hệ thống cần được phân công chức năng và phối hợp **ra sao** để thực hiện hiệu quả chu trình thu thập dữ liệu, phân tích, dự báo mức độ hài lòng và đề xuất hành động quản trị tương ứng với từng nhóm nguyên nhân rủi ro?"* |
| **Vấn đề** | (1) Ở dạng **mô tả** ("ra sao") → **không thể sai** → không phải câu hỏi nghiên cứu. (2) Phụ thuộc hoàn toàn vào **nhãn nguyên nhân do chính tác giả sinh ra** bằng luật từ khóa → vòng tròn: `label_causes()` → `RootCauseAgent.fit()` → đánh giá so với chính nhãn giả đó |
| **v2** | *"Cơ chế quy kết nguyên nhân bằng nhiều tác tử chuyên biệt cạnh tranh (đấu thầu kèm bằng chứng, có quyền từ chối) **có cho kết quả tốt hơn** một bộ phân loại đa lớp đơn khối hay không — xét trên **tập nhãn chuẩn do người gán**, và đặc biệt trong hai tình huống khó: (a) đơn có **nhiều nguyên nhân đồng thời**, (b) đơn **không có bằng chứng văn bản**?"* |
| **Cải thiện** | (1) Đo trên **gold set** → thoát vòng tròn. (2) Ở dạng **so sánh** → có thể cho kết quả "không tốt hơn" → **có thể sai**. (3) Nêu đích danh hai tình huống mà cơ chế cạnh tranh *lẽ ra* phải thắng |
| **Lưu ý** | Contract Net **không tự cứu được** vấn đề vòng tròn — nếu vẫn chấm theo nhãn giả thì vòng tròn chỉ to hơn. Gold set là điều kiện tiên quyết |

#### RQ3 — thay đổi nguy hiểm nhất nếu bỏ qua

| | Nội dung |
|---|---|
| **Gốc** | *"Hệ thống MAS kết hợp DSS rule-based có tạo ra cải thiện đáng kể về **độ chính xác dự báo mức độ hài lòng**, khả năng phát hiện các trường hợp cần can thiệp, **thời gian xử lý** và **hiệu quả hỗ trợ quyết định** so với MIS truyền thống và mô hình học máy đơn lẻ hay không?"* |
| **Vấn đề** | (1) **Tự đặt bẫy**: MAS và single-ML dùng chung LightGBM → accuracy sẽ bằng nhau. (2) "Thời gian xử lý": MAS **chắc chắn chậm hơn** do overhead — hỏi cũng thua. (3) "Hiệu quả hỗ trợ quyết định" chưa thao tác hóa, và **không đo được** vì Olist không có biến hành động |
| **v2** | *"So với **ba** phương án thay thế — báo cáo kiểu MIS, mô hình học máy đơn lẻ, và **một hệ đơn khối có đầy đủ chức năng** — kiến trúc MAS-DSS khác biệt thế nào về (a) **chất lượng khuyến nghị theo đánh giá của chuyên gia**, (b) **tính giải thích được**, (c) **độ trễ xử lý end-to-end**?"* |
| **Ba thay đổi then chốt** | (1) **Bỏ hẳn "độ chính xác dự báo" khỏi câu hỏi**, chuyển thành **điều kiện kiểm soát** khai báo trước. (2) **Thêm baseline Monolithic-Complete** — không có nó, RQ3 chỉ là so với bù nhìn. (3) "Hiệu quả hỗ trợ quyết định" thao tác hóa bằng **đánh giá chuyên gia mù**, không phải metric tự bịa |
| **Về độ trễ** | Vẫn hỏi, nhưng **khai báo trước là kỳ vọng thua** (H5). Báo cáo cái giá của khả năng chịu lỗi làm luận văn đáng tin hơn nhiều so với chỉ khoe ưu điểm |

#### RQ4 gốc → RQ5 mới

| | Nội dung |
|---|---|
| **Gốc** | *"Trong những điều kiện bối cảnh nào (đặc điểm dữ liệu, quy trình kinh doanh, quy mô doanh nghiệp) kiến trúc MAS-DSS đề xuất phát huy hiệu quả tốt nhất, và mức độ có thể **mở rộng sang các bài toán quản trị tương tự như CRM hoặc chuỗi cung ứng** là như thế nào?"* |
| **Vấn đề** | **Không kiểm chứng được với một dataset.** Không có dữ liệu CRM, không có dữ liệu chuỗi cung ứng, không có dataset TMĐT thứ hai, không có dữ liệu về "quy mô doanh nghiệp". Trả lời câu này = **suy đoán, không phải nghiên cứu** |
| **v2 (RQ5)** | *"Kiến trúc đề xuất còn giữ được hiệu lực trong những **điều kiện thông tin** nào — cụ thể: (a) khi **thời điểm ra quyết định lùi về sớm hơn** (T₂ lúc bàn giao vận chuyển, thay vì T₃ sau khi giao hàng), (b) khi đơn hàng **không có bằng chứng văn bản** (không có bình luận review)?"* |
| **Cải thiện** | Trả lời được ngay **bằng chính Olist**, qua hai thí nghiệm cắt lớp. Đây là *context validity* đúng nghĩa |
| **CRM/chuỗi cung ứng đi đâu?** | Chuyển sang **lập luận phân tích ở Chương 5**, dựa trên **4 Design Principles** — các DP phát biểu ở mức trừu tượng, độc lập với miền, nên *có thể chuyển giao*. **Và nói rõ đây là suy luận thiết kế, chưa kiểm chứng thực nghiệm, là hướng nghiên cứu tiếp theo.** Trung thực và vẫn giữ được phần thảo luận có giá trị |

#### RQ4 mới — không có tiền thân trong đề cương gốc

| | Nội dung |
|---|---|
| **v2** | *"Khi một hoặc nhiều tác tử **lỗi (crash)** hoặc **suy giảm chất lượng mà không lỗi** (drift phân phối, mô hình mất hiệu chuẩn), kiến trúc MAS-DSS và kiến trúc đơn khối khác nhau thế nào về: (a) tỷ lệ hệ thống cho ra quyết định sai mà không cảnh báo (**silent failure**), (b) **độ nhạy và độ trễ phát hiện** của bộ giám sát, (c) mức suy giảm chất lượng quyết định, và (d) **chi phí phải trả** cho khả năng đó?"* |
| **Vì sao phải bổ sung** | Nó phụ trách **đóng góp thật** của luận văn — thứ hiện đang **không có RQ nào bảo vệ**. Văn liệu MAS-DSS hầu như không đánh giá khả năng chịu lỗi; đây là khoảng trống thật, hẹp, và lấp được |
| **Vì sao không tầm thường** | `silent_failure = 0%` của MAS là tautology (được thiết kế ra thế), **nhưng** độ nhạy/độ trễ phát hiện drift, tỷ lệ báo động giả, silent failure của Monolithic-Complete, và chi phí overhead thì **hoàn toàn là kết quả thực nghiệm** — không biết trước |
| **Vế (d) buộc phải trung thực** | Khả năng chịu lỗi **không miễn phí**. Báo cáo cái giá (latency, độ phức tạp) làm luận văn đáng tin hơn nhiều |

---

## Phần 3 — Ánh xạ với khung Validity (Larsen et al., 2025)

Đề cương gốc đã dùng khung này ở mục 2.3.3 và 3.2.5. **Cấu trúc giữ nguyên, nội dung đổi.**

| | Đề cương gốc (mục 3.2.5) | Bản v2 |
|---|---|---|
| **Criterion validity** | So MAS-DSS với MIS và ML đơn lẻ theo accuracy, Macro F1, khả năng phát hiện, thời gian xử lý, chất lượng chuỗi phát hiện–phân loại–đề xuất | **RQ2**: macro-F1 đa nhãn **trên gold set** vs classifier đơn khối. **RQ3**: **4 baseline** + **đánh giá chuyên gia mù** + kiểm định tương đương cho accuracy |
| **Causal validity** | Ablation: bỏ Recommendation/Action Agent hoặc mô-đun phân loại nguyên nhân | **RQ4**: ablation **+ chaos harness** (tiêm lỗi crash + Byzantine, 3 mức nhiễu loạn), so MAS vs Monolithic-Complete |
| **Context validity** | Phân tích trong bối cảnh Olist/Brazil, **thảo luận khả năng mở rộng sang CRM/chuỗi cung ứng** | **RQ5**: cắt lớp **T₂/T₃** và **có/không bình luận**. CRM/SCM → **lập luận phân tích qua DP**, ghi rõ là chưa kiểm chứng |
| **Design (mới)** | *(không có)* | **RQ1**: demonstration + 4 Design Principles — trả lời câu hỏi *"tri thức trừu tượng nào rút ra được?"* |

Đề cương gốc chỉ có ba loại claim. **Bản v2 thêm tầng design/prescriptive** — đây là thứ nâng luận văn
từ "tôi xây một cái" lên DSR thật, theo Gregor & Hevner (2013) và Gregor, Chandra Kuk & Hevner (2020).

---

## Phần 4 — Giả thuyết (đề cương gốc không có)

Đề cương gốc **không khai báo giả thuyết nào**. Bản v2 khai báo sáu, **kể cả hai cái kỳ vọng thua**:

| # | Giả thuyết | Kỳ vọng | Đo bằng |
|---|---|---|---|
| **H1** | MAS-DSS **không** khác biệt có ý nghĩa so với single-ML về accuracy / PR-AUC | **Vô hiệu — và đó là điều mong muốn** (điều kiện kiểm soát) | **Kiểm định tương đương**, không phải t-test |
| **H2** | Quy kết bằng đấu thầu cạnh tranh **tốt hơn** classifier đơn khối trên gold set, đặc biệt nhóm đa nguyên nhân | Có (nhưng có thể sai) | Macro-F1 đa nhãn trên gold set |
| **H3** | Khuyến nghị của MAS-DSS được chuyên gia đánh giá **phù hợp hơn** MIS và Monolithic-Complete | Có | Likert, kiểm định phi tham số, Krippendorff's α |
| **H4** | Khi tiêm lỗi, hệ đơn khối có **tỷ lệ hỏng âm thầm cao hơn đáng kể** | Có — và là kết quả *thật* (baseline không bị dàn dựng để hỏng) | Chaos harness |
| **H5** | MAS-DSS chịu **overhead độ trễ cao hơn** | **Có — và phải báo cáo** | Latency p50/p95 |
| **H6** | Bộ giám sát phát hiện drift trước khi chất lượng quyết định suy giảm quá ngưỡng | **Chưa biết** — kết quả thực nghiệm thật | Đường cong độ nhạy/độ trễ phát hiện |

Khai báo trước H1 và H5 (hai cái **kỳ vọng thua**) là dấu hiệu của nhà nghiên cứu chững chạc, và nó
chặn trước đòn phản biện *"anh đang cố chứng minh cái mình muốn tin"*. Nó cũng làm H2, H3, H4 đáng tin
hơn nhiều.

---

## Phần 5 — Phạm vi: những gì bị loại bỏ so với đề cương gốc

Đề cương gốc (mục 1.4.2) giới hạn phạm vi ở mức **chức năng** (chưa mở sang tài chính, nhân sự, chuỗi
cung ứng). Bản v2 bổ sung một lớp giới hạn về **tri thức luận** — thứ đề cương gốc không có, và là chỗ
dễ bị đánh nhất khi bảo vệ.

| Bị loại khỏi phạm vi | Lý do — viết thẳng vào Chương 1 |
|---|---|
| **Đo hiệu quả thực tế của hành động can thiệp** | Olist **không ghi nhận hành động nào đã được áp dụng** → không có biến treatment → không suy luận nhân quả được (Rubin causal model). Nghiên cứu đánh giá **chất lượng khuyến nghị** (qua chuyên gia), **không** phải hiệu quả can thiệp |
| **Tuyên bố "thời gian thực" / "biến động nhanh"** | Hệ chạy **batch offline** trên parquet. Latency đo được nhưng **không được gọi là real-time**. Đây là chữ có trong RQ1 và mục 1.1 của đề cương gốc |
| **"Nhận diện sớm" / "phòng ngừa"** | Feature mạnh nhất chỉ có **sau khi giao hàng**. Đổi framing sang **phục hồi dịch vụ (service recovery) trong cửa sổ trước review**. `expedite_shipment` bị loại vì bất khả thi về mặt thời gian ở T₃ |
| **Khái quát hóa sang CRM / chuỗi cung ứng bằng thực nghiệm** | Không có dữ liệu. Chuyển sang **lập luận phân tích qua Design Principles**, nói rõ là chưa kiểm chứng |
| **"Quy mô doanh nghiệp" như một biến bối cảnh** | Olist là một nền tảng, một thị trường, 2016–2018. Không có biến quy mô để cắt lớp |
| **LLM agent** (mặc định) | Sẽ **làm nhiễu loạn causal claim** ở RQ4: nếu MAS thắng, không tách được phần nào do kiến trúc, phần nào do LLM. Chỉ thêm như **một nhánh thí nghiệm riêng** nếu dư thời gian |

**Tuyên bố phạm vi rõ ràng là áo giáp khi bảo vệ, không phải sự thú nhận yếu kém.**

---

## Phần 6 — Tác động lên từng chương của đề cương

Bảng này là danh sách việc phải làm khi cập nhật bản Word/PDF.

| Chương / mục | Trong đề cương gốc | Phải sửa gì | Mức |
|---|---|---|---|
| **1.1 Bối cảnh** | "dữ liệu... **biến động nhanh**", "xử lý... **trong thời gian thực**" | Bỏ mọi tuyên bố real-time. Đổi thành "batch định kỳ tại điểm giao hàng" | **Bắt buộc** |
| **1.1 Bối cảnh** | "**nhận diện sớm** các đơn hàng có nguy cơ" | Đổi framing sang **service recovery tại T₃**, nêu cửa sổ trước review | **Bắt buộc** |
| **1.2 Mục tiêu** | 3 mục tiêu | Thay bằng MT1–MT3 v2 (§1.1 tài liệu này) | **Bắt buộc** |
| **1.3 Câu hỏi** | 4 RQ | Thay bằng 5 RQ v2 (§2 tài liệu này) | **Bắt buộc** |
| **1.4.2 Phạm vi** | Chỉ giới hạn chức năng | **Thêm mục "Giới hạn về tri thức luận"** (§5 tài liệu này) | **Bắt buộc** |
| **1.5 Cấu trúc** | 5 chương | Không đổi | — |
| **2.2 Kiến trúc MAS** | 5 tác tử: Data Integration, Analytics, Prediction, Recommendation/Action, Dashboard | Cập nhật thành 15 agent + tầng MAS (message, CNP, supervisor, guard) — xem [technical-plan-v3.md Phụ lục A.2](technical-plan-v3.md) | **Bắt buộc** |
| **2.3 Literature review** | Trọng tâm ở **agentic AI / LLM-MAS** (Reyes Fernández de Bulnes 2025, Bandi 2025, MCP) | **Chuyển trọng tâm sang coordination protocols**: Smith (1980) Contract Net, Hayes-Roth (1985) Blackboard, FIPA-ACL, Erlang/OTP supervision. Giữ LLM-MAS như **hướng mở rộng tương lai**, không phải nền tảng | **Bắt buộc** — nếu không, có độ lệch giữa Chương 2 và thứ thực sự xây |
| **2.3.3 Khung Validity** | 3 loại claim | Thêm tầng **design/prescriptive** cho RQ1 (§3 tài liệu này) | Nên làm |
| **3.2.2 Mục tiêu giải pháp** | Lặp lại 3 mục tiêu | Đồng bộ với 1.2 mới | **Bắt buộc** |
| **3.2.3 Thiết kế & phát triển** | Mô tả 5 agent | Cập nhật theo technical-plan-v3. **Thêm mục 4 Design Principles** | **Bắt buộc** |
| **3.2.5a Criterion** | So với MIS + single-ML | Thêm **Monolithic-Complete**; thêm **đánh giá chuyên gia**; accuracy → **điều kiện kiểm soát** | **Bắt buộc** |
| **3.2.5b Causal** | Ablation từng agent | Thêm **chaos harness** (phân loại lỗi, quy trình tiêm, bộ chỉ số, giao thức so sánh) | **Bắt buộc** |
| **3.2.5c Context** | Thảo luận mở rộng CRM/SCM | Thay bằng **cắt lớp T₂/T₃ và có/không bình luận**. CRM/SCM → lập luận qua DP ở Chương 5 | **Bắt buộc** |
| **3.3 Thiết kế kiến trúc** | Luồng tuần tự Data → Analytics → Prediction → Recommendation → Dashboard | Thay bằng **định tuyến động + CNP + blackboard + supervision** | **Bắt buộc** |
| **Chương 4** | Chưa viết | Viết mới: decision point T₃, feature set, gold set, 4 baseline, 6 giả thuyết, bộ chỉ số, giao thức chuyên gia | Viết mới |
| **Chương 5** | Chưa viết | Viết mới. **Con số đầu tiên phải là % đơn bất mãn không có bình luận** | Viết mới |
| **Tài liệu tham khảo** | 9 mục | Thêm: Smith (1980), Hayes-Roth (1985), FIPA-ACL, Gregor & Hevner (2013), Gregor/Chandra Kuk/Hevner (2020), Venable/Pries-Heje/Baskerville (FEDS), Souza et al. (BERTimbau), Rubin causal model | **Bắt buộc** |

---

## Phần 7 — Tuyên bố: cái gì bỏ, cái gì giữ

| **Đừng tuyên bố** (nằm trong hoặc suy ra từ đề cương gốc) | **Vì sao** |
|---|---|
| ~~"MAS-DSS dự báo chính xác hơn mô hình đơn lẻ"~~ | Dùng chung model — sẽ không đúng |
| ~~"Hành động khuyến nghị cải thiện mức độ hài lòng"~~ | Không kiểm chứng được trên Olist (không có treatment) |
| ~~"Hệ thống phòng ngừa bất mãn từ sớm"~~ | Feature chỉ có sau khi giao hàng |
| ~~"Xử lý trong thời gian thực"~~ | Hệ chạy batch offline |
| ~~"Silent failure = 0% chứng minh tính vượt trội"~~ | Tautology — kiểm tra đặc tả, không phải phát hiện |

| **Nên tuyên bố** | Bằng chứng đứng sau |
|---|---|
| "Với **cùng năng lực dự báo**, kiến trúc đa tác tử tạo ra một **chuỗi quyết định giải thích được và chịu lỗi** mà kiến trúc đơn khối không có — và cái giá phải trả là *x* ms overhead trên mỗi case" | Kiểm định tương đương (H1) + chaos harness (H4) + latency (H5) |
| "Hệ thống phát hiện đơn có nguy cơ **tại điểm giao hàng** và đề xuất hành động **phục hồi dịch vụ** trong cửa sổ trước khi khách viết đánh giá; khuyến nghị được **chuyên gia đánh giá** phù hợp hơn đáng kể so với báo cáo kiểu MIS (Likert *a* vs *b*, α = *c*)" | Đánh giá chuyên gia mù (A7, H3) |
| "Khi một tác tử lỗi, kiến trúc đơn khối hỏng **âm thầm** trên *p*% case, trong khi kiến trúc đề xuất suy giảm **minh bạch** và chuyển giao cho con người" | Chaos harness trên Monolithic-Complete (H4) |
| "Bộ giám sát phát hiện drift phân phối ở mức *d*% sau *n* case, với tỷ lệ báo động giả *f*%" | Đường cong độ nhạy guard (H6) |
| "Bốn Design Principles có thể chuyển giao sang CRM / chuỗi cung ứng" — **nêu rõ là suy luận thiết kế chưa kiểm chứng** | A2 + lập luận phân tích Chương 5 |

Những tuyên bố này **hẹp hơn** đề cương gốc, nhưng **đúng** — và mỗi cái đều có bằng chứng không vòng
tròn đứng sau.

---

## Phần 8 — Novelty claim: nói cho chính xác

Theo Gregor & Hevner (2013): Contract Net (1980), Blackboard (1985), OTP supervision (1990s), FIPA-ACL
(2002) — **không có gì mới**. Bài toán (DSS cho hài lòng khách hàng TMĐT) cũng không mới. Vậy đây là
**Improvement** (giải pháp mới cho vấn đề đã biết) — hoàn toàn hợp lệ cho luận văn thạc sĩ, nhưng
**tuyên bố novelty phải khiêm tốn và chính xác**.

Đề cương gốc phát biểu khoảng trống là *"thiếu một framework tích hợp hoàn chỉnh cho HTTT doanh nghiệp
trong TMĐT"* — quá rộng, và dễ bị chỉ ra là đã có người làm.

**Phát biểu v2, hẹp và bảo vệ được:**

> **Tích hợp giám sát chịu lỗi và suy giảm minh bạch vào một pipeline hỗ trợ quyết định, cùng với một
> phương pháp đánh giá (chaos harness) để định lượng khả năng chịu lỗi của DSS — một khía cạnh mà văn
> liệu MAS-DSS hiện tại bỏ trống.**

Kèm theo **4 Design Principles** làm tri thức trừu tượng rút ra được. Đừng tuyên bố rộng hơn thế.

---

## Phần 9 — Sáu việc P0, theo thứ tự

| # | Việc | Vì sao trước tiên |
|---|---|---|
| 1 | **Đếm % đơn bất mãn không có bình luận** trong Olist | Nếu > 40%, "Root Cause Agent" trên phần lớn dữ liệu chỉ là ngưỡng `delivery_delay` đội lốt ML. **Con số này quyết định RQ2 có tồn tại được hay không** |
| 2 | **Xóa `review_lag_days`** khỏi feature set | Rò rỉ nhãn trắng trợn — chỉ tồn tại sau khi review đã viết |
| 3 | Chốt **decision point = T₃**, đổi framing sang **service recovery**, sửa tập luật (bỏ `expedite`) | Hệ hiện đang khuyến nghị điều bất khả thi về mặt thời gian |
| 4 | **Bắt đầu gold set ngay** (A3) | Mất nhiều thời gian nhất, là **đường tới hạn**. Không có nó, Chương 5 vô giá trị. Chạy song song với code |
| 5 | Cập nhật **Chương 1** (mục tiêu, RQ, phạm vi) và **Chương 3** (thêm 4 DP, sửa 3.2.5) | Để phần viết không phải làm lại lần hai |
| 6 | Dựng **Monolithic-Complete** baseline (A6) | Rẻ (~1 ngày), nhưng quyết định giá trị của toàn bộ Chương 5 |
