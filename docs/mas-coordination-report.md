# Kiến trúc phối hợp đa tác tử và tính truy vết — đã chuyển thành Phụ lục B

> ⛔ **Bản nháp làm việc của tài liệu này đã được viết lại thành phụ lục luận văn.**
> Nội dung hiện hành: **[docs/thesis/phu-luc.md → Phụ lục B](thesis/phu-luc.md)**

Bản nháp cũ *(14/08/2026)* đã bị thay thế thay vì giữ song song, theo đúng bài học mà chính dự án ghi
lại ở [evaluation-handbook.md](evaluation-handbook.md): **duy trì hai bản của cùng một nội dung là cơ
chế đã sinh ra bẫy trích dẫn** phải rào lại ở `session-state.md` §4 và `status-checklist.md` §6.

## Phụ lục B trả lời gì

| Mục | Nội dung |
|---|---|
| **B.1** | Luận điểm: tính truy vết đạt được bằng cách làm cho trạng thái không truy vết được trở nên **không biểu đạt được** |
| **B.2** | Kiến trúc phối hợp — bốn cơ chế · kế hoạch dạng dữ liệu · tô-pô hình sao · mười tác tử · một phiên xử lý thật |
| **B.3** | **Bốn điều kiện của tính truy vết**: đầy đủ · bất biến · tự đủ · định địa chỉ ổn định — mỗi điều kiện kèm tầng cưỡng chế và chế độ hỏng |
| **B.4** | Khả năng giải thích như một **đại lượng đo được** — độ phân kỳ **40,61%**, và vì sao phần mất đi không ngẫu nhiên |
| **B.5** | Ranh giới hiệu lực — gồm điểm yếu **không có kiểm thử canh giữ điều kiện đầy đủ** |
| **B.6** | Bảng tổng: cơ chế ↔ tầng cưỡng chế ↔ kiểm thử ↔ số đo |

## Hai sửa chữa phát sinh khi viết phụ lục

| # | Vấn đề | Xử lý |
|---|---|---|
| 1 | Docstring của bộ dựng trace trỏ tới `tests-v3/test_explain_signature.py` — **tệp không tồn tại**. Guard vẫn chạy đúng ở `test_skeleton_e2e.py`, nhưng người kiểm chứng theo docstring sẽ không tìm thấy gì và kết luận nhầm là claim không có bằng chứng | ✅ Trỏ lại đúng hai test |
| 2 | Bản nháp ghi tầng chịu lỗi có **5 module**; nguồn chuẩn `cost_5_ma_nguon_MO_TA.csv` ghi **6** | ✅ Phụ lục B dùng số của artifact |
