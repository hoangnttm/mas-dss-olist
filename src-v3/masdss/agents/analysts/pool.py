"""WP6 / T6.6 — Bon Analyst chuyen biet.

Phuc vu: RQ3 (DP2 — quy ket bang canh tranh).

Moi analyst la mot lop RAT MONG dat tren lop nen. Toan bo khac biet giua chung
nam o ba thu: nguyen nhan phu trach, capability duoc cam vao, va `cost_class`.

BA ANALYST (`PriceAnalyst` da bi go — xem `core/ontology.Cause`).

BANG DIEU KIEN REFUSE — moi dieu kien deu kiem chung duoc, khong phai "cho co":

| Analyst  | REFUSE khi                                        | Ty le thuc te |
|----------|---------------------------------------------------|---------------|
| Delivery | thieu moc thoi gian giao, hoac nhom hang qua it mau |               |
| Quality  | don khong co binh luan (tang B)                     | 25,23% don    |
| Service  | don khong co binh luan (tang B)                     | 25,23% don    |

`cost_class` khong phai chu thich: no la dau vao cua bai toan phan bo ngan sach
trong Contract Net (T7.1). Hai analyst van ban dat gap hang tram lan hai analyst
cau truc, va do chinh la thu lam cho giao thuc tro nen load-bearing.
"""

from __future__ import annotations

from masdss.agents.base import AnalystAgent, TextAnalystAgent
from masdss.core.ontology import Cause


class DeliveryAnalyst(AnalystAgent):
    agent_id = "DeliveryAnalyst"
    cause = Cause.DELIVERY
    cost_class = "cheap"


class QualityAnalyst(TextAnalystAgent):
    agent_id = "QualityAnalyst"
    cause = Cause.QUALITY
    cost_class = "expensive"


class ServiceAnalyst(TextAnalystAgent):
    agent_id = "ServiceAnalyst"
    cause = Cause.SERVICE
    cost_class = "expensive"
