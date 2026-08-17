"""WP0 / T6.2 — Ke hoach dieu phoi o DANG DU LIEU.

Phuc vu: RQ2 (dinh tuyen dong), RQ3 (mo phien dau thau theo muc rui ro).

RANG BUOC BAT BUOC (technical-plan-v3.md §2.2c): ke hoach la DU LIEU, khong phai
ma dieu khien. Hai ly do:
  - Chan nguy co tu viet may trang thai te: khong chu trinh, khong nhanh long nhau.
  - Ke hoach in ra duoc vao phu luc luan van nhu mot artifact kiem tra duoc.

Hai ke hoach ung voi hai moc quyet dinh (research-questions-objectives.md §0.2):
  STAGE1_PLAN @ T3 — du bao rui ro, chi dac trung bang, CHUA co van ban
  STAGE2_PLAN @ T4 — quy ket nguyen nhan, co van ban voi 74,71% don
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from masdss.core.ontology import RiskLevel
from masdss.system.blackboard import Blackboard

Guard = Callable[[Blackboard], bool]
BudgetFn = Callable[[Blackboard], float]


@dataclass(frozen=True)
class Step:
    """Mot buoc trong ke hoach.

    `agent` va `fanout` loai tru nhau: mot buoc hoac goi mot tac tu, hoac mo mot
    phien dau thau toi ca nhom.
    """

    name: str
    agent: str | None = None
    fanout: str | None = None
    on: Guard | None = None          # dieu kien de buoc nay duoc chay
    budget: BudgetFn | None = None   # ngan sach tinh toan cap cho phien dau thau
    deadline_ms: float | None = None
    # "broadcast"     — goi moi tac tu trong nhom (khong co rang buoc tai nguyen)
    # "contract_net"  — hai pha: tham do roi phan bo duoi rang buoc ngan sach (T7.1)
    protocol: str = "broadcast"

    def __post_init__(self) -> None:
        if bool(self.agent) == bool(self.fanout):
            raise ValueError(f"Step '{self.name}' phai co dung mot trong agent/fanout")

    def should_run(self, bb: Blackboard) -> bool:
        return True if self.on is None else bool(self.on(bb))


Plan = tuple[Step, ...]


# Gia DO DUOC cua BA analyst, mili giay moi loi goi (p95 tren 400 case that).
# `PriceAnalyst` da bi go 12/08 cung voi nhan `price` — xem `core/ontology.Cause`.
# Do lai bang: python -m masdss.cli.compare_heads
#
# `delivery` DOI GIA 0,3 -> 1,6 tu 14/08: no nay HOP hai nguon bang chung (z-score
# cau truc + nhanh van ban cua cause head), nen phai chay ca hai moi ket luan duoc.
# Xem `capabilities/delivery_signal.CombinedDeliverySignal`.
#
# Con so nay la MAU SO cua ngan sach, nen quen cap nhat no se lam moi muc ngan sach
# nho di mot cach am tham va Contract Net that chat hon y dinh.
FULL_ANALYST_COST_MS = 1.6 + 1.3 + 1.3   # delivery(hop) + quality + service

# Ngan sach dat theo BOI SO cua chi phi chay HET, khong dat bang so tuyet doi.
#
# Cach dat cu dung so tuyet doi (2 / 20 / 120 ms) va no da gay ra loi L27: khi
# cause head doi tu ban tam (0,0093 ms) sang ban huan luyen, muc 2,0 ms cua case
# rui ro THAP tro nen khong du cho bat ky analyst van ban nao. Hau qua la CONG RUI
# RO da duoc go tuong minh khoi moc T4 lai quay ve mot cach NGAM qua ngan sach —
# don rui ro thap khong bao gio duoc phan tich van ban, va macro-F1 cua MAS-DSS
# tut 0,14 duoi doi chung don khoi vi mot tham so chu khong vi kien truc.
#
# Dat theo boi so lam rang buoc DIEN DAT DUOC va tu dieu chinh khi gia doi:
#   0,70 -> phai chon: du cho analyst giao hang + DUNG MOT analyst van ban
#   1,0  -> vua du chay het
#   1,5  -> chay het con du
#
# Muc thap nhat la co chu dich: no giu Contract Net LOAD-BEARING o case rui ro thap
# (van phai chon), nhung KHONG loai han phan tich van ban ra khoi nhom do.
#
# HE SO THAP DA DOI 0,60 -> 0,70 NGAY 14/08, va day la mot phep KHOI PHUC NGU NGHIA
# chu khong phai mot lan noi long de lam so dep hon:
#
#     He so 0,60 duoc hieu chuan khi `delivery` con gia 0,3 ms. Khi do
#     0,60 x 2,9 = 1,74 >= 0,3 + 1,3 — dung y dinh da ghi o dong tren.
#
#     Tu 14/08 `delivery` hop hai nguon bang chung nen gia len 1,6, va mau so len
#     4,2. He so cu cho 0,60 x 4,2 = 2,52 < 1,6 + 1,3 = 2,9 — tuc muc thap KHONG CON
#     mua noi mot analyst van ban nao, trai voi chinh cau mo ta cua no.
#
#     Hau qua do duoc, va no lon: macro-F1 cua `quality` tut 0,6667 -> 0,2376 vi
#     `QualityAnalyst` bi loai khoi phan lon phien dau thau. `delivery` van tot len
#     nho nguon hop nhat, nhung tong the xau di.
#
#     He so dung suy tu chinh y dinh: (1,6 + 1,3) / 4,2 = 0,6905 -> lam tron 0,70.
#
# BAI HOC LAP LAI CUA L27, o mot tang khac: lan truoc ngan sach dat bang SO TUYET
# DOI nen no vo nghia khi gia doi. Nay no dat bang TY LE — nhung chinh ty le do ma
# hoa "bao nhieu analyst duoc chay", nen khi CO CAU chi phi doi thi ty le cung phai
# tinh lai. Mot tham so tu dieu chinh theo gia van khong tu dieu chinh theo co cau.
BUDGET_RATIO = {"low": 0.70, "medium": 1.0, "high": 1.5}

# RANG BUOC NGAN SACH MAC DINH **TAT** — quyet dinh pham vi ngay 14/08.
#
# VI SAO TAT, va vi sao co che van o lai trong ma nguon.
#
#   Do duoc tren gold set 300 dong: bat ngan sach lam macro-F1 cua MAS-DSS tut tu
#   0,6862 xuong 0,5862, va toan bo mat mat roi DUNG VAO hai tang bi cat:
#
#       LOW     152 case · 2,00 analyst · 0,5725 vs 0,6667  ->  -0,0942
#       MEDIUM   80 case · 3,00 analyst · 0,6933 vs 0,6933  ->   0,0000
#       HIGH     43 case · 3,00 analyst · 0,7579 vs 0,7579  ->   0,0000
#       OOD      25 case · 2,00 analyst · 0,6818 vs 0,8000  ->  -0,1182
#
#   Co che cat DUNG CHO no nham, va thiet hai KHONG lan sang nhom gia tri cao. Nhung
#   cai gia -0,10 macro-F1 chi doi lay -0,77 ms moi case — o quy mo nay khong dang.
#
#   Tat ngan sach thi MAS-DSS va Monolithic-Complete cho ket qua GIONG HET nhau, nen
#   RQ3 tro thanh mot dieu kien kiem soat sach: moi khac biet o RQ1 khong the quy cho
#   do chinh xac nen.
#
# CAI GIA CUA VIEC TAT, phai noi thang o Chuong 4 va §5.7 chu khong duoc giau:
#   - `allocate()` suy bien thanh ham hang: moi analyst deu duoc goi.
#   - `REJECT_PROPOSAL` khong xuat hien TREN DUONG KHOE. Khong duoc phat bieu manh hon
#     the: duoi tiem loi no van duoc phat 1.200 lan (crash_k2/k3, hang_k2/k3), vi
#     analyst hong ngay trong pha 1 nen khong khai bao, con vong trao thau duyet theo
#     DANH SACH TAC TU chu khong theo danh sach ban khai. Performative nay DOI VAI
#     ("thua thau" -> "khong khai bao duoc"), khong chet.
#   - Pha 1 cua Contract Net van ton 6/21,16 message moi case ma KHONG quyet dinh gi.
#
# Co che o lai vi hai ly do doc lap: no la doi tuong cua phan tich do nhay (§5.11), va
# tieu chi MT2.2 doi "moi co che dieu phoi bat/tat duoc BANG THAM SO CAU HINH, khong
# bang nhanh ma nguon".
BUDGET_ENABLED_BY_DEFAULT = False


def budget_for(bb: Blackboard) -> float:
    """Ngan sach tinh toan theo muc rui ro, tinh theo boi so chi phi chay het."""
    if bb.risk is None or bb.risk == RiskLevel.LOW:
        ratio = BUDGET_RATIO["low"]
    elif bb.risk == RiskLevel.MEDIUM:
        ratio = BUDGET_RATIO["medium"]
    else:
        ratio = BUDGET_RATIO["high"]
    return round(FULL_ANALYST_COST_MS * ratio, 3)


# --- Giai doan 1 @ T3: du bao rui ro tren dac trung bang ---
STAGE1_PLAN: Plan = (
    Step("analytics", agent="Analytics"),
    Step("prediction", agent="Prediction"),
    Step("rules", agent="RuleAgent"),
)

# --- Giai doan 2 @ T4: quy ket nguyen nhan va sinh hanh dong ---
STAGE2_PLAN: Plan = (
    Step("analytics", agent="Analytics"),
    Step("prediction", agent="Prediction"),
    # KHONG co dieu kien `risk >= MEDIUM` o day, va day la mot sua loi thiet ke.
    #
    # Ban dau buoc nay bi chan sau nguong rui ro du bao. Nhung o T4, case DA co
    # danh gia 1-2 sao roi — su bat man la SU KIEN DA XAY RA, khong con la thu can
    # du bao. Chan quy ket nguyen nhan sau mot du bao (PR-AUC 0,40) khien 94,7% so
    # case khong bao gio duoc phan tich, va toan bo RQ3 mat doi tuong nghien cuu.
    #
    # "Duong tat cho case rui ro thap" van co y nghia, nhung no thuoc GIAI DOAN 1
    # @ T3 — noi ta thuc su dang du bao. Ngan sach tinh toan van thay doi theo muc
    # rui ro, nen Contract Net khong mat tinh phan bo tai nguyen.
    Step("contract_net", fanout="AnalystPool", budget=budget_for,
         protocol="contract_net"),
    Step("recommend", agent="Recommendation", on=lambda bb: bool(bb.causes)),
    Step("critique", agent="PolicyCritic", on=lambda bb: bb.proposal is not None),
    Step("arbitrate", agent="Arbiter",
         on=lambda bb: bb.critique is not None and bb.critique.challenged),
    Step("rules", agent="RuleAgent"),
)


def with_budget(plan: Plan, enabled: bool) -> Plan:
    """Bat/tat rang buoc ngan sach cho moi buoc dau thau.

    Tat ngan sach = go ham `budget` khoi `Step`, khong phai dat mot con so rat lon.
    Hai cach cho cung ket qua phan bo, nhung chi cach dau lam bao cao TRUNG THUC:
    `budget_binds_rate` se la 0 va `avg_utilisation` khong con y nghia, thay vi mot
    con so nho gia tao trong nhu the co che van dang lam viec.

    Xem `BUDGET_ENABLED_BY_DEFAULT` de biet vi sao mac dinh la tat.
    """
    if enabled:
        return plan
    return tuple(
        Step(name=s.name, agent=s.agent, fanout=s.fanout, on=s.on,
             budget=None, deadline_ms=s.deadline_ms, protocol=s.protocol)
        for s in plan
    )


def with_budget_scale(plan: Plan, scale: float | None) -> Plan:
    """Nhan ngan sach cua moi buoc dau thau voi mot he so.

    Ton tai de chay PHAN TICH DO NHAY NGAN SACH, va phan tich do can thiet vi mot
    ly do cu the phat hien duoc khi chay het chu trinh tren gold set:

        `budget_for` cap 2,0 ms cho case rui ro THAP. Khi cause head con la ban tam
        (0,4 ms) thi con so do khong rang buoc gi. Voi head da huan luyen (12 ms),
        analyst van ban KHONG BAO GIO mua duoc suat tren case rui ro thap — tuc
        cong rui ro da bi go tuong minh o T4 nay quay lai mot cach NGAM qua ngan
        sach, va macro-F1 cua MAS-DSS tut xuong duoi doi chung don khoi.

    Bao cao mot con so o duy nhat mot muc ngan sach se bien mot tham so chua hieu
    chinh thanh mot ket luan ve kien truc. Do la ly do he so nay ton tai.
    """
    if scale is None or scale == 1.0:
        return plan
    return tuple(
        Step(name=s.name, agent=s.agent, fanout=s.fanout, on=s.on,
             budget=(None if s.budget is None
                     else (lambda bb, fn=s.budget: fn(bb) * scale)),
             deadline_ms=s.deadline_ms, protocol=s.protocol)
        for s in plan
    )


def with_deadline(plan: Plan, deadline_ms: float | None) -> Plan:
    """Dung lai ke hoach voi han chot khac cho moi buoc.

    Dung cho kich ban `hang`: rut ngan han chot de timeout xay ra trong vai chuc
    mili giay thay vi vai giay, nen 300 case chay xong trong thoi gian hop ly ma
    van la timeout THAT (task bi huy), khong phai mo phong.
    """
    if deadline_ms is None:
        return plan
    return tuple(
        Step(name=s.name, agent=s.agent, fanout=s.fanout, on=s.on,
             budget=s.budget, deadline_ms=deadline_ms, protocol=s.protocol)
        for s in plan
    )
