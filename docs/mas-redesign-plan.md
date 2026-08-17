# Plan thiết kế lại: từ pipeline sang hệ đa tác tử thực thụ

> ⚠️ **TÀI LIỆU LỖI THỜI — ĐÃ BỊ THAY THẾ bởi [technical-design-v2.md](technical-design-v2.md).**
>
> Bản này viết *trước* [adversarial-review.md](adversarial-review.md). Ba mục dưới đây **đã bị chính
> bản phản biện đó bác bỏ** vì Olist không có biến treatment (không cột nào ghi hành động đã áp dụng):
> - **§4.3 Policy Critic tính EV** — `ΔP(recover | action)` không ước lượng được → phải bịa tham số
> - **§5 Episodic memory chứa kết quả hành động** — bịa dữ liệu
> - **§10 nhóm chỉ số "chi phí can thiệp vs giá trị cứu vãn"** — xây trên tham số bịa
>
> Ngoài ra §4.2 (CNP) đã được sửa lại thành **CNP có ngân sách tính toán** để không còn là "ensemble
> đội lốt giao thức", và tầng xử lý text đã đổi từ keyword lexicon sang **BERTimbau + head đa nhãn**.
>
> Giữ file này làm **hồ sơ lịch sử thiết kế**. Đừng cài đặt theo nó.

Tài liệu này là **bản thiết kế**, chưa phải code. Nó trả lời năm yêu cầu: giao tiếp giữa agent,
điều phối, giám sát, bộ nhớ ngắn hạn, và xử lý ngoại lệ khi một agent hoạt động sai.

**Hai quyết định kiến trúc đã chốt:**
1. **Hybrid** — LangGraph làm engine thực thi bền vững; message layer, Contract Net, supervision là code tự viết.
2. **MAS thuần deterministic — không dùng LLM agent.** Toàn bộ tác tử là ML model, luật, hoặc engine tính toán.

---

## Phần 0 — Chẩn đoán hệ hiện tại

| Vấn đề | Bằng chứng trong code | Hệ quả với luận văn |
|---|---|---|
| Không có giao tiếp giữa agent | Agent chỉ mutate `OrderCase`; không có message, không có địa chỉ | RQ2 ("các tác tử phối hợp ra sao") **không có câu trả lời** |
| Điều phối là vòng `for` cứng | `CoordinatorAgent.run_batch()` | Không có tự chủ, không có định tuyến động |
| Ngoại lệ gây hỏng âm thầm | Agent lỗi → case đi tiếp với `prediction=None` → mọi đơn rơi vào `MONITOR`, hệ thống báo thành công | **Nguy hiểm nhất**: hệ thống nói dối thay vì sập |
| Timeout không được cưỡng chế | Đo latency *sau khi* agent chạy xong | Agent treo → pipeline treo vĩnh viễn |
| Retry vô nghĩa | Retry cùng batch, cùng input, model deterministic | Lỗi lặp lại y hệt 3 lần rồi bỏ qua |
| Không có bộ nhớ | Không có working memory / blackboard / episodic | Không học được gì từ case đã xử lý |
| Đơn vị lỗi là batch | 1 case xấu làm hỏng cả batch 512 case | Blast radius quá lớn |

**Giữ lại được:** Layer 1 (ingestion, preprocessing, feature store), các model ML đã huấn luyện, tập
luật DSS YAML, bộ chỉ số đánh giá. Chúng trở thành *capability* mà agent gọi, không còn là agent.

---

## Phần 1 — Ranh giới LangGraph ↔ code tự viết

Đây là quyết định quan trọng nhất của bản thiết kế hybrid. Nếu ranh giới mờ, bạn sẽ có **hai nguồn
sự thật về trạng thái case** và hệ thống sẽ hỏng theo cách rất khó debug.

| Thành phần | Ai sở hữu | Vì sao |
|---|---|---|
| Thực thi kế hoạch của Orchestrator (node, edge, conditional routing, cycle) | **LangGraph** | Khỏi tự viết state machine |
| Checkpoint / resume sau khi crash | **LangGraph** (Redis checkpointer) | Miễn phí, đúng đắn, đã được kiểm chứng |
| Retry policy ở mức node | **LangGraph** | Có sẵn |
| Human-in-the-loop (`interrupt`) | **LangGraph** | Có sẵn — dùng cho case escalate |
| **Message envelope + performative** | **Tự viết** | Là artifact khoa học — RQ2 |
| **Contract Net Protocol** (CFP → PROPOSE → ACCEPT) | **Tự viết** | Là artifact khoa học — RQ2 |
| **Blackboard semantics** (agent đọc kết quả của nhau) | **Tự viết** | Là artifact khoa học |
| **Supervisor, circuit breaker, degradation ladder** | **Tự viết** | LangGraph retry không đủ — nó không biết fallback, không biết Byzantine fault |
| **Output guard** (schema/sanity/calibration/consistency) | **Tự viết** | LangGraph không có khái niệm này |

### Quy tắc một nguồn sự thật

> **LangGraph state object *chính là* blackboard. Không xây blackboard thứ hai.**

```
LangGraph State (checkpoint xuống Redis)
├── case              : OrderCase          ← dữ liệu nghiệp vụ
├── blackboard        : dict               ← nơi agent đọc kết quả của nhau
│   ├── context, prediction, bids[], proposal, critique
├── plan_state        : dict               ← bước nào xong, agent nào đã chạy
├── health            : dict               ← degradation_level, circuit states
└── messages[]        : list[Message]      ← nhật ký hội thoại (append-only)
```

**Redis Streams** chạy song song, **không** giữ trạng thái — nó chỉ dùng cho hai việc:
1. Fan-out bất đồng bộ của phiên đấu thầu Contract Net (4 Analyst chạy song song)
2. Audit log bền vững của mọi message (đổ tiếp về Postgres)

Nếu bạn thấy mình ghi cùng một dữ liệu vào cả LangGraph state lẫn Redis Hash — dừng lại, bạn đang
tạo bug.

---

## Phần 2 — Mô hình tác tử

Một agent **không phải là một hàm**. Nó là thực thể có:

```
Agent
├── identity        : agent_id, role, capabilities[]
├── mailbox         : inbox queue (bounded, có backpressure)
├── local_state     : trạng thái riêng, không ai đọc trực tiếp
├── policy          : quyết định ACT / DEFER / DELEGATE / REFUSE khi nhận message
├── capability      : model ML, tập luật, hoặc engine tính toán
├── health          : heartbeat, error_rate, latency_p95, circuit state
└── degradation     : thang phương án dự phòng khi capability chính hỏng
```

Điểm mấu chốt: agent **có quyền từ chối**. Prediction Agent thấy đặc trưng nằm ngoài phân phối huấn
luyện (OOD) → trả `REFUSE` kèm lý do thay vì đoán bừa. Đó là tự chủ.

### Danh sách agent (bản deterministic — không LLM)

| Agent | Capability | Vai trò |
|---|---|---|
| **Orchestrator** | LangGraph plan | Định tuyến động theo trạng thái case |
| **Supervisor** | Code | Cây giám sát, restart, circuit breaker, degradation |
| **Health Monitor** | Code + thống kê | Heartbeat, drift detection, phát hiện agent sai mà không chết |
| **Analytics** | Thống kê + luật | Chỉ báo ngữ cảnh, phát hiện bất thường |
| **Prediction** | LightGBM + OOD detector | P(không hài lòng), confidence, `REFUSE` khi OOD |
| **Delivery Analyst** | GBM trên đặc trưng logistics | Đấu thầu case có tín hiệu giao hàng |
| **Quality Analyst** | GBM + TF-IDF trên review text | Đấu thầu case có tín hiệu chất lượng |
| **Service Analyst** | GBM + TF-IDF trên review text | Đấu thầu case có tín hiệu CSKH |
| **Price Analyst** | Luật + z-score giá theo nhóm hàng | Đấu thầu case có tín hiệu giá/phí ship |
| **Recommendation** | Playbook + kNN tiền lệ | Đề xuất hành động dựa trên case tương tự đã có kết quả |
| **Policy Critic** | **Engine chi phí–lợi ích + ràng buộc** | **Phản biện** đề xuất bằng tính toán kinh tế (xem §4.3) |
| **Arbiter** | Hàm hữu dụng kỳ vọng | Phân xử bất đồng Recommendation ↔ Critic |
| **Rule Engine** | YAML rules | Áp chính sách kinh doanh, chốt hành động |
| **Explanation** | Template trên message log | Dựng decision trace từ hội thoại |
| **Case Manager** | Code | Tạo/đóng intervention case |

**Xử lý review text không cần LLM.** TF-IDF + Logistic Regression trên bình luận tiếng Bồ là đủ, và
*mạnh hơn* về mặt phương pháp so với weak-label → RandomForest hiện tại: nó deterministic, rẻ, tái
lập được, và calibrate được xác suất.

---

## Phần 3 — Giao tiếp giữa agent (yêu cầu #1)

### Message envelope

Lấy cảm hứng từ **FIPA-ACL** (chuẩn giao tiếp agent của FIPA — tham chiếu học thuật vững):

```python
Message:
    msg_id          : UUID
    conversation_id : UUID          # gom mọi message của cùng một case
    trace_id        : UUID          # distributed tracing
    in_reply_to     : UUID | None   # dựng lại cây hội thoại
    sender          : agent_id
    receiver        : agent_id | broadcast | topic
    performative    : Performative
    content         : dict          # validate bằng Pydantic
    ontology        : str           # "order_case" | "bid" | "critique" | ...
    reply_by        : datetime      # DEADLINE — phải trả lời trước mốc này
    priority        : int
```

### Performative

| Performative | Ý nghĩa | Ai dùng |
|---|---|---|
| `REQUEST` | Yêu cầu thực hiện | Orchestrator → agent |
| `INFORM` | Thông báo kết quả | Agent → Orchestrator |
| `CFP` | Mời đấu thầu | Orchestrator → 4 Analyst |
| `PROPOSE` | Đấu thầu kèm confidence + evidence | Analyst → Orchestrator |
| `ACCEPT_PROPOSAL` / `REJECT_PROPOSAL` | Trao / từ chối thầu | Orchestrator → Analyst |
| `CHALLENGE` | Phản biện một đề xuất | Policy Critic → Recommendation |
| `REFUSE` | Từ chối vì ngoài năng lực (OOD) | Agent → Orchestrator |
| `FAILURE` | Thất bại khi đang thực hiện | Agent → Supervisor |
| `NOT_UNDERSTOOD` | Payload sai ontology | Bất kỳ |

Chỉ 9 performative — đủ dùng, không cố làm đủ FIPA-ACL.

**Message log là artifact khoa học.** Decision trace ở Layer 4 được *dựng lại từ message log* chứ
không viết tay như hiện nay. Đây là bằng chứng kiểm chứng được cho RQ2.

---

## Phần 4 — Điều phối (yêu cầu #2)

Ba cơ chế cho ba tình huống. Đây là phần trả lời trực tiếp RQ2.

### 4.1 Định tuyến động (LangGraph conditional edges)

Orchestrator **lập kế hoạch** cho từng case thay vì chạy thứ tự cứng:

```
nhận case
  → REQUEST Analytics
  → REQUEST Prediction
  → nếu risk == LOW           : chốt no_action, kết thúc     ← bỏ qua 5 agent
    nếu Prediction REFUSE (OOD): LangGraph interrupt → giao người
    nếu risk >= MEDIUM        : mở phiên Contract Net (4.2)
                                → Recommendation → Policy Critic
                                → (Arbiter nếu bất đồng)
                                → Rule Engine → Case Manager
```

Đây là *quyết định*, không phải vòng lặp. Tỷ lệ case đi đường tắt là một chỉ số hiệu năng mới.

### 4.2 Contract Net Protocol — phân loại nguyên nhân

Thay classifier đa lớp bằng **bốn chuyên gia cạnh tranh** (Smith, 1980 — protocol MAS kinh điển, rất
dễ bảo vệ trước hội đồng):

```
Orchestrator ──CFP(case)──▶ Delivery Analyst ──PROPOSE(conf=0.82, ev=[trễ 9 ngày])──┐
             ──CFP(case)──▶ Quality Analyst  ──PROPOSE(conf=0.31, ev=[...])          │
             ──CFP(case)──▶ Service Analyst  ──REFUSE(không có tín hiệu)             │
             ──CFP(case)──▶ Price Analyst    ──PROPOSE(conf=0.44, ev=[freight 0.3])  │
                                                                                      ▼
             ◀────────────────── thu thập bid, trao thầu ──────────────────────────────
             ──ACCEPT_PROPOSAL──▶ Delivery Analyst
```

Giá trị: (a) mỗi analyst có bằng chứng riêng → giải thích được; (b) hai analyst bid gần bằng nhau →
**nguyên nhân đa yếu tố**, thứ classifier đơn không nhận ra; (c) một analyst chết → ba analyst còn
lại vẫn đấu thầu, suy giảm mềm chứ không sập.

**Bid phải được calibrate** (Platt scaling / isotonic) — nếu không, analyst nào "tự tin quá mức" sẽ
luôn thắng thầu bất kể đúng sai. Đây là chi tiết kỹ thuật dễ bỏ sót và sẽ bị hội đồng hỏi.

### 4.3 Policy Critic — phản biện bằng kinh tế học, không bằng LLM

Đây là chỗ thiết kế thay đổi nhiều nhất khi bỏ LLM, và kết quả **tốt hơn cho luận văn**: Critic trở
thành một **engine chi phí–lợi ích** — hoàn toàn deterministic, đo được bằng tiền, và khớp chính xác
với chữ "DSS rule-based" trong tên đề tài.

Critic tính **hữu dụng kỳ vọng** của mỗi hành động được đề xuất:

```
EV(action) = P(dissatisfied) × ΔP(recover | action) × value_at_risk
             − cost(action)
             − penalty(ràng buộc bị vi phạm)

value_at_risk = giá trị đơn + CLV loss ước tính từ dữ liệu
                (khách bất mãn có tỷ lệ quay lại thấp hơn — đo được từ Olist)
```

Critic phát `CHALLENGE` khi bất kỳ điều nào đúng:

| Ràng buộc | Ví dụ |
|---|---|
| **EV âm** | Bồi thường 30 BRL cho đơn 45 BRL, xác suất cứu vãn 20% → lỗ |
| **Ngân sách can thiệp** | Đã dùng hết quota can thiệp trong ngày/tuần |
| **Cooldown seller** | Seller này đã bị audit 2 lần trong 30 ngày → can thiệp thừa |
| **Công bằng** | Tỷ lệ audit lệch bất thường về một nhóm seller |
| **Mâu thuẫn bằng chứng** | Recommendation dựa trên cause có `cause_probability < 0.4` |

Nếu Recommendation không rút đề xuất → **Arbiter** phân xử bằng hàm hữu dụng có trọng số chính sách
(ví dụ: ưu tiên giữ khách hơn tiết kiệm chi phí ở nhóm khách giá trị cao).

**Đây là nâng cấp thật cho Chương 5:** RQ3 hỏi "hiệu quả hỗ trợ quyết định" — giờ bạn đo được **bằng
tiền**: tổng chi phí can thiệp và giá trị kỳ vọng cứu vãn được, so với MIS (can thiệp mù theo ngưỡng
trễ hẹn) và single-ML (không sinh hành động nên không có chi phí lẫn lợi ích). Không LLM nào cho bạn
con số đó.

---

## Phần 5 — Bộ nhớ (yêu cầu #4)

| Tầng | Nội dung | Lưu ở đâu | Vòng đời |
|---|---|---|---|
| **Working memory (ngắn hạn)** | Blackboard của case: kết quả từng phần, bid, plan_state | **LangGraph state → Redis checkpointer** | Theo case (phút) |
| **Episodic memory (tiền lệ)** | Case đã xử lý + hành động + **kết quả thực tế** | Postgres + kNN index (sklearn) | Vĩnh viễn |
| **Procedural memory** | Tập luật + trọng số học từ kết quả | Postgres | Vĩnh viễn |

*(Không còn session memory vì đã bỏ Manager Assistant.)*

### Blackboard — bộ nhớ ngắn hạn

Không phải chỉ là chỗ chứa dữ liệu. Nó là **không gian làm việc chung** để agent đọc kết quả *của
nhau* mà không gọi trực tiếp:

```
blackboard (trong LangGraph state)
├── context           ← Analytics ghi
├── prediction        ← Prediction ghi
├── bids[]            ← 4 Analyst cùng ghi
│                       Price Analyst ĐỌC bid của Delivery trước khi bid:
│                       "đã trễ 9 ngày → phí ship không phải nguyên nhân chính,
│                        hạ confidence của mình xuống"     ← đây mới là phối hợp
├── proposal          ← Recommendation ghi
├── critique          ← Policy Critic ghi (kèm EV tính được)
└── plan_state        ← Orchestrator ghi
```

`plan_state` được LangGraph checkpoint xuống Redis → tiến trình chết giữa chừng thì chạy tiếp từ bước
dở, **không chạy lại từ đầu**. Đây là phần bạn được miễn phí từ LangGraph.

### Episodic memory — không cần vector DB

Vì không dùng LLM/embedding, tiền lệ được truy hồi bằng **kNN trên không gian đặc trưng đã chuẩn
hóa** (`sklearn.neighbors`), không cần ChromaDB/Qdrant. Bớt được một service.

Recommendation Agent, trước khi đề xuất, truy hồi *k* case tương tự **kèm kết quả thực tế**:

> *"3 đơn tương tự (cùng nhóm hàng, trễ 7-10 ngày, cùng bang): `expedite` áp dụng 2 lần → review
> score cuối 4 và 5. `apology_only` áp dụng 1 lần → review score 1. Đề xuất: expedite."*

Thứ này MIS **và** single-ML đều không làm được, và nó biến hệ thống từ "dự báo" thành "học từ kinh
nghiệm". Ablation: tắt episodic memory → đo `action_cause_fit` giảm bao nhiêu.

---

## Phần 6 — Giám sát và xử lý ngoại lệ (yêu cầu #3 và #5)

Phần yếu nhất của hệ hiện tại → thiết kế thành hệ thống con riêng.

### 6.1 Hai loại lỗi — LangGraph chỉ giải quyết được loại thứ nhất

| Loại | Biểu hiện | Ai xử lý |
|---|---|---|
| **Crash fault** | Exception, timeout, không heartbeat | LangGraph retry + **Supervisor tự viết** |
| **Byzantine / quality fault** | Agent trả về **kết quả hợp lệ nhưng sai** — model drift, xác suất luôn 0.5, phân bố nguyên nhân lệch hẳn | **Chỉ Health Monitor tự viết** — LangGraph hoàn toàn mù với loại này |

Loại thứ hai là loại giết chết hệ thống trong thực tế: không exception, không log đỏ, chỉ là **quyết
định sai hàng loạt**. Đây là lý do bạn không thể phó mặc fault handling cho LangGraph, và là điểm
cộng lớn cho luận văn.

### 6.2 Output guard — chống Byzantine fault

Mọi output đi qua validator trước khi vào blackboard:

```
Prediction trả về risk_score = 0.5 cho 100% case liên tiếp
  → Sanity guard: "phương sai output = 0 → nghi model hỏng"
  → Health Monitor: mở circuit
  → Supervisor: restart agent, nạp lại model từ checkpoint
  → vẫn hỏng → degradation ladder, đánh dấu degradation_level = 2
```

| Guard | Kiểm tra gì |
|---|---|
| **Schema** | Đúng kiểu, `risk_score ∈ [0,1]`, `cause ∈ enum` |
| **Sanity** | Phương sai output, phân bố nhãn không lệch quá ngưỡng |
| **Calibration** | So xác suất dự báo với tỷ lệ thực tế trên cửa sổ trượt (PSI, Brier score) |
| **Consistency** | Prediction nói risk=0.9 nhưng Analytics không thấy bất thường nào → mâu thuẫn → gọi Arbiter |

### 6.3 Degradation ladder — thay vì hỏng âm thầm

**Nguyên tắc bất di bất dịch: hệ thống không bao giờ được im lặng cho ra quyết định rác.**

| Agent | L0 (bình thường) | L1 | L2 | L3 (đáy) |
|---|---|---|---|---|
| Prediction | LightGBM | Logistic Regression | Heuristic `is_late → HIGH` | `escalate_to_human` |
| Root-Cause | CNP 4 analyst | Analyst còn sống bid | Luật từ khóa | `cause=unknown`, giao người |
| Recommendation | Playbook + tiền lệ | Playbook tĩnh | — | `assign_to_cs_review` |
| Policy Critic | EV đầy đủ | Chỉ check ràng buộc cứng | — | Bỏ qua, gắn cờ |
| Rule Engine | Luật đầy đủ | Luật core | — | `escalate` toàn bộ |

`Decision.degradation_level > 0` → Rule Engine **bắt buộc** gắn `needs_human_review`. Không quyết định
tự động nào được đưa ra trên nền hệ thống đang suy giảm.

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
- **Timeout thật**: `asyncio.wait_for()` — **hủy** task, không phải đo sau khi chạy xong.
- **Retry có ý nghĩa**: chỉ retry lỗi *transient* (I/O, Redis) với exponential backoff + jitter.
  **Không retry lỗi deterministic** — model chết thì retry 3 lần cũng chết 3 lần.
- **Bulkhead**: mỗi agent có pool riêng; Analyst chậm không làm cạn tài nguyên Prediction.
- **Dead-letter queue**: case thất bại hoàn toàn → DLQ, có người xem, **không bị nuốt im lặng**.
- **Saga**: Case Manager tạo case rồi Notification lỗi → rollback, không để case mồ côi.

### 6.5 Chaos harness — biến khả năng chịu lỗi thành số liệu

**Thí nghiệm mới cho Chương 5** mà MIS và single-ML không đủ tư cách tham gia:

| Kịch bản | MAS-DSS (mới) | MAS-DSS (cũ) | Single-ML | MIS |
|---|---|---|---|---|
| Bình thường | F1 = x | F1 = x | F1 = x | F1 = y |
| Prediction chết | F1 = x−δ, degraded=L2 | **HỎNG ÂM THẦM 100%** | HỆ SẬP | n/a |
| 1 Analyst chết | F1 = x−ε (3 analyst bid) | HỎNG ÂM THẦM | n/a | n/a |
| Model drift | Guard bắt, cảnh báo | **KHÔNG BIẾT GÌ** | KHÔNG BIẾT | n/a |
| Redis chậm 5s | Circuit mở, fallback | **TREO VĨNH VIỄN** | n/a | n/a |

Chỉ số then chốt: **silent failure rate** — tỷ lệ hệ thống cho ra quyết định sai mà *không* báo. Hệ
cũ: **100%** khi Prediction chết. Hệ mới: **0%** theo thiết kế. Con số đó tự nó là một đóng góp.

---

## Phần 7 — Tech stack

| Thành phần | Chọn | Vì sao |
|---|---|---|
| **Runtime** | Python 3.11 + `asyncio` | — |
| **Execution engine** | **LangGraph** (+ Redis checkpointer) | Plan execution, conditional routing, checkpoint/resume, `interrupt` cho HITL — miễn phí, đã kiểm chứng |
| **MAS layer** | **Tự viết** (~500 LOC) | Message envelope, 9 performative, Contract Net, supervisor, circuit breaker, output guard — **đây là artifact Design Science** |
| **Message bus** | Redis Streams | Fan-out CNP song song + audit log. Consumer group, ACK/NACK, DLQ |
| **Working memory** | LangGraph state → Redis checkpointer | **Một nguồn sự thật duy nhất** |
| **Persistent store** | PostgreSQL + SQLAlchemy | Case store, message log (audit), decision trace, outcome feedback |
| **Episodic memory** | Postgres + `sklearn.neighbors` kNN | Không cần vector DB vì không có embedding |
| **ML capability** | LightGBM + scikit-learn | Deterministic, <1ms/case, so sánh công bằng với baseline |
| **Text capability** | TF-IDF + Logistic Regression | Đọc review tiếng Bồ. Deterministic, calibrate được — **mạnh hơn weak-label→RF hiện tại** |
| **Critic/Arbiter** | Engine chi phí–lợi ích (code thuần) | Deterministic, đo được bằng tiền |
| **Observability** | OpenTelemetry → Jaeger | 1 trace = 1 case, 1 span = 1 message |
| **API** | FastAPI | Agent runtime + manager API |
| **Dashboard** | Streamlit (giữ) | Đủ cho prototype |
| **Đóng gói** | docker-compose | redis + postgres + app + jaeger (**4 service, không còn Chroma**) |
| **Test** | pytest + chaos harness | Fault injection là thí nghiệm, không phải test phụ |

**Chi phí vận hành: $0.** Không API key, không token. Với Design Science đây là *ưu điểm*: artifact
hoàn toàn tái lập được, ai chạy lại cũng ra đúng số — điều mà một hệ có LLM không đảm bảo nổi.

---

## Phần 8 — Xử lý lệch với literature review

Đề tài tên là "AI đa tác tử" và Chương 2 trích Reyes Fernández de Bulnes et al. (2025) về LLM-powered
MAS. Bỏ LLM sẽ bị hỏi. **Chuẩn bị sẵn câu trả lời, đừng để bị động:**

> *"Kiến trúc MAS-DSS đề xuất **không phụ thuộc vào LLM**. LLM là một capability có thể cắm vào tầng
> Analyst hoặc Critic, nhưng luận văn chọn hiện thực hóa bằng các capability deterministic vì ba lý
> do: (1) **tính tái lập** — yêu cầu bắt buộc của Design Science, artifact phải cho cùng kết quả khi
> đánh giá lại; (2) **so sánh công bằng** với baseline MIS và mô hình học máy đơn lẻ — nếu MAS dùng
> LLM còn baseline thì không, phần cải thiện đo được sẽ không quy được cho kiến trúc đa tác tử; (3)
> đóng góp của luận văn là **cơ chế phối hợp** (Contract Net, blackboard, supervision, degradation),
> không phải năng lực suy luận của mô hình nền."*

Điều chỉnh Chương 2 cho khớp: chuyển trọng tâm literature review từ *agentic AI / LLM-MAS* sang
*coordination protocols trong MAS* (Smith 1980 — Contract Net; Hayes-Roth 1985 — Blackboard;
FIPA-ACL; Erlang/OTP supervision). Đây là dòng tài liệu vững hơn và khớp với thứ bạn thực sự xây.

Giữ Reyes Fernández de Bulnes như một *hướng mở rộng tương lai* ở Chương 5, không phải nền tảng.

---

## Phần 9 — Lộ trình

| GĐ | Nội dung | Kết quả kỹ thuật | Kết quả luận văn |
|---|---|---|---|
| **0** | Giữ Layer 1 + model + rule YAML | Không đổi | — |
| **1** | MAS layer: envelope, 9 performative, actor, Redis Streams; LangGraph skeleton | Agent cũ bọc thành node, chạy qua message | §3.3 Kiến trúc — **RQ1** |
| **2** | Định tuyến động + Contract Net cho 4 Analyst (có calibrate bid) | Case LOW đi đường tắt; analyst đấu thầu | **RQ2** — cơ chế phối hợp |
| **3** | Bộ nhớ: blackboard (LangGraph state) + episodic kNN | Recommendation tra tiền lệ trước khi đề xuất | Đóng góp mới, ablation mạnh |
| **4** | Fault tolerance: supervisor, circuit breaker, output guard, degradation ladder, DLQ | Suy giảm mềm, không hỏng âm thầm | Thí nghiệm robustness |
| **5** | Policy Critic (EV engine) + Arbiter | Agent tranh biện bằng kinh tế học | Ablation: tắt Critic → đo can thiệp thừa |
| **6** | Đánh giá: benchmark cũ + chỉ số mới + chaos harness | `benchmark.md` mở rộng | **Chương 5** |

**Đường tới hạn: GĐ 1 → 2 → 4.** Nếu thiếu thời gian, cắt GĐ 3 (episodic memory) trước. **Đừng cắt
GĐ 4** — đó chính là câu hỏi bạn đặt ra.

---

## Phần 10 — Bộ chỉ số đánh giá

Giữ toàn bộ chỉ số cũ. Bổ sung ba nhóm — chỗ MAS thắng, và MIS/single-ML **không đủ tư cách tham gia**:

**Phối hợp (coordination)**
- Số message / case, độ sâu cây hội thoại, coordination overhead (ms) — *cái giá* của đa tác tử
- Tỷ lệ case đi đường tắt (LOW risk skip) — *lợi ích* của định tuyến động
- Bid entropy — độ đồng thuận giữa Analyst; entropy cao = nguyên nhân đa yếu tố
- Tỷ lệ Critic bác bỏ đề xuất; tỷ lệ Arbiter đứng về phía Critic

**Chịu lỗi (resilience)** — thí nghiệm chaos
- **Silent failure rate** — chỉ số quan trọng nhất. Cũ: 100%. Mới: 0%.
- Chất lượng quyết định khi k agent chết (k = 1, 2, 3)
- Phân bố `degradation_level`; MTTR; tỷ lệ circuit mở; độ sâu DLQ

**Kinh tế (mới — nhờ Critic deterministic)**
- Tổng chi phí can thiệp vs giá trị kỳ vọng cứu vãn được
- Tỷ lệ can thiệp thừa (false-positive intervention) — MAS vs MIS
- Đây là cách đo "hiệu quả hỗ trợ quyết định" của **RQ3 bằng tiền**, không phải bằng F1

**Bộ nhớ**
- Precedent hit rate; ablation tắt episodic memory → `action_cause_fit` giảm bao nhiêu

---

## Phần 11 — Rủi ro

| Rủi ro | Cách xử |
|---|---|
| **Hai nguồn sự thật** giữa LangGraph state và Redis Hash | Quy tắc §1: LangGraph state *chính là* blackboard. Redis Streams chỉ chở message, không giữ trạng thái. Đây là bug nguy hiểm nhất của bản hybrid |
| Bid không calibrate → analyst "tự tin quá mức" luôn thắng thầu | Platt scaling / isotonic trên tập validation. Hội đồng sẽ hỏi điều này |
| Weak label nguyên nhân bị phản biện (vấn đề cũ chưa giải quyết) | **Vẫn phải gán tay ~200 đơn để kiểm định.** Contract Net không xóa được vấn đề này |
| Hội đồng hỏi "sao không dùng LLM?" | Câu trả lời sẵn ở §8 |
| Hội đồng hỏi "sao không để LangGraph lo hết?" | Vì LangGraph mù với Byzantine fault (§6.1) và không có khái niệm degradation ladder. Đó chính là đóng góp của bạn |
| MAS overhead làm latency tệ hơn single-ML | Báo cáo **trung thực**. Lập luận: đánh đổi latency lấy khả năng giải thích, chịu lỗi, và chất lượng chuỗi quyết định — có số liệu chaos harness làm bằng chứng |
