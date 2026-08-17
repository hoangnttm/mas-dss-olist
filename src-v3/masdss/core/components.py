"""WP9 / T9.3 — Dinh danh THANH PHAN LOGIC, doc lap voi kien truc.  [core]

Phuc vu: RQ1 (giao thuc so sanh: chay CUNG kich ban loi tren hai kien truc).

VAN DE MA FILE NAY GIAI QUYET:

    Kich ban loi truoc day duoc phat bieu theo `agent_id` — "Prediction chet". Nhung
    Monolithic-Complete KHONG CO tac tu nao; no goi capability truc tiep. Mot kich
    ban phat bieu theo agent_id vi vay chi ap duoc len mot trong hai kien truc, va
    con so hong am tham cua ben con lai khong so sanh duoc voi ben nay.

CACH GIAI:

    Kich ban duoc phat bieu theo THANH PHAN LOGIC — mot khai niem ma ca hai kien
    truc deu co. "Nang luc du bao rui ro that bai" la mot menh de co nghia voi ca
    MAS-DSS (PredictionAgent) lan Monolithic (buoc goi risk_model).

    MAS-DSS      : agent_id -> component  (bang anh xa duoi day)
    Monolithic   : moi buoc tu khai bao component cua no

Nho vay `crash:prediction` ap duoc len ca hai, va ty le hong am tham cua chung tro
thanh mot phep so sanh that.

VI SAO FILE NAY NAM O `core/` CHU KHONG PHAI `chaos/`: `runtime/faults.py` can no de
dich agent_id sang ten thanh phan, ma `runtime` khong duoc phep phu thuoc `chaos`
(test_layering.py). Dat o day la dung ban chat — day la TU VUNG CHUNG de goi ten
cac bo phan cua he thong, khong phai mot cong cu cua thi nghiem chaos.
"""

from __future__ import annotations

from enum import Enum


# --- Be mat hong: thanh phan nao ton tai o kien truc nao ---
#
# Nam thanh phan CHI MAS-DSS moi co. Day la phan be mat hong ma kien truc da tang
# them, va H2 doi hoi no phai duoc phu boi guard chu khong duoc bo qua.
#
# Mot dieu phai noi thang khi bao cao: tren nam thanh phan nay, con so "Monolithic
# hong am tham 0%" KHONG phai mot chien thang cua MAS-DSS. Monolithic khong co
# thanh phan do de ma hong. Phep so sanh dung o day la MAS-DSS voi CHINH NO khi
# tat tang chiu loi — khong phai MAS-DSS voi doi chung.
MAS_ONLY_COMPONENTS = ("analytics", "recommendation", "critic", "arbiter", "case_manager")
SHARED_COMPONENTS = ("prediction", "cause_delivery", "cause_quality",
                     "cause_service", "rules")


class Component(str, Enum):
    """Thanh phan logic cua he thong.

    KHONG phai moi thanh phan deu co mat o ca hai kien truc — xem `SHARED_COMPONENTS`
    va `MAS_ONLY_COMPONENTS` o tren. Chu thich cu ("co mat trong CA HAI kien truc")
    la sai, va cai sai do che dung dieu ma H2 phai tra loi.
    """

    ANALYTICS = "analytics"
    PREDICTION = "prediction"
    CAUSE_DELIVERY = "cause_delivery"
    CAUSE_QUALITY = "cause_quality"
    CAUSE_SERVICE = "cause_service"
    RECOMMENDATION = "recommendation"
    CRITIC = "critic"
    ARBITER = "arbiter"
    RULES = "rules"
    CASE_MANAGER = "case_manager"


# MAS-DSS: tac tu -> thanh phan logic
AGENT_TO_COMPONENT: dict[str, Component] = {
    "Analytics": Component.ANALYTICS,
    "Prediction": Component.PREDICTION,
    "DeliveryAnalyst": Component.CAUSE_DELIVERY,
    "QualityAnalyst": Component.CAUSE_QUALITY,
    "ServiceAnalyst": Component.CAUSE_SERVICE,
    "Recommendation": Component.RECOMMENDATION,
    "PolicyCritic": Component.CRITIC,
    "Arbiter": Component.ARBITER,
    "RuleAgent": Component.RULES,
    "CaseManager": Component.CASE_MANAGER,
}


def component_of(agent_id: str) -> str:
    """Tra ve ten thanh phan logic cua mot tac tu.

    Tac tu chua duoc anh xa se tra ve chinh agent_id — de kich ban van chay duoc,
    nhung khi do no chi ap len MAS-DSS. `test_chaos_parity.py` chan truong hop nay.
    """
    component = AGENT_TO_COMPONENT.get(agent_id)
    return component.value if component else agent_id


def normalize_target(name: str) -> str:
    """Chap nhan ca ten tac tu lan ten thanh phan, chuan hoa ve ten thanh phan.

    Cho phep viet `crash:Prediction` (quen thuoc) lan `crash:prediction` (chinh xac).
    """
    if name in AGENT_TO_COMPONENT:
        return AGENT_TO_COMPONENT[name].value
    return name
