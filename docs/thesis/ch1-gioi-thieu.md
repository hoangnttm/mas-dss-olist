# CHƯƠNG 1 — GIỚI THIỆU

## 1.1 Bối cảnh nghiên cứu

Trong thương mại điện tử, một đánh giá một sao hiếm khi là một sự kiện đơn lẻ. Nó là dấu vết còn lại
của một chuỗi sự cố đã diễn ra trước đó — hàng đến muộn, người bán chưa gửi, sản phẩm không đúng như
mô tả, hoặc một yêu cầu hỗ trợ bị bỏ quên. Vào thời điểm khách hàng ngồi xuống viết đánh giá, phần lớn
thiệt hại đã thành hình: trải nghiệm tiêu cực đã xảy ra, đánh giá sắp trở thành công khai, và tổ chức
chỉ còn lựa chọn xử lý hậu quả thay vì ngăn chặn nguyên nhân.

Văn liệu về phục hồi dịch vụ (service recovery) từ lâu đã chỉ ra rằng khoảng thời gian giữa lúc sự cố
phát sinh và lúc khách hàng bày tỏ bất mãn là khoảng thời gian có giá trị nhất đối với tổ chức. Một
hành động phục hồi đúng lúc và đúng nguyên nhân có khả năng giữ lại quan hệ khách hàng, thậm chí củng
cố nó; cũng hành động ấy nhưng áp dụng sau khi khách đã công khai bày tỏ bất mãn thì hiệu quả thấp hơn
đáng kể trong khi chi phí lại cao hơn. Nói cách khác, giá trị của một hệ thống hỗ trợ phục hồi dịch vụ
phụ thuộc không chỉ vào việc nó *nhận ra điều gì*, mà còn vào việc nó nhận ra *khi nào*.

Từ đó hình thành một bài toán hệ thống thông tin có ranh giới rõ ràng: làm thế nào để phát hiện sớm
những đơn hàng có nguy cơ dẫn tới bất mãn, xác định nguyên nhân của nguy cơ đó, và đề xuất hành động
phục hồi phù hợp — tất cả trước khi khách hàng viết đánh giá. Bài toán này là điểm xuất phát của luận
văn.

### 1.1.1 Vì sao một mô hình dự báo đơn lẻ không đủ để trả lời bài toán

Cách tiếp cận trực tiếp nhất là huấn luyện một mô hình phân loại: đưa vào đặc trưng của đơn hàng, nhận
về xác suất khách hàng sẽ bất mãn. Cách này giải quyết được vế *phát hiện*, và trong nhiều nghiên cứu
trên dữ liệu thương mại điện tử, nó là toàn bộ phạm vi bài toán. Tuy nhiên, khi đặt hệ thống vào bối
cảnh vận hành thực tế của một tổ chức, ba khoảng trống lộ ra mà một mô hình đơn lẻ không lấp được.

Khoảng trống thứ nhất là **khoảng cách giữa một xác suất và một hành động**. Biết rằng một đơn hàng có
sáu mươi tám phần trăm khả năng bị đánh giá xấu không cho biết nên gửi phiếu giảm giá, nên liên hệ với
người bán để thúc tiến độ, hay nên chủ động hoàn phí vận chuyển. Ba hành động ấy ứng với ba nguyên
nhân khác nhau, có chi phí khác nhau, và chọn sai không phải là lựa chọn trung tính: một phiếu giảm
giá gửi cho khách hàng đang bực bội vì hàng chưa rời kho người bán có thể làm tình hình xấu thêm.

Khoảng trống thứ hai là **khả năng truy vết**. Khi một nhà quản lý hỏi vì sao hệ thống đề xuất hoàn
phí cho một đơn hàng cụ thể, một điểm số kèm biểu đồ đóng góp đặc trưng không phải là câu trả lời ở
mức mà một quy trình vận hành có thể chấp nhận. Thứ cần có là một chuỗi lập luận có thể kiểm tra lại:
bằng chứng nào đã được xem xét, kết luận nào đã được rút ra từ bằng chứng ấy, và quan trọng không kém
— phương án nào đã bị loại bỏ và vì lý do gì.

Khoảng trống thứ ba, và là khoảng trống trung tâm của luận văn này, là **sự vắng mặt của khái niệm về
độ tin cậy của chính hệ thống tại thời điểm nó ra quyết định**. Khi một thành phần trong hệ thống gặp
lỗi, suy giảm chất lượng, hoặc trả về kết quả hợp lệ về mặt kỹ thuật nhưng sai về mặt nội dung, hệ
thống vẫn tiếp tục sinh ra quyết định với vẻ ngoài hoàn toàn bình thường. Không có gì trong đầu ra cho
người sử dụng biết rằng quyết định này được sinh ra trên một nền năng lực đã suy giảm.

### 1.1.2 Hỏng âm thầm và hệ quả riêng của nó trong hệ hỗ trợ quyết định

Loại lỗi vừa mô tả có tên gọi trong kỹ thuật độ tin cậy: **hỏng âm thầm** (silent failure). Nó nguy
hiểm hơn lỗi làm hệ thống dừng, bởi một lỗi làm dừng thì ai cũng nhìn thấy và quy trình xử lý sự cố
được kích hoạt ngay, còn hỏng âm thầm thì hệ thống vẫn chạy, vẫn cho ra kết quả, và kết quả ấy vẫn
được sử dụng để ra quyết định.

Trong một dịch vụ kỹ thuật thuần túy, hỏng âm thầm gây ra dữ liệu sai và có thể được phát hiện muộn
qua đối soát. Trong một hệ hỗ trợ quyết định, hậu quả có bản chất khác: nó ăn mòn chính thứ làm cho hệ
thống có ích, tức là lòng tin của người ra quyết định. Một hệ thống thỉnh thoảng nói rằng nó không đủ
cơ sở và đề nghị con người xem lại có giá trị vận hành cao hơn một hệ thống luôn trả lời với vẻ tự tin
đồng đều bất kể tình trạng nội tại của nó — bởi người sử dụng hệ thống thứ hai không có cách nào phân
biệt lúc nào nên tin và lúc nào không.

Văn liệu về hệ đa tác tử và văn liệu về hệ hỗ trợ quyết định đều đã phát triển lâu và đều phong phú.
Tuy nhiên phần giao giữa chúng — cụ thể là hành vi của một kiến trúc đa tác tử dưới điều kiện lỗi,
trong vai trò hỗ trợ quyết định — còn ít được nghiên cứu bằng thực nghiệm. Các công trình về hệ hỗ trợ
quyết định hướng tác tử thường chứng minh giá trị của kiến trúc thông qua khả năng biểu diễn bài toán
và thông qua độ chính xác trên đường chạy bình thường, hiếm khi đặt câu hỏi điều gì xảy ra với chất
lượng quyết định khi một thành phần hỏng. Đây chính là khoảng trống mà luận văn nhắm tới.

---

## 1.2 Vấn đề nghiên cứu

Từ bối cảnh trên, luận văn xác định vấn đề nghiên cứu như sau:

> Một kiến trúc hệ thống thông tin đa tác tử cho bài toán phát hiện và xử lý bất mãn của khách hàng
> trong thương mại điện tử cần được thiết kế như thế nào để vẫn tạo ra quyết định *truy vết được* và
> *trung thực về mức độ tin cậy* khi một hoặc nhiều thành phần gặp lỗi, và liệu khả năng đó có phải
> đánh đổi bằng độ chính xác hay không.

Phát biểu này chứa ba mệnh đề phụ, và cả ba đều dễ trở thành khẩu hiệu nếu không được quy về đại lượng
quan sát được. Luận văn vì vậy thao tác hóa từng mệnh đề ngay từ giai đoạn thiết kế nghiên cứu, trước
khi tiến hành đo đạc; chi tiết đầy đủ trình bày ở [§3.6](ch3-phuong-phap.md). Bảng 1.1 tóm tắt phép
quy đổi này.

**Bảng 1.1.** Thao tác hóa ba mệnh đề trong phát biểu vấn đề nghiên cứu

| Mệnh đề | Đại lượng quan sát được |
|---|---|
| Quyết định *truy vết được* | tỷ lệ decision trace tái lập được hoàn toàn từ nhật ký thông điệp; độ phân kỳ giữa trace dựng từ nhật ký và trace viết tay |
| Quyết định *trung thực về mức độ tin cậy* | mức suy giảm là trường bắt buộc của mọi quyết định; tỷ lệ quyết định tự động được sinh khi mức suy giảm lớn hơn không |
| *Không đánh đổi độ chính xác* | kiểm định tương đương trên chỉ số dự báo; số đơn hàng mà hai kiến trúc cho kết quả khác nhau |

Điểm đáng lưu ý ở cột bên phải của Bảng 1.1 là cả ba đại lượng đều có thể nhận giá trị bất lợi cho giả
thuyết của nghiên cứu. Đây là điều kiện tối thiểu để một phép đo có giá trị chứng minh, và luận văn sẽ
trở lại điểm này ở [§3.7](ch3-phuong-phap.md) khi trình bày các giả thuyết khai báo trước.

---

## 1.3 Mục tiêu nghiên cứu

### 1.3.1 Mục tiêu tổng quát

Nghiên cứu hướng đến việc thiết kế, hiện thực hóa và đánh giá một kiến trúc hệ hỗ trợ quyết định đa
tác tử đạt được độ tin cậy vận hành dưới điều kiện lỗi mà không phải đánh đổi độ chính xác, cho chuỗi
xử lý gồm ba khâu: phát hiện rủi ro bất mãn, quy kết nguyên nhân, và đề xuất hành động phục hồi dịch
vụ. Song song với artifact, nghiên cứu rút ra một tập nguyên lý thiết kế cho việc xây dựng hệ hỗ trợ
quyết định vận hành được dưới điều kiện lỗi.

Cách phát biểu *"không phải đánh đổi độ chính xác"* là một lựa chọn có cân nhắc, và nó khác về bản
chất với *"vượt trội về độ chính xác"*. Bổ sung khả năng chịu lỗi vào một hệ thống thường phải trả giá
— bằng độ chính xác, bằng độ trễ, hoặc bằng độ phức tạp vận hành. Câu hỏi thiết kế đúng đắn vì vậy
không phải là kiến trúc nào chính xác hơn, mà là liệu có thể có được khả năng chịu lỗi mà không mất gì
ở phía độ chính xác hay không, và nếu cái giá không nằm ở đó thì nó nằm ở đâu. Đặt câu hỏi theo cách
này còn có một ưu điểm về mặt phương pháp: nó buộc nghiên cứu phải đo và công bố chi phí, thay vì chỉ
trình bày ưu điểm.

### 1.3.2 Ba mục tiêu cụ thể

Mục tiêu tổng quát được phân rã thành ba mục tiêu cụ thể, mỗi mục tiêu tương ứng một câu hỏi nghiên
cứu và tạo ra một nhóm artifact riêng.

Mục tiêu thứ nhất là **phát triển và công bố một phương pháp đánh giá khả năng chịu lỗi cho hệ hỗ trợ
quyết định**. Sản phẩm gồm một phân loại lỗi, một cơ chế tiêm lỗi có kiểm soát, một bộ chỉ số, và một
giao thức so sánh hai kiến trúc trên cùng kịch bản lỗi. Yêu cầu về phạm vi được đặt ra ngay từ mục
tiêu: phép đo phải thực hiện ở cả hai mốc quyết định và trên toàn bộ bề mặt hỏng của kiến trúc, chứ
không chỉ trên phần bề mặt thuận lợi cho kiến trúc đề xuất. Sản phẩm chính là bộ công cụ tiêm lỗi mà
luận văn gọi là *chaos harness*, và đây là đóng góp phương pháp của nghiên cứu.

Mục tiêu thứ hai là **thiết kế kiến trúc tham chiếu và rút ra bốn nguyên lý thiết kế**. Ràng buộc đặt
ra ở đây là mỗi nguyên lý phải gắn với một cơ chế cưỡng chế trong mã nguồn và một thí nghiệm ablation
tương ứng — nghĩa là nguyên lý phải được kiểm chứng chứ không chỉ được phát biểu. Sản phẩm gồm ontology
và giao thức giao tiếp giữa các tác tử, kiến trúc tham chiếu, và bốn nguyên lý; đây là đóng góp lý
thuyết của nghiên cứu.

Mục tiêu thứ ba là **hiện thực hóa một prototype cùng với các điều kiện tiên quyết cho một phép so
sánh không thiên lệch**. Hai điều kiện tiên quyết ấy là một bộ nhãn chuẩn do con người gán, và một
kiến trúc đối chứng đầy đủ chức năng, không bị làm yếu có chủ đích. Điều kiện thứ hai đáng được nhấn
mạnh: nếu kiến trúc đối chứng được thiết kế sao cho nó thua, thì mọi khác biệt đo được sau đó không
nói lên điều gì về kiến trúc đề xuất.

---

## 1.4 Câu hỏi nghiên cứu

Ba câu hỏi nghiên cứu dưới đây được sắp xếp theo trọng số đóng góp chứ không theo trình tự thi công.
Thứ tự này phản ánh một đánh giá đã được kiểm chứng bằng thực nghiệm: claim mạnh nhất mà nghiên cứu
chứng minh được là một claim về hành vi kiến trúc dưới điều kiện lỗi, chứ không phải một claim về độ
chính xác.

**Câu hỏi thứ nhất — câu hỏi chịu lỗi.** *Khi một hoặc nhiều thành phần gặp lỗi hoặc suy giảm chất
lượng, kiến trúc đa tác tử và kiến trúc đơn khối khác nhau như thế nào về tỷ lệ hỏng âm thầm, về độ
nhạy và độ trễ phát hiện, về mức suy giảm chất lượng quyết định, và về bề mặt hỏng cùng chi phí tính
toán?*

**Câu hỏi thứ hai — câu hỏi thiết kế.** *Một kiến trúc hệ thống thông tin đa tác tử cần được thiết kế
như thế nào để chuỗi ra quyết định phát hiện, quy kết nguyên nhân và đề xuất hành động vẫn tạo ra
quyết định truy vết được và trung thực về mức độ tin cậy, kể cả khi một hoặc nhiều tác tử lỗi?*

**Câu hỏi thứ ba — câu hỏi điều kiện kiểm soát.** *Kiến trúc đa tác tử có đạt được các thuộc tính vận
hành nêu ở hai câu hỏi trên mà không đánh đổi độ chính xác hay không, cả ở khâu dự báo rủi ro lẫn khâu
quy kết nguyên nhân, khi nó và các kiến trúc đối chứng vận hành trên cùng một năng lực nền?*

Ba câu hỏi này không độc lập với nhau; chúng tạo thành một cấu trúc lập luận trong đó mỗi câu hỏi giữ
một vai trò khác biệt. Câu hỏi chịu lỗi là trục chính, mang claim nhân quả về hành vi kiến trúc. Câu
hỏi thiết kế giải thích **vì sao** câu hỏi thứ nhất cho kết quả như đã quan sát: bốn nguyên lý thiết
kế chính là cơ chế đứng sau kết quả, và cũng là phần tri thức có khả năng chuyển giao sang miền ứng
dụng khác. Câu hỏi điều kiện kiểm soát có vai trò loại bỏ một lời giải thích thay thế: nếu hai kiến
trúc khác nhau về độ chính xác nền, thì mọi khác biệt quan sát được ở câu hỏi thứ nhất đều có thể được
quy cho độ chính xác thay vì cho kiến trúc, và claim nhân quả sẽ mất hiệu lực.

Cấu trúc lập luận này được ánh xạ tường minh vào khung phân loại hiệu lực của Larsen và cộng sự
(2025), như trình bày ở Bảng 1.2. Việc khai báo trước loại bằng chứng mà mỗi câu hỏi sẽ và sẽ không
cung cấp có tác dụng phòng ngừa cụ thể: nó ngăn việc trình bày một kết quả thuộc loại *demonstration*
như thể nó là bằng chứng nhân quả.

**Bảng 1.2.** Ánh xạ ba câu hỏi nghiên cứu vào khung hiệu lực

| Câu hỏi | Loại claim | Loại hiệu lực | Loại bằng chứng |
|---|---|---|---|
| Chịu lỗi | Nhân quả | Causal validity | ablation và tiêm lỗi có kiểm soát |
| Thiết kế | Thiết kế / quy phạm | — | demonstration bằng một hiện thực vận hành được |
| Điều kiện kiểm soát | Criterion | Criterion efficacy | bộ nhãn chuẩn do người gán |

Hàng giữa của Bảng 1.2 là tầng mà đề cương ban đầu của nghiên cứu không có. Bổ sung tầng thiết kế —
tức tầng tri thức quy phạm — chính là điều nâng luận văn từ mức mô tả một hệ thống đã xây lên mức
nghiên cứu Design Science đúng nghĩa theo phân loại của Gregor và Hevner (2013). Nếu chỉ có tầng nhân
quả và tầng criterion, công trình sẽ dừng ở một báo cáo kỹ thuật có đo đạc cẩn thận.

---

## 1.5 Phạm vi và giới hạn

### 1.5.1 Dữ liệu và đơn vị phân tích

Nghiên cứu sử dụng bộ dữ liệu công khai *Brazilian E-Commerce Public Dataset by Olist*, gồm chín bảng
quan hệ mô tả khoảng chín mươi chín nghìn đơn hàng thương mại điện tử tại Brazil trong giai đoạn 2016
đến 2018. Đơn vị phân tích của luận văn là **case đơn hàng**, không phải dòng đánh giá thô: trong dữ
liệu có năm trăm năm mươi mốt đơn mang nhiều hơn một bản ghi đánh giá, và sau khi khử trùng lặp bằng
cách giữ bản ghi sớm nhất, tổng thể còn **98.673 case**. Thống kê mô tả đầy đủ được trình bày ở
[§3.2.2](ch3-phuong-phap.md).

### 1.5.2 Năm ràng buộc dữ liệu định hình toàn bộ nghiên cứu

Phạm vi của luận văn không được xác định bằng sở thích của người nghiên cứu mà bằng năm ràng buộc rút
ra từ chính cấu trúc dữ liệu. Đây không phải các lưu ý kỹ thuật mà là **biên của nghiên cứu**: mọi mục
tiêu hoặc câu hỏi vi phạm một trong năm ràng buộc này đều đã bị loại bỏ, bất kể mức độ hấp dẫn của
chúng về mặt học thuật. Bảng 1.3 trình bày tóm tắt; lập luận đầy đủ cho từng ràng buộc nằm ở
[§3.2.3](ch3-phuong-phap.md).

**Bảng 1.3.** Năm ràng buộc dữ liệu và hệ quả đối với phạm vi nghiên cứu

| Ràng buộc | Nội dung | Hệ quả |
|---|---|---|
| Không có biến treatment | Không trường nào ghi nhận hành động đã áp dụng; không tồn tại kết quả phản thực | Nghiên cứu đánh giá **chất lượng khuyến nghị**, không đánh giá **hiệu quả can thiệp** |
| Nhãn nguyên nhân không có sẵn | Dữ liệu có điểm và văn bản nhưng không có nguyên nhân | Mọi phép đo quy kết nguyên nhân bắt buộc dựa trên bộ nhãn do người gán |
| Kết cục giao hàng không dùng để dự báo được | Đánh giá đến trung vị 6,2 giờ sau khi giao; 87,8% đánh giá viết trước hạn dự kiến | Mốc quyết định phải neo vào **ngày mua** |
| Văn bản xuất hiện cùng lúc với nhãn | Bình luận được viết đồng thời với điểm số | Chuỗi xử lý bắt buộc tách làm **hai mốc quyết định** |
| Không quan sát được chất lượng trước khi đánh giá được viết | Chín bảng dữ liệu không có phiếu hỗ trợ, đổi trả hay lịch sử liên hệ | Quy kết nguyên nhân về chất lượng và dịch vụ bất khả thi ở mọi mốc sớm |

Ràng buộc cuối cùng trong Bảng 1.3 đáng được nhấn mạnh riêng, bởi nó giữ một vai trò khác với bốn ràng
buộc còn lại. Bốn ràng buộc đầu **loại bỏ** các hướng nghiên cứu; ràng buộc thứ năm **biện minh cho
một quyết định thiết kế**. Cụ thể, việc không tồn tại bất kỳ quan sát nào về chất lượng sản phẩm hay
chất lượng phục vụ trước thời điểm khách hàng viết đánh giá khiến cho việc tách chuỗi xử lý thành hai
mốc quyết định trở thành **hệ quả bắt buộc của cấu trúc dữ liệu**, chứ không phải một lựa chọn tiện
lợi về mặt kỹ thuật. Đây là điểm mà luận văn sẽ quay lại nhiều lần, vì nó là nền của toàn bộ kiến
trúc.

### 1.5.3 Những nội dung nằm ngoài phạm vi

Bốn nhóm nội dung được loại khỏi tuyến chính của nghiên cứu, mỗi nhóm có một lý do cụ thể chứ không
phải vì thiếu thời gian.

Nghiên cứu **không đánh giá hiệu quả của hành động can thiệp**. Đây là hệ quả trực tiếp của ràng buộc
về biến treatment: không có dữ liệu phản thực thì không có cách nào biết điều gì đã xảy ra nếu áp dụng
một hành động khác. Mọi phát biểu về hiệu quả can thiệp trong luận văn, nếu có, đều là suy luận từ văn
liệu chứ không phải kết quả đo được.

Nghiên cứu **không tuyên bố khả năng xử lý thời gian thực**. Hệ thống chạy theo lô, ngoại tuyến, trên
dữ liệu lịch sử. Một tuyên bố về thời gian thực sẽ không kiểm chứng được trong thiết kế thí nghiệm
hiện tại, và vì vậy nó bị loại khỏi cả mục tiêu lẫn phần kết luận.

Nghiên cứu **không bao gồm đánh giá bởi chuyên gia miền**. Nhánh này phụ thuộc vào nguồn lực nằm ngoài
tầm kiểm soát của nghiên cứu sinh, nên nó được giữ lại như một nhánh tùy chọn thay vì đưa vào tuyến
chính — một câu hỏi nghiên cứu phụ thuộc vào nguồn lực không kiểm soát được là một câu hỏi có rủi ro
tiến độ cao.

Cuối cùng, việc **mở rộng sang các miền quản trị khác** như quản trị quan hệ khách hàng hay chuỗi cung
ứng chỉ được lập luận thông qua bốn nguyên lý thiết kế, và luận văn nêu rõ rằng đó là **suy luận thiết
kế chưa được kiểm chứng thực nghiệm**. Nguyên lý thiết kế là cầu nối hợp lệ duy nhất sang miền khác;
một tuyên bố mạnh hơn thế sẽ vượt quá bằng chứng đang có.

---

## 1.6 Đóng góp của luận văn

Đóng góp của nghiên cứu được trình bày theo bốn nhóm, tương ứng bốn loại tri thức khác nhau.

### 1.6.1 Đóng góp về phương pháp

Nghiên cứu xây dựng một khung đánh giá khả năng chịu lỗi dành riêng cho hệ hỗ trợ quyết định, gồm ba
thành phần: một phân loại lỗi theo năm nhóm với ba mức độ nghiêm trọng, một cơ chế tiêm lỗi ở mức
*thành phần logic* cho phép áp cùng một kịch bản lỗi lên hai kiến trúc có cấu trúc hoàn toàn khác
nhau, và một bộ chỉ số lấy lượt chạy khỏe làm sự thật nền.

Thành phần thứ ba là điểm mà luận văn cho rằng có giá trị phương pháp cao nhất. Một chỉ số hỏng âm
thầm dựa trên tự báo cáo của hệ thống — nghĩa là hỏi hệ thống xem nó có gặp lỗi hay không — sẽ mù hoàn
toàn với chính loại lỗi mà nghiên cứu này quan tâm nhất, tức trường hợp một thành phần trả về kết quả
sai mà không tự biết mình sai. Lấy lượt chạy khỏe làm sự thật nền là cách rẻ nhất để có một tham chiếu
nằm bên ngoài hệ thống đang được đo.

### 1.6.2 Đóng góp về lý thuyết

Nghiên cứu rút ra bốn nguyên lý thiết kế, phát biểu theo cấu trúc do Gregor, Chandra Kuk và Hevner
(2020) đề xuất, gồm ba vế: *để* đạt mục tiêu nào, *hãy* dùng cơ chế gì, *bởi vì* lý thuyết nào biện
minh cho cơ chế đó. Bốn nguyên lý lần lượt bàn về việc gắn mức suy giảm vào từng quyết định, về việc
giữ đầu ra đa nhãn cùng điều kiện để cơ chế cạnh tranh sinh thêm thông tin, về quyền từ chối trả lời
của tác tử, và về việc dựng decision trace từ nhật ký thông điệp thật thay vì viết tay. Mỗi nguyên lý
được gắn với một cơ chế cưỡng chế trong mã nguồn và một thí nghiệm ablation, bởi một nguyên lý không
kiểm chứng được thì không phải là đóng góp.

Kèm theo bốn nguyên lý là một **construct mới**: mức suy giảm (`DegradationLevel`), biểu diễn độ tin
cậy của hệ thống tại thời điểm sinh ra quyết định. Văn liệu về hệ hỗ trợ quyết định bàn nhiều về khả
năng giải thích nhưng hầu như không có khái niệm này, và khoảng trống ấy có hệ quả thực tế: một quyết
định kèm lời giải thích đầy đủ vẫn có thể được sinh ra trên nền năng lực đã suy giảm mà lời giải thích
không hề đề cập tới điều đó.

### 1.6.3 Đóng góp về thực nghiệm

Kết quả thực nghiệm được báo cáo nguyên trạng, kể cả những kết quả bất lợi cho kiến trúc đề xuất. Kết
quả trung tâm liên quan tới tỷ lệ hỏng âm thầm dưới các nhóm lỗi khác nhau, và nó có thể phát biểu gọn
trong một câu.

> Ưu thế chịu lỗi của kiến trúc đa tác tử nằm trọn vẹn ở nhóm lỗi **không ném ngoại lệ**. Một lỗi biết
> phát tín hiệu thì kiến trúc nào cũng bắt được, và cơ chế xử lý ngoại lệ thông thường là đủ. Lỗi trả
> về giá trị hợp lệ nhưng sai mới là loại lỗi cần đến thang suy giảm và cơ chế kiểm tra đầu ra, và đó
> chính là phần mà kiến trúc đa tác tử đóng góp.

Phát biểu này hẹp hơn tuyên bố ban đầu của nghiên cứu, vốn cho rằng kiến trúc đa tác tử chịu lỗi tốt
hơn nói chung. Nhưng nó **mạnh hơn** ở chỗ nó nêu được cơ chế: nó nói ưu thế nằm ở đâu và vì sao, nên
nó có giá trị dự đoán cho những hệ thống khác. Số liệu chi tiết và quá trình đi đến phát biểu này được
trình bày ở [§5.2](ch5-ket-qua-ban-luan.md).

Bên cạnh đó, ba kết quả âm hoặc trung tính cũng được báo cáo: hai kiến trúc cho kết quả giống hệt nhau
ở khâu quy kết nguyên nhân, bộ giám sát không phát hiện được dịch chuyển phân phối ở cả ba mức nhiễu
loạn, và cơ chế bảo vệ không phủ được lỗi Byzantine trên chính những thành phần mà kiến trúc đa tác tử
tạo thêm.

### 1.6.4 Đóng góp về phản tư quy trình

Trong suốt quá trình nghiên cứu, một nhật ký lỗi phương pháp được duy trì, ghi lại **ba mươi bảy** lỗi
đã làm cho một kết luận trở nên sai hoặc vô nghĩa, kèm theo cơ chế đã phát hiện ra từng lỗi. Trong
Design Science, quá trình phát hiện và sửa lỗi thiết kế là một phần của đóng góp chứ không phải thứ
cần che giấu, bởi nó chính là bằng chứng cho thấy artifact đã trải qua đánh giá thực chất.

Ba trong số các lỗi này đáng được phân tích riêng vì chúng có cùng một hướng sai lệch: cả ba đều làm
cho artifact của chính nghiên cứu trông tốt hơn thực tế. Việc ba lỗi độc lập cùng lệch về một phía
không phải là ngẫu nhiên, và điều này được bàn ở [§5.6](ch5-ket-qua-ban-luan.md).

---

## 1.7 Cấu trúc của luận văn

Luận văn gồm sáu chương. Chương 1 trình bày bối cảnh, vấn đề, mục tiêu, câu hỏi nghiên cứu, phạm vi và
đóng góp. Chương 2 xây dựng cơ sở lý thuyết trên năm nhánh văn liệu — hệ đa tác tử, hệ hỗ trợ quyết
định, phục hồi dịch vụ, độ tin cậy và khả năng chịu lỗi, học máy trên dữ liệu mất cân bằng — cùng với
khung phương pháp Design Science, và kết thúc bằng việc xác định ba khoảng trống nghiên cứu. Chương 3
trình bày phương pháp: quy trình nghiên cứu, năm ràng buộc dữ liệu, kiến trúc hai mốc quyết định, cách
chia tập và ngăn rò rỉ, thao tác hóa ba câu hỏi, ba giả thuyết khai báo trước, và thiết kế thí nghiệm
chịu lỗi. Chương 4 mô tả sáu artifact đã được thiết kế và hiện thực hóa. Chương 5 trình bày kết quả,
trả lời ba câu hỏi nghiên cứu, phán quyết ba giả thuyết, và phản tư về quy trình. Chương 6 tổng kết
đóng góp, nêu hạn chế và hướng phát triển.

---

## 1.8 Một lưu ý về cách đọc luận văn này

Luận văn báo cáo ba kết quả âm hoặc trung tính ở vị trí nổi bật thay vì đặt chúng ở phần phụ lục. Đây
là một lựa chọn có chủ đích, và lý do của nó thuộc về phương pháp chứ không thuộc về phong cách trình
bày.

Kết quả thứ nhất — hai kiến trúc cho kết quả giống hệt nhau ở khâu quy kết nguyên nhân — giữ vai trò
**điều kiện kiểm soát**. Chính vì hai kiến trúc tương đương về độ chính xác nền mà mọi khác biệt quan
sát được dưới điều kiện lỗi mới có thể quy cho kiến trúc. Nói cách khác, kết quả âm này là thứ làm cho
claim nhân quả của nghiên cứu đáng tin hơn.

Kết quả thứ hai và thứ ba — bộ giám sát không phát hiện được dịch chuyển phân phối, và cơ chế bảo vệ
không phủ được lỗi Byzantine trên các thành phần riêng có — là **tri thức thiết kế**. Chúng chỉ ra
chính xác chỗ mà kiến trúc đề xuất chưa đủ, và một nghiên cứu chỉ báo cáo những kết quả thuận lợi
không thể cung cấp loại tri thức đó cho người đọc muốn xây dựng hệ thống tương tự.
