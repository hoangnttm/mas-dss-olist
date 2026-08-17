# CHƯƠNG 2 — CƠ SỞ LÝ THUYẾT VÀ TỔNG QUAN NGHIÊN CỨU

> **Ghi chú cho người viết — xóa trước khi nộp.** Các trích dẫn trong chương này nêu công trình nền của
> từng khái niệm, nhưng **thông tin thư mục đầy đủ chưa được đối chiếu với bản gốc**, và
> [tai-lieu-tham-khao.md](tai-lieu-tham-khao.md) hiện **còn trống**. Đây là một hạng mục còn mở, không
> phải một ghi chú trang trí: giữ khối này cho tới khi danh mục tài liệu tham khảo được viết và đối
> chiếu xong.

Chương này xây dựng cơ sở lý thuyết cho ba câu hỏi nghiên cứu đã nêu ở [§1.4](ch1-gioi-thieu.md).
Khác với một khảo sát văn liệu tổng quát, chương được tổ chức theo lập luận: mỗi nhánh văn liệu được
trình bày cùng với hệ quả cụ thể mà nó tạo ra đối với thiết kế của nghiên cứu này. Năm nhánh đầu cung
cấp nền khái niệm và kỹ thuật; nhánh thứ sáu cung cấp khung phương pháp; hai mục cuối đối chiếu với
các công trình liên quan và xác định khoảng trống mà luận văn nhắm tới.

---

## 2.1 Hệ đa tác tử

### 2.1.1 Tác tử và hệ đa tác tử

Một **tác tử** (agent) là một thực thể tính toán có khả năng tự chủ hành động trong một môi trường để
đạt mục tiêu được giao. Bốn thuộc tính thường được nêu trong định nghĩa là tính tự chủ, khả năng phản
ứng với môi trường, khả năng chủ động theo đuổi mục tiêu, và năng lực xã hội — tức khả năng giao tiếp
và phối hợp với các tác tử khác (Wooldridge). Một **hệ đa tác tử** là hệ gồm nhiều tác tử tương tác
với nhau, trong đó không tác tử nào có đủ thông tin hoặc năng lực để giải quyết toàn bộ bài toán một
mình.

Định nghĩa này dễ bị hiểu thành một cách gọi khác của việc phân rã chương trình theo mô-đun, và việc
phân biệt hai khái niệm có ý nghĩa trực tiếp với luận văn. Điểm khác biệt nằm ở ba chỗ. Thứ nhất là
**quyền quyết định**: trong phân rã theo mô-đun, bên gọi quyết định mô-đun nào chạy và chạy thế nào,
còn tác tử tự quyết định, kể cả quyết định không trả lời. Thứ hai là **bản chất của giao tiếp**:
mô-đun trao đổi qua lời gọi hàm, còn tác tử trao đổi qua thông điệp mang ngữ nghĩa — thông điệp không
chỉ chứa dữ liệu mà còn chứa ý định của bên gửi. Thứ ba là **cơ chế phối hợp**: mô-đun được ghép theo
một luồng điều khiển cố định, còn tác tử phối hợp qua các giao thức thương lượng.

Ba khác biệt này chính là ba cơ chế mà kiến trúc đề xuất trong luận văn khai thác. Quyền từ chối trả
lời trở thành nền tảng của nguyên lý *từ chối thay vì đoán*; thông điệp mang ngữ nghĩa trở thành nguồn
dữ liệu duy nhất để dựng lại chuỗi lập luận của một quyết định, tức nguyên lý *nguồn gốc từ giao
tiếp*. Cả hai nguyên lý được trình bày ở [§4.5](ch4-thiet-ke-hien-thuc.md).

### 2.1.2 Ngôn ngữ giao tiếp giữa các tác tử

Chuẩn FIPA-ACL định nghĩa một tập **performative** — loại hành vi ngôn ngữ mà một thông điệp thực
hiện, chẳng hạn thông báo, yêu cầu, đề xuất, hay từ chối. Điểm cốt lõi của chuẩn này là thông điệp
mang ý định chứ không chỉ mang dữ liệu: cùng một nội dung, một thông điệp *đề xuất* và một thông điệp
*thông báo* đòi hỏi bên nhận xử lý theo hai cách khác nhau.

Luận văn sử dụng mười performative, trong đó performative *từ chối* giữ vai trò trung tâm. Nó là cơ
chế biểu diễn mệnh đề *"tôi không đủ cơ sở để trả lời"* — một mệnh đề mà một lời gọi hàm trả về giá
trị không biểu diễn được nếu không quy ước thêm, chẳng hạn quy ước rằng giá trị rỗng hoặc giá trị âm
mang nghĩa từ chối. Vấn đề của các quy ước như vậy là chúng không được cưỡng chế: người viết mã ở phía
nhận có thể quên kiểm tra, và khi đó việc từ chối bị diễn giải thành một câu trả lời hợp lệ.

### 2.1.3 Contract Net Protocol

Contract Net Protocol (Smith, 1980) là giao thức phân bổ nhiệm vụ theo mô hình đấu thầu, gồm bốn pha:
bên điều phối thông báo nhiệm vụ, các tác tử gửi thầu, bên điều phối chọn thầu, và tác tử thắng thầu
thực hiện nhiệm vụ. Giao thức này phù hợp khi năng lực của các tác tử không đồng nhất và bên điều phối
không biết trước tác tử nào phù hợp nhất với một nhiệm vụ cụ thể.

Luận văn sử dụng một biến thể hai pha có bổ sung ràng buộc ngân sách tính toán: pha thứ nhất thăm dò
chi phí và độ tin cậy mà từng tác tử khai báo, pha thứ hai giải bài toán phân bổ dưới ràng buộc ngân
sách. Ràng buộc ngân sách là điểm khác so với giao thức gốc, và nó không phải một bổ sung tùy tiện —
nó xuất phát từ một yêu cầu thực tế của bài toán, đồng thời đã gây ra một lỗi thiết kế đáng chú ý được
phân tích ở [§4.3.4](ch4-thiet-ke-hien-thuc.md).

### 2.1.4 Kiến trúc blackboard

Mô hình blackboard sử dụng một không gian trạng thái dùng chung mà mọi tác tử đều đọc và ghi, thay cho
việc truyền trạng thái qua tham số giữa các lời gọi. Với luận văn này, ưu điểm quyết định của mô hình
là nó cho **một nguồn sự thật duy nhất** về trạng thái của phiên xử lý.

Tính chất đó không phải một tiện lợi kỹ thuật mà là điều kiện để kiểm chứng một thuộc tính: nếu trạng
thái được truyền ngầm qua tham số giữa các thành phần, sẽ tồn tại những bước xử lý không để lại dấu
vết nào trong nhật ký thông điệp, và khi đó tuyên bố *"chuỗi lập luận của quyết định có thể dựng lại
hoàn toàn từ nhật ký"* trở thành một tuyên bố không kiểm tra được.

---

## 2.2 Hệ hỗ trợ quyết định

### 2.2.1 Định nghĩa và phân loại

Hệ hỗ trợ quyết định (decision support system) là hệ thông tin hỗ trợ người ra quyết định trong các
bài toán bán cấu trúc hoặc phi cấu trúc — những bài toán mà thuật toán không thể thay thế hoàn toàn
phán đoán của con người. Phân loại kinh điển của Power chia các hệ này theo thành phần chi phối, gồm
năm nhóm: hướng dữ liệu, hướng mô hình, hướng tri thức, hướng tài liệu, và hướng giao tiếp. Hệ thống
được xây dựng trong luận văn thuộc nhóm lai giữa hướng dữ liệu — với một mô hình dự báo học từ dữ liệu
lịch sử — và hướng tri thức, với một tập luật nghiệp vụ quyết định hành động cuối cùng.

### 2.2.2 Hỗ trợ quyết định khác với tự động hóa quyết định

Sự phân biệt giữa *hỗ trợ* và *tự động hóa* thường được nêu như một khác biệt về mức độ can thiệp của
con người. Với luận văn này, nó có một hệ quả sâu hơn và trực tiếp lên thiết kế.

Một hệ tự động hóa được tối ưu cho việc **luôn có câu trả lời**: mọi đầu vào phải dẫn tới một đầu ra,
và việc không trả lời được coi là một dạng thất bại. Một hệ hỗ trợ quyết định thì được tối ưu cho một
mục tiêu khác — **người dùng biết khi nào nên tin câu trả lời**. Hai mục tiêu này không xung đột trong
điều kiện bình thường, nhưng chúng xung đột trực tiếp ở đúng tình huống mà luận văn quan tâm: khi hệ
thống đang suy giảm năng lực. Ở tình huống đó, mục tiêu thứ nhất đòi hệ thống tiếp tục trả lời, còn
mục tiêu thứ hai đòi hệ thống thừa nhận rằng câu trả lời của nó kém tin cậy hơn bình thường.

Từ đó rút ra một mệnh đề chi phối toàn bộ thiết kế của nghiên cứu: trong một hệ hỗ trợ quyết định, một
câu trả lời sai kèm vẻ tự tin gây hại hơn là không có câu trả lời. Mệnh đề này là biện minh lý thuyết
cho hai trong bốn nguyên lý thiết kế — nguyên lý *suy giảm minh bạch* và nguyên lý *từ chối thay vì
đoán* — được trình bày ở [§4.5](ch4-thiet-ke-hien-thuc.md).

### 2.2.3 Hệ hỗ trợ quyết định thông minh và hướng đa tác tử

Nhánh *intelligent decision support* đưa các kỹ thuật trí tuệ nhân tạo vào hệ hỗ trợ quyết định, còn
nhánh *agent-based decision support* sử dụng kiến trúc đa tác tử làm nền. Lập luận thường gặp cho lựa
chọn thứ hai là các tác tử có thể chuyên biệt hóa theo miền tri thức, phối hợp mềm dẻo hơn một luồng
xử lý cố định, và hệ thống dễ mở rộng khi bổ sung năng lực mới.

Điểm cần lưu ý về nhánh văn liệu này — và nó dẫn thẳng tới khoảng trống của luận văn — nằm ở **cách
giá trị của kiến trúc được chứng minh**. Phần lớn công trình chứng minh giá trị thông qua khả năng
biểu diễn: hệ thống mô hình hóa được bài toán, chạy được trên dữ liệu thật, và cho kết quả hợp lý. Một
số công trình bổ sung so sánh độ chính xác với một mô hình đơn lẻ. Rất ít công trình đo **hành vi của
kiến trúc dưới điều kiện lỗi**, tức trả lời câu hỏi điều gì xảy ra với quyết định cuối cùng khi một
tác tử hỏng.

Khoảng trống này đáng chú ý bởi vì chính khả năng chịu lỗi là một trong những lập luận thường được nêu
để biện minh cho kiến trúc đa tác tử. Nếu lập luận ấy được nêu mà không được đo, nó là một giả định
chứ không phải một kết quả.

---

## 2.3 Bất mãn khách hàng và phục hồi dịch vụ

### 2.3.1 Thất bại dịch vụ và phục hồi dịch vụ

Thất bại dịch vụ (service failure) là sự kiện dịch vụ không đạt kỳ vọng của khách hàng; phục hồi dịch
vụ (service recovery) là hành động của tổ chức nhằm khắc phục hậu quả và giữ lại quan hệ khách hàng.

Nghịch lý phục hồi (service recovery paradox) — nhận định rằng khách hàng trải qua một thất bại được
phục hồi tốt có thể có mức hài lòng cao hơn khách hàng chưa từng gặp thất bại (McCollough và
Bharadwaj) — là lập luận thường được dùng để biện minh cho đầu tư vào năng lực phục hồi. Văn liệu sau
đó cho thấy hiệu ứng này có điều kiện và không phổ quát; tuy nhiên mệnh đề yếu hơn, rằng phục hồi tốt
làm giảm đáng kể thiệt hại so với không phục hồi, thì được ủng hộ rộng rãi. Luận văn dựa trên mệnh đề
yếu hơn này, vốn đủ để biện minh cho bài toán và không đòi hỏi những điều kiện mà dữ liệu không cho
phép kiểm chứng.

### 2.3.2 Yếu tố thời điểm và biện minh cho kiến trúc hai mốc

Hiệu quả của phục hồi phụ thuộc mạnh vào thời điểm can thiệp. Can thiệp trước khi khách hàng công khai
bày tỏ bất mãn khác về bản chất với can thiệp sau đó: ở trường hợp thứ nhất, tổ chức đang xử lý một
**sự cố**; ở trường hợp thứ hai, tổ chức đang xử lý một **khiếu nại đã công khai**, với những ràng
buộc và kỳ vọng khác hẳn.

Sự phân biệt này là biện minh lý thuyết cho kiến trúc hai mốc quyết định của luận văn, trình bày ở
[§3.3](ch3-phuong-phap.md). Mốc thứ nhất, đặt trước khi đánh giá được viết, ứng với phục hồi **chủ
động** và dựa trên văn liệu về nhận diện sớm rủi ro. Mốc thứ hai, đặt khi đánh giá một hoặc hai sao đã
về, ứng với phục hồi **phản ứng**.

Một điểm cần nói rõ để tránh hiểu lầm: cách đóng khung bài toán như một bài toán *phục hồi dịch vụ*
không bị mất đi khi chuyển sang mốc thứ hai. Ngược lại, văn liệu về nghịch lý phục hồi bàn về việc
phục hồi *sau khi* khách hàng đã bày tỏ bất mãn, nên giai đoạn thứ hai khớp với lý thuyết ấy chặt hơn
giai đoạn thứ nhất.

### 2.3.3 Phân loại nguyên nhân bất mãn

Luận văn sử dụng hệ phân loại gồm ba nguyên nhân — giao hàng, chất lượng sản phẩm, chất lượng phục vụ
— cùng một nhãn *không xác định* dành cho những trường hợp bằng chứng không đủ để quy kết.

Một nhãn thứ tư, về **giá**, từng tồn tại trong các bản thiết kế trước và đã bị gỡ bỏ. Lý do không
phải vì nhãn ấy hiếm, mặc dù nó hiếm thật, mà vì nó đặt sai chỗ về mặt khái niệm. Khách hàng đã xác
nhận mua hàng, tức đã đồng ý với giá niêm yết và phí vận chuyển hiển thị tại thời điểm thanh toán. Một
lời phàn nàn *sau khi mua* vì vậy không thể là về giá; nó luôn là về một cơ chế khác đã hỏng — hoặc
phí vận chuyển không tương xứng với dịch vụ thực nhận, thuộc nhóm giao hàng, hoặc sản phẩm không xứng
với số tiền đã trả, thuộc nhóm chất lượng. Lập luận đầy đủ cùng bằng chứng kiểm chứng được trình bày ở
[§3.4.2](ch3-phuong-phap.md).

---

## 2.4 Độ tin cậy và khả năng chịu lỗi

### 2.4.1 Phân loại lỗi và ranh giới quyết định

Trong hệ phân tán, lỗi thường được phân loại theo mức độ khó xử lý tăng dần. **Lỗi dừng** khiến thành
phần ngừng hoạt động hoàn toàn và được phát hiện dễ dàng qua ngoại lệ hoặc qua việc mất tín hiệu. **Lỗi
bỏ sót hoặc lỗi thời gian** khiến thành phần không phản hồi hoặc phản hồi quá muộn, cũng được phát hiện
tương đối dễ qua cơ chế hết hạn chờ. **Lỗi Byzantine**, đặt tên theo bài toán *Byzantine Generals*
(Lamport, Shostak và Pease, 1982), là trường hợp thành phần trả về kết quả hợp lệ về hình thức nhưng
sai về nội dung; đây là loại khó phát hiện nhất bởi nó không để lại tín hiệu nào.

Ranh giới quan trọng nhất đối với luận văn không nằm ở ba tên gọi trên mà nằm ở một thuộc tính chung:
**hai loại đầu ném ngoại lệ, loại thứ ba thì không**. Toàn bộ kết quả thực nghiệm của nghiên cứu, như
sẽ thấy ở [§5.2](ch5-ket-qua-ban-luan.md), xoay quanh đúng ranh giới này. Điều đó không được dự đoán
từ đầu; nó là kết quả của việc phân loại lỗi theo cơ chế thay vì theo mức độ nghiêm trọng cảm tính.

### 2.4.2 Hỏng âm thầm

Hỏng âm thầm là trường hợp hệ thống cho ra kết quả sai mà không phát ra tín hiệu nào; nó là hệ quả vận
hành của lỗi Byzantine. Trong một dịch vụ kỹ thuật, hỏng âm thầm gây ra dữ liệu sai và thường được
phát hiện muộn qua đối soát với một nguồn độc lập.

Trong một hệ hỗ trợ quyết định, hậu quả nghiêm trọng hơn theo một cách riêng: người ra quyết định
không có cách nào biết rằng cơ sở của quyết định đã hỏng. Vấn đề không phải một quyết định sai đơn lẻ,
mà là việc mất khả năng phân biệt giữa quyết định đáng tin và quyết định không đáng tin — tức mất
chính thứ mà hệ hỗ trợ quyết định tồn tại để cung cấp.

Đây là lý do luận văn chọn tỷ lệ hỏng âm thầm làm chỉ số trung tâm, thay vì các chỉ số độ tin cậy
thông dụng hơn như tỷ lệ khả dụng hay thời gian phục hồi trung bình. Hai chỉ số sau đo *hệ thống có
chạy hay không*; chỉ số được chọn đo *khi hệ thống chạy sai, người dùng có biết hay không*.

### 2.4.3 Suy giảm có kiểm soát và cây giám sát

Suy giảm có kiểm soát (graceful degradation) là nguyên tắc thiết kế theo đó hệ thống, khi một phần
hỏng, tiếp tục vận hành ở mức năng lực thấp hơn thay vì dừng hẳn. Luận văn bổ sung vào nguyên tắc này
một yêu cầu mà bản gốc không nêu: **mức suy giảm phải quan sát được từ bên ngoài**.

Lý do của bổ sung này rút ra trực tiếp từ mục trước. Suy giảm mà người dùng không nhìn thấy chính là
hỏng âm thầm; một hệ thống suy giảm êm ái nhưng im lặng không tốt hơn một hệ thống suy giảm ồn ào, xét
theo tiêu chí của hệ hỗ trợ quyết định. Yêu cầu này được cụ thể hóa thành construct **mức suy giảm** và
thành nguyên lý *suy giảm minh bạch*, trình bày ở [§4.2.4](ch4-thiet-ke-hien-thuc.md) và
[§4.5.1](ch4-thiet-ke-hien-thuc.md).

Cây giám sát (supervision tree), mô hình quen thuộc trong hệ sinh thái Erlang/OTP, tổ chức các tiến
trình thành cấu trúc cây trong đó tiến trình cha chịu trách nhiệm giám sát và khởi động lại tiến trình
con theo một chiến lược khai báo trước. Luận văn mượn cấu trúc này cho tầng chịu lỗi của kiến trúc.

### 2.4.4 Chaos engineering

Chaos engineering là phương pháp đánh giá độ tin cậy bằng cách chủ động tiêm lỗi vào hệ thống và quan
sát hành vi, thay vì suy luận về độ tin cậy từ thiết kế. Bộ nguyên tắc nền, phát triển từ thực tiễn
vận hành tại Netflix, gồm bốn bước: xác định một trạng thái ổn định đo được, đưa ra giả thuyết rằng
trạng thái ấy được giữ nguyên dưới nhiễu loạn, tiêm nhiễu loạn phản ánh sự cố có thể xảy ra trong thực
tế, và giới hạn bán kính ảnh hưởng của thí nghiệm.

Phương pháp này đã được áp dụng rộng rãi cho hạ tầng và cho kiến trúc microservice. Việc áp dụng nó
cho một hệ hỗ trợ quyết định thì hiếm gặp, và đây là một trong hai khoảng trống mà luận văn nhắm tới.
Nguyên nhân của khoảng trống nằm ở bước đầu tiên trong bốn bước nêu trên: trong bối cảnh hạ tầng,
*trạng thái ổn định* thường được đo bằng tỷ lệ khả dụng hoặc tỷ lệ lỗi của yêu cầu, còn trong bối cảnh
hỗ trợ quyết định, trạng thái ổn định phải được định nghĩa theo **chất lượng và tính trung thực của
quyết định**. Định nghĩa lại đại lượng ấy là một phần công việc của luận văn, chứ không phải một chi
tiết áp dụng.

---

## 2.5 Học máy trên dữ liệu mất cân bằng

### 2.5.1 Giới hạn của các chỉ số tóm tắt đường cong

Với tỷ lệ lớp dương trong khoảng mười hai đến mười bảy phần trăm như trong bài toán này, chỉ số
ROC-AUC cho một con số trông khả quan hơn giá trị nghiệp vụ thực tế, bởi nó chuẩn hóa theo cả hai lớp
trong khi lớp âm áp đảo về số lượng. Chỉ số PR-AUC nhạy hơn với lớp thiểu số và được luận văn chọn làm
chỉ số chính.

Tuy nhiên, ngay cả PR-AUC cũng chưa đủ, và lý do có tính nguyên tắc chứ không phải kỹ thuật: cả hai
chỉ số đều tóm tắt **toàn bộ đường cong** thành một con số, trong khi một quyết định vận hành chỉ sử
dụng **một điểm** trên đường cong đó. Đội chăm sóc khách hàng không xử lý toàn bộ số đơn được xếp
hạng; họ xử lý một tỷ lệ nhất định ở đầu bảng, tương ứng với năng lực thực tế của họ. Một chỉ số tóm
tắt tốt nhưng có hình dạng đường cong bất lợi ở đúng vùng đó sẽ cho một kết luận sai lệch.

### 2.5.2 Ba thước đo bổ sung

Từ nhận định trên, luận văn bổ sung ba thước đo bên cạnh PR-AUC, mỗi thước đo trả lời một câu hỏi mà
chỉ số tóm tắt không trả lời được.

Thước đo thứ nhất là **precision@k**, trả lời câu hỏi: trong k phần trăm số đơn được xếp hạng cao nhất
— đúng bằng năng lực xử lý thực tế — có bao nhiêu đơn thực sự dẫn tới bất mãn. Đại lượng quan trọng
nhất trong bảng precision@k không phải bản thân độ chính xác mà là **hệ số lift**, tức tỷ số giữa độ
chính xác đạt được và tỷ lệ nền; lift bằng một nghĩa là việc xếp hạng không hơn gì việc rút ngẫu nhiên.

Thước đo thứ hai là **bảng hiệu chuẩn theo thập phân vị**, trả lời câu hỏi xác suất mà hệ thống báo ra
có khớp với tần suất thực tế hay không, và nếu lệch thì lệch ở nhóm nào. Một chỉ số hiệu chuẩn gộp
thành một con số duy nhất không cho biết mô hình sai ở đâu, trong khi vị trí của sai lệch có ý nghĩa
thực tế: lệch ở nhóm điểm cao nghiêm trọng hơn nhiều so với lệch ở nhóm điểm thấp, bởi nhóm điểm cao
chính là nhóm được đưa ra can thiệp.

Thước đo thứ ba là **đối chiếu với hằng số nền**, trả lời câu hỏi liệu mô hình có hơn được một mô hình
tầm thường chỉ trả về tỷ lệ nền cho mọi đơn hàng hay không. Đây là phép thử rẻ nhất trong ba thước đo
và cũng là phép thử hay bị bỏ qua nhất. Trên dữ liệu mất cân bằng, một mô hình có thể đạt điểm Brier
trông tốt mà vẫn thua một hằng số; nếu hai con số không được đặt cạnh nhau, bản thân điểm Brier không
nói lên điều gì. Kết quả thực tế của phép đối chiếu này trong luận văn, trình bày ở
[§5.3](ch5-ket-qua-ban-luan.md), là một minh họa trực tiếp cho nhận định vừa nêu.

### 2.5.3 Hiệu chuẩn xác suất

Hiệu chuẩn là yêu cầu rằng xác suất mà mô hình báo ra khớp với tần suất thực tế. Hai kỹ thuật phổ biến
là *Platt scaling* và **hồi quy đơn điệu** (isotonic regression, Zadrozny và Elkan); chỉ số thường
dùng để đánh giá là sai số hiệu chuẩn kỳ vọng.

Với một hệ hỗ trợ quyết định, hiệu chuẩn không phải một chi tiết kỹ thuật mà là điều kiện để đầu ra có
nghĩa. Nếu hệ thống báo rằng một đơn hàng có sáu mươi tám phần trăm khả năng bị đánh giá xấu, mà con
số ấy không tương ứng với tần suất thực tế, thì người ra quyết định không có cách nào dùng nó để cân
nhắc chi phí của hành động can thiệp.

Một tính chất của hồi quy đơn điệu có hệ quả trực tiếp lên kết quả của luận văn và cần được nêu trước:
phép biến đổi này **đơn điệu không giảm**. Do đó, đặt một ngưỡng trên điểm đã hiệu chuẩn tương đương
với việc đặt một ngưỡng khác trên điểm thô. Hệ quả là hai kiến trúc dùng chung một mô hình và chung
một ngưỡng vẫn cho kết quả giống hệt nhau sau khi hiệu chuẩn — hiệu chuẩn không phá được đẳng thức
được phân tích ở [§5.4](ch5-ket-qua-ban-luan.md).

### 2.5.4 Dự báo có chọn lọc

Dự báo có chọn lọc (selective prediction) cho phép mô hình từ chối trả lời trên phần dữ liệu mà nó
không đủ tự tin, và đánh giá hiệu năng bằng đường cong rủi ro theo độ phủ thay vì bằng một chỉ số đơn
lẻ ở độ phủ toàn phần.

Khái niệm này cần thiết cho luận văn vì một lý do đo lường cụ thể: chỉ số macro-F1 **phạt việc từ
chối**. Một tác tử phát tín hiệu từ chối bị tính là không trả lời đúng, nên nguyên lý *từ chối thay vì
đoán* sẽ tự trừ điểm chính nó nếu hiệu năng chỉ được đo bằng macro-F1. Đường cong rủi ro theo độ phủ
cho phép so sánh hai hệ ở cùng một mức độ phủ, tức so sánh công bằng giữa một hệ có quyền từ chối và
một hệ buộc phải trả lời.

### 2.5.5 Phát hiện dịch chuyển phân phối

Chỉ số ổn định tổng thể (population stability index) là công cụ thông dụng để đo mức dịch chuyển phân
phối giữa một tập tham chiếu và tập hiện hành. Quy ước thường gặp trong thực hành công nghiệp là các
ngưỡng 0,1 và 0,25.

Luận văn cho thấy quy ước ấy không dùng được trực tiếp trong bối cảnh này, bởi bản thân dữ liệu đã
chứa dịch chuyển thời gian tự nhiên đáng kể — tập dữ liệu trải dài từ 2016 đến 2018 và tỷ lệ nền của
biến mục tiêu giảm đơn điệu qua ba giai đoạn. Ngưỡng phải được hiệu chuẩn trên một lượt chạy khỏe thay
vì lấy theo quy ước; hậu quả của việc lấy theo quy ước, cùng bốn cái bẫy khác gặp phải trong quá trình
xây dựng bộ giám sát, được trình bày ở [§5.5](ch5-ket-qua-ban-luan.md).

---

## 2.6 Design Science Research

### 2.6.1 Khung phương pháp

Design Science Research là mô hình nghiên cứu trong đó tri thức được tạo ra thông qua việc xây dựng và
đánh giá artifact. Nó khác với nghiên cứu hành vi ở mục tiêu: không phải giải thích một hiện tượng
đang tồn tại, mà tạo ra một thứ chưa tồn tại và rút ra tri thức từ quá trình tạo ra nó. Bảy hướng dẫn
của Hevner và cộng sự — trong đó có yêu cầu artifact là sản phẩm bắt buộc, yêu cầu đánh giá nghiêm
ngặt, và yêu cầu đóng góp nghiên cứu phải rõ ràng — là khung nền của luận văn.

Bốn loại artifact được phân biệt trong khung này là construct, model, method và instantiation. Nghiên
cứu này tạo ra cả bốn loại, như trình bày ở Bảng 2.1.

**Bảng 2.1.** Bốn loại artifact và sản phẩm tương ứng của nghiên cứu

| Loại artifact | Sản phẩm trong luận văn |
|---|---|
| Construct | Mức suy giảm; ontology và tập performative |
| Model | Kiến trúc tham chiếu và bốn nguyên lý thiết kế |
| Method | Chaos harness — phương pháp đánh giá chịu lỗi cho hệ hỗ trợ quyết định; khung đánh giá và bốn kiến trúc đối chứng |
| Instantiation | Prototype vận hành trên dữ liệu Olist; bộ nhãn chuẩn do người gán |

Điều đáng lưu ý ở Bảng 2.1 là hàng thứ ba. Trong nhiều luận văn hướng hệ thống, đóng góp dừng ở hàng
cuối — một hiện thực chạy được. Hàng thứ ba, tức phương pháp, là loại artifact có khả năng tái sử dụng
cao nhất bởi nó không gắn với miền ứng dụng cụ thể.

### 2.6.2 Phân loại mức đóng góp tri thức

Gregor và Hevner (2013) phân biệt các mức đóng góp theo hai trục — độ trưởng thành của miền vấn đề và
độ trưởng thành của giải pháp — tạo thành bốn ô: *routine design*, *improvement*, *exaptation*, và
*invention*. Đóng góp của luận văn nằm chủ yếu ở ô **exaptation**: mở rộng những giải pháp đã biết ở
miền khác sang một miền vấn đề mới. Cụ thể, chaos engineering được mở rộng từ hạ tầng sang hệ hỗ trợ
quyết định, suy giảm có kiểm soát được mở rộng từ hệ phân tán, và cây giám sát được mượn từ hệ sinh
thái Erlang/OTP.

Cùng công trình này phân biệt hai loại tri thức: tri thức về giải pháp, mang tính quy phạm, ký hiệu là
Λ; và tri thức mô tả về hiện tượng, ký hiệu là Ω. Bốn nguyên lý thiết kế của luận văn thuộc loại Λ,
còn kết quả thực nghiệm về hành vi kiến trúc dưới điều kiện lỗi thuộc loại Ω.

Sự phân biệt này quyết định cấu trúc của luận văn. Nếu nghiên cứu chỉ tạo ra tri thức loại Ω — mô tả
một hệ thống đã xây và đo nó — thì công trình dừng ở mức một báo cáo kỹ thuật có đo đạc cẩn thận. Tầng
Λ, tương ứng với câu hỏi thiết kế, chính là thứ nâng nó lên thành nghiên cứu Design Science.

### 2.6.3 Cấu trúc phát biểu nguyên lý thiết kế

Gregor, Chandra Kuk và Hevner (2020) đề xuất một cấu trúc cho phát biểu nguyên lý thiết kế, gồm các
thành phần mục tiêu, ngữ cảnh, cơ chế và lý thuyết biện minh. Luận văn sử dụng dạng rút gọn ba vế:
*để* đạt mục tiêu nào, *hãy* dùng cơ chế gì, *bởi vì* lý thuyết nào biện minh.

Khuôn này không phải một quy ước hình thức. Ba vế buộc ba thành phần khác nhau phải cùng hiện diện, và
vế thứ ba là vế phân biệt một **nguyên lý thiết kế** với một **ghi chú cấu hình**. Một phát biểu dạng
*"hãy đặt trường mức suy giảm là bắt buộc"* mà không có vế biện minh thì chỉ là một quy ước lập trình;
cùng phát biểu ấy kèm lý do — rằng một quyết định tự động sinh ra trên nền năng lực đã suy giảm gây
hại hơn là không có quyết định — thì trở thành tri thức có thể chuyển giao sang bối cảnh khác.

### 2.6.4 Khung hiệu lực cho nghiên cứu thiết kế

Larsen và cộng sự (2025) đề xuất một khung phân loại hiệu lực cho nghiên cứu hệ thống thông tin, phân
biệt các loại claim và loại bằng chứng tương ứng. Luận văn sử dụng khung này không phải để phân loại
kết quả sau khi có, mà để **khai báo trước** loại bằng chứng mà mỗi câu hỏi nghiên cứu sẽ cung cấp và
sẽ không cung cấp; ánh xạ cụ thể đã trình bày ở Bảng 1.2.

Việc khai báo trước có một tác dụng phòng ngừa cụ thể: nó ngăn việc trình bày một kết quả thuộc loại
demonstration như thể nó là bằng chứng nhân quả. Trong các nghiên cứu hướng hệ thống, nhầm lẫn này khá
phổ biến và khó phát hiện sau khi đã xảy ra, bởi một hệ thống chạy tốt tự nó tạo cảm giác rằng thiết
kế của nó đã được chứng minh.

### 2.6.5 HARKing và kỷ luật khai báo trước

HARKing — viết tắt của *Hypothesizing After the Results are Known*, tức phát biểu hoặc sửa giả thuyết
sau khi đã biết kết quả rồi trình bày như thể nó có từ trước — làm mất đi đúng thứ mà việc khai báo
trước mua được: bằng chứng rằng nghiên cứu không đang chứng minh điều mình muốn tin.

Luận văn áp dụng một quy tắc ba tầng để phân biệt các loại mệnh đề, và điểm đáng chú ý là **hai loại
có quy tắc sửa đổi ngược nhau**. Ràng buộc dữ liệu được kiểm chứng bằng cách đọc lược đồ dữ liệu và
**được phép sửa** khi hiểu biết về dữ liệu thay đổi — nó là một sự thật về dữ liệu, không phải một dự
đoán. Giả thuyết được kiểm chứng bằng thí nghiệm và **không được phép sửa** sau khi thấy kết quả.
Nguyên lý thiết kế thì lại **được phép sửa**, và điều này nhìn qua có vẻ mâu thuẫn với quy tắc dành
cho giả thuyết.

Mâu thuẫn ấy chỉ là bề ngoài. Giả thuyết là một **dự đoán khai báo trước**, và giá trị của nó nằm ở
chỗ nó có thể sai; sửa nó sau khi biết kết quả sẽ xóa bỏ chính giá trị đó. Nguyên lý thiết kế thì là
**sản phẩm** của nghiên cứu — tri thức quy phạm được rút ra *từ* quá trình xây dựng và đo đạc — nên
việc tinh chỉnh nó theo bằng chứng chính là vòng lặp xây dựng–đánh giá của Design Science. Trong luận
văn, nguyên lý thứ hai đã được sửa sau thực nghiệm theo đúng cơ chế này, và quá trình sửa được ghi lại
nguyên vẹn ở [§4.5.2](ch4-thiet-ke-hien-thuc.md) thay vì bị xóa đi.

---

## 2.7 Các công trình liên quan trên bộ dữ liệu Olist

Bộ dữ liệu Olist được sử dụng rộng rãi trong các công trình phân tích và trong nhiều dự án mã nguồn
mở. Khảo sát hai hiện thực tham chiếu công khai cho thấy một mẫu hình chung trong cách đặt bài toán,
và mẫu hình ấy có ý nghĩa đối chiếu với luận văn.

Đặc điểm thứ nhất là bài toán được **đóng khung như một bài toán phân loại hài lòng hay không hài
lòng**. Cách đóng khung này dừng ở khâu dự báo, không có tầng quy kết nguyên nhân và không có tầng đề
xuất hành động. Đây là một lựa chọn hợp lý với mục tiêu phân tích mô tả, nhưng nó không tạo ra một hệ
hỗ trợ quyết định theo nghĩa đã định nghĩa ở §2.2.

Ba đặc điểm còn lại đáng chú ý hơn vì chúng đều là các dạng **rò rỉ theo mốc quyết định**. Cả hai hiện
thực đều lọc dữ liệu để chỉ giữ những đơn đã giao thành công, qua đó loại bỏ nhóm đơn quá hạn mà chưa
được giao — chính là nhóm có tỷ lệ bất mãn cao nhất trong toàn bộ dữ liệu. Cả hai đều sử dụng kết cục
giao hàng làm đặc trưng dự báo, trong khi thông tin này chỉ tồn tại sau khi giao xong, tức sau thời
điểm cần ra quyết định. Và cả hai đều không khai báo một mốc quyết định tường minh, nên không có cơ
chế nào phân biệt đặc trưng nào tồn tại tại thời điểm nào.

Việc chỉ ra ba đặc điểm trên không nhằm phê phán các dự án đó, vốn đặt ra mục tiêu khác với luận văn.
Mục đích là làm rõ một nhận định có ý nghĩa phương pháp: **các con số hiệu năng công bố trên bộ dữ
liệu Olist không so sánh trực tiếp được với nhau nếu mốc quyết định không được khai báo**. Luận văn xử
lý vấn đề này một cách tường minh ở [§3.3](ch3-phuong-phap.md), và bản thân nghiên cứu cũng đã mắc
đúng loại lỗi ấy hai lần trước khi phát hiện ra.

Về mặt đặc trưng, hai hiện thực tham chiếu đóng góp một số ý tưởng được luận văn tiếp thu, chủ yếu là
nhóm đặc trưng theo người bán: khoảng cách địa lý giữa người bán và người mua, hạn bàn giao cam kết,
và số đơn hàng trước đó của người bán. Đặc trưng cuối cùng được luận văn tính lại theo cách lũy tiến
theo thời gian thay vì đếm trên toàn tập, bởi cách đếm trên toàn tập sử dụng đơn hàng tương lai để dự
báo đơn hàng hiện tại — một dạng rò rỉ thời gian tinh vi mà tác động của nó được định lượng ở
[§5.3](ch5-ket-qua-ban-luan.md).

---

## 2.8 Khoảng trống nghiên cứu

Tổng hợp bảy mục trên, luận văn xác định ba khoảng trống nghiên cứu, sắp xếp theo mức độ trung tâm đối
với công trình.

**Khoảng trống thứ nhất là hành vi của kiến trúc hệ hỗ trợ quyết định dưới điều kiện lỗi.** Văn liệu
về hệ hỗ trợ quyết định hướng tác tử chứng minh giá trị kiến trúc chủ yếu bằng khả năng biểu diễn bài
toán và bằng độ chính xác trên đường chạy bình thường; rất ít công trình đo điều gì xảy ra khi một
thành phần hỏng, đặc biệt là hỏng theo kiểu không ném ngoại lệ. Chaos engineering có sẵn phương pháp
cho loại câu hỏi này nhưng được phát triển cho hạ tầng, nơi trạng thái ổn định được đo bằng tỷ lệ khả
dụng chứ không bằng tính trung thực của quyết định. Khoảng trống này dẫn tới **câu hỏi chịu lỗi**, và
phương pháp đánh giá tương ứng — chaos harness — là đóng góp phương pháp của luận văn.

**Khoảng trống thứ hai là sự thiếu vắng một construct biểu diễn độ tin cậy tại thời điểm ra quyết
định.** Văn liệu bàn nhiều về khả năng giải thích, nhưng một quyết định kèm lời giải thích đầy đủ vẫn
có thể được sinh ra trên nền năng lực đã suy giảm mà lời giải thích không hề nói tới điều đó. Giải
thích trả lời câu hỏi *quyết định này được rút ra thế nào*; nó không trả lời câu hỏi *hệ thống đang ở
tình trạng nào khi rút ra quyết định ấy*. Khoảng trống này dẫn tới **câu hỏi thiết kế**, tới construct
mức suy giảm, và tới bốn nguyên lý thiết kế.

**Khoảng trống thứ ba là việc các phép so sánh kiến trúc thường thiếu điều kiện kiểm soát.** Những so
sánh dạng *kiến trúc A tốt hơn kiến trúc B* thường không bảo đảm hai bên vận hành trên cùng một năng
lực nền. Khi điều kiện ấy không được bảo đảm, khác biệt quan sát được có thể đến từ mô hình, từ tập
đặc trưng, hoặc từ ngưỡng quyết định — chứ không nhất thiết từ kiến trúc. Khoảng trống này dẫn tới
**câu hỏi điều kiện kiểm soát**, và tới yêu cầu rằng kiến trúc đối chứng phải đầy đủ chức năng và
không bị làm yếu có chủ đích.

---

## 2.9 Tóm tắt chương

Chương này đã đặt nền lý thuyết cho ba câu hỏi nghiên cứu. Văn liệu về hệ đa tác tử cung cấp ba cơ chế
mà kiến trúc đề xuất khai thác: quyền tự chủ bao gồm quyền từ chối, thông điệp mang ngữ nghĩa, và giao
thức thương lượng. Văn liệu về hệ hỗ trợ quyết định đặt ra một ràng buộc mà hệ tự động hóa không có,
là người dùng phải biết khi nào nên tin câu trả lời. Văn liệu về phục hồi dịch vụ biện minh cho kiến
trúc hai mốc quyết định. Lý thuyết về độ tin cậy cung cấp phân loại lỗi Byzantine, và cùng với nó là
ranh giới *có ném ngoại lệ hay không* mà toàn bộ kết quả thực nghiệm của luận văn xoay quanh. Văn liệu
về học máy trên dữ liệu mất cân bằng cung cấp bộ chỉ số, đồng thời cảnh báo rằng một chỉ số đơn lẻ
không đủ. Cuối cùng, Design Science Research cung cấp khung phương pháp, phân loại mức đóng góp, cấu
trúc phát biểu nguyên lý, và kỷ luật khai báo trước.

Chương 3 trình bày cách các nền tảng này được chuyển thành một thiết kế nghiên cứu cụ thể, với các
ràng buộc, các phép đo và các giả thuyết được khai báo trước khi tiến hành thí nghiệm.
