# Phản biện luận văn — góc nhìn hội đồng

Vai: giáo sư Hệ thống thông tin, hướng Design Science. Nhiệm vụ: tìm chỗ luận văn sẽ vỡ khi bị hỏi.

**Kết luận trước:** kiến trúc thì ổn. **Phần đánh giá mới là chỗ luận văn có thể trượt.** Ba lỗi ở
Tier 1 dưới đây, nếu không xử lý, sẽ làm mọi con số trong Chương 5 trở nên vô nghĩa — không phải
"chưa thuyết phục", mà là **không đo được thứ nó tuyên bố đang đo**.

Hai trong ba lỗi đó nằm trong bản plan tôi vừa đề xuất. Tôi rút lại chúng ở §1 và §2.

---

# TIER 1 — Lỗi tồn vong

## 1. Bài toán phản thực: hệ thống khuyến nghị hành động, nhưng dữ liệu không có hành động nào

**Đây là lỗi nghiêm trọng nhất và nó phá luôn ý tưởng episodic memory tôi đề xuất hôm qua.**

Bộ Olist ghi nhận: đơn hàng, giao hàng, review score. Nó **không** ghi nhận:
- Olist/seller đã can thiệp gì (expedite? xin lỗi? bồi thường?) — **không có cột `action`**
- Kết quả *nếu* đã can thiệp khác đi

Suy ra, mọi tuyên bố dạng *"hệ thống đề xuất hành động đúng"* hoặc *"hành động này cải thiện mức độ
hài lòng"* là **không thể kiểm chứng trên dữ liệu này**. Đây là bài toán inference phản thực kinh
điển (Rubin causal model): bạn chỉ quan sát được outcome dưới **một** treatment — cái treatment mà
Olist thực tế đã làm và không ai ghi lại.

**Hệ quả trực tiếp — hai thứ tôi đề xuất hôm qua đều sai:**

| Thứ tôi đề xuất | Vì sao nó sai |
|---|---|
| Episodic memory: *"3 đơn tương tự: `expedite` áp dụng 2 lần → score 4,5"* | **Bịa dữ liệu.** Olist không ghi hành động nào được áp dụng. Không có gì để truy hồi. |
| Policy Critic tính `EV = P(dissat) × ΔP(recover \| action) × value` | `ΔP(recover \| action)` **không ước lượng được** — không có biến treatment. Bạn sẽ phải bịa con số rồi trình bày như thể đo được. |
| Chỉ số "chi phí can thiệp vs giá trị cứu vãn" | Xây trên tham số bịa → con số đẹp nhưng rỗng. |

Nếu bạn nộp bài với episodic memory kiểu đó, một thành viên hội đồng sẽ hỏi *"cột nào trong Olist cho
biết hành động đã áp dụng?"* và toàn bộ đóng góp sụp trong 30 giây.

### Hướng xử lý

**Không được** giả vờ đo hiệu quả hành động. Có ba lối thoát hợp lệ, nên dùng cả ba:

**(a) Thu hẹp knowledge claim.** Đừng tuyên bố hành động *hiệu quả*. Tuyên bố hệ thống sinh ra khuyến
nghị **kịp thời, có căn cứ, giải thích được, và nhất quán với nguyên nhân** — bốn thứ này đo được.
Viết thẳng vào Chương 4 rằng hiệu quả can thiệp nằm ngoài phạm vi vì dữ liệu không có treatment. Sự
thành thật này **cộng điểm**, không trừ.

**(b) Đưa chuyên gia vào vòng đánh giá.** Đây là phương pháp DSR chính thống (Venable, Pries-Heje &
Baskerville — FEDS framework: *artificial* vs *naturalistic* evaluation). Lấy 100–150 case mà hệ
thống khuyến nghị, đưa cho 3–5 người có kinh nghiệm vận hành TMĐT chấm trên thang Likert:
*"khuyến nghị này có phù hợp với tình huống không?"*. Báo cáo **inter-rater reliability (Krippendorff's
α hoặc Fleiss' κ)**. So sánh điểm chuyên gia giữa MAS-DSS, MIS, và single-ML.

Đây là bằng chứng **không tự tham chiếu** duy nhất bạn có thể có về chất lượng hành động. Nó biến
điểm yếu chí mạng thành một đóng góp phương pháp luận.

**(c) Episodic memory viết lại — bỏ "kết quả hành động", giữ "tiền lệ tình huống".** Vẫn dùng được kNN,
nhưng nội dung truy hồi đổi:

> ~~"3 đơn tương tự: expedite 2 lần → score 4,5"~~ (bịa)
>
> **"3 đơn tương tự (cùng nhóm hàng, trễ 7–10 ngày, cùng bang): review score thực tế 1, 2, 1;
> nguyên nhân được gán: delivery (2), price (1). Đơn này thuộc nhóm rủi ro đã xác nhận."**

Tức là tiền lệ dùng để **hiệu chỉnh niềm tin về rủi ro và nguyên nhân** — thứ Olist *có* dữ liệu —
chứ không phải để chọn hành động. Vẫn có giá trị, vẫn ablation được, và không bịa gì.

**(d) Policy Critic viết lại — bỏ EV, giữ ràng buộc.** Xem §7.

---

## 2. Đánh giá vòng tròn: bạn tự sinh nhãn, tự chấm điểm mình theo nhãn đó

Nhìn kỹ chuỗi này trong code hiện tại:

```
label_causes()      ← luật từ khóa do BẠN viết, sinh nhãn giả
      ↓
RootCauseAgent.fit()← học nhãn giả đó
      ↓
đánh giá            ← so với... chính nhãn giả đó
```

Bạn không đo *độ chính xác phân loại nguyên nhân*. Bạn đo **RandomForest học thuộc hàm từ khóa của
chính bạn giỏi đến đâu**. Con số sẽ rất đẹp và hoàn toàn vô nghĩa.

Tệ hơn, `action_cause_fit` trong [metrics.py](../src/mas_dss/layer5_presentation/evaluation/metrics.py)
còn vòng tròn ở tầng hai: bảng `CAUSE_ACTION_FIT` ánh xạ nguyên nhân → hành động "đúng" cũng **do bạn
viết**, và cả tập luật DSS sinh hành động cũng **do bạn viết**. Nên `pipeline_completeness = 0.87`
chỉ nói lên: *"hai file YAML tôi viết thì nhất quán với nhau"*. Đây không phải kết quả thực nghiệm.

**Contract Net không cứu được điều này.** Bốn analyst đấu thầu, orchestrator trao thầu — nhưng "trao
đúng" vẫn được chấm theo cùng cái nhãn giả kia. Vòng tròn chỉ to hơn, không biến mất.

### Hướng xử lý

**Phải có gold set do người gán.** Không có đường tắt.

1. Lấy **mẫu phân tầng 300–400 đơn bất mãn** (phân tầng theo có/không bình luận, theo nhóm nguyên
   nhân sơ bộ, theo nhóm hàng).
2. **Hai người gán độc lập**, có codebook rõ ràng, **cho phép đa nhãn** (xem §4). Báo cáo **Cohen's
   κ**. Nếu κ < 0.6 thì chính định nghĩa nguyên nhân của bạn có vấn đề — và đó cũng là một phát hiện
   đáng viết.
3. Chia gold set: một nửa để **đo độ nhiễu của weak label** (weak label đúng bao nhiêu % so với gold?
   → báo cáo con số này, đây là một threat to validity được định lượng), một nửa làm **test set thật**
   cho Root-Cause Agent.
4. Mọi con số về phân loại nguyên nhân trong Chương 5 phải báo cáo **trên gold set**, không phải trên
   weak label.
5. `action_cause_fit` bỏ hoàn toàn, thay bằng **điểm chuyên gia** (§1b).

Bạn không nói được tiếng Bồ — xử lý: dịch máy sang tiếng Việt/Anh **rồi có người thứ hai kiểm chứng
mẫu dịch**, và ghi rõ điều này trong Threats to Validity. Hoặc thuê 1 annotator biết tiếng Bồ trên
Prolific/Upwork cho 400 mẫu (chi phí rất thấp, và nó biến điểm yếu thành điểm mạnh về rigor).

---

## 3. Baseline là bù nhìn (strawman)

Đây là đòn hội đồng sẽ đánh chắc chắn.

Trong thiết kế hiện tại:
- MAS-DSS và single-ML **dùng chung một LightGBM** → accuracy/F1 gần như bằng nhau **theo cấu tạo**.
- MAS thắng ở `pipeline_completeness` và `action_cause_fit` — nhưng **bạn định nghĩa baseline là không
  có hai thứ đó**. Baseline được cho điểm 0 vì bạn đặt luật là nó phải bằng 0.

Đó là **tautology, không phải kết quả**. Nói cách khác: *"Kiến trúc đa tác tử sinh ra hành động, còn
mô hình đơn lẻ mà tôi cố tình không cho sinh hành động thì không sinh hành động."*

Larsen et al. (2025) yêu cầu criterion validity phải so với **giải pháp hiện có tốt nhất**, không phải
với phiên bản đã bị chặt tay.

### Hướng xử lý — thêm một baseline thứ ba, mạnh thật

**Monolithic-Complete baseline**: một hệ **đơn khối** có **đầy đủ chức năng** như MAS-DSS:
- Một multi-task model (hoặc 2 model tuần tự) dự báo *đồng thời* risk + cause
- Dùng **chính tập luật DSS YAML đó** để sinh hành động
- Nhưng: không message passing, không CNP, không blackboard, không supervisor, không degradation

Bây giờ MAS-DSS phải chứng minh nó **hơn được một hệ đơn khối cũng làm đủ mọi việc**. Đây mới là thí
nghiệm thật sự trả lời câu hỏi *"kiến trúc đa tác tử có đáng không?"*.

**Và bạn phải chuẩn bị tinh thần: về accuracy/F1, MAS sẽ KHÔNG thắng.** Có thể còn thua chút vì
overhead. **Điều đó không sao — miễn là bạn tuyên bố đúng thứ mình thắng.** Xem §12.

Ma trận baseline đúng phải là:

| Hệ | Dự báo | Nguyên nhân | Hành động | Giải thích | Chịu lỗi |
|---|---|---|---|---|---|
| MIS | ✗ (ngưỡng mô tả) | ✗ | ✗ | ✗ | ✗ |
| Single-ML | ✓ | ✗ | ✗ | ✗ | ✗ |
| **Monolithic-Complete** | ✓ | ✓ | ✓ | một phần | **✗** ← chỗ MAS thắng |
| MAS-DSS | ✓ | ✓ | ✓ | ✓ | ✓ |

Nhìn bảng này là thấy ngay đóng góp thật của luận văn nằm ở **cột cuối**, không phải cột đầu.

---

# TIER 2 — Lỗi nghiêm trọng

## 4. Tiếng Bồ Đào Nha và việc tự đánh nhãn — đúng như bạn nghi ngờ, có vấn đề nặng

Bạn hỏi đúng chỗ. Sáu vấn đề, xếp theo mức nguy hiểm:

**(a) Bao nhiêu % đơn bất mãn thực sự CÓ bình luận?** Trong Olist, khoảng **40–45% review không có
`review_comment_message`**. Với những đơn đó, `label_causes()` rơi vào fallback:

```python
labels[fallback & (df["delivery_delay_days"] > 0)] = "delivery"
labels[fallback & (...) & (df["freight_ratio"] >= 0.25)] = "price"
labels[labels.isna() & fallback] = "product_quality"
```

Tức là với gần **một nửa** tập huấn luyện, "nguyên nhân" **chính là biến `delivery_delay_days` được
đổi tên**. Rồi bạn huấn luyện RandomForest trên feature (trong đó có `delivery_delay_days`) để dự đoán
nhãn đó. Nó sẽ đạt độ chính xác rất cao — vì **nó đang học lại một câu lệnh `if`**.

→ **Việc đầu tiên phải làm: tính và báo cáo con số này.** Nếu >40%, "Root Cause Agent" trên phần lớn
dữ liệu chỉ là một cái ngưỡng được khoác áo ML. Hội đồng sẽ tìm ra.

→ Cách xử: tách thành **hai tầng** rõ ràng. Đơn **có bình luận** → phân loại nguyên nhân dựa trên văn
bản (có gold set). Đơn **không có bình luận** → **thừa nhận là không xác định được nguyên nhân từ dữ
liệu**, gán `cause = unknown` và cho hệ thống escalate. Điều này *đúng về mặt tri thức luận* và còn
làm nổi bật giá trị của cơ chế `REFUSE` trong thiết kế MAS của bạn.

**(b) Danh sách từ khóa do ai làm ra?** Bạn không nói tiếng Bồ. Danh sách hiện tại được sinh ra thế
nào — từ ChatGPT? Từ đọc lướt? Đây là **construct validity threat** trực diện: công cụ đo lường không
được kiểm định. Phải: xây lexicon từ dữ liệu (log-odds ratio của từ giữa nhóm score thấp/cao), rồi có
người biết tiếng Bồ (hoặc dịch có kiểm chứng) rà lại.

**(c) Phủ định và mỉa mai.** `"produto não chegou quebrado"` (hàng KHÔNG bị vỡ) chứa từ khóa `quebrado`
→ bị gán `product_quality`. Đếm từ khóa không xử lý được phủ định. Với tiếng Bồ, phủ định
(`não`, `nem`, `sem`) rất phổ biến trong review.

**(d) Đa nhãn bị ép thành đơn nhãn.** `"produto quebrado na entrega"` (hàng vỡ trong lúc giao) — là
delivery hay quality? `scores.idxmax(axis=1)` **ép chọn một**, và với hòa điểm thì `idxmax` chọn theo
thứ tự cột — tức là **thiên vị theo alphabet**. Đây là bug thật trong code hiện tại.

→ Cách xử: cho phép **đa nhãn**. Và đây là chỗ Contract Net *thực sự* tỏa sáng: hai analyst cùng bid
cao → hệ thống báo "nguyên nhân đa yếu tố" thay vì ép chọn. **Đó mới là lập luận thuyết phục cho CNP**
— mạnh hơn nhiều so với "4 agent thi nhau cho vui".

**(e) Chính tả và biến thể.** `nao`, `não`, `naum`, `n`, `ñ`... Danh sách từ khóa cứng sẽ trượt phần
lớn. TF-IDF trên n-gram ký tự (`char_wb`, 3–5 gram) chịu lỗi chính tả tốt hơn nhiều — **dùng cái này
thay cho keyword matching**.

**(f) Giải pháp tốt hơn cả: BERTimbau.** Có mô hình BERT pretrained cho tiếng Bồ Đào Nha
(`neuralmind/bert-base-portuguese-cased`). Dùng nó làm **encoder** (lấy embedding), rồi gắn một
classifier head nhỏ huấn luyện trên **gold set**. Ưu điểm rất lớn cho luận văn:
- **Deterministic** (không sinh văn bản, không sampling) → giữ được tính tái lập
- Hiểu ngữ nghĩa, phủ định, biến thể chính tả — thứ keyword không làm được
- **Là "AI" mà không phải "LLM agent"** → không phá lập luận ở §8 của plan
- Rất dễ bảo vệ: pretrained model công khai, có bài báo, có benchmark

→ **Đề xuất mạnh: thay toàn bộ keyword lexicon bằng BERTimbau + classifier head.** Đây là nâng cấp
lớn nhất về mặt phương pháp mà bạn có thể làm với chi phí thấp.

---

## 5. Thời điểm ra quyết định: hệ thống dự báo quá muộn để "can thiệp sớm"

Chương 1 hứa: *"nhận diện **sớm** các đơn có nguy cơ không hài lòng cần can thiệp"*.

Nhưng đặc trưng mạnh nhất của model là `delivery_delay_days`, `delivery_days` — những thứ **chỉ biết
được SAU KHI hàng đã giao**. Bạn không thể "expedite shipment" cho một đơn **đã giao xong**. Khuyến
nghị `expedite_shipment_and_notify_customer` trong luật R01 là **bất khả thi về mặt thời gian**.

Tệ hơn: `review_lag_days` (từ lúc giao đến lúc viết review) đang nằm trong `OrderFeatures` — đây là
**rò rỉ trắng trợn**: nó chỉ tồn tại sau khi review đã được viết, mà review score chính là nhãn.

### Hướng xử lý — và đây lại là chỗ biến điểm yếu thành điểm mạnh

Định nghĩa **decision point** tường minh, rồi chọn framing:

| Decision point | Feature có sẵn | Hành động khả thi | Đánh giá |
|---|---|---|---|
| T₁ = lúc đặt hàng | Chỉ static (giá, seller, category, khoảng cách) | Chọn 3PL tốt hơn, cảnh báo seller | AUC sẽ thấp, nhưng **thực sự phòng ngừa** |
| T₂ = lúc bàn giao cho vận chuyển | + `carrier_handover_days`, ETA | Expedite, đổi tuyến | Khả thi |
| **T₃ = ngay sau khi giao hàng** | Toàn bộ feature giao hàng | **Service recovery**: chủ động xin lỗi, bồi thường, mở ticket — **TRƯỚC KHI khách viết review** | ✓ |

**T₃ chính là framing đúng, và nó rất mạnh:** trong Olist, khoảng cách trung vị từ lúc giao đến lúc
viết review là **vài ngày**. Đó là một **cửa sổ can thiệp có thật**. Hệ thống dự báo tại thời điểm
giao hàng, và can thiệp trong cửa sổ đó để cứu vãn trải nghiệm **trước khi** khách để lại 1 sao.

Đây là bài toán **service recovery** — có cả một dòng văn liệu marketing/OM về nó (recovery paradox),
và nó *hợp lý về mặt nghiệp vụ*. Bạn chỉ cần **nói ra** thay vì để hội đồng phát hiện mâu thuẫn.

**Việc phải làm ngay:**
1. **Xóa `review_lag_days` khỏi feature set.** Đây là leakage.
2. Đổi ngôn ngữ Chương 1 từ "can thiệp sớm/phòng ngừa" sang **"phát hiện rủi ro tại điểm giao hàng và
   phục hồi dịch vụ trong cửa sổ trước review"**.
3. Sửa lại tập luật: bỏ `expedite_shipment` (bất khả thi ở T₃), thay bằng các hành động service
   recovery khả thi.
4. **Bonus rất đáng làm:** chạy thêm kịch bản T₂ (dự báo tại lúc bàn giao vận chuyển) như một
   *context validity* experiment — "kiến trúc hoạt động thế nào khi thông tin ít hơn?". Đây là câu trả
   lời trực tiếp cho **RQ4**, câu hỏi mà hiện tại bạn chưa có cách trả lời.

---

## 6. Contract Net đang bị dùng sai — người biết Smith (1980) sẽ hỏi ngay

CNP nguyên bản là giao thức **phân bổ nhiệm vụ khi có cạnh tranh tài nguyên**: contractor phát CFP,
các agent bid **chi phí/năng lực thực hiện**, contractor chọn để tối ưu phân bổ.

Thiết kế của bạn: 4 analyst **cùng làm một việc**, bid **độ tin cậy của mình**, orchestrator lấy
argmax. Đây là **ensemble classifier có gắn nhãn giao thức** (softmax → argmax), không phải task
allocation. Một thành viên hội đồng đọc Smith sẽ nói đúng câu đó.

### Hai hướng xử lý

**(a) Thành thật:** gọi nó là *"phiên đấu giá độ tin cậy lấy cảm hứng từ CNP"* và biện minh bằng thứ
ensemble **không** có: bid mang theo **bằng chứng** (giải thích được), agent có quyền **REFUSE**
(nhận biết ngoài năng lực), và analyst chết thì phiên đấu vẫn diễn ra (**chịu lỗi**). Ổn, nhưng hơi
yếu.

**(b) Làm cho CNP trở thành CNP thật — tôi khuyến nghị cách này.** Đưa vào **ngân sách tính toán/độ
trễ cho mỗi case**. Các analyst có chi phí khác nhau:

| Analyst | Chi phí | Ghi chú |
|---|---|---|
| Price Analyst | rẻ (vài µs) | Chỉ tính z-score |
| Delivery Analyst | rẻ | GBM trên feature |
| Quality Analyst | **đắt** | Phải chạy BERTimbau trên review text |
| Service Analyst | **đắt** | Phải chạy BERTimbau |

Bây giờ analyst bid `(expected_confidence, cost)`, và Orchestrator **phân bổ dưới ràng buộc ngân
sách** — đúng nghĩa CNP. Với case rủi ro thấp → chỉ mời analyst rẻ. Case rủi ro cao → chi ngân sách
cho analyst đắt.

Giao thức trở nên **load-bearing** (nếu bỏ nó đi thì hệ thống thực sự mất thứ gì đó), và bạn có thêm
một chỉ số mới: **chất lượng phân loại đạt được trên mỗi đơn vị chi phí tính toán**. Đây là lập luận
vững chắc cho RQ2.

---

## 7. Policy Critic: LLM local hay không? — Trả lời câu hỏi của bạn

Câu hỏi này hay, và câu trả lời của tôi có ba tầng.

### Tầng 1 — EV engine tôi đề xuất hôm qua đã chết rồi (xem §1)

`ΔP(recover | action)` không ước lượng được từ Olist. Nên **bỏ phần EV**. Critic viết lại thành
**engine ràng buộc thuần túy** — vẫn có giá trị, vẫn deterministic, và **không bịa tham số nào**:

| Ràng buộc | Tính được từ Olist? |
|---|---|
| Chi phí hành động vượt giá trị đơn | ✓ (có `price`, `payment_value`) |
| Ngân sách can thiệp (chỉ can thiệp top-k% rủi ro cao nhất) | ✓ (chính sách, không cần dữ liệu) |
| Cooldown seller (đã audit gần đây) | ✓ (tính được từ lịch sử case của chính hệ thống) |
| Công bằng: tỷ lệ can thiệp lệch theo bang/nhóm hàng | ✓ |
| Bằng chứng yếu: `cause_probability < ngưỡng` | ✓ |
| Mâu thuẫn: Prediction nói risk cao, Analytics không thấy bất thường | ✓ |

Đây vẫn là một agent **phản biện thật**, có `CHALLENGE` thật, có ablation thật ("tắt Critic → tỷ lệ
can thiệp thừa tăng bao nhiêu?"). Chỉ là nó không giả vờ biết thứ nó không biết.

### Tầng 2 — Nếu thêm LLM local, nó là NGHĨA VỤ hay TÀI SẢN?

**Lập luận PHẢN ĐỐI (mạnh):**

1. **Phá tính tái lập.** DSR yêu cầu artifact phải đánh giá lại được. LLM sinh văn bản có tính ngẫu
   nhiên. *(Phản biện lại: `temperature=0` + seed cố định + greedy decoding lấy lại được phần lớn tính
   xác định. Nhưng vẫn phụ thuộc phiên bản model, phiên bản runtime.)*
2. **Làm nhiễu loạn ablation — đây mới là đòn chí mạng.** Nếu MAS-DSS có LLM Critic và nó thắng
   baseline, bạn **không tách được** phần thắng nào do *kiến trúc đa tác tử* và phần nào do *năng lực
   suy luận của LLM*. Toàn bộ causal claim (§3.2.5b của bạn) bị confound. Đây là lý do nặng nhất.
3. **Thêm một component chưa được đánh giá vào chuỗi quyết định.** Một LLM local 7B lập luận nghiệp vụ
   TMĐT trên context tiếng Bồ — độ tin cậy của nó là bao nhiêu? Bạn không biết, và bạn cũng không có
   thời gian đánh giá nó riêng.
4. Không so sánh công bằng với baseline (baseline không có LLM).

**Lập luận ỦNG HỘ:**
- Khớp với literature review (Chương 2 đang trích LLM-MAS)
- Việc của Critic — cân nhắc các ràng buộc kinh doanh xung đột — *đúng là* bài toán suy luận
- Là điểm mới về mặt kỹ thuật

### Tầng 3 — Phán quyết của tôi

> **Nếu dùng LLM, nó phải là ĐỐI TƯỢNG ĐƯỢC ĐÁNH GIÁ, không phải NGUYÊN LIỆU ẨN.**

Cụ thể: **giữ MAS-DSS deterministic làm artifact chính**, và nếu còn thời gian, thêm **một nhánh thực
nghiệm**:

```
Điều kiện A: MAS-DSS + Critic ràng buộc (deterministic)     ← artifact chính
Điều kiện B: MAS-DSS + Critic LLM local (Qwen/Llama, T=0)   ← nhánh thí nghiệm
```

Rồi **đo** xem B có tốt hơn A không — theo điểm chuyên gia (§1b), theo tỷ lệ can thiệp thừa, theo độ
trễ. Lúc này LLM biến từ *nghĩa vụ phải bào chữa* thành **một câu hỏi nghiên cứu có câu trả lời**:
*"Liệu phản biện dựa trên LLM có cải thiện chất lượng chuỗi quyết định so với phản biện dựa trên ràng
buộc?"* — và câu trả lời "không" cũng là một phát hiện có giá trị đăng được.

Nó cũng **giải quyết luôn độ lệch với literature review** ở §8 của plan cũ: bạn không né LLM, bạn **thí
nghiệm với nó**.

**Nếu thời gian eo hẹp: bỏ LLM. Đừng nửa vời.** Một LLM cắm vào mà không đánh giá còn tệ hơn không có.

---

## 8. "Silent failure rate = 0%" không phải kết quả thực nghiệm, đó là tautology

Bạn thiết kế hệ thống để không thể hỏng âm thầm, rồi đo được rằng nó không hỏng âm thầm. Đó là
**kiểm tra đặc tả**, không phải phát hiện khoa học. Tôi sẽ hỏi: *"Anh đã phát hiện được điều gì mà anh
chưa biết trước khi chạy thí nghiệm?"*

### Hướng xử lý — đo cái đắt giá thật sự

Cái *thú vị* không phải là "guard có bắt được lỗi tôi cố tình thiết kế để nó bắt không", mà là:

1. **Độ nhạy / độ đặc hiệu của guard trên lỗi bạn KHÔNG thiết kế riêng cho nó.** Tiêm nhiễu loạn tinh
   vi: drift dần dần (dịch phân phối feature 5%, 10%, 20%), model bị hoán vị nhãn một phần, analyst
   trả về bid lệch hệ thống. **Guard bắt được ở mức nhiễu loạn nào? Sau bao nhiêu case? Tỷ lệ báo động
   giả là bao nhiêu?** → đây là đường cong ROC của hệ giám sát. **Đây mới là kết quả.**
2. **Cái giá của bảo đảm đó:** overhead latency, số dòng code, độ phức tạp — so với Monolithic-Complete.
   Bảo đảm không miễn phí; đo cái giá.
3. **Silent failure của các baseline** thì lại là kết quả thật (vì bạn không thiết kế chúng để hỏng):
   Monolithic-Complete khi model chết → hỏng âm thầm bao nhiêu %? Con số đó **có ý nghĩa**, vì bạn
   không dàn dựng nó.

---

# TIER 3 — Vệ sinh phương pháp (nhỏ nhưng hội đồng sẽ nhặt)

| # | Vấn đề | Xử lý |
|---|---|---|
| 9 | **Ngưỡng `review_score <= 3` = bất mãn.** 3 sao là trung tính. Điều này thổi phồng lớp dương và mọi chỉ số | Phân tích độ nhạy ở ngưỡng ≤2 và ≤3. Báo cáo cả hai. Biện minh bằng phân bố bình luận theo score |
| 10 | **ROC-AUC gây hiểu lầm khi mất cân bằng lớp** (bất mãn ~12-15%) | Báo cáo **PR-AUC** là chính. ROC-AUC là phụ |
| 11 | `class_weight="balanced"` thổi recall, dìm precision | Báo cáo precision-recall curve, và chọn ngưỡng theo chi phí, không dùng 0.5 |
| 12 | **kNN episodic memory có thể rò rỉ test set** | Index chỉ được xây trên train. Ghi rõ |
| 13 | **Latency/throughput đo trên batch parquet in-process** → không nói lên gì về "thời gian thực" | Bỏ từ "real-time" khỏi luận văn, hoặc dựng test streaming thật. Đừng tuyên bố thứ không đo |
| 14 | **Context validity**: một dataset, một thị trường (Brazil), 2016–2018, một nền tảng | Nói thẳng giới hạn. Đừng khái quát hóa |
| 15 | `idxmax` với điểm hòa → **thiên vị theo alphabet** khi gán nhãn | Bug thật. Xử lý hòa tường minh (→ đa nhãn) |
| 16 | Gộp đơn nhiều item về **item đắt nhất** | Đã ghi trong docs, tốt. Nhưng cần báo cáo % đơn nhiều seller bị ảnh hưởng |

---

# Phần II — Đóng góp thật sự nằm ở đâu

## 17. Novelty claim đang mơ hồ — phải đóng đinh nó lại

Theo khung Gregor & Hevner (2013): Contract Net (1980), Blackboard (1985), OTP supervision (1990s),
FIPA-ACL (2002) — **không có gì mới**. Bài toán (DSS cho hài lòng khách hàng TMĐT) cũng không mới.
Vậy đây là **Improvement** (giải pháp mới cho vấn đề đã biết) — hợp lệ cho luận văn thạc sĩ, nhưng
**tuyên bố novelty phải khiêm tốn và CHÍNH XÁC**.

Đóng góp thật của bạn, nói cho đúng, là:

> **Tích hợp giám sát chịu lỗi và suy giảm minh bạch vào một pipeline hỗ trợ quyết định, cùng với một
> phương pháp đánh giá (chaos harness) để định lượng khả năng chịu lỗi của DSS — một khía cạnh mà văn
> liệu MAS-DSS hiện tại bỏ trống.**

Hẹp, thành thật, và **bảo vệ được**. Đừng tuyên bố rộng hơn thế.

## 18. Nâng lên tầm Design Principles — đây là thứ biến luận văn từ "tôi xây một cái" thành DSR thật

Hội đồng DSR sẽ hỏi: *"Tri thức trừu tượng nào rút ra được từ artifact này?"* Trả lời bằng **các
nguyên lý thiết kế** (Gregor, Chandra Kuk & Hevner 2020 — anatomy of a design principle). Ví dụ:

**DP1 — Suy giảm minh bạch (Transparent Degradation).**
*Để* một DSS duy trì được lòng tin của nhà quản lý trong điều kiện thành phần lỗi, *hãy* gắn mức suy
giảm vào từng quyết định và bắt buộc con người xem lại khi mức > 0, *bởi vì* một quyết định tự động
sinh ra trên nền năng lực đã suy giảm gây hại nhiều hơn là không có quyết định.

**DP2 — Quy kết nguyên nhân bằng cạnh tranh (Competitive Attribution).**
*Để* nhận diện tình huống đa nguyên nhân, *hãy* để nhiều tác tử chuyên biệt đấu thầu kèm bằng chứng
thay vì dùng một bộ phân loại đa lớp, *bởi vì* độ đồng thuận giữa các bid mang thông tin mà argmax làm
mất đi.

**DP3 — Từ chối thay vì đoán (Refusal over Guessing).**
*Để* tránh quyết định tự tin nhưng sai trên dữ liệu ngoài phân phối, *hãy* cấp cho tác tử quyền
`REFUSE`, *bởi vì* chuyển giao cho con người có chi phí thấp hơn nhiều so với một hành động sai.

**DP4 — Nguồn gốc quyết định là sản phẩm phụ của giao tiếp (Provenance from Communication).**
*Để* decision trace luôn trung thực, *hãy* dựng nó **từ nhật ký message thật** thay vì viết tay,
*bởi vì* trace viết tay có thể phân kỳ với hành vi thực tế của hệ thống.

Bốn DP này **trừu tượng, có thể chuyển giao sang bài toán khác** (CRM, chuỗi cung ứng — đúng RQ4), và
chúng chính là **đóng góp lý thuyết** của luận văn. Artifact chỉ là hiện thân của chúng.

---

# Phần III — Bản đồ điều chỉnh

## 19. Việc phải làm, xếp theo mức khẩn

| Ưu tiên | Việc | Vì sao |
|---|---|---|
| **P0** | Tính % đơn bất mãn **không có bình luận**. Nếu >40% → tách hai tầng, đơn không bình luận gán `unknown` | Nếu không làm, "Root Cause Agent" là ngưỡng đội lốt ML |
| **P0** | **Xóa `review_lag_days`** khỏi feature set | Rò rỉ nhãn |
| **P0** | Định nghĩa **decision point = T₃ (sau giao hàng)**, đổi framing sang **service recovery**, sửa tập luật bỏ `expedite` | Hệ thống hiện đang khuyến nghị điều bất khả thi |
| **P0** | **Gold set 300–400 đơn, 2 annotator, Cohen's κ, đa nhãn** | Không có nó, mọi số về nguyên nhân đều vòng tròn |
| **P0** | Bỏ episodic memory "kết quả hành động"; bỏ EV engine | Bịa dữ liệu |
| **P1** | Thêm baseline **Monolithic-Complete** | Baseline hiện tại là bù nhìn |
| **P1** | Thay keyword lexicon bằng **BERTimbau + classifier head** | Deterministic, mạnh hơn nhiều, dễ bảo vệ |
| **P1** | **Đánh giá bởi chuyên gia** (3–5 người, 100–150 case, Likert, Krippendorff's α) | Bằng chứng KHÔNG tự tham chiếu duy nhất về chất lượng hành động |
| **P1** | Đưa **ngân sách tính toán** vào CNP để nó là CNP thật | Chống lại đòn "đây chỉ là ensemble" |
| **P2** | Chaos harness đo **độ nhạy/đặc hiệu của guard**, không chỉ "silent failure = 0" | Biến tautology thành kết quả |
| **P2** | Phân tích độ nhạy ngưỡng (≤2 vs ≤3); dùng **PR-AUC** | Vệ sinh thống kê |
| **P2** | Viết **4 Design Principles** vào Chương 3 | Nâng từ "xây một cái" lên DSR thật |
| **P3** | Nhánh thí nghiệm **LLM Critic** (nếu còn thời gian) | Biến LLM từ nghĩa vụ thành câu hỏi nghiên cứu |
| **P3** | Kịch bản T₂ (dự báo lúc bàn giao vận chuyển) | Trả lời RQ4 (context validity) |

## 20. Tuyên bố mà luận văn NÊN đưa ra

**Đừng tuyên bố:**
- ~~"MAS-DSS dự báo chính xác hơn mô hình đơn lẻ"~~ (sẽ không đúng — dùng chung model)
- ~~"Hành động khuyến nghị cải thiện mức độ hài lòng"~~ (không kiểm chứng được trên Olist)
- ~~"Hệ thống phòng ngừa bất mãn từ sớm"~~ (feature chỉ có sau khi giao hàng)
- ~~"Silent failure = 0% chứng minh tính vượt trội"~~ (tautology)

**Nên tuyên bố:**
- "Với **cùng năng lực dự báo**, kiến trúc đa tác tử tạo ra một **chuỗi quyết định giải thích được và
  chịu lỗi** mà kiến trúc đơn khối không có — và cái giá phải trả là *x* ms overhead trên mỗi case."
- "Hệ thống phát hiện đơn có nguy cơ **tại điểm giao hàng** và đề xuất hành động **phục hồi dịch vụ**
  trong cửa sổ trước khi khách viết đánh giá; khuyến nghị được **chuyên gia đánh giá** phù hợp hơn
  đáng kể so với báo cáo kiểu MIS (điểm Likert *a* vs *b*, α = *c*)."
- "Khi một tác tử lỗi, kiến trúc đơn khối hỏng **âm thầm** trên *p*% case, trong khi kiến trúc đề xuất
  suy giảm **minh bạch** và chuyển giao cho con người."
- "Bộ giám sát phát hiện drift phân phối ở mức *d*% sau *n* case, với tỷ lệ báo động giả *f*%."
- Bốn Design Principles có thể chuyển giao sang CRM / chuỗi cung ứng.

Những tuyên bố này **hẹp hơn**, nhưng **đúng** — và mỗi cái đều có bằng chứng không vòng tròn đứng sau.
Đó là khác biệt giữa một luận văn được thông qua và một luận văn bị bắt làm lại phần đánh giá.
