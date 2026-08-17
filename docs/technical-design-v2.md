# Thiết kế kỹ thuật MAS-DSS v2

> ## ⛔ TÀI LIỆU LỖI THỜI — KHÔNG SỬ DỤNG, KHÔNG TRÍCH DẪN, KHÔNG CÀI ĐẶT THEO
>
> **Đã bị thay thế hoàn toàn bởi [technical-plan-v3.md](technical-plan-v3.md).** Mọi đặc tả còn hiệu
> lực đã được chuyển sang **Phụ lục A** của file đó, kèm điều chỉnh. Giữ file này **chỉ làm hồ sơ lịch
> sử thiết kế**.
>
> **Năm lý do bị thay thế** — mỗi lý do là một quyết định đã đảo ngược, xem `technical-plan-v3.md §9`:
>
> | # | Bản này nói | Bản v3 quyết định | Vì sao |
> |---|---|---|---|
> | 1 | Một mốc quyết định **T₃**, đồng thời cho Analyst đọc `review_comment_message` (§7.2, §8.1) | **Hai mốc T₃ / T₄** | Hai mệnh đề đó mâu thuẫn: tại T₃ bình luận **chưa tồn tại** — nó được viết cùng lúc với nhãn |
> | 2 | Tầng A ~55–60% · tầng B ~40–45% (§7.2) | **A 74,71% · B 24,6%** | Số đo thật trên 14.575 đánh giá 1–2★ |
> | 3 | Monolithic-Complete **đơn nhãn, argmax** (§9) | **Đa nhãn** | Đối chứng bị chặn không cho trả nhiều nhãn thì MAS thắng tình huống (a) *theo cấu tạo* — baseline bù nhìn |
> | 4 | LangGraph + Redis checkpointer (§1, §11) | **Tự viết orchestrator** | RQ3 cần kiểm soát chính xác cách một lời gọi tác tử thất bại; checkpoint/resume không RQ nào cần |
> | 5 | Redis + PostgreSQL + Jaeger + docker-compose (§11) | **Parquet + SQLite** | Không RQ nào cần; mỗi dịch vụ nền làm giảm khả năng tái lập |
>
> Ngoài ra, **đánh số RQ trong file này theo bản 5 câu hỏi** đã bị thu gọn còn 3. Quy đổi: RQ4 → RQ3 ·
> RQ1, RQ2 giữ số · RQ5(b) → RQ2 tình huống (b) · RQ5(a) → phân tích độ nhạy · RQ3 cũ tách ba (giải
> thích được → RQ1, độ trễ → RQ3 vế d, đánh giá chuyên gia → nhánh tùy chọn).
>
> **Bộ tài liệu đang có hiệu lực:**
> [research-questions-objectives.md](research-questions-objectives.md) — RQ, mục tiêu, phạm vi ·
> [technical-plan-v3.md](technical-plan-v3.md) — **toàn bộ quyết định kỹ thuật** ·
> [research-design-v2.md](research-design-v2.md) — danh mục artifact ·
> [proposal-comparison.md](proposal-comparison.md) — đối chiếu đề cương gốc ·
> [adversarial-review.md](adversarial-review.md) — hồ sơ lý do.

---

## Phần 0 — Ba ràng buộc dữ liệu chi phối toàn bộ thiết kế

Đây không phải là "lưu ý", đây là **biên** của thiết kế. Mọi cơ chế vi phạm một trong ba ràng buộc này
đều bị loại, kể cả khi nó hấp dẫn về mặt kỹ thuật.

| # | Ràng buộc | Hệ quả kiến trúc |
|---|---|---|
| **C1** | **Olist không có biến treatment.** Không cột nào ghi hành động đã áp dụng, không có outcome phản thực | Không thành phần nào được ước lượng `ΔP(recover \| action)`, được truy hồi "hành động nào đã hiệu quả", hay được tính lợi ích kỳ vọng bằng tiền. Hệ thống **đề xuất** hành động; nó **không** tuyên bố hành động hiệu quả |
| **C2** | **Nhãn nguyên nhân không tồn tại sẵn.** Nhãn hiện tại do chính ta sinh bằng từ khóa | Weak label chỉ được dùng làm **tín hiệu huấn luyện có nhiễu**, không bao giờ làm thước đo. Mọi con số về quy kết nguyên nhân trong Chương 5 phải đo trên **gold set do người gán**. Code phải *cưỡng chế* việc tách này, không phó mặc kỷ luật cá nhân |
| **C3** | **Đặc trưng mạnh nhất chỉ có sau khi giao hàng.** Decision point = **T₃** | Tập hành động là **service recovery**, không phải phòng ngừa. `expedite_shipment` bị loại. `review_lag_days` bị loại khỏi feature set (leakage). Cửa sổ can thiệp = từ lúc giao đến lúc khách viết review |

**C1 giết ba thứ trong plan v1.** Ghi rõ ở đây để không ai (kể cả tác giả sau ba tháng) hồi sinh chúng:

| Thứ bị xóa khỏi v1 | Vì sao | Thay bằng |
|---|---|---|
| Policy Critic tính `EV = P(dissat) × ΔP(recover\|action) × value − cost` | `ΔP(recover\|action)` không ước lượng được từ Olist → phải bịa tham số | **Critic = engine ràng buộc thuần** (§4.3). Vẫn `CHALLENGE` thật, vẫn ablation được, không bịa số |
| Episodic memory chứa **kết quả của hành động** ("expedite 2 lần → score 4,5") | Bịa dữ liệu. Olist không ghi hành động nào | **Precedent memory** — truy hồi case tương tự kèm **review score thực tế và nhãn nguyên nhân**, dùng để hiệu chỉnh niềm tin về *rủi ro/nguyên nhân*, không để chọn hành động (§5.2) |
| Nhóm chỉ số "chi phí can thiệp vs giá trị cứu vãn" | Xây trên tham số bịa | Nhóm chỉ số **chi phí kiến trúc** (overhead thật, đo được) + **điểm chuyên gia** (§12) |
| Arbiter dùng "hàm hữu dụng kỳ vọng" | Cùng lý do | Arbiter dùng **thứ tự ưu tiên chính sách khai báo trong YAML** (§4.4) |

---

## Phần 1 — Ranh giới LangGraph ↔ code tự viết

Quyết định hybrid giữ nguyên từ v1. Đây vẫn là quyết định quan trọng nhất về mặt kỹ thuật: nếu ranh
giới mờ, sẽ có **hai nguồn sự thật về trạng thái case** và hệ thống hỏng theo cách rất khó debug.

| Thành phần | Ai sở hữu | Vì sao |
|---|---|---|
| Thực thi kế hoạch (node, edge, conditional routing, cycle) | **LangGraph** | Khỏi tự viết state machine |
| Checkpoint / resume sau crash | **LangGraph** + Redis checkpointer | Miễn phí, đã kiểm chứng |
| Retry policy mức node | **LangGraph** | Có sẵn |
| Human-in-the-loop (`interrupt`) | **LangGraph** | Dùng cho case escalate và case `cause=unknown` |
| **Message envelope + 9 performative** | **Tự viết** | Artifact khoa học — RQ1, RQ2 |
| **Contract Net có ngân sách tính toán** | **Tự viết** | Artifact khoa học — RQ2 |
| **Blackboard semantics** | **Tự viết** (trên LangGraph state) | Artifact khoa học |
| **Supervisor, circuit breaker, degradation ladder** | **Tự viết** | LangGraph retry không biết fallback, không biết Byzantine fault |
| **Output guard** (schema/sanity/calibration/consistency) | **Tự viết** | LangGraph không có khái niệm này — đây là chỗ novelty nằm |

### Quy tắc một nguồn sự thật

> **LangGraph state object *chính là* blackboard. Không xây blackboard thứ hai.**

```
LangGraph State  (checkpoint → Redis)
├── case          : OrderCase           ← dữ liệu nghiệp vụ (immutable core)
├── blackboard    : dict                ← nơi agent đọc kết quả của nhau
│   ├── context      ← Analytics
│   ├── prediction   ← Prediction (kèm confidence đã calibrate + cờ OOD)
│   ├── bids[]       ← các Analyst thắng thầu
│   ├── causes[]     ← tập nguyên nhân ĐA NHÃN sau khi lọc ngưỡng
│   ├── precedents   ← Precedent memory
│   ├── proposal     ← Recommendation
│   └── critique     ← Policy Critic
├── plan_state    : dict                ← bước nào xong, ngân sách còn lại
├── health        : dict                ← degradation_level, circuit states
└── messages[]    : list[Message]       ← nhật ký hội thoại, append-only
```

**Redis Streams** chạy song song, **không giữ trạng thái**. Chỉ hai việc: (1) fan-out bất đồng bộ của
phiên đấu thầu; (2) audit log bền vững của mọi message (đổ tiếp về Postgres).

> Nếu thấy mình ghi cùng một dữ liệu vào cả LangGraph state lẫn Redis Hash — dừng lại, đó là bug.

---

## Phần 2 — Mô hình tác tử

Một agent **không phải là một hàm**:

```
Agent
├── identity      : agent_id, role, capabilities[], cost_class
├── mailbox       : inbox bounded, có backpressure
├── local_state   : riêng tư, không ai đọc trực tiếp
├── policy        : ACT / DEFER / DELEGATE / REFUSE khi nhận message
├── capability    : ML model | tập luật | engine tính toán
├── health        : heartbeat, error_rate, latency_p95, circuit state
└── degradation   : thang phương án dự phòng khi capability chính hỏng
```

Điểm mấu chốt: agent **có quyền từ chối**. Đây không phải chi tiết phụ — nó là **DP3** và là cơ chế
trả lời RQ5(b).

### Danh sách agent

| Agent | Capability | Chi phí | Vai trò |
|---|---|---|---|
| **Orchestrator** | LangGraph plan | — | Định tuyến động, phân bổ ngân sách tính toán |
| **Supervisor** | Code | — | Cây giám sát, restart, circuit breaker, degradation ladder |
| **Health Monitor** | Code + thống kê | — | Heartbeat, drift detection, phát hiện agent **sai mà không chết** |
| **Analytics** | Thống kê + luật | rẻ | Chỉ báo ngữ cảnh, phát hiện bất thường seller/category |
| **Prediction** | LightGBM + isotonic + OOD detector | rẻ | P(không hài lòng), confidence đã calibrate, `REFUSE` khi OOD |
| **Delivery Analyst** | GBM trên đặc trưng logistics | rẻ | Đấu thầu case có tín hiệu giao hàng |
| **Price Analyst** | Luật + z-score giá/phí theo nhóm hàng | **rất rẻ** | Đấu thầu case có tín hiệu giá/phí ship |
| **Quality Analyst** | BERTimbau encoder + head | **đắt** | Đấu thầu case có tín hiệu chất lượng sản phẩm (cần review text) |
| **Service Analyst** | BERTimbau encoder + head | **đắt** | Đấu thầu case có tín hiệu CSKH (cần review text) |
| **Recommendation** | Playbook + precedent kNN | rẻ | Sinh ứng viên hành động service recovery |
| **Policy Critic** | **Engine ràng buộc** | rẻ | `CHALLENGE` đề xuất vi phạm ràng buộc (§4.3) |
| **Arbiter** | Thứ tự ưu tiên chính sách (YAML) | rẻ | Phân xử bất đồng Recommendation ↔ Critic |
| **Rule Engine** | YAML rules | rẻ | Áp chính sách kinh doanh, chốt hành động |
| **Explanation** | Template trên **message log** | rẻ | Dựng decision trace từ hội thoại thật (DP4) |
| **Case Manager** | Code | rẻ | Tạo/đóng intervention case, saga rollback |

**Cột `cost_class` là load-bearing**, không phải trang trí — nó là đầu vào của bài toán phân bổ ngân
sách trong CNP (§4.2). Đây chính là thứ biến CNP từ "ensemble đội lốt giao thức" thành task allocation
thật.

---

## Phần 3 — Giao tiếp giữa agent

### Message envelope

Lấy cảm hứng từ **FIPA-ACL**:

```python
Message:
    msg_id          : UUID
    conversation_id : UUID           # gom mọi message của cùng một case
    trace_id        : UUID           # distributed tracing
    in_reply_to     : UUID | None    # dựng lại cây hội thoại
    sender          : agent_id
    receiver        : agent_id | broadcast | topic
    performative    : Performative
    content         : dict           # validate bằng Pydantic theo ontology
    ontology        : str            # "order_case" | "bid" | "critique" | ...
    reply_by        : datetime       # DEADLINE — cưỡng chế bằng asyncio.wait_for
    cost_hint       : float | None   # chi phí tính toán ước lượng (ms) — dùng cho CNP
    priority        : int
```

### 9 Performative

| Performative | Ý nghĩa | Ai dùng |
|---|---|---|
| `REQUEST` | Yêu cầu thực hiện | Orchestrator → agent |
| `INFORM` | Thông báo kết quả | Agent → Orchestrator |
| `CFP` | Mời đấu thầu | Orchestrator → Analyst pool |
| `PROPOSE` | Đấu thầu kèm `(confidence, cost, evidence[])` | Analyst → Orchestrator |
| `ACCEPT_PROPOSAL` / `REJECT_PROPOSAL` | Trao / từ chối thầu | Orchestrator → Analyst |
| `CHALLENGE` | Phản biện một đề xuất | Policy Critic → Recommendation |
| `REFUSE` | Từ chối vì ngoài năng lực / thiếu bằng chứng | Agent → Orchestrator |
| `FAILURE` | Thất bại khi đang thực hiện | Agent → Supervisor |
| `NOT_UNDERSTOOD` | Payload sai ontology | Bất kỳ |

**Message log là artifact khoa học.** Decision trace ở Layer 4 được *dựng lại từ message log* (DP4),
không viết tay. Đây là bằng chứng kiểm chứng được cho RQ2, và là thứ duy nhất bảo đảm trace không phân
kỳ với hành vi thực tế.

---

## Phần 4 — Điều phối

### 4.1 Định tuyến động

Orchestrator **lập kế hoạch cho từng case** thay vì chạy thứ tự cứng:

```
nhận case
  → REQUEST Analytics                       (rẻ, luôn chạy)
  → REQUEST Prediction                      (rẻ, luôn chạy)
  → nếu Prediction REFUSE (OOD)   : LangGraph interrupt → giao người, degradation_level = 3
    nếu risk == LOW               : chốt no_action, kết thúc          ← bỏ qua 6 agent
    nếu risk >= MEDIUM            : cấp ngân sách B(risk) → phiên CNP (§4.2)
                                    → Precedent lookup
                                    → Recommendation → Policy Critic
                                    → (Arbiter nếu bất đồng)
                                    → Rule Engine → Case Manager
```

Tỷ lệ case đi đường tắt là một **chỉ số hiệu năng**, không phải chi tiết cài đặt: nó là *lợi ích* đo
được của định tuyến động, đối trọng với *chi phí* coordination overhead.

### 4.2 Contract Net có ngân sách tính toán

Đây là thay đổi lớn nhất so với v1, xử lý đòn phản biện §6 ("đây chỉ là ensemble có gắn nhãn giao thức").

**Vấn đề của v1:** 4 analyst cùng làm một việc, bid độ tin cậy của mình, orchestrator lấy argmax →
softmax + argmax, không phải task allocation. Ai đọc Smith (1980) sẽ nói đúng câu đó.

**Bản v2 — CNP hai pha, có ràng buộc tài nguyên:**

```
PHA 1 — Thăm dò (rẻ, mọi analyst đều tham gia)
  Orchestrator ──CFP(case, budget=B)──▶ 4 Analyst
  Mỗi Analyst trả về BẢN KHAI NĂNG LỰC (không chạy model đắt):
      (expected_confidence, cost_ms, has_evidence)
    · Price Analyst    : (0.4, 0.1ms,  True)   ← chỉ cần z-score
    · Delivery Analyst : (0.8, 1.2ms,  True)   ← GBM trên feature có sẵn
    · Quality Analyst  : (0.5, 45ms,   True)   ← phải chạy BERTimbau
    · Service Analyst  : REFUSE(no_text)       ← đơn không có bình luận

PHA 2 — Phân bổ dưới ràng buộc ngân sách
  Orchestrator giải bài toán knapsack nhỏ:
      max Σ expected_information_gain(a)   s.t.   Σ cost_ms(a) ≤ B
  → ACCEPT_PROPOSAL cho tập analyst thắng thầu
  → chỉ những analyst đó mới thực sự chạy capability đắt và trả PROPOSE kèm evidence
```

Ngân sách `B` do Orchestrator cấp theo mức rủi ro: case rủi ro thấp chỉ đủ tiền mời analyst rẻ; case
rủi ro cao mới chi cho BERTimbau. **Giao thức trở nên load-bearing** — bỏ nó đi thì hệ thống thực sự
mất một thứ (khả năng phân bổ tính toán theo giá trị case), chứ không chỉ mất một cái tên.

Chỉ số mới sinh ra từ đây: **chất lượng quy kết đạt được trên mỗi ms tính toán** — đây là lập luận
định lượng cho RQ2 mà một ensemble không có.

**Ba chi tiết bắt buộc, hội đồng sẽ hỏi cả ba:**

| Chi tiết | Cách xử lý | Vì sao bắt buộc |
|---|---|---|
| **Calibrate bid** | Isotonic regression trên validation set, **riêng cho từng analyst**. Báo cáo ECE và Brier trước/sau | Không calibrate → analyst "tự tin quá mức" luôn thắng thầu bất kể đúng sai. Toàn bộ CNP thành vô nghĩa |
| **Đa nhãn, không argmax** | Giữ **mọi** bid vượt ngưỡng τ → `causes[]`. `idxmax` bị xóa khỏi code | `idxmax` khi hòa điểm thiên vị theo alphabet — bug thật trong code v1. Và ép đơn nhãn làm mất đúng thứ CNP sinh ra để bắt |
| **Cờ đa nguyên nhân** | `bid_entropy` cao hoặc ≥2 bid vượt τ → `multi_cause = True` | Đây là **DP2** và là tình huống (a) trong RQ2 — chỗ cơ chế cạnh tranh *lẽ ra* phải thắng classifier đơn khối |

**Điều kiện `REFUSE` của analyst** (mỗi cái đều kiểm chứng được, không phải "cho có"):

| Analyst | REFUSE khi |
|---|---|
| Quality / Service | Đơn **không có `review_comment_message`** → không có bằng chứng văn bản |
| Delivery | Thiếu mốc thời gian giao hàng |
| Price | Nhóm hàng có < N mẫu để tính z-score đáng tin |
| Mọi analyst | Vector đặc trưng nằm ngoài phân phối huấn luyện (OOD detector) |

Nếu **không analyst nào** vượt ngưỡng τ → `cause = unknown` → escalate. Đây không phải thất bại của hệ
thống; đây là **hành vi đúng về mặt tri thức luận**, và là thứ được đo trong RQ5(b).

### 4.3 Policy Critic — engine ràng buộc, không phải engine EV

Critic phát `CHALLENGE` khi bất kỳ ràng buộc nào bị vi phạm. **Mọi ràng buộc dưới đây đều tính được từ
dữ liệu thật, không tham số nào bịa:**

| Ràng buộc | Tính từ | Ví dụ vi phạm |
|---|---|---|
| **Chi phí hành động vượt giá trị đơn** | `price`, `payment_value`, bảng chi phí hành động khai báo trong YAML | Đề xuất bồi thường 30 BRL cho đơn 45 BRL |
| **Ngân sách can thiệp** | Chính sách: chỉ can thiệp top-k% rủi ro cao nhất trong kỳ | Đã dùng hết quota trong ngày |
| **Cooldown seller** | Lịch sử case của chính hệ thống | Seller đã bị audit 2 lần trong 30 ngày |
| **Công bằng** | Tỷ lệ can thiệp theo bang / nhóm hàng | Tỷ lệ audit lệch bất thường về một nhóm seller |
| **Bằng chứng yếu** | `cause_probability < τ_evidence` | Đề xuất dựa trên nguyên nhân chỉ 0.35 tin cậy |
| **Mâu thuẫn nội bộ** | Blackboard | Prediction nói risk 0.9, Analytics không thấy bất thường nào |
| **Suy giảm hệ thống** | `health.degradation_level > 0` | Bất kỳ hành động tự động nào khi hệ đang suy giảm |

**Chú ý sự khác biệt về mặt tri thức luận:** Critic không tuyên bố "hành động này sẽ không hiệu quả"
(không biết được). Nó tuyên bố "hành động này **vi phạm ràng buộc X**, đo được ngay bây giờ". Yếu hơn,
nhưng **đúng** — và vẫn ablation được: *tắt Critic → tỷ lệ can thiệp thừa tăng bao nhiêu?*

### 4.4 Arbiter

Khi Recommendation không rút đề xuất sau `CHALLENGE`, Arbiter phân xử bằng **thứ tự ưu tiên chính sách
khai báo tường minh trong YAML** (ví dụ: `fairness > budget > cost_benefit > customer_value`). Không có
hàm hữu dụng kỳ vọng, vì không ước lượng được (C1).

Chỉ số: tỷ lệ Arbiter đứng về phía Critic — cho biết Critic có đang phản biện *có lý* hay chỉ ồn ào.

---

## Phần 5 — Bộ nhớ

Hai tầng, **không phải ba**. Tầng "kết quả hành động" đã bị C1 xóa.

| Tầng | Nội dung | Lưu ở đâu | Vòng đời |
|---|---|---|---|
| **Working memory** | Blackboard của case: kết quả từng phần, bids, plan_state, ngân sách còn lại | **LangGraph state → Redis checkpointer** | Theo case (giây–phút) |
| **Precedent memory** | Case đã xử lý + **review score thực tế** + nhãn nguyên nhân | Postgres + kNN index (`sklearn.neighbors`) | Vĩnh viễn |

### 5.1 Working memory

`plan_state` được LangGraph checkpoint xuống Redis → tiến trình chết giữa chừng thì chạy tiếp từ bước
dở, không chạy lại từ đầu. Đây là phần được miễn phí từ LangGraph.

Blackboard không chỉ là chỗ chứa dữ liệu — nó cho phép agent đọc kết quả *của nhau* mà không gọi trực
tiếp. Ví dụ phối hợp thật: Price Analyst đọc bid của Delivery trước khi bid — *"đã trễ 9 ngày → phí ship
không phải nguyên nhân chính, hạ confidence của mình xuống"*.

### 5.2 Precedent memory — cái gì được truy hồi, cái gì không

```
✗ SAI (v1, đã xóa):
  "3 đơn tương tự: expedite áp dụng 2 lần → review score cuối 4 và 5,
   apology_only 1 lần → score 1. Đề xuất: expedite."
  → Olist KHÔNG ghi hành động nào được áp dụng. Đây là bịa dữ liệu.

✓ ĐÚNG (v2):
  "3 đơn tương tự (cùng nhóm hàng, trễ 7–10 ngày, cùng bang):
   review score thực tế 1, 2, 1;
   nguyên nhân được gán: delivery (2), price (1);
   → nâng prior rủi ro, củng cố giả thuyết nguyên nhân delivery."
```

Precedent dùng để **hiệu chỉnh niềm tin về rủi ro và nguyên nhân** — thứ Olist *có* dữ liệu — chứ không
để chọn hành động.

**Chống rò rỉ:** index kNN **chỉ được xây trên tập train**, cưỡng chế bằng assert trong code, không phó
mặc kỷ luật. Ghi rõ trong Chương 4.

**Ablation:** tắt precedent memory → đo mức giảm của **macro-F1 quy kết nguyên nhân trên gold set** và
**ECE của risk score**. (Không còn đo `action_cause_fit` — chỉ số đó đã bị bỏ vì vòng tròn, §12.)

---

## Phần 6 — Giám sát, suy giảm, và chaos harness

Đây là chỗ **novelty của luận văn nằm**. Thiết kế thành hệ thống con riêng, không phải try/except rải rác.

### 6.1 Hai loại lỗi — LangGraph chỉ giải quyết được loại thứ nhất

| Loại | Biểu hiện | Ai xử lý |
|---|---|---|
| **Crash fault** | Exception, timeout, mất heartbeat | LangGraph retry + **Supervisor tự viết** |
| **Byzantine / quality fault** | Agent trả **kết quả hợp lệ nhưng sai**: model drift, xác suất luôn ≈0.5, phân bố nguyên nhân lệch hẳn, bid lệch hệ thống | **Chỉ Health Monitor tự viết** — LangGraph hoàn toàn mù |

Loại thứ hai là loại giết hệ thống trong thực tế: không exception, không log đỏ, chỉ là **quyết định sai
hàng loạt**. Đây là lý do không thể phó mặc fault handling cho LangGraph — và là câu trả lời cho câu hỏi
*"sao không để LangGraph lo hết?"*.

### 6.2 Output guard

Mọi output đi qua validator trước khi vào blackboard:

| Guard | Kiểm tra | Bắt được gì |
|---|---|---|
| **Schema** | Đúng kiểu, `risk_score ∈ [0,1]`, `cause ∈ enum`, evidence không rỗng | Lỗi cài đặt, lỗi tuần tự hóa |
| **Sanity** | Phương sai output trên cửa sổ trượt, phân bố nhãn lệch quá ngưỡng | Model chết mà vẫn trả số |
| **Calibration** | PSI trên phân phối feature, Brier score / ECE trên cửa sổ trượt | Drift, mất hiệu chuẩn |
| **Consistency** | Prediction nói risk 0.9 nhưng Analytics không thấy bất thường | Mâu thuẫn nội bộ → gọi Arbiter |

### 6.3 Degradation ladder

> **Nguyên tắc bất di bất dịch: hệ thống không bao giờ được im lặng cho ra quyết định rác.**

| Agent | L0 (bình thường) | L1 | L2 | L3 (đáy) |
|---|---|---|---|---|
| Prediction | LightGBM + isotonic | Logistic Regression | Heuristic `is_late → HIGH` | `escalate_to_human` |
| Quy kết nguyên nhân | CNP 4 analyst có ngân sách | Analyst còn sống bid, giảm ngân sách | Chỉ analyst rẻ (Delivery, Price) | `cause = unknown`, giao người |
| Recommendation | Playbook + precedent | Playbook tĩnh | — | `assign_to_cs_review` |
| Policy Critic | Đủ 7 ràng buộc | Chỉ ràng buộc cứng (chi phí, ngân sách) | — | Bỏ qua, gắn cờ |
| Rule Engine | Luật đầy đủ | Luật core | — | `escalate` toàn bộ |

`Decision.degradation_level > 0` → Rule Engine **bắt buộc** gắn `needs_human_review`. Không quyết định
tự động nào được đưa ra trên nền hệ thống đang suy giảm. Đây là **DP1**, và nó phải là *cưỡng chế trong
code*, không phải quy ước.

### 6.4 Cây giám sát và circuit breaker

```
Supervisor (one-for-one, max 3 restart / 60s)
├── Analytics        [CLOSED]
├── Prediction       [HALF_OPEN — đang thử lại]
├── Analyst Pool (4) [CLOSED, CLOSED, OPEN, CLOSED]  ← Service Analyst bị cách ly
├── Recommendation   [CLOSED]
└── Policy Critic    [CLOSED]
```

- **Circuit breaker**: N lỗi liên tiếp → OPEN (dùng fallback ngay, không phí timeout) → cooldown →
  HALF_OPEN (thử 1 request) → CLOSED nếu thành công.
- **Timeout thật**: `asyncio.wait_for()` — **hủy** task, không đo sau khi chạy xong.
- **Retry có ý nghĩa**: chỉ retry lỗi *transient* (I/O, Redis) với exponential backoff + jitter.
  **Không retry lỗi deterministic** — model chết thì retry 3 lần cũng chết 3 lần.
- **Bulkhead**: mỗi agent có pool riêng; Analyst đắt không làm cạn tài nguyên Prediction.
- **Dead-letter queue**: case thất bại hoàn toàn → DLQ, có người xem, không bị nuốt im lặng.
- **Saga**: Case Manager tạo case rồi bước sau lỗi → rollback, không để case mồ côi.
- **Đơn vị lỗi là case, không phải batch** — sửa lỗi blast radius của v0 (1 case xấu hỏng cả batch 512).

### 6.5 Chaos harness — đo cái đắt giá thật, không đo tautology

**Vấn đề của v1:** "silent failure rate = 0%" là *kiểm tra đặc tả*, không phải phát hiện khoa học. Ta
thiết kế hệ thống để không hỏng âm thầm rồi đo được rằng nó không hỏng âm thầm. Hội đồng sẽ hỏi: *"Anh
phát hiện được điều gì mà anh chưa biết trước khi chạy thí nghiệm?"*

**Bản v2 đo bốn thứ, trong đó ba thứ là kết quả thật:**

| # | Đo gì | Có phải kết quả thật không |
|---|---|---|
| 1 | **Đường cong độ nhạy/độ đặc hiệu của guard** trên nhiễu loạn *không được thiết kế riêng cho nó* | ✓ **Không biết trước** |
| 2 | **Độ trễ phát hiện**: bao nhiêu case trước khi guard báo động | ✓ **Không biết trước** |
| 3 | **Tỷ lệ báo động giả** khi hệ thống bình thường | ✓ **Không biết trước** |
| 4 | **Silent failure rate của Monolithic-Complete** dưới cùng kịch bản | ✓ **Không dàn dựng** — baseline được xây theo cách tự nhiên nhất, không cố tình làm cho hỏng |
| — | Silent failure rate của MAS-DSS | ✗ Tautology — vẫn báo cáo, nhưng **không** dùng làm luận cứ chính |
| 5 | **Chi phí của bảo đảm**: overhead latency p50/p95, số dòng code, số thành phần — so với Monolithic-Complete | ✓ Kết quả thật, và bắt buộc phải trung thực |

**Phân loại lỗi tiêm vào** (đây là artifact A4 — phương pháp có thể tái sử dụng):

| Nhóm | Lỗi cụ thể | Mức |
|---|---|---|
| **Crash** | Agent raise exception; agent treo quá `reply_by`; Redis chậm 5s | k = 1, 2, 3 agent |
| **Byzantine — thô** | Model trả hằng số; phương sai output = 0 | — |
| **Byzantine — tinh vi** | **Drift phân phối feature dần dần: 5%, 10%, 20%** | 3 mức |
| **Byzantine — tinh vi** | **Hoán vị nhãn một phần** (p = 5%, 10%, 20% nhãn bị đảo) | 3 mức |
| **Byzantine — tinh vi** | **Bid lệch hệ thống**: một analyst luôn +0.15 confidence | — |

Nhóm "tinh vi" là nhóm **guard không được thiết kế riêng để bắt** — kết quả ở đó mới là kết quả.

**Giao thức so sánh:** chạy **cùng kịch bản lỗi** trên MAS-DSS và trên Monolithic-Complete. Không so
với MIS/single-ML — chúng không đủ tư cách tham gia thí nghiệm này, và nói thẳng điều đó.

---

## Phần 7 — Tầng xử lý văn bản tiếng Bồ Đào Nha

Đây là chỗ thay đổi phương pháp lớn nhất so với v0/v1, và là chỗ dễ bị đánh nhất nếu không sửa.

### 7.1 Vì sao keyword lexicon phải bị loại bỏ

| Vấn đề | Ví dụ | Hệ quả |
|---|---|---|
| Danh sách từ khóa **không được kiểm định** — tác giả không nói tiếng Bồ | — | Construct validity threat trực diện: công cụ đo không được kiểm định |
| **Phủ định** | `"produto não chegou quebrado"` (hàng KHÔNG bị vỡ) chứa `quebrado` → gán `product_quality` | Nhãn sai có hệ thống |
| **Biến thể chính tả** | `nao`, `não`, `naum`, `n`, `ñ` | Trượt phần lớn |
| **Đa nhãn bị ép đơn nhãn** | `"produto quebrado na entrega"` — delivery hay quality? | `idxmax` chọn theo alphabet khi hòa — bug thật |

### 7.2 Kiến trúc hai tầng theo bằng chứng

**Việc P0 số 1 của toàn bộ dự án: đếm % đơn bất mãn không có `review_comment_message`.** Con số này
(dự kiến 40–45%) quyết định RQ2 có tồn tại được hay không, và phải nằm ngay đầu Chương 5.

```
Đơn bất mãn
├── Tầng A — CÓ bình luận  (~55–60%)
│     BERTimbau (neuralmind/bert-base-portuguese-cased) làm ENCODER đóng băng
│       → classifier head nhẹ, ĐA NHÃN, huấn luyện trên gold set
│       → Quality Analyst và Service Analyst dùng head này
│     Weak label chỉ dùng để pre-train head, KHÔNG dùng để đánh giá
│
└── Tầng B — KHÔNG bình luận  (~40–45%)
      Quality & Service Analyst phát REFUSE (thiếu bằng chứng)
      Chỉ Delivery & Price Analyst được bid trên bằng chứng cấu trúc
      Nếu không bid nào vượt τ → cause = unknown → escalate
```

**Tầng B là lời thú nhận có kiểm soát, và nó *mạnh* chứ không yếu:** với gần một nửa dữ liệu, "nguyên
nhân" trong hệ v0 chính là biến `delivery_delay_days` được đổi tên, rồi RandomForest học lại một câu
lệnh `if`. Thừa nhận điều đó và để hệ thống `REFUSE` là **đúng về mặt tri thức luận**, đồng thời làm
**DP3 trở nên load-bearing** và cho RQ5(b) một câu trả lời thật.

### 7.3 Vì sao BERTimbau không phá lập luận "không dùng LLM"

| Tiêu chí | BERTimbau encoder |
|---|---|
| Sinh văn bản? | **Không** — chỉ trả embedding |
| Sampling / nhiệt độ? | **Không** — eval mode, seed cố định, deterministic |
| Tái lập được? | **Có** — model công khai, phiên bản ghim, cùng input → cùng output |
| Có phải "LLM agent"? | **Không** — không có prompt, không có suy luận tự do, không có tự chủ ngôn ngữ |

→ Lập luận ở §8 (vì sao MAS deterministic, không LLM agent) **vẫn nguyên vẹn**. BERTimbau là một
*capability* ML như LightGBM, chỉ khác miền dữ liệu.

---

## Phần 8 — Decision point và feature set

### 8.1 Chốt T₃ và đổi framing

| Decision point | Feature có sẵn | Hành động khả thi | Vai trò trong luận văn |
|---|---|---|---|
| T₁ — lúc đặt hàng | Chỉ static | Chọn 3PL, cảnh báo seller | Ngoài phạm vi |
| **T₂ — lúc bàn giao vận chuyển** | + `carrier_handover_days`, ETA | Expedite, đổi tuyến | **Thí nghiệm cắt lớp cho RQ5(a)** |
| **T₃ — ngay sau khi giao hàng** ← **CHỐT** | Toàn bộ feature giao hàng | **Service recovery** trước khi khách viết review | **Cấu hình chính** |

Cửa sổ can thiệp ở T₃ là **có thật**: trung vị khoảng cách từ lúc giao đến lúc viết review trong Olist
là vài ngày. Bài toán trở thành **service recovery** — có cả một dòng văn liệu marketing/OM đứng sau
(recovery paradox), và hợp lý về mặt nghiệp vụ.

### 8.2 Yêu cầu cài đặt

`decision_point` phải là **tham số cấu hình**, không phải nhánh code:

```python
FeatureSet(decision_point="T3")   # cấu hình chính
FeatureSet(decision_point="T2")   # thí nghiệm RQ5(a) — CHỈ đổi config, không fork code
```

Mỗi feature khai báo `available_at` ∈ {T1, T2, T3}; `FeatureSet` lọc theo decision point. Nhờ vậy thí
nghiệm context validity là một lần đổi cấu hình, không phải một lần viết lại pipeline — và không thể
vô tình rò rỉ feature của T₃ vào kịch bản T₂.

### 8.3 Bảng thanh lọc feature

| Feature | Quyết định | Lý do |
|---|---|---|
| `review_lag_days` | **XÓA** | **Leakage trắng trợn** — chỉ tồn tại sau khi review đã viết, mà review score là nhãn |
| `delivery_delay_days`, `delivery_days` | Giữ, `available_at = T3` | Hợp lệ ở T₃ |
| `carrier_handover_days` | Giữ, `available_at = T2` | Có ở cả T₂ và T₃ |
| `freight_ratio`, `price`, `payment_value` | Giữ, `available_at = T1` | Static |
| Thống kê seller/category | Giữ, **chỉ học từ tập train** | Chống rò rỉ; split theo thời gian, không random |

### 8.4 Tập hành động service recovery (thay tập luật cũ)

| Bỏ | Thay bằng |
|---|---|
| `expedite_shipment_and_notify_customer` | `proactive_apology_with_coupon` |
| — | `preemptive_ticket_open` (mở ticket CSKH trước khi khách khiếu nại) |
| — | `cs_callback_within_24h` |
| — | `partial_refund` / `compensation_voucher` |
| — | `return_replacement_offer` |
| — | `seller_audit_flag` |
| — | `escalate_to_human` (bắt buộc khi `degradation_level > 0` hoặc `cause = unknown`) |

`expedite_shipment` bất khả thi về mặt thời gian ở T₃ — giữ nó lại là để hội đồng tìm ra mâu thuẫn.

---

## Phần 9 — Baseline Monolithic-Complete

Không có baseline này, RQ3 là đánh nhau với bù nhìn và cả Chương 5 mất giá trị. Nó là **thành phần
hạng nhất của codebase**, không phải script phụ.

| | MIS | Single-ML | **Monolithic-Complete** | MAS-DSS |
|---|---|---|---|---|
| Dự báo | ✗ (ngưỡng mô tả) | ✓ | ✓ | ✓ |
| Quy kết nguyên nhân | ✗ | ✗ | ✓ (đơn nhãn, argmax) | ✓ (đa nhãn, CNP) |
| Sinh hành động | ✗ | ✗ | ✓ (cùng YAML) | ✓ |
| Giải thích | ✗ | ✗ | một phần (feature importance) | ✓ (từ message log) |
| **Chịu lỗi** | ✗ | ✗ | **✗** | **✓** ← chỗ MAS thắng |

**Nguyên tắc xây dựng — phải công bằng, nếu không lại là bù nhìn lần hai:**

| Dùng chung với MAS-DSS | Không có |
|---|---|
| **Cùng** LightGBM đã huấn luyện, cùng siêu tham số | Message passing |
| **Cùng** BERTimbau encoder + head | Contract Net, ngân sách tính toán |
| **Cùng** tập luật DSS YAML | Blackboard |
| **Cùng** split thời gian, cùng feature set, cùng decision point | Supervisor, circuit breaker, output guard |
| **Cùng** gold set để đánh giá | Degradation ladder, quyền REFUSE |

Monolithic-Complete được viết theo **cách tự nhiên nhất mà một kỹ sư giỏi sẽ viết** — một quy trình
tuần tự, exception thì log rồi đi tiếp. Chính vì không cố tình làm cho nó hỏng nên **silent failure
rate của nó là kết quả thực nghiệm thật**.

---

## Phần 10 — Gold set (A3) — đường tới hạn của cả luận văn

Đây là hạng mục mất nhiều thời gian nhất và **phải bắt đầu song song với code, không phải sau khi code
xong**. Không có nó, Chương 5 không có giá trị.

| Hạng mục | Quy cách |
|---|---|
| Kích thước | **300–400 đơn bất mãn** |
| Lấy mẫu | **Phân tầng** theo: có/không bình luận × nhóm hàng × mức trễ |
| Annotator | **Hai người độc lập**, codebook rõ ràng |
| Nhãn | **Đa nhãn bắt buộc** (một đơn có thể vừa delivery vừa quality) |
| Độ tin cậy | Báo cáo **Cohen's κ**. Nếu κ < 0.6 → chính định nghĩa nguyên nhân có vấn đề, **và đó cũng là phát hiện đáng viết** |
| Chia đôi | Nửa A: **đo độ nhiễu của weak label** (weak label đúng bao nhiêu % so với gold → threat được định lượng). Nửa B: **test set thật** |
| Rào cản tiếng Bồ | (a) dịch máy + người thứ hai kiểm chứng mẫu dịch, ghi vào Threats to Validity; hoặc (b) thuê 1 annotator biết tiếng Bồ trên Prolific/Upwork cho 400 mẫu — chi phí rất thấp |

**Hỗ trợ kỹ thuật cần xây (nhỏ, nhưng phải có):** script lấy mẫu phân tầng, giao diện gán nhãn tối
giản (Streamlit là đủ), script tính κ, script đo độ nhiễu weak label. Ước lượng ~1 ngày code, và nó mở
khóa toàn bộ Chương 5.

**Cưỡng chế trong code:** hàm đánh giá quy kết nguyên nhân **chỉ nhận gold set**; truyền weak label vào
phải raise. Đây là cách duy nhất bảo đảm vòng tròn đánh giá không lẻn về sau ba tháng.

---

## Phần 11 — Tech stack

| Thành phần | Chọn | Vì sao |
|---|---|---|
| Runtime | Python 3.11 + `asyncio` | — |
| **Execution engine** | **LangGraph** + Redis checkpointer | Plan execution, conditional routing, checkpoint/resume, `interrupt` cho HITL |
| **MAS layer** | **Tự viết** (~500–700 LOC) | Envelope, 9 performative, CNP có ngân sách, supervisor, circuit breaker, output guard — **đây là artifact Design Science** |
| Message bus | Redis Streams | Fan-out CNP song song + audit log. Consumer group, ACK/NACK, DLQ |
| Working memory | LangGraph state → Redis checkpointer | **Một nguồn sự thật duy nhất** |
| Persistent store | PostgreSQL + SQLAlchemy | Case store, message log (audit), decision trace |
| Precedent memory | Postgres + `sklearn.neighbors` | Không cần vector DB vì không có embedding sinh từ LLM |
| ML capability | LightGBM + scikit-learn (+ isotonic) | Deterministic, <1ms/case, so sánh công bằng với baseline |
| **Text capability** | **BERTimbau encoder (đóng băng) + head đa nhãn** | Hiểu phủ định, biến thể chính tả; deterministic; **không phải LLM agent** |
| Critic / Arbiter | Engine ràng buộc + thứ tự ưu tiên YAML (code thuần) | Deterministic, **không tham số bịa** |
| Observability | OpenTelemetry → Jaeger | 1 trace = 1 case, 1 span = 1 message |
| API | FastAPI | Agent runtime + manager API |
| Dashboard | Streamlit | Đủ cho prototype; thêm tab annotation và tab chaos |
| Đóng gói | docker-compose | redis + postgres + app + jaeger (4 service) |
| Test | pytest + **chaos harness** | Fault injection là **thí nghiệm**, không phải test phụ |

**Chi phí vận hành: $0.** Không API key, không token. Với Design Science đây là *ưu điểm*: artifact tái
lập hoàn toàn, ai chạy lại cũng ra đúng số — điều một hệ có LLM sinh văn bản không đảm bảo nổi.

---

## Phần 12 — Bộ chỉ số

### Bỏ hẳn

| Chỉ số | Vì sao bỏ |
|---|---|
| `action_cause_fit` | **Vòng tròn tầng hai**: bảng `CAUSE_ACTION_FIT` do ta viết, tập luật sinh hành động cũng do ta viết → chỉ đo "hai file YAML tôi viết có nhất quán với nhau không" |
| `pipeline_completeness` làm luận cứ chính | Tautology: baseline bị *định nghĩa* là bằng 0 |
| Mọi chỉ số "giá trị cứu vãn được" | Xây trên tham số bịa (C1) |

`pipeline_completeness` **vẫn được báo cáo** nhưng trình bày đúng bản chất: mô tả sự khác nhau về chức
năng giữa các kiến trúc, **không** phải bằng chứng ưu việt.

### Giữ và bổ sung

**A. Dự báo — điều kiện kiểm soát (H1)**
- **PR-AUC là chính**, ROC-AUC là phụ (mất cân bằng lớp ~12–15%)
- **Kiểm định tương đương** (equivalence test), không phải t-test — vì kỳ vọng *không khác biệt*
- Phân tích độ nhạy ngưỡng `review_score ≤ 2` vs `≤ 3`, báo cáo cả hai
- Ngưỡng quyết định chọn theo chi phí, không mặc định 0.5

**B. Quy kết nguyên nhân — trên gold set (H2)**
- **Macro-F1 đa nhãn trên gold set** (không bao giờ trên weak label)
- Cắt lớp: nhóm **đa nguyên nhân** và nhóm **không có bình luận** — hai tình huống RQ2 nêu đích danh
- Độ nhiễu weak label so với gold — threat được định lượng
- ECE / Brier của từng analyst, trước và sau calibration

**C. Phối hợp (coordination) — MIS/single-ML không đủ tư cách tham gia**
- Số message/case, độ sâu cây hội thoại, coordination overhead (ms) — **cái giá**
- Tỷ lệ case đi đường tắt (LOW risk skip) — **lợi ích**
- `bid_entropy` — độ đồng thuận giữa analyst; entropy cao = đa nguyên nhân
- **Chất lượng quy kết trên mỗi ms tính toán** — chỉ số riêng của CNP có ngân sách
- Tỷ lệ Critic bác bỏ; tỷ lệ Arbiter đứng về phía Critic
- Tỷ lệ `REFUSE` và tỷ lệ `cause = unknown` theo tầng A/B

**D. Chịu lỗi (resilience) — chaos harness (H4, H6)**
- **Đường cong độ nhạy/độ đặc hiệu của guard** theo mức nhiễu loạn ← *kết quả thật*
- **Độ trễ phát hiện** (số case trước báo động) ← *kết quả thật*
- **Tỷ lệ báo động giả** khi bình thường ← *kết quả thật*
- **Silent failure rate của Monolithic-Complete** ← *kết quả thật*
- Silent failure rate của MAS-DSS ← báo cáo, nhưng nêu rõ là kiểm tra đặc tả
- Chất lượng quyết định khi k agent chết (k = 1, 2, 3); phân bố `degradation_level`; MTTR; độ sâu DLQ

**E. Chi phí của kiến trúc (H5) — bắt buộc báo cáo**
- Latency p50/p95 end-to-end, MAS-DSS vs Monolithic-Complete
- Số thành phần, số dòng code của tầng chịu lỗi
- **Không được giấu.** Khả năng chịu lỗi không miễn phí; báo cáo cái giá làm luận văn đáng tin hơn nhiều

**F. Đánh giá bởi chuyên gia (H3) — bằng chứng không tự tham chiếu duy nhất**
- 100–150 case × 3 hệ (MIS / Monolithic-Complete / MAS-DSS), **trình bày mù và ngẫu nhiên hóa**
- 3–5 người có kinh nghiệm vận hành TMĐT/CSKH, Likert 5 mức: *phù hợp*, *khả thi*, *giải thích được*
- **Krippendorff's α**; kiểm định phi tham số (Friedman + post-hoc)

**G. Bộ nhớ**
- Precedent hit rate; ablation tắt precedent → mức giảm macro-F1 trên gold set và ECE

---

## Phần 13 — Ánh xạ Design Principles → cơ chế code

Bốn DP là **đóng góp lý thuyết** của luận văn (A2). Mỗi DP phải có một cơ chế cưỡng chế tương ứng trong
code — nếu không, nó chỉ là câu văn hay.

| DP | Cơ chế cưỡng chế | Ablation tương ứng | Chỉ số chứng minh |
|---|---|---|---|
| **DP1 — Suy giảm minh bạch** | `degradation_level` là trường **bắt buộc** của `Decision`; Rule Engine gắn `needs_human_review` khi > 0 | Tắt guard/ladder → chạy chaos | Silent failure rate (MAS vs Monolithic), phân bố degradation_level |
| **DP2 — Quy kết bằng cạnh tranh** | CNP hai pha, đa nhãn, `bid_entropy`, cấm `idxmax` | Thay CNP bằng classifier đơn khối | Macro-F1 trên gold set, **cắt lớp đa nguyên nhân** |
| **DP3 — Từ chối thay vì đoán** | Performative `REFUSE`; OOD detector; tầng B không có bình luận | Cấm REFUSE, ép agent luôn trả lời | Tỷ lệ quyết định sai trên tầng B; điểm chuyên gia |
| **DP4 — Nguồn gốc từ giao tiếp** | Explanation Agent **chỉ đọc message log**, không nhận tham số ngoài | Dựng trace viết tay → so độ phân kỳ | Tỷ lệ trace tái lập được từ log; điểm "giải thích được" của chuyên gia |

Cột "Ablation" là lý do cột này tồn tại: **DP không được kiểm chứng thì không phải đóng góp**.

---

## Phần 14 — Lộ trình

| GĐ | Nội dung | Kết quả kỹ thuật | Kết quả luận văn |
|---|---|---|---|
| **0** | **P0 dữ liệu**: đếm % không bình luận; xóa `review_lag_days`; chốt T₃; sửa tập luật bỏ `expedite` | Feature set và action set đúng | Chốt được phạm vi Chương 1 |
| **0′** | **Khởi động gold set** (song song, chạy suốt) | Sampler + UI gán nhãn + script κ | **A3 — đường tới hạn** |
| **1** | MAS layer: envelope, 9 performative, actor, Redis Streams; LangGraph skeleton | Agent cũ bọc thành node, chạy qua message | §3.3 Kiến trúc — **RQ1** |
| **2** | BERTimbau head đa nhãn + kiến trúc hai tầng A/B | Quality/Service Analyst chạy trên text thật | Xử lý threat construct validity |
| **3** | CNP có ngân sách + calibrate bid + định tuyến động | Analyst đấu thầu dưới ràng buộc; case LOW đi đường tắt | **RQ2** |
| **4** | **Fault tolerance**: supervisor, circuit breaker, output guard, degradation ladder, DLQ | Suy giảm mềm, không hỏng âm thầm | Nền cho **RQ4** |
| **5** | **Monolithic-Complete** baseline | Baseline mạnh thật | Cứu giá trị cả Chương 5 |
| **6** | Precedent memory (kNN, chỉ train) | Recommendation tra tiền lệ | Ablation bổ sung |
| **7** | Policy Critic (ràng buộc) + Arbiter | Agent tranh biện có căn cứ | Ablation: tắt Critic → can thiệp thừa |
| **8** | **Chaos harness** đầy đủ (5 nhóm lỗi, 3 mức) | Đường cong độ nhạy guard | **RQ4 — đóng góp chính** |
| **9** | **Đánh giá chuyên gia** (A7) | Điểm Likert + Krippendorff's α | **RQ3** |
| **10** | Cắt lớp T₂ và tầng A/B | Kết quả context validity | **RQ5** |

**Đường tới hạn: 0 → 0′ → 1 → 3 → 4 → 5 → 8.**

Nếu thiếu thời gian, cắt theo thứ tự: **GĐ 6 (precedent memory) trước, rồi GĐ 7 (Critic).**
**Tuyệt đối không cắt GĐ 0′ (gold set), GĐ 4, GĐ 5, GĐ 8** — đó là bốn thứ giữ cho Chương 5 có giá trị.

---

## Phần 15 — Rủi ro

| Rủi ro | Mức | Cách xử |
|---|---|---|
| **Gold set không kịp** | **Cao nhất** | Bắt đầu từ tuần đầu, song song với code. Nếu chỉ kịp 200 đơn thì vẫn báo cáo — 200 đơn có κ tốt hơn 400 đơn không có |
| **Tỷ lệ không bình luận > 50%** | Trung bình | Kiến trúc hai tầng đã lường trước; con số này *củng cố* DP3 chứ không phá thiết kế. Nhưng phải báo cáo ngay đầu Chương 5 |
| **Hai nguồn sự thật** giữa LangGraph state và Redis Hash | Cao | Quy tắc §1. Đây là bug nguy hiểm nhất của bản hybrid |
| **Bid không calibrate** → analyst tự tin quá mức luôn thắng | Cao | Isotonic trên validation, báo cáo ECE trước/sau. Hội đồng sẽ hỏi |
| **Không tìm được 3–5 chuyên gia** | Cao | Dùng người làm TMĐT/CSKH ở Việt Nam — tình huống (giao trễ, hàng lỗi, phí ship cao) mang tính phổ quát. Ghi rõ trong Threats to Validity. Hạ xuống 3 người nếu cần, báo cáo α trung thực |
| **MAS overhead làm latency tệ hơn** | Chắc chắn xảy ra | **Đã khai báo trước là H5 kỳ vọng thua.** Báo cáo trung thực, lập luận đánh đổi bằng số liệu chaos harness |
| Hội đồng hỏi *"sao không dùng LLM?"* | Trung bình | Ba lý do: tái lập, so sánh công bằng, tách bạch causal claim. Nhánh thí nghiệm LLM Critic là tùy chọn nếu dư thời gian |
| Hội đồng hỏi *"sao không để LangGraph lo hết?"* | Trung bình | LangGraph mù với Byzantine fault (§6.1) và không có khái niệm degradation ladder — **đó chính là đóng góp** |
| Hội đồng hỏi *"CNP hay chỉ là ensemble?"* | Trung bình | Ngân sách tính toán làm giao thức load-bearing (§4.2); có chỉ số chất lượng/ms làm bằng chứng |
| BERTimbau chậm làm latency xấu | Thấp | Đó chính là lý do có ngân sách tính toán — case rủi ro thấp không phải trả tiền cho nó |

---

## Phụ lục — Cấu trúc mã nguồn đề xuất

```
src/mas_dss/
├── common/
│   ├── schemas.py           # OrderCase, Decision (có degradation_level), Evidence
│   ├── message.py           # Message envelope, 9 Performative          ← A1
│   └── ontology.py          # Bid, Critique, DegradationLevel           ← A1
├── layer1_data_integration/ # GIỮ NGUYÊN từ v0
│   └── features.py          # + available_at cho từng feature, FeatureSet(decision_point)
├── mas/                     # ← TẦNG MỚI, artifact khoa học
│   ├── actor.py             # mailbox, policy ACT/DEFER/DELEGATE/REFUSE
│   ├── bus.py               # Redis Streams, consumer group, DLQ
│   ├── contract_net.py      # CFP hai pha + knapsack ngân sách          ← §4.2
│   ├── supervisor.py        # cây giám sát, circuit breaker
│   ├── health_monitor.py    # drift, PSI, phát hiện Byzantine fault
│   ├── guards.py            # schema / sanity / calibration / consistency
│   └── degradation.py       # ladder, cưỡng chế needs_human_review      ← DP1
├── agents/
│   ├── analytics.py  prediction.py
│   ├── analysts/            # delivery, quality, service, price (có cost_class)
│   ├── recommendation.py  policy_critic.py  arbiter.py
│   ├── rule_engine.py  explanation.py  case_manager.py
├── graph/
│   └── plan.py              # LangGraph nodes, conditional edges, interrupt
├── memory/
│   ├── precedent.py         # kNN, assert chỉ-train                     ← §5.2
├── baselines/
│   ├── mis.py  single_ml.py
│   └── monolithic_complete.py   # ← A6, dùng chung model + YAML
├── evaluation/
│   ├── metrics.py           # đã bỏ action_cause_fit
│   ├── gold_set.py          # sampler, κ, đo nhiễu weak label; CHỈ nhận gold
│   ├── chaos/               # ← A4: fault taxonomy, injector, kịch bản
│   └── expert_study.py      # ← A7: sinh phiếu mù, tính Krippendorff's α
└── pipelines/
    └── build_dataset.py  train_models.py  run_pipeline.py  run_evaluation.py  run_chaos.py
```
