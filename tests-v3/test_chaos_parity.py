"""WP9 / T9.3 — Giao thuc so sanh: CUNG kich ban loi tren HAI kien truc.

Phuc vu: RQ1(a).

Neu mot kich ban chi ap duoc len mot kien truc thi hai con so hong am tham khong
so sanh duoc voi nhau, va RQ1(a) khong tra loi duoc. Cac test o day canh dung dieu
kien do.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from masdss.baselines.monolithic import CAUSE_COMPONENT, MonolithicComplete
from masdss.capabilities.cause_head import LexiconCauseHead
from masdss.capabilities.delivery_signal import DeliverySignal
from masdss.capabilities.price_signal import PriceSignal
from masdss.capabilities.rules import RuleEngine
from masdss.core.components import AGENT_TO_COMPONENT, Component, normalize_target
from masdss.chaos.injector import BiasInjector, ConstantOutputInjector, CrashInjector
from masdss.core.ontology import DecisionPoint, OrderCase
from masdss.evaluation.resilience import (
    monolithic_silent_failures,
    mas_silent_failures,
)


def _train() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    n = 200
    return pd.DataFrame({
        "category": ["toys"] * n,
        "freight_ratio": rng.normal(0.2, 0.05, n),
        "delivery_delay_days": rng.normal(-10, 5, n),
    })


def _case() -> OrderCase:
    return OrderCase(
        case_id="c1", decision_point=DecisionPoint.T4,
        features={"category": "toys", "freight_ratio": 0.2,
                  "delivery_delay_days": 30.0, "price": 100.0, "freight_value": 10.0},
        review_text="produto chegou quebrado",
    )


class _Caps:
    def __init__(self) -> None:
        class Risk:
            cost_ms = 0.5
            # Nguong phai co that o ban gia lap: `PredictionAgent` gui kem chung trong
            # thong diep de bo tiem loi suy lai duoc muc rui ro sau khi dau doc diem.
            # Mot ban gia lap thieu chung se lam chinh phep kiem tra cong bang o duoi
            # tro thanh phep thu rong.
            risk_thresholds = (0.3, 0.7)

            def can_handle(self, case):
                return True

            def run(self, case):
                return 0.8

            @staticmethod
            def to_risk_level(p):
                from masdss.core.ontology import RiskLevel

                return RiskLevel.HIGH if p >= 0.7 else RiskLevel.LOW

        self.risk_model = Risk()
        self.ood = None
        self.delivery = DeliverySignal().fit(_train())
        self.price = PriceSignal().fit(_train())
        self.cause_head = LexiconCauseHead()
        self.rules = RuleEngine.load()


# --- Anh xa thanh phan ---

def test_every_agent_maps_to_a_component() -> None:
    """Tac tu khong duoc anh xa se khien kich ban chi ap duoc len MAS-DSS."""
    from masdss.system.app import build_registry

    registry = build_registry(_Caps())
    agent_ids = set(registry._agents) | {a.agent_id for a in registry.pool("AnalystPool")}
    missing = agent_ids - set(AGENT_TO_COMPONENT)
    assert not missing, f"tac tu chua co thanh phan logic tuong ung: {sorted(missing)}"


def test_monolithic_covers_the_same_components() -> None:
    """BA nguyen nhan cua Monolithic phai trung ten voi BA Analyst cua MAS-DSS.

    So luong giam tu bon xuong ba khi nhan `price` bi go (12/08). Dieu duoc canh
    khong doi: hai kien truc phai dung CHUNG mot he dinh danh thanh phan, neu khong
    mot kich ban tiem loi khong ap duoc len ca hai (loi L12).
    """
    mono_components = set(CAUSE_COMPONENT.values())
    mas_components = {
        AGENT_TO_COMPONENT[a].value
        for a in ("DeliveryAnalyst", "QualityAnalyst", "ServiceAnalyst")
    }
    assert mono_components == mas_components


def test_agent_name_and_component_name_both_accepted() -> None:
    assert normalize_target("Prediction") == Component.PREDICTION.value
    assert normalize_target("prediction") == Component.PREDICTION.value


# --- Tiem loi ap duoc len Monolithic ---

def test_crash_reaches_monolithic() -> None:
    caps = _Caps()
    injector = CrashInjector(targets=(Component.PREDICTION.value,), seed=0)
    result = MonolithicComplete(caps, injector).run(_case())
    assert "prediction" in result.failed_steps


def test_crash_on_analyst_reaches_monolithic() -> None:
    caps = _Caps()
    injector = CrashInjector(targets=(Component.CAUSE_DELIVERY.value,), seed=0)
    result = MonolithicComplete(caps, injector).run(_case())
    assert "cause_delivery" in result.failed_steps


def test_byzantine_leaves_no_trace_of_failure() -> None:
    """Diem mau chot: loi Byzantine KHONG sinh ra `failed_steps` nao.

    Day chinh la ly do dinh nghia "hong am tham" khong duoc dua tren viec he thong
    tu bao cao la no hong.
    """
    caps = _Caps()
    injector = ConstantOutputInjector(targets=(Component.CAUSE_DELIVERY.value,),
                                      field_name="confidence", constant=0.99)
    result = MonolithicComplete(caps, injector).run(_case())
    assert result.failed_steps == []
    assert "delivery" in result.causes  # da bi dau doc ma khong ai biet


def test_bias_injector_shifts_capability_output() -> None:
    """Bid lech he thong phai day duoc mot nguyen nhan tu duoi nguong len tren.

    `_case()` co van ban "produto chegou quebrado" nen sach se chi ra `delivery` va
    `quality`; `service` khong co tin hieu nao. Tiem lech vao `cause_service` phai
    lam no xuat hien — do la ca hong AM THAM: khong exception, khong canh bao, chi
    mot nguyen nhan sai duoc them vao quyet dinh.
    """
    caps = _Caps()
    clean = MonolithicComplete(caps).run(_case())
    biased = MonolithicComplete(
        caps, BiasInjector(targets=(Component.CAUSE_SERVICE.value,),
                           field_name="confidence", delta=0.9)
    ).run(_case())
    assert "service" not in clean.causes
    assert "service" in biased.causes


def test_tiem_loi_byzantine_phai_cham_DUONG_QUYET_DINH_cua_ca_hai_kien_truc() -> None:
    """Khong du de loi "cham" ca hai kien truc — no phai cham DUONG QUYET DINH ca hai.

    LO HONG NAY DA CO THAT, va no lam sai lech dung con so trung tam cua RQ1.

        `PredictionAgent` phat ra HAI truong: `risk_score` (diem tho) va `risk` (muc
        da suy ra). `ConstantOutputInjector` chi dau doc `risk_score`, con
        `reduce_reply` lai doc `risk` de dung quyet dinh. Hau qua:

            MAS-DSS     — `risk_score` bi dau doc, nhung `risk` KHONG DOI
                          => quyet dinh KHONG bi anh huong
            Monolithic  — `guard_call` boc `risk_model.run` tra ve mot SO tran, nen
                          bo tiem thay the nguyen gia tri => quyet dinh BI anh huong

        Do duoc tren 200 case, kich ban `byz_gross_k2`, tang chiu loi TAT:
            phan bo muc rui ro cua MAS   : {0: 122, 1: 50, 2: 28} — Y HET duong khoe
            phan bo muc rui ro cua Mono  : {2: 200}               — hong toan bo

        Nghia la "MAS-DSS hong am tham 0,0%" o nhom byzantine KHONG chung minh kha
        nang chiu loi — no chi phan anh viec loi chua bao gio toi duoc quyet dinh.
        Phep so sanh o nhom nay bi nhieu boi CHO DAT BO TIEM, dung loai loi ma L12 da
        canh bao va nghien cuu da cam ket tranh.

    Bai kiem thu nay canh dieu kien toi thieu de phep so sanh con nghia: mot kich ban
    Byzantine tiem vao `prediction` phai lam DOI muc rui ro ma quyet dinh thuc su
    dung, o CA HAI kien truc.
    """
    import asyncio
    from uuid import uuid4

    from masdss.agents.core_agents import PredictionAgent
    from masdss.core.message import Performative, new_request

    caps = _Caps()
    case = _case()

    sach = MonolithicComplete(caps).run(case)
    injector = ConstantOutputInjector(targets=(Component.PREDICTION.value,),
                                      field_name="risk_score", constant=0.5)
    hong = MonolithicComplete(caps, injector).run(case)
    assert hong.risk != sach.risk, "bo tiem khong cham duoc duong quyet dinh cua don khoi"

    # Phia MAS-DSS: dung chinh thong diep ma `PredictionAgent` phat ra.
    agent = PredictionAgent(caps.risk_model, caps.ood)
    yeu_cau = new_request(conversation_id=uuid4(), sender="Orchestrator",
                          receiver=agent.agent_id, ontology="cfp",
                          content={"step": "prediction"}, payload=case,
                          performative=Performative.REQUEST)
    tra_loi = asyncio.run(agent.handle(yeu_cau))
    truoc = tra_loi.content.get("risk")
    sau = injector.after(Component.PREDICTION.value, tra_loi).content.get("risk")

    assert sau != truoc, (
        "Bo tiem Byzantine dau doc `risk_score` nhung quyet dinh cua MAS-DSS doc "
        "`risk` — loi khong toi duoc duong quyet dinh. Con so 'hong am tham 0,0%' o "
        "nhom byzantine vi vay KHONG so sanh duoc voi don khoi."
    )


# --- Dinh nghia hong am tham ---

def test_silent_failure_requires_injection_ground_truth() -> None:
    """Khong tiem loi thi khong the co hong am tham — du he co ra quyet dinh gi."""
    decisions = [{"degradation_level": 0, "needs_human_review": False, "action": "x"}]
    report = mas_silent_failures(decisions, injected=None)
    assert report.n_exposed == 0
    assert report.rate == 0.0


def test_silent_failure_is_not_based_on_self_report() -> None:
    """Mot he hong am tham luon TU BAO CAO la binh thuong.

    Duoi loi Byzantine, `failed_steps` rong nhung case van phai bi tinh la hong am
    tham — vi ta BIET da tiem loi vao thanh phan nam tren duong thuc thi.
    """
    rows = [{"monolithic": {"action": "partial_refund", "failed_steps": []}}] * 10
    report = monolithic_silent_failures(rows, injected=Component.PREDICTION.value)
    assert report.n_silent == 10


def test_escalation_is_not_a_silent_failure() -> None:
    rows = [{"monolithic": {"action": "escalate_to_human", "failed_steps": ["prediction"]}}]
    report = monolithic_silent_failures(rows, injected=Component.PREDICTION.value)
    assert report.n_silent == 0


def test_mas_degradation_marker_counts_as_a_warning() -> None:
    decisions = [
        {"degradation_level": 2, "needs_human_review": True, "action": "escalate_to_human"},
        {"degradation_level": 0, "needs_human_review": False, "action": "partial_refund"},
    ]
    report = mas_silent_failures(decisions, injected=Component.PREDICTION.value)
    assert report.n_silent == 1  # chi case thu hai
