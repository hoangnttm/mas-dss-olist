# Nhật ký lỗi phương pháp và kế hoạch cải tiến

> **Mục đích kép.** Đây vừa là hồ sơ kỹ thuật, vừa là **nguyên liệu trực tiếp cho hai mục của luận
> văn**: *Threats to Validity* (Chương 4) và phần **phản tư Design Science** (Chương 5). Trong DSR,
> quá trình phát hiện và sửa lỗi thiết kế **là một phần của đóng góp**, không phải thứ cần giấu.
>
> **Nguyên tắc ghi.** Chỉ ghi lỗi làm cho một kết luận **sai** hoặc **vô nghĩa**, không ghi lỗi cài
> đặt thông thường. Mỗi mục phải trả lời: triệu chứng là gì, nguyên nhân gốc, sửa thế nào, và **bài
> học tổng quát** rút ra được.
>
> ### ⚠️ Số hiệu RQ trong file này là **số hiệu ĐƯƠNG THỜI**, không đổi theo
>
> Ngày **12/08/2026** ba câu hỏi nghiên cứu được sắp xếp lại *(RQ1↔RQ3 hoán vị vòng)*. Các mục dưới
> đây **giữ nguyên văn** như lúc viết — đó là bản chất của một nhật ký. Khi đọc, tra bảng:
>
> | Trong file này | Nghĩa | Số hiệu hiện hành |
> |---|---|---|
> | RQ1 | thiết kế, truy vết được | **RQ2** |
> | RQ2 | quy kết nguyên nhân, so sánh độ chính xác | **RQ3** |
> | RQ3 | chịu lỗi, chi phí | **RQ1** |
>
> Tương tự với giả thuyết: bản trước có **H1–H5**, bản hiện hành có **H1–H3**. Ánh xạ đầy đủ ở
> [research-questions-objectives.md](research-questions-objectives.md) §3.1.

---

## Phần 1 — Bảng tổng hợp

**47 lỗi phương pháp**, phát hiện trong quá trình xây `src-v3/`, chạy ba vòng gán nhãn, và chạy
trọn chu trình đánh giá. Bảy mục cuối *(L23–L29)* lộ ra khi **chạy thật**, không phải khi đọc lại tài
liệu — đó là bằng chứng cho luận điểm ở Phần 3: chạy sớm trên dữ liệu thật có hiệu suất phát hiện cao
nhất trong các cơ chế đã dùng.

| # | Nhóm | Lỗi | Phát hiện bằng | Trạng thái |
|---|---|---|---|---|
| L01 | Vòng tròn | `action_cause_fit` đo hai file YAML do chính tác giả viết | Phản biện tài liệu | ✅ Bỏ chỉ số |
| L02 | Vòng tròn | `pipeline_completeness` — baseline *bị định nghĩa* bằng 0 | Phản biện tài liệu | ✅ Hạ xuống mô tả |
| L03 | Vòng tròn | Weak label vừa huấn luyện vừa chấm điểm | Phản biện tài liệu | ✅ Hai kiểu dữ liệu tách biệt |
| L04 | In-sample | **ECE sau hiệu chuẩn = 0,0000** vì đo trên chính tập đã khớp isotonic | Nhìn con số quá đẹp | ✅ Báo cáo trên test |
| L05 | Baseline | Monolithic **đơn nhãn + argmax** → MAS thắng tình huống (a) theo cấu tạo | Phản biện tài liệu | ✅ Đổi sang đa nhãn |
| L06 | Chỉ số | Macro-F1 **phạt việc `REFUSE`** → DP3 tự trừ điểm chính nó | Suy luận về tầng B | ✅ Thêm selective prediction |
| L07 | Chỉ số | Silent failure định nghĩa theo **tự báo cáo** → mù với Byzantine | Chạy chaos, số vô lý | ✅ Dựa vào sự thật nền |
| L08 | Thiết kế | Cổng `risk >= MEDIUM` chặn quy kết ở T₄ → **94,7% case không được phân tích** | Chạy trên dữ liệu thật | ✅ Bỏ cổng |
| L09 | Thiết kế | T₃ đơn lẻ mâu thuẫn với việc dùng bằng chứng văn bản | Đọc lại ràng buộc C4 | ✅ Tách hai mốc T₃/T₄ |
| L10 | Thiết kế | Luật cho `no_action` dù **đã tìm ra nguyên nhân** | Chạy trên dữ liệu thật | ✅ Thêm `n_causes == 0` |
| L11 | Thiết kế | `Decision` thiếu bất biến *escalate ⟹ human review* | Đọc output lát cắt dọc | ✅ Bổ sung bất biến |
| L12 | So sánh | Kịch bản lỗi phát biểu theo `agent_id` → **không áp được lên Monolithic** | Số 0% đáng ngờ | ✅ Định danh thành phần |
| L13 | Giám sát | Cảnh báo chỉ phát **một lần** → 299 case sau hỏng y nguyên | Silent failure chỉ giảm 0,3% | ✅ Tách cảnh báo / trạng thái |
| L14 | Giám sát | Phương sai 0 coi là bằng chứng hỏng → **93,7% báo động giả** | Chạy lượt khỏe | ✅ Yêu cầu tiền đề tham chiếu |
| L15 | Thống kê | Tham chiếu PSI lấy **sai tổng thể** → PSI 0,807 trên dữ liệu khỏe | Đo trực tiếp hai phân phối | ✅ Khớp tổng thể |
| L16 | Thống kê | PSI **cửa sổ nhỏ + khoảng cố định** → PSI 2,911 trên dữ liệu khỏe | Đo trực tiếp hai phân phối | ✅ Phân vị + ≥100 mẫu |
| L17 | Thống kê | Ngưỡng PSI lấy theo **quy ước 0,25** → 66% báo động giả | Chạy lượt khỏe | ✅ Hiệu chuẩn từ dữ liệu |
| L18 | Kiến trúc | `runtime/` import `chaos/` — vi phạm phân tầng | Test tự động | ✅ Chuyển sang `core/` |
| **L19** | **Thống kê** | **Nghịch lý kappa: lấy trung bình κ qua các nhãn có tần suất chênh lệch cực lớn** → κ tổng 0,436 thay vì 0,547, và chỉ sai địa chỉ vấn đề | Đọc κ theo từng nhãn | ✅ Loại nhãn quá hiếm khỏi trung bình |
| **L20** | **Thiết kế thí nghiệm** | **Suýt cho hiện nhãn vòng một trong tệp gán lại** → κ vòng hai sẽ bị thổi phồng giả tạo | Rà lại trước khi sinh tệp | ✅ Tệp gán lại để mù |
| **L21** | **Chỉ số** | **Hỏng âm thầm định nghĩa lần hai vẫn sai**: đếm cả trường hợp lỗi làm hệ **chậm** chứ không làm **sai** → Monolithic bị báo 28,5% dưới `hang` trong khi mọi quyết định vẫn đúng | Chạy đủ 5 nhóm lỗi | ✅ So với đường chạy khỏe |
| **L22** | **Độ tin cậy vs độ đúng** | **Đồng thuận giữa hai người che giấu sai sót CHUNG**: 23,7% dòng tầng A được cả hai cùng gán `unknown`, ~60% trong số đó có nguyên nhân nêu tường minh | Đọc chính văn bản của các dòng đã đồng thuận | 🟡 Đang sửa bằng vòng 3 trên bản dịch |
| **L23** | **Nguồn dữ liệu** | **Đọc số đo từ chuỗi đã làm tròn để hiển thị** → điều kiện kiểm soát H1 báo lệch +0,000014 trên hai dãy giống hệt nhau | Chạy `run_evaluation` lần đầu | ✅ Thêm trường số thô `SimpleResult.score` |
| **L24** | **Sai lệch có hướng** | **Bộ đếm dòng mã hụt ~26%, hụt đúng theo hướng làm artifact trông rẻ hơn** — và `max(code, 0)` biến lỗi thành số 0 im lặng | Viết test cho bộ đếm | ✅ Dùng `lineno`/`end_lineno` của AST |
| **L25** | **Độ tin cậy vs độ đúng** | **Tôi lặp lại đúng L22**: lấy *"đồng thuận tuyệt đối 0/150"* làm lý do miễn kiểm tra tầng B, trong khi 43/150 dòng thỏa Quy tắc 6 mà không dòng nào được gán `delivery` | Rà artifact theo RQ/MT | ✅ Rút lại khẳng định ở 3 nơi; Quy tắc 6 chờ quyết định |
| **L26** | **Giả định của chỉ số** | **κ = 0,957 không đo gì** — hai tệp có cùng nguồn (ghi chú trùng 96,4%), nên giả định *"hai người đo độc lập"* của κ sai | Kiểm tra các cột tự do trước khi tin κ | ✅ `check_validation` kiểm tính độc lập TRƯỚC khi tính κ |
| **L27** | **Baseline / thiết kế** | **Hai kiến trúc giống hệt nhau — 0/250 đơn khác biệt**, vì các tác tử *phân chia* không gian nhãn thay vì *tranh chấp* nó · kèm ngân sách chưa hiệu chỉnh làm cổng rủi ro quay lại một cách ngầm | Chạy trọn chu trình T10.2 | ✅ Sửa **DP2** kèm điều kiện biên; ngân sách đặt theo bội số chi phí |
| **L28** | **Cơ chế an toàn** | **Cờ `citable` không truyền được** — nguồn gốc đọc từ đường dẫn đặt cứng, bỏ qua `--gold`; sai được theo **cả hai chiều** mà không để lại dấu hiệu | **Diễn tập** toàn chuỗi ở trạng thái `human_independent` | ✅ `meta_path()` bám theo tên tệp; dừng hẳn nếu thiếu meta |
| **L29** | **Thao tác hóa** | **Hai trong năm giả thuyết chứa mệnh đề không kiểm định được như đã viết**: H2 *"nhóm không có bình luận"* (không có sự thật nền) và H4 *"quá ngưỡng"* (ngưỡng chưa từng đặt) | Chốt phán quyết cho năm giả thuyết | ✅ Rà ba câu hỏi cho mỗi mệnh đề; giữ **nguyên văn** phát biểu |
| **L30** | **Mốc quyết định** | **T₃ hiểu là SỰ KIỆN thay vì MỐC THỜI GIAN** — 2.841 đơn chưa từng giao (77,9% bất mãn) khiến mô hình học *"thiếu ngày giao ⟹ rủi ro cao"*; PR-AUC 0,3993 → 0,2883 khi bỏ nhóm đó | Người hướng dẫn chỉ ra đơn quá hạn chưa giao mới là ca cần can thiệp | ✅ T₃ = hạn dự kiến + 3 ngày; `delivery_state` ba mức; đặc trưng kết cục chuyển sang T₄ |
| **L31** | **Rò rỉ thời gian** | **`seller_popularity` đếm trên toàn tập** dùng đơn tương lai để dự báo đơn hiện tại — thổi phồng PR-AUC +0,005 | Dựng hai bản rồi đo chênh lệch | ✅ Đếm lũy tiến theo thời gian; test canh |
| **L32** | **Hệ phân loại** | **`cause_price` là triệu chứng, không phải nguyên nhân** — khách đã đồng ý giá lúc mua, nên 10/12 dòng thực ra than về phí vận chuyển; 2 dòng nói rõ hàng vẫn tốt | Đọc cả 12 dòng thay vì chỉ nhìn cỡ mẫu | ✅ Gỡ `price`, định tuyến ba nhánh theo cơ chế hỏng (Quy tắc 7) |
| **L33** | **Mốc quyết định** | **T₃ đặt SAU T₄ với 97,6% số đơn** — *hạn dự kiến + 3* rơi vào sau lúc khách đã viết đánh giá, nên "dự báo" thực chất chạy sau kết cục nó dự báo. Mọi số ở L30 đo trên mốc này | Phân tích phân bố thời điểm review so với ba mốc | 🕐 T₃ = **ngày mua + 7**; toàn bộ số phải đo lại |
| **L34** | **Thao tác trên artifact** | **Tôi làm hỏng `status-checklist.md`**: chuỗi `.replace()` nối tiếp bắt lại chính chuỗi nó vừa tạo, gộp cả 40 tham chiếu MT/RQ về một giá trị. Không có VCS để hoàn tác | Bất biến số đếm chạy ngay sau phép đổi | ✅ Phục hồi từ bản grep trước đó; đổi sang `re.sub` một lượt |
| **L35** | **Biện minh không khớp phép đo** | **Con số biện minh cho mốc T₃ sai theo hai vế**: C3 viết *"lift đạt đỉnh 2,19"* tại mua+7, nhưng đo lại cho **2,12**, và lift **không** đạt đỉnh ở đó — nó còn tăng tới **2,39** ở mốc +10 | Đo lại toàn dải trước khi trích vào tài liệu | ✅ Thay bằng bảng đánh đổi đầy đủ; phát biểu lại lý do chọn |
| **L36** | **Phép thử rỗng** | **Kịch bản Byzantine trên bề mặt chỉ-MAS không tiêm được gì**: bộ tiêm gắn cứng trường `risk_score`, mà 5 thành phần đó không phát ra trường này — `_poison` gặp trường thiếu thì trả về nguyên kết quả. Bảng cho `mas_changed = 0,0%`, trông như bằng chứng chịu lỗi | `mas_changed = 0,0%` **cùng lúc** `mas_degraded = 0,0%` — lỗi thật luôn để lại một trong hai | ✅ `ByzantineByComponent` đầu độc đúng trường từng thành phần phát ra |
| **L37** | **Đối chứng bị thiệt** | **Kiến trúc đơn khối bị tính là "hỏng âm thầm" ngay cả khi nó CÓ báo lỗi**: phép đếm coi mọi đầu ra bị đổi là âm thầm, bỏ qua trường `failed_steps` mà nó điền đầy đủ khi một bước raise. Dưới `crash`, **100%** số ca đổi đầu ra đều có cờ này | Đối chiếu `failed_steps` với danh sách ca đổi đầu ra | ✅ `_mono_warned()`; ưu thế của MAS thu hẹp về nhóm lỗi **không raise** |
| **L38** | **Đường risk–coverage cắt sai trục** | **`selective_curve.csv` không phải đường risk–coverage**: phép cắt mức phủ dùng **thứ tự dòng trong DataFrame** thay vì độ tin cậy, mà khung đã `sort_index()` theo `order_id` — tức cắt **ngẫu nhiên có hệ thống**. Bug sống sót vì nó không bao giờ kêu lên: tệp vẫn được sinh ra và vẫn đọc được như một đường cong | Ví dụ dựng tay có độ tin cậy và thứ tự dòng đi **ngược** nhau: F1 ở mức phủ thấp phải **cao hơn** ở mức phủ đầy đủ, nhưng nó thấp hơn | ✅ Xếp hạng theo độ tin cậy giảm dần; thiếu cột `confidence` nay là **lỗi dừng hẳn** |
| **L39** | **Số không tái lập được** | **Hai con số phán quyết H1 chỉ tồn tại trong văn bản**: McNemar *(n = 6, p = 0,219)* và KTC bootstrap cho chênh lệch macro-F1 được báo cáo trong tài liệu nhưng **không hàm nào trong `src-v3/` tính chúng** — vi phạm chính hợp đồng *"không con số nào được gõ tay"* | Rà từng con số trong tài liệu ngược về lệnh sinh ra nó | ✅ `mcnemar_exact()` + `bootstrap_macro_f1_diff()`; xuất `attribution_compare.csv` |
| **L40** | **Hai cài đặt cùng tên, khác hành vi** | **Hai hàm `expected_calibration_error` khác nhau ở biên**: bản trong `risk_model.py` dùng `(p > low) & (p <= high)` cho mọi bin nên điểm bằng **đúng 0,0** rơi ra ngoài **mọi** bin và bị bỏ qua im lặng; bản trong `calibration.py` xử lý riêng bin đầu. Cùng tên, cùng mục đích, khác kết quả | So sánh hai cài đặt cùng tên khi rà tầng đo | ✅ Một cài đặt duy nhất; bản kia chuyển tiếp sang |
| **L41** | **Sửa L37 chỉ áp một nơi** | **Hai định nghĩa "hỏng âm thầm" cùng tồn tại trong mã**: `chaos/runner.py` đã áp bản sửa L37, nhưng `evaluation/resilience.py` — vốn in ra màn hình mỗi lần `run_system --inject` — **vẫn đếm theo bản cũ**, bỏ qua `failed_steps`. Hai nơi cho hai con số khác nhau trên cùng một lần chạy | Đọc lại **mọi** nơi cài cùng một khái niệm khi sửa một nơi | ✅ Áp L37 vào cả hai; gắn biển rõ bản nào sinh số Chương 5 |
| **L42** | **"Không khai báo" ≠ "bằng không"** | Khi gỡ ràng buộc ngân sách khỏi cấu hình báo cáo, bước đấu thầu không còn hàm `budget`, nên `bb.budget_ms_left` giữ **mặc định 0,0** và `allocate()` đi vào nhánh *"không đủ tài nguyên"* — **từ chối toàn bộ** analyst. Kết quả: **0%** case được quy kết, mà giao thức vẫn chạy đủ hai pha nên không có dấu hiệu bất thường | Bất biến trên **đầu ra** *(≥20% case qua đấu thầu — IMP-2)* bắt được ngay | ✅ `budget_ms=None` nghĩa **không ràng buộc**; test canh phân biệt hai trạng thái |
| **L43** | **Tiêm lỗi không cân xứng giữa hai kiến trúc** | **Lỗi Byzantine không tới được đường quyết định của MAS-DSS**: `PredictionAgent` phát ra cả `risk_score` *(nguồn)* lẫn `risk` *(dẫn xuất)*, bộ tiêm chỉ đầu độc `risk_score`, còn quyết định lại đọc `risk`. Với đơn khối, `guard_call` bọc một hàm trả về **số trần** nên đầu độc thay cả giá trị. Đo trên 200 case, `byz_gross_k2`, tầng chịu lỗi TẮT: mức rủi ro của MAS **y hệt đường khỏe** *(122/50/28)*, của đơn khối **200× HIGH**. Nghĩa là *"MAS hỏng âm thầm 0,0%"* ở nhóm byzantine **không đo khả năng chịu lỗi** — nó phản ánh **chỗ đặt bộ tiêm** | Ablation DP1 cho `quyết_định_đổi = 0` khi **tắt** tầng chịu lỗi — một lỗi thật không thể để đầu ra y nguyên | ✅ Thông điệp mang theo `risk_thresholds`; `_recompute_derived()` suy lại mức sau khi nguồn bị đầu độc; test parity canh **cả hai** đường quyết định |

| **L44** | **Chú thích mã nguồn giữ lại một khẳng định đã bị bác bỏ** | Chương 3 sửa bảng đánh đổi mốc T₃ theo phép đo toàn dải *(L35)*, nhưng khối chú thích ở `config.py` **vẫn ghi nguyên** *"+7 · lift 2,19 · đạt đỉnh"* và *"+10 · lift 2,11"* — sai cả ba con số so với Bảng 3.5 *(2,12 và 2,39)*. Chú thích ấy là nơi một phụ lục kỹ thuật sẽ trích, nên nó suýt đưa khẳng định đã bị bác bỏ trở lại luận văn | Rà chú thích mã nguồn khi viết tài liệu trích từ chính chú thích đó | ✅ Viết lại khối chú thích theo Bảng 3.5, ghi rõ +7 **không** phải mốc lift cao nhất |
| **L45** | **Sửa một cài đặt mà không sinh lại số phụ thuộc nó** | Sau khi hợp nhất hai cài đặt ECE *(L40)*, giá trị đúng đổi từ **0,0283** thành **0,028** — điểm bằng đúng 0,0 trước đây rơi ra ngoài mọi bin và bị bỏ qua. Nhưng `train` không được chạy lại ngay, nên ba tài liệu vẫn trích số cũ. Bước đối chiếu chéo *(mọi con số ngược về tệp nguồn)* bắt được | Sau khi sửa một hàm tính, **chạy lại mọi lệnh sinh số phụ thuộc nó**, không chỉ lệnh gần nhất | ✅ Chạy lại `train`, sửa số ở ch5, sổ tay đánh giá, phụ lục và session-state |

| **L46** | **Hai vế của một phép so sánh được đo bằng hai cơ sở khác nhau** | Hàng *"thời gian xử lý mỗi case"* ở Bảng 5.24 so **`sum(span.duration_ms)`** của MAS-DSS với **wall-clock** của vòng lặp baseline. Hai vế không cùng cơ sở, và **cả hai sai lệch đều có lợi cho MAS**: *(a)* span chỉ tính thời gian **bên trong** các lời gọi capability, bỏ qua glue điều phối và **toàn bộ phần ghi nhật ký**, nên **hạ thấp** chi phí MAS; *(b)* đồng hồ baseline ôm trọn **ba** baseline *(`mis`, `single_ml`, `monolithic`)* cộng phần `json.dumps`, nên **nâng cao** chi phí đối chứng. Kết quả công bố *"10,96 so với 10,82 ms — chênh +10,5 giây mỗi lô"* vì vậy **không phải một phép so sánh**. Đo lại đúng cách trên bốn lượt chạy: MAS **115–130 ms/case**, đơn khối **6,8–9,2 ms/case** — chênh **12,5–17,9 lần**, không phải 1,3% | Rà lại `coordination.csv` sau khi phát hiện nó được tính từ lượt chạy `stage2` *(còn **bật** ngân sách)*, tức nó mâu thuẫn với chính cấu hình được báo cáo | ✅ Cả hai vế đo bằng wall-clock trong cùng tiến trình trên cùng tập case; đồng hồ baseline chỉ ôm `mono.run`; `sum_span` giữ lại nhưng hạ xuống vai **chặn dưới mô tả**; sinh lại `cost_*.csv` và `coordination.csv` từ lượt chạy đúng cấu hình; viết lại §5.9 |
| **L47** | **Một artifact báo cáo được tính từ lượt chạy sai cấu hình** | `coordination.csv` — nguồn của Bảng 5.20 — được tính từ `data/v3/runs/stage2`, một lượt chạy **bật ràng buộc ngân sách** *(`budget_ms = 1,74`, phát **223** `REJECT_PROPOSAL`, chỉ trao **677/900** thầu)*. Nhưng §5.7.8 lại khẳng định *"tỷ lệ bị loại 0,0%"* dựa trên báo cáo độ tin cậy của lượt chạy **tắt** ngân sách. Hai bảng cạnh nhau trong cùng một chương mô tả **hai cấu hình khác nhau** | Đối chiếu chéo khi viết §5.7: số của Bảng 5.20 *(19,38 tin/case)* không khớp nhật ký goldset *(21,30)*, buộc phải truy nguồn | ✅ Sinh lại từ `stage2_nobudget`; ghi rõ lượt chạy nguồn trong sổ tay đánh giá |

> **L46/L47 là bản lặp lại thứ tư và thứ năm của cùng một cơ chế** — L36 *(bộ tiêm không chạm được
> thành phần)*, L37 *(đối chứng bị thiệt trong phép đếm)*, L43 *(bộ tiêm chạm được nhưng không tới
> đường quyết định)*, nay L46 *(hai vế đo bằng hai cơ sở)* và L47 *(artifact tính từ lượt chạy sai cấu
> hình)*. **Cả năm đều nghiêng về phía có lợi cho artifact của chính nghiên cứu**, và không lỗi nào làm
> chương trình đổ. Bài học chung, phát biểu ở dạng tổng quát nhất: **trong một phép so sánh giữa hai
> kiến trúc, mọi thứ không được phát biểu tường minh sẽ trôi về phía có lợi cho artifact.** Ba điều
> phải phát biểu tường minh và kiểm bằng test: nhiễu loạn tới được đúng đại lượng mà **cả hai** dùng để
> quyết định *(L36/L37/L43)*; hai vế đo bằng **cùng một cơ sở** *(L46)*; artifact báo cáo sinh từ
> **đúng cấu hình** được công bố *(L47)*.

**Bốn lỗi test** (không tính vào 47 lỗi trên vì chúng làm sai *phép đo*, không sai *hệ thống*):

| # | Lỗi | Hậu quả |
|---|---|---|
| T01 | Test quét **văn bản thô**, bắt phải comment nhắc tới `uuid4` / `chaos` | Báo động giả, che mất vi phạm thật |
| T02 | Test **pass vì lý do sai** — tự `raise` ở cuối khối `pytest.raises` | Guard hỏng mà test vẫn xanh |
| T03 | Test nạp lại toàn bộ dữ liệu và huấn luyện lại mỗi lần | Suite chạy >2 phút → mất thói quen chạy thường xuyên |
| **T04** | **Test "lượt chạy khỏe phải im lặng" chạy trên 25 case, trong khi PSI cần ≥100 quan sát** | **Phép thử rỗng — xanh vì phép đo không chạy, không phải vì hệ thống đúng** |

---

## Phần 2 — Chi tiết theo nhóm

### 2.1 Nhóm vòng tròn — đo lại chính thứ mình đã thiết kế

**L01–L03.** Cả ba cùng một hình dạng: hệ thống được chấm điểm bằng một thước đo do chính nó sinh ra.
`action_cause_fit` so bảng ánh xạ nguyên nhân→hành động (tác giả viết) với tập luật sinh hành động (tác
giả viết) — nó chỉ nói *"hai file YAML tôi viết có nhất quán với nhau không"*. `pipeline_completeness`
đo một năng lực mà baseline *bị định nghĩa* là không có. Weak label vừa dùng huấn luyện vừa dùng chấm
điểm.

> **Bài học.** Trước khi tin một chỉ số, hỏi: *"kết quả nào của chỉ số này sẽ khiến tôi kết luận thiết
> kế của mình sai?"* Nếu không có câu trả lời, chỉ số đó không đo gì cả.

**Cơ chế phòng ngừa đã cài:** `evaluation/attribution.py` chỉ nhận `GoldLabels`; truyền `WeakLabels`
vào phát `WeakLabelInEvaluation`. Ràng buộc ở tầng **kiểu dữ liệu**, không phó mặc kỷ luật cá nhân.

### 2.2 Nhóm in-sample — đo trên chính tập đã dùng để khớp

**L04.** Bộ hiệu chuẩn isotonic được khớp trên tập validation, rồi ECE sau hiệu chuẩn cũng được đo trên
tập validation → **0,0000**. Con số đó không phải thành tích, nó là hệ quả tất yếu của phép khớp. Số
thật trên tập test: **0,0133 → 0,0072**.

> **Bài học.** Một con số *quá đẹp* là tín hiệu đáng ngờ mạnh hơn một con số xấu. Phản xạ đúng khi thấy
> 0,0000 là hỏi *"tôi đã đo trên tập nào?"* chứ không phải ghi nó vào báo cáo.

**Cơ chế phòng ngừa đã cài:** `CalibrationReport` có trường `in_sample`, và tên chỉ số bị gắn nhãn
`[IN-SAMPLE — không dùng để báo cáo]` khi in ra.

### 2.3 Nhóm baseline không công bằng

**L05.** Đối chứng bị chặn ở đơn nhãn + `argmax`, trong khi MAS-DSS trả đa nhãn. Ở tình huống (a) của
RQ2 — đơn có nhiều nguyên nhân — MAS-DSS **thắng theo cấu tạo**, không phải theo năng lực. Đó đúng là
lỗi "baseline bù nhìn" mà nghiên cứu đã cam kết tránh.

> **Bài học.** Phép so sánh phải cô lập đúng **một** biến. Ở đây biến cần đo là *cách tổ chức*; nếu
> hình dạng đầu ra cũng khác thì không quy được kết quả cho biến nào.

**Cơ chế phòng ngừa đã cài:** `test_baseline_parity` so sánh **định danh đối tượng** (`is`), không so
giá trị — baseline và MAS-DSS phải nhận đúng cùng một đối tượng capability.

### 2.4 Nhóm định nghĩa chỉ số

**L06.** Macro-F1 tính recall trên mọi case. Ở tầng B, MAS-DSS phát `REFUSE` — hành vi **đúng** về mặt
tri thức luận — nhưng recall tiến về 0 và nó thua theo cấu tạo. Chỉ số đang **phạt đúng thứ thiết kế
sinh ra để làm**.

**L07.** Silent failure định nghĩa là *"có bước tự báo cáo thất bại nhưng vẫn ra quyết định"*. Lỗi
Byzantine không raise exception nào — đó chính là lý do nó nguy hiểm. Đo bằng cách hỏi hệ thống *"anh
có hỏng không"* thì một hệ hỏng âm thầm sẽ luôn trả lời *"không"*.

> **Bài học.** Chỉ số phải đo được thứ mà **đối tượng đo không tự khai báo**. Với thí nghiệm tiêm lỗi,
> luôn có sẵn sự thật nền — ta *biết* đã tiêm vào đâu, vì chính ta tiêm. Dùng nó.

### 2.5 Nhóm thiết kế lộ ra khi chạy dữ liệu thật

**L08** là nghiêm trọng nhất. Kế hoạch giai đoạn 2 chỉ mở phiên đấu thầu khi `risk >= MEDIUM`. Nhưng ở
T₄ đơn **đã có** đánh giá 1–2★ — bất mãn là sự kiện đã xảy ra, không còn cần dự báo. Chặn quy kết sau
một dự báo PR-AUC 0,40 khiến **94,7% case không bao giờ được phân tích**, và RQ2 mất đối tượng nghiên
cứu. Trên giấy nó trông hợp lý; chỉ khi chạy mới thấy.

**L10** cùng gốc: luật `low_risk_default` chỉ ràng buộc `risk == 0`, nên một đơn có nguyên nhân giao
hàng rõ ràng nhưng điểm rủi ro thấp lại rơi vào `no_action` — vô lý ở T₄.

> **Bài học.** Cả hai đều là **rò rỉ khái niệm giữa hai mốc thời gian**: logic của giai đoạn dự báo bị
> mang nguyên sang giai đoạn quy kết. Khi hệ thống có nhiều mốc quyết định, mỗi mốc phải được rà lại
> **toàn bộ** điều kiện, không kế thừa mặc định.

### 2.6 Nhóm thống kê — bộ giám sát drift

**L15, L16, L17** đều làm PSI báo động trên dữ liệu hoàn toàn khỏe, mỗi lỗi một cơ chế khác nhau:

| Lỗi | Cơ chế | PSI trên dữ liệu khỏe |
|---|---|---|
| Sai tổng thể *(toàn bộ val vs chỉ đơn bất mãn)* | Chọn mẫu bị đọc nhầm thành drift | 0,807 |
| Cửa sổ 50 mẫu, 10 khoảng đều nhau | Khoảng rỗng → log của tỷ số hai số cực nhỏ | 2,911 |
| Ngưỡng quy ước 0,25 | Dịch chuyển tổng thể theo thời gian là thật | 0,466 → 66% báo động giả |

**L14** thì ngược lại — phép kiểm tra phương sai bằng 0 thiếu **tiền đề**. Mệnh đề *"phương sai 0 ⟹
hỏng"* sai với một capability trả hằng số do thiết kế. Mệnh đề đúng: *"đại lượng **đã biến thiên trong
huấn luyện** mà đứng yên khi vận hành là bất thường"*.

> **Bài học.** Mọi phép kiểm tra thống kê đều mang **giả định ngầm** về tổng thể, cỡ mẫu, và phân phối
> tham chiếu. Trước khi tin một cảnh báo, chạy công cụ trên **dữ liệu chắc chắn khỏe** và xem nó có im
> lặng không. Nếu không im lặng, công cụ hỏng chứ không phải dữ liệu.

**L19 — nghịch lý kappa.** Sau vòng gán nhãn thứ nhất, công cụ báo κ trung bình = **0,436** và chỉ
`cause_price` là *"nguyên nhân bất đồng nhất"*. Cả hai kết luận đều sai:

| Nhãn | Lượt gán dương | % đồng ý | κ |
|---|---|---|---|
| `cause_price` | **5 / 798** | **98,7%** | **−0,006** |

Với một nhãn chiếm ~0,6%, kỳ vọng ngẫu nhiên đã gần bằng 1, nên tử số `(po − pe)` trở nên cực nhỏ và
cực nhiễu. κ ≈ 0 ở đây **không** nói lên độ tin cậy — nó nói lên rằng nhãn quá hiếm để đo. Đưa nó vào
trung bình kéo con số tổng từ 0,547 xuống 0,436, và làm người đọc đi sửa nhầm chỗ: vấn đề thật nằm ở
`cause_service` (κ = 0,345), không phải `cause_price`.

> **Bài học.** Khi tổng hợp một chỉ số qua nhiều lớp, phải kiểm tra **tần suất từng lớp trước khi lấy
> trung bình**. Một lớp quá hiếm không đóng góp thông tin mà chỉ đóng góp nhiễu — và nhiễu đó không
> trung hòa, nó kéo lệch một chiều.

**Cơ chế phòng ngừa đã cài:** nhãn có dưới `MIN_POSITIVES_FOR_KAPPA = 20` lượt gán dương vẫn được báo
cáo đầy đủ nhưng **không** vào trung bình và **không** được chọn làm "bất đồng nhất"; thông điệp của
Gate G2 nêu riêng chúng kèm số lượt.

**L20 — suýt phá phép đo của vòng hai.** Khi thiết kế tệp gán lại, phương án đầu là cho hiện nhãn vòng
một của **cả hai** người để họ thấy điểm khác biệt. Điều đó sẽ khiến hai người hội tụ về phía nhau và κ
vòng hai cao **một cách giả tạo** — ta sẽ đo được sức ép tuân thủ xã hội thay vì đo độ rõ của định
nghĩa. Mục đích của vòng hai là kiểm tra xem *codebook bản 2* có làm hai người hội tụ hay không, và chỉ
một phép đo **mù** mới trả lời được.

**Cơ chế phòng ngừa đã cài:** `cli/build_reannotation.py` sinh tệp **không chứa nhãn vòng một**; ánh xạ
được giữ riêng trong `reannotate_manifest.csv` để phân tích về sau, không đến tay người gán.

### L22 — đồng thuận che giấu sai sót chung *(lỗi nghiêm trọng nhất của cả dự án)*

Vòng gán nhãn thứ nhất cho κ = 0,547, và phản xạ đầu tiên — của cả tôi lẫn tài liệu
nghiên cứu — là *"định nghĩa nguyên nhân có vấn đề, sửa codebook"*. Tôi đã viết cả
một bản codebook v2 với sáu quy tắc quyết định dựa trên giả định đó.

**Giả định đó sai.** Phân tích 102 dòng bất đồng theo *bản chất* thay vì theo *số
lượng*:

| Bản chất | Số dòng | Diễn giải |
|---|---|---|
| Một bên nói `unknown`, bên kia tìm ra nguyên nhân | **76 (75,2%)** | **bỏ sót bằng chứng** |
| Cùng hướng, khác số lượng nhãn | 18 (17,8%) | ngưỡng |
| Quy kết khác hẳn nhau | 7 (6,9%) | định nghĩa |

Codebook v2 xử lý được 24,7% cuối. **Ba phần tư vấn đề nằm ở chỗ khác.**

Bốn ví dụ của nhóm 75%, tất cả đều là câu hiển nhiên với người đọc được tiếng Bồ:
`ainda n recebi o produto` · `muita demora na entrega` · `A LONA NÃO ENCAIXOU NA
ESTEIRA` · `COMPREI 2 CARTUCHOS... SÓ CHEGOU UM`. Và **cả hai người đều bỏ sót**, chỉ
khác dòng nào — A bỏ sót 27 lần, B bỏ sót 49 lần.

**Phần nghiêm trọng hơn.** Nếu cả hai cùng bỏ sót *cùng một dòng*, họ **đồng thuận** —
và κ không hề phát hiện. Kiểm tra: **59/249 dòng tầng A (23,7%) được cả hai cùng gán
`unknown`**, trong khi đọc 10 dòng mẫu thì 6 dòng có nguyên nhân nêu tường minh
*(`n foi entregue o produto que comprei`, `Produto não é bom pois não faz nenhum
efeito`, `Produto entregue diferente da compra`…)*.

> **Bài học — và đây là bài học đắt nhất của dự án.** κ đo **độ tin cậy giữa hai người
> đo**, không đo **độ đúng của phép đo**. Hai người dùng chung một công cụ bị lỗi sẽ
> đồng thuận cao trong khi cùng sai. Một chỉ số đồng thuận cao **không** miễn cho ta
> nghĩa vụ kiểm tra xem phép đo có đúng không.
>
> Cách phát hiện duy nhất là **đọc chính dữ liệu đã đồng thuận** — thứ mà không chỉ số
> tổng hợp nào thay thế được.

**Hệ quả kéo theo — một kết luận phải rút lại.** Phát hiện *"PriceAnalyst quy kết 9,3%
số đơn nhưng người gán đồng thuận 0%"* từng được ghi là bằng chứng mạnh cho giá trị
của gold set. Nó nay trở thành **tạm thời**: nếu cả hai người cùng bỏ sót các câu
`frete caro`, con số 0% phản ánh sai sót chung chứ chưa chắc phản ánh hệ thống sai.
Phải đo lại sau vòng 3.

**Cơ chế đang sửa:** gán nhãn vòng 3 trên **bản dịch tiếng Anh** (codebook bản 3), giữ
tiếng Bồ bên cạnh để neo nhãn vào văn bản gốc. Phạm vi 250 dòng tầng A — tầng B không
có văn bản nên không phụ thuộc ngôn ngữ.

### L32 — một nguyên nhân bị gỡ vì **hệ phân loại đặt sai**, không vì cỡ mẫu

`cause_price` chỉ có **12 mẫu dương trên 250 dòng (4,8%)**, và tính toán cỡ mẫu cho
thấy cần **~896 dòng** để ước lượng recall của nó. Phản xạ dễ nhất là bỏ nó *"vì quá
hiếm"* — và đó sẽ là một lý do sai cho một hành động đúng.

**Lý do đúng nằm ở logic của giao dịch.** Khách hàng đã **xác nhận mua**, tức đã đồng ý
với giá niêm yết và phí vận chuyển hiển thị lúc thanh toán. Một lời than **sau khi mua**
vì vậy không thể là về *giá*; nó luôn là về một **cơ chế khác đã hỏng**.

**Kiểm chứng bằng cách đọc cả 12 dòng:**

| Nội dung thật | Số dòng |
|---|---|
| **Phí vận chuyển** — trả tiền ship nhưng phải tự ra bưu điện lấy | **10** |
| **Giá trị sản phẩm** — chất lượng không xứng tiền | 2 |

Hai dòng nói rõ hàng vẫn tốt: *"**Quality merchandise**, I just think the freight should
be more affordable"* và *"I **received the product right**, but I want a refund of the
shipping"*. Gộp chúng vào `quality` sẽ **dán nhãn ngược với điều khách nói**.

**Ba quy tắc định tuyến** *(codebook §Quy tắc 7)* — hỏi *"cơ chế nào đã hỏng"*, không hỏi
*"có nhắc tới tiền không"*:

| Nội dung | Về |
|---|---|
| Phí vận chuyển · đòi hoàn phí **chung chung** | `delivery` |
| *"không đáng tiền"* · chất lượng không tương xứng | `quality` |
| Đòi hoàn phí **không được phản hồi** | `service` |

Điểm phân biệt hàng 1 với hàng 3 là **phản hồi**, không phải nội dung tiền bạc.

> **Bài học.** Khi một nhãn quá hiếm để đo, câu hỏi đầu tiên không phải *"có nên bỏ
> không"* mà **"nó có thật sự là một nhóm nguyên nhân, hay là một triệu chứng của nhóm
> khác?"** Ở đây nó là triệu chứng — và cỡ mẫu nhỏ chính là **dấu hiệu** của việc đặt sai
> hệ phân loại, không phải một vấn đề độc lập cần khắc phục bằng cách gán thêm.
>
> Ngược lại cũng đúng: nếu tôi gỡ nó *vì hiếm*, tôi sẽ gỡ đúng nhãn nhưng **giữ nguyên
> sai lầm khái niệm** — và 10 dòng phí vận chuyển sẽ tiếp tục bị gán sai chỗ.

**Hệ quả đo được:**

| | Trước | Sau |
|---|---|---|
| Số nguyên nhân | 4 | **3** + `unknown` |
| Dòng mất hết nhãn khi gỡ | — | **2/250 (0,8%)** — cả hai về `delivery` |
| Cỡ mẫu cần cho kế hoạch đánh giá | 896 dòng *(bất khả thi)* | **300 dòng — đủ cho cả ba** |
| Analyst trong Contract Net | 4 | 3 · chi phí chạy hết 3,0 → **2,9 ms** |

**Một kết luận tồn đọng tự khép lại.** Phát hiện *"PriceAnalyst quy kết 9,3% số đơn mà
người gán đồng thuận 0%"* từng được ghi là bằng chứng cho giá trị của gold set, rồi bị
rút lại thành tạm thời *(L22)*. Nay nó có lời giải thật: **cả hệ thống lẫn người gán đều
đang trả lời một câu hỏi đặt sai.**

**Phòng ngừa đã cài:** `Cause` không còn `PRICE`; từ khóa cũ định tuyến lại trong
`LEXICON` *(`frete caro` → `delivery`; `nao vale`, `nao compensa` → `quality`)*; `caro` và
`preco alto` trần **bỏ hẳn** vì quá mơ hồ để xác định cơ chế hỏng. `build_goldset` có
**Luật 0** định tuyến nhãn cũ và **ghi ra từng dòng bị động vào** — tệp gốc của người gán
không bị sửa.

### L30 — mốc quyết định được cưỡng chế ở **đặc trưng** nhưng bỏ ngỏ ở **tổng thể**

Dự án có `FeatureSet(decision_point)` và `test_leakage.py` để chặn đặc trưng của mốc muộn
lọt vào mốc sớm. Cơ chế đó chạy đúng suốt. Nhưng nó chỉ hỏi *"đặc trưng này có tồn tại
tại mốc không"*, chưa bao giờ hỏi *"**đơn hàng này** có tồn tại tại mốc không"*.

**T₃ từng được hiểu là một SỰ KIỆN — "sau khi giao xong".** Với cách hiểu đó:

| | Số đơn | Bất mãn | Thiếu `delivery_delay_days` |
|---|---|---|---|
| đã giao | 95.832 | 12,8% | 0,01% |
| **chưa từng giao** | **2.841 (2,88%)** | **77,9%** | **99,8%** |

Nhóm chưa giao đóng góp **15,3% tổng số đơn bất mãn**, và mô hình học được
*"thiếu ngày giao ⟹ rủi ro cao"*. Đo được: **PR-AUC 0,3993 → 0,2883** khi giới hạn về
đơn đã giao — **28% tương đối** đến từ một mẫu hình **không thể xảy ra lúc triển khai**,
vì tại T₃ theo định nghĩa hàng đã giao xong nên đặc trưng đó không bao giờ thiếu.

**Phản xạ đầu tiên của tôi là lọc `order_status == "delivered"`. Sai.** Người hướng dẫn
chỉ ra: đơn **quá hạn mà vẫn chưa giao** chính là ca cần can thiệp nhất. Lọc chúng đi là
vứt bỏ đúng nhóm 77,9% bất mãn — và đó là điều **cả hai cài đặt tham chiếu trên GitHub
đều làm**, trong đó một repo còn ghi rõ *"delivery feature only valid if the product is
delivered"* rồi chọn cách xử lý làm mất nhóm đó.

**Cách đúng: T₃ là một MỐC THỜI GIAN, không phải một sự kiện.** T₃ = hạn giao dự kiến +
k ngày. Chọn k bằng đo đạc:

| k | Đơn chưa tới | Bất mãn \| chưa tới | Bất mãn \| đã tới | Tỷ số |
|---|---|---|---|---|
| 0 | 10,65% | 60,4% | 9,2% | 6,6× |
| **3** | **7,97%** | **74,3%** | 9,5% | **7,8×** |
| 7 | 6,18% | 78,0% | 10,5% | 7,4× |
| 14 | 4,41% | 78,0% | 11,8% | 6,6× |

Tại mốc đó, trạng thái quan sát được có **ba mức đơn điệu**, thay cho một giá trị thiếu:

| `delivery_state` | Số đơn | Bất mãn |
|---|---|---|
| 0 — đã giao | 90.804 (92,0%) | 9,5% |
| 1 — đang vận chuyển, quá hạn | 5.910 (6,0%) | **71,4%** |
| 2 — chưa gửi, quá hạn | 1.959 (2,0%) | **82,8%** |

> **Bài học.** Một mốc quyết định ràng buộc **hai** thứ, không phải một: *đặc trưng nào
> đã tồn tại*, và *đơn hàng nào đã tới mốc đó*. Cưỡng chế vế đầu mà bỏ ngỏ vế sau thì
> mô hình vẫn học được từ tương lai — qua **hình dạng của dữ liệu thiếu** thay vì qua
> giá trị của một cột.
>
> Và khi một nhóm dữ liệu gây khó, phản xạ *"lọc nó đi"* thường là phản xạ sai. Ở đây
> nhóm khó chính là nhóm mang giá trị nghiệp vụ cao nhất. Cách đúng là **định nghĩa lại
> phép đo cho đúng thực tế**, không phải cắt bớt thực tế cho vừa phép đo.

**Kết quả sau khi sửa: PR-AUC 0,3892** *(so với 0,3993 có rò rỉ, và 0,2883 nếu lọc bỏ
nhóm chưa giao)*. Gần như giữ nguyên sức mạnh dự báo, nhưng nay **hợp lệ tại mốc**.

**Phòng ngừa đã cài:** `delivery_delay_days`, `delivery_days`, `is_late`,
`carrier_handover_days` chuyển sang **T₄** *(chúng là kết cuc)*; T₃ nhận ba đặc trưng
**kiểm duyệt bên phải** thay thế; bốn test canh, trong đó
`test_bang_don_hang_KHONG_loc_theo_trang_thai_giao_hang` chặn đúng phản xạ sai ở trên.

### L31 — thống kê tích lũy tính trên **toàn tập** là rò rỉ thời gian

Khi bổ sung đặc trưng phía người bán, `seller_popularity` là chỗ dễ sai nhất. Cách làm
phổ biến — đếm tổng số đơn của mỗi người bán trên **toàn bộ** dữ liệu — dùng **đơn tương
lai** để dự báo đơn hiện tại.

| Cách tính | PR-AUC |
|---|---|
| không dùng | 0,3754 |
| **đếm lũy tiến, chỉ đơn trước đó** *(đúng)* | 0,3748 |
| tổng trên toàn tập *(rò rỉ)* | **0,3799** |

Hai bản tương quan **0,809**, và bản rò rỉ thổi phồng **+0,005**.

**Bản đúng gần như không đóng góp gì** — và đó là một phát hiện, không phải thất bại:
**danh tiếng người bán không dự báo được bất mãn một khi đã biết thông tin hạn giao
hàng.** Nó loại trừ một giả thuyết cạnh tranh *("có phải chỉ do vài người bán tệ?")*.

> **Bài học.** Mọi thống kê **tích lũy theo thực thể** — số đơn, điểm trung bình, tỷ lệ
> hoàn — đều phải hỏi *"tính đến thời điểm nào"*. Không có mốc thời gian thì mặc định
> nó dùng cả tương lai. `test_leakage.py` cũ canh rò rỉ **theo mốc quyết định**; nay bổ
> sung canh rò rỉ **theo thời gian**.

### L29 — hai trong năm giả thuyết chứa mệnh đề **không kiểm định được như đã viết**

Khi chốt phán quyết cho năm giả thuyết, hai mệnh đề hóa ra chưa bao giờ kiểm định được:

| Giả thuyết | Mệnh đề hỏng | Vì sao |
|---|---|---|
| **H2** | *"đặc biệt ở … **nhóm không có bình luận**"* | Sự thật nền ở tầng B là *"không quy kết được"* trên **149/150** dòng. Không có nền thì không có phép so sánh độ chính xác |
| **H4** | *"suy giảm **quá ngưỡng**"* | **Ngưỡng chưa bao giờ được đặc tả.** Một so sánh *"trước khi"* không có mốc thì không kiểm định được |

**H4 thoát được nhờ may, không nhờ thiết kế.** Vì tỷ lệ phát hiện drift bằng **0 ở cả ba mức**, mệnh đề
*"phát hiện trước khi vượt ngưỡng"* sai với **mọi** giá trị ngưỡng — nên bác bỏ vẫn vững. Nếu bộ giám
sát có phát hiện ở một mức nào đó, H4 sẽ **treo**: không có ngưỡng thì không nói được nó phát hiện
*kịp* hay *muộn*. Kết quả cứu cho phát biểu, chứ phát biểu tự nó không đứng được.

**H2 thì không thoát.** Vế tầng B của nó là **một lỗi thao tác hóa, không phải một kết quả**, và phải
báo cáo đúng như vậy — nói *"bác bỏ ở tầng B"* sẽ là tuyên bố một phép đo chưa từng chạy được.

> **Bài học.** Ba tài liệu của dự án đều rà rất kỹ *chỉ số* và *đối chứng*, nhưng không tài liệu nào rà
> **từng mệnh đề trong từng giả thuyết**. Một giả thuyết trông có vẻ đo được ở mức tổng thể vẫn có thể
> chứa một mệnh đề phụ không đo được — và mệnh đề phụ ấy thường là mệnh đề **thú vị nhất**, vì đó là
> chỗ tác giả kỳ vọng artifact tỏa sáng. Đúng hai chỗ đó là hai chỗ hỏng ở đây.
>
> Cả hai chỉ lộ ra **lúc đánh giá** — muộn nhất có thể, và là lúc không còn sửa được thiết kế thí
> nghiệm nữa.

**Biện pháp đã cài lại — rà ba câu hỏi cho MỖI mệnh đề trước khi khai báo giả thuyết:**

| Câu hỏi | Chặn lỗi nào |
|---|---|
| Đo bằng **chỉ số** nào? | mệnh đề không có phép đo |
| **Sự thật nền** ở đâu, và nó có tồn tại trên nhóm này không? | lỗi vế tầng B của **H2** |
| **Ngưỡng** là bao nhiêu, đặt trước khi chạy? | lỗi *"quá ngưỡng"* của **H4** |

Mệnh đề nào không trả lời đủ ba thì **hoặc bỏ, hoặc tách thành một câu hỏi mô tả** — chứ không để nằm
trong một giả thuyết rồi tưởng là đã kiểm định. Quy trình này bổ sung vào **IMP-6** *(rà chỉ số)*, vốn
chỉ rà chỉ số chứ không rà mệnh đề.

**Ranh giới phải giữ khi sửa tài liệu.** Phát biểu của cả năm giả thuyết được giữ **nguyên văn**. Sửa
một giả thuyết sau khi thấy kết quả là **HARKing**, và nó sẽ phá hỏng đúng thứ mà việc khai báo trước
H1 và H5 đã mua được. Chỉ **phán quyết** và **diễn giải** được cập nhật. Điều này khác với **DP2**
*(L27)*: DP2 là Design Principle — tri thức quy phạm, là **sản phẩm** của nghiên cứu — nên sửa nó theo
bằng chứng là đúng quy trình DSR.

### L28 — cơ chế canh giữ ranh giới trích dẫn **không truyền được**, và chỉ diễn tập mới bắt ra

Chạy diễn tập toàn bộ chuỗi dưới **giả định** bộ nhãn hiện có là của hai người gán độc lập
— tức chuyển `Provenance` sang `human_independent` và xem hệ có tự đổi trạng thái không.

**Nó không đổi.** Bảng kết quả vẫn mang `citable = False`, banner tạm thời vẫn in ra.

Nguyên nhân: `run_attribution` đọc nguồn gốc từ **một đường dẫn đặt cứng**
`gold_labels_meta.json`, bỏ qua tệp thực sự truyền vào qua `--gold`. Và `build_goldset`
cũng ghi meta ra đúng tên cố định đó, nên hai gold set trong cùng thư mục **ghi đè meta
của nhau**.

> **Vì sao đây là lỗi nguy hiểm nhất có thể có trong thiết kế này.** Toàn bộ kỷ luật của
> `Provenance` — trường bắt buộc, cột `citable` trên mọi bảng, banner cảnh báo — tồn tại để
> ngăn số tạm lẫn vào Chương 5. Một đường dẫn đặt cứng vô hiệu hóa tất cả **mà không để lại
> dấu hiệu nào**: nó gắn cờ theo gold set *mặc định* chứ không theo gold set *đang được đo*,
> và sai được **theo cả hai chiều**. Lần này nó gắn nhầm thành "không trích được"; lần sau
> nó gắn nhầm thành "trích được".
>
> **Bài học.** Một cơ chế an toàn chưa từng được thử ở trạng thái *bật* thì chưa phải cơ chế
> an toàn. Tôi đã kiểm nó chặn đúng ở trạng thái *tắt* (số tạm → `citable=False`) và coi thế
> là đủ. Nửa còn lại — số thật → `citable=True` — chưa ai chạy qua bao giờ.

**Lỗi thứ hai, của chính tôi khi sửa lỗi thứ nhất.** Lần sửa đầu tôi dùng `str.replace` mà
không kèm `assert` kiểm mẫu khớp. Mẫu không khớp, script in ra `ok`, và tôi tin là đã sửa.
Chỉ đến khi chạy lại mới lộ. **Một phép biến đổi mã nguồn không kiểm chứng kết quả thì
không khác gì không làm** — và nó tệ hơn không làm, vì nó tạo niềm tin sai.

**Phòng ngừa đã cài lại:** `meta_path(gold_path)` bám theo tên tệp gold · `run_attribution`
**dừng hẳn** nếu thiếu meta thay vì mặc định "tạm thời" một cách im lặng · ba test canh
`test_meta_bam_theo_ten_tep_gold_khong_dat_cung`, `test_provenance_citable_phan_biet_dung_hai_trang_thai`,
`test_bang_ket_qua_doi_co_citable_khi_doi_nguon_goc`.

**Hai thông báo lỗi thời cũng lộ ra trong lần diễn tập này:** `run_evaluation` vẫn in
*"BỊ CHẶN cho tới khi có gold set: T10.2, T10.3"* trong khi hai task đó đã chạy được, và
chú thích của `attribution_per_ms` vẫn trỏ tới một chỉ số "chưa tồn tại". Cả hai đã sửa.

### L27 — hai kiến trúc cho kết quả **giống hệt nhau**, và điều đó đúng theo cấu tạo

Chạy trọn chu trình T10.2 trên gold set 250 đơn, ở mức ngân sách dư:

| | macro-F1 | số đơn khác biệt |
|---|---|---|
| MAS-DSS | 0,3804 | — |
| Monolithic-Complete | 0,3804 | **0 / 250** |

Không phải xấp xỉ. **Giống hệt từng đơn, từng nhãn.** Và khi truy ngược thì thấy nó
*phải* như vậy:

- Bốn analyst sở hữu **bốn nguyên nhân rời nhau** — mỗi analyst chấm đúng một nhãn.
- Cả bốn dùng **chung một cause head**.
- Arbiter nhận **mọi bid vượt `tau_cause`**.

Ghép lại: MAS = *"chấm 4 nhãn bằng head chung, giữ nhãn nào vượt τ"*. Monolithic =
*"chấm 4 nhãn bằng head chung, giữ nhãn nào vượt τ"*. Hai phép toán **bằng nhau về mặt
đại số**, nên không dữ liệu nào tách được chúng.

> **Bài học.** DP2 phát biểu *"để các tác tử cạnh tranh kèm bằng chứng"*, nhưng ở cài
> đặt hiện tại **không có cạnh tranh nào**: các tác tử **phân chia** không gian nhãn chứ
> không **tranh chấp** nó. Cạnh tranh chỉ có nghĩa khi hai bên cùng có thẩm quyền trên
> một phần bằng chứng và phải phân xử. Tôi đã viết cảnh báo tautology cho MIS/Single-ML
> *(chúng bằng 0 theo định nghĩa)* mà không thấy phiên bản đối xứng của nó: một đối chứng
> có thể **bằng đúng** artifact theo định nghĩa, và điều đó nguy hiểm hơn — vì nó trông
> như một phép so sánh công bằng cho tới khi ta đọc con số 0/250.

**Phát hiện thứ hai, ở mức ngân sách đã hiệu chỉnh.** `budget_for` cấp **2,0 ms** cho case
rủi ro THẤP. Head đã huấn luyện khai giá **12 ms**, nên analyst văn bản **không bao giờ
mua được suất** trên đơn rủi ro thấp:

| hệ số ngân sách | ngân sách TB | analyst được nhận | macro-F1 MAS | macro-F1 Mono |
|---|---|---|---|---|
| ×1 *(hiệu chỉnh cho head tạm)* | 30,7 ms | 2,39 | **0,2386** | 0,3804 |
| ×2 | 61,5 ms | 2,52 | 0,2376 | 0,3804 |
| ×10 | 307 ms | 3,16 | 0,3776 | 0,3804 |
| ×25 | 768 ms | 3,81 | **0,3804** | 0,3804 |

**Cổng rủi ro đã được gỡ tường minh khỏi T4 nay quay lại một cách ngầm qua ngân sách.**
Đơn rủi ro thấp không được phân tích văn bản, nên MAS thua đối chứng 0,14 macro-F1 — và
thua vì **một tham số chưa hiệu chỉnh lại sau khi head đổi giá**, không vì kiến trúc.

**Hệ quả cho H2 — phải nói thẳng.** Ở dạng hiện tại, cơ chế đấu thầu **không thể** tốt hơn
bộ phân loại đơn khối về macro-F1: nó hoặc **bằng** (ngân sách dư) hoặc **kém hơn** (ngân
sách ràng buộc). Báo cáo một con số ở duy nhất một mức ngân sách sẽ biến một tham số thành
một kết luận về kiến trúc — theo cả hai chiều.

**Ba đường đi, không loại trừ nhau:**

1. **Báo cáo như phát hiện phủ định.** RQ2 §2.2 đã khai báo trước rằng kết quả phủ định là
   *"một phát hiện trung thực và đáng công bố"*. Kết luận khi đó: **phối hợp không mua được
   độ chính xác; nó mua khả năng chịu lỗi và tính truy vết, với cái giá đo được** — nhất
   quán với kết quả mạnh của RQ3 và với H5.
2. **Làm cho cạnh tranh có thật.** Hiện `tau_cause` là ngưỡng CHUNG, nên bid chỉ là head thô.
   **T7.3b — hiệu chuẩn isotonic riêng từng analyst** phá được đẳng thức đó, và nó vốn đã
   nằm trong kế hoạch, nay hết bị chặn. Xa hơn: cho các analyst có **thẩm quyền chồng lấn**
   để arbiter có việc thật phải phân xử.
3. **Hiệu chỉnh lại ngân sách** theo giá thật của head, rồi báo cáo kèm đường cong độ nhạy
   ở trên thay vì một con số đơn lẻ.

**Đường ống đã kiểm chứng được là đúng** — đó chính là điều việc chạy trọn chu trình nhắm
tới. Ba lỗi nối ghép đã lộ ra và đã sửa: bộ đọc `causes` giả định sai dạng dữ liệu, ngân
sách chưa hiệu chỉnh, và đẳng thức kiến trúc ở trên.

### L26 — κ = 0,957 và con số đó không đo gì

Vòng 3 hoàn tất, Gate G2 cho **κ = 0,957** trên cả 5 nhãn — so với 0,547 của vòng 1.
Mọi thứ đều trông như một cải thiện lớn: `unknown` giảm 87 → 18, `price` tăng 3 → 12,
`cause_service` từ 0,345 lên 0,893.

Nhưng chính vì L22 mà tôi kiểm tra thay vì mừng. Kết quả:

| Kiểm tra | |
|---|---|
| Ghi chú **giống hệt từng ký tự** giữa hai bản | **241/250 (96,4%)** |
| Cột `confidence` giống hệt | 248/250 |
| Số **mẫu ghi chú** khác nhau trên 250 dòng | **15**, dạng `"Giao hàng — chưa nhận/không được giao: '<trích dẫn>'"` |

Hỏi lại thì rõ: nhãn do **một mô hình ngôn ngữ sinh**, người nghiên cứu rà lại, và
**cùng một đầu ra** được dùng cho cả hai file. Không tồn tại người gán thứ hai.

Cohen's κ đo độ đồng thuận giữa **hai người đo độc lập**. Giả định độc lập sai thì κ
không còn nghĩa — nó vẫn cho ra một con số đẹp, và đó chính là chỗ nguy hiểm. Cùng loại
tautology với TOST trên hai dãy số giống hệt nhau ở H1 *(L23)*.

**Điều KHÔNG xảy ra, và cần nói rõ để không phóng đại mức nghiêm trọng.** Đây **không**
phải vòng tròn C2. Mô hình ngôn ngữ đọc hiểu câu là cơ chế khác hẳn `LexiconCauseHead`
(khớp từ khóa) và khác LightGBM; nhãn không do chính hệ thống đang được đánh giá sinh ra.
Chất lượng nhãn nhìn qua còn có vẻ **tốt hơn** vòng 1 — mà L22 đã chứng minh vòng 1 bỏ
sót bằng chứng có hệ thống. Vấn đề không phải nhãn xấu; vấn đề là **chưa có gì chứng minh
nhãn tốt**.

**Một hệ quả không sửa được.** Người nghiên cứu đã rà cả 250 dòng **sau khi** thấy nhãn
của mô hình, nên phán đoán trên chính 250 dòng đó đã bị **neo**. Hỏi lại cùng những dòng
ấy chỉ đo được mức đồng ý với một câu trả lời đã biết.

> **Bài học.** Trước khi tính bất kỳ chỉ số đồng thuận nào, phải **kiểm tra giả định độc
> lập** của chính chỉ số đó — bằng dữ liệu, không bằng niềm tin vào quy trình. Dấu hiệu rẻ
> nhất là các cột *tự do* (ghi chú, độ tin cậy): hai người đọc cùng một câu có thể ra cùng
> một nhãn, nhưng **không** viết ra cùng một câu ghi chú 96% số lần.

**Biện pháp đã cài lại:**

- `cli/build_validation_sample.py` — rút 150 dòng tầng A từ **10.573 dòng chưa ai đụng**,
  tránh hiệu ứng neo. Lấy mẫu **ngẫu nhiên đơn giản**, không phân tầng theo nhãn của mô
  hình — phân tầng như vậy sẽ chọn trước những dòng mô hình tự tin và làm méo ước lượng.
- `cli/check_validation.py` — **Gate G2 thật**, ba bước theo thứ tự: *độc lập* → *độ đúng*
  → *hướng lệch*. Bước 1 chặn trước; nó đã được thử trên chính hai file vòng 3 và **chặn
  đúng** với lý do `notes` trùng 96,4% và `confidence` trùng 99,2%.
- Bước *hướng lệch* tồn tại vì một κ trơn che mất việc mô hình quy kết **nhiều hơn** hay
  **ít hơn** người. Nếu nhiều hơn một cách hệ thống thì sự thật nền bị thổi phồng recall,
  và macro-F1 của RQ2 sẽ đo trên một nền rộng hơn thực tế.

**Thứ tự bắt buộc trong vòng kiểm chứng: NGƯỜI GÁN TRƯỚC, MÔ HÌNH CHẠY SAU.** Đảo lại là
tái lập đúng hiệu ứng neo vừa mô tả.

### L25 — tôi lặp lại đúng L22, ba tuần sau khi tự viết ra L22

Khi chốt phạm vi vòng 3, tôi viết vào codebook bản 3: *"Tầng B giữ nguyên nhãn vòng
một — nó không phụ thuộc ngôn ngữ và **đã đạt đồng thuận tuyệt đối 0/150**."* Câu đó
dùng **độ đồng thuận** làm lý do miễn kiểm tra — đúng cái sai lầm mà L22 vừa mô tả.

Kiểm tra thật, đối chiếu với **Quy tắc 6 trong chính codebook đó** *(tầng B: gán
`delivery` khi `delivery_delay_days > 3`)*:

| | |
|---|---|
| dòng tầng B | 150 |
| **thỏa Quy tắc 6** | **43 (28,7%)** — trong đó 20 dòng trễ > 10 ngày, cao nhất 41,7 ngày |
| người A gán `delivery` | **0** |
| người B gán `delivery` | **0** |

Cả hai người gán `unknown` cho **toàn bộ** 43 dòng, với ghi chú giống hệt nhau
*"không có tiêu đề hoặc nội dung; không thể xác định nguyên nhân"* — dù phiếu gán nhãn
**có hiển thị** `delivery_delay_days`. Đồng thuận 150/150. Sai hệ thống 43/150.

**Nhưng câu hỏi đúng không phải "ai sai".** Xét kỹ thì **Quy tắc 6 mới là thứ hỏng**:
nó biến nhãn vàng thành một **hàm tất định của chính đặc trưng mà hệ thống cũng nhìn
thấy**. Chấm điểm `DeliveryAnalyst` trên nhãn sinh theo cách đó là **vòng tròn** — đúng
loại vòng tròn mà gold set tồn tại để phá *(ràng buộc C2)*. Trực giác của hai người gán
— không có văn bản thì không quy kết — về mặt tri thức luận là **đúng**.

> **Bài học.** Một quy tắc gán nhãn suy nhãn từ đặc trưng đầu vào thì không tạo ra sự
> thật nền; nó chỉ **phát lại luật** dưới danh nghĩa con người. Và lần này tôi biết
> trước bài học *(L22)* mà vẫn mắc, vì "đồng thuận tuyệt đối" nghe như một tín hiệu tốt.
> Đồng thuận càng cao thì càng phải hỏi *"cả hai có cùng dùng một công cụ hỏng không"*.

**Hệ quả cho RQ2 tình huống (b) — cần anh quyết định**, xem báo cáo tình hình. Ba đường:
bỏ Quy tắc 6 và đổi cách đo ở tầng B *(khuyến nghị)* · gán lại tầng B theo Quy tắc 6
*(giữ vòng tròn — không khuyến nghị)* · tuyên bố tầng B không đánh giá được.

### L23 — đọc số đo từ chuỗi đã làm tròn để hiển thị

Điều kiện kiểm soát của H1 khẳng định MAS-DSS và Single-ML dùng **chung một đối tượng**
`risk_model`, nên điểm dự báo phải giống nhau **từng bit**. Lần chạy đầu tiên báo *lệch
+0,000014* và in ra cảnh báo "mọi so sánh khác mất hiệu lực".

Hệ thống không sai. Đoạn kiểm tra của tôi lấy điểm của Single-ML bằng cách **tách chuỗi
`note`** — chuỗi này được sinh bằng `f"risk_score={score:.4f}"`, tức đã làm tròn để
người đọc. Tôi đã so sánh một số thực với chính nó sau khi ép qua 4 chữ số thập phân.

> **Bài học.** Một trường sinh ra để **hiển thị** không được dùng làm nguồn cho phép
> **đo**. Ranh giới này dễ mờ vì chuỗi hiển thị *trông như* dữ liệu. Cách sửa không phải
> nới ngưỡng so sánh cho hết kêu — làm vậy sẽ vô hiệu hóa đúng cái test đang bảo vệ tính
> hợp lệ của cả Chương 5 — mà là **thêm trường số thô** `SimpleResult.score`.

**Phòng ngừa đã cài lại:** `test_dieu_kien_kiem_soat_khong_bi_qua_mat_boi_lam_tron` khẳng
định ngưỡng `1e-12` phân biệt được một dãy số với chính nó đã làm tròn 4 chữ số. Nới
ngưỡng lên `1e-3` làm test đỏ.

### L24 — sai số đo lệch về phía **có lợi cho artifact**

T10.6 đo "phải viết thêm bao nhiêu dòng mã để có được khả năng chịu lỗi". Hàm đếm dòng
loại trừ docstring bằng ước lượng `len(docstring.splitlines()) + 2`, cộng 2 cho cặp dấu
nháy. Nhưng theo văn phong của dự án, dòng mở và dòng đóng **đã nằm trong** nội dung
chuỗi, nên phép trừ tính trùng. Với module docstring dài, kết quả âm — và `max(code, 0)`
biến nó thành **số 0 im lặng**.

| | trước | sau |
|---|---|---|
| tầng chịu lỗi | 330 dòng | **448** |
| tầng phối hợp | 503 dòng | **632** |

Sai lệch ~26%, và **toàn bộ theo một hướng: làm nhẹ đi cái giá của kiến trúc**. H5 được
khai báo trước là *kỳ vọng thua*; một lỗi đo làm artifact trông rẻ hơn thực tế là loại
sai lệch nguy hiểm nhất, vì nó trùng hướng với điều tác giả muốn tin nên khó tự phát hiện.

> **Bài học kép.** (a) Khi một phép đếm có thể ra giá trị vô lý, đừng **kẹp** nó về giá
> trị hợp lệ — hãy để nó nổ, hoặc dùng phép đo chính xác thay cho ước lượng. Ở đây `ast`
> có sẵn `lineno`/`end_lineno` của node docstring; không có lý do gì phải đoán. (b) Rà
> chỉ số **bất lợi** kỹ ít nhất ngang chỉ số có lợi. Chỉ số có lợi được soi vì ta ngờ nó;
> chỉ số bất lợi được tin vì nó "đúng như dự đoán".

**Phòng ngừa đã cài lại:** ba test — đếm đúng trên file mẫu, không bao giờ ra 0 do kẹp, và
`test_danh_sach_module_chi_phi_deu_ton_tai` biến việc **đổi tên một module** từ lỗi im
lặng (bảng chi phí lặng lẽ bỏ qua module đó) thành lỗi ồn ào.

---

**L13** là lỗi ngữ nghĩa chứ không phải thống kê: cảnh báo là **sự kiện một lần** (để đo độ trễ phát
hiện), nhưng trạng thái sức khỏe phải **bền vững**. Trộn hai khái niệm khiến guard chặn đúng case đầu
tiên rồi im — silent failure chỉ giảm 18,0% → 17,7%.

### 2.7 Nhóm kiến trúc và phép đo

**L18.** `runtime/faults.py` import `masdss.chaos.components` — tầng runtime phụ thuộc tầng thí nghiệm.
Test phân tầng bắt được ngay. Định danh thành phần là **từ vựng chung**, thuộc `core/`.

**T01–T03.** Ba lỗi trong chính công cụ đo. Đáng chú ý nhất là **T02**: test có `pytest.raises` nhưng
tự `raise` ở cuối khối, nên nó **luôn xanh** bất kể guard có hoạt động hay không.

**T04** là lỗi nghiêm trọng nhất trong nhóm này, và nó được phát hiện **bằng chính IMP-3**. Sau khi
viết xong tầng test IMP-1, tôi tái hiện L17 (đặt ngưỡng PSI về 0,25) để xác nhận test chuyển đỏ.
**Tất cả vẫn xanh.**

Nguyên nhân: fixture dùng 25 case, trong khi PSI cần ít nhất 100 quan sát mới được tính. Bộ giám sát
không bao giờ chạy, nên phép thử "phải im lặng" luôn thỏa mãn một cách tầm thường. Một tầng test được
viết riêng để chặn bốn lỗi báo động giả, và nó **không chặn được cái nào**.

Sau khi thêm fixture 200 case, phép thử lại cho: **4 test đỏ đúng như mong đợi**.

> **Bài học.** Một test mới viết phải được xác nhận **đỏ vì đúng lý do** trước khi làm cho nó xanh. Test
> quét mã nguồn phải dùng **AST**, không dùng tìm chuỗi — comment giải thích không phải vi phạm.
>
> **Bài học bổ sung từ T04:** một phép thử phải chạy trên **cỡ mẫu đủ để cơ chế cần kiểm tra được kích
> hoạt**. Test rỗng nguy hiểm hơn không có test, vì nó tạo cảm giác an toàn sai. Cách phát hiện duy
> nhất là tái hiện lỗi và kiểm tra test có đỏ không — không có đường tắt.

---

### L33 — mốc "dự báo" nằm **sau** mốc nó dự báo, với 97,6% số đơn

Cấu hình cũ đặt **T₃ = hạn giao dự kiến + 3 ngày**. Con số nghe hợp lý: đợi quá hạn ba
ngày rồi mới kết luận đơn có vấn đề. Sai lầm nằm ở chỗ **không ai đối chiếu mốc đó với
thời điểm khách thực sự viết đánh giá**.

| Quan sát trên 75.480 đơn | Giá trị |
|---|---|
| Đánh giá viết **trước** hạn giao dự kiến | **87,8%** |
| Khoảng cách từ lúc giao tới lúc viết đánh giá *(trung vị)* | **6,2 giờ** |
| Đơn có **T₃ rơi sau T₄** — tức "dự báo" chạy sau kết cục | **97,6%** |

**Vì sao nó không bị phát hiện sớm.** Cưỡng chế ràng buộc chỉ diễn ra ở **mức đặc trưng**:
`FeatureSet(decision_point)` chặn được cột nào lộ tương lai. Nhưng **bản thân mốc thời gian**
lại là một tham số cấu hình, và không có bất biến nào so nó với `review_creation_date`. Đây
đúng là dạng khuyết đã gây ra **L30** — cưỡng chế ở một mức, bỏ ngỏ ở mức kia.

**Hệ quả nghiêm trọng hơn một chỉ số bị thổi phồng.** Nếu T₃ nằm sau T₄ thì **toàn bộ mệnh
đề "phục hồi dịch vụ trước khi khách đánh giá" không còn nghĩa** — không còn gì để phục hồi.
Mọi số ở **L30** *(PR-AUC 0,3993 → 0,2883)* đều đo trên mốc hỏng này và **phải bỏ**.

#### Đối chiếu trước/sau — mọi chỉ số đều **xấu đi**, và đó là chiều đúng

Cấu hình cũ được **dựng lại và đo lại**, không trích từ trí nhớ. Cùng **15 đặc trưng**, cùng
mô hình, cùng seed; chỉ khác mốc và tổng thể.

| | **Cũ** — hạn dự kiến + 3 | **Mới** — ngày mua + 7 |
|---|---|---|
| **T₃ nằm sau T₄** | **97,6%** ❌ | **0,0%** ✅ |
| Tổng thể | 98.673 | 73.234 |
| n test | 14.801 | 11.322 |
| Tỷ lệ nền test | 10,99% | 12,74% |
| **PR-AUC** | **0,402** | **0,244** |
| lift PR-AUC | 3,66 | 1,92 |
| ROC-AUC | 0,7178 | 0,6502 |
| **precision@1%** | **0,750** | **0,469** |
| lift@1% | 6,83 | 3,68 |
| Brier thô | 0,0807 | 0,1148 |
| Brier hằng số nền | 0,0978 | 0,1111 |
| Brier isotonic | 0,0798 | 0,1077 |
| ECE thô → isotonic | 0,0206 → 0,0116 | 0,0711 → 0,0273 |

**PR-AUC tụt 0,158 và precision@1% tụt 0,281.** Nếu chỉ nhìn bảng này mà không nhìn dòng đầu,
thay đổi trông như một bước lùi nghiêm trọng. Dòng đầu là thứ giải thích tất cả: ở cấu hình cũ,
với **97,6%** số đơn, mô hình "dự báo" ở một thời điểm mà **khách đã viết đánh giá xong**. Con số
0,402 không đo năng lực dự báo — nó đo khả năng đọc lại một kết cục đã có.

**Một chi tiết đáng chú ý riêng.** Sau khi thêm `days_to_deadline` — đặc trưng *thời gian còn lại
đến hạn cam kết, tính tại mốc* — precision@1% hồi từ **0,469 lên 0,549** *(lift 3,68 → 4,31)*
trong khi PR-AUC gần như không đổi *(0,244 → 0,2455)*. Tức đặc trưng đó không cải thiện xếp hạng
nói chung, nhưng cải thiện đúng **phần đầu bảng xếp hạng** — phần duy nhất được đem ra can thiệp.
Đây là lý do `precision@k` phải được báo cáo cạnh PR-AUC chứ không thay thế bằng nó.

**Bài học tổng quát.** Một mốc quyết định ràng buộc **hai** thứ: *đặc trưng nào tồn tại* và
*đơn nào đã tới được mốc đó*. Ràng buộc thứ hai phải được canh bằng một bất biến so với **thời
điểm của biến kết cục**, không phải bằng lập luận về mặt nghiệp vụ nghe hợp lý.

---

### L34 — tôi làm hỏng một tài liệu nghiên cứu bằng chuỗi `.replace()` nối tiếp

Khi hoán vị số hiệu ba câu hỏi *(RQ1→RQ2→RQ3→RQ1)* trong `status-checklist.md`, tôi viết:

```python
s = s.replace("RQ1", "\x00RQ2").replace("RQ2", "\x00RQ3").replace("RQ3", "\x00RQ1")
```

Lệnh thứ hai **bắt lại chính `RQ2` mà lệnh thứ nhất vừa tạo ra**. Sau ba lượt, cả **40**
tham chiếu MT/RQ trong tài liệu sập về `MT1`/`RQ1`. Tôi đã ghi tệp trước khi kiểm.

**Vì sao nó suýt không bị phát hiện.** Placeholder `\x00` được đặt vào **đúng với ý định**
chặn chồng lấn — nhưng nó chỉ chặn nếu được dọn **sau mỗi lượt**, không phải sau cả ba. Bản
thân đoạn mã *trông như* đã phòng ngừa. Và bất biến tôi tự đặt — *"tổng số tham chiếu không
đổi"* — **vẫn đúng** sau khi hỏng: 22 tham chiếu MT vào, 22 ra. Một bất biến bảo toàn tổng
**không** phát hiện được phép trộn.

**Cái đã cứu:** in **phân bố theo từng giá trị** chứ không chỉ tổng. `{MT1: 22, MT2: 0, MT3: 0}`
lộ ngay lập tức.

**Phục hồi.** Dự án **không nằm dưới quản lý phiên bản**, nên không có `git checkout`. Khôi phục
được là nhờ **may**: bản `grep` liệt kê nguyên trạng 16 tham chiếu RQ và các dòng tiêu đề MT còn
trong phiên làm việc, và số đếm từng loại *(MT 8/8/6 · RQ 3/10/5)* khớp chính xác nên phép dựng
lại là **xác định**, không phải phỏng đoán.

**Hai bài học, cái thứ hai quan trọng hơn.**

1. Phép hoán vị phải làm bằng **một lượt duy nhất** — `re.sub` với hàm thay thế, mỗi vị trí
   được chạm đúng một lần. Và bất biến kiểm chứng phải **theo từng giá trị**, không phải theo tổng.
2. **Rủi ro dự án chưa được ghi nhận: không có quản lý phiên bản.** Lần này khôi phục được.
   Một thao tác tương tự lên `docs/research-questions-objectives.md` hay `data/processed/` sẽ
   **không** khôi phục được. Đây là rủi ro lớn nhất của dự án hiện nay và nó không nằm ở mã nguồn.

---

### L35 — một biện minh nghe chặt chẽ nhưng không khớp phép đo

Ràng buộc **C3** biện minh cho mốc `T₃ = ngày mua + 7` bằng câu: *"mức tối ưu đo được: kịp
87,4% đơn bất mãn, **lift đạt đỉnh 2,19**"*. Câu đó có cấu trúc của một lập luận tốt — một
đại lượng, một cực trị, một con số. Khi đo lại thì **cả hai vế đều sai**:

| Mốc | Phủ đơn bất mãn | Lift nhóm *chưa bàn giao 3PL* |
|---|---|---|
| mua + 5 | 94,0% | 1,67 |
| **mua + 7** | **87,4%** ✅ | **2,12** *(không phải 2,19)* |
| mua + 10 | 75,4% | **2,39** ← đỉnh thật |
| mua + 14 | 61,5% | 2,36 |

Chỉ con số phủ sóng là đúng. Lift tại +7 lệch, và quan trọng hơn: **+7 không phải điểm cực đại**
của lift. Lập luận *"đây là mức tối ưu"* vì vậy không có cơ sở như đã viết.

**Vì sao lỗi này nguy hiểm hơn vẻ ngoài của nó.** Nó không làm sai một kết quả — mốc +7 vẫn là
lựa chọn đúng. Nó làm sai **lý do**, và lý do sai thì không phát hiện được bằng việc chạy lại thí
nghiệm: mọi con số hạ nguồn vẫn tự nhất quán. Chỉ việc đo lại chính mệnh đề biện minh mới lộ ra.

**Lý do đúng, sau khi đo.** +7 không phải mốc tín hiệu mạnh nhất mà là mốc **cân bằng**: đẩy sang
+10 mua thêm 0,27 lift nhưng mất **12 điểm phần trăm phủ sóng**, tức khoảng **1.700 đơn bất mãn**
không còn kịp can thiệp. Với một hệ *phục hồi dịch vụ*, số đơn tiếp cận được là đại lượng có
nghĩa nghiệp vụ.

**Bài học tổng quát.** Mệnh đề dạng *"X là mức tối ưu"* là một **khẳng định thực nghiệm**, không
phải câu dẫn dắt. Nó phải được đo trên **toàn dải** trước khi viết ra — nếu không, nó chỉ có hình
thức của một lập luận. Và khi phép đo không ủng hộ *"tối ưu"*, cách sửa đúng là **phát biểu lại
lý do**, không phải đi tìm một đại lượng khác tình cờ đạt đỉnh ở đó.

---

### L36 — một phép thử rỗng trông giống hệt một kết quả tốt

Mở rộng chaos sang **năm thành phần chỉ MAS-DSS mới có** là điều kiện để H2 kiểm định
được. Lần chạy đầu cho bảng này:

| Kịch bản | `mas_changed` | `mas_silent` | `mono_silent` |
|---|---|---|---|
| `byz_gross_masonly_k1..k3` | **0,0%** | **0,0%** | 0,0% |

Đọc nhanh thì đây là kết quả đẹp nhất có thể: *không case nào bị ảnh hưởng, không case
nào hỏng âm thầm*. Đọc kỹ thì nó **không đo gì cả**.

**Nguyên nhân gốc.** `ConstantOutputInjector` gắn cứng tên trường `risk_score`. Chỉ
`prediction` phát ra trường đó. Năm thành phần chỉ-MAS phát ra `context` · `proposal` ·
`challenged` · `sided_with`. Hàm `_poison` gặp trường không tồn tại thì **trả về nguyên
kết quả** — một lựa chọn hợp lý cho một hàm tiện ích, và tai hại khi không ai kiểm.

**Dấu hiệu nhận ra.** `mas_changed = 0,0%` **đồng thời** `mas_degraded = 0,0%`. Một lỗi
thật luôn để lại **ít nhất một** trong hai: hoặc đầu ra đổi, hoặc hệ ghi nhận suy giảm.
Bằng 0 cả hai không phải "hệ chịu lỗi hoàn hảo" mà là **không có lỗi nào được tiêm**.

Đối chiếu: cùng bề mặt đó, `crash` và `hang` cho `mas_changed = 7,5%` và
`mas_degraded = 100%`. Hai nhóm ấy tiêm được; nhóm Byzantine thì không.

**Hai điều lộ ra thêm trong lúc sửa.**

1. **`case_manager` không nằm trong kế hoạch nào.** Cả `STAGE1_PLAN` lẫn `STAGE2_PLAN`
   đều không gọi nó, nên nó không hỏng được. Đếm nó vào "bề mặt hỏng" là **đếm thừa**:
   bề mặt chỉ-MAS *gọi được* là **bốn**, không phải năm.
2. **Trường đáng đầu độc nhất là `challenged` của Policy Critic.** Đặt nó thành `False`
   khiến bộ phản biện im lặng chấp thuận mọi đề xuất, và không có gì trong đầu ra tỏ ra
   bất thường — đúng định nghĩa Byzantine, khác hẳn một hằng số thô.

**Bài học tổng quát.** Một bộ tiêm lỗi cần **bằng chứng rằng nó đã tiêm được**. Kiểm tra
rẻ nhất: lượt chạy có lỗi phải khác lượt chạy khỏe ở **ít nhất một** đại lượng quan sát
được. Nếu không khác gì, giả định mặc định phải là *"phép thử hỏng"*, không phải
*"hệ thống tốt"* — vì hai khả năng đó cho **cùng một bảng số**.

---

### L37 — đối chứng bị tính là "im lặng" trong khi nó có kêu

Chỉ số trung tâm của RQ1 là **tỷ lệ hỏng âm thầm**, định nghĩa: *đầu ra đổi so với lượt
chạy khỏe mà hệ thống không phát tín hiệu nào*. Với MAS-DSS, "tín hiệu" là
`degradation_level > 0`, `needs_human_review`, hoặc `escalate_to_human`.

Với kiến trúc đơn khối, phép đếm **không hỏi câu tương ứng**. Nó coi **mọi** đầu ra bị
đổi là hỏng âm thầm, với lý do ngầm *"đơn khối không có cờ suy giảm"*. Lý do đó **sai**:
nó có `failed_steps`, và trường này được điền đầy đủ mỗi khi một bước raise exception.

#### Độ lệch, đo trên chính dữ liệu đã lưu

| Kịch bản | Mono đổi đầu ra | Trong đó **có** `failed_steps` | Âm thầm **thật** |
|---|---|---|---|
| `crash_k1` @ T₄ | 32 | **32** | **0** |
| `crash_k2` @ T₄ | 42 | **42** | **0** |
| `crash_k3` @ T₄ | 76 | **76** | **0** |
| `crash_s1_k3` @ T₃ | 15 | **15** | **0** |
| `byz_gross_k3` @ T₄ | 200 | 0 | **200** |
| `bias_30` @ T₄ | 75 | 0 | **75** |

Con số đã công bố *"đơn khối hỏng âm thầm 16,0 → 38,0% dưới crash"* thực ra là **0,0%**.

**Sai lệch nghiêng về phía có lợi cho artifact của chính nghiên cứu** — cùng loại với
**L24** *(bộ đếm dòng mã)* và **L05** *(baseline đơn nhãn)*. Ba lần, cùng một hướng.

#### Vì sao bản sửa làm kết quả **mạnh hơn**, không yếu đi

Tuyên bố cũ — *"MAS-DSS chịu lỗi tốt hơn"* — rộng và mơ hồ. Bản sửa cho một tuyên bố
**có cơ chế**:

| Nhóm lỗi | Có raise exception? | Mono âm thầm | MAS âm thầm |
|---|---|---|---|
| crash · hang | ✔ có | **0,0%** | **0,0%** |
| **byzantine** | ✘ không | **90,5 – 100%** | **0,0%** |
| **bias** | ✘ không | **7,5 – 37,5%** | **0,0%** |
| drift | ✘ không | 2,5 – 9,0% | 1,5 – 6,5% |

> Ưu thế của MAS-DSS nằm **trọn vẹn** ở nhóm lỗi **không ném ngoại lệ**.

Đó là điều `try/except` không mua được: một lỗi biết raise thì kiến trúc nào cũng bắt
được. Lỗi trả về **giá trị hợp lệ nhưng sai** mới là lỗi cần một thang suy giảm và một
output guard — và đó chính xác là phần MAS-DSS đóng góp. Trên `drift`, cả hai đều gần
như mù, và điều đó cũng phải báo cáo.

**Bài học tổng quát.** Một chỉ số so sánh phải hỏi **cùng một câu** với cả hai bên. Khi
hai kiến trúc biểu diễn "tín hiệu cảnh báo" bằng hai cơ chế khác nhau, việc chỉ tìm cơ
chế của bên mình rồi kết luận bên kia *"không có gì"* là **làm yếu đối chứng bằng cách
định nghĩa**. Câu hỏi phải là *"bên kia biểu diễn điều này bằng gì"* trước khi kết luận
là nó không biểu diễn.

---

## Phần 3 — Cơ chế nào phát hiện được nhiều lỗi nhất

| Cơ chế | Số lỗi bắt được | Nhận xét |
|---|---|---|
| **Chạy trên dữ liệu thật** | 6 *(L04, L08, L10, L11, L13, L14)* | Nhiều nhất. Lỗi thiết kế trông hợp lý trên giấy chỉ lộ ra khi có số |
| **Phản biện tài liệu** | 5 *(L01, L02, L03, L05, L09)* | Rẻ nhất, bắt được nhóm vòng tròn và baseline |
| **Đo trực tiếp thay vì suy đoán** | 3 *(L15, L16, L17)* | Cả ba lỗi PSI đều chỉ lộ khi in ra hai phân phối |
| **Test tự động** | 2 *(L18, T01)* | Ít về số lượng nhưng bắt **tức thì** và **lặp lại được** |
| **Nghi ngờ con số quá đẹp** | 2 *(L04, L12)* | 0,0000 và 0,0% đều là tín hiệu đáng ngờ |

**Kết luận rút ra:** kiểm chứng bằng cách **chạy thật, sớm, trên dữ liệu thật** có hiệu suất phát hiện
cao nhất. Đây là lập luận hậu nghiệm ủng hộ quyết định chèn *walking skeleton* ở Đợt 0
(`implementation-plan.md §4`) — chiến lược đó đúng, và nên đẩy xa hơn.

---

## Phần 4 — Kế hoạch cải tiến

Bảy biện pháp, sắp theo tỷ lệ *giá trị / chi phí*. Cột "Chặn nhóm nào" trỏ về §2.

| ID | Biện pháp | Chặn nhóm nào | Chi phí | Ưu tiên |
|---|---|---|---|---|
| **IMP-1** | **Lượt chạy khỏe là bài kiểm tra bắt buộc của mọi bộ giám sát** | §2.6 | 0,5 ngày | **Cao nhất** ✅ **đã cài** |
| **IMP-2** | **Kiểm tra bất biến trên đầu ra**, không chỉ trên đơn vị | §2.5 | 1 ngày | Cao ✅ **đã cài** |
| **IMP-3** | **Quy tắc đỏ-trước-xanh** cho mọi test mới | §2.7 | 0 *(quy ước)* | Cao ✅ **đã áp dụng** |
| **IMP-4** | **Bảng khai giả định** cho mỗi phép kiểm tra thống kê | §2.6 | 0,5 ngày | Cao 🟡 **một phần** |
| **IMP-5** | **Rà điều kiện theo từng mốc quyết định** | §2.5 | 0,5 ngày | Trung bình |
| **IMP-6** | **Danh sách kiểm tra chỉ số** trước khi đưa vào báo cáo | §2.1, §2.4 | 0,5 ngày | Trung bình |
| **IMP-7** | **Chạy chaos trong CI** trên mẫu nhỏ | §2.4, §2.6 | 1 ngày | Trung bình |

### IMP-1 — Lượt chạy khỏe là bài kiểm tra bắt buộc

**Vấn đề chặn:** L14, L15, L16, L17 — bốn lỗi, tất cả đều là **báo động giả trên dữ liệu khỏe**, và
tất cả đều lẽ ra phải lộ ra ngay nếu có một phép thử duy nhất.

**Biện pháp.** Mọi bộ giám sát, guard, hay bộ phát hiện bất thường phải có một test dạng:

> *chạy trên dữ liệu chắc chắn khỏe → số cảnh báo phải bằng 0*

Test này phải viết **trước** test phát hiện. Nếu công cụ không im lặng được trên dữ liệu khỏe thì nó
chưa dùng được, bất kể nó bắt lỗi tốt đến đâu.

**Trạng thái: đã cài.** `tests-v3/test_output_invariants.py` — bốn test trên lượt chạy khỏe 200 case:
0 cảnh báo · 0 guard chặn · 0 case suy giảm · 0 breaker mở. Kèm test đối xứng
`test_crash_injection_is_never_silent`.

**Đã kiểm chứng bằng IMP-3:** tái hiện L17 (ngưỡng PSI về 0,25) → đúng 4 test chuyển đỏ. Lần kiểm
chứng đầu tiên **thất bại** vì fixture chỉ có 25 case (lỗi T04); phải thêm fixture 200 case mới phát
hiện được.

### IMP-2 — Kiểm tra bất biến trên đầu ra

**Vấn đề chặn:** L08, L10, L11 — cả ba đều là bất biến nghiệp vụ bị vi phạm, và cả ba chỉ lộ ra khi
người đọc nhìn vào `decisions.jsonl` bằng mắt.

**Biện pháp.** Bổ sung một tầng test chạy trên **tệp đầu ra thật**, khẳng định các bất biến mức hệ
thống:

| Bất biến | Phát biểu |
|---|---|
| Quy kết được thì phải hành động | `causes != [] ⟹ action != "no_action"` |
| Có bằng chứng thì phải phân tích | tỷ lệ case đi qua phiên đấu thầu phải ≥ ngưỡng |
| Chuyển giao thì phải đánh dấu | `action == "escalate_to_human" ⟹ needs_human_review` |
| Suy giảm thì phải chuyển giao | `degradation_level > 0 ⟹ needs_human_review` |
| Không tiêm lỗi thì không suy giảm | `inject is None ⟹ mọi degradation_level == 0` |

**Trạng thái: đã cài.** Cả năm bất biến, cộng thêm hai bất biến nữa: cờ `multi_cause` phải khớp số
nguyên nhân (DP2), và mọi bid trong nhật ký phải kèm bằng chứng.

Ngưỡng của bất biến "có bằng chứng thì phải phân tích" đặt ở **20%** một cách có chủ đích: nó không
nhằm đo chất lượng quy kết — con số đó sẽ thay đổi khi T3.4 xong — mà nhằm bắt trường hợp cơ chế quy
kết bị **vô hiệu hóa hoàn toàn**, đúng như L08.

### IMP-3 — Quy tắc đỏ-trước-xanh

**Vấn đề chặn:** T02 — test luôn xanh vì tự `raise`, nên guard hỏng mà không ai biết.

**Biện pháp.** Quy ước bắt buộc: mọi test mới phải được xác nhận **đỏ vì đúng lý do** trước khi làm nó
xanh. Với test khẳng định một guard hoạt động, cách xác nhận là **tạm thời tắt guard** và kiểm tra test
đỏ. Ghi vào `technical-plan-v3.md §8` như kỷ luật thứ năm.

Kèm hai quy tắc phụ:
- **Test quét mã nguồn phải dùng AST**, không dùng tìm chuỗi *(chặn T01)*.
- **Phép thử phải chạy trên cỡ mẫu đủ để cơ chế cần kiểm tra được kích hoạt** *(chặn T04)*. Đã cài
  `test_monitoring_run_is_large_enough_to_engage_psi` để biến điều kiện này thành lỗi tại chỗ.

**Trạng thái: đã áp dụng.** Quy tắc này tự nó đã phát hiện T04 ngay trong lần dùng đầu tiên.

### IMP-4 — Bảng khai giả định cho phép kiểm tra thống kê

**Vấn đề chặn:** L14, L15, L16 — cả ba là giả định ngầm bị vi phạm.

**Biện pháp.** Mỗi phép kiểm tra thống kê trong `reliability/` phải khai báo tường minh trong docstring:

| Mục khai báo | Ví dụ với PSI |
|---|---|
| Tổng thể của luồng giám sát | đơn bất mãn ở T₄ |
| Tổng thể của phân phối tham chiếu | **phải trùng** với dòng trên |
| Cỡ mẫu tối thiểu | ≥ 100 quan sát |
| Cách chia khoảng | phân vị của tham chiếu, không phải khoảng đều |
| Nguồn của ngưỡng | hiệu chuẩn từ lượt chạy khỏe, không lấy quy ước |
| Tiền đề của kết luận | tham chiếu phải có phương sai > 0 |

Thêm một hàm `assert_reference_population_matches()` chạy lúc `set_reference()` để biến điều kiện đầu
thành lỗi tại chỗ thay vì báo động giả ba trăm case sau.

**Trạng thái: một phần.** `reliability/reference.py` đã cưỡng chế ba trong sáu mục — khớp tổng thể, cỡ
mẫu tối thiểu, và tiền đề phương sai > 0 — bằng cách **từ chối nạp tham chiếu** kèm lý do cụ thể thay
vì nạp một tham chiếu tồi rồi báo động giả về sau. Ba mục còn lại *(cách chia khoảng, nguồn ngưỡng, cỡ
mẫu cửa sổ)* mới ở dạng docstring.

### IMP-5 — Rà điều kiện theo từng mốc quyết định

**Vấn đề chặn:** L08, L09, L10 — rò rỉ khái niệm giữa T₃ và T₄.

**Biện pháp.** Với mỗi mốc quyết định, lập bảng rà: *điều kiện này có ý nghĩa gì ở mốc này?* Một điều
kiện chỉ được kế thừa sang mốc khác khi có lý do tường minh.

| Điều kiện | Ở T₃ | Ở T₄ |
|---|---|---|
| `risk >= MEDIUM` mở phiên đấu thầu | **Có nghĩa** — đang dự báo | **Vô nghĩa** — bất mãn đã xảy ra |
| `causes == []` ⟹ escalate | **Vô nghĩa** — chưa có nhiệm vụ quy kết | **Có nghĩa** — quy kết thất bại |
| `has_comment` là đặc trưng | **Rò rỉ nhãn** | Hợp lệ |

Bảng này nên đưa vào Chương 4 như một phần mô tả thiết kế thí nghiệm.

### IMP-6 — Danh sách kiểm tra chỉ số

**Vấn đề chặn:** L01, L02, L04, L06, L07.

Trước khi một chỉ số được đưa vào báo cáo, trả lời **sáu câu**:

1. Kết quả nào của chỉ số này sẽ khiến tôi kết luận thiết kế của mình **sai**? *(chặn vòng tròn)*
2. Chỉ số đo trên **tập nào**? Tập đó có được dùng để khớp bất cứ tham số nào không? *(chặn in-sample)*
3. Baseline có **cơ hội ngang bằng** để đạt điểm cao không? *(chặn bù nhìn)*
4. Chỉ số có **phạt** hành vi mà thiết kế cố tình sinh ra không? *(chặn L06)*
5. Chỉ số có phụ thuộc vào việc **đối tượng đo tự khai báo** không? *(chặn L07)*
6. Chỉ số này có **tautology** không — nghĩa là nó chỉ xác nhận đặc tả? *(chặn L02)*

### IMP-7 — Chaos trong CI

**Biện pháp.** Thêm một job chạy 3 kịch bản lỗi trên 50 case và khẳng định:
tỷ lệ báo động giả = 0 · hỏng âm thầm dưới crash = 0 · kết quả tái lập theo seed.

Chi phí ~30 giây mỗi lần chạy. Nó biến bốn phát hiện đắt giá nhất của WP8 thành **hàng rào tự động**
thay vì kiến thức nằm trong đầu một người.

---

## Phần 5 — Đưa vào luận văn ở đâu

| Nội dung | Chương | Cách trình bày |
|---|---|---|
| L01–L03, L05 *(vòng tròn, baseline)* | **4** — Thiết kế nghiên cứu | Trình bày như **lý do** của các quyết định thiết kế thí nghiệm, không phải như lỗi |
| L04 *(in-sample)* | **5** — Kết quả | Một hộp cảnh báo cạnh bảng hiệu chuẩn: vì sao báo cáo số trên test |
| L06, L07 *(định nghĩa chỉ số)* | **4** | Phần thao tác hóa: vì sao dùng selective prediction và sự thật nền |
| L14–L17 *(thống kê PSI)* | **5** — RQ3(b) | Bảng bốn cái bẫy + quy trình hiệu chuẩn ngưỡng. **Đây là phần có giá trị phương pháp luận cao nhất** |
| L08–L10 *(rò rỉ khái niệm giữa hai mốc)* | **4** | Bảng rà điều kiện theo mốc ở IMP-5 |
| Phần 3 *(cơ chế phát hiện)* | **5** — Thảo luận | Phản tư DSR: chạy sớm trên dữ liệu thật có hiệu suất phát hiện cao nhất |
| Giới hạn phủ của guard | **5** + Threats | Guard hiện chỉ phủ `prediction`; mở rộng cần T7.3 |

**Cách đóng khung khi bảo vệ.** Không trình bày đây là danh sách sai lầm. Trình bày là **quá trình
kiểm chứng nội tại của một nghiên cứu Design Science**: mỗi lỗi được phát hiện bằng một cơ chế cụ thể,
được sửa, và biện pháp phòng ngừa được cài lại vào artifact. Bốn cái bẫy PSI ở §2.6 tự chúng đã là một
đóng góp phương pháp nhỏ — chúng là thứ mà bất kỳ ai xây bộ giám sát drift cho DSS cũng sẽ gặp.
