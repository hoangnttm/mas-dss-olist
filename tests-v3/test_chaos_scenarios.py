"""WP9 / T9.2 — Danh muc 5 nhom loi x 3 muc, va dinh nghia hong am tham.

Phuc vu: RQ1(a), RQ1(b).
"""

from __future__ import annotations

import asyncio

import pytest

from masdss.chaos.injector import (
    BiasInjector,
    ConstantOutputInjector,
    CrashInjector,
    HangInjector,
    NullInjector,
    drift_cases,
)
from masdss.chaos.runner import Baseline, _mas_key
from masdss.chaos.scenarios import ALL_SCENARIOS, HEALTHY, by_group, groups
from masdss.config import deterministic_uuid
from masdss.core.components import Component
from masdss.core.errors import AgentTimeout, DeterministicError
from masdss.core.message import Message, Performative, new_request
from masdss.core.ontology import DecisionPoint, OrderCase
from masdss.runtime.faults import invoke


def _case(case_id: str = "c1", **features) -> OrderCase:
    base = {"delivery_delay_days": 5.0, "freight_ratio": 0.2, "price": 100.0,
            "freight_value": 10.0, "delivery_days": 12.0, "carrier_handover_days": 2.0}
    base.update(features)
    return OrderCase(case_id=case_id, decision_point=DecisionPoint.T4, features=base)


# =============== Danh muc kich ban ===============

def test_catalogue_has_five_groups_of_three_levels() -> None:
    assert len(ALL_SCENARIOS) == 15
    for group in groups():
        levels = sorted(s.level for s in by_group(group))
        assert levels == [1, 2, 3], f"nhom {group} co muc {levels}"


def test_scenario_ids_are_unique() -> None:
    ids = [s.id for s in ALL_SCENARIOS]
    assert len(ids) == len(set(ids))


def test_designed_for_separates_specification_check_from_real_result() -> None:
    """Phan biet nay phai duoc giu khi viet Chuong 5.

    Bao cao "guard bat duoc loi crash" nhu mot phat hien la tu lua — ta viet guard
    de bat no. Chi nhom `designed_for = False` moi mang thong tin moi.
    """
    designed = {s.group for s in ALL_SCENARIOS if s.designed_for}
    discovered = {s.group for s in ALL_SCENARIOS if not s.designed_for}
    assert designed == {"crash", "hang", "byzantine_gross"}
    assert discovered == {"drift", "bias"}


def test_escalating_levels_touch_more_components() -> None:
    """Muc do tang nghia la nhieu thanh phan bi anh huong hon."""
    for group in ("crash", "hang", "byzantine_gross"):
        sizes = [len(s.targets) for s in sorted(by_group(group), key=lambda s: s.level)]
        assert sizes == [1, 2, 3], f"{group}: {sizes}"


def test_drift_is_not_a_component_injector() -> None:
    """Drift la thuoc tinh cua DONG DU LIEU VAO, khong phai hanh vi sai cua mot
    thanh phan — nen no khong duoc mo hinh hoa nhu bo tiem theo thanh phan."""
    for scenario in by_group("drift"):
        assert scenario.drift > 0
        assert scenario.targets == (), "drift khong duoc nham vao thanh phan nao"


def test_healthy_scenario_injects_nothing() -> None:
    assert isinstance(HEALTHY.make_injector(), NullInjector)
    assert HEALTHY.drift == 0.0


# =============== Nhom 1: crash ===============

def test_crash_hits_only_its_targets() -> None:
    injector = CrashInjector(targets=(Component.PREDICTION.value,), seed=0)
    with pytest.raises(DeterministicError):
        injector.before(Component.PREDICTION.value)
    assert injector.before(Component.CAUSE_SERVICE.value) is None


def test_crash_can_hit_multiple_components() -> None:
    targets = (Component.PREDICTION.value, Component.CAUSE_DELIVERY.value)
    injector = CrashInjector(targets=targets, seed=0)
    for component in targets:
        with pytest.raises(DeterministicError):
            injector.before(component)


# =============== Nhom 2: hang ===============

class _SlowAgent:
    agent_id = "Prediction"

    async def handle(self, message: Message) -> Message:
        return message.reply(sender=self.agent_id, performative=Performative.INFORM,
                             content={"risk": 1}, ontology="prediction")


def test_hang_produces_a_real_timeout() -> None:
    """Do tre nam BEN TRONG pham vi wait_for, nen task bi HUY that.

    Ban v0 do latency SAU khi tac tu chay xong, nen mot tac tu treo lam treo ca
    pipeline vinh vien. Day la kich ban chung minh khac biet do.
    """
    conv = deterministic_uuid("test", "hang")
    message = new_request(conversation_id=conv, sender="Orchestrator",
                          receiver="Prediction", content={"step": "t"},
                          seq=1, deadline_ms=10.0)
    injector = HangInjector(targets=(Component.PREDICTION.value,), delay=60.0)

    with pytest.raises(AgentTimeout):
        asyncio.run(invoke(_SlowAgent(), message, injector=injector))


def test_hang_leaves_untargeted_components_alone() -> None:
    injector = HangInjector(targets=(Component.CAUSE_SERVICE.value,), delay=60.0)
    assert injector.delay_ms(Component.PREDICTION.value) == 0.0
    assert injector.delay_ms(Component.CAUSE_SERVICE.value) == 60.0


# =============== Nhom 3 va 5: dau doc dau ra ===============

def _reply(**content) -> Message:
    conv = deterministic_uuid("test", "reply")
    return Message(msg_id=conv, conversation_id=conv, trace_id=conv,
                   sender="Prediction", receiver="Orchestrator",
                   performative=Performative.INFORM, ontology="prediction",
                   content=content)


def test_constant_injector_poisons_message_and_raw_value() -> None:
    """Hai kien truc bieu dien ket qua khac nhau — bo tiem phai xu ly ca hai."""
    injector = ConstantOutputInjector(targets=(Component.PREDICTION.value,),
                                      field_name="risk_score", constant=0.5)
    poisoned = injector.after(Component.PREDICTION.value, _reply(risk_score=0.9))
    assert poisoned.content["risk_score"] == 0.5

    # Monolithic: capability tra (confidence, evidence)
    assert injector.after(Component.PREDICTION.value, (0.9, ()))[0] == 0.5


def test_bias_injector_clamps_to_unit_interval() -> None:
    injector = BiasInjector(targets=(Component.PREDICTION.value,), delta=0.5)
    assert injector.after(Component.PREDICTION.value, _reply(risk_score=0.8)) \
        .content["risk_score"] == 1.0


# =============== Nhom 4: drift ===============

def test_drift_shifts_features_progressively() -> None:
    """Drift tich luy dan, khong phai mot cu soc tuc thoi."""
    cases = [_case(f"c{i}") for i in range(100)]
    drifted = drift_cases(cases, magnitude=0.5, seed=0)

    first = drifted[0].features["delivery_delay_days"]
    last = drifted[-1].features["delivery_delay_days"]
    assert abs(last - 5.0) > abs(first - 5.0), "drift phai tang dan theo thu tu case"


def test_drift_is_deterministic() -> None:
    cases = [_case(f"c{i}") for i in range(50)]
    a = drift_cases(cases, 0.2, seed=7)
    b = drift_cases(cases, 0.2, seed=7)
    assert [c.features["delivery_delay_days"] for c in a] == \
           [c.features["delivery_delay_days"] for c in b]


def test_zero_drift_returns_cases_unchanged() -> None:
    cases = [_case("c1")]
    assert drift_cases(cases, 0.0) is cases


def test_drift_preserves_case_identity() -> None:
    cases = [_case(f"c{i}") for i in range(20)]
    drifted = drift_cases(cases, 0.3, seed=1)
    assert [c.case_id for c in drifted] == [c.case_id for c in cases]


# =============== Dinh nghia hong am tham (v3) ===============

def _decision(case_id: str, action: str, causes: list[str], risk: int = 1,
              degradation: int = 0, human: bool = False) -> dict:
    return {"case_id": case_id, "action": action, "risk": risk,
            "causes": [{"cause": c, "probability": 0.8} for c in causes],
            "degradation_level": degradation, "needs_human_review": human}


def test_identical_output_is_not_a_silent_failure() -> None:
    """Bai hoc tu nhom `hang`: mot lan goi bi treo lam he CHAM di, khong lam SAI.

    Dinh nghia truoc do dem moi case khong chuyen giao la hong am tham, nen bao
    Monolithic 28,5% trong khi moi quyet dinh cua no van dung y het duong khoe.
    """
    healthy = [_decision("c1", "partial_refund", ["price"])]
    baseline = Baseline.of(healthy, [{"case_id": "c1",
                                      "monolithic": {"action": "partial_refund",
                                                     "causes": ["price"], "risk": 1}}])
    assert baseline.mas["c1"] == _mas_key(healthy[0])


def test_changed_output_without_warning_is_a_silent_failure() -> None:
    healthy = [_decision("c1", "partial_refund", ["price"])]
    baseline = Baseline.of(healthy, [])

    faulty = _decision("c1", "no_action", [])
    changed = baseline.mas["c1"] != _mas_key(faulty)
    warned = faulty["degradation_level"] > 0 or faulty["needs_human_review"] \
        or faulty["action"] == "escalate_to_human"
    assert changed and not warned


def test_changed_output_with_warning_is_not_silent() -> None:
    healthy = [_decision("c1", "partial_refund", ["price"])]
    baseline = Baseline.of(healthy, [])

    faulty = _decision("c1", "escalate_to_human", [], degradation=2, human=True)
    changed = baseline.mas["c1"] != _mas_key(faulty)
    warned = faulty["degradation_level"] > 0 or faulty["needs_human_review"]
    assert changed and warned


def test_decision_key_ignores_warning_fields() -> None:
    """Khoa so sanh phai la phan NOI DUNG, khong gom co canh bao.

    Neu gom, moi quyet dinh bi danh dau suy giam se tu dong "khac" duong khoe va
    phep do mat y nghia.
    """
    a = _decision("c1", "partial_refund", ["price"], degradation=0, human=False)
    b = _decision("c1", "partial_refund", ["price"], degradation=2, human=True)
    assert _mas_key(a) == _mas_key(b)


# --------------------------------------------------------------------------
# L36 — mot bo tiem KHONG cham duoc muc tieu cho ra bang so giong het mot he
# chiu loi hoan hao. Bon test duoi canh cho khoang cach do.
# --------------------------------------------------------------------------

def _message(sender: str, content: dict):
    from masdss.core.message import Message, Performative
    return Message(
        msg_id="m1", conversation_id="c1", trace_id="t1", sender=sender,
        receiver="Orchestrator", performative=Performative.INFORM,
        ontology="order_case", content=dict(content), in_reply_to=None,
        deadline_ms=1000.0, seq=1)


def test_bo_tiem_cu_KHONG_cham_duoc_thanh_phan_chi_MAS():
    """Tai lap dung loi L36 — day la ly do `ByzantineByComponent` ton tai.

    Test nay khang dinh mot HAN CHE, khong phai mot tinh nang. Neu ai do sua
    `ConstantOutputInjector` cho no dau doc duoc moi truong, test nay do va do la
    tin hieu dung: khi ay `ByzantineByComponent` khong con can thiet nua.
    """
    from masdss.chaos.injector import ConstantOutputInjector

    tiem = ConstantOutputInjector(targets=("critic",), field_name="risk_score",
                                  constant=0.5)
    goc = _message("PolicyCritic", {"challenged": True, "violated": ["x"]})
    assert tiem.after("critic", goc).content == goc.content, (
        "neu phep tiem nay da cham duoc thi L36 khong the xay ra")


def test_byzantine_theo_thanh_phan_THUC_SU_doi_dau_ra():
    """Bang chung rang phep tiem cham duoc — dieu ma lan chay dau khong co."""
    from masdss.chaos.injector import MAS_ONLY_POISON, ByzantineByComponent

    tiem = ByzantineByComponent(field_by_component=MAS_ONLY_POISON)
    goc = _message("PolicyCritic", {"challenged": True, "violated": ["x"]})
    sau = tiem.after("critic", goc)
    assert sau.content["challenged"] is False, "bo phan bien phai bi lam im lang"
    assert sau.content["violated"] == ["x"], "chi truong duoc chi dinh moi bi doi"


def test_moi_thanh_phan_chi_MAS_deu_bi_dau_doc_o_truong_NO_THUC_SU_phat_ra():
    """Ten truong doc tu nhat ky message that, khong doan tu ten lop."""
    from masdss.chaos.injector import MAS_ONLY_POISON, ByzantineByComponent

    that = {"analytics": "context", "recommendation": "proposal",
            "critic": "challenged", "arbiter": "sided_with"}
    tiem = ByzantineByComponent(field_by_component=MAS_ONLY_POISON)
    for thanh_phan, truong in that.items():
        goc = _message("X", {truong: "GIA_TRI_GOC"})
        assert tiem.after(thanh_phan, goc).content[truong] != "GIA_TRI_GOC", (
            f"`{thanh_phan}` khong bi dau doc o truong `{truong}`")


def test_case_manager_KHONG_nam_trong_be_mat_hong_dem_duoc():
    """No khong co trong ke hoach nao, nen no khong hong duoc — dem no la dem thua."""
    from masdss.chaos.injector import MAS_ONLY_POISON
    from masdss.system.plan import STAGE1_PLAN, STAGE2_PLAN

    goi_duoc = {s.agent for s in (*STAGE1_PLAN, *STAGE2_PLAN) if s.agent}
    assert "CaseManager" not in goi_duoc
    assert "case_manager" not in MAS_ONLY_POISON
