"""WP9 / T9.2 — Danh muc kich ban loi: 5 nhom x 3 muc.

Phuc vu: RQ1(b) — duong cong do nhay va do dac hieu cua bo giam sat.

CACH DOC BANG KET QUA. Ba nhom dau (crash, hang, byzantine tho) la nhung nhom ma
guard ĐƯỢC thiet ke de bat, nen ket qua o do la KIEM TRA DAC TA. Hai nhom cuoi
(drift, bias) la nhung nhom guard KHONG duoc thiet ke rieng de bat — ket qua o do
moi la KET QUA THUC NGHIEM.

Phan biet nay phai duoc giu nguyen khi viet Chuong 5. Bao cao "guard bat duoc loi
crash" nhu mot phat hien la tu lua: ta viet guard de bat no.

MUC DO tang dan trong moi nhom:
    crash / hang / byzantine tho : so THANH PHAN bi anh huong (1 -> 2 -> 3)
    drift                        : bien do dich chuyen phan phoi (5% -> 10% -> 20%)
    bias                         : do lech do tin cay (+0,05 -> +0,15 -> +0,30)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from masdss.chaos.injector import (
    MAS_ONLY_POISON,
    BiasInjector,
    ByzantineByComponent,
    ConstantOutputInjector,
    CrashInjector,
    HangInjector,
    NullInjector,
)
from masdss.config import CONFIG
from masdss.core.components import Component

# Ba thanh phan bi nham toi khi tang muc do. Thu tu co chu dich: bat dau tu thanh
# phan duoc giam sat tot nhat, roi mo rong sang thanh phan giam sat kem hon.
ESCALATION = (
    Component.PREDICTION.value,
    Component.CAUSE_DELIVERY.value,
    Component.CAUSE_QUALITY.value,
)

# Guard co duoc thiet ke rieng de bat nhom nay khong.
DESIGNED_FOR = {
    "crash": True,
    "hang": True,
    "byzantine_gross": True,
    "drift": False,
    "bias": False,
}


@dataclass(frozen=True)
class Scenario:
    """Mot kich ban loi co the tai lap."""

    id: str
    group: str
    level: int
    description: str
    make_injector: Callable[[], object] = field(repr=False)
    drift: float = 0.0
    deadline_ms: float | None = None

    @property
    def designed_for(self) -> bool:
        """Guard co duoc thiet ke rieng de bat nhom loi nay khong."""
        return DESIGNED_FOR[self.group]

    @property
    def targets(self) -> tuple[str, ...]:
        return tuple(getattr(self.make_injector(), "targets", ()))


def _crash(level: int) -> Scenario:
    targets = ESCALATION[:level]
    return Scenario(
        id=f"crash_k{level}", group="crash", level=level,
        description=f"{level} thanh phan raise exception tat dinh: {', '.join(targets)}",
        make_injector=lambda t=targets: CrashInjector(
            targets=t, deterministic=True, seed=CONFIG.seed),
    )


def _hang(level: int) -> Scenario:
    targets = ESCALATION[:level]
    # Han chot rut ngan de kich ban chay trong thoi gian hop ly. Do tre gap doi han
    # chot nen timeout chac chan xay ra, nhung chi ton ~20ms moi case.
    return Scenario(
        id=f"hang_k{level}", group="hang", level=level,
        description=f"{level} thanh phan treo qua han chot: {', '.join(targets)}",
        make_injector=lambda t=targets: HangInjector(targets=t, delay=20.0),
        deadline_ms=10.0,
    )


def _byzantine_gross(level: int) -> Scenario:
    targets = ESCALATION[:level]
    return Scenario(
        id=f"byz_gross_k{level}", group="byzantine_gross", level=level,
        description=f"{level} thanh phan tra hang so: {', '.join(targets)}",
        make_injector=lambda t=targets: ConstantOutputInjector(
            targets=t, field_name="risk_score", constant=0.5),
    )


def _drift(level: int, magnitude: float) -> Scenario:
    return Scenario(
        id=f"drift_{int(magnitude * 100)}pct", group="drift", level=level,
        description=f"phan phoi dac trung dau vao dich {int(magnitude * 100)}% do lech chuan",
        make_injector=NullInjector,   # drift ap o tang case, khong tiem vao thanh phan
        drift=magnitude,
    )


def _bias(level: int, delta: float) -> Scenario:
    target = (Component.PREDICTION.value,)
    return Scenario(
        id=f"bias_{int(delta * 100):02d}", group="bias", level=level,
        description=f"do tin cay cua prediction lech he thong +{delta:.2f}",
        make_injector=lambda d=delta: BiasInjector(
            targets=target, field_name="risk_score", delta=d),
    )


# --------------------------------------------------------------------------
# HAI BO KICH BAN CON THIEU DE H2 KIEM DINH DUOC
#
# H2 phat bieu pham vi: "tren TOAN BO be mat hong cua no, o CA HAI moc quyet dinh,
# ke ca nam thanh phan ma kien truc don khoi khong co". Bo kich ban truoc day chi
# phu MOT phan tu cua ca hai chieu do — giai doan 2, thanh phan dung chung.
#
# Hai bo duoi day dong hai lo hong ay. Chung khong lam H2 de thoa man hon; chung
# lam no KIEM DINH DUOC. Va vi pham vi rong hon, kha nang H2 that bai cung cao hon.
# --------------------------------------------------------------------------

# Giai doan 1 @ T3 chi co ba buoc (system/plan.STAGE1_PLAN), nen thang do leo phai
# khac giai doan 2 — `cause_*` khong ton tai o day.
ESCALATION_STAGE1 = (
    Component.PREDICTION.value,
    Component.ANALYTICS.value,
    Component.RULES.value,
)

# Nam thanh phan CHI MAS-DSS moi co, theo thu tu xuat hien trong STAGE2_PLAN.
ESCALATION_MAS_ONLY = (
    Component.ANALYTICS.value,
    Component.RECOMMENDATION.value,
    Component.CRITIC.value,
    Component.ARBITER.value,
    Component.CASE_MANAGER.value,
)


def _kich_ban(kind: str, level: int, targets: tuple[str, ...], hau_to: str) -> Scenario:
    """Dung mot kich ban tren MOT danh sach thanh phan bat ky.

    Ba ham `_crash`/`_hang`/`_byzantine_gross` o tren gan cung `ESCALATION`. Ham nay
    tach phan "nham vao dau" ra khoi phan "hong kieu gi", de cung mot kieu hong ap
    duoc len ba be mat khac nhau ma khong nhan ba lan cung mot doan ma.
    """
    ten = ", ".join(targets)
    if kind == "crash":
        return Scenario(
            id=f"crash_{hau_to}k{level}", group="crash", level=level,
            description=f"{len(targets)} thanh phan raise exception: {ten}",
            make_injector=lambda t=targets: CrashInjector(
                targets=t, deterministic=True, seed=CONFIG.seed))
    if kind == "hang":
        return Scenario(
            id=f"hang_{hau_to}k{level}", group="hang", level=level,
            description=f"{len(targets)} thanh phan treo qua han chot: {ten}",
            make_injector=lambda t=targets: HangInjector(targets=t, delay=20.0),
            deadline_ms=10.0)
    if kind == "byzantine_gross":
        return Scenario(
            id=f"byz_gross_{hau_to}k{level}", group="byzantine_gross", level=level,
            description=f"{len(targets)} thanh phan tra hang so: {ten}",
            make_injector=lambda t=targets: ConstantOutputInjector(
                targets=t, field_name="risk_score", constant=0.5))
    raise ValueError(f"kieu hong khong biet: {kind}")


# Giai doan 1: chi ba nhom hong theo thanh phan. `drift` va `bias` ap o tang case
# nen chung khong doi theo giai doan — chay lai chung o day chi nhan doi con so.
STAGE1_SCENARIOS: tuple[Scenario, ...] = tuple(
    _kich_ban(kind, level, ESCALATION_STAGE1[:level], "s1_")
    for kind in ("crash", "hang", "byzantine_gross")
    for level in (1, 2, 3)
)

def _byz_mas_only(level: int, n: int) -> Scenario:
    """Byzantine tren be mat chi-MAS, dau doc DUNG truong tung thanh phan phat ra.

    KHONG dung `ConstantOutputInjector` o day. No gan cung ten truong `risk_score`,
    ma khong thanh phan nao trong nhom nay phat ra truong do — nen phep tiem tro
    thanh mot ham dong nhat va bang ket qua cho `mas_changed = 0,0%`. Con so do
    trong nhu bang chung chiu loi nhung thuc ra la mot phep thu rong. Xem L36.
    """
    thanh_phan = [c for c in ESCALATION_MAS_ONLY if c in MAS_ONLY_POISON][:n]
    bang = {c: MAS_ONLY_POISON[c] for c in thanh_phan}
    return Scenario(
        id=f"byz_gross_masonly_k{level}", group="byzantine_gross", level=level,
        description=("{} thanh phan tra ket qua hop le nhung sai: {}".format(
            len(thanh_phan), ", ".join(f"{c}.{f}" for c, (f, _) in bang.items()))),
        make_injector=lambda b=bang: ByzantineByComponent(field_by_component=b))


# Nam thanh phan chi MAS moi co — nhung `case_manager` KHONG nam trong ke hoach nao
# (STAGE1_PLAN va STAGE2_PLAN deu khong goi no), nen thang do leo dung lai o BON
# thanh phan goi duoc. Dua vao mot thanh phan khong bao gio chay chi lam bang ket
# qua trong day dan hon thuc te.
MAS_ONLY_SCENARIOS: tuple[Scenario, ...] = tuple([
    *(_kich_ban(kind, level, ESCALATION_MAS_ONLY[:n], "masonly_")
      for kind in ("crash", "hang")
      for level, n in ((1, 1), (2, 3), (3, 5))),
    *(_byz_mas_only(level, n) for level, n in ((1, 1), (2, 3), (3, 4))),
])


ALL_SCENARIOS: tuple[Scenario, ...] = (
    _crash(1), _crash(2), _crash(3),
    _hang(1), _hang(2), _hang(3),
    _byzantine_gross(1), _byzantine_gross(2), _byzantine_gross(3),
    _drift(1, 0.05), _drift(2, 0.10), _drift(3, 0.20),
    _bias(1, 0.05), _bias(2, 0.15), _bias(3, 0.30),
)

HEALTHY = Scenario(
    id="healthy", group="healthy", level=0,
    description="khong tiem loi — duong co so de do ty le bao dong gia",
    make_injector=NullInjector,
)

DESIGNED_FOR["healthy"] = False


def by_group(group: str) -> tuple[Scenario, ...]:
    return tuple(s for s in ALL_SCENARIOS if s.group == group)


def groups() -> tuple[str, ...]:
    return ("crash", "hang", "byzantine_gross", "drift", "bias")
