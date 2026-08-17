# Kế hoạch triển khai mã nguồn vào `src-v3/`

> **Nguồn:** [build-plan.md](build-plan.md) (phân rã công việc WP0–WP11) và
> [technical-plan-v3.md](technical-plan-v3.md) (kiến trúc, 5 giao diện, kỷ luật kỹ thuật).
>
> Tài liệu này trả lời ba câu hỏi thi công: **đặt file nào ở đâu**, **tạo theo thứ tự nào**, và **cùng
> tồn tại với `src/` cũ ra sao**.

---

## Phần 1 — Nguyên tắc cùng tồn tại với `src/` cũ

Codebase cũ (`src/mas_dss/` với `layer1..layer5`) **không bị xóa và không bị sửa**. Nó đóng băng làm hồ
sơ, đúng như `mas-redesign-plan.md` và `technical-design-v2.md` đóng băng ở tầng tài liệu.

| Đối tượng | Quy tắc |
|---|---|
| `src/mas_dss/` | **Đóng băng.** Không sửa, không xóa. Không được dùng làm tham chiếu thiết kế |
| `src-v3/masdss/` | Codebase mới, **cấm import bất cứ thứ gì từ `mas_dss`** — cưỡng chế bằng test |
| `data/raw/` | **Dùng chung, chỉ đọc.** 9 tệp CSV Olist |
| `data/processed/`, `models/` | **Không đụng vào.** Đầu ra mới ghi sang `data/v3/`, `models/v3/` |
| `config/config.yaml`, `config/dss_rules.yaml` | **Không đụng vào.** Cấu hình mới đặt tại `config/v3/` |
| `tests/` | Giữ nguyên. Test mới đặt tại `tests-v3/` |

Lý do tách triệt để: `data/processed/order_cases.parquet` và `config/dss_rules.yaml` hiện có đang mang
những thứ đã bị bác bỏ — `review_lag_days` và hành động `expedite_shipment`. Ghi đè lên chúng sẽ làm mất
khả năng đối chiếu "trước và sau", còn đọc từ chúng sẽ kéo lỗi cũ vào hệ mới.

---

## Phần 2 — Bố trí `src-v3/` đầy đủ

Cột **Đợt** trỏ tới §4. Cột **Task** trỏ tới ID trong [build-plan.md](build-plan.md).

> **⚠️ Đây là bố trí *dự kiến*. Bố trí *thực tế* khác ở bốn chỗ.**
>
> Cây dưới đây giữ nguyên làm hồ sơ kế hoạch. **Nguồn chuẩn cho bố trí đang chạy là
> [technical-plan-v3.md §4](technical-plan-v3.md).** Bốn khác biệt, mỗi cái có lý do:
>
> | Dự kiến | Thực tế | Vì sao |
> |---|---|---|
> | `capabilities/text_encoder.py` — BERTimbau | **không tồn tại**; `cause_head.py` dùng TF-IDF | T3.3 chặn bởi quyết định không cài `torch` |
> | `runtime/bus.py`, `runtime/budget.py` | **không tồn tại** | Không có bus — mọi trao đổi qua orchestrator theo tô-pô hình sao. Ngân sách nằm ở `system/plan.py` vì nó là tham số của **kế hoạch** |
> | `reliability/supervisor.py`, `degradation.py` | gộp vào `breaker.py` và `blackboard.py` | `Supervisor` chỉ ~35 dòng; thang suy giảm là `Blackboard.degrade()` + bất biến trong `Decision` |
> | Một tệp một tác tử *(`analytics.py`, `prediction.py`, `rule_agent.py`…)* | gom theo vai trò: `core_agents.py`, `critic.py`, `analysts/pool.py` | Mỗi tác tử chỉ 15–40 dòng; một tệp cho mỗi tác tử tạo ra nhiều tệp gần rỗng |
>
> Ngoài ra **không xây**: `memory/precedent.py`, `goldset/annotate_app.py`, `chaos/taxonomy.py` —
> đều nằm trong danh sách cố ý không xây ở `technical-plan-v3.md §7`.

```
src-v3/masdss/
├── __init__.py
├── config.py                    # cấu hình tập trung + seed toàn cục      [Đ0 · T0.2]
│
├── core/
│   ├── ontology.py              # Cause, Evidence, Bid, Declaration, Critique [Đ0 · T5.1]
│   ├── message.py               # Message envelope + 10 Performative          [Đ0 · T5.2]
│   ├── decision.py              # Decision — degradation_level BẮT BUỘC       [Đ0 · T5.3]
│   └── errors.py                # TransientError vs DeterministicError        [Đ0 · T5.4]
│
├── runtime/
│   ├── actor.py                 # hộp thư, chính sách ACT/REFUSE              [Đ0 · T5.5]
│   ├── bus.py                   # bus trong tiến trình (asyncio.Queue)        [Đ0 · T5.5]
│   ├── faults.py                # ★ SEAM TIÊM LỖI — invoke()                  [Đ0 · T5.6]
│   ├── tracing.py               # span thủ công → SQLite                      [Đ0 · T5.7]
│   ├── message_log.py           # nhật ký append-only + schema SQLite         [Đ0 · T6.1]
│   └── budget.py                # ngân sách tính toán theo mức rủi ro         [Đ2 · T7.2]
│
├── system/
│   ├── plan.py                  # STAGE1_PLAN, STAGE2_PLAN — DẠNG DỮ LIỆU     [Đ0 · T6.2]
│   ├── orchestrator.py          # execute(plan, case, invoke_fn)              [Đ0 · T6.3]
│   ├── blackboard.py            # working memory của case                     [Đ0 · T6.4]
│   ├── contract_net.py          # CFP hai pha + knapsack ngân sách            [Đ2 · T7.1-7.4]
│   ├── explain.py               # dựng trace CHỈ từ conversation_id           [Đ1 · T6.8]
│   └── reliability/
│       ├── guards.py            # schema · sanity · calibration · consistency [Đ3 · T8.1]
│       ├── health.py            # heartbeat, PSI, drift                       [Đ3 · T8.2]
│       ├── breaker.py           # circuit breaker                             [Đ3 · T8.3]
│       ├── supervisor.py        # cây giám sát, restart, retry policy         [Đ3 · T8.4]
│       └── degradation.py       # thang suy giảm, cưỡng chế human review      [Đ3 · T8.5]
│
├── data/
│   ├── load.py                  # ghép 9 bảng Olist → bảng chuẩn hóa          [Đ1 · T1.1]
│   ├── features.py              # available_at ∈ {T1,T2,T3,T4} cho MỌI cột    [Đ1 · T1.2]
│   ├── featureset.py            # FeatureSet(decision_point)                  [Đ1 · T1.3]
│   ├── labels.py                # nhãn bất mãn + weak label (kiểu riêng)      [Đ1 · T1.5]
│   └── splits.py                # chia theo thời gian                         [Đ1 · T1.6]
│
├── capabilities/                # ★ DÙNG CHUNG MAS-DSS ↔ baselines ★
│   ├── base.py                  # Protocol Capability: cost_ms, can_handle, run
│   ├── risk_model.py            # LightGBM + isotonic                         [Đ1 · T3.1]
│   ├── ood.py                   # phát hiện ngoài phân phối                   [Đ1 · T3.2]
│   ├── text_encoder.py          # BERTimbau đóng băng + đệm embedding         [Đ1 · T3.3]
│   ├── cause_head.py            # head ĐA NHÃN 4 nguyên nhân                  [Đ1 · T3.4]
│   ├── price_signal.py          # z-score giá/phí theo nhóm hàng              [Đ1 · T3.5]
│   ├── calibration.py           # isotonic riêng từng analyst                 [Đ2 · T7.3]
│   └── rules.py                 # rule engine đọc YAML                        [Đ1 · T3.6]
│
├── agents/
│   ├── base.py                  # lớp nền agent — vỏ mỏng
│   ├── analytics.py                                                          [Đ2 · T6.5]
│   ├── prediction.py                                                         [Đ2 · T6.5]
│   ├── analysts/
│   │   ├── delivery.py  price.py  quality.py  service.py                     [Đ2 · T6.6]
│   ├── recommendation.py                                                     [Đ2 · T6.7]
│   ├── rule_agent.py  case_manager.py                                        [Đ2 · T6.7]
│   ├── policy_critic.py  arbiter.py            # CẮT ĐƯỢC — xem build-plan §7 [Đ3]
│   └── explanation.py                                                        [Đ1 · T6.8]
│
├── memory/
│   └── precedent.py             # kNN, assert chỉ-train — CẮT ĐƯỢC ĐẦU TIÊN   [Đ3]
│
├── baselines/
│   ├── mis.py                                                                [Đ2 · T4.1]
│   ├── single_ml.py                                                          [Đ2 · T4.2]
│   └── monolithic.py            # ★ ĐA NHÃN, chung capability, chung YAML     [Đ2 · T4.3]
│
├── goldset/
│   ├── sample.py                # phân tầng KHÔNG cân xứng 250 A / 150 B      [Đ1 · T2.1]
│   ├── annotate_app.py          # giao diện Streamlit tối giản                [Đ1 · T2.3]
│   ├── agreement.py             # Cohen's κ                                   [Đ1 · T2.4]
│   └── weak_noise.py            # đo độ nhiễu weak label so với gold          [Đ1 · T2.4]
│
├── chaos/
│   ├── taxonomy.py              # phân loại crash / Byzantine                 [Đ3 · T9.1]
│   ├── injector.py              # cắm vào runtime/faults.py, có seed          [Đ3 · T9.1]
│   ├── scenarios.py             # 5 nhóm × 3 mức                              [Đ3 · T9.2]
│   └── runner.py                # cùng kịch bản trên 2 kiến trúc              [Đ3 · T9.3]
│
├── evaluation/
│   ├── forecasting.py           # PR-AUC + kiểm định tương đương              [Đ3 · T10.1]
│   ├── attribution.py           # ★ CHỈ nhận gold set, weak label phải raise  [Đ3 · T10.2]
│   ├── selective.py             # đường cong risk–coverage                    [Đ3 · T10.3]
│   ├── coordination.py          # message/case, bid_entropy, chất lượng/ms    [Đ3 · T10.4]
│   ├── resilience.py            # độ nhạy guard, độ trễ phát hiện             [Đ3 · T10.5]
│   └── cost.py                  # latency p50/p95, quy mô kiến trúc           [Đ3 · T10.6]
│
└── cli/
    ├── build_dataset.py  train.py                                            [Đ1]
    ├── run_system.py                                                         [Đ0 → Đ2]
    ├── run_chaos.py                                                          [Đ3]
    └── run_evaluation.py        # MỘT lệnh ra đủ bảng Chương 5                [Đ3 · T11.1]

tests-v3/
├── test_layering.py             # capabilities/ không import agents/, system/ [Đ0 · T0.3]
├── test_no_legacy_import.py     # masdss không import mas_dss                 [Đ0]
├── test_determinism.py          # hai lần chạy giống nhau đến từng byte       [Đ0 · T0.4]
├── test_leakage.py              # available_at; chặn has_comment ở T₂/T₃      [Đ1 · T1.4]
├── test_decision_invariant.py   # degradation_level > 0 ⟹ needs_human_review  [Đ0 · T5.3]
├── test_no_argmax.py            # quét tĩnh agents/analysts, baselines        [Đ2 · T7.4]
├── test_baseline_parity.py      # baseline dùng CÙNG đối tượng capability     [Đ2 · T4.4]
├── test_explain_signature.py    # explain() chỉ nhận conversation_id          [Đ1 · T6.8]
└── test_chaos_repro.py          # cùng seed → kết quả trùng khớp              [Đ3 · T9.4]

config/v3/
├── system.yaml                  # seed, đường dẫn, ngưỡng τ, ngân sách B
├── rules.yaml                   # tập hành động phục hồi dịch vụ (KHÔNG expedite)
└── chaos/*.yaml                 # kịch bản tiêm lỗi

data/v3/    · dữ liệu dẫn xuất mới, không đụng data/processed/ cũ
models/v3/  · mô hình đã huấn luyện + đệm embedding BERTimbau
```

---

## Phần 3 — Cấu hình packaging

Sửa `pyproject.toml` để hai package cùng tồn tại, và **đổi `testpaths` sang `tests-v3`** để CI không
chạy test cũ đã lỗi thời:

```toml
[tool.setuptools.packages.find]
where = ["src", "src-v3"]

[tool.pytest.ini_options]
pythonpath = ["src", "src-v3"]
testpaths  = ["tests-v3"]

[tool.ruff]
line-length = 100
src = ["src-v3"]
```

**Phụ thuộc cần bổ sung vào `requirements.txt`:**

| Gói | Dùng cho | Ghi chú |
|---|---|---|
| ~~`torch` (bản CPU)~~ | ~~BERTimbau encoder~~ | ⬜ **Chưa cài — quyết định đã chốt.** T3.3 vì vậy bị chặn; `TfidfCauseHead` thay thế và đạt macro-F1 0,4730 so với 0,2196 của bản lexicon |
| ~~`transformers`, `sentencepiece`~~ | ~~BERTimbau~~ | Như trên. Nếu cài lại: **ghim phiên bản** — yêu cầu tái lập |
| `scikit-learn` | TF-IDF + Logistic Regression cho cause head, isotonic | Ghim phiên bản |
| `scipy` | Kiểm định tương đương (H1), thống kê | — |
| `hypothesis` | Property-based test cho bất biến `Decision` | — |

Không thêm gì khác. Redis, PostgreSQL, LangGraph, vector DB đều nằm ngoài phạm vi theo
`technical-plan-v3.md §2` và `§7`.

---

## Phần 4 — Bốn đợt triển khai

### Đợt 0 — Bộ khung chạy được *(walking skeleton)* · ~5 ngày · **bổ sung so với build-plan**

Đây là điều chỉnh duy nhất tôi đề xuất so với thứ tự trong `build-plan.md`, và lý do rất cụ thể.

**Vấn đề của thứ tự gốc:** WP6 (agents + orchestrator, 13 ngày) là gói rủi ro nhất và lại nằm ở tuần
7–9. Nếu năm giao diện ở `technical-plan-v3.md §5` có sai sót về thiết kế, ta chỉ phát hiện sau khi đã
xây xong toàn bộ tầng capabilities. Tương tự, `build-plan.md §9` đã nhận diện rủi ro *"seam tiêm lỗi đặt
sai chỗ, phát hiện muộn ở WP9"*.

**Cách xử lý:** dựng một **lát cắt dọc mỏng chạy được end-to-end**, dùng capability giả, trước khi xây
bất kỳ mô hình học máy nào.

| Bước | Nội dung |
|---|---|
| 1 | `core/` đầy đủ: ontology, message, decision, errors |
| 2 | `runtime/`: actor, bus, **faults.py**, tracing, message_log |
| 3 | `system/`: plan.py với một plan 3 bước, orchestrator, blackboard |
| 4 | Hai agent giả trả kết quả cố định, một capability giả | 
| 5 | `cli/run_system.py` xử lý **một case giả** đi trọn chuỗi |
| 6 | `system/explain.py` dựng trace từ nhật ký |
| 7 | **Một kịch bản chaos tối giản** tiêm lỗi qua `faults.py` để kiểm chứng seam |

**Tiêu chí ra khỏi Đợt 0** — đây là bản thu nhỏ của Gate G4 và G5:

- Một case đi trọn chuỗi và sinh ra `Decision` hợp lệ.
- Trace dựng lại được **chỉ từ `conversation_id`**.
- Tiêm được lỗi crash và lỗi Byzantine mà **không sửa một dòng nào** trong `system/` hay `agents/`.
- Hai lần chạy cho kết quả trùng khớp đến từng byte.
- Bốn test kỷ luật đã chạy xanh: phân tầng, không import mã cũ, tất định, bất biến `Decision`.

**Chi phí ròng: khoảng +2 ngày**, vì phần lớn công việc này thuộc WP5/WP6 vốn đã có trong ước lượng —
chỉ là làm sớm với capability giả. Đổi lại, ba rủi ro lớn nhất của dự án được kiểm chứng ở tuần 1–2 thay
vì tuần 9 và tuần 13.

> ### ✅ Đợt 0 — ĐÃ HOÀN THÀNH
>
> Năm tiêu chí ra đều đạt, xác nhận bằng `pytest` (26 test xanh):
>
> | Tiêu chí | Xác nhận bằng |
> |---|---|
> | Case đi trọn chuỗi, sinh `Decision` hợp lệ | `test_skeleton_e2e.py::test_every_case_produces_a_decision` |
> | Trace dựng lại **chỉ từ `conversation_id`** | `test_trace_is_rebuilt_from_log_alone`, `test_explainer_build_accepts_only_conversation_id` |
> | Tiêm crash và Byzantine **không sửa `system/` hay `agents/`** | `test_crash_injection_degrades_transparently`, `test_byzantine_injection_passes_through_seam`, `test_injection_requires_no_change_to_system_or_agents` |
> | Hai lần chạy trùng khớp đến từng byte | `test_determinism.py` (cả đường bình thường lẫn đường tiêm lỗi) |
> | Bốn test kỷ luật xanh | `test_layering`, `test_no_legacy_import`, `test_determinism`, `test_decision_invariant` |
>
> Bằng chứng vận hành — cùng một case, hai chế độ:
>
> ```
> bình thường          → action=preemptive_ticket_open · degradation_level=0 · needs_human_review=false
> tiêm crash:Prediction → action=escalate_to_human      · degradation_level=2 · needs_human_review=true
> ```
>
> Trace ở chế độ tiêm lỗi cho thấy `Orchestrator → Prediction [REQUEST]` **không có message trả lời** —
> hệ thống suy giảm minh bạch và ghi lại đúng chuyện đã xảy ra, thay vì hỏng âm thầm.

### Đợt 1 — Dữ liệu, capabilities, gold set · ~19 ngày

Thay capability giả bằng capability thật. Gold set khởi động song song ngay từ đầu đợt này.

| Nhóm | Task | Ghi chú |
|---|---|---|
| Dữ liệu | T1.1–T1.6 | `test_leakage.py` phải xanh trước khi đi tiếp |
| Gold set | T2.1–T2.7 | Chạy song song suốt Đợt 1 và Đợt 2 |
| Capabilities | T3.1–T3.6 | T3.4 chỉ hoàn tất khi có phần đầu của gold set |
| Explain | T6.8 | Nâng từ bản khung lên bản đầy đủ |

### Đợt 2 — Agents, Contract Net, baselines · ~23 ngày

| Nhóm | Task | Ghi chú |
|---|---|---|
| Baselines | T4.1–T4.4 | **Làm trước agents** — ép `capabilities/` thật sự độc lập |
| Agents | T6.5–T6.7 | Mỗi agent dưới ~80 dòng |
| Contract Net | T7.1–T7.4 | `test_no_argmax.py` bật lên từ đây |

### Đợt 3 — Chịu lỗi, chaos, đánh giá · ~32 ngày

| Nhóm | Task | Ghi chú |
|---|---|---|
| Reliability | T8.1–T8.5 | Không được cắt |
| Chaos | T9.1–T9.4 | Seam đã kiểm chứng từ Đợt 0 nên rủi ro thấp hơn nhiều |
| Evaluation | T10.1–T10.6 | — |
| Kết quả | T11.1–T11.3 | Một lệnh ra đủ bảng Chương 5 |
| Cắt được | `policy_critic`, `arbiter`, `precedent` | Theo thứ tự ở `build-plan.md §7` |

---

## Phần 5 — Quy ước mã nguồn

| # | Quy ước | Lý do |
|---|---|---|
| 1 | Mỗi module mở đầu bằng docstring ghi **`WP/Task` và `RQ` mà nó phục vụ** | Biến quy tắc "mọi thành phần truy được về một RQ" thành thứ kiểm tra được bằng `grep` |
| 2 | `Decision` và mọi đối tượng ontology là **`frozen dataclass`**, bất biến kiểm trong `__post_init__` | Chặn việc sửa lén trạng thái ngoài blackboard. *(Không dùng Pydantic — giữ số phụ thuộc ngoài ở mức tối thiểu; xem MT2.1)* |
| 3 | **Không dùng đồng hồ hệ thống trong logic nghiệp vụ** — mọi mốc thời gian lấy từ dữ liệu | Điều kiện của tính tất định |
| 4 | Mọi nguồn ngẫu nhiên nhận seed từ `config.py`, không tự khởi tạo | Như trên |
| 5 | `capabilities/` là hàm thuần, không side effect, không biết gì về agent | Bảo đảm tính công bằng của phép so sánh bằng cấu trúc |
| 6 | Agent dưới ~80 dòng; vượt ngưỡng gần như chắc chắn có logic đặt sai tầng | Giữ ranh giới tầng |
| 7 | Kế hoạch điều phối là **dữ liệu**, không phải mã điều khiển | Chặn nguy cơ tự viết máy trạng thái tệ; in được vào phụ lục luận văn |

---

## Phần 6 — Bootstrap: sáu bước đầu tiên

```bash
# 1. Khung thư mục
mkdir -p src-v3/masdss/{core,runtime,system/reliability,data,capabilities,agents/analysts,memory,baselines,goldset,chaos,evaluation,cli}
mkdir -p tests-v3 config/v3/chaos data/v3 models/v3

# 2. Sửa pyproject.toml theo §3, bổ sung requirements.txt

# 3. Cài đặt
pip install -e .

# 4. Viết trước bốn test kỷ luật — TRƯỚC khi có mã nghiệp vụ
#    tests-v3/test_layering.py, test_no_legacy_import.py,
#    test_determinism.py, test_decision_invariant.py

# 5. Xác nhận chúng ĐANG ĐỎ vì đúng lý do, không phải vì lỗi cài đặt

# 6. Bắt đầu Đợt 0 theo thứ tự bảy bước ở §4
```

Bước 4 và 5 quan trọng hơn vẻ ngoài: nếu thêm test kỷ luật sau khi đã có mã, ta luôn phát hiện vi phạm
đã tồn tại và phải sửa ngược — tốn hơn nhiều so với việc để test dẫn đường ngay từ đầu.

---

## Phần 7 — Rủi ro triển khai

| Rủi ro | Mức | Xử lý |
|---|---|---|
| Vô tình import từ `mas_dss` cũ để "dùng lại cho nhanh" | **Cao** | `test_no_legacy_import.py` chạy trong CI từ ngày đầu |
| Ghi đè `data/processed/` hoặc `config/dss_rules.yaml` | Trung bình | Mọi đường dẫn ghi đều lấy từ `config.py`, trỏ vào `data/v3/` và `models/v3/` |
| `torch` kéo về bản CUDA vài GB | Thấp | Cài từ index CPU và ghim phiên bản |
| Đợt 0 phình ra thành xây thật | Trung bình | Capability giả **chỉ trả hằng số**; cấm viết mô hình trong Đợt 0 |
| Test cũ trong `tests/` gây nhiễu CI | Thấp | `testpaths = ["tests-v3"]`; test cũ chỉ chạy khi gọi tường minh |

---

## Phần 8 — Tổng hợp tiến độ

| Đợt | Nội dung | Ngày công | Tích lũy |
|---|---|---|---|
| **Đợt 0** | Bộ khung chạy được, 4 test kỷ luật, seam tiêm lỗi đã kiểm chứng | 5 | 5 |
| **Đợt 1** | Dữ liệu, capabilities, gold set *(song song)* | 19 | 24 |
| **Đợt 2** | Baselines, agents, Contract Net | 23 | 47 |
| **Đợt 3** | Reliability, chaos, evaluation, kết quả | 32 | 79 |
| | **Tổng** | **~82 ngày công** | |

Chênh khoảng +2 ngày so với `build-plan.md` — đó là chi phí của Đợt 0, đổi lấy việc kiểm chứng ba rủi ro
lớn nhất ngay trong tuần đầu thay vì ở tuần 9 và tuần 13.

---

## Phần 9 — Nhật ký thi công: ba điều chỉnh phát sinh khi cài đặt Đợt 0

Đúng mục đích của walking skeleton — ba điểm dưới đây chỉ lộ ra khi viết mã thật, và nếu phát hiện ở
tuần 9 thì đều tốn công sửa ngược.

### 9.1 `Message` tách làm hai trường nội dung

**Vấn đề.** Tác tử cần đối tượng `OrderCase`, nhưng nội dung message phải tuần tự hóa được sang JSON để
ghi nhật ký. Nếu nhét đối tượng vào `content` thì nhật ký hỏng; nếu chỉ truyền `case_id` thì tác tử phải
tra cứu ngược, sinh ra một đường phụ thuộc mới.

**Giải pháp.** Tách hai trường với mục đích rõ ràng:

| Trường | Nội dung | Ghi vào nhật ký |
|---|---|---|
| `content` | Dữ liệu **ngữ nghĩa**, bắt buộc tuần tự hóa được | **Có** — và là thứ duy nhất `Explainer` đọc |
| `payload` | Tham chiếu đối tượng trong tiến trình | **Không bao giờ** |

Điểm quan trọng: vì `payload` **không được ghi**, nó không thể trở thành đường lách làm trace phân kỳ với
hành vi thật. DP4 được giữ nguyên. Có test canh: `test_payload_is_never_written_to_log`.

### 9.2 Bất biến "không quy kết được thì phải chuyển giao" chỉ áp dụng tại T₄

**Vấn đề.** Bất biến này áp cho mọi `Decision` sẽ buộc **mọi** quyết định ở giai đoạn 1 phải chuyển cho
người, vì tại T₃ `causes` luôn rỗng.

**Nguyên nhân.** Tại T₃ **không hề có nhiệm vụ quy kết nguyên nhân** — đó là nhiệm vụ của T₄ (§0.2 của
tài liệu RQ). `causes` rỗng ở T₃ là bình thường, không phải thất bại.

**Giải pháp.** Bất biến thu hẹp lại: `decision_point is T4 and not causes ⟹ needs_human_review`.

### 9.3 Bổ sung một bất biến chưa có trong thiết kế

Lát cắt dọc sinh ra một `Decision` mang `action = escalate_to_human` nhưng `needs_human_review = False`
— báo cáo và hành vi thực tế phân kỳ, đúng loại lỗi mà DP1 sinh ra để chặn. Bổ sung bất biến thứ ba vào
`core/decision.py`:

> `action.name == "escalate_to_human"` ⟹ `needs_human_review is True`

Ba bất biến hiện có trên `Decision`, tất cả cưỡng chế lúc khởi tạo: suy giảm ⟹ chuyển giao; chuyển giao
⟹ đánh dấu chuyển giao; ≥2 nguyên nhân ⟹ gắn cờ `multi_cause`.
