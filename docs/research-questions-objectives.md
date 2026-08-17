# Câu hỏi nghiên cứu và Mục tiêu nghiên cứu

> **Trạng thái:** bản tổng hợp hiện hành, **nguồn chuẩn duy nhất** cho mục **1.2 (Mục tiêu)** và
> **1.3 (Câu hỏi nghiên cứu)** của luận văn. Chép thẳng từ file này vào bản Word.
>
> **Bản này thu gọn từ năm câu hỏi xuống ba**, theo tiêu chí *giá trị đóng góp × tính khả thi trong
> khung thời gian luận văn*. Lý do thu gọn và số phận của hai câu bị loại: §2.4. Bản năm câu hỏi được
> giữ nguyên trong [research-design-v2.md](research-design-v2.md) làm hồ sơ thiết kế.
>
> **Quan hệ với bộ tài liệu:**
>
> | File | Vai trò | Còn hiệu lực |
> |---|---|---|
> | **research-questions-objectives.md** (file này) | MT, RQ, giả thuyết, thao tác hóa, phạm vi, ma trận truy vết | ✅ **Nguồn chuẩn** cho câu hỏi, mục tiêu & phạm vi |
> | [research-design-v2.md](research-design-v2.md) | Danh mục artifact A1–A7; bản 5 câu hỏi và lý do viết lại từng câu | ✅ Nguồn chuẩn cho **artifact**; hồ sơ bản 5 câu |
> | [technical-plan-v3.md](technical-plan-v3.md) | Kiến trúc, quyết định công nghệ, cấu trúc mã nguồn, lộ trình thi công, đặc tả chi tiết | ✅ **Nguồn chuẩn cho kỹ thuật** |
> | [technical-design-v2.md](technical-design-v2.md) | Bản thiết kế kỹ thuật cũ | ❌ **Lỗi thời** — thay thế bởi technical-plan-v3.md |
> | [proposal-comparison.md](proposal-comparison.md) | Đối chiếu nguyên văn với đề cương gốc, việc phải sửa từng chương | ✅ Tài liệu chuyển đổi |
> | [adversarial-review.md](adversarial-review.md) | Hồ sơ lý do — mọi thay đổi truy được về một mục cụ thể | ✅ Hồ sơ |
> | [plan-2026-08-12.md](plan-2026-08-12.md) | **Kế hoạch đã duyệt** cho đợt viết lại này, giữ nguyên văn + biên bản thi công | ✅ Hồ sơ khai báo trước |
> | [mas-redesign-plan.md](mas-redesign-plan.md) | Bản v1 | ❌ **Lỗi thời** — đừng trích |

---

## ⚠️ Số hiệu câu hỏi nghiên cứu đã đổi (12/08/2026)

Ba câu hỏi được **sắp xếp lại theo trọng số đóng góp**. Nội dung từng câu giữ nguyên bản chất; chỉ
**số hiệu và thứ tự trình bày** thay đổi.

| Số hiệu **mới** | Nội dung | Số hiệu **cũ** | Vai trò mới |
|---|---|---|---|
| **RQ1** | **Chịu lỗi** — hỏng âm thầm, phát hiện, suy giảm, chi phí | RQ3 | **trục chính** |
| **RQ2** | **Thiết kế** — truy vết được, trung thực về độ tin cậy, 4 DP | RQ1 | giải thích **vì sao** RQ1 cho kết quả đó |
| **RQ3** | **Điều kiện kiểm soát** — không đánh đổi độ chính xác | RQ2 | loại bỏ lời giải thích thay thế |

**Vì sao đổi.** Phép so sánh trung tâm của RQ2 cũ cho kết quả **âm** — hai kiến trúc giống hệt nhau
trên **250/250 đơn**, một đẳng thức **đại số** chứ không phải kết quả thống kê. Trong khi đó câu hỏi
về chịu lỗi có số đo mạnh *(hỏng âm thầm **0,0%** so với **16–100%**)* và là khoảng trống thật trong
văn liệu MAS-DSS. Kết quả âm không bị vứt bỏ — nó đổi vai trò thành **điều kiện kiểm soát**, thứ làm
cho claim nhân quả ở RQ1 **đáng tin hơn**.

**Phạm vi đã đồng bộ** *(245 test xanh sau khi đổi)*:

| Đã đổi sang số hiệu mới | Cố ý **giữ** số hiệu cũ |
|---|---|
| file này · `status-checklist.md` · `build-plan.md` · `session-state.md` | `methodology-log.md` — **nhật ký, giữ nguyên văn**; có bảng tra ở đầu file |
| `src-v3/` + `tests-v3/` *(153 tham chiếu, 71 tệp)* · `config/v3/rules.yaml` | `thesis-mapping.md` — ánh xạ **đề cương gốc 5 câu** vào codebase v1 đã đóng băng |

> Trong chính file này, các tham chiếu ghi rõ *"RQ… gốc"* / *"RQ… cũ"* *(§2.4, §3.1, §7.3)* chỉ bản đề
> cương 5 câu và **không** đổi theo.

---

## Phần 0 — Năm ràng buộc dữ liệu định hình toàn bộ mục tiêu và câu hỏi

Đây không phải là các lưu ý kỹ thuật mà là **biên của nghiên cứu**. Mọi mục tiêu hoặc câu hỏi vi phạm
một trong năm ràng buộc dưới đây đều đã bị loại khỏi bản này, bất kể mức độ hấp dẫn về mặt học thuật.

> **Ràng buộc khác giả thuyết.** Ràng buộc kiểm chứng được bằng **đọc lược đồ dữ liệu**, không cần thí
> nghiệm — nên nó **được phép sửa** khi hiểu biết về dữ liệu thay đổi. Giả thuyết thì không: sửa một
> giả thuyết sau khi thấy kết quả là HARKing. **C3 được sửa** và **C5 được bổ sung** trong bản này,
> cả hai đều dựa trên phép đo trên dữ liệu thô chứ không dựa trên kết quả thí nghiệm.

| # | Ràng buộc | Hệ quả đối với mục tiêu và câu hỏi |
|---|---|---|
| **C1** | **Bộ dữ liệu Olist không có biến treatment.** Không trường dữ liệu nào ghi nhận hành động đã được áp dụng, và không tồn tại kết quả phản thực | Không mục tiêu hay câu hỏi nào được phép hỏi *"hành động can thiệp có hiệu quả hay không"*. Nghiên cứu đánh giá **chất lượng khuyến nghị**, không phải **hiệu quả can thiệp** |
| **C2** | **Nhãn nguyên nhân không tồn tại sẵn trong dữ liệu.** Nhãn hiện có do chính nghiên cứu sinh ra bằng luật từ khóa | Mọi câu hỏi về quy kết nguyên nhân **bắt buộc** đo trên **tập nhãn chuẩn do người gán** (gold set). Weak label chỉ là tín hiệu huấn luyện có nhiễu, không bao giờ là thước đo |
| **C3** *(sửa 12/08)* | **Kết cục giao hàng KHÔNG dùng được để dự báo.** Đặc trưng mạnh nhất — độ trễ thực tế, có giao được hay không — chỉ xác định sau khi giao; nhưng đánh giá của khách đến **trung vị 6,2 giờ** sau đó, và **87,8%** đánh giá viết **trước** hạn dự kiến | Mốc quyết định phải neo vào **ngày mua**, không vào sự kiện giao hàng. **T₃ = ngày mua + 7** — chọn theo **đánh đổi phủ sóng ↔ tín hiệu**, xem bảng ở §0.3. Tín hiệu mạnh nhất khả dụng là **tiến độ vận chuyển**, không phải kết cục. Bài toán vẫn là **phục hồi dịch vụ**; các cụm "nhận diện sớm" và "thời gian thực" vẫn bị loại |
| **C4** | **Bằng chứng văn bản xuất hiện cùng lúc với nhãn.** Trường `review_comment_message` được khách hàng viết cùng thời điểm với `review_score` | Chuỗi xử lý bắt buộc tách làm **hai mốc quyết định** (§0.2): dự báo rủi ro tại **T₃** chỉ trên đặc trưng bảng; quy kết nguyên nhân tại **T₄** khi đánh giá đã về. Đặc trưng `has_comment` bị **cấm** ở giai đoạn T₃ vì chưa tồn tại và tương quan mạnh với nhãn |
| **C5** *(mới 12/08)* | **Không tồn tại quan sát nào về chất lượng sản phẩm hay chất lượng dịch vụ trước khi đánh giá được viết.** Toàn bộ trường thời gian trong 9 bảng Olist chỉ gồm: *mua · bàn giao 3PL · giao khách · hạn dự kiến · viết đánh giá · trả lời đánh giá*. Không bảng phiếu hỗ trợ, không đổi trả, không lịch sử liên hệ | Quy kết `quality` và `service` **bất khả thi ở mọi mốc trước T₄** — không vì mô hình yếu mà vì **không có gì để quan sát**: `quality` bộc lộ khi khách mở hộp, `service` khi khách liên hệ người bán, và không sự kiện nào được ghi lại. Đây là **biện minh dữ liệu cho kiến trúc hai mốc**: sự phân chia T₃/T₄ là **hệ quả bắt buộc**, không phải lựa chọn tiện lợi |

### 0.1 Số liệu kiểm chứng M0 *(đã đo trên dữ liệu thật)*

Đây là con số quyết định RQ3 có tồn tại được hay không, và phải xuất hiện ngay đầu Chương 5.

Đơn vị phân tích của nghiên cứu là **case đơn hàng**, không phải dòng đánh giá thô. Trong Olist có 551
đơn mang nhiều hơn một bản ghi đánh giá; sau khử trùng (giữ bản sớm nhất) còn 98.673 case. Cột "dòng
thô" giữ lại để đối chiếu, cột "case đơn hàng" là con số **dùng trong luận văn**.

| Chỉ tiêu | Dòng thô | **Case đơn hàng** | Dự kiến ban đầu | Ngưỡng cảnh báo |
|---|---|---|---|---|
| Tổng số đánh giá | 99.224 | **98.673** | — | — |
| Đánh giá bất mãn (1–2★) | 14.575 — 14,69% | **14.475 — 14,67%** | 12–15% | Khớp; giữ PR-AUC làm chỉ số chính |
| Tầng A — **có** `review_content` | 10.889 — 74,71% | **10.823 — 74,77%** | 55–60% | — |
| Tầng B — **không có** `review_content` | 3.686 — 25,29% | **3.652 — 25,23%** | 40–45% | >40% đáng lo · >50% phải xét lại phạm vi RQ3 |
| *(phụ)* Không một chữ nào, kể cả tiêu đề | 3.581 — 24,56% | **3.547 — 24,50%** | — | — |

Kết luận: **cổng M0 đạt**, và điều kiện dữ liệu thuận lợi hơn dự kiến. Rủi ro *"tỷ lệ không bình luận
vượt 50%"* được đóng lại. Không đánh giá nào bị mất khi ghép bảng; sai lệch lớn nhất giữa hai đơn vị
đếm là 0,56%.

> **Đính chính so với bản ghi đầu tiên.** Cặp số "74,71% / 24,6%" từng được ghi cạnh nhau nhưng trộn
> hai định nghĩa: 74,71% tính theo `review_content`, còn 24,6% tính theo *không có cả nội dung lẫn tiêu
> đề* — hai con số không bù nhau. Định nghĩa thống nhất đã chốt là **theo `review_content`**, nên cặp
> đúng là **74,77% / 25,23%**; chỉ tiêu 24,50% được báo cáo riêng.

Chỉ tiêu được chọn là `review_content`, không phải hợp của `review_content` và `review_title`: gộp cả
hai chỉ thêm 105 đơn (2.246 trong số 2.351 đơn có tiêu đề thì cũng có nội dung), trong khi tiêu đề
thường là cụm ngắn không mang thông tin quy kết nguyên nhân.

**Phát hiện phụ đáng đưa vào Chương 5.** Tỷ lệ để lại nội dung theo mức sao có dạng chữ U và **không
đơn điệu**: 1★ 76,54% · 2★ 68,07% · 3★ 43,48% · 4★ 31,19% · **5★ 35,82%**. Khách hàng viết khi cảm xúc
mạnh về cả hai phía. Hệ quả kỹ thuật: sự hiện diện của bình luận tự nó là tín hiệu mạnh về mức độ bất
mãn, nên `has_comment` là một đặc trưng rò rỉ nhãn nếu lọt vào giai đoạn T₃ — ngang hàng với
`review_lag_days` (ràng buộc C4).

### 0.2 Hai mốc quyết định

Ràng buộc C4 buộc chuỗi xử lý tách làm hai giai đoạn. Đây không phải chi tiết cài đặt mà là điều kiện
để RQ3 có nghĩa: nhãn chuẩn do người gán được tạo ra bằng cách **đọc bình luận**, tức bản thân nhãn là
thông tin ở T₄; không thể dùng nhãn T₄ để chấm điểm một hệ thống bị chặn không cho thấy dữ liệu T₄.

| | **Giai đoạn 1 — T₃ = ngày mua + 7** | **Giai đoạn 2 — T₄** *(khi đánh giá 1–2★ về)* |
|---|---|---|
| Nhiệm vụ | Dự báo rủi ro bất mãn | Quy kết nguyên nhân |
| Bằng chứng khả dụng | Chỉ đặc trưng bảng: giao hàng, giá/phí, seller, nhóm hàng | Toàn bộ đặc trưng bảng **+ văn bản với 74,77% đơn** |
| Hành động | Phục hồi dịch vụ **chủ động** | Phân loại khiếu nại và phục hồi **phản ứng** |
| Tầng A/B | Toàn bộ thuộc tầng B — không có bằng chứng văn bản | A 74,77% · B 25,23% |
| Câu hỏi phụ trách | H1 (điều kiện kiểm soát) | **RQ3** |

Cách đóng khung *phục hồi dịch vụ* **không bị mất** khi chuyển RQ3 sang T₄: văn liệu về recovery
paradox bàn về việc phục hồi *sau khi* khách hàng đã bày tỏ bất mãn, nên giai đoạn 2 khớp với lý thuyết
đó chặt hơn giai đoạn 1.

### 0.3 Vì sao chọn mốc +7 — đánh đổi phủ sóng và tín hiệu

| Mốc | Tổng thể | Phủ đơn bất mãn | Tỷ lệ nền | Lift nhóm *chưa bàn giao 3PL* |
|---|---|---|---|---|
| mua + 3 | 95.087 | 98,1% | 14,93% | 1,32 |
| mua + 5 | 87.166 | 94,0% | 15,61% | 1,67 |
| **mua + 7** | **75.480** | **87,4%** | **16,77%** | **2,12** ← chọn |
| mua + 10 | 54.717 | 75,4% | 19,96% | **2,39** |
| mua + 14 | 34.163 | 61,5% | 26,04% | 2,36 |
| mua + 21 | 14.576 | 41,5% | 41,25% | 1,86 |

> ⚠️ **Đính chính.** Bản trước của C3 viết *"mức tối ưu đo được: lift đạt đỉnh 2,19"* tại +7. Cả hai
> vế đều sai khi đo lại: lift tại +7 là **2,12**, và nó **không** đạt đỉnh ở đó — lift còn tăng tới
> **2,39** ở mốc +10. Xem **L35**.

**Lý do chọn +7 vẫn đứng vững, nhưng phải phát biểu đúng.** Nó không phải mốc cho tín hiệu mạnh nhất;
nó là mốc **cân bằng**. Đẩy sang +10 mua thêm 0,27 lift nhưng đánh mất **12 điểm phần trăm phủ sóng** —
tức 1.700 đơn bất mãn không còn kịp can thiệp. Với một hệ **phục hồi dịch vụ**, số đơn tiếp cận được
là đại lượng có nghĩa nghiệp vụ; xếp hạng tốt hơn trên một tổng thể đã thu hẹp không bù lại được.

Mốc **+10 được giữ làm phân tích độ nhạy** *(một lần đổi `CONFIG.t3_cutoff_days`)*, không phải cấu
hình chính.

---

#### Tổng thể và phép chia tập — số liệu đã đo *(cấu hình T₃ = ngày mua + 7)*

Mốc quyết định ràng buộc **hai** thứ: *đặc trưng nào tồn tại*, và *đơn nào đã tới được mốc*. Vế thứ
hai từng bị bỏ ngỏ hai lần — **L30** rồi **L33** — nên nay nó được cưỡng chế bằng **tệp vật lý riêng**
*(`data/v3/features/`, xem `data/export.py`)*, không phải bằng bộ lọc lúc chạy.

| | Số đơn | Ghi chú |
|---|---|---|
| Đơn có đánh giá | 98.673 | toàn bộ |
| **Còn kịp can thiệp tại T₃** | **75.480** *(76,5%)* | điều kiện `review_created_at > t3_cutoff` |
| Phủ sóng đơn bất mãn | **12.656 / 14.475 = 87,4%** | đây là đại lượng đánh đổi khi dời mốc |

| Tập | Số đơn | Ngày mua từ | Đến | Tỷ lệ bất mãn |
|---|---|---|---|---|
| **train** | 52.835 | 2016-09-04 | 2018-03-22 | **17,90%** |
| **val** | 9.077 | 2018-03-22 | 2018-05-23 | **14,82%** |
| **test** | 11.322 | 2018-05-31 | 2018-08-23 | **12,74%** |

**Tỷ lệ nền trôi 17,90% → 14,82% → 12,74%**, đơn điệu giảm. Đây là **dịch chuyển phân phối thật** qua
thời gian; nó vừa giải thích vấn đề hiệu chuẩn vừa cho bộ giám sát drift của RQ1 một nhiệm vụ có thật.

**Khoảng cách ly.** Nhãn chỉ tồn tại lúc khách viết đánh giá — muộn hơn lúc mua. Mô hình chấm điểm kỳ
test được mô phỏng là huấn luyện tại `test_start`, nên mọi dòng train/val có `review_created_at` sau
mốc đó bị loại: **1 dòng train · 2.245 dòng val**.

> **Một hệ quả phải nói rõ.** Dòng bị loại **không** là mẫu ngẫu nhiên — người viết đánh giá muộn bất
> mãn nhiều hơn hẳn. Bản cách ly chặt hơn *(train cách ly theo `val_start`)* đã được thử và bị bác:
> nó loại **5.789 dòng có tỷ lệ bất mãn 29,52%** so với **16,28%** ở phần giữ lại — tức cắt đúng nhóm
> khó nhất — mà **không mua được gì**, vì một dòng train có đánh giá đến trong kỳ *val* không chứa
> thông tin nào về kỳ *test*. Hai con số này được ghi vào `manifest.json`.

---

**Nguyên tắc chọn câu hỏi:** mỗi câu hỏi phải trả lời được bằng dữ liệu thực sự có, và phải có khả năng
cho ra câu trả lời phủ định. Một câu hỏi mà kết quả đã biết trước, hoặc không thể sai, không phải là
câu hỏi nghiên cứu.

**Nguyên tắc thu gọn còn ba câu:** mỗi câu hỏi được giữ lại phải đồng thời (i) mang một đóng góp phân
biệt được với các câu còn lại, (ii) trả lời được bằng nguồn lực nằm trong tầm kiểm soát của nghiên cứu
sinh, và (iii) có một artifact tương ứng đã được xác định. Câu hỏi phụ thuộc vào nguồn lực bên ngoài
không kiểm soát được thì bị chuyển thành nhánh tùy chọn, không nằm trong tuyến chính.

---

## Phần 1 — Mục tiêu nghiên cứu

### 1.1 Mục tiêu tổng quát

Nghiên cứu hướng đến việc **thiết kế, hiện thực hóa và đánh giá một kiến trúc hệ thống thông tin đa tác
tử tích hợp hệ hỗ trợ ra quyết định dựa trên luật (MAS-DSS) đạt được ĐỘ TIN CẬY VẬN HÀNH DƯỚI ĐIỀU KIỆN
LỖI MÀ KHÔNG PHẢI ĐÁNH ĐỔI ĐỘ CHÍNH XÁC**, cho chuỗi ra quyết định *phát hiện rủi ro không hài lòng →
quy kết nguyên nhân → đề xuất hành động phục hồi dịch vụ* trong thương mại điện tử; đồng thời **rút ra
tập nguyên lý thiết kế (Design Principles)** cho việc xây hệ hỗ trợ quyết định vận hành được khi một
hoặc nhiều thành phần gặp lỗi hoặc suy giảm chất lượng.

Nghiên cứu **thiết lập trước một điều kiện kiểm soát** — kiến trúc đề xuất và các kiến trúc đối chứng
vận hành trên **cùng một năng lực nền**, nên **tương đương về độ chính xác** — rồi đo **khả năng chịu
lỗi trên toàn bộ bề mặt hỏng của kiến trúc**, **cùng với cái giá phải trả**.

> **Vì sao phát biểu theo hướng "không phải đánh đổi" thay vì "vượt trội".** Thêm khả năng chịu lỗi vào
> một hệ thống **thường phải trả giá** bằng độ chính xác hoặc độ trễ. Ở đây thì không: hai kiến trúc
> dùng chung năng lực nền nên cho kết quả **giống hệt nhau**. Đó là góc nhìn đúng cho một **quyết định
> thiết kế** — người triển khai không hỏi *"kiến trúc này có chính xác hơn không?"* mà hỏi *"nếu tôi
> chọn nó, tôi mất gì?"*.

Mục tiêu tổng quát này được cụ thể hóa qua **ba** lựa chọn về mặt phương pháp:

- **Thay thế tiêu chí "phù hợp" bằng hai thuộc tính quan sát được.** Đề cương gốc đặt mục tiêu thiết kế
  kiến trúc "phù hợp với hệ thống thông tin doanh nghiệp" — một tiêu chí không thao tác hóa được. Bản
  này thay bằng *tính truy vết được* (decision trace dựng lại được từ nhật ký giao tiếp) và *tính trung
  thực về độ tin cậy* (mọi quyết định mang theo mức suy giảm năng lực của hệ thống tại thời điểm sinh
  ra nó). Cách thao tác hóa chi tiết được trình bày tại RQ2 (§2.2).
- **Đặt điều kiện lỗi và suy giảm chất lượng làm ràng buộc thiết kế hạng nhất**, thay vì xem đó là vấn
  đề kỹ thuật vận hành nằm ngoài phạm vi nghiên cứu.
- **Nêu thẳng những gì nghiên cứu KHÔNG tuyên bố, và biến việc đó thành một bước có chủ đích.** Chứng
  minh trước rằng kiến trúc đề xuất **không** vượt trội về độ chính xác **loại bỏ lời giải thích thay
  thế** cho mọi khác biệt còn lại: nếu MAS-DSS vừa chính xác hơn vừa chịu lỗi tốt hơn, phản biện
  *"có phải chỉ vì mô hình tốt hơn không?"* sẽ không bác được. Ranh giới tuyên bố đầy đủ tại §6.

### 1.2 Các mục tiêu cụ thể

Luận văn đặt ra ba mục tiêu cụ thể, **sắp xếp theo trọng số đóng góp** chứ không theo thứ tự thi công,
và **ánh xạ một–một với ba câu hỏi nghiên cứu** tại §2.

> **Vì sao đảo thứ tự so với bản trước.** Mục tiêu về khả năng chịu lỗi *(trước đây là MT3)* nay đứng
> đầu vì ba lý do đo được: văn liệu MAS-DSS hầu như chỉ báo cáo độ chính xác và **bỏ trống** khía cạnh
> chịu lỗi · nó **khả thi nhất** vì sự thật nền là chính chỗ đã tiêm lỗi, không cần gán nhãn · và
> nghiên cứu **đã có số đo** — hỏng âm thầm **0,0% so với 16–100%**.
>
> Ngược lại, mục tiêu về quy kết nguyên nhân *(trước đây là MT2)* xuống cuối vì phép so sánh trung tâm
> của nó cho kết quả **âm**: hai kiến trúc giống hệt nhau trên **250/250 đơn**. Kết quả âm đó không bị
> vứt bỏ — nó đổi vai trò thành **điều kiện kiểm soát** cho MT1.

---

#### **MT1 — Phát triển và công bố phương pháp đánh giá khả năng chịu lỗi** → **RQ1**

**Phát biểu.** Đánh giá artifact trong điều kiện lỗi và suy giảm chất lượng, đối chiếu với một hệ đơn
khối đầy đủ chức năng được xây dựng công bằng; đồng thời công bố phương pháp đánh giá khả năng chịu lỗi
(chaos harness) như một đóng góp về phương pháp luận.

**Các nhiệm vụ cụ thể:**

- **MT1.1 — Xây dựng bộ khung đánh giá và các phương án thay thế** *(artifact A6)*
  - Sản phẩm: bốn hệ thống chạy trên cùng dữ liệu và cùng phương án chia tập theo thời gian — báo cáo
    kiểu MIS, mô hình học máy đơn lẻ, hệ đơn khối đầy đủ chức năng (Monolithic-Complete), và MAS-DSS.
  - Tiêu chí hoàn thành: Monolithic-Complete sử dụng **chung** mô hình dự báo, **chung** BERTimbau head
    và **chung** tập luật YAML với MAS-DSS, chỉ khác ở chỗ không có tầng đa tác tử; hệ này được cài đặt
    theo cách tự nhiên nhất mà một kỹ sư có kinh nghiệm sẽ viết, không bị làm yếu có chủ ý. Đây là điều
    kiện để phép so sánh không trở thành so với một baseline bù nhìn.

- **MT1.2 — Phát triển phương pháp đánh giá khả năng chịu lỗi** *(artifact A4)*
  - Sản phẩm: một quy trình tái sử dụng được gồm bốn thành phần — phân loại lỗi (crash fault và
    Byzantine/quality fault), quy trình tiêm lỗi có kiểm soát, bộ chỉ số, và giao thức so sánh.
  - Tiêu chí hoàn thành: năm nhóm lỗi được tiêm ở ba mức nhiễu loạn, trong đó nhóm lỗi tinh vi (drift
    phân phối, hoán vị nhãn một phần, bid lệch hệ thống) **không được thiết kế riêng để bộ giám sát bắt
    được**; **cùng một kịch bản lỗi** được chạy trên cả MAS-DSS lẫn Monolithic-Complete.

- **MT1.3 — Định lượng và công bố chi phí của kiến trúc**
  - Sản phẩm: số liệu độ trễ p50/p95 end-to-end, số thành phần hệ thống, và quy mô mã nguồn của tầng
    chịu lỗi, đối chiếu giữa MAS-DSS và Monolithic-Complete.
  - Tiêu chí hoàn thành: chi phí được báo cáo đầy đủ và công khai. Khả năng chịu lỗi không miễn phí;
    việc công bố cái giá phải trả là điều kiện để các kết luận về ưu điểm giữ được độ tin cậy.

**So với đề cương gốc.** Đây là mục tiêu thay đổi nhiều nhất, do MT3 gốc mắc ba lỗi về thiết kế đánh
giá:

- **Baseline bị làm yếu.** MAS-DSS "thắng" ở những chỉ số mà các baseline *bị định nghĩa* là bằng 0
  (`pipeline_completeness`, `action_cause_fit`), trong khi Larsen et al. (2025) yêu cầu criterion
  validity phải so với giải pháp hiện có tốt nhất. Bản này bổ sung baseline Monolithic-Complete.
- **Đo ở đúng chỗ kiến trúc không thể thắng.** MT3 gốc đặt "độ chính xác dự báo" ở vị trí trung tâm,
  trong khi MAS-DSS và mô hình đơn lẻ dùng chung một mô hình LightGBM nên tất yếu tương đương. Bản này
  chuyển sự tương đương đó thành **điều kiện kiểm soát** được khai báo và kiểm chứng trước (giả thuyết
  H1).
- **Khái niệm trung tâm chưa được thao tác hóa.** "Hiệu quả hỗ trợ quyết định" trong MT3 gốc không có
  cách đo, và cũng không thể đo bằng dữ liệu Olist do thiếu biến treatment (ràng buộc C1). Bản này
  không tuyên bố về hiệu quả hỗ trợ quyết định trên tuyến chính; nếu điều kiện cho phép, khái niệm này
  được thao tác hóa bằng đánh giá chuyên gia theo thiết kế mù ở nhánh tùy chọn (§5.1).

---

#### **MT2 — Thiết kế kiến trúc và rút ra tri thức thiết kế** *(prescriptive)* → **RQ2**

**Phát biểu.** Đề xuất một kiến trúc tham chiếu MAS-DSS và rút ra tập Design Principles cho việc ra
quyết định truy vết được, trung thực về độ tin cậy, trong điều kiện tác tử có thể lỗi hoặc suy giảm
chất lượng.

**Các nhiệm vụ cụ thể:**

- **MT2.1 — Xây dựng ontology và giao thức giao tiếp giữa các tác tử** *(artifact A1)*
  - Sản phẩm: tập khái niệm chung gồm `Message` (message envelope), **mười** `Performative`, `Bid` kèm
    `Evidence`, `Critique`, `Decision`, và construct mới `DegradationLevel`.
  - Tiêu chí hoàn thành: mọi bất biến của ontology được **cưỡng chế lúc khởi tạo đối tượng** — sai
    ràng buộc thì chương trình dừng ngay tại chỗ tạo ra lỗi, không phải ở nơi hậu quả xuất hiện — và
    mỗi bất biến có ít nhất một kiểm thử canh giữ. Ba bất biến bắt buộc: `degradation_level` **không
    có giá trị mặc định**; suy giảm lớn hơn 0 kéo theo `needs_human_review`; từ hai nguyên nhân trở
    lên kéo theo `multi_cause`.

  > **Đính chính so với bản trước.** Tiêu chí cũ ghi *"đặc tả bằng Pydantic schema"*. Cài đặt thực tế
  > dùng **dataclass với `__post_init__`**, không dùng Pydantic — dự án cố ý giữ số phụ thuộc ngoài ở
  > mức tối thiểu để điều kiện tái lập không phụ thuộc vào phiên bản của một thư viện bên thứ ba.
  > Tiêu chí nay phát biểu theo **thuộc tính cần đạt** (cưỡng chế lúc khởi tạo, có test canh) thay vì
  > theo **công cụ cụ thể**. Một tiêu chí nghiệm thu nêu đích danh thư viện là tiêu chí đặt sai chỗ:
  > nó ràng buộc phương tiện trong khi điều cần bảo đảm là kết quả.

- **MT2.2 — Đặc tả kiến trúc tham chiếu và các cơ chế điều phối** *(artifact A2)*
  - Sản phẩm: kiến trúc năm lớp cùng bốn cơ chế điều phối — định tuyến động theo trạng thái case,
    Contract Net Protocol có ràng buộc ngân sách tính toán, blackboard dùng chung, và cây giám sát
    (supervision tree).
  - Tiêu chí hoàn thành: sơ đồ kiến trúc hoàn chỉnh; **một nguồn sự thật duy nhất về trạng thái** là
    blackboard của phiên, kiểm chứng được bằng việc decision trace dựng lại được trọn vẹn **chỉ từ
    nhật ký message**; và mọi cơ chế điều phối bật/tắt được **bằng tham số cấu hình**, không bằng
    nhánh mã nguồn — đó là điều kiện để các thí nghiệm ablation ở §4 chạy được.

  > **Đính chính so với bản trước.** Tiêu chí cũ đòi *"bảng phân định trách nhiệm giữa engine thực thi
  > (LangGraph) và phần cài đặt tự phát triển"*. Nghiên cứu **đã chốt không dùng LangGraph** — lý do
  > đầy đủ ở [technical-plan-v3.md §2.2](technical-plan-v3.md), tóm tắt: điều kiện tái lập từng byte
  > và quyền kiểm soát hoàn toàn đường tiêm lỗi của chaos harness (MT1.2) quan trọng hơn phần tiện lợi
  > mà một engine dựng sẵn mang lại, và bản thân bộ điều phối chỉ chiếm một phần nhỏ khối lượng.
  > Không còn hai bên để phân định, nên tiêu chí được thay bằng **thuộc tính mà bảng phân định đó vốn
  > nhằm bảo đảm**: một nguồn sự thật về trạng thái, và khả năng ablation bằng cấu hình.

- **MT2.3 — Rút ra và phát biểu bốn Design Principles**
  - Sản phẩm: bốn nguyên lý thiết kế trừu tượng, độc lập với miền ứng dụng, phát biểu theo cấu trúc
    *"Để [mục tiêu], hãy [cơ chế], bởi vì [lý thuyết biện minh]"* của Gregor, Chandra Kuk & Hevner
    (2020).
  - Tiêu chí hoàn thành: mỗi nguyên lý được gắn với một **cơ chế cưỡng chế trong mã nguồn** và một
    **thí nghiệm ablation** tương ứng, bảo đảm nguyên lý được kiểm chứng chứ không chỉ được phát biểu
    (chi tiết tại §4).

**So với đề cương gốc.** Nội dung kiến trúc được giữ nguyên; mục tiêu được **mở rộng** theo hai hướng:
(i) bổ sung Design Principles như tri thức trừu tượng có khả năng chuyển giao, và (ii) đưa điều kiện
lỗi/suy giảm vào chính phát biểu mục tiêu.

---

#### **MT3 — Hiện thực hóa prototype cùng điều kiện tiên quyết cho so sánh không thiên lệch** → **RQ3**

**Phát biểu.** Hiện thực hóa kiến trúc đề xuất thành một prototype vận hành được trên bộ dữ liệu Olist,
kèm theo bộ nhãn chuẩn do người gán (gold set) nhằm bảo đảm việc đánh giá năng lực quy kết nguyên nhân
không rơi vào vòng tròn tự tham chiếu.

**Các nhiệm vụ cụ thể:**

- **MT3.1 — Xây dựng prototype MAS-DSS vận hành end-to-end** *(artifact A5)*
  - Sản phẩm: hệ thống xử lý trọn vẹn một case từ tiếp nhận đơn hàng đến quyết định hành động, bao gồm
    cơ chế Contract Net có ngân sách tính toán và quyền từ chối (`REFUSE`) của tác tử.
  - Tiêu chí hoàn thành: decision trace của mỗi case **dựng lại được hoàn toàn từ nhật ký message**,
    không phụ thuộc vào bất kỳ tham số nào nằm ngoài nhật ký đó.

- **MT3.2 — Xây dựng bộ nhãn chuẩn do người gán** *(artifact A3 — đường tới hạn của nghiên cứu)*
  - Sản phẩm: 300–400 đơn hàng bất mãn được lấy mẫu phân tầng theo ba chiều (có/không bình luận × nhóm
    hàng × mức trễ giao), gán nhãn độc lập bởi hai người theo codebook thống nhất, **cho phép đa nhãn**.
  - **Lấy mẫu không cân xứng giữa hai tầng.** Tầng B chỉ chiếm 25,23% tổng thể (§0.1); nếu lấy mẫu theo
    đúng tỷ lệ thì 400 đơn chỉ cho khoảng 98 mẫu tầng B — quá mỏng để kết luận về tình huống khó (b) của
    RQ3. Phân bổ đề xuất: **250 đơn tầng A và 150 đơn tầng B**, kèm hiệu chỉnh trọng số khi báo cáo chỉ
    số trên toàn bộ tổng thể.
  - Tiêu chí hoàn thành: báo cáo hệ số đồng thuận Cohen's κ; bộ nhãn được chia đôi, một nửa dùng để
    định lượng độ nhiễu của weak label như một threat được đo đạc, nửa còn lại làm tập kiểm thử độc lập.
  - Phương án dự phòng: nếu nguồn lực chỉ đủ cho 200 đơn, quy mô được hạ xuống và báo cáo trung thực —
    200 đơn có κ chấp nhận được vẫn có giá trị hơn 400 đơn không đo được độ đồng thuận.

- **MT3.3 — Xây dựng tầng xử lý văn bản tiếng Bồ Đào Nha theo bằng chứng**
  - Sản phẩm: classifier head đa nhãn vận hành ở **giai đoạn T₄** theo kiến trúc hai tầng — tầng A
    (74,77%) cho đơn hàng có bình luận, tầng B (25,23%) cho đơn hàng không có bằng chứng văn bản, nơi
    Quality Analyst và Service Analyst phát `REFUSE`.
  - **Encoder đang dùng là TF-IDF, không phải BERTimbau.** T3.3 bị chặn bởi quyết định không cài
    `torch`; `TfidfCauseHead` đạt macro-F1 0,4730 so với 0,2196 của bản lexicon trên 250 dòng gold, đủ
    để dựng và đo toàn bộ đường ống. Hệ quả phải nêu ở Threats to Validity: chi phí đo được của analyst
    văn bản là 1,3 ms thay vì ~45 ms, nên **ràng buộc ngân sách của Contract Net yếu hơn thiết kế**.
  - Tiêu chí hoàn thành: head được huấn luyện và đánh giá trên gold set; weak label chỉ được dùng ở
    bước pre-train. Nguyên tắc này được **cưỡng chế bằng mã nguồn**: hàm đánh giá quy kết nguyên nhân
    chỉ chấp nhận gold set, mọi lời gọi truyền weak label vào đều phát sinh lỗi.

- **MT3.4 — Chuẩn hóa hai mốc quyết định và tập hành động**
  - Sản phẩm: mốc quyết định được khai báo dưới dạng **tham số cấu hình**
    `FeatureSet(decision_point=...)` với miền giá trị `{T₂, T₃, T₄}`; mỗi đặc trưng mang thuộc tính
    `available_at` và bị lọc theo mốc; đặc trưng `review_lag_days` bị loại bỏ do rò rỉ nhãn; tập hành
    động là các hành động phục hồi dịch vụ khả thi trong cửa sổ tương ứng.
  - Tiêu chí hoàn thành: chuyển đổi giữa các mốc chỉ thông qua thay đổi cấu hình, không phân nhánh mã
    nguồn. Hai ràng buộc được kiểm tra tự động: không đặc trưng nào của mốc muộn lọt vào mốc sớm, và
    **`has_comment` cùng mọi đặc trưng dẫn xuất từ văn bản bị chặn ở T₃** (ràng buộc C4).

**So với đề cương gốc.** Phạm vi prototype được giữ nguyên; mục tiêu được bổ sung **một điều kiện tiên
quyết**: nếu không có gold set (A3), mô-đun phân loại nguyên nhân không thể được đánh giá một cách hợp
lệ, do nhãn nguyên nhân hiện có là nhãn do chính nghiên cứu sinh ra (ràng buộc C2).

---

## Phần 2 — Câu hỏi nghiên cứu

Ba câu hỏi, **sắp xếp theo trọng số đóng góp**, ánh xạ vào khung **Validity in Design Science
(Larsen et al., 2025)** đã trích ở Chương 2.

> **Vì sao RQ chịu lỗi đứng đầu.** Nó là câu hỏi **duy nhất** mà văn liệu MAS-DSS còn bỏ trống, là câu
> **khả thi nhất** *(sự thật nền là chính chỗ đã tiêm lỗi — không cần gán nhãn, không cần người tham
> gia)*, và là câu **đã có số đo**. Hai câu còn lại đổi vai trò: RQ2 **giải thích vì sao** RQ1 cho kết
> quả đó; RQ3 là **điều kiện kiểm soát** loại bỏ lời giải thích thay thế.

### 2.1 RQ1 — Câu hỏi chịu lỗi *(causal validity)* ← MT1 — **trục chính của luận văn**

> **Khi một hoặc nhiều thành phần lỗi (crash) hoặc suy giảm chất lượng mà không lỗi (drift phân phối,
> bid lệch hệ thống), kiến trúc MAS-DSS và kiến trúc đơn khối khác nhau thế nào về: (a) tỷ lệ hệ thống
> cho ra quyết định sai mà không cảnh báo (*silent failure*) — đo trên **toàn bộ bề mặt hỏng** và ở
> **cả hai mốc quyết định**, (b) độ nhạy và độ trễ phát hiện của bộ giám sát, (c) mức suy giảm chất
> lượng quyết định, và (d) **bề mặt hỏng tăng thêm và chi phí tính toán** phải trả cho khả năng đó?**

*Hai mệnh đề phạm vi ở vế (a) là có chủ đích và chúng làm câu hỏi **khó trả lời hơn**.*

*__Toàn bộ bề mặt hỏng__ — MAS-DSS có **năm thành phần** mà kiến trúc đơn khối không có: `analytics` ·
`arbiter` · `case_manager` · `critic` · `recommendation`. Đo hỏng âm thầm chỉ trên thành phần **dùng
chung** sẽ bỏ sót đúng phần rủi ro **do chính kiến trúc tạo ra**.*

*__Cả hai mốc__ — tại **T₃** đầu ra là **hành động** *(gọi khách, thúc người bán)*, nên hỏng âm thầm ở
đó làm **bỏ sót ca cần can thiệp**; tại **T₄** đầu ra là **báo cáo**, nên hỏng âm thầm dẫn tới **quy
kết sai**. Hai loại thiệt hại khác nhau, phải đo riêng.*

- **Vì sao đáng giá nhất trong ba câu.** Câu hỏi này phụ trách **đóng góp mới** của luận văn, và không
  có tiền thân trong đề cương gốc. Văn liệu MAS-DSS hiện tại hầu như chỉ báo cáo độ chính xác và bỏ
  trống khía cạnh chịu lỗi; đây là một khoảng trống thật, đủ hẹp để một luận văn thạc sĩ lấp được.
- **Vì sao khả thi nhất trong ba câu.** Toàn bộ chi phí là mã nguồn và kịch bản thí nghiệm — không cần
  gán nhãn, không cần người tham gia, không phụ thuộc nguồn lực bên ngoài. Baseline Monolithic-Complete
  tái sử dụng chính mô hình và tập luật đã có.
- **Vế (d) là điều kiện để câu hỏi giữ được tính trung thực.** Khả năng chịu lỗi không miễn phí. Việc
  đo và công bố chi phí (độ trễ, độ phức tạp, quy mô mã nguồn) làm cho kết luận ở ba vế còn lại đáng
  tin hơn nhiều so với một báo cáo chỉ nêu ưu điểm.
- **Ranh giới giữa kết quả thực nghiệm và kiểm tra đặc tả** — phải trình bày rõ trong Chương 5:

  | Nội dung đo | Bản chất |
  |---|---|
  | Đường cong độ nhạy/độ đặc hiệu của bộ giám sát trên các nhiễu loạn không được thiết kế riêng cho nó | ✅ Kết quả thực nghiệm — không biết trước |
  | Độ trễ phát hiện: số case xử lý trước khi bộ giám sát phát cảnh báo | ✅ Kết quả thực nghiệm — không biết trước |
  | Tỷ lệ báo động giả khi hệ thống vận hành bình thường | ✅ Kết quả thực nghiệm — không biết trước |
  | Tỷ lệ hỏng âm thầm của Monolithic-Complete | ✅ Kết quả thực nghiệm — baseline không bị dàn dựng để hỏng |
  | Chi phí của bảo đảm: overhead độ trễ, số thành phần, số dòng mã | ✅ Kết quả thực nghiệm |
  | Tỷ lệ hỏng âm thầm của MAS-DSS | ❌ Kiểm tra đặc tả — vẫn báo cáo, nhưng **không** dùng làm luận cứ chính |

- **Artifact tương ứng.** A4 (chaos harness), A5 (prototype), A6 (baseline).

---

### 2.2 RQ2 — Câu hỏi thiết kế *(design / prescriptive)* ← MT2

> **Một kiến trúc hệ thống thông tin đa tác tử cần được thiết kế như thế nào để chuỗi ra quyết định
> phát hiện → quy kết nguyên nhân → đề xuất hành động vẫn tạo ra quyết định *truy vết được* và *trung
> thực về mức độ tin cậy*, kể cả khi một hoặc nhiều tác tử lỗi hoặc suy giảm chất lượng?**

- **Vì sao đáng giá.** Câu hỏi này mang **đóng góp lý thuyết** của luận văn: bốn Design Principles là
  tri thức trừu tượng, độc lập với miền ứng dụng, và là cầu nối hợp lệ duy nhất sang các bài toán quản
  trị khác. Nếu thiếu tầng câu hỏi prescriptive này, luận văn dừng lại ở mức mô tả một hệ thống đã xây,
  không đạt chuẩn Design Science theo Gregor & Hevner (2013).
- **Vì sao khả thi.** Chi phí gia tăng gần bằng không: sản phẩm là kiến trúc và phần viết, dựa trên
  chính prototype đã phải xây để phục vụ hai câu hỏi còn lại. Không phụ thuộc nguồn lực bên ngoài.
- **Cải thiện so với RQ1 gốc.** Không hỏi "phù hợp thế nào" — một tiêu chí không đo được — mà hỏi hai
  thuộc tính cụ thể, quan sát được. Đồng thời loại bỏ tuyên bố "dữ liệu biến động nhanh / xử lý thời
  gian thực", vốn không kiểm chứng được với một hệ thống chạy theo lô ngoại tuyến.
- **Thao tác hóa.**

  | Thuộc tính | Cách đo |
  |---|---|
  | *Truy vết được* | Tỷ lệ decision trace tái lập được hoàn toàn từ nhật ký message; độ phân kỳ giữa trace dựng từ nhật ký và trace viết tay |
  | *Trung thực về độ tin cậy* | `degradation_level` là trường bắt buộc của mọi `Decision`; tỷ lệ quyết định tự động được sinh khi `degradation_level > 0` phải bằng **0**, cưỡng chế bằng mã nguồn chứ không bằng quy ước |

- **Loại bằng chứng.** Demonstration — chứng minh bằng một hiện thực vận hành được, không phải bằng
  kiểm định thống kê.
- **Artifact tương ứng.** A1 (ontology), A2 (kiến trúc + 4 DP), A5 (prototype).

---

### 2.3 RQ3 — Câu hỏi điều kiện kiểm soát *(criterion validity)* ← MT3

> **Kiến trúc đa tác tử có đạt được các thuộc tính vận hành ở RQ1 và RQ2 MÀ KHÔNG ĐÁNH ĐỔI ĐỘ CHÍNH
> XÁC hay không — cả ở dự báo rủi ro tại T₃ lẫn quy kết nguyên nhân tại T₄ — khi nó và các kiến trúc
> đối chứng vận hành trên cùng một năng lực nền?**

> **Câu hỏi này đã đổi động từ, và lý do phải nêu rõ.** Bản trước hỏi cơ chế đấu thầu có cho kết quả
> **tốt hơn** bộ phân loại đơn khối hay không. Câu trả lời là **không**: hai kiến trúc cho kết quả
> **giống hệt nhau trên 250/250 đơn** — một đẳng thức **đại số**, không phải một kết quả thống kê.
>
> Phát biểu gốc được **giữ nguyên văn** tại §3.1 kèm phán quyết bác bỏ. Phát biểu mới **yếu hơn** phát
> biểu cũ chứ không mạnh hơn: nó chuyển từ một tuyên bố **có lợi cho artifact** sang một **điều kiện
> kiểm soát**. Sửa theo hướng bất lợi cho mình là hướng duy nhất được phép sửa sau khi thấy kết quả.
>
> **Vai trò của câu hỏi này trong luận văn:** nếu MAS-DSS vừa chính xác hơn vừa chịu lỗi tốt hơn, phản
> biện *"có phải chỉ vì mô hình nền tốt hơn không?"* sẽ **không bác được**. Chứng minh tương đương về
> độ chính xác khiến mọi khác biệt ở RQ1 và RQ2 **chỉ quy được cho cách tổ chức**.

*Phạm vi thời điểm: câu hỏi này thuộc **giai đoạn 2 — mốc T₄** (§0.2), nơi đánh giá của khách hàng đã
về và bằng chứng văn bản khả dụng với 74,77% đơn bất mãn.*

- **Vì sao đáng giá.** Đây là câu hỏi **duy nhất kiểm chứng chính cơ chế đa tác tử**. Nếu không có nó,
  Contract Net và quyền từ chối chỉ được mô tả chứ không được chứng minh là mang lại giá trị, và phản
  biện *"đây thực chất chỉ là một ensemble được gắn nhãn giao thức"* không có gì để bác bỏ. Câu hỏi
  cũng là nơi duy nhất phá được vòng tròn tự tham chiếu của bản đề cương gốc.
- **Vì sao khả thi.** Chi phí tập trung ở gold set — hạng mục nằm trong tầm kiểm soát của nghiên cứu
  sinh, có phương án dự phòng quy mô (200 đơn), và có thể khởi động song song với việc lập trình ngay
  từ tuần đầu.
- **Cải thiện so với RQ2 gốc.** Ba điểm: (i) đo trên gold set do người gán, thoát khỏi vòng tròn
  *sinh nhãn → huấn luyện → đánh giá bằng chính nhãn đã sinh*; (ii) ở dạng so sánh thay vì mô tả "phối
  hợp ra sao", nên **có thể cho kết quả phủ định**; (iii) nêu đích danh hai tình huống mà cơ chế cạnh
  tranh về mặt lý thuyết phải tỏ ra vượt trội, qua đó biến câu hỏi thành một phép thử có rủi ro thực sự.
- **Điều kiện kiểm soát được khai báo trước.** Mệnh đề *"vận hành trên cùng một năng lực dự báo nền"*
  là một phần của câu hỏi, không phải chú thích: MAS-DSS và bộ phân loại đơn khối dùng chung mô hình dự
  báo và chung BERTimbau head, do đó mọi khác biệt quan sát được về quy kết nguyên nhân không thể quy
  cho năng lực dự báo. Sự tương đương này được kiểm chứng bằng kiểm định tương đương (H1).
- **Thao tác hóa.** Macro-F1 đa nhãn trên gold set là chỉ số chính, cắt lớp theo nhóm đa nguyên nhân và
  theo tầng A/B; kèm theo ECE và Brier score của từng analyst trước và sau hiệu chuẩn, tỷ lệ `REFUSE`
  và tỷ lệ `cause = unknown` theo từng tầng.
- **Bổ sung bắt buộc: chỉ số selective prediction cho tầng B.** Macro-F1 thuần túy **phạt việc từ chối
  trả lời**: nếu MAS-DSS phát `REFUSE` trên phần lớn tầng B thì recall của nó ở tầng đó tiến về 0 và nó
  **thua theo cấu tạo**, trong khi từ chối mới là hành vi đúng về mặt tri thức luận. Do đó ở tầng B,
  phép so sánh phải báo cáo đồng thời *độ chính xác trên phần đã trả lời* và *độ phủ*, dựng đường cong
  risk–coverage, và đối chiếu hai hệ **ở cùng mức độ phủ**. Nếu không có điều chỉnh này, DP3 tự trừ
  điểm chính nó.
- **Yêu cầu công bằng đối với đối chứng.** Bộ phân loại đơn khối phải là **bộ phân loại đa nhãn** (bốn
  đầu ra sigmoid, cùng ngưỡng τ, cùng capability nền), không phải bộ phân loại đơn nhãn dùng `argmax`.
  Nếu đối chứng bị chặn không cho trả về nhiều nhãn thì cơ chế đa tác tử thắng ở tình huống (a) **theo
  cấu tạo** — đúng lỗi baseline bù nhìn mà nghiên cứu đã cam kết tránh. Phép so sánh phải cô lập được
  *cách tổ chức*, không phải *hình dạng đầu ra*.
- **Có thể sai như thế nào.** Nếu cơ chế đấu thầu không vượt được bộ phân loại đơn khối ở hai tình
  huống khó, đó là một phát hiện trung thực và đáng công bố, không phải một thất bại của nghiên cứu.
- **Cảnh báo về điều kiện tiên quyết.** Contract Net **không tự giải quyết được** vấn đề vòng tròn: nếu
  vẫn chấm điểm theo weak label thì vòng tròn chỉ mở rộng chứ không biến mất. Gold set là điều kiện
  tiên quyết, không phải một hạng mục bổ sung.
- **Artifact tương ứng.** A3 (gold set), A5 (prototype), A6 (bộ khung đánh giá và baseline).

---

### 2.4 Số phận của hai câu hỏi bị loại khỏi tuyến chính

Bản năm câu hỏi tại [research-design-v2.md](research-design-v2.md) được thu gọn theo tiêu chí *giá trị
đóng góp × tính khả thi*. Không nội dung nào bị vứt bỏ; tất cả đều được chuyển về một vị trí xác định.

| Câu hỏi bản 5 câu | Đánh giá | Số phận trong bản 3 câu |
|---|---|---|
| **RQ3 cũ** — giá trị của khuyến nghị theo đánh giá chuyên gia, tính giải thích được, độ trễ | Giá trị trung bình–cao, nhưng **phụ thuộc vào việc tuyển được 3–5 chuyên gia** — nguồn lực nằm ngoài tầm kiểm soát, và là rủi ro được xếp mức "Cao" | **Tách làm ba phần:** (i) vế *tính giải thích được* → thao tác hóa thành chỉ số tái lập trace trong **RQ2**; (ii) vế *độ trễ* → trở thành vế (d) của **RQ1** mới; (iii) vế *đánh giá chuyên gia* → **nhánh tùy chọn** (§5.1), chỉ thực hiện nếu tuyển được người đánh giá |
| **RQ5 cũ** — bối cảnh: (a) lùi thời điểm quyết định về T₂, (b) đơn không có bình luận | Chi phí gần bằng không, nhưng **giá trị đóng góp thấp nhất**; vế (b) vốn đã trùng với tình huống khó thứ hai của RQ3 | **Hấp thụ hoàn toàn:** (a) → **phân tích độ nhạy** báo cáo trong Chương 5, không nâng lên thành câu hỏi nghiên cứu; (b) → đã nằm sẵn trong **RQ3**, tình huống (b) |
| Lập luận chuyển giao sang CRM / chuỗi cung ứng | Không có dữ liệu để kiểm chứng | Giữ nguyên vị trí cũ: **lập luận phân tích ở Chương 5** dựa trên bốn Design Principles, kèm tuyên bố rõ đây là suy luận thiết kế chưa được kiểm chứng thực nghiệm |

**Hệ quả cần chấp nhận và nói rõ trong Chương 1.** Khi rút xuống ba câu hỏi, nghiên cứu **không còn
tuyên bố** về hiệu quả hỗ trợ quyết định so với MIS và mô hình đơn lẻ, vì nguồn bằng chứng không tự
tham chiếu duy nhất cho tuyên bố đó là đánh giá chuyên gia, nay đã chuyển sang nhánh tùy chọn. So sánh
với bốn phương án thay thế vẫn được trình bày, nhưng ở mức **mô tả sự khác biệt về chức năng và về hành
vi khi lỗi**, không phải ở mức khẳng định ưu thế về giá trị quản trị.

---

### 2.5 Bảng ánh xạ RQ ↔ khung Validity (Larsen et al., 2025)

| RQ | Mục tiêu | Loại claim | Loại validity | Bằng chứng |
|---|---|---|---|---|
| **RQ1** | MT1 | **Causal** | **Causal validity** | Ablation + tiêm lỗi có kiểm soát *(chaos harness)*, trên **toàn bộ bề mặt hỏng** và ở **cả hai mốc** |
| **RQ2** | MT2 | Design *(tầng mới — đề cương gốc không có)* | — (demonstration) | Prototype vận hành được + 4 Design Principles, mỗi DP có cơ chế cưỡng chế và ablation |
| **RQ3** | MT3 | Criterion | Criterion efficacy | Gold set do người gán; **điều kiện kiểm soát** — đếm số đơn hai kiến trúc cho kết quả khác nhau |

Đề cương gốc chỉ có ba loại claim (criterion, causal, context). Bản này **bổ sung tầng
design/prescriptive** cho RQ2 — thứ nâng luận văn từ mức "mô tả một hệ thống đã xây" lên Design Science
đúng nghĩa theo Gregor & Hevner (2013) — và **lược bỏ tầng context** khỏi tuyến chính.

**Tầng causal nay đứng đầu.** Đó là thay đổi lớn nhất so với các bản trước: claim mạnh nhất mà nghiên
cứu này chứng minh được là một claim **nhân quả** về hành vi kiến trúc dưới điều kiện lỗi, không phải
một claim **criterion** về độ chính xác. Tầng criterion xuống vai trò **điều kiện kiểm soát** — nó tồn
tại để loại bỏ lời giải thích thay thế cho claim nhân quả, chứ không mang đóng góp độc lập.

---

## Phần 3 — Giả thuyết

Đề cương gốc **không khai báo giả thuyết nào**. **Ba** giả thuyết dưới đây được khai báo *trước khi
chạy thí nghiệm*.

### Quy tắc phân loại mệnh đề

Bản này tách rõ **ba loại mệnh đề** vốn bị trộn lẫn ở các bản trước. Phân biệt này quyết định mệnh đề
nào được phép sửa và mệnh đề nào không.

| Loại | Kiểm chứng bằng | Đặt ở đâu | Sửa sau khi thấy kết quả? |
|---|---|---|---|
| **Ràng buộc (C)** | **đọc lược đồ dữ liệu** — không cần thí nghiệm | §0 | **được** — nó là sự thật về dữ liệu, không phải dự đoán |
| **Giả thuyết (H)** | thí nghiệm · **có bất định thật** · **có mốc phán quyết rõ** | §3 | ❌ **không** — sửa là HARKing |
| **Phát hiện (F)** | nảy sinh **từ** phân tích | Chương 5 | — ghi rõ là **hậu nghiệm** |

**Ba mệnh đề của các bản trước đã bị chuyển khỏi bảng giả thuyết** vì không thỏa định nghĩa:

| Mệnh đề cũ | Chuyển thành | Vì sao |
|---|---|---|
| *"`quality`/`service` không quy kết được từ đặc trưng bảng"* | **ràng buộc C5** | Kiểm chứng bằng đọc lược đồ 9 tệp thô — **không có bất định** để kiểm định |
| *"cái giá nằm trong ngưỡng chấp nhận được"* | **báo cáo mô tả** dưới RQ1(d) | *"Ngưỡng chấp nhận được"* **chưa từng được đặc tả** — mắc đúng lỗi **L29**. **77 giây** có đáng chấp nhận không? So với **30 giây**? Không có mốc để phán quyết. Đặt ngưỡng bây giờ cũng không cứu được: nó sẽ là chọn **sau khi** đã biết kết quả |
| *"xếp hạng theo năng lực hơn ngưỡng cố định"* | **phát hiện**, Chương 5 | Nảy sinh **khi đo** precision@k. Khai báo bây giờ như giả thuyết là HARKing |

### Ba giả thuyết

| # | Giả thuyết | Thuộc RQ | Kỳ vọng | Phương pháp kiểm chứng |
|---|---|---|---|---|
| **H1** | MAS-DSS và các kiến trúc đối chứng vận hành trên **cùng năng lực nền** nên **tương đương về độ chính xác ở cả hai mốc** — dự báo tại T₃ và quy kết tại T₄ | RQ3 *(điều kiện kiểm soát)* | **Tương đương — và đó là kết quả mong muốn** | **Kiểm định tương đương** *(không phải t-test)* cho dự báo · đếm **số đơn cho kết quả khác nhau** cho quy kết · **PHÁN QUYẾT: ✅ TƯƠNG ĐƯƠNG ở cả hai mốc — xem §3.3** |
| **H2** *(bản sửa 14/08)* | Dưới tiêm lỗi có kiểm soát, MAS-DSS đạt **tỷ lệ hỏng âm thầm thấp hơn đáng kể** so với kiến trúc đơn khối **trên bề mặt thành phần dùng chung**, ở **cả hai mốc quyết định** | RQ1 *(vế a)* | **Có** — và là kết quả thực nghiệm thật, do đối chứng không bị dàn dựng để hỏng | Chaos harness, **cùng** kịch bản lỗi trên hai kiến trúc, chạy ở **cả giai đoạn 1 và 2** |
| **H3** | Bộ giám sát phát hiện được drift phân phối **trước khi** chất lượng quyết định suy giảm quá ngưỡng | RQ1 *(vế b)* | **Chưa biết** — kết quả thực nghiệm thật | Đường cong độ nhạy và độ trễ phát hiện · **PHÁN QUYẾT: ❌ BÁC BỎ** |

### 🔴 H2 đã được sửa ngày 14/08 — hồ sơ sửa đổi

> **Đây là một ngoại lệ với chính quy tắc ba tầng ở bảng trên**, và nó được ghi lại đầy đủ thay vì
> được thực hiện lặng lẽ. Bảng đó xếp giả thuyết vào loại **không được phép sửa**; việc sửa H2 sau khi
> đã chạy thí nghiệm vì vậy là một quyết định có rủi ro phương pháp, không phải một thao tác trung tính.

**Phát biểu gốc, giữ nguyên văn:**

> *Dưới tiêm lỗi có kiểm soát, MAS-DSS đạt tỷ lệ hỏng âm thầm thấp hơn đáng kể so với kiến trúc đơn
> khối — **trên toàn bộ bề mặt hỏng của nó**, ở cả hai mốc quyết định, kể cả **năm thành phần** mà
> kiến trúc đơn khối không có.*

**Phần bị gỡ:** mệnh đề phạm vi *"trên toàn bộ bề mặt hỏng"* và vế *"năm thành phần riêng có"*.

**Căn cứ — một sự thật về artifact, không phải một kết quả đo:** tầng `system/reliability/` chỉ đăng ký
guard cho **bề mặt thành phần dùng chung**; nó chưa bao giờ được thiết kế để phủ bốn thành phần riêng
có *(`analytics`, `recommendation`, `critic`, `arbiter`)*. Điều này kiểm chứng được bằng cách đọc mã
nguồn, và trường `monitoring_coverage` trong `reliability_report.json` cũng ghi lại độ phủ giám sát
chưa đầy đủ. Mở rộng cơ chế bảo vệ sang nhóm đó là **một hạng mục thiết kế mới**, và nó được đặt
**ngoài phạm vi** của luận văn *(Chương 1, mục Phạm vi)*.

**Điều người đọc phải được biết, và không được giấu:** phát biểu gốc **đã từng được đo** trước khi
phạm vi thu hẹp, và nó **thất bại** ở nhóm thành phần riêng có. Artifact tương ứng được chuyển sang
`data/v3/_ngoai_pham_vi/chaos_masonly/` kèm lý do, thay vì bị xoá. Vì vậy tuyên bố về khả năng chịu
lỗi trong luận văn **chỉ áp cho bề mặt dùng chung**, và mọi cách diễn đạt rộng hơn đều vượt quá bằng
chứng.

**Cái giá phải chấp nhận:** bản sửa **dễ thỏa mãn hơn** bản gốc. Nó không còn là một phép thử có rủi ro
ngang mức đã khai báo ban đầu, và Chương 5 phải nói đúng như vậy thay vì trình bày H2 như một giả
thuyết khắt khe đã vượt qua.

### Vì sao gộp bốn mệnh đề cũ thành H2

Các bản trước tách thành bốn mệnh đề riêng: *đơn khối hỏng âm thầm nhiều hơn* · *hỏng âm thầm ở T₃ làm
bỏ sót ca cần cứu* · *năm thành phần riêng có cũng được guard phủ* · … Cả bốn chứng minh **cùng một
luận điểm**: *MAS-DSS chịu lỗi tốt hơn*. Tách ra là **đếm một bằng chứng nhiều lần**, và làm bộ giả
thuyết trông đông hơn thực chất. Việc gộp vẫn đứng vững sau bản sửa.

Mệnh đề phạm vi còn lại — *"ở cả hai mốc"* — vẫn được giữ, và nó vẫn ràng buộc thật: chỉ cần T₃ cho
kết quả khác T₄ là H2 thất bại.

### Bộ giả thuyết còn mang bao nhiêu rủi ro sau bản sửa

**H1 kỳ vọng KHÔNG có ưu thế** — bản chất của một điều kiện kiểm soát; nếu nó thất bại thì mọi so sánh
khác trong luận văn mất hiệu lực. **H3 đã bị bác bỏ.** **H2 sau khi thu hẹp phạm vi thì dễ thỏa mãn
hơn hẳn** — và đó là điều phải nói ra, không phải điều để im lặng.

Vì vậy phát biểu trung thực về bộ giả thuyết nay là: **một giả thuyết đã bị bác bỏ *(H3)*, một là kiểm
tra đặc tả không thể sai theo cấu tạo *(H1)*, và một đã bị thu hẹp phạm vi sau khi thấy kết quả
*(H2)*.** Bộ này mang ít rủi ro hơn bộ đã khai báo ban đầu.

*(Giả thuyết về đánh giá của chuyên gia chuyển sang nhánh tùy chọn tại §5.1.)*

---

### 3.2 Phán quyết H2 *(12/08/2026)* — **bác bỏ một phần**

H2 được phát biểu với **hai mệnh đề phạm vi** — *"trên toàn bộ bề mặt hỏng"* và *"ở cả hai mốc"* —
chính vì chúng làm nó **khó thỏa mãn hơn**. Cả hai nay đã đo được, và một trong hai **thất bại**.

#### Kết quả theo từng ô của bề mặt hỏng

> ⚠️ **Bảng này đã được tính lại sau L37.** Bản trước tính đơn khối là *"hỏng âm thầm"* kể cả khi nó
> **có** điền `failed_steps` — nên con số *"16–38% dưới crash"* thực ra là **0,0%**. Sai lệch nghiêng
> về phía có lợi cho artifact của chính nghiên cứu.

| Mốc | Bề mặt | Nhóm lỗi | Có ném ngoại lệ? | MAS âm thầm | Đơn khối âm thầm | Phán quyết |
|---|---|---|---|---|---|---|
| T₃ | dùng chung | crash · hang | ✔ | **0,0%** | **0,0%** | ⚪ **không có khác biệt** |
| **T₃** | dùng chung | **byzantine** | ✘ | **0,0%** | **100,0%** | ✅ **khác biệt lớn nhất** |
| T₄ | dùng chung | crash · hang | ✔ | **0,0%** | **0,0%** | ⚪ **không có khác biệt** |
| **T₄** | dùng chung | **byzantine** | ✘ | **0,0%** | **90,5 – 100%** | ✅ |
| **T₄** | dùng chung | **bias** | ✘ | **0,0%** | **7,5 – 37,5%** | ✅ |
| T₄ | dùng chung | drift | ✘ | 1,5 – 6,5% | 2,5 – 9,0% | ⚠️ **cả hai gần như mù** |
| T₄ | **chỉ MAS** | crash · hang | ✔ | **0,0%** | — | ✅ |
| **T₄** | **chỉ MAS** | **byzantine** | ✘ | **11,0%** = **100% số ca bị ảnh hưởng** | — | ❌ **THẤT BẠI** |

**Điều bảng này nói, phát biểu bằng một câu.** Ưu thế chịu lỗi của MAS-DSS nằm **trọn vẹn** ở nhóm lỗi
**không ném ngoại lệ**. Một lỗi biết `raise` thì kiến trúc nào cũng bắt được — `try/except` là đủ. Lỗi
trả về **giá trị hợp lệ nhưng sai** mới cần thang suy giảm và output guard, và đó đúng là phần MAS-DSS
đóng góp. Đây là tuyên bố **hẹp hơn** bản trước nhưng **có cơ chế giải thích**, nên nó mạnh hơn.

#### Điều thất bại, phát biểu chính xác

Khi ba thành phần chỉ MAS-DSS mới có — `analytics` · `recommendation` · `critic` — trả về kết quả
**hợp lệ về lược đồ nhưng sai**, hệ thống đổi quyết định ở **11,0%** số ca và **không ca nào** trong
số đó được gắn `degradation_level > 0`, `needs_human_review`, hay bị guard chặn. Tỷ lệ hỏng âm thầm
trong nhóm bị ảnh hưởng là **100%**.

Nguy hiểm nhất là `critic.challenged = False`: bộ phản biện **im lặng chấp thuận mọi đề xuất**. Đầu
ra vẫn đúng lược đồ, vẫn có vẻ hợp lý, và không có tín hiệu nào cho biết lớp kiểm soát đã ngừng
kiểm soát.

#### Vì sao đây là kết quả **đáng công bố**, không phải một thất bại cần giấu

**Tuyên bố chịu lỗi phải thu hẹp lại**, và bản thu hẹp vẫn là một đóng góp thật:

> MAS-DSS loại bỏ hoàn toàn hỏng âm thầm **trên bề mặt hỏng dùng chung, ở cả hai mốc quyết định** —
> đúng phần bề mặt mà kiến trúc đơn khối cũng có, nơi phép so sánh có nghĩa. Trên **bề mặt hỏng do
> chính nó tạo thêm**, guard phủ được lỗi **dừng** *(crash, hang)* nhưng **không** phủ lỗi
> **Byzantine**.

Và nó xác nhận thẳng nhận định đã ghi ở §3 phần chi phí: **một phần khả năng chịu lỗi của MAS-DSS tồn
tại để quản lý chính rủi ro mà kiến trúc đó tạo ra** — nay có số đo cho biết phần quản lý ấy **chưa
đủ**. Đây là loại tri thức thiết kế mà một kết quả toàn dương không thể mang lại.

> **Ghi chú về HARKing.** H2 **không được sửa** sau kết quả này. Phát biểu giữ nguyên văn; chỉ có
> **phán quyết** được ghi thêm. Việc nới phạm vi H2 xuống *"chỉ thành phần dùng chung"* để nó thành
> ✅ chính là điều §3.1 cấm.

#### Việc phải làm tiếp, và nó thuộc loại nào

Mở guard sang bốn thành phần chỉ-MAS là **cải tiến thiết kế** *(sửa DP1 hoặc bổ sung một DP mới)*,
không phải sửa giả thuyết. Nếu làm và đo lại, kết quả mới phải báo cáo **cạnh** kết quả này, không
thay thế nó.

---

### 3.1 Hồ sơ giả thuyết các bản trước — **giữ nguyên văn** kèm phán quyết

> **Phát biểu của năm giả thuyết bản trước được giữ NGUYÊN VĂN, không sửa một chữ.**
>
> Viết lại một giả thuyết sau khi đã thấy kết quả là **HARKing** *(Hypothesizing After the Results are
> Known)*, và nó sẽ phá hỏng đúng thứ mà việc khai báo trước đã mua được: bằng chứng rằng nghiên cứu
> không đang chứng minh điều mình muốn tin.
>
> Phân biệt này khác với **DP2** ở §4: DP2 là *Design Principle* — tri thức quy phạm, tức **sản phẩm**
> của nghiên cứu — nên sửa nó theo bằng chứng là đúng quy trình Design Science. Giả thuyết là **dự
> đoán khai báo trước**; chúng chỉ được phán quyết, không được viết lại.

#### Ánh xạ sang bộ ba giả thuyết hiện hành

| Bản trước — **nguyên văn** | Phán quyết | Bằng chứng | Nay thuộc |
|---|---|---|---|
| **H1** *"MAS-DSS **không** khác biệt có ý nghĩa so với mô hình học máy đơn lẻ về accuracy / PR-AUC"* | ✅ **Điều kiện kiểm soát đã kiểm chứng** | chênh lệch **0,000000** — giống nhau từng bit | **H1** hiện hành *(vế dự báo)* |
| **H2** *"Quy kết nguyên nhân bằng đấu thầu cạnh tranh **tốt hơn** bộ phân loại đơn khối trên gold set, đặc biệt ở nhóm đa nguyên nhân và nhóm không có bình luận"* | ❌ **BÁC BỎ** *(và một vế không kiểm định được)* | **0/250 đơn** khác nhau ở ngân sách đủ | **H1** hiện hành *(vế quy kết)* — đổi từ *"tốt hơn"* sang **tương đương** |
| **H3** *"Khi tiêm lỗi tác tử, kiến trúc đơn khối có **tỷ lệ hỏng âm thầm cao hơn đáng kể** so với MAS-DSS"* | 🟡 **ỦNG HỘ MỘT PHẦN** | đơn khối **16–100%**, MAS-DSS **0,0%** — nhưng **chỉ trên thành phần dùng chung, chỉ ở T₄** | **H2** hiện hành — mở rộng phạm vi |
| **H4** *"Bộ giám sát phát hiện được drift phân phối **trước khi** chất lượng quyết định suy giảm quá ngưỡng"* | ❌ **BÁC BỎ** *(ngưỡng chưa từng được đặc tả)* | **không phát hiện** drift ở cả ba mức | **H3** hiện hành — giữ nguyên |
| **H5** *"MAS-DSS chịu **overhead độ trễ cao hơn** kiến trúc đơn khối"* | ✅ **ỦNG HỘ** | **chậm hơn 12,5–17,9 lần** *(số cũ "+10,8%" đã rút — L46)* | **rút khỏi bảng giả thuyết** → báo cáo mô tả *(xem dưới)* |

#### Vì sao H5 bản trước bị rút khỏi bảng giả thuyết

Nó **đúng** nhưng **không có mốc phán quyết**. *"Overhead cao hơn"* thì cao hơn bao nhiêu mới đáng kể?
Và bản sau đó sửa thành *"nằm trong ngưỡng chấp nhận được"* lại mắc **đúng lỗi L29**: ngưỡng chưa từng
được đặc tả.

🔴 **Đính chính (L46).** Đoạn này trước đây lập luận rằng **+10,8%** *"nghe lớn"* nhưng chênh lệch
tuyệt đối chỉ là **1,016 ms mỗi case**, và vì vậy báo cáo dạng phần trăm làm sai lệch nhận thức về độ
lớn. **Con số nền của lập luận ấy sai, nên lập luận ấy phải rút lại.**

Hai vế khi đó được đo bằng **hai cơ sở khác nhau**: MAS lấy tổng thời lượng các span *(chỉ phần bên
trong các lời gọi năng lực, bỏ qua glue điều phối và toàn bộ phần ghi nhật ký)*, còn đơn khối lấy đồng
hồ treo tường của một vòng lặp **chạy cả ba baseline** cộng phần tuần tự hóa. Một vế bị hạ thấp, một vế
bị nâng cao, **cả hai đều có lợi cho MAS-DSS**.

Đo lại bằng đồng hồ treo tường cho cả hai vế, trên cùng tập case và trong cùng tiến trình: MAS-DSS
**115–130 ms/case**, đơn khối **6,8–9,2 ms/case** — chậm hơn **12,5 đến 17,9 lần**, tức **144 phút so
với 11,6 phút** cho lô 75.480 đơn. Hơn nửa chi phí ấy *(≈65,7 ms/case)* đến từ việc nhật ký ghi bền
vững **sau mỗi thông điệp**, một đánh đổi được giữ có chủ đích vì thí nghiệm crash cần nó.

Điều **vẫn đúng** sau đính chính: chi phí không được báo cáo ở dạng phần trăm, và mệnh đề về chi phí
nằm ngoài bộ giả thuyết vì không có mốc phán quyết được đặc tả trước. Điều **không còn đúng**: kết luận
rằng chênh lệch không có ý nghĩa vận hành.

Chi phí vì vậy chuyển thành **báo cáo mô tả** dưới RQ1(d), với **ba thước đo** và thước đo chính không
phải độ trễ:

| Thước đo | Giá trị | Vai trò |
|---|---|---|
| **Bề mặt hỏng tăng thêm** | **5 thành phần** chỉ có ở MAS: `analytics` · `arbiter` · `case_manager` · `critic` · `recommendation` | **chính** |
| Độ trễ tuyệt đối ở quy mô | **77 giây** mỗi lô 75.480 đơn | chính — **không** báo cáo dạng phần trăm |
| Quy mô mã nguồn | 1.094 dòng theo tầng | **mô tả**, không dùng làm luận cứ |

Người đọc tự phán quyết theo bối cảnh vận hành của họ. Đó là cách trung thực duy nhất khi không có
ngưỡng khai báo trước.

> **Một nhận định phải nói thẳng.** Bề mặt hỏng tăng thêm nghĩa là **một phần khả năng chịu lỗi của
> MAS-DSS tồn tại để quản lý chính rủi ro mà kiến trúc đó tạo ra**. **H2** hiện hành chính là phép thử
> cho điều đó: nếu năm thành phần riêng có **không** được guard phủ, tuyên bố chịu lỗi phải thu hẹp.

#### H1 *(bản trước)* — tautology, và phải trình bày đúng như vậy

Hai kiến trúc dùng **chung một đối tượng** `risk_model`, nên điểm dự báo giống nhau từng bit là điều
**tất yếu về cấu tạo**. Đây là **kiểm tra đặc tả đã vượt qua**, không phải bằng chứng thực nghiệm. Vai
trò thật của H1: nếu nó *thất bại*, mọi so sánh khác trong Chương 5 mất hiệu lực, vì khác biệt quan sát
được có thể quy cho năng lực dự báo thay vì kiến trúc.

#### H2 *(bản trước)* — bác bỏ ở vế kiểm định được, và **một vế chưa bao giờ kiểm định được**

Phát biểu gốc nêu **hai** nhóm khó: *"đặc biệt ở nhóm đa nguyên nhân **và nhóm không có bình luận**"*.

| Vế | Trạng thái | Lý do |
|---|---|---|
| Tổng thể + nhóm **đa nguyên nhân** | ❌ **Bác bỏ** | 0/250 đơn khác biệt ở ngân sách đủ; ở ngân sách hiệu chỉnh, 0,3776 so với 0,3804 — **nằm trong nhiễu** |
| Nhóm **không có bình luận** *(tầng B)* | ⚠️ **KHÔNG KIỂM ĐỊNH ĐƯỢC** | Sự thật nền ở tầng B là *"không quy kết được"* trên **149/150 dòng**; macro-F1 ở đó không xác định |

**Vế thứ hai là một lỗi thao tác hóa, không phải một kết quả.** Giả thuyết đòi so sánh độ chính xác
quy kết trên nhóm mà **cả hai người gán đều không quy kết được** — vì theo đúng định nghĩa, tầng B
không có bằng chứng văn bản. Không có sự thật nền thì không có phép so sánh nào. Điều này lẽ ra phải
phát hiện được **lúc khai báo giả thuyết**, không phải lúc đánh giá.

Cái **đo được** ở tầng B là một câu hỏi khác và hợp lệ: *"hệ nào biết im lặng"* — đo bằng **tỷ lệ quy
kết sai khi con người bỏ trống**. Chỉ số này đã cài trong `evaluation/selective.py` và cho MAS-DSS
**35,3%** so với Monolithic **41,2%**, và **100%** khi cấm phát `REFUSE` *(ablation DP3)*.

#### H4 *(bản trước)* — bác bỏ, và bác bỏ **vững** bất chấp một khiếm khuyết trong phát biểu

Phát biểu chứa cụm *"suy giảm quá **ngưỡng**"* nhưng **ngưỡng đó chưa bao giờ được đặc tả**. Về nguyên
tắc, một giả thuyết thiếu ngưỡng thì không kiểm định được.

**Ở đây nó vẫn kiểm định được, vì kết quả không phụ thuộc vào ngưỡng.** Bộ giám sát **không phát hiện
drift ở bất kỳ mức nào trong ba mức**, trong khi chất lượng quyết định suy giảm rõ rệt:

| Mức nhiễu loạn | Quyết định đổi so với lần chạy khỏe | Hỏng âm thầm MAS | Phát hiện? |
|---|---|---|---|
| drift 1 | 3,0% | 1,5% | ❌ |
| drift 2 | 6,5% | 3,5% | ❌ |
| drift 3 | **11,5%** | **6,5%** | ❌ |

Vì tỷ lệ phát hiện bằng **0 với mọi mức**, mệnh đề *"phát hiện **trước khi** suy giảm quá ngưỡng"* sai
với **mọi giá trị ngưỡng có thể đặt**. Bác bỏ vững, không cần biết ngưỡng là bao nhiêu.

**Phạm vi của phán quyết.** H4 nói về **drift phân phối**. Trên hai nhóm nhiễu loạn tinh vi còn lại, bộ
giám sát **có** phát hiện: `bias` sau **100 quan sát**, `byzantine` sau **20**. Nên kết luận đúng là
*"bộ giám sát bắt được lệch hệ thống và lỗi Byzantine, nhưng **mù với drift phân phối**"* — chứ không
phải *"bộ giám sát không hoạt động"*.

#### H3 và H5 *(bản trước)* — ủng hộ, với một ranh giới phải giữ

**H3.** Tỷ lệ hỏng âm thầm của Monolithic-Complete là **kết quả thực nghiệm thật** — baseline không bị
dàn dựng để hỏng, và nó dùng chung mọi năng lực nền. Tỷ lệ **0,0%** của MAS-DSS thì **không**: theo
bảng ranh giới ở §2.3, đó là **kiểm tra đặc tả**, vẫn báo cáo nhưng **không dùng làm luận cứ chính**.

**H5.** Kỳ vọng thua và đã thua đúng như khai báo — nhưng thua **nặng hơn nhiều** so với con số công bố
ban đầu: **114,6 so với 9,2 ms** mỗi case *(số cũ "+10,8%" đo sai cơ sở, xem L46)*, cùng **1.118 dòng
mã** tồn tại chỉ để chịu lỗi và phối hợp.

#### Hai khiếm khuyết thao tác hóa — và cách bản hiện hành xử lý

H2 và H4 đều mang một cụm **không kiểm định được như đã viết**: *"nhóm không có bình luận"* khi nhóm đó
không có sự thật nền, và *"quá ngưỡng"* khi ngưỡng chưa được đặt. Cả hai chỉ lộ ra **lúc đánh giá**,
tức muộn nhất có thể.

> **Biện pháp đã rút ra:** mỗi mệnh đề trong một giả thuyết phải trả lời được ba câu hỏi **trước khi
> khai báo** — *đo bằng chỉ số nào · sự thật nền ở đâu · ngưỡng là bao nhiêu*. Mệnh đề nào không trả
> lời đủ ba thì hoặc bỏ, hoặc tách thành một câu hỏi mô tả. Chi tiết ở
> [methodology-log.md §L29](methodology-log.md).

---

## Phần 4 — Bốn Design Principles (sản phẩm cốt lõi của MT2)

Bốn nguyên lý được phát biểu theo cấu trúc Gregor, Chandra Kuk & Hevner (2020): *Để* [mục tiêu], *hãy*
[cơ chế], *bởi vì* [lý thuyết biện minh]. Một nguyên lý không được kiểm chứng thì không phải là đóng
góp; do đó mỗi nguyên lý được gắn với một cơ chế cưỡng chế trong mã nguồn và một thí nghiệm ablation.

| DP | Phát biểu | Cơ chế cưỡng chế | Ablation | Chỉ số chứng minh | RQ |
|---|---|---|---|---|---|
| **DP1 — Suy giảm minh bạch** | *Để* hệ hỗ trợ quyết định giữ được lòng tin của nhà quản lý khi thành phần gặp lỗi, *hãy* gắn mức suy giảm vào từng quyết định và bắt buộc con người xem lại khi mức lớn hơn 0, *bởi vì* một quyết định tự động sinh ra trên nền năng lực đã suy giảm gây hại hơn là không có quyết định | `degradation_level` là trường bắt buộc của `Decision`; Rule Engine gắn `needs_human_review` khi giá trị lớn hơn 0 | Tắt output guard và degradation ladder, chạy lại chaos harness | Tỷ lệ hỏng âm thầm (MAS-DSS đối chiếu Monolithic-Complete); phân bố `degradation_level` | RQ1, RQ2 |
| **DP2 — Đa nhãn, và cạnh tranh chỉ khi thẩm quyền chồng lấn** *(sửa sau thực nghiệm)* | *Để* không đánh mất thông tin về các nguyên nhân đồng thời, *hãy* giữ đầu ra **đa nhãn** và cấm mọi phép chọn một nhãn; *và chỉ khi* các tác tử có **thẩm quyền chồng lấn** trên cùng một phần bằng chứng thì cơ chế đấu thầu cạnh tranh mới sinh thêm thông tin, *bởi vì* khi các tác tử **phân chia** không gian nhãn và dùng chung một năng lực nền cùng một ngưỡng, tập bid vượt ngưỡng **bằng đúng** đầu ra của một bộ phân loại đa nhãn | Đầu ra đa nhãn; cấm `argmax`/`idxmax` trong mã nguồn; Contract Net hai pha; `bid_entropy` | So với **Monolithic-Complete** đa nhãn dùng chung năng lực nền và chung ngưỡng | Macro-F1 trên gold set, cắt lớp nhóm đa nguyên nhân; **số đơn hai kiến trúc cho kết quả khác nhau** | RQ3 |
| **DP3 — Từ chối thay vì đoán** | *Để* tránh những quyết định tự tin nhưng sai trên dữ liệu ngoài phân phối hoặc thiếu bằng chứng, *hãy* cấp cho tác tử quyền phát `REFUSE`, *bởi vì* chi phí chuyển giao cho con người thấp hơn nhiều so với chi phí của một hành động sai | Performative `REFUSE`; bộ phát hiện ngoài phân phối; kiến trúc hai tầng A/B theo sự hiện diện của bình luận | Cấm phát `REFUSE`, buộc tác tử luôn trả lời | Tỷ lệ quy kết sai khi con người bỏ trống; tỷ lệ `cause = unknown` | RQ2, RQ3 |
| **DP4 — Nguồn gốc từ giao tiếp** | *Để* decision trace luôn trung thực với hành vi thực tế của hệ thống, *hãy* dựng trace từ nhật ký message thật thay vì viết tay, *bởi vì* một trace viết tay có thể phân kỳ với những gì hệ thống thực sự đã làm | Explanation Agent chỉ đọc nhật ký message, không nhận bất kỳ tham số nào từ bên ngoài | Dựng trace theo cách viết tay và đo độ phân kỳ so với trace dựng từ nhật ký | Tỷ lệ trace tái lập được từ nhật ký; **độ phân kỳ** giữa hai cách dựng | RQ2 |

Bốn nguyên lý này đồng thời là **cầu nối hợp lệ duy nhất** sang các bài toán quản trị khác (CRM, chuỗi
cung ứng), với điều kiện nêu rõ rằng đó là suy luận thiết kế chưa được kiểm chứng thực nghiệm.

### DP2 đã được sửa sau thực nghiệm — và vì sao bản sửa mạnh hơn bản gốc

**Bản gốc phát biểu:** *"hãy để nhiều tác tử chuyên biệt đấu thầu kèm bằng chứng **thay vì dùng một
bộ phân loại đa lớp**, bởi vì độ đồng thuận giữa các bid mang thông tin mà phép `argmax` làm mất"*.

**Thực nghiệm bác bỏ vế so sánh đó.** Trên 250 đơn gold, ở mức ngân sách đủ, MAS-DSS và
Monolithic-Complete cho kết quả **giống hệt nhau trên từng đơn — 0/250 đơn khác biệt**. Truy ngược
thì nó *phải* như vậy: bốn tác tử sở hữu bốn nguyên nhân **rời nhau**, dùng **chung** một cause head,
và arbiter nhận **mọi** bid vượt **cùng** một ngưỡng τ. Ghép lại, cơ chế đa tác tử **bằng đúng về mặt
đại số** với một bộ phân loại đa nhãn. Không dữ liệu nào tách được hai phép toán bằng nhau.

**Bản gốc sai ở đâu — và đúng ở đâu.** Nó gộp hai mệnh đề khác nhau vào một câu:

| Mệnh đề | Trạng thái |
|---|---|
| Phép chọn một nhãn (`argmax`) làm mất thông tin về nguyên nhân đồng thời | ✅ **Đúng, và vẫn giữ** |
| Đấu thầu cạnh tranh tốt hơn một bộ phân loại **đa nhãn** | ❌ **Bị bác bỏ** — bằng nhau theo cấu tạo |

Đối chứng công bằng của RQ2 là bộ phân loại **đa nhãn**, không phải đa lớp dùng `argmax`. Bản gốc lấy
đối chứng yếu hơn làm mốc so sánh, nên nó *có vẻ* đúng cho tới khi đối chứng được dựng cho đàng hoàng.

**Vì sao bản sửa là một đóng góp mạnh hơn.** Gregor & Hevner (2013) nhấn mạnh rằng một Design Principle
có giá trị chuyển giao khi nó nêu được **điều kiện biên áp dụng**. Bản gốc là một khẳng định không điều
kiện — và vì thế sai. Bản sửa nêu đúng điều kiện để cơ chế cạnh tranh sinh thêm thông tin: **các tác tử
phải tranh chấp cùng một phần bằng chứng, chứ không phân chia nó**. Đó là tri thức thiết kế dùng được
cho người khác, và nó chỉ rút ra được nhờ một kết quả phủ định.

**Cái mà kiến trúc đa tác tử thực sự mua được** không nằm ở độ chính xác quy kết mà ở ba chỗ khác, cả
ba đều đo được: **khả năng chịu lỗi** *(DP1 — hỏng âm thầm 0% so với 16–100%)*, **quyền từ chối có
căn cứ** *(DP3 — quy kết sai khi con người bỏ trống 35,3% so với 100% khi cấm `REFUSE`)*, và **tính
truy vết** *(DP4 — độ phân kỳ 48,2% giữa trace từ nhật ký và trace viết tay)*.

*Chi tiết đầy đủ của phát hiện này ở [methodology-log.md §L27](methodology-log.md).*

---

## Phần 5 — Phạm vi: những nội dung bị loại khỏi mục tiêu và câu hỏi

Một tuyên bố phạm vi rõ ràng là công cụ bảo vệ khi phản biện, không phải sự thừa nhận điểm yếu. Nội
dung mục này được đưa vào **1.4.2 — Giới hạn về tri thức luận** của luận văn; đề cương gốc chỉ giới
hạn phạm vi ở mức chức năng và chưa có lớp giới hạn này.

| Nội dung bị loại | Lý do — trình bày trực tiếp trong Chương 1 |
|---|---|
| **Đo hiệu quả thực tế của hành động can thiệp** | Olist không ghi nhận bất kỳ hành động nào đã được áp dụng, do đó không có biến treatment và không thể suy luận nhân quả (theo mô hình nhân quả Rubin). Nghiên cứu đánh giá **chất lượng cơ chế sinh khuyến nghị**, không phải hiệu quả can thiệp *(C1)* |
| **Bộ nhớ tình tiết chứa kết quả của hành động** | Cùng lý do — sẽ là dữ liệu bịa. Thay bằng **precedent memory**: truy hồi các case tương tự kèm review score thực tế và nhãn nguyên nhân, dùng để hiệu chỉnh niềm tin về *rủi ro và nguyên nhân*, không dùng để chọn hành động |
| **Policy Critic tính hữu dụng kỳ vọng** | Đại lượng `ΔP(recover \| action)` không ước lượng được từ dữ liệu, nên buộc phải bịa tham số. Critic được thu hẹp thành **engine kiểm tra ràng buộc** (chi phí hành động so với giá trị đơn, ngân sách can thiệp, cooldown người bán, công bằng, bằng chứng yếu, mâu thuẫn nội bộ, trạng thái suy giảm) — toàn bộ tính được từ dữ liệu thật |
| **Mọi chỉ số về "giá trị cứu vãn được"** | Xây trên tham số bịa *(C1)*. Thay bằng nhóm chỉ số **chi phí kiến trúc** — overhead đo được trực tiếp |
| **Tuyên bố về "thời gian thực" và "dữ liệu biến động nhanh"** | Hệ thống chạy theo lô, ngoại tuyến, trên tệp parquet. Độ trễ được đo nhưng không được gọi là real-time. Đây là cụm từ có trong RQ1 và mục 1.1 của đề cương gốc |
| **Tuyên bố "nhận diện sớm" và "phòng ngừa"** | Các đặc trưng có sức phân biệt cao nhất chỉ xuất hiện sau khi giao hàng *(C3)*. Bài toán được đóng khung lại thành **phục hồi dịch vụ trong cửa sổ trước khi khách viết đánh giá**; hành động `expedite_shipment` bị loại vì bất khả thi về mặt thời gian tại T₃ |
| **Tuyên bố về hiệu quả hỗ trợ ra quyết định so với MIS và mô hình đơn lẻ** | Nguồn bằng chứng không tự tham chiếu duy nhất cho tuyên bố này là đánh giá của chuyên gia, nay thuộc nhánh tùy chọn (§5.1). Trên tuyến chính, so sánh với bốn phương án chỉ được trình bày ở mức **mô tả khác biệt chức năng và hành vi khi lỗi** |
| **Khái quát hóa sang CRM và chuỗi cung ứng bằng thực nghiệm** | Không có dữ liệu. Chuyển thành **lập luận phân tích qua bốn Design Principles**, kèm tuyên bố rõ là chưa kiểm chứng |
| **"Quy mô doanh nghiệp" như một biến bối cảnh** | Olist là một nền tảng, một thị trường, giai đoạn 2016–2018. Không tồn tại biến quy mô để cắt lớp |
| **Tác tử dựa trên mô hình ngôn ngữ lớn** *(mặc định)* | Sẽ làm nhiễu loạn causal claim ở RQ1: nếu MAS-DSS tỏ ra vượt trội, không thể tách phần đóng góp của kiến trúc khỏi phần đóng góp của mô hình nền. Chỉ đưa vào như một nhánh thí nghiệm riêng nếu điều kiện thời gian cho phép *(§5.2)* |

### 5.1 Nhánh tùy chọn thứ nhất — đánh giá bởi chuyên gia *(artifact A7)*

Thực hiện nếu tuyển được người đánh giá. Đây là phần bị tách khỏi RQ3 cũ (§2.4).

- **Câu hỏi phụ:** *Khuyến nghị do MAS-DSS sinh ra có được chuyên gia đánh giá là phù hợp hơn so với
  khuyến nghị từ báo cáo kiểu MIS và từ hệ đơn khối đầy đủ chức năng hay không?*
- **Thiết kế:** 100–150 case, mỗi case kèm khuyến nghị từ ba hệ thống, trình bày ngẫu nhiên và ẩn danh
  nguồn gốc; 3–5 người có kinh nghiệm vận hành thương mại điện tử hoặc chăm sóc khách hàng; thang
  Likert 5 mức trên ba tiêu chí: tính phù hợp, tính khả thi, tính giải thích được.
- **Phân tích:** hệ số Krippendorff's α; kiểm định phi tham số Friedman kèm post-hoc.
- **Điều kiện kích hoạt:** tuyển được tối thiểu ba người đánh giá. Nếu không đạt, nhánh này bị bỏ và
  luận văn không đưa ra tuyên bố nào về hiệu quả hỗ trợ ra quyết định.
- **Nếu thực hiện:** nhánh này khôi phục lại một câu hỏi ở tầng criterion validity và bổ sung giả
  thuyết *"khuyến nghị của MAS-DSS được đánh giá phù hợp hơn"* vào bảng tại §3.

### 5.2 Nhánh tùy chọn thứ hai — phản biện dựa trên mô hình ngôn ngữ lớn

- **Câu hỏi phụ:** *Cơ chế phản biện dựa trên mô hình ngôn ngữ lớn có cải thiện chất lượng chuỗi quyết
  định so với cơ chế phản biện dựa trên ràng buộc hay không?*
- **Thiết kế:** điều kiện A là MAS-DSS với Policy Critic dựa trên ràng buộc (artifact chính); điều kiện
  B là MAS-DSS với Policy Critic dựa trên mô hình ngôn ngữ chạy cục bộ, nhiệt độ bằng 0 và seed cố định.
- **Ý nghĩa:** cách bố trí này chuyển mô hình ngôn ngữ lớn từ một nghĩa vụ phải biện minh trước hội
  đồng thành một câu hỏi nghiên cứu có câu trả lời — trong đó kết quả "không cải thiện" cũng là một kết
  quả có giá trị. Nhánh này đồng thời khép lại độ lệch giữa phần tổng quan tài liệu về agentic AI ở
  Chương 2 và hệ thống thực sự được xây dựng.

### 5.3 Phân tích độ nhạy được giữ lại trong Chương 5 *(không nâng thành câu hỏi nghiên cứu)*

- **Theo điều kiện bằng chứng — phân tích chính:** đối chiếu **T₃** (chỉ đặc trưng bảng, không có văn
  bản) với **T₄** (có văn bản với 74,77% đơn). Đây là cặp tương phản mạnh nhất về điều kiện thông tin,
  vì cả hai đều là chế độ hệ thống **thực sự vận hành** chứ không phải kịch bản giả định, và nó lượng
  hóa trực tiếp giá trị mà bằng chứng văn bản đóng góp cho việc quy kết nguyên nhân.
- **Theo thời điểm ra quyết định — phân tích bổ sung:** đối chiếu T₂ (lúc bàn giao vận chuyển) với T₃
  (sau khi giao hàng), thực hiện bằng một thay đổi cấu hình theo MT3.4. Chỉ áp dụng cho nhiệm vụ dự báo
  rủi ro ở giai đoạn 1. Kết quả báo cáo như phân tích độ nhạy, không kèm tuyên bố về tính khái quát.
- **Theo mức ngưỡng định nghĩa nhãn:** đối chiếu `review_score ≤ 2` với `review_score ≤ 3`, báo cáo cả
  hai để chứng minh kết luận không phụ thuộc vào một lựa chọn ngưỡng tùy ý.

---

## Phần 6 — Ranh giới tuyên bố

| **Không được tuyên bố** | **Lý do** |
|---|---|
| ~~"MAS-DSS dự báo chính xác hơn mô hình học máy đơn lẻ"~~ | Hai hệ dùng chung một mô hình LightGBM, nên tuyên bố này tất yếu sai (H1) |
| ~~"Hành động khuyến nghị cải thiện mức độ hài lòng của khách hàng"~~ | Không kiểm chứng được trên Olist do thiếu biến treatment (C1) |
| ~~"Hệ thống phòng ngừa sự bất mãn từ sớm"~~ | Các đặc trưng có sức phân biệt chỉ xuất hiện sau khi giao hàng (C3) |
| ~~"Hệ thống xử lý trong thời gian thực"~~ | Hệ thống chạy theo lô, ngoại tuyến |
| ~~"Tỷ lệ hỏng âm thầm bằng 0 chứng minh tính vượt trội của kiến trúc"~~ | Đây là kiểm tra đặc tả, không phải một phát hiện thực nghiệm |
| ~~"MAS-DSS hỗ trợ ra quyết định hiệu quả hơn MIS"~~ | Chỉ tuyên bố được nếu nhánh đánh giá chuyên gia (§5.1) được thực hiện |

| **Được tuyên bố** | **Bằng chứng đứng sau** |
|---|---|
| "Trên cùng một năng lực dự báo nền, cơ chế quy kết nguyên nhân bằng nhiều tác tử cạnh tranh đạt macro-F1 *x* trên tập nhãn chuẩn do người gán, so với *y* của bộ phân loại đơn khối; khoảng cách mở rộng lên *z* ở nhóm đơn hàng có nhiều nguyên nhân đồng thời" | Gold set (A3) + kiểm định tương đương (H1) + macro-F1 có cắt lớp (H2) |
| "Khi một tác tử gặp lỗi, kiến trúc đơn khối cho ra quyết định sai mà không cảnh báo trên *p*% số case, trong khi kiến trúc đề xuất suy giảm một cách minh bạch và chuyển giao cho con người" | Chaos harness trên Monolithic-Complete (H3) |
| "Bộ giám sát phát hiện được drift phân phối ở mức *d*% sau *n* case, với tỷ lệ báo động giả *f*%" | Đường cong độ nhạy và độ trễ phát hiện (H4) |
| "Khả năng chịu lỗi nêu trên phải trả giá bằng *x* ms overhead trên mỗi case và *k* thành phần bổ sung" | Đo độ trễ p50/p95 và quy mô kiến trúc (H5) |
| "Quyết định của hệ thống truy vết được: *r*% decision trace tái lập được hoàn toàn từ nhật ký giao tiếp, và không có quyết định tự động nào được sinh ra khi hệ thống ở trạng thái suy giảm" | Demonstration cho RQ2 + cơ chế cưỡng chế DP1, DP4 |
| "Bốn Design Principles **có thể** chuyển giao sang các bài toán CRM và chuỗi cung ứng" — kèm tuyên bố rõ đây là suy luận thiết kế chưa được kiểm chứng | A2 + lập luận phân tích tại Chương 5 |

**Phát biểu về tính mới.** Theo phân loại của Gregor & Hevner (2013), luận văn thuộc loại **Improvement**
— giải pháp mới cho một vấn đề đã biết. Các thành phần nền tảng đều không mới (Contract Net 1980,
Blackboard 1985, supervision tree của Erlang/OTP thập niên 1990, FIPA-ACL 2002), do đó tuyên bố về tính
mới phải hẹp và chính xác:

> **Tích hợp cơ chế giám sát chịu lỗi và suy giảm minh bạch vào một chuỗi hỗ trợ ra quyết định, cùng với
> một phương pháp đánh giá (chaos harness) cho phép định lượng khả năng chịu lỗi của hệ hỗ trợ quyết
> định — khía cạnh mà văn liệu MAS-DSS hiện tại bỏ trống.**

Kèm theo bốn Design Principles với tư cách tri thức trừu tượng rút ra được. Không tuyên bố rộng hơn.

---

## Phần 7 — Ma trận truy vết

### 7.1 Mục tiêu → Câu hỏi → Giả thuyết → Artifact → Thí nghiệm → Chương

| MT | RQ | Giả thuyết | Artifact | Thí nghiệm | Chương |
|---|---|---|---|---|---|
| **MT1** | **RQ1** | **H2, H3** | A4, A5, A6 | **Chaos harness**: 5 nhóm lỗi × 3 mức, gồm crash và Byzantine; cùng kịch bản trên MAS-DSS và Monolithic-Complete; chạy ở **cả hai giai đoạn** và trên **năm thành phần chỉ có ở MAS**; đo bề mặt hỏng và độ trễ tuyệt đối | 5 |
| **MT2** | **RQ2** | — (demonstration) | A1, A2, A5 | Chạy end-to-end trên Olist; đo **độ phân kỳ** giữa trace dựng từ nhật ký và trace viết tay; kiểm tra cưỡng chế `degradation_level`; bốn ablation cho bốn DP | 3, 4 |
| **MT3** | **RQ3** | **H1** | A3, A5, A6 | Kiểm định tương đương cho dự báo tại T₃; đếm **số đơn cho kết quả khác nhau** cho quy kết tại T₄, trên **gold set**; cắt lớp nhóm đa nguyên nhân | 4, 5 |
| MT2 | — | — | A2 (4 DP) | Lập luận phân tích về khả năng chuyển giao sang CRM và chuỗi cung ứng *(chưa kiểm chứng)* | 5 (thảo luận) |
| MT1, MT3 | — | — | A5, A6 | Phân tích độ nhạy: **mốc T₃** *(mua+3 · +7 · +14)*; ngưỡng nhãn `≤ 2` đối chiếu `≤ 3`; ngưỡng chi phí FN:FP | 5 |
| *(tùy chọn)* | §5.1 | *(bổ sung)* | A7 | Đánh giá chuyên gia theo thiết kế mù | 5 |

**Không có ô trống, không có artifact thừa, và không có câu hỏi nào không trả lời được bằng dữ liệu
hiện có.**

### 7.2 Danh mục artifact

Phân loại theo Hevner (constructs / models / methods / instantiations). Chi tiết tại
[research-design-v2.md §5](research-design-v2.md).

| ID | Artifact | Loại | Phục vụ | Ghi chú |
|---|---|---|---|---|
| **A1** | Ontology và giao thức giao tiếp (**10** performative, construct `DegradationLevel`) | Construct | RQ2 | — |
| **A2** | Kiến trúc tham chiếu MAS-DSS và **bốn Design Principles** | Model | RQ2 | **Tri thức thiết kế — giải thích vì sao RQ1 cho kết quả đó** |
| **A3** | **Gold set 300 đơn hàng do người gán** | Instantiation / resource | RQ3 | **Điều kiện tiên quyết của RQ3** |
| **A4** | **Chaos harness** — phương pháp đánh giá khả năng chịu lỗi cho DSS | Method | RQ1 | **Đóng góp phương pháp — trục chính** |
| **A5** | Prototype MAS-DSS trên Olist | Instantiation | RQ1, RQ2, RQ3 | Nền tảng của mọi thí nghiệm |
| **A6** | Bộ khung đánh giá và bốn phương án thay thế (có Monolithic-Complete) | Method + instantiation | RQ1, RQ3 | Điều kiện để phép so sánh không phải là so với baseline bù nhìn |
| *(A7)* | Giao thức đánh giá bởi chuyên gia | Method | §5.1 | **Nhánh tùy chọn** — chỉ thực hiện nếu tuyển được người đánh giá |

---

## Phần 8 — Thứ tự công việc để chốt được Chương 1

| # | Công việc | Lý do ưu tiên |
|---|---|---|
| 1 | ~~**Thống kê tỷ lệ đơn hàng bất mãn không có bình luận**~~ ✅ **ĐÃ XONG** | Kết quả: **25,23% không có văn bản, 74,77% có** (§0.1). Cổng M0 đạt; RQ3 đứng vững; rủi ro ">50%" đóng lại |
| 2 | **Loại bỏ `review_lag_days`** và **chặn `has_comment`** khỏi feature set giai đoạn T₃ | Cả hai đều là rò rỉ nhãn: chỉ tồn tại sau khi đánh giá đã được viết, trong khi điểm đánh giá chính là nhãn (C3, C4) |
| 3 | Chốt **hai mốc quyết định T₃ / T₄** (§0.2), đóng khung lại bài toán thành **phục hồi dịch vụ**, và sửa tập luật (loại `expedite_shipment`) | Mốc T₃ đơn lẻ mâu thuẫn với việc dùng bằng chứng văn bản; hệ thống hiện cũng đang khuyến nghị một hành động bất khả thi về mặt thời gian |
| 4 | **Khởi động việc xây dựng gold set** (A3) song song với lập trình | Hạng mục tốn thời gian nhất và nằm trên **đường tới hạn**. Không có gold set thì RQ3 không trả lời được và Chương 5 mất phần lớn giá trị |
| 5 | Cập nhật **mục 1.2, 1.3 và 1.4.2** theo tài liệu này; bổ sung **bốn Design Principles** vào Chương 3 và sửa mục 3.2.5 | Để phần viết không phải thực hiện lại lần thứ hai |
| 6 | Xây dựng baseline **Monolithic-Complete** (A6) | Chi phí thấp (khoảng một ngày) nhưng quyết định giá trị của cả RQ2 lẫn RQ3 |

---

## Phụ lục — Đối chiếu với đề cương gốc

Đề cương gốc: `context/250104007_NguyenTanTruongMinhHoang_Report_L1.pdf`, mục 1.2 và 1.3. Bản đối chiếu
nguyên văn đầy đủ: [proposal-comparison.md](proposal-comparison.md).

### A. Mục tiêu nghiên cứu

| # | Đề cương gốc | Bản này | Mức thay đổi |
|---|---|---|---|
| MT1 | Đề xuất kiến trúc MAS cho thương mại điện tử theo chu trình thu thập – phân tích – dự báo – đề xuất | Bổ sung **bốn Design Principles** và **điều kiện tác tử có thể lỗi hoặc suy giảm** | **Mở rộng** |
| MT2 | Xây dựng prototype trên Olist gồm mô-đun phân loại nguyên nhân và DSS dựa trên luật | Bổ sung **gold set do người gán** làm điều kiện tiên quyết; bổ sung tầng xử lý văn bản hai tầng A/B | **Bổ sung điều kiện tiên quyết** |
| MT3 | Đánh giá định lượng so với MIS và mô hình học máy đơn lẻ, trọng tâm là **độ chính xác dự báo** | Chuyển trọng tâm sang **đánh giá khả năng chịu lỗi** đối chiếu với **Monolithic-Complete**; độ chính xác dự báo trở thành **điều kiện kiểm soát**; công bố **chaos harness** như đóng góp phương pháp | **Viết lại** |

### B. Câu hỏi nghiên cứu

| Đề cương gốc | Chủ đề | Số phận | Bản này |
|---|---|---|---|
| **RQ1** | Thiết kế thế nào để **"phù hợp"** với hệ thống thông tin doanh nghiệp, dữ liệu **biến động nhanh** | Viết lại — thu hẹp thành thuộc tính quan sát được | **RQ2** — truy vết được và trung thực về độ tin cậy khi tác tử lỗi |
| **RQ2** | Các tác tử phân công và phối hợp **ra sao** | Làm sắc lại — chuyển từ mô tả sang so sánh; bổ sung gold set | **RQ3** — đạt các thuộc tính đó **mà không đánh đổi** độ chính xác *(đổi từ "tốt hơn" sang tương đương sau khi đo được 0/250)* |
| **RQ3** | Có cải thiện **độ chính xác dự báo**, khả năng phát hiện, thời gian xử lý và "hiệu quả hỗ trợ quyết định" không | Tách ba phần | Vế giải thích được → **RQ2**; vế độ trễ → **RQ1** vế (d); vế đánh giá chuyên gia → **nhánh tùy chọn §5.1** |
| **RQ4** | Bối cảnh nào phát huy tốt nhất; mở rộng sang **CRM / chuỗi cung ứng** | Thay bằng nội dung trả lời được, rồi hấp thụ | Cắt lớp theo bình luận → **RQ3** tình huống (b); cắt lớp T₂/T₃ → **phân tích độ nhạy §5.3**; CRM/SCM → lập luận qua Design Principles |
| *(không có)* | — | **Bổ sung — nay là trục chính** | **RQ1** — chịu lỗi: hỏng âm thầm, độ nhạy và độ trễ phát hiện, mức suy giảm, và chi phí phải trả |

**Nhận xét cốt lõi.** Bộ câu hỏi gốc đặt trọng tâm vào chỗ kiến trúc chắc chắn không thể vượt trội (độ
chính xác dự báo, do dùng chung mô hình) và vào chỗ không có dữ liệu để trả lời (mở rộng sang CRM và
chuỗi cung ứng), trong khi **không câu hỏi nào phụ trách khả năng chịu lỗi** — vốn là đóng góp thật sự
của luận văn. Bản ba câu hỏi này giữ lại đúng ba trục có đồng thời giá trị đóng góp và tính khả thi:
**thiết kế** (tri thức trừu tượng), **cơ chế** (kiểm chứng được trên nhãn chuẩn), và **chịu lỗi**
(khoảng trống trong văn liệu).
