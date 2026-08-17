# Kế hoạch kỹ thuật v3 — xây dựng từ ba câu hỏi nghiên cứu

> **Cơ sở duy nhất của tài liệu này:** [research-questions-objectives.md](research-questions-objectives.md)
> (bản 3 RQ / 3 MT). Không kế thừa cấu trúc mã nguồn cũ, không kế thừa quyết định công nghệ cũ.
>
> **Tài liệu này là nguồn chuẩn duy nhất cho mọi quyết định kỹ thuật.** Nó **thay thế**
> [technical-design-v2.md](technical-design-v2.md) — bản đó đã được đánh dấu lỗi thời và không được
> trích dẫn hay cài đặt theo nữa. Các đặc tả chi tiết còn hiệu lực của bản cũ đã được chuyển vào
> **Phụ lục A** của tài liệu này.
>
> **Quy tắc chi phối toàn bộ kế hoạch:** mỗi thành phần được xây phải **truy được về một câu hỏi nghiên
> cứu**. Thành phần không phục vụ RQ1, RQ2 hoặc RQ3 thì không nằm trong phạm vi, bất kể nó hợp lý về
> mặt kỹ thuật.
>
> **Phân rã thành công việc giao được:** [build-plan.md](build-plan.md) — 12 gói công việc, ~80 ngày
> công, kèm tiêu chí nghiệm thu, lịch theo tuần, năm điểm quyết định và đường cắt giảm.
>
> **Số hiệu câu hỏi nghiên cứu trong tài liệu này đã được đồng bộ sang bản 12/08/2026**
> *(RQ1 chịu lỗi · RQ2 thiết kế · RQ3 điều kiện kiểm soát)*. Bảng tra số hiệu cũ ↔ mới nằm ở
> [research-questions-objectives.md](research-questions-objectives.md) đầu tài liệu.

---

## Phần 0 — Điều kiện dữ liệu đã kiểm chứng và hệ quả kiến trúc

Cổng M0 đã chạy trên dữ liệu thật. Kết quả chi phối phần lớn thiết kế bên dưới.

Đơn vị phân tích là **case đơn hàng**, không phải dòng đánh giá thô — 551 đơn mang nhiều hơn một bản
ghi đánh giá, sau khử trùng còn 98.673 case. Cột dùng trong luận văn là cột case.

| Chỉ tiêu | Dòng thô | **Case đơn hàng** |
|---|---|---|
| Tổng số đánh giá | 99.224 | **98.673** |
| Đánh giá bất mãn (1–2★) | 14.575 — 14,69% | **14.475 — 14,67%** |
| Bất mãn **có** `review_content` — tầng A | 10.889 — 74,71% | **10.823 — 74,77%** |
| Bất mãn **không có** `review_content` — tầng B | 3.686 — 25,29% | **3.652 — 25,23%** |
| *(phụ)* Không một chữ nào, kể cả tiêu đề | 3.581 — 24,56% | 3.547 — 24,50% |

> **Cặp số cũ "74,71% / 24,6%" đã bị rút.** Nó trộn hai định nghĩa — tử số tính theo `review_content`,
> mẫu số tính theo *không có cả nội dung lẫn tiêu đề* — nên hai con số không bù nhau. Định nghĩa thống
> nhất là **theo `review_content`**; xem `research-questions-objectives.md §0.1`.

**Hệ quả kiến trúc quan trọng nhất: chuỗi xử lý tách làm hai giai đoạn theo hai mốc quyết định.** Lý do
là ràng buộc C4 — `review_comment_message` được viết cùng lúc với `review_score`, nên tại T₃ (trước khi
khách viết đánh giá) **không tồn tại bất kỳ bằng chứng văn bản nào**.

| | **Giai đoạn 1 — T₃** | **Giai đoạn 2 — T₄** |
|---|---|---|
| Nhiệm vụ | Dự báo rủi ro bất mãn | Quy kết nguyên nhân + sinh hành động |
| Bằng chứng | Chỉ đặc trưng bảng | Đặc trưng bảng **+ văn bản (74,77%)** |
| Agent tham gia | Analytics, Prediction, Rule Agent | Toàn bộ Analyst pool, Recommendation, Critic, Arbiter, Rule Agent |
| Tầng A/B | Toàn bộ là tầng B | A 74,77% · B 25,23% |
| Phục vụ | H1 (điều kiện kiểm soát) | **RQ3** |

Hai giai đoạn **dùng chung** toàn bộ hạ tầng: cùng message envelope, cùng nhật ký, cùng seam tiêm lỗi,
cùng cơ chế suy giảm. Chúng khác nhau ở kế hoạch định tuyến và ở `FeatureSet` được cấp — không phải hai
hệ thống riêng biệt.

**Ba đặc trưng bị cấm ở giai đoạn 1** vì rò rỉ nhãn: `review_lag_days`, `has_comment`, và mọi đặc trưng
dẫn xuất từ văn bản. Riêng `has_comment` nguy hiểm và dễ lọt: tỷ lệ để lại bình luận là 76,5% ở mức 1★
so với 31,2% ở mức 4★, nên bản thân sự hiện diện của bình luận đã là tín hiệu mạnh về nhãn.

---

## Phần 1 — Suy ra yêu cầu kỹ thuật từ ba câu hỏi

Đây là bước quan trọng nhất. Mọi quyết định phía sau đều là hệ quả của bảng này.

| RQ | Điều phải chứng minh được | Yêu cầu kỹ thuật bắt buộc |
|---|---|---|
| **RQ1** — chịu lỗi và cái giá của nó *(trục chính)* | Tiêm lỗi có kiểm soát, đo được độ nhạy/độ trễ phát hiện, đo được overhead | (1) **Seam tiêm lỗi** ở mọi lời gọi tác tử; (2) output guard 4 tầng; (3) supervisor + circuit breaker + degradation ladder; (4) đo latency theo từng span; (5) baseline Monolithic-Complete chạy **cùng seam tiêm lỗi** |
| **RQ2** — thiết kế: truy vết được, trung thực về độ tin cậy | Mọi quyết định dựng lại được từ nhật ký giao tiếp; không quyết định tự động nào sinh ra khi hệ đang suy giảm | (6) Message envelope + **10** performative, có `conversation_id` và `in_reply_to`; (7) nhật ký message **bền vững, append-only**; (8) bộ dựng trace **chỉ đọc nhật ký**; (9) `degradation_level` là trường bắt buộc của `Decision`, cưỡng chế ở tầng kiểu dữ liệu |
| **RQ3** — điều kiện kiểm soát: không đánh đổi độ chính xác | So sánh công bằng với một bộ phân loại đơn khối, trên gold set, ở hai tình huống khó | (10) Contract Net hai pha có ngân sách tính toán; (11) đầu ra **đa nhãn** + `bid_entropy`; (12) `REFUSE` có điều kiện kiểm chứng được; (13) hiệu chuẩn bid riêng từng analyst; (14) **tầng capability dùng chung** giữa MAS và baseline; (15) công cụ gold set; (16) chỉ số selective prediction |

**Ba hệ quả kiến trúc rút ra ngay từ bảng trên:**

1. **Nhật ký message là cấu trúc dữ liệu trung tâm**, không phải log phụ trợ. RQ2 đo trên nó, RQ1 dùng
   nó để dựng lại chuyện gì đã xảy ra khi tiêm lỗi. Nó phải là sản phẩm hạng nhất, có schema, có test.
2. **Tầng capability phải tách khỏi tầng agent.** RQ1 và RQ3 đều yêu cầu baseline dùng *chung* mô hình
   với MAS-DSS. Nếu mô hình bị nhúng bên trong agent thì không thể dùng chung, và phép so sánh mất
   tính công bằng ngay từ kiến trúc.
3. **Seam tiêm lỗi phải là một phần của thiết kế, không phải thứ chắp vá lúc chạy thí nghiệm.** RQ1 là
   đóng góp chính; nếu tiêm lỗi phải sửa mã nguồn thì thí nghiệm không tái lập được.

---

## Phần 2 — Ba quyết định công nghệ, xét lại từ đầu

Tiêu chí xét: *thành phần này phục vụ RQ nào, và nếu bỏ đi thì RQ nào không trả lời được?*

### 2.1 Chế độ chạy: một tiến trình, bất đồng bộ, xác định

Phạm vi nghiên cứu đã tuyên bố hệ thống chạy **theo lô, ngoại tuyến**, và bác bỏ mọi tuyên bố thời gian
thực. Không RQ nào yêu cầu nhiều tiến trình, phân tán, hay xử lý đồng thời quy mô lớn.

| Phương án | Phục vụ RQ nào | Kết luận |
|---|---|---|
| Một tiến trình Python + `asyncio` | Đủ cho cả ba | ✅ **Chọn** |
| Nhiều tiến trình / message broker ngoài | Không RQ nào yêu cầu; làm việc tiêm lỗi khó tái lập | ❌ Loại khỏi tuyến chính |

Điểm quan trọng: chạy trong một tiến trình khiến RQ1 **dễ làm hơn và chặt hơn**, vì việc tiêm lỗi trở
nên tất định — cùng seed cho ra cùng chuỗi sự kiện. Một hệ phân tán sẽ đưa vào tính bất định về thứ tự
mà nghiên cứu không kiểm soát được và cũng không quan tâm.

### 2.2 Tự viết orchestrator, loại bỏ engine điều phối bên ngoài

**Quyết định: tự viết.** Đây là quyết định **đảo ngược** lựa chọn hybrid trong bản v2. Vì nó gây tranh
luận và chắc chắn bị hội đồng hỏi, mục này ghi lại lập luận **cả hai chiều**, chứ không chỉ chiều ủng hộ.

#### a. LangGraph cung cấp gì, và câu hỏi nghiên cứu nào cần đến

| Tính năng | RQ cần? | Đánh giá |
|---|---|---|
| `StateGraph` — node, conditional edge, reducer | RQ2, RQ3 cần *chức năng* này | Nhưng cần chức năng, không cần thư viện: kế hoạch chỉ 7 bước tuyến tính có điều kiện |
| Checkpoint / resume sau crash | **Không** | Chạy theo lô, mỗi case độc lập, tất định — chạy lại rẻ hơn khôi phục |
| `interrupt` cho human-in-the-loop | **Không** | "Chuyển cho người" chỉ là một giá trị của `Decision`, không cần treo tiến trình |
| Retry policy theo node | **Phản tác dụng** | RQ1 cần chính sách riêng: chỉ retry lỗi *transient*, tuyệt đối không retry lỗi deterministic |
| Fan-out / fan-in theo super-step | Có cần | Nhưng đây đúng bằng `asyncio.gather` |
| Streaming state, subgraph, tích hợp quan sát | **Không** | Tiện nghi vận hành, không phục vụ RQ nào |

Chỉ hai dòng đầu là thứ thật sự dùng đến.

#### b. Ba lập luận quyết định

1. **Tính tất định là nền của RQ1, và phải chứng minh được.** Toàn bộ kết quả chaos chỉ có giá trị nếu
   cùng seed cho ra cùng kết quả. Một engine tổng quát đưa vào ba nguồn bất định nằm ngoài tầm kiểm
   soát: thứ tự hoàn thành các nhánh song song trong một super-step, I/O của checkpointer, và hành vi
   retry nội bộ. Có thể ghim lại được, nhưng khi bị hỏi *"làm sao bảo đảm hai lần chạy cho cùng con
   số"*, câu trả lời **"tôi kiểm soát toàn bộ vòng thực thi"** mạnh hơn **"tôi đã cấu hình thư viện cho
   nó tất định"**.
2. **Một nguồn sự thật.** Trong thiết kế này, **nhật ký message là nguồn sự thật** — RQ2 đo trên nó,
   DP4 buộc trace chỉ được dựng từ nó. LangGraph lấy state object làm trung tâm theo thiết kế của nó.
   Hai mô hình không xung đột về kỹ thuật nhưng tạo ra hai biểu diễn song song của cùng một tiến trình
   phải liên tục giữ đồng bộ. Chính bản v2 đã xếp "hai nguồn sự thật" là rủi ro nguy hiểm nhất của
   phương án hybrid — cảnh báo đó áp dụng cho chính nó.
3. **Quy thuộc đóng góp.** Đóng góp của luận văn là **tầng phối hợp và giám sát**. Nếu tầng đó chạy
   trên một engine có sẵn, câu hỏi *"phần nào là của tác giả"* trở nên khó trả lời gọn. Dùng framework
   để tiết kiệm công lại làm loãng đúng thứ muốn tuyên bố.

#### c. Lập luận ngược — bốn điểm đã cân nhắc

| Phản biện | Đánh giá |
|---|---|
| **"Phát minh lại bánh xe"** | Có thật, nhưng nhỏ hơn rủi ro đối xứng ở lập luận 3. Đã có câu trả lời chuẩn bị ở mục (e) |
| **Nguy cơ tự viết máy trạng thái tệ** | Rủi ro thật. Giảm thiểu bằng ràng buộc thiết kế: kế hoạch ở **dạng dữ liệu tuyến tính có điều kiện** — không chu trình, không nhánh lồng nhau. Nếu bài toán cần đồ thị phức tạp thì lập luận này đổ |
| **Mất cơ hội trích dẫn một framework có tiếng ở Chương 3** | Chương 3 vẫn trích Smith (1980), Hayes-Roth (1985), FIPA-ACL, mô hình supervision của Erlang/OTP — nền học thuật vững hơn một thư viện ba năm tuổi |
| **Nếu phạm vi mở rộng sau này phải viết lại** | Chi phí ~300 dòng, chấp nhận được; và đã có bảo hiểm rẻ ở mục (d) |

#### d. Chi phí thực và cách cài đặt

Ước lượng ban đầu là **khoảng 300 dòng**, không phải 150 như phác thảo đầu tiên. **Số đo được sau khi
xây xong: 632 dòng cho toàn tầng phối hợp (9 module) và 448 dòng cho tầng chịu lỗi (6 module)** — đếm
bằng `ast`, đã loại docstring. Ước lượng hụt khoảng một nửa, và hụt đúng theo hướng làm quyết định "tự
viết" trông rẻ hơn thực tế; điều đó phải được nêu thẳng chứ không lặng lẽ thay số.

| Thành phần | Dòng ước tính |
|---|---|
| Định nghĩa kế hoạch dạng dữ liệu (2 plan: giai đoạn 1 và 2) | ~60 |
| Bộ thực thi: duyệt bước, đánh giá điều kiện rẽ nhánh, cập nhật blackboard | ~120 |
| Fan-out/gather cho phiên đấu thầu + timeout theo từng lời gọi | ~60 |
| Chính sách retry và phân loại lỗi transient / deterministic | ~50 |
| Bỏ qua case đã xong khi chạy lại (thay cho checkpoint) | ~15 |

**Kế hoạch là dữ liệu, không phải mã điều khiển** — đây là ràng buộc bắt buộc, không phải gợi ý. Bản
đang chạy tại `system/plan.py`:

```python
STAGE2_PLAN: Plan = (
    Step("analytics",     agent="Analytics"),
    Step("prediction",    agent="Prediction"),
    Step("contract_net",  fanout="AnalystPool", budget=budget_for,
         protocol="contract_net"),
    Step("recommend",     agent="Recommendation", on=lambda bb: bool(bb.causes)),
    Step("critique",      agent="PolicyCritic",   on=lambda bb: bb.proposal is not None),
    Step("arbitrate",     agent="Arbiter",
         on=lambda bb: bb.critique is not None and bb.critique.challenged),
    Step("rules",         agent="RuleAgent"),
)
```

> **Điều kiện `on: risk >= MEDIUM` của bước đấu thầu đã bị gỡ, và đó là một sửa lỗi thiết kế.** Tại T₄
> case **đã có** đánh giá 1–2★ — bất mãn là *sự kiện đã xảy ra*, không còn là thứ cần dự báo. Chặn quy
> kết nguyên nhân sau một dự báo PR-AUC 0,40 khiến **94,7% case không bao giờ được phân tích** và toàn
> bộ RQ3 mất đối tượng nghiên cứu. "Đường tắt cho case rủi ro thấp" vẫn có nghĩa, nhưng nó thuộc
> **giai đoạn 1 @ T₃** — nơi ta thực sự đang dự báo. Ngân sách tính toán vẫn thay đổi theo mức rủi ro
> nên Contract Net không mất tính phân bổ tài nguyên.

**Bảo hiểm rẻ cho trường hợp phải đổi ý:** bộ thực thi có chữ ký hàm tường minh
`execute(plan, case, invoke_fn) -> Blackboard` (§5.5). Nếu về sau cần đổi sang một engine bên ngoài,
chỉ phải viết một lớp adapter, không đụng vào `agents/`, `reliability/` hay `chaos/`. Chi phí trừu
tượng hóa này khoảng 20 dòng.

#### e. Câu trả lời chuẩn bị sẵn cho hội đồng

> *"Nghiên cứu không dùng engine điều phối có sẵn vì ba lý do. Thứ nhất, câu hỏi nghiên cứu chính là về
> hành vi của hệ thống khi tác tử lỗi, nên vòng thực thi — nơi lỗi được tiêm và được xử lý — phải nằm
> trong phạm vi khảo sát chứ không phải trong một thư viện. Thứ hai, Design Science yêu cầu artifact
> tái lập được; kiểm soát trọn vòng thực thi cho phép bảo đảm hai lần chạy cùng cấu hình cho kết quả
> trùng khớp đến từng byte. Thứ ba, kế hoạch điều phối trong bài toán này chỉ gồm bảy bước tuyến tính
> có điều kiện; chi phí tự cài đặt đo được là **632 dòng cho tầng phối hợp** — cao hơn ước lượng ban
> đầu khoảng gấp đôi, và chúng tôi báo cáo con số đo được chứ không phải con số ước lượng. Đó vẫn thấp
> hơn chi phí kiểm soát tính bất định do một engine tổng quát mang lại. Các tính năng còn lại của những
> engine đó — checkpoint, resume, treo chờ người — không được câu hỏi nghiên cứu nào yêu cầu."*

#### f. Tiêu chí đảo ngược quyết định

Quay lại engine bên ngoài nếu **bất kỳ** điều nào sau đây trở thành đúng:

- Phạm vi mở sang chạy trực tuyến hoặc nhiều tiến trình.
- Kế hoạch điều phối vượt quá ~15 bước, hoặc cần chu trình thật sự.
- Một lần chạy đầy đủ vượt vài giờ khiến resume từng phần trở nên cần thiết *(hiện đã có phương án rẻ:
  bỏ qua theo `case_id` đã hoàn tất)*.
- Xuất hiện yêu cầu human-in-the-loop **đồng bộ** — người phải trả lời giữa chừng thì tiến trình mới
  đi tiếp.

### 2.3 Lưu trữ: tệp và SQLite, không dịch vụ nền

| Nhu cầu | Do RQ nào | Phương án |
|---|---|---|
| Dataset, feature, split | Cả ba | **Parquet** trên đĩa |
| Nhật ký message, case store, decision trace | RQ1, RQ2 | **SQLite** — một tệp, có schema, truy vấn được bằng SQL, không cần dịch vụ |
| Working memory của case | RQ2 | Đối tượng trong bộ nhớ tiến trình, ghi ra SQLite khi kết thúc case |
| Kết quả thí nghiệm chaos | RQ1 | Parquet + tệp cấu hình kịch bản |
| Quan sát độ trễ | RQ1 vế (d) | Bản ghi span tự viết, ghi vào SQLite |

**Bị loại khỏi tuyến chính:** Redis, PostgreSQL, hệ truy vết phân tán, `docker-compose`. Không RQ nào
cần đến chúng, và mỗi dịch vụ nền là một điểm hỏng khiến thí nghiệm khó tái lập trên máy người khác.

**Lợi ích trực tiếp cho luận văn:** toàn bộ nghiên cứu tái lập được bằng `pip install` và một lệnh chạy.
Với Design Science, khả năng tái lập là yêu cầu bắt buộc chứ không phải tiện nghi.

---

## Phần 3 — Kiến trúc phân tầng

Nguyên tắc phụ thuộc: **mũi tên chỉ đi xuống**. Tầng dưới không được biết gì về tầng trên.

```
┌──────────────────────────────────────────────────────────────────┐
│  cli/            Điểm chạy: dựng dữ liệu, huấn luyện, chạy hệ,   │
│                  chạy đánh giá, chạy chaos                        │
├──────────────────────────────────────────────────────────────────┤
│  evaluation/     Chỉ số, đánh giá quy kết (chỉ nhận gold set),   │
│  chaos/          phân loại lỗi, bộ tiêm lỗi, kịch bản            │
├───────────────────────────────┬──────────────────────────────────┤
│  system/  MAS-DSS             │  baselines/  MIS · Single-ML ·   │
│    orchestrator, protocol,    │              Monolithic-Complete │
│    reliability, explain       │                                   │
├───────────────────────────────┴──────────────────────────────────┤
│  agents/         Vỏ mỏng: chính sách bid / REFUSE / degradation   │
├──────────────────────────────────────────────────────────────────┤
│  capabilities/   ★ DÙNG CHUNG giữa MAS-DSS và baselines ★        │
│                  Mô hình bảng, encoder+head văn bản, z-score giá, │
│                  rule engine — thuần hàm, không biết gì về agent  │
├──────────────────────────────────────────────────────────────────┤
│  runtime/        Actor, hộp thư, bus trong tiến trình, ngân sách, │
│                  seam tiêm lỗi, đo span                           │
├──────────────────────────────────────────────────────────────────┤
│  core/           Ontology, Message, Performative, Bid, Evidence,  │
│                  Decision, DegradationLevel                       │
├──────────────────────────────────────────────────────────────────┤
│  data/           Nạp dữ liệu, feature có available_at, split thời │
│                  gian, nhãn                                       │
└──────────────────────────────────────────────────────────────────┘
```

**Tầng `capabilities/` là biểu hiện kiến trúc của yêu cầu công bằng.** Vì baseline và MAS-DSS cùng
`import` từ đây, không tồn tại khả năng "vô tình cho MAS mô hình tốt hơn". Đây không phải quy ước đạo
đức nghiên cứu — đây là ràng buộc do cấu trúc mã nguồn áp đặt.

**Tầng `agents/` phải mỏng.** Một agent chỉ làm ba việc: nhận message, quyết định `ACT` / `REFUSE`, gọi
capability, đóng gói kết quả thành `Bid` hoặc `INFORM`. Mọi logic học máy nằm ở tầng dưới. Nếu một
agent dài quá khoảng 80 dòng, gần như chắc chắn có logic bị đặt sai tầng.

---

## Phần 4 — Cấu trúc thư mục

> **Bản này phản ánh mã nguồn thực tế tại `src-v3/masdss/`** *(85 tệp Python, 11.047 dòng)*, không phải
> bố trí dự kiến. Bốn khác biệt so với phác thảo ban đầu được ghi ngay trong cây, kèm lý do.

```
src-v3/masdss/
├── core/
│   ├── ontology.py         # Cause (3 nhãn + unknown), Evidence, Bid, Declaration,
│   │                       #   Critique, Action, OrderCase, DegradationLevel
│   ├── message.py          # Message envelope + 10 Performative
│   ├── decision.py         # Decision — degradation_level là trường BẮT BUỘC
│   ├── components.py       # ★ tên THÀNH PHẦN LOGIC — từ vựng chung của hai kiến trúc
│   └── errors.py           # phân biệt TransientError vs DeterministicError
│
├── data/
│   ├── load.py             # đọc Olist thô → bảng chuẩn hóa
│   ├── features.py         # mỗi feature khai báo available_at ∈ {T1,T2,T3,T4}
│   ├── featureset.py       # FeatureSet(decision_point) lọc theo mốc; chặn rò rỉ T4→T3
│   ├── labels.py           # nhãn bất mãn; weak label nguyên nhân (chỉ để pre-train)
│   ├── splits.py           # chia theo thời gian, KHÔNG ngẫu nhiên
│   └── export.py           # xuất tệp đặc trưng vật lý; load_split() là đường vào duy nhất
│
├── capabilities/           # ★ dùng chung MAS-DSS ↔ baselines ★
│   ├── risk_model.py       # LightGBM + hiệu chuẩn isotonic
│   ├── calibration.py      # isotonic dùng chung cho risk model và bid
│   ├── ood.py              # phát hiện ngoài phân phối
│   ├── cause_head.py       # LexiconCauseHead (bản tạm) · TfidfCauseHead (đang dùng)
│   ├── delivery_signal.py  # GBM trên đặc trưng logistics
│   ├── price_signal.py     # z-score giá/phí — CÒN LẠI cho baseline, không agent nào dùng
│   └── rules.py            # rule engine đọc YAML
│
├── runtime/
│   ├── actor.py            # danh tính, hộp thư, chính sách ACT/DEFER/DELEGATE/REFUSE
│   ├── faults.py           # ★ SEAM TIÊM LỖI — mọi lời gọi agent đi qua đây
│   ├── message_log.py      # nhật ký SQLite append-only (trigger chặn UPDATE/DELETE)
│   └── tracing.py          # span thủ công: 1 case = 1 trace, 1 message = 1 span
│
├── agents/                 # vỏ mỏng: mỗi tệp gom nhiều tác tử cùng vai trò
│   ├── base.py             # AnalystAgent · TextAnalystAgent · DeclaringAgent
│   ├── core_agents.py      # Analytics · Prediction · Recommendation · RuleAgent · CaseManager
│   ├── critic.py           # PolicyCritic · Arbiter
│   ├── skeleton.py         # khung tác tử tối giản dùng trong test
│   └── analysts/pool.py    # BA analyst: Delivery · Quality · Service
│
├── system/
│   ├── plan.py             # STAGE1_PLAN, STAGE2_PLAN — kế hoạch ở DẠNG DỮ LIỆU
│   ├── orchestrator.py     # execute(plan, case, invoke_fn) + phiên Contract Net  ← §2.2
│   ├── contract_net.py     # phân bổ knapsack dưới ràng buộc ngân sách
│   ├── blackboard.py       # working memory của case
│   ├── app.py              # nối capability → agent → registry; dùng chung với baseline
│   ├── reliability/
│   │   ├── guards.py       # schema · statistical (sanity+calibration) · consistency
│   │   ├── health.py       # phương sai bằng 0, PSI — bắt lỗi Byzantine
│   │   ├── breaker.py      # circuit breaker + Supervisor (gộp, không tách tệp)
│   │   ├── reference.py    # nạp phân phối tham chiếu sạch, báo cáo phạm vi phủ
│   │   └── pipeline.py     # bọc invoke_fn: breaker → gọi → guard → ghi nhận
│   └── explain.py          # dựng decision trace CHỈ từ nhật ký message
│
├── baselines/
│   ├── simple.py           # MISBaseline (báo cáo mô tả) + SingleMLBaseline (chỉ dự báo)
│   └── monolithic.py       # ★ ĐA NHÃN, cùng capability, cùng YAML, không có tầng MAS
│
├── goldset/
│   ├── sample.py           # lấy mẫu phân tầng
│   └── agreement.py        # Cohen's κ + kiểm tra tính độc lập của hai bản gán
│
├── evaluation/
│   ├── attribution.py      # ★ CHỈ nhận gold set — truyền weak label vào phải raise
│   ├── selective.py        # đường cong risk–coverage, độ chính xác theo độ phủ
│   ├── forecasting.py      # PR-AUC, kiểm định tương đương (H1)
│   ├── coordination.py     # số message, bid_entropy, tỷ lệ đi đường tắt, chất lượng/ms
│   ├── resilience.py       # hỏng âm thầm, độ trễ phát hiện, so sánh hai kiến trúc
│   ├── trace_divergence.py # đo độ phân kỳ giữa trace dựng từ nhật ký và hành vi thật (DP4)
│   └── cost.py             # latency p50/p95, số thành phần, quy mô mã nguồn
│
├── chaos/
│   ├── injector.py         # Crash · Hang · ConstantOutput · Bias · Null — có seed
│   ├── scenarios.py        # 5 nhóm lỗi × 3 mức
│   └── runner.py           # chạy cùng kịch bản trên MAS-DSS và Monolithic
│
└── cli/                    # 16 điểm chạy; xem `python -m masdss.cli.<tên> --help`
    run_system.py · run_evaluation.py · run_attribution.py · run_chaos.py · train.py
    build_goldset*.py · check_goldset.py · check_validation.py · export_features.py …
```

**Bốn khác biệt có chủ đích so với phác thảo ban đầu, mỗi cái có lý do:**

| Phác thảo | Thực tế | Lý do |
|---|---|---|
| `capabilities/text_encoder.py` — BERTimbau | **Không tồn tại**; `cause_head.py` dùng TF-IDF | T3.3 bị chặn bởi quyết định không cài `torch`. `TfidfCauseHead` đạt macro-F1 0,4730 so với 0,2196 của bản lexicon, đủ để dựng toàn bộ đường ống |
| `runtime/bus.py`, `runtime/budget.py` | **Không tồn tại** | Không có bus: mọi trao đổi đi qua orchestrator theo tô-pô hình sao. Ngân sách nằm ở `system/plan.py:budget_for` vì nó là **tham số của kế hoạch**, không phải của runtime |
| `reliability/supervisor.py`, `degradation.py` | Gộp vào `breaker.py` và `blackboard.py` | `Supervisor` chỉ là bộ quản lý breaker + chính sách retry (~35 dòng); thang suy giảm là `Blackboard.degrade()` + bất biến trong `Decision.__post_init__` |
| `memory/precedent.py`, `goldset/annotate_app.py`, `chaos/taxonomy.py` | **Không xây** | Nằm trong danh sách "cố ý không xây" ở §7; gán nhãn làm trên CSV/Sheets nên không cần giao diện riêng |

---

## Phần 5 — Năm giao diện quyết định toàn bộ thiết kế

Nếu năm giao diện này đúng, phần còn lại chỉ là công việc thi công. Nếu sai, phải làm lại.

### 5.1 `Decision` — nơi RQ2 được cưỡng chế

```python
@dataclass(frozen=True)
class Decision:
    case_id: str
    decision_point: DecisionPoint          # T3 hay T4 — quyết định bất biến nào được áp
    risk: RiskLevel
    causes: tuple[CauseAssignment, ...]    # ĐA NHÃN — không bao giờ là một giá trị đơn
    action: Action
    degradation_level: int                 # BẮT BUỘC — không có giá trị mặc định
    needs_human_review: bool
    conversation_id: UUID                  # khóa để dựng lại trace từ nhật ký
    multi_cause: bool = False
    notes: tuple[str, ...] = ()
```

Không đặt giá trị mặc định cho `degradation_level`. Người viết mã **buộc phải** khai báo mức suy giảm ở
mọi nơi tạo `Decision`. **Bốn bất biến** được kiểm ngay trong `__post_init__`, nên không tầng nào có
thể "quên" chúng:

| # | Bất biến | Cưỡng chế |
|---|---|---|
| 1 | `degradation_level > 0` ⟹ `needs_human_review is True` | **DP1** — hệ thống không bao giờ im lặng cho ra quyết định rác |
| 2 | `action = escalate_to_human` ⟹ `needs_human_review is True` | báo cáo và hành vi thực tế không được phân kỳ |
| 3 | Tại **T₄**, `causes` rỗng hoặc toàn `unknown` ⟹ phải chuyển giao cho người | **DP3** — quy kết thất bại là hành vi đúng về tri thức luận. Chỉ áp ở T₄ vì T₃ chưa hề có nhiệm vụ quy kết |
| 4 | ≥2 nguyên nhân vượt ngưỡng ⟹ `multi_cause is True` | **DP2** — không được đánh mất thông tin mà cơ chế cạnh tranh sinh ra để bắt |

Vi phạm bất biến 1–3 phát `DegradedAutonomyError`. `to_row()` là **biểu diễn chính tắc** dùng cho test
tái lập: không chứa dấu thời gian, không chứa độ trễ.

### 5.2 `Capability` — nơi tính công bằng của phép so sánh được bảo đảm

```python
class Capability(Protocol):
    cost_ms: float                     # đầu vào của bài toán phân bổ ngân sách (RQ3)
    def can_handle(self, case) -> bool # cơ sở kiểm chứng được của REFUSE
    def run(self, case) -> Output      # thuần hàm, không side effect, không biết agent
```

Capability không import bất cứ thứ gì từ `agents/`, `system/` hay `chaos/`. Ràng buộc này được kiểm tra
bằng một test tĩnh về đồ thị phụ thuộc, chạy trong CI.

### 5.3 Seam tiêm lỗi — nơi RQ1 được làm cho khả thi

```python
async def invoke(handler, message, *, injector=None) -> Message:
    component = component_of(handler.agent_id)   # tên THÀNH PHẦN LOGIC, không phải agent_id
    injector?.before(component, message)         # crash · treo quá hạn · trễ
    out = await asyncio.wait_for(_run(), timeout=message.deadline_ms / 1000)
    out = injector?.after(component, out)        # Byzantine: hằng số · lệch bid · đảo nhãn
    return out
```

**Mọi** lời gọi tác tử — của MAS-DSS lẫn của Monolithic-Complete — đi qua đúng hàm này. Nhờ vậy cùng
một kịch bản lỗi áp được lên hai kiến trúc mà không phải viết hai bộ mã tiêm lỗi, và giao thức so sánh
của RQ1 trở nên đúng theo cấu trúc chứ không theo lời hứa.

**Hai chi tiết đã đổi so với phác thảo, cả hai đều bắt buộc:**

- Kịch bản lỗi phát biểu theo **thành phần logic** (`crash:prediction`), không theo `agent_id`. Kiến
  trúc đơn khối **không có tác tử nào**, nên một kịch bản theo `agent_id` chỉ áp được lên một bên và hai
  con số hỏng âm thầm không so sánh được. Bảng ánh xạ nằm ở `core/components.py`.
- Độ trễ nhân tạo được áp **bên trong** phạm vi `wait_for`, nên vượt hạn chót sinh ra timeout **thật** —
  task bị hủy. Bản v0 đo độ trễ *sau khi* tác tử chạy xong, nên một tác tử treo làm treo cả chuỗi.
  Kiến trúc đơn khối không có hạn chót nào nên nó chỉ **chậm đi**, không bị hủy: đó là thất bại về
  **tính sống**, không phải quyết định sai, và vì vậy không được tính là hỏng âm thầm.

Bộ tiêm lỗi nhận một seed. Cùng seed, cùng dữ liệu, cùng cấu hình thì cho cùng chuỗi sự kiện — điều kiện
để kết quả chaos đưa vào luận văn được.

### 5.4 Nhật ký message — nguồn duy nhất để dựng trace

```python
class MessageLog:
    def append(self, msg: Message) -> None
    def conversation(self, cid: UUID) -> list[Message]
```

`system/explain.py` nhận **đúng một tham số**: `conversation_id`. Nó không được nhận `case`, không được
nhận `blackboard`. Ràng buộc chữ ký hàm này chính là DP4 — nếu trace dựng được chỉ từ nhật ký thì nó
không thể phân kỳ với hành vi thật.

### 5.5 `Executor` — nơi quyết định "tự viết orchestrator" được cô lập

```python
async def execute(plan: list[Step], case: OrderCase, invoke_fn) -> Blackboard
```

Ba ràng buộc bắt buộc, mỗi ràng buộc phục vụ một mục đích cụ thể:

| Ràng buộc | Phục vụ |
|---|---|
| `plan` là **dữ liệu thuần** (danh sách `Step` có điều kiện), không phải mã điều khiển | Kế hoạch kiểm tra được, so sánh được, và in ra được vào phụ lục luận văn |
| Mọi lời gọi tác tử đi qua `invoke_fn` được truyền từ ngoài vào | Seam tiêm lỗi (§5.3) cắm vào đây; chaos harness không cần sửa orchestrator |
| Bộ thực thi **không** import gì từ `agents/`, `chaos/`, `evaluation/` | Đổi engine sau này chỉ cần một adapter, không lan sang tầng khác |

Ràng buộc thứ ba là **bảo hiểm cho quyết định §2.2**: nếu phạm vi mở rộng và phải chuyển sang engine
bên ngoài, phần phải viết lại được giới hạn trong đúng một hàm.

---

## Phần 6 — Lộ trình thi công

Thứ tự được sắp theo **rủi ro giảm dần**, không theo độ dễ. Hạng mục nào có khả năng làm hỏng cả nghiên
cứu thì làm trước.

| GĐ | Nội dung | Tiêu chí ra (exit criteria) | Phục vụ |
|---|---|---|---|
| **M0** ✅ | **Kiểm chứng dữ liệu.** Thống kê tỷ lệ đơn bất mãn không có bình luận | **Đạt:** 25,23% không văn bản · 74,77% có văn bản (§0). Ngưỡng dừng 50% không chạm tới. Phát hiện kèm theo: mâu thuẫn T₃ ↔ bằng chứng văn bản → chốt **hai mốc T₃/T₄** | RQ3 |
| **M0b** ✅ | Loại `review_lag_days` và `has_comment` khỏi T₃; khai báo `available_at` cho mọi feature; split theo thời gian | Test rò rỉ chạy xanh trên cả ba mốc T₂/T₃/T₄ | RQ3 |
| **M0′** 🟢 | **Khởi động gold set** — chạy song song suốt dự án | Bộ lấy mẫu phân tầng **không cân xứng 250 tầng A / 150 tầng B** ✅ · gán nhãn trên CSV/Sheets thay cho giao diện riêng ✅ · **bộ nhãn cuối 300 dòng chưa gán** ⬜ | RQ3 |
| **M1** ✅ | `core/` + `data/` + `capabilities/` | Mô hình rủi ro và head nguyên nhân huấn luyện xong; `FeatureSet(T2)` và `FeatureSet(T3)` đều chạy; **không rò rỉ feature** | RQ2, RQ3 |
| **M2** ✅ | **Monolithic-Complete trước MAS-DSS** | Baseline chạy end-to-end, **đa nhãn**, dùng chính capability của M1 | RQ1, RQ3 |
| **M3** ✅ | `runtime/` + `agents/` + orchestrator; nhật ký message; `explain.py` | Một case đi trọn chuỗi; trace dựng lại được **chỉ từ nhật ký** | **RQ2** |
| **M4** 🟡 | `contract_net.py` — CFP hai pha, ngân sách, hiệu chuẩn bid, đa nhãn | Hai pha ✅ · ngân sách theo bội số ✅ · `bid_entropy` đo được ✅ · **hiệu chuẩn isotonic riêng từng analyst (T7.3b) còn chặn bởi gold set** ⬜ | **RQ3** |
| **M5** ✅ | `reliability/` — guard, health, breaker, supervisor, degradation ladder | Bất biến "không quyết định tự động khi suy giảm" được test bao phủ | **RQ1, RQ2** |
| **M6** ✅ | `chaos/` — phân loại lỗi, bộ tiêm, 5 nhóm × 3 mức, runner hai kiến trúc | Cùng kịch bản chạy trên hai hệ; **kiểm tái lập theo seed chưa chạy lại sau khi đổi mốc T₃ (T9.4)** ⬜ | **RQ1** |
| **M7** 🟢 | `evaluation/` đầy đủ + phân tích độ nhạy T₂/T₃ và ngưỡng nhãn | Sinh được toàn bộ bảng số cho Chương 5 bằng một lệnh ✅ · mọi số mang cờ `citable=False` cho tới khi có gold set thật | Cả ba |

**Đường tới hạn: M0 → M0′ → M1 → M2 → M3 → M5 → M6.**

Hai điểm đáng chú ý trong thứ tự này:

- **M2 đứng trước M3** — xây baseline *trước* hệ chính. Lý do: baseline dùng chung capability, nên xây
  nó trước sẽ ép tầng `capabilities/` phải thật sự độc lập với tầng agent. Nếu xây MAS trước, gần như
  chắc chắn mô hình sẽ bị nhúng vào agent và việc tách ra sau đó rất tốn công.
- **M5 đứng trước M6** — không thể tiêm lỗi vào một hệ chưa có cơ chế phản ứng với lỗi.

Nếu thiếu thời gian, cắt theo thứ tự: `memory/precedent.py` trước, rồi `policy_critic.py` và
`arbiter.py`. **Không được cắt M0′, M2, M5, M6.**

---

## Phần 7 — Những gì cố ý không xây

Danh sách này tồn tại để chặn việc mở rộng phạm vi ngoài kế hoạch. Mỗi mục kèm điều kiện đảo ngược.

| Không xây | Vì sao | Xây khi nào |
|---|---|---|
| Dịch vụ nền (Redis, PostgreSQL, hệ truy vết phân tán) | Không RQ nào cần; làm giảm khả năng tái lập | Khi phạm vi mở sang chạy trực tuyến |
| Engine điều phối bên ngoài | Đưa lớp điều khiển lỗi ra ngoài tầm kiểm soát của RQ1 | Khi cần nhiều tiến trình |
| Cơ chế checkpoint / khôi phục sau crash | Chạy theo lô và tất định — chạy lại rẻ hơn | Khi một lần chạy vượt vài giờ |
| Vector database | Không có embedding sinh từ mô hình ngôn ngữ; kNN trên feature là đủ | Không |
| Giao diện web đầy đủ | Không RQ nào đo giao diện; chỉ cần giao diện gán nhãn tối giản | Khi làm nhánh đánh giá chuyên gia |
| Tác tử dựa trên mô hình ngôn ngữ lớn | Làm nhiễu loạn causal claim của RQ1 | Nhánh tùy chọn §5.2 của tài liệu RQ |
| Bộ nhớ tiền lệ | Không RQ nào bắt buộc; chỉ là ablation bổ sung | Khi ba RQ chính đã xong |

---

## Phần 8 — Kỷ luật kỹ thuật bắt buộc

Bốn quy tắc dưới đây **phải được cưỡng chế bằng test tự động**, không phải bằng ghi nhớ.

| # | Quy tắc | Cách cưỡng chế |
|---|---|---|
| 1 | **Không rò rỉ nhãn.** `review_lag_days` không tồn tại; `FeatureSet(T)` không chứa feature của mốc muộn hơn `T`; **`has_comment` và mọi đặc trưng dẫn xuất từ văn bản bị chặn ở T₂ và T₃** | Test đối chiếu `available_at` của mọi cột với `decision_point`; test riêng chặn nhóm đặc trưng văn bản ở giai đoạn 1 |
| 2 | **Đánh giá quy kết chỉ trên gold set.** Truyền weak label vào hàm đánh giá phải phát sinh lỗi | Test khẳng định `attribution.evaluate(weak_labels)` raise |
| 3 | **Không quyết định tự động khi suy giảm.** `degradation_level > 0` bắt buộc `needs_human_review = True` | Bất biến lúc khởi tạo `Decision` + property-based test |
| 4 | **Không `argmax` trong đường quy kết nguyên nhân.** | Test tĩnh quét mã nguồn tìm `idxmax` / `argmax` trong `agents/analysts/` và `baselines/monolithic.py` |

**Tính tất định.** Cố định seed toàn cục; mọi mô hình huấn luyện với seed ghim; không dùng thời gian
thực trong logic nghiệp vụ — mọi mốc thời gian lấy từ dữ liệu, và `deadline_ms` là **thời lượng** chứ
không phải dấu thời gian. `msg_id` sinh tất định từ `(conversation_id, sender, performative, seq)`.
Tiêu chí kiểm tra: chạy hai lần cùng cấu hình phải cho hai tệp `decisions.jsonl` trùng `sha256`.

> ⬜ **Kiểm tái lập chưa chạy lại sau khi đổi mốc T₃ (12/08)** — T9.4. Không con số chaos nào được đưa
> vào luận văn trước khi phép kiểm này xanh.

---

## Phần 9 — Năm quyết định khác với bản thiết kế v2 đã lỗi thời

Ghi lại tường minh để không ai — kể cả tác giả sau ba tháng — hồi sinh các lựa chọn cũ.

| # | Quyết định | Bản v2 lỗi thời | Lý do thay đổi |
|---|---|---|---|
| 1 | **Hai mốc quyết định T₃ / T₄** | Chỉ có T₃, đồng thời cho Analyst đọc `review_comment_message` | Hai điều đó mâu thuẫn nhau: tại T₃ bình luận **chưa tồn tại**. Giữ nguyên T₃ đơn lẻ thì 100% đơn rơi vào tầng B và tầng BERTimbau mất lý do tồn tại |
| 2 | **Monolithic-Complete là bộ phân loại đa nhãn** | Đơn nhãn + `argmax` | Nếu đối chứng bị chặn không cho trả nhiều nhãn, MAS-DSS thắng ở tình huống (a) **theo cấu tạo** — đúng lỗi baseline bù nhìn đã cam kết tránh. Phép so sánh phải cô lập *cách tổ chức*, không phải *hình dạng đầu ra* |
| 3 | **Bổ sung chỉ số selective prediction cho tầng B** | Chỉ có macro-F1 | Macro-F1 phạt việc từ chối trả lời; ở tầng B, DP3 sẽ tự trừ điểm chính nó. Cần so ở **cùng mức độ phủ** |
| 4 | **Tự viết orchestrator; bỏ engine điều phối bên ngoài** | LangGraph + Redis checkpointer | RQ1 đòi kiểm soát chính xác thời điểm và cách một lời gọi tác tử thất bại; checkpoint/resume và HITL interrupt không RQ nào cần (§2.2) |
| 5 | **Parquet + SQLite; bỏ toàn bộ dịch vụ nền** | Redis Streams + PostgreSQL + Jaeger + docker-compose 4 dịch vụ | Không RQ nào cần; mỗi dịch vụ nền là một điểm hỏng làm giảm khả năng tái lập (§2.3) |

Cả năm đã được phản ánh trong cấu trúc thư mục ở §4 và trong lộ trình ở §6.

---

## Phần 10 — Rủi ro kỹ thuật

| Rủi ro | Mức | Xử lý |
|---|---|---|
| Gold set không kịp tiến độ | **Cao nhất** | Khởi động từ M0′, song song toàn bộ dự án; hạ quy mô xuống 200 đơn và báo cáo trung thực nếu cần |
| Tỷ lệ đơn không có bình luận vượt 50% | Trung bình | M0 phát hiện sớm, trước khi viết mã hệ thống. Con số này *củng cố* DP3 nhưng thu hẹp phạm vi RQ3 — phải xử lý bằng cách viết, không bằng cách giấu |
| Mô hình bị nhúng vào agent, phá tính công bằng | Trung bình | Thứ tự M2 trước M3 + test đồ thị phụ thuộc |
| **Orchestrator tự viết có bug tinh vi**, làm sai lệch kết quả mà không lộ ra | Trung bình | Ràng buộc kế hoạch ở dạng dữ liệu tuyến tính, cấm chu trình và nhánh lồng nhau (§2.2c); property-based test trên bộ thực thi; kiểm tra hai lần chạy cho kết quả trùng khớp đến từng byte |
| Bid không được hiệu chuẩn | Cao | Isotonic riêng từng analyst; báo cáo ECE trước/sau — hội đồng sẽ hỏi |
| ~~BERTimbau làm chậm thí nghiệm chaos~~ | — | **Không còn áp dụng:** T3.3 bị chặn bởi quyết định không cài `torch`; `TfidfCauseHead` chỉ tốn 1,3 ms. Rủi ro đã đảo chiều — xem dòng dưới |
| **Cause head rẻ khiến ràng buộc ngân sách không bao giờ ràng buộc** | **Cao** | `budget_binds` báo cáo tường minh tỷ lệ phiên có ràng buộc; ngân sách đặt theo **bội số** để tự điều chỉnh khi giá đổi; cờ `--text-cost-ms` mô phỏng giá BERTimbau để kiểm chứng cơ chế, và mọi số sinh ra từ đó phải ghi rõ là **kết quả mô phỏng** |
| Kết quả chaos không tái lập | Cao | Seed cho bộ tiêm lỗi; kiểm tra hai lần chạy cho kết quả giống hệt trước khi đưa số vào luận văn |

---

## Phụ lục A — Đặc tả chi tiết

Phần này chuyển từ `technical-design-v2.md` (đã lỗi thời) sang, giữ lại những đặc tả còn hiệu lực và đã
được điều chỉnh theo năm quyết định ở §9. **Đây là đặc tả cài đặt, không phải gợi ý.**

### A.1 — Mười performative

| Performative | Ý nghĩa | Ai dùng |
|---|---|---|
| `REQUEST` | Yêu cầu thực hiện | Orchestrator → agent |
| `INFORM` | Thông báo kết quả | Agent → Orchestrator |
| `CFP` | Mời đấu thầu | Orchestrator → Analyst pool |
| `PROPOSE` | **Hai vai**: bản khai năng lực ở pha 1 *(`ontology="declaration"`)* và bid thật ở pha 2 *(`ontology="bid"`, kèm `evidence[]`)* | Analyst → Orchestrator |
| `ACCEPT_PROPOSAL` | Trao thầu | Orchestrator → Analyst |
| `REJECT_PROPOSAL` | Từ chối thầu | Orchestrator → Analyst |
| `CHALLENGE` | Phản biện một đề xuất | Policy Critic → Recommendation |
| `REFUSE` | Từ chối vì ngoài năng lực hoặc thiếu bằng chứng | Agent → Orchestrator |
| `FAILURE` | Thất bại khi đang thực hiện | Agent → Supervisor |
| `NOT_UNDERSTOOD` | Nội dung sai ontology | Bất kỳ |

> **`PROPOSE` mang hai vai là điều bắt buộc phải biết khi đọc nhật ký.** Guard và bộ dựng trace đều
> khóa theo **`ontology`** chứ không theo performative — khóa theo performative sẽ chặn sạch mọi bản
> khai năng lực *(chưa có bằng chứng theo đúng thiết kế)* và làm sập phiên đấu thầu.

Trường của `Message`: `msg_id`, `conversation_id`, `trace_id`, `in_reply_to`, `sender`, `receiver`,
`performative`, `ontology`, `content`, `deadline_ms`, `cost_hint`, `priority`, `seq`, `payload`.

**Ba sai khác có chủ đích so với phác thảo, mỗi cái phục vụ tính tái lập:**

| Phác thảo | Cài đặt | Lý do |
|---|---|---|
| `reply_by` — dấu thời gian tuyệt đối | **`deadline_ms`** — thời lượng | Dấu thời gian kéo đồng hồ hệ thống vào nội dung message ⟹ hai lần chạy sinh hai tệp khác nhau |
| *(không có)* | **`payload`** — tham chiếu `OrderCase` trong tiến trình, `compare=False`, **không bao giờ ghi nhật ký** | Tách dữ liệu ngữ nghĩa (`content`, ghi nhật ký) khỏi tham chiếu tiện dụng. Vì `payload` không được ghi, nó **không thể** thành đường lách làm trace phân kỳ với hành vi thật — đây là cách DP4 được cưỡng chế |
| *(không có)* | **`seq`** + `msg_id` sinh tất định từ `(conversation_id, sender, performative, seq)` | Chạy lại cùng cấu hình cho nhật ký trùng đến từng byte |

### A.2 — Danh sách agent và cost_class

Cột `cost_class` **là dữ liệu vận hành**, không phải chú thích: nó là đầu vào của bài toán phân bổ ngân
sách trong Contract Net (A.3). Cột `cost_ms` là **giá đo được** (p95 trên 400 case thật), đo lại bằng
`python -m masdss.cli.compare_heads`.

**Mười tác tử** — tức mười thành phần có thể hỏng, và đó là thước đo chi phí kiến trúc chính:

| Agent | `agent_id` | Capability | cost_class · cost_ms | Giai đoạn | Vai trò |
|---|---|---|---|---|---|
| Analytics | `Analytics` | *(không — thuần luật)* | rẻ · 0,2 | 1, 2 | Chỉ báo ngữ cảnh: tầng A/B, nhóm hàng, cờ `is_late` |
| Prediction | `Prediction` | LightGBM + isotonic + OOD | rẻ · theo model | **1**, 2 | P(bất mãn), confidence đã hiệu chuẩn, `REFUSE` khi OOD |
| Delivery Analyst | `DeliveryAnalyst` | `DeliverySignal` — GBM trên đặc trưng logistics | rẻ · **0,3** | **2** | Đấu thầu case có tín hiệu giao hàng |
| Quality Analyst | `QualityAnalyst` | `TfidfCauseHead` đa nhãn | **đắt** · **1,3** | **2** | Tín hiệu chất lượng sản phẩm — cần văn bản |
| Service Analyst | `ServiceAnalyst` | *cùng object* `TfidfCauseHead` | **đắt** · **1,3** | **2** | Tín hiệu chăm sóc khách hàng — cần văn bản |
| Recommendation | `Recommendation` | Rule engine *(chạy thử để lấy hành động ứng viên)* | rẻ · 0,1 | 2 | Sinh ứng viên hành động phục hồi dịch vụ |
| Policy Critic | `PolicyCritic` | Engine ràng buộc | rẻ · 0,1 | 2 | `CHALLENGE` đề xuất vi phạm ràng buộc (A.5) |
| Arbiter | `Arbiter` | Thứ tự ưu tiên chính sách khai báo trong YAML | rẻ · 0,05 | 2 | Phân xử bất đồng Recommendation ↔ Critic |
| Rule Agent | `RuleAgent` | YAML rules | rẻ · 0,05 | 1, 2 | Áp chính sách, chốt hành động; cưỡng chế DP1 |
| Case Manager | `CaseManager` | Code | rẻ · 0,05 | — | ⚠️ **Có trong registry nhưng không nằm trong kế hoạch nào** — xem ghi chú dưới |

**Bốn thành phần thuộc kiến trúc nhưng *không* phải tác tử** *(không có hộp thư, không nhận message)*:

| Thành phần | Vai trò |
|---|---|
| Orchestrator | Duyệt kế hoạch, cấp ngân sách, mở phiên đấu thầu, áp chính sách lỗi. Là tâm của tô-pô hình sao |
| Supervisor + Circuit Breaker | Một breaker cho mỗi thành phần logic; chính sách retry **chỉ cho lỗi transient** |
| Health Monitor | Phương sai bằng 0 + PSI trên cửa sổ trượt — bắt tác tử **sai mà không chết** |
| Explainer | Dựng decision trace từ nhật ký, nhận **đúng một** tham số `conversation_id` (DP4) |

**Ba ghi chú bắt buộc khi trích bảng này vào luận văn:**

- **`PriceAnalyst` đã bị gỡ ngày 12/08** cùng nhãn `price`. Lý do là **hệ phân loại đặt sai**, không
  phải cỡ mẫu: khách đã xác nhận mua tức đã đồng ý giá niêm yết, nên một lời than sau khi mua không thể
  về *giá sản phẩm*. Đọc lại 12 dòng gán `price` trong gold set: **10/12 than về phí vận chuyển** — đó
  là thất bại giao hàng. Ba quy tắc định tuyến thay thế nằm ở `codebook.md §Quy tắc 7`. Capability
  `price_signal.py` **vẫn còn** vì baseline đơn khối dùng, nhưng **không tác tử nào dùng nó**.
- **`CaseManager` không được gọi.** Nó có trong `build_registry` và trong bảng ánh xạ thành phần, nhưng
  không xuất hiện ở `STAGE1_PLAN` lẫn `STAGE2_PLAN`. Hệ quả cho Chương 4: bề mặt hỏng **gọi được** là
  **9**, không phải 10. `tests-v3/test_chaos_scenarios.py` canh đúng điều này.
- **Quality/Service dùng `TfidfCauseHead`, không phải BERTimbau.** T3.3 bị chặn bởi quyết định không cài
  `torch`. Chi phí đo được vì vậy là 1,3 ms chứ không phải ~45 ms, và điều đó **làm yếu ràng buộc ngân
  sách** — xem cảnh báo `budget_binds` ở A.3.

### A.3 — Contract Net có ngân sách tính toán

Đây là cơ chế biến giao thức từ "ensemble đội lốt" thành phân bổ tác vụ thật.

```
PHA 1 — Thăm dò (rẻ, mọi analyst đều tham gia)
  Orchestrator ──CFP(case, budget=B)──▶ 3 Analyst
  Mỗi Analyst trả BẢN KHAI NĂNG LỰC, KHÔNG chạy capability đắt:
      (expected_confidence, cost_ms, has_evidence)
    · Delivery Analyst : (prior, 0.3ms, True)    ← GBM trên feature có sẵn
    · Quality Analyst  : (prior, 1.3ms, True)    ← chỉ kiểm CÓ VĂN BẢN HAY KHÔNG
    · Service Analyst  : REFUSE(no_text)         ← đơn thuộc tầng B

  information_gain(a) = expected_confidence NẾU has_evidence, ngược lại 0.0
      ⟹ không có bằng chứng thì không có lợi ích, bất kể tiên nghiệm cao đến đâu

PHA 2 — Phân bổ dưới ràng buộc ngân sách
  Orchestrator giải bài toán knapsack nhỏ bằng VÉT CẠN (3 analyst = 8 tổ hợp):
      max Σ information_gain(a)   s.t.   Σ cost_ms(a) ≤ B
  Phá thế cân bằng: lợi ích CAO nhất → chi phí THẤP nhất → tên theo bảng chữ cái
  → ACCEPT_PROPOSAL cho tập analyst thắng thầu
  → REJECT_PROPOSAL cho bên thua — họ DỪNG, không chạy capability
  → chỉ bên thắng mới chạy capability đắt và trả PROPOSE kèm evidence
```

Vét cạn chứ không tham lam: ở quy mô này nó cho nghiệm **tối ưu và tất định**, còn tham lam theo tỷ số
gain/cost chỉ là xấp xỉ. Quy tắc phá thế cân bằng là bắt buộc — không có nó, kết quả phụ thuộc thứ tự
duyệt và tính tái lập bị phá vỡ âm thầm.

**Ngân sách `B` đặt theo BỘI SỐ của chi phí chạy hết, không phải số tuyệt đối:**

| Mức rủi ro | Hệ số | Nghĩa |
|---|---|---|
| LOW | **0,6** | **phải chọn** — đủ cho analyst giao hàng + đúng một analyst văn bản |
| MEDIUM | 1,0 | vừa đủ chạy hết |
| HIGH | 1,5 | chạy hết còn dư |

> **Cách đặt cũ dùng số tuyệt đối (2 / 20 / 120 ms) đã gây lỗi L27.** Khi cause head đổi từ bản tạm
> (0,0093 ms) sang bản huấn luyện (12 ms), mức 2,0 ms của case rủi ro thấp không còn đủ cho bất kỳ
> analyst văn bản nào. Hậu quả: **cổng rủi ro đã được gỡ tường minh khỏi mốc T₄ lại quay về một cách
> ngầm qua ngân sách** — đơn rủi ro thấp không bao giờ được phân tích văn bản, và macro-F1 của MAS-DSS
> tụt 0,14 dưới đối chứng đơn khối **vì một tham số chứ không vì kiến trúc**. Đặt theo bội số làm ràng
> buộc tự điều chỉnh khi giá đổi.

Chỉ số riêng sinh ra từ cơ chế này: **chất lượng quy kết đạt được trên mỗi ms tính toán** — lập luận
định lượng cho RQ3 mà một ensemble không có.

**Kiểm tra trung thực bắt buộc: `budget_binds`.** Nếu ngân sách không bao giờ ràng buộc thì giao thức
vẫn chạy đúng hai pha nhưng **không quyết định gì** — mọi analyst đều được gọi — và mọi con số về "phân
bổ tính toán" trở nên rỗng. Hàm `contract_net.budget_binds()` tính điều đó và `run_system` in cảnh báo
tường minh khi tỷ lệ bằng 0. Đây là hệ quả trực tiếp của việc `TfidfCauseHead` rẻ hơn BERTimbau nhiều
lần (A.2).

**Ba yêu cầu bắt buộc:**

| Yêu cầu | Cách làm | Trạng thái |
|---|---|---|
| Hiệu chuẩn bid | Isotonic regression trên tập validation, **riêng từng analyst**; báo cáo ECE và Brier trước/sau | ⬜ **T7.3b — còn chặn bởi gold set.** Không hiệu chuẩn thì analyst "tự tin quá mức" luôn thắng thầu bất kể đúng sai |
| Đa nhãn, không `argmax` | Giữ **mọi** bid vượt ngưỡng τ vào `causes[]`; cấm `idxmax` trong mã nguồn | ✅ Có test tĩnh quét `agents/analysts/` và `baselines/monolithic.py` |
| Cờ đa nguyên nhân | `bid_entropy` cao hoặc ≥2 bid vượt τ → `multi_cause = True` | ✅ Cưỡng chế trong `Decision.__post_init__`. Đây là DP2 và là tình huống (a) của RQ3 |

**Điều kiện `REFUSE` — mỗi điều kiện đều kiểm chứng được:**

| Analyst | REFUSE khi |
|---|---|
| Quality / Service | Đơn không có `review_content` → thuộc tầng B *(25,23% đơn bất mãn)*, không có bằng chứng văn bản |
| Delivery | Thiếu mốc thời gian giao hàng, hoặc nhóm hàng quá ít mẫu |
| Mọi analyst | Chạy capability xong mà không tìm được bằng chứng vượt ngưỡng — **từ chối thay vì bid số 0**, vì một bid rỗng vẫn chiếm chỗ trong phiên và làm nhiễu `bid_entropy` |
| Prediction | Vector đặc trưng nằm ngoài phân phối huấn luyện (OOD detector) |

Nếu **không analyst nào** vượt ngưỡng τ → `cause = unknown` → escalate. Đây không phải thất bại của hệ
thống mà là hành vi đúng về mặt tri thức luận.

**Đường ablation của DP3:** cờ `allow_refuse=False` *(`run_system --no-refuse`)* cấm mọi analyst phát
`REFUSE`, buộc chúng bid ở đúng ngưỡng `tau_cause` kèm `Evidence(kind="forced_guess")`. Đây **không
phải chế độ vận hành** — nó tồn tại duy nhất để đo cái giá của việc bỏ quyền từ chối, tức để DP3 được
kiểm chứng chứ không chỉ được phát biểu.

### A.4 — Output guard

Mọi output đi qua validator trước khi vào blackboard.

| Guard | Kiểm tra | Bắt được gì |
|---|---|---|
| **Schema** | Đúng kiểu, `risk_score`/`confidence ∈ [0,1]`, `risk ∈ {0,1,2}`, **bid** *(`ontology="bid"`)* phải kèm evidence, **bản khai** *(`ontology="declaration"`)* phải đủ trường | Lỗi cài đặt, lỗi tuần tự hóa |
| **Sanity** | Phương sai bằng 0 trên cửa sổ trượt — **chỉ khi có phân phối tham chiếu chứng tỏ đại lượng đó *phải* biến thiên** | Model chết mà vẫn trả số |
| **Calibration** | PSI so với phân phối tham chiếu sạch, ngưỡng **1,0 hiệu chuẩn trên lần chạy khỏe** *(không dùng quy ước 0,25)* | Drift, mất hiệu chuẩn |
| **Consistency** | Prediction báo rủi ro CAO nhưng không analyst nào tìm ra bằng chứng và Analytics không thấy bất thường | Mâu thuẫn nội bộ |

Cài đặt gộp Sanity và Calibration vào một `StatisticalGuard` vì chúng dùng chung cửa sổ trượt; lý do
cảnh báo vẫn được phân biệt rõ trong thông điệp. **Trạng thái sức khỏe là bền vững**: một thành phần đã
bị kết luận bất thường thì không được phục vụ tiếp — nếu guard chỉ chặn đúng case đầu tiên thì các case
sau vẫn hỏng âm thầm y nguyên.

> **Nguyên tắc thiết kế quyết định giá trị của kết quả RQ1:** guard phải viết theo **nguyên lý tổng
> quát**, không được viết để bắt đúng một bộ tiêm lỗi cụ thể. Nếu guard biết trước `ConstantOutputInjector`
> đặt giá trị 0,5 rồi đi kiểm "có phải 0,5 không" thì ta không đo được gì — ta chỉ kiểm rằng mình đã
> viết đúng cái mình vừa nghĩ ra.

`GuardViolation` **là một `DeterministicError`**, mà orchestrator đã có sẵn chính sách cho loại lỗi đó
(hạ hai bậc suy giảm, đi tiếp). Nhờ vậy không một dòng nào trong orchestrator phải sửa để tầng chịu lỗi
hoạt động, và bật/tắt nó là **một tham số** (`--no-reliability`) chứ không phải một nhánh mã nguồn.

### A.5 — Policy Critic: engine ràng buộc, không phải engine EV

Mọi ràng buộc dưới đây tính được từ dữ liệu thật, **không tham số nào bịa** (ràng buộc C1).

| Ràng buộc | Tính từ | Đã cài |
|---|---|---|
| Suy giảm hệ thống | `degradation_level > 0` | ✅ `degraded_system` |
| Mâu thuẫn nội bộ | Blackboard: rủi ro CAO nhưng không có nguyên nhân nào | ✅ `internal_contradiction` |
| Chi phí hành động vượt giá trị đơn | `price` + `freight_value`, bảng chi phí hành động khai báo trong YAML | ✅ `cost_exceeds_order_value` |
| Bằng chứng yếu | `max_cause_probability < min_cause_probability` | ✅ `weak_evidence` |
| Ngân sách can thiệp | Chính sách: chỉ can thiệp top-k% rủi ro cao nhất trong kỳ | ⬜ cần trạng thái xuyên kỳ |
| Cooldown seller | Lịch sử case của chính hệ thống | ⬜ cần case store tích lũy |
| Công bằng | Tỷ lệ can thiệp theo bang / nhóm hàng | ⬜ cần trạng thái xuyên kỳ |

Bốn ràng buộc đầu chạy trên **một case độc lập** nên cài được ngay; ba ràng buộc còn lại cần trạng thái
tích lũy xuyên kỳ. Khi báo cáo tỷ lệ Critic bác bỏ ở Chương 5 phải nói rõ nó tính trên **bốn** ràng
buộc, không phải bảy — nếu không, con số sẽ được đọc như thể toàn bộ engine đã hoạt động.

Critic **không** tuyên bố "hành động này sẽ không hiệu quả" — không biết được. Nó tuyên bố "hành động
này vi phạm ràng buộc X, đo được ngay bây giờ". Yếu hơn, nhưng đúng, và vẫn ablation được.

Arbiter phân xử bằng **thứ tự ưu tiên chính sách khai báo tường minh trong YAML**, không dùng hàm hữu
dụng kỳ vọng. Thứ tự đang dùng, đọc từ `config/v3/rules.yaml`:

```
degraded_system > internal_contradiction > cost_exceeds_order_value > weak_evidence
```

Mọi vi phạm trong danh sách này đều đủ nghiêm trọng để chuyển giao cho người, nên Arbiter luôn đứng về
phía Critic khi có bất đồng; thứ tự ưu tiên quyết định **ràng buộc nào được ghi là lý do**. Chỉ số sinh
ra từ đây — tỷ lệ Arbiter đứng về phía Critic — vì vậy hiện là **hằng số theo cấu tạo**, và phải trình
bày đúng bản chất đó thay vì như một kết quả thực nghiệm.

### A.6 — Thang suy giảm

> Nguyên tắc bất di bất dịch: hệ thống không bao giờ được im lặng cho ra quyết định rác.

| Thành phần | L0 (bình thường) | L1 | L2 | L3 (đáy) |
|---|---|---|---|---|
| Prediction | LightGBM + isotonic | Logistic Regression | Heuristic `is_late → HIGH` | `escalate_to_human` |
| Quy kết nguyên nhân | CNP 3 analyst có ngân sách | Analyst còn sống bid, giảm ngân sách | Chỉ analyst rẻ (Delivery) | `cause = unknown`, giao người |
| Recommendation | Playbook | Playbook tĩnh | — | `assign_to_cs_review` |
| Policy Critic | Đủ 4 ràng buộc đã cài | Chỉ ràng buộc cứng (chi phí, suy giảm) | — | Bỏ qua, gắn cờ |
| Rule Agent | Luật đầy đủ | Luật core | — | `escalate` toàn bộ |

**Cài đặt thực tế đơn giản hơn bảng trên, và phải nói thẳng điều đó.** Mức suy giảm hiện được nâng bởi
`Blackboard.degrade()` — transient hạ một bậc, deterministic hạ hai bậc — rồi `build_decision` cưỡng
chế `escalate_to_human` ở mọi mức `> 0`. Tức hệ thống **nhảy thẳng từ L0 sang hành vi của L3**; các mức
fallback trung gian (Logistic Regression thay LightGBM, playbook tĩnh) **chưa được cài**. Bảng này vì
vậy là **đặc tả thang suy giảm**, không phải mô tả hành vi đã đo — Chương 4 phải trình bày đúng như thế.

`degradation_level > 0` → Rule Agent **bắt buộc** gắn `needs_human_review`. Đây là DP1 và phải là cưỡng
chế trong mã nguồn, không phải quy ước.

Cơ chế đi kèm: circuit breaker (N lỗi liên tiếp → OPEN → cooldown → HALF_OPEN → CLOSED); timeout thật
bằng `asyncio.wait_for` **hủy** task chứ không đo sau khi chạy xong; chỉ retry lỗi *transient* với
exponential backoff kèm jitter, **không retry lỗi deterministic**; bulkhead theo từng agent; dead-letter
queue cho case thất bại hoàn toàn; **đơn vị lỗi là case, không phải batch**.

### A.7 — Phân loại lỗi cho chaos harness

**Năm nhóm × ba mức, cài đặt ở `chaos/scenarios.py`:**

| Nhóm | Lỗi cụ thể | Ba mức | Guard được thiết kế để bắt? |
|---|---|---|---|
| **crash** | Thành phần raise exception tất định | k = 1, 2, 3 thành phần | ✅ có |
| **hang** | Thành phần treo quá hạn chót → task **bị hủy** | k = 1, 2, 3 | ✅ có |
| **byzantine_gross** | Trả hằng số; phương sai output bằng 0 | k = 1, 2, 3 | ✅ có |
| **drift** | Dịch chuyển phân phối đặc trưng ở tầng case | 5%, 10%, 20% | ❌ **không** |
| **bias** | Bid lệch hệ thống: một analyst luôn cộng thêm confidence | +0,05 · +0,15 · +0,30 | ❌ **không** |

Thứ tự leo thang có chủ đích — `prediction` → `cause_delivery` → `cause_quality` — bắt đầu từ thành
phần **được giám sát tốt nhất** rồi mở sang thành phần giám sát kém hơn.

**Hai nhóm cuối là nhóm guard *không* được thiết kế riêng để bắt, và chỉ kết quả ở đó mới là kết quả
thực nghiệm.** Báo cáo "guard bắt được lỗi crash" như một phát hiện là tự lừa: ta viết guard để bắt nó.
Phân biệt này được cưỡng chế bằng trường `designed_for` trong chính kịch bản, và phải giữ nguyên khi
viết Chương 5.

Giao thức so sánh: chạy **cùng kịch bản lỗi** trên MAS-DSS và Monolithic-Complete; không so với MIS và
single-ML vì chúng không đủ tư cách tham gia thí nghiệm này, và nói thẳng điều đó.

**Bộ tiêm riêng cho thành phần chỉ-MAS.** Năm thành phần mà kiến trúc đơn khối không có
*(`analytics`, `recommendation`, `critic`, `arbiter`, `case_manager`)* cần bộ tiêm riêng, vì trên chúng
con số "đơn khối hỏng âm thầm 0%" **không phải chiến thắng của MAS-DSS** — đơn khối không có thành phần
đó để mà hỏng. Phép so sánh đúng ở đây là **MAS-DSS với chính nó khi tắt tầng chịu lỗi**.

### A.8 — Đặc tả gold set

| Hạng mục | Quy cách |
|---|---|
| Kích thước | **300 dòng** cho bộ nhãn cuối *(`goldset_v2`)*; bộ 250+150 của vòng 3 giữ lại làm bộ **dựng đường ống** |
| **Lấy mẫu** | **Không cân xứng giữa hai tầng**, kèm hiệu chỉnh trọng số khi báo cáo chỉ số tổng thể. Lấy theo tỷ lệ tự nhiên sẽ chỉ cho ~98 mẫu tầng B — quá mỏng cho tình huống (b) của RQ3 |
| **Nguồn** | Bộ cuối lấy **chỉ từ `t3_test`** — không dòng nào từng tham gia huấn luyện hay phát triển. Hiệu quả thiết kế 0,915 |
| Phân tầng phụ | Nhóm hàng × mức trễ giao |
| Annotator | Hai người độc lập, codebook rõ ràng, **kiểm tính độc lập trước khi tính κ** |
| Nhãn | **Đa nhãn bắt buộc** |
| Độ tin cậy | Báo cáo **Cohen's κ**. Nếu κ < 0.6 thì chính định nghĩa nguyên nhân có vấn đề — và đó cũng là phát hiện đáng viết |
| Rào cản tiếng Bồ | Dịch máy + đóng băng bản dịch thành artifact có checksum, gán nhãn trên bản tiếng Anh với cột tiếng Bồ để đối chiếu; ghi vào Threats to Validity |

**Ranh giới giữa hai bộ nhãn được cưỡng chế bằng kiểu dữ liệu, không bằng trí nhớ:**

| | Bộ nhãn hiện có | Bộ nhãn cuối |
|---|---|---|
| Mục đích | dựng và gỡ lỗi đường ống | **sinh kết quả cho Chương 5** |
| `Provenance` | `model_assisted_provisional` | `human_independent` |
| Số sinh ra | `citable = False` | `citable = True` |

`Provenance` **không có giá trị mặc định**, mọi bảng kết quả mang cột `citable`, và đổi **một tham số**
`--provenance human_independent` là toàn chuỗi tự đổi trạng thái. Lệnh `check_validation` kiểm **tính
độc lập** trước khi tính κ — nó đã chặn đúng hai tệp của vòng 3 với lý do ghi chú trùng 96,4%, tức
κ = 0,957 của vòng đó **không đo gì cả**.

**Cưỡng chế trong mã nguồn:** `evaluation/attribution.py` chỉ nhận gold set; truyền weak label vào phải
raise.

### A.9 — Thanh lọc đặc trưng và tập hành động

| Feature | Quyết định | Lý do |
|---|---|---|
| `review_lag_days` | **XÓA** | Leakage trắng trợn — chỉ tồn tại sau khi review đã viết |
| `has_comment` và mọi đặc trưng dẫn xuất từ văn bản | `available_at = T4` | Chưa tồn tại ở T₃, và tương quan mạnh với nhãn (76,5% ở 1★ so với 31,2% ở 4★) |
| `delivery_delay_days`, `delivery_days` | Giữ, `available_at = T3` | Hợp lệ ở T₃ |
| `carrier_handover_days` | Giữ, `available_at = T2` | Có ở cả T₂, T₃, T₄ |
| `freight_ratio`, `price`, `payment_value` | Giữ, `available_at = T1` | Static |
| Thống kê seller / nhóm hàng | Giữ, **chỉ học từ tập train** | Chống rò rỉ; split theo thời gian, không ngẫu nhiên |

**Tập hành động phục hồi dịch vụ** *(thay tập luật cũ; `expedite_shipment` bị loại vì bất khả thi về
mặt thời gian)*: `proactive_apology_with_coupon`, `preemptive_ticket_open`, `cs_callback_within_24h`,
`partial_refund` / `compensation_voucher`, `return_replacement_offer`, `seller_audit_flag`,
`escalate_to_human` *(bắt buộc khi `degradation_level > 0` hoặc `cause = unknown`)*.

### A.10 — Nguyên tắc xây dựng Monolithic-Complete

| Dùng chung với MAS-DSS | Không có |
|---|---|
| **Cùng** LightGBM đã huấn luyện, cùng siêu tham số | Message passing |
| **Cùng** cause head **đa nhãn** *(`TfidfCauseHead`)* | Contract Net, ngân sách tính toán |
| **Cùng** tập luật YAML | Blackboard |
| **Cùng** split thời gian, feature set, mốc quyết định | Supervisor, circuit breaker, output guard |
| **Cùng** gold set để đánh giá | Thang suy giảm, quyền `REFUSE` |
| **Cùng** seam tiêm lỗi *(`guard_call`, bản đồng bộ)* | Hạn chót cho mỗi lời gọi |

**Tính công bằng được bảo đảm bằng định danh đối tượng, không bằng lời hứa.** `Capabilities` được dựng
**một lần** rồi truyền vào cả MAS-DSS lẫn mọi baseline; `test_baseline_parity.py` kiểm bằng phép so
sánh `is`, không phải so sánh giá trị.

**Một điểm bất đối xứng phải nêu khi báo cáo:** thêm seam tiêm lỗi vào Monolithic làm nó **chịu** được
cùng kịch bản lỗi để đo, chứ **không** làm nó **chịu đựng** được lỗi — nó vẫn không có guard, không có
thang suy giảm, không có trường nào báo rằng một phần hệ thống đã hỏng. Và vì nó không có hạn chót nào,
kịch bản `hang` chỉ làm nó **chậm đi**: đó là thất bại về **tính sống**, không phải quyết định sai, nên
không được tính là hỏng âm thầm.

Monolithic-Complete được viết theo **cách tự nhiên nhất mà một kỹ sư giỏi sẽ viết**: một quy trình tuần
tự, gặp exception thì ghi log rồi đi tiếp. Chính vì không cố tình làm cho nó hỏng nên tỷ lệ hỏng âm
thầm của nó là **kết quả thực nghiệm thật**.

### A.11 — Bộ chỉ số

**Đã bỏ hẳn:** `action_cause_fit` (vòng tròn tầng hai — chỉ đo hai file YAML do chính tác giả viết có
nhất quán với nhau không); `pipeline_completeness` làm luận cứ chính (tautology — baseline *bị định
nghĩa* là bằng 0, vẫn báo cáo nhưng trình bày đúng bản chất là mô tả khác biệt chức năng); mọi chỉ số
"giá trị cứu vãn được" (xây trên tham số bịa).

| Nhóm | Chỉ số | Phục vụ |
|---|---|---|
| **A. Dự báo** | PR-AUC là chính, ROC-AUC phụ; **kiểm định tương đương** chứ không phải t-test; phân tích độ nhạy ngưỡng `≤2` so với `≤3`; ngưỡng quyết định chọn theo chi phí, không mặc định 0.5 | RQ3, **H1** |
| **B. Quy kết** | Macro-F1 đa nhãn **trên gold set**; cắt lớp nhóm đa nguyên nhân và tầng A/B; **đường cong risk–coverage cho tầng B**; độ nhiễu weak label so với gold; ECE/Brier từng analyst trước–sau hiệu chuẩn | RQ3, **H1** |
| **C. Phối hợp** | Số message/case; độ sâu cây hội thoại; coordination overhead (ms); tỷ lệ case đi đường tắt; `bid_entropy`; **chất lượng quy kết trên mỗi ms**; tỷ lệ Critic bác bỏ; tỷ lệ Arbiter đứng về phía Critic; tỷ lệ `REFUSE` và `cause = unknown` theo tầng | RQ2 |
| **D. Chịu lỗi** | **Đường cong độ nhạy/độ đặc hiệu của guard**; **độ trễ phát hiện**; **tỷ lệ báo động giả**; **silent failure rate của Monolithic-Complete**; chất lượng quyết định khi k thành phần hỏng (k=1,2,3); phân bố `degradation_level` | RQ1, **H2, H3** |
| **E. Chi phí** | Latency p50/p95 end-to-end; **số thành phần có thể hỏng** *(thước đo chính)*; số dòng mã của tầng chịu lỗi và phối hợp. **Không được giấu** | RQ1 vế (d) |

**Ba thay đổi so với bản trước, mỗi cái có lý do:**

- **H4 và H5 không còn tồn tại.** Bộ giả thuyết đã gộp về **ba**: H1 *(tương đương độ chính xác — điều
  kiện kiểm soát)*, H2 *(hỏng âm thầm thấp hơn trên toàn bộ bề mặt hỏng)*, H3 *(phát hiện drift trước
  khi chất lượng suy giảm)*. Mệnh đề cũ *"cái giá nằm trong ngưỡng chấp nhận được"* bị chuyển thành
  **báo cáo mô tả** vì "ngưỡng chấp nhận được" chưa từng được đặc tả — đặt ngưỡng sau khi đã biết kết
  quả là HARKing.
- **Thước đo chi phí chính là *số thành phần có thể hỏng*, không phải mili giây hay dòng mã.** Hai đại
  lượng kia đo *quy mô công việc*; số thành phần đo *rủi ro đã tạo thêm* — với một câu hỏi về chịu lỗi
  thì đại lượng thứ hai mới liên quan.
- **MTTR và độ sâu DLQ bị rút.** Không có dead-letter queue trong cài đặt, và không có vòng khôi phục
  nào để đo MTTR — đơn vị lỗi là case, case hỏng thì chuyển giao cho người chứ không được sửa rồi chạy
  lại.
