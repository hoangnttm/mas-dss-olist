"""WP9 / T9.1, T9.2, T9.3 — Bo tiem loi.

Phuc vu: RQ1 (dong gop chinh cua luan van).

NAM NHOM LOI, moi nhom ba muc — phan loai theo technical-plan-v3.md §A.7:

    1. crash            — thanh phan raise exception          (k = 1, 2, 3 thanh phan)
    2. hang             — thanh phan treo qua han chot        (k = 1, 2, 3 thanh phan)
    3. byzantine_gross  — tra ket qua HOP LE nhung la hang so (k = 1, 2, 3 thanh phan)
    4. drift            — phan phoi dac trung dau vao lech    (5%, 10%, 20%)
    5. bias             — do tin cay lech he thong            (+0,05 / +0,15 / +0,30)

MOT QUYET DINH MO HINH HOA QUAN TRONG: nhom 4 KHONG phai la bo tiem theo thanh phan.

    Drift phan phoi la thuoc tinh cua DONG DU LIEU VAO, khong phai hanh vi sai cua
    mot thanh phan. Mo hinh hoa no nhu mot bo tiem theo thanh phan se sai ve ban
    chat, va con lam no chi anh huong mot kien truc. Vi vay drift duoc ap o tang
    case (`drift_cases`), truoc khi case di vao he thong — nen no tac dong len
    MAS-DSS va Monolithic-Complete y het nhau theo cau tao.

Moi bo tiem nham vao THANH PHAN LOGIC (core/components.py), khong phai tac tu, de
cung mot kich ban ap duoc len ca hai kien truc (T9.3).

Moi bo tiem nhan SEED. Cung seed, cung du lieu, cung cau hinh thi cho cung chuoi
su kien — dieu kien de ket qua chaos duoc dua vao luan van (Gate G5).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

import numpy as np

from masdss.core.errors import DeterministicError, TransientError
from masdss.core.message import Message
from masdss.core.ontology import OrderCase

# --- Dac trung so duoc dung khi mo phong drift phan phoi ---
DRIFTABLE_FEATURES = ("delivery_delay_days", "delivery_days", "carrier_handover_days",
                      "freight_ratio", "price", "freight_value")


def _recompute_derived(content: dict, poisoned_field: str) -> dict:
    """Suy lai cac truong DAN XUAT sau khi truong NGUON bi dau doc.

    Chi suy lai khi chinh truong NGUON bi dau doc. Neu bo tiem nham thang vao truong
    dan xuat (`--inject constant:Prediction:risk`) thi phep suy lai se GHI DE dung cho
    vua dau doc, va kich ban tro thanh vo hieu — mot phep thu rong khac.

    VI SAO HAM NAY BAT BUOC PHAI TON TAI — day la mot lo hong that da lam sai lech
    dung con so trung tam cua RQ1.

        `PredictionAgent` phat ra ca `risk_score` (nguon) lan `risk` (dan xuat).
        `reduce_reply` dung `risk` de dung quyet dinh. Bo tiem chi dau doc `risk_score`,
        nen truoc khi co ham nay:

            MAS-DSS     — `risk_score` bi dau doc, `risk` KHONG DOI => quyet dinh
                          khong bi anh huong
            Monolithic  — `guard_call` boc `risk_model.run` tra ve mot SO tran, bo
                          tiem thay the nguyen gia tri => quyet dinh BI anh huong

        Do duoc tren 200 case, `byz_gross_k2`, tang chiu loi TAT:
            muc rui ro cua MAS  {0: 122, 1: 50, 2: 28} — Y HET duong khoe
            muc rui ro cua Mono {2: 200}               — hong toan bo

        Nghia la "MAS-DSS hong am tham 0,0%" o nhom byzantine KHONG do kha nang chiu
        loi — no chi phan anh CHO DAT BO TIEM. Dung loai loi ma L12 canh bao.

    Phep suy lai dung DUNG nguong ma chinh mo hinh dung, lay tu `risk_thresholds` di
    kem trong thong diep. Nho vay bo tiem khong phai biet gi ve mo hinh, va thong diep
    van tu giai thich duoc (DP4).
    """
    if poisoned_field != "risk_score":
        return content
    if "risk_score" not in content or "risk" not in content:
        return content
    bounds = content.get("risk_thresholds")
    if not bounds or len(bounds) != 2:
        return content
    low, high = float(bounds[0]), float(bounds[1])
    score = float(content["risk_score"])
    content["risk"] = 2 if score >= high else (1 if score >= low else 0)
    return content


def _poison(result, field_name: str, value):
    """Dau doc mot o trong ket qua, bat ke ket qua o dang nao.

    Hai kien truc bieu dien ket qua khac nhau, nen bo tiem phai xu ly ca hai:
        Message      — MAS-DSS
        gia tri tho  — Monolithic (so, hoac tuple (confidence, evidence))
    """
    if isinstance(result, Message):
        if field_name not in result.content:
            return result
        content = dict(result.content)
        content[field_name] = value
        content = _recompute_derived(content, field_name)
        return Message(
            msg_id=result.msg_id, conversation_id=result.conversation_id,
            trace_id=result.trace_id, sender=result.sender, receiver=result.receiver,
            performative=result.performative, ontology=result.ontology,
            content=content, in_reply_to=result.in_reply_to,
            deadline_ms=result.deadline_ms, seq=result.seq,
        )
    if isinstance(result, tuple) and result and isinstance(result[0], (int, float)):
        return (value, *result[1:])
    if isinstance(result, (int, float)):
        return value
    return result


def _shift(result, field_name: str, delta: float):
    if isinstance(result, Message):
        if field_name not in result.content:
            return result
        current = float(result.content[field_name])
        return _poison(result, field_name, max(0.0, min(1.0, current + delta)))
    if isinstance(result, tuple) and result and isinstance(result[0], (int, float)):
        return (max(0.0, min(1.0, float(result[0]) + delta)), *result[1:])
    if isinstance(result, (int, float)):
        return max(0.0, min(1.0, float(result) + delta))
    return result


@dataclass
class BaseInjector:
    """Nen chung: nham vao mot hoac nhieu thanh phan logic."""

    targets: tuple[str, ...] = ()

    def hits(self, component: str) -> bool:
        return component in self.targets

    def before(self, component: str, message: Message | None = None) -> None:
        return None

    def after(self, component: str, result):
        return result

    def delay_ms(self, component: str) -> float:
        return 0.0


@dataclass
class NullInjector(BaseInjector):
    """Khong lam gi. Duong chay binh thuong, chi phi bang khong."""


@dataclass
class CrashInjector(BaseInjector):
    """Nhom 1 — CRASH: thanh phan raise exception.

    `deterministic=True` mo phong nang luc nen hong: thu lai vo nghia.
    `deterministic=False` mo phong loi I/O nhat thoi: thu lai co y nghia.
    """

    deterministic: bool = True
    probability: float = 1.0
    seed: int = 0
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def before(self, component: str, message: Message | None = None) -> None:
        if not self.hits(component) or self._rng.random() > self.probability:
            return
        if self.deterministic:
            raise DeterministicError(f"[chaos] {component}: nang luc nen hong")
        raise TransientError(f"[chaos] {component}: loi I/O nhat thoi")


@dataclass
class HangInjector(BaseInjector):
    """Nhom 2 — HANG: thanh phan treo qua han chot.

    Do tre duoc ap BEN TRONG pham vi `asyncio.wait_for`, nen no sinh ra `AgentTimeout`
    that — task bi HUY. Ban v0 do latency SAU khi tac tu chay xong, nen mot tac tu
    treo lam treo ca pipeline vinh vien; day la kich ban chung minh khac biet do.
    """

    delay: float = 50.0  # mili giay

    def delay_ms(self, component: str) -> float:
        return self.delay if self.hits(component) else 0.0


@dataclass
class ConstantOutputInjector(BaseInjector):
    """Nhom 3 — BYZANTINE THO: tra ket qua HOP LE nhung la hang so.

    Day la loai loi giet he thong trong thuc te: khong exception, khong log do, chi
    la quyet dinh sai hang loat. Moi engine dieu phoi deu MU voi loai nay — do chinh
    la ly do Health Monitor phai tu viet (technical-plan-v3.md §6.1).
    """

    field_name: str = "risk_score"
    constant: float = 0.5

    def after(self, component: str, result):
        return _poison(result, self.field_name, self.constant) if self.hits(component) else result


@dataclass
class BiasInjector(BaseInjector):
    """Nhom 5 — BYZANTINE TINH VI: do tin cay lech mot cach he thong.

    Guard KHONG duoc thiet ke rieng de bat loai nay. Ket qua o day moi la ket qua
    thuc nghiem that (technical-plan-v3.md §A.7).
    """

    field_name: str = "risk_score"
    delta: float = 0.15

    def after(self, component: str, result):
        return _shift(result, self.field_name, self.delta) if self.hits(component) else result


# --- Nhom 4: drift phan phoi, ap o TANG CASE ---

def drift_cases(cases: list[OrderCase], magnitude: float, seed: int = 0) -> list[OrderCase]:
    """Nhom 4 — DRIFT: dich chuyen phan phoi dac trung dau vao.

    `magnitude` la ty le dich theo do lech chuan cua chinh tap case, ap DAN theo thu
    tu case de mo phong drift tich luy chu khong phai mot cu soc tuc thoi.

    Ap o tang case chu khong tiem vao thanh phan, vi drift la thuoc tinh cua dong du
    lieu vao. Nho vay no tac dong len hai kien truc y het nhau theo cau tao — dieu
    kien de RQ1(a) so sanh duoc.
    """
    if magnitude <= 0 or not cases:
        return cases

    rng = np.random.default_rng(seed)
    stats: dict[str, float] = {}
    for name in DRIFTABLE_FEATURES:
        values = [float(c.features[name]) for c in cases
                  if name in c.features and c.features[name] is not None
                  and not (isinstance(c.features[name], float) and np.isnan(c.features[name]))]
        if len(values) > 1:
            stats[name] = float(np.std(values)) or 1.0

    drifted: list[OrderCase] = []
    n = len(cases)
    for index, case in enumerate(cases):
        ramp = (index + 1) / n  # drift tich luy dan, khong phai cu soc tuc thoi
        features = dict(case.features)
        for name, spread in stats.items():
            value = features.get(name)
            if value is None or (isinstance(value, float) and np.isnan(value)):
                continue
            features[name] = float(value) + ramp * magnitude * spread * (1.0 + rng.normal(0, 0.1))
        drifted.append(OrderCase(
            case_id=case.case_id, decision_point=case.decision_point,
            features=features, review_text=case.review_text,
        ))
    return drifted


@dataclass
class ByzantineByComponent(BaseInjector):
    """Byzantine THEO TUNG THANH PHAN — moi thanh phan bi dau doc o dung truong no phat ra.

    VI SAO CAN LOP NAY. `ConstantOutputInjector` gan cung mot ten truong (`risk_score`)
    cho moi muc tieu. Voi `prediction` thi dung, nhung nam thanh phan chi MAS-DSS moi
    co KHONG phat ra truong do — `_poison` gap truong khong ton tai thi tra ve nguyen
    ket qua, tuc PHEP TIEM KHONG LAM GI CA.

    Va no da that su khong lam gi: lan chay dau tren be mat `mas-only` cho
    `mas_changed = 0,0%` o ca ba muc. Con so do trong nhu bang chung ve tinh chiu loi
    ("khong case nao bi anh huong"), nhung no chi la mot phep thu RONG. Xem L36.

    Gia tri dau doc duoc chon la HOP LE VE LUOC DO va NGHE HOP LY — do la dinh nghia
    cua Byzantine. `challenged = False` nguy hiem nhat: bo phan bien im lang chap
    thuan moi de xuat, va khong co gi trong dau ra to ra bat thuong.
    """

    field_by_component: dict[str, tuple[str, object]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # `targets` phai khop danh sach thanh phan bi dau doc, neu khong `Scenario.targets`
        # se bao cao mot be mat khac voi be mat that su bi tiem.
        object.__setattr__(self, "targets", tuple(self.field_by_component))

    def after(self, component: str, result):
        spec = self.field_by_component.get(component)
        if spec is None:
            return result
        field_name, value = spec
        return _poison(result, field_name, value)


# Truong ma tung thanh phan CHI-MAS thuc su phat ra, doc tu nhat ky message cua mot
# lan chay khoe — khong phai doan tu ten lop.
#
# `case_manager` KHONG co trong bang nay va do la co y: no khong xuat hien trong
# STAGE1_PLAN lan STAGE2_PLAN, tuc no khong bao gio duoc goi. Mot thanh phan khong
# duoc goi thi khong hong duoc, va dua no vao danh sach be mat hong la dem thua.
MAS_ONLY_POISON: dict[str, tuple[str, object]] = {
    "analytics": ("context", {}),
    "recommendation": ("proposal", {"candidate_action": "no_action", "causes": [],
                                    "max_probability": 0.0, "n_causes": 0}),
    # Nguy hiem nhat trong bon: bo phan bien im lang dong y voi moi de xuat.
    "critic": ("challenged", False),
    "arbiter": ("sided_with", "proposal"),
}
