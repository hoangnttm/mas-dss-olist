# Codebook gán nhãn nguyên nhân bất mãn — **bản 3 (gán trên bản dịch tiếng Anh)**

> **Vì sao có bản 3.** Phân tích 102 dòng bất đồng của vòng một cho một kết luận
> khác hẳn giả định ban đầu: vấn đề **không phải** ở định nghĩa nguyên nhân, mà ở
> **rào cản ngôn ngữ**.
>
> | Bản chất bất đồng | Số dòng | |
> |---|---|---|
> | Một bên nói *"không quy kết được"*, bên kia tìm ra nguyên nhân | **76 (75,2%)** | **bỏ sót bằng chứng** |
> | Cùng hướng, khác số lượng nhãn | 18 (17,8%) | ngưỡng |
> | Hai bên quy kết khác hẳn nhau | 7 (6,9%) | định nghĩa |
>
> Và nghiêm trọng hơn: **23,7% số dòng tầng A được cả hai người cùng gán `unknown`**,
> trong khi khoảng 6/10 dòng trong số đó có nguyên nhân nêu tường minh. Hai người
> cùng bỏ sót thì κ vẫn cao — **κ đo độ tin cậy, không đo độ đúng**.
>
> Bản 3 vì vậy đổi **phương tiện đọc**, không chỉ đổi định nghĩa: gán nhãn trên **bản
> dịch tiếng Anh**, giữ tiếng Bồ bên cạnh để đối chiếu.
>
> **Phạm vi:** chỉ **250 dòng tầng A**. Tầng B (150 dòng, không có văn bản) giữ nguyên
> nhãn vòng một vì không phụ thuộc ngôn ngữ.
>
> ⚠️ **Lý do "đã đạt đồng thuận tuyệt đối 0/150" đã bị bác bỏ — xem L25.** Đồng thuận
> tuyệt đối ở tầng B che giấu việc **43/150 dòng (28,7%) thỏa Quy tắc 6 mà không dòng
> nào được gán `delivery`**. Đây đúng là lỗi L22 lặp lại. Nhưng thủ phạm là **chính Quy
> tắc 6**: nó suy nhãn vàng từ đặc trưng mà hệ thống cũng nhìn thấy, tức tạo ra vòng
> tròn. **Quy tắc 6 đang chờ quyết định bỏ hay giữ** — chưa áp dụng cho tới lúc đó.

---

## 1. Nhiệm vụ

Với mỗi đơn hàng bị đánh giá 1–2 sao, xác định **nguyên nhân nào đã dẫn đến sự bất
mãn**, dựa trên bằng chứng có trong dòng dữ liệu.

**Đây là gán nhãn ĐA NHÃN.** Đặt `1` cho **mọi** nguyên nhân phù hợp. Không ép chọn một.

### 1.1 Đọc cột nào

| Cột | Vai trò |
|---|---|
| `review_content_en` | **Căn cứ chính** — bản dịch tiếng Anh |
| `review_content` | **Đối chiếu** — bản gốc tiếng Bồ |
| `delivery_delay_days`, `freight_ratio`, … | Bằng chứng cấu trúc |

> **Vì sao vẫn giữ tiếng Bồ.** Nhãn phải neo vào **văn bản gốc**, không vào bản dịch.
> Bản dịch là công cụ đọc, không phải sự thật. Nếu chỉ nhìn tiếng Anh, một câu dịch
> sai sẽ tạo ra nhãn sai mà không ai biết — và nhãn đó lại được dùng để chấm điểm một
> mô hình **đọc tiếng Bồ**.
>
> Không cần biết tiếng Bồ để dùng cột này. Chỉ cần **đối chiếu độ dài**: nếu bản dịch
> ngắn hơn hẳn bản gốc, nhiều khả năng một mệnh đề đã bị bỏ rơi — hãy dịch lại riêng
> câu đó bằng công cụ khác.

### 1.2 Quy tắc bao trùm — đọc trước tiên

> **QUÉT HẾT CÂU TRƯỚC KHI KẾT LUẬN `unknown`.**
>
> Lỗi phổ biến nhất của vòng một là dừng lại quá sớm. Một đánh giá dài thường nêu
> **nhiều hơn một** vấn đề, và mệnh đề quan trọng có thể nằm ở cuối:
>
> *"I really like shopping at this store, **but I still haven't received the product**"*
> → `delivery`, dù nửa đầu câu là lời khen.
>
> Chỉ đặt `unknown` sau khi đã đọc hết và **không** tìm thấy mệnh đề nào nêu vấn đề.

---

## 2. Bốn nguyên nhân

### `cause_delivery` — Giao hàng

Hàng **không đến đúng, đủ, hoặc đúng hẹn**.

Bao gồm: trễ hẹn · chưa nhận được · thất lạc · giao sai địa chỉ · **giao thiếu số
lượng** · hư hỏng **do vận chuyển**.

| Cụm tiếng Anh thường gặp | Bản gốc tiếng Bồ |
|---|---|
| `didn't arrive`, `did not arrive`, `never arrived` | `não chegou` |
| `haven't received`, `still haven't received` | `não recebi`, `ainda não recebi` |
| `delay`, `delayed`, `took too long`, `long wait` | `atraso`, `demora` |
| `past the deadline`, `beyond the delivery date` | `fora do prazo` |
| `lost`, `went missing` | `extraviado` |
| `only one arrived`, `only received 2`, `product missing` | `só chegou um`, `faltou produto` |
| `delivered to another person` | `entregue para outra pessoa` |

Bằng chứng cấu trúc: `delivery_delay_days` **dương**.

### `cause_quality` — Chất lượng sản phẩm

Hàng **đã đến rồi**, nhưng nó sai hoặc tệ.

Bao gồm: vỡ · lỗi · không hoạt động · **sai chủng loại hoặc sai thuộc tính** · khác
mô tả · hàng giả · thiếu **bộ phận** của một sản phẩm.

| Cụm tiếng Anh thường gặp | Bản gốc tiếng Bồ |
|---|---|
| `broken`, `damaged`, `arrived broken` | `quebrado`, `danificado` |
| `defect`, `doesn't work`, `not working` | `defeito`, `não funciona` |
| `wrong product`, `they sent the wrong`, `sent me another` | `veio errado`, `enviaram outro` |
| `wrong color`, `wrong voltage`, `wrong model` | `cor errada`, `voltagem errada` |
| `different from`, `not as described`, `not as pictured` | `diferente`, `conforme a ilustração` |
| `fake`, `counterfeit` | `falso` |
| `missing parts`, `parts were missing` | `faltou peças` |
| `doesn't fit`, `didn't fit` | `não encaixou` |

### `cause_service` — Chăm sóc khách hàng

**Một lượt tương tác đã xảy ra và đã thất bại.**

> **Điều kiện cần.** Chỉ gán `service` khi văn bản có bằng chứng tường minh rằng:
> **(a)** khách hàng **đã liên hệ** (gọi, email, mở ticket, nhắn tin), **hoặc** người
> bán đã liên hệ; **và (b)** lượt tương tác đó **thất bại** — không ai trả lời, không
> giải quyết, hoặc bị từ chối.
>
> **Không đủ:** chỉ nêu *mong muốn* đổi/trả/hoàn tiền mà không nói đã liên hệ và bị
> từ chối · suy diễn "dịch vụ kém" từ việc vấn đề chưa được giải quyết.

| Cụm tiếng Anh thường gặp | Bản gốc tiếng Bồ |
|---|---|
| `no response`, `no one replied`, `nobody got back to me` | `sem resposta`, `ninguém me deu retorno` |
| `can't get in touch`, `tried to contact and couldn't` | `não consigo contato` |
| `opened a ticket`, `sent an email` + không hồi đáp | `abri chamado`, `mandei e-mail` |
| `didn't resolve`, `no solution` | `não resolveram`, `nenhuma solução` |
| `no customer support channel` | `não tem canal de apoio` |
| `poor service`, `terrible service`, `they don't care` | `péssimo atendimento`, `descaso` |

**`service` hầu như luôn là nguyên nhân CỘNG THÊM**, đi kèm `delivery` hoặc `quality`.

### ~~`cause_price`~~ — **ĐÃ GỠ khỏi hệ phân loại (12/08)**

**Không còn nhãn `price`.** Lý do không phải cỡ mẫu nhỏ mà là **hệ phân loại đặt sai**:

> Khách hàng đã **xác nhận mua**, tức đã đồng ý với giá niêm yết và phí vận chuyển
> hiển thị lúc thanh toán. Một lời than **sau khi mua** vì vậy không thể là về *giá*.
> Nó luôn là về một **cơ chế khác đã hỏng**.

Đọc cả 12 dòng từng được gán `price` trong vòng trước xác nhận điều đó — **10/12 than
về phí vận chuyển**, và hai trong số đó nói rõ hàng vẫn tốt:

> *"**Quality merchandise**, I just think the freight should be more affordable."*
> *"I **received the product right**, but I want a refund of the shipping."*

Gộp những dòng này vào `quality` sẽ dán nhãn sai — khách đang nói ngược lại.

---

### Quy tắc 7 — Định tuyến lời than về tiền *(thay cho `price`)*

Hỏi: **cơ chế nào đã hỏng?** — không hỏi *"có nhắc tới tiền không?"*

| Nội dung than phiền | Gán về | Vì sao |
|---|---|---|
| Phí vận chuyển cao · trả phí mà phải tự ra lấy hàng · **đòi hoàn phí chung chung** *(chưa rõ đã liên hệ hay chưa)* | **`delivery`** | Trả tiền cho một **dịch vụ giao tận nhà không được cung cấp** |
| *"không đáng tiền"* · *"chất lượng không tương xứng số tiền"* · hàng kém so với giá | **`quality`** | Đúng là **phán xét giá trị** — chất lượng không xứng số tiền bỏ ra |
| **Đòi hoàn phí nhưng không được phản hồi / không được giải quyết** | **`service`** | Vấn đề nằm ở **xử lý sau bán**, không ở phí |

**Điểm phân biệt giữa hàng 1 và hàng 3 là *phản hồi*.** *"Tôi muốn hoàn phí ship"* →
`delivery`. *"Tôi đã yêu cầu hoàn phí ba lần mà không ai trả lời"* → `service`.

**Ví dụ đã định tuyến, lấy từ dữ liệu thật:**

| Câu *(bản dịch)* | Gán về |
|---|---|
| *"I want the freight refund please"* | `delivery` |
| *"shipping cost (14.00) was almost equal to its price (15.00)"* | `delivery` |
| *"I paid an expensive freight and then had to carry weight from the mail home"* | `delivery` |
| *"**Terrible for the value** I thought the cloth would be better"* | `quality` |
| *"poor quality fabric… the blue color was **more expensive and has no quality**"* | `quality` |
| *"I opened a ticket asking for the freight refund and **got no response**"* | `service` |

> **Một câu có thể mang nhiều nhãn.** *"Tôi trả phí ship mà phải tự ra bưu điện lấy,
> đã khiếu nại mà không ai trả lời"* → `delivery` **và** `service`.

---

### `cause_unknown` — Không quy kết được

Bằng chứng **không đủ** để quy về bất kỳ nguyên nhân nào ở trên.

Ba trường hợp hợp lệ:
- Cảm thán không nêu đối tượng: `terrible`, `I didn't like it`
- Văn bản **khen** dù đánh giá 1–2 sao: `I always shop here and I like it`
- Đơn tầng B không có văn bản và mức trễ dưới ngưỡng

Khi đặt `cause_unknown = 1`, **để trống cả bốn nguyên nhân còn lại**.

---

## 3. Sáu quy tắc quyết định

### Quy tắc 1 — SỐ LƯỢNG thuộc `delivery`, CHỦNG LOẠI thuộc `quality`

| Tình huống | Nhãn |
|---|---|
| `bought 3, only received 2` · `product missing` | **`delivery`** |
| `ordered red, received pink` · `ordered Master, got Standard` | **`quality`** |
| Bộ 4 món, chỉ nhận 1 món | **`delivery`** |
| Một sản phẩm đến nhưng **thiếu ốc vít / phụ kiện** bên trong | **`quality`** |
| `not as pictured` · `fake` | **`quality`** |

**Câu hỏi tự kiểm:** *Món hàng khách cầm trên tay có đúng thứ họ đặt không?*
Không đúng thứ → `quality`. Đúng thứ nhưng **thiếu món** → `delivery`.

### Quy tắc 2 — `service` cần một lượt tương tác ĐÃ THẤT BẠI

1. Văn bản có nhắc tới **một lượt liên hệ đã xảy ra** không? Không → **không gán**.
2. Lượt đó có **thất bại** không? Không → **không gán**.
3. Cả hai đều có → **gán `service`**, đồng thời giữ nguyên nhân gốc.

### Quy tắc 3 — Ngưỡng "đủ cụ thể" giữa `quality` và `unknown`

| Văn bản | Nhãn |
|---|---|
| `terrible` · `awful` · `I didn't like it` | **`unknown`** |
| `the cartridge is garbage` · `the product is bad` | **`quality`** |
| `no punctuality` | **`delivery`** |
| `I don't like this store` | **`unknown`** |

**Câu hỏi tự kiểm:** *Câu này có nêu được ĐỐI TƯỢNG của lời chê không — món hàng,
việc giao, hay việc hỗ trợ?*

### Quy tắc 4 — Lời khen kèm theo KHÔNG hủy bỏ nguyên nhân

`Good price, but the delivery took very long` → **`delivery`**.

Chỉ cần **một mệnh đề tường minh** về một vấn đề là đủ. Ngược lại, khía cạnh được
**khen** thì không gán: `it was late but the seller resolved it quickly` → gán
`delivery`, **không** gán `service`.

### Quy tắc 5 — Đối chiếu bản gốc ở ba tình huống

Bản dịch máy yếu nhất đúng ở chỗ dữ liệu này khó: câu ngắn, sai chính tả, viết tắt
(`n` thay `não`, `vcs`, `pq`). Hãy liếc cột tiếng Bồ khi:

| Tình huống | Vì sao |
|---|---|
| Bản dịch **ngắn hơn hẳn** bản gốc | Có thể một mệnh đề đã bị bỏ rơi |
| Bản dịch **vô nghĩa** hoặc lủng củng | Bản gốc có thể viết tắt nặng |
| Bạn định gán `unknown` cho một câu **dài** | Câu dài mà không quy kết được là hiếm — kiểm tra lại |

Ghi vào cột `notes` khi bạn nghi bản dịch có vấn đề. Những dòng đó sẽ được đưa cho
người biết tiếng Bồ đối chiếu.

### Quy tắc 6 — Trễ hẹn ở đơn không có bình luận

Chỉ áp dụng cho tầng B *(vòng 3 không gán lại tầng B — quy tắc này giữ để tham chiếu)*:
gán `delivery` **chỉ khi** `delivery_delay_days > 3`.

---

## 4. Mười lăm ví dụ biên

Mười ví dụ đầu lấy từ chính các dòng vòng một đã sai — **sáu dòng đầu là những dòng
CẢ HAI người cùng bỏ sót**, minh họa đúng lỗi mà bản 3 sinh ra để sửa.

| # | Bằng chứng *(bản dịch)* | Nhãn đúng | Quy tắc |
|---|---|---|---|
| 1 | `the product I bought was not delivered, and I'm already paying for it` | **delivery** | §1.2 — cả hai cùng bỏ sót ở vòng 1 |
| 2 | `the product is not good, it has no effect on the eyebrows` | **quality** | §1.2 — cả hai cùng bỏ sót |
| 3 | `store not fit to operate as resellers, they don't care about logistics` | **delivery + service** | §1.2 — cả hai cùng bỏ sót |
| 4 | `I wanted my order as illustrated in the picture` | **quality** | QT1 — sai mô tả, cả hai cùng bỏ sót |
| 5 | `product delivered different from the purchase` | **quality** | QT1 — cả hai cùng bỏ sót |
| 6 | `I really like shopping here, but I still haven't received the product` | **delivery** | QT4 — lời khen không hủy nguyên nhân |
| 7 | `I bought 3 lamps, only received 2. I opened a ticket and got no response.` | **delivery + service** | QT1 + QT2 |
| 8 | `I ordered the Master model and they sent the Standard. I requested cancellation` | **quality** | QT1. **Không** gán service — mới *yêu cầu* hủy |
| 9 | `product more than a month old, no delivery forecast` | **delivery** | **Không** gán service — không có lượt liên hệ nào |
| 10 | `I would like to exchange the product` | **unknown** | QT3 — không nêu vấn đề gì |
| 11 | `I emailed saying I received the wrong voltage and NOBODY GOT BACK TO ME` | **quality + service** | QT1 + QT2 |
| 12 | `product broken on delivery` | **delivery + quality** | Vỡ *trong lúc giao* |
| 13 | `missing parts and the assembly was poorly explained` | **quality** | QT1 — thiếu **bộ phận** |
| 14 | `I always shop at this store and I like it` | **unknown** | Văn bản khen dù 1 sao |
| 15 | `terrible` | **unknown** | QT3 — không nêu đối tượng |

---

## 5. Cột `confidence` và `notes`

| Cột | Cách điền |
|---|---|
| `confidence` | Mức chắc chắn. Vòng một dùng **phần trăm** (`88%`) — giữ nguyên cách đó |
| `notes` | Bắt buộc khi độ chắc chắn thấp, **hoặc khi nghi bản dịch có vấn đề** *(QT5)* |

---

## 6. Quy trình vòng ba

1. Chờ tệp `round2_annotator_A.csv` và `_B.csv` — **250 dòng tầng A**, có cả tiếng
   Anh lẫn tiếng Bồ.
2. **Đọc §1.2 và §3 trước khi gán dòng đầu tiên.** §1.2 là quy tắc quan trọng nhất
   của bản này.
3. Gán **độc lập**, không trao đổi. Tệp để **mù** — không chứa nhãn vòng một.
4. Chạy `python -m masdss.cli.check_goldset --require-complete`.

> **Nếu κ vẫn < 0,6 sau vòng này:** dừng, không gán lần bốn. Khi đó κ thấp là kết
> luận thật về mức độ khó của việc quy kết nguyên nhân từ văn bản đánh giá, và được
> báo cáo như một threat được định lượng ở Chương 4.

**Gold set cuối cùng ghép từ hai nguồn**, và điều này phải ghi rõ trong Chương 4:

| Phần | Nguồn | Lý do |
|---|---|---|
| 250 dòng tầng A | Vòng 3, gán trên bản dịch tiếng Anh | Nơi rào cản ngôn ngữ gây sai sót |
| 150 dòng tầng B | Vòng 1, giữ nguyên | Không phụ thuộc ngôn ngữ. **Đồng thuận 0/150 KHÔNG phải bằng chứng nhãn đúng — xem L25** |

---

## 7. Bản dịch là một công cụ đo, và nó chưa được kiểm định

Bản dịch được tạo bằng dịch máy bên ngoài, nên nó **không tái tạo được bằng một
lệnh**. Vì vậy nó được đóng băng thành artifact có checksum (`translations.csv` +
`translations_meta.json`), và phải được kiểm định như mọi công cụ đo khác:

- **Đối chiếu 50 bản dịch** với người biết tiếng Bồ, ưu tiên các câu có phủ định,
  viết tắt, và các dòng người gán đã ghi chú nghi ngờ.
- Báo cáo tỷ lệ dịch sai trong **Threats to Validity**.
- Nếu bỏ qua bước này, ta lặp lại đúng lỗi mà bản phản biện đã chỉ ra với bộ từ khóa:
  một công cụ đo không được kiểm định.

---

## 8. Những gì cố ý không có trong tệp gán nhãn

| Không có | Vì sao |
|---|---|
| Nhãn vòng một của bất kỳ ai | Nhìn thấy nhãn cũ sẽ neo phán đoán, và κ vòng này sẽ cao giả tạo |
| Nhãn yếu sinh bằng từ khóa | Làm nhiễm người gán, gold set mất giá trị phá vòng tròn |
| Nguyên nhân hệ thống đã quy kết | Gold set đang được dùng để **kiểm tra** hệ thống |

Nếu bạn thấy mình đang cố đoán "hệ thống muốn nhãn gì", hãy dừng lại — nhãn của bạn
chính là thước đo để chấm hệ thống, không phải ngược lại.
