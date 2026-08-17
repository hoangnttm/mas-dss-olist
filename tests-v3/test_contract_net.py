"""WP7 / T7.1, T7.2 — Contract Net hai pha co rang buoc ngan sach.

Phuc vu: RQ3 — day la co che khien giao thuc load-bearing thay vi "ensemble doi lot".

Don phan bien can tra loi: "bon analyst cung lam mot viec, orchestrator lay argmax —
do la softmax co gan nhan giao thuc". Cac test o day canh dung ba dieu kien lam cho
phan bien do khong con dung:

    1. Ban khai o pha 1 KHONG chay capability dat
    2. Ngan sach THUC SU loai bot analyst khi chi phi vuot han muc
    3. Ket qua phan bo TAT DINH, khong phu thuoc thu tu duyet
"""

from __future__ import annotations

import asyncio

import numpy as np
import pandas as pd
import pytest

from masdss.agents.analysts.pool import (
    DeliveryAnalyst,
    QualityAnalyst,
    ServiceAnalyst,
)
from masdss.capabilities.cause_head import LexiconCauseHead
from masdss.capabilities.delivery_signal import DeliverySignal
from masdss.capabilities.price_signal import PriceSignal
from masdss.config import deterministic_uuid
from masdss.core.message import Performative, new_request
from masdss.core.ontology import Declaration, DecisionPoint, OrderCase
from masdss.system.contract_net import allocate, budget_binds

CONV = deterministic_uuid("test", "cnp")


def _train(n: int = 300) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "category": ["toys"] * n,
        "freight_ratio": rng.normal(0.2, 0.06, n),
        "delivery_delay_days": rng.normal(0.0, 10.0, n),
    })


def _case(text: str | None = "produto chegou quebrado") -> OrderCase:
    return OrderCase(
        case_id="c1", decision_point=DecisionPoint.T4,
        features={"category": "toys", "freight_ratio": 0.55,
                  "delivery_delay_days": 30.0, "price": 100.0, "freight_value": 10.0},
        review_text=text,
    )


def _cfp(agent_id: str, case: OrderCase):
    return new_request(conversation_id=CONV, sender="Orchestrator", receiver=agent_id,
                       content={"step": "contract_net"}, seq=1, payload=case,
                       performative=Performative.CFP)


def _decl(agent_id: str, gain: float, cost: float, evidence: bool = True) -> Declaration:
    return Declaration(agent_id=agent_id, expected_confidence=gain,
                       cost_ms=cost, has_evidence=evidence)


# =============== Bai toan phan bo ===============

def test_budget_excludes_expensive_analyst() -> None:
    """Day la menh de trung tam: ngan sach THUC SU loai bot."""
    declarations = [_decl("Price", 0.6, 0.1), _decl("Delivery", 0.7, 0.3),
                    _decl("Quality", 0.5, 45.0)]
    tight = allocate(declarations, budget_ms=2.0)
    loose = allocate(declarations, budget_ms=120.0)

    assert "Quality" not in tight.accepted, "ngan sach chat phai loai analyst dat"
    assert "Quality" in loose.accepted, "ngan sach rong phai cho phep analyst dat"
    assert set(tight.accepted) == {"Price", "Delivery"}


def test_allocation_maximises_gain_not_just_count() -> None:
    """Toi da hoa LOI ICH, khong phai toi da hoa SO LUONG analyst duoc goi."""
    declarations = [_decl("Cheap1", 0.1, 1.0), _decl("Cheap2", 0.1, 1.0),
                    _decl("Strong", 0.9, 2.0)]
    result = allocate(declarations, budget_ms=2.0)
    assert result.accepted == ("Strong",)


def test_no_evidence_means_no_gain() -> None:
    """`has_evidence` tham gia vao bai toan phan bo, khong phai co trang tri."""
    declarations = [_decl("Delivery", 0.7, 0.3), _decl("Service", 0.9, 0.4, evidence=False)]
    result = allocate(declarations, budget_ms=100.0)
    assert result.accepted == ("Delivery",)
    assert "Service" in result.rejected


def test_allocation_is_deterministic_under_ties() -> None:
    """Hoa diem thi chon tap RE HON; van hoa thi theo bang chu cai.

    Khong co quy tac pha vo the can nay thi ket qua phu thuoc thu tu duyet, va tinh
    tai lap bi pha vo mot cach am tham.
    """
    a = [_decl("Zulu", 0.5, 1.0), _decl("Alpha", 0.5, 1.0)]
    first = allocate(a, budget_ms=1.0)
    second = allocate(list(reversed(a)), budget_ms=1.0)
    assert first.accepted == second.accepted == ("Alpha",)


def test_cheaper_subset_wins_on_equal_gain() -> None:
    """Hoa loi ich thi chon tap RE HON.

    Ngan sach 40ms chi du cho MOT trong hai — neu de 100ms thi lay ca hai lai dung,
    vi loi ich cong don cao hon. Day la mot ky vong sai trong ban dau cua chinh test
    nay, khong phai loi cua thuat toan.
    """
    declarations = [_decl("Cheap", 0.5, 1.0), _decl("Costly", 0.5, 40.0)]
    assert allocate(declarations, budget_ms=40.0).accepted == ("Cheap",)


def test_more_analysts_win_when_budget_allows() -> None:
    """Ngan sach rong thi goi ca hai — nhieu bang chung hon la tot hon."""
    declarations = [_decl("Cheap", 0.5, 1.0), _decl("Costly", 0.5, 40.0)]
    assert allocate(declarations, budget_ms=100.0).accepted == ("Cheap", "Costly")


def test_zero_budget_accepts_nobody() -> None:
    result = allocate([_decl("Delivery", 0.7, 0.3)], budget_ms=0.0)
    assert result.accepted == ()
    assert result.rejected == ("Delivery",)


def test_khong_khai_bao_ngan_sach_KHAC_HAN_ngan_sach_bang_khong() -> None:
    """Hai trang thai NGUOC NHAU ve y nghia, va viec tron chung da gay ra mot loi that.

    Khi rang buoc ngan sach duoc go khoi cau hinh bao cao (14/08), buoc dau thau khong
    con ham `budget`, nen `bb.budget_ms_left` giu mac dinh cu 0,0 va `allocate()` di
    vao nhanh "khong du tien": TU CHOI TOAN BO analyst. Ket qua la 0% case duoc quy
    ket nguyen nhan, trong khi giao thuc van chay du hai pha nen khong co gi bao dong.

    `None` phai co nghia "khong rang buoc" va nhan HET, khong phai nhan KHONG AI.
    """
    declarations = [_decl("Delivery", 0.7, 1.6), _decl("Quality", 0.5, 1.3),
                    _decl("Service", 0.5, 1.3)]

    khong_rang_buoc = allocate(declarations, budget_ms=None)
    assert khong_rang_buoc.accepted == ("Delivery", "Quality", "Service")
    assert khong_rang_buoc.rejected == ()
    assert khong_rang_buoc.budget_ms is None
    assert not budget_binds(declarations, budget_ms=None)

    bang_khong = allocate(declarations, budget_ms=0.0)
    assert bang_khong.accepted == ()


def test_ngan_sach_khong_rang_buoc_khong_ghi_infinity_vao_artifact() -> None:
    """Bang phan bo phai serialise duoc bang JSON chuan.

    Cach cai dat de nghi nhat cho "khong rang buoc" la dat ngan sach bang `math.inf`,
    nhung `json.dumps` khi do sinh ra `Infinity` — mot token KHONG hop le trong JSON
    chuan. `reliability_report.json` la artifact duoc doc lai boi cac buoc sau, nen
    no phai giu dung chuan.
    """
    import json

    row = allocate([_decl("Delivery", 0.7, 1.6)], budget_ms=None).to_row()
    assert row["budget_ms"] is None
    assert json.loads(json.dumps(row, allow_nan=False))["budget_ms"] is None


def test_budget_binds_reports_honestly() -> None:
    """Neu ngan sach khong bao gio rang buoc thi giao thuc khong quyet dinh gi.

    Ham nay ton tai de bao cao trung thuc dieu do thay vi de no am tham — mot phien
    dau thau "chap nhan tat ca" khong chung minh duoc gi ve phan bo tinh toan.
    """
    cheap = [_decl("Price", 0.6, 0.1), _decl("Delivery", 0.7, 0.3)]
    assert not budget_binds(cheap, budget_ms=120.0)
    assert budget_binds(cheap + [_decl("Quality", 0.5, 45.0)], budget_ms=10.0)


def test_utilisation_is_reported() -> None:
    result = allocate([_decl("Delivery", 0.7, 5.0)], budget_ms=10.0)
    assert result.spent_ms == 5.0
    assert result.utilisation == pytest.approx(0.5)


# =============== Pha 1: khai bao khong duoc chay capability ===============

class _CountingHead(LexiconCauseHead):
    """Dem so lan `score()` duoc goi — de bat pha tham do lo chay capability.

    `LexiconCauseHead` la dataclass, va lop con nay khong duoc trang tri lai nen
    `__post_init__` cua no khong duoc goi. Vi vay bo dem duoc khoi tao o muc lop.
    """

    calls: int = 0

    def score(self, case, cause):
        self.calls += 1
        return super().score(case, cause)


def test_declaration_never_runs_the_capability() -> None:
    """RANH GIOI QUAN TRONG NHAT cua giao thuc.

    Neu `declare()` lo goi capability, pha tham do khong con re nua va toan bo bai
    toan phan bo tro nen vo nghia — ta da tra gia truoc khi quyet dinh co tra gia hay
    khong.
    """
    head = _CountingHead()
    agent = QualityAnalyst(head)
    case = _case()

    reply = asyncio.run(agent.handle(_cfp(agent.agent_id, case)))

    assert head.calls == 0, "pha tham do da chay capability — giao thuc mat y nghia"
    assert reply.performative is Performative.PROPOSE
    assert reply.ontology == "declaration"
    assert reply.content["declaration"]["has_evidence"] is True


def test_declaration_reports_no_evidence_on_tier_b() -> None:
    agent = ServiceAnalyst(LexiconCauseHead())
    reply = asyncio.run(agent.handle(_cfp(agent.agent_id, _case(text=None))))
    declaration = reply.content["declaration"]
    assert declaration["has_evidence"] is False
    assert "tang B" in declaration["reason"]


def test_declaration_carries_real_cost() -> None:
    """`cost_ms` phai la chi phi THAT cua capability, khong phai hang so tuy y."""
    head = LexiconCauseHead()
    agent = QualityAnalyst(head)
    reply = asyncio.run(agent.handle(_cfp(agent.agent_id, _case())))
    assert reply.content["declaration"]["cost_ms"] == head.cost_ms


def test_structural_analyst_declares_without_running() -> None:
    signal = DeliverySignal().fit(_train())
    agent = DeliveryAnalyst(signal)
    reply = asyncio.run(agent.handle(_cfp(agent.agent_id, _case())))
    declaration = reply.content["declaration"]
    assert declaration["cost_ms"] == signal.cost_ms
    assert 0.0 < declaration["expected_confidence"] <= 1.0


def test_prior_confidence_is_learned_from_train() -> None:
    """Do tin cay tien nghiem uoc luong tu tap train, khong phai hang so cung."""
    signal = DeliverySignal()
    before = signal.prior_confidence
    signal.fit(_train())
    assert 0.0 < signal.prior_confidence <= 0.95
    assert signal.prior_confidence != before or before == 0.55


# =============== Pha 2: ben thua thau khong chay capability ===============

def test_accept_proposal_runs_the_capability() -> None:
    head = _CountingHead()
    agent = QualityAnalyst(head)
    award = new_request(conversation_id=CONV, sender="Orchestrator",
                        receiver=agent.agent_id, content={"step": "contract_net"},
                        seq=2, payload=_case(),
                        performative=Performative.ACCEPT_PROPOSAL)
    asyncio.run(agent.handle(award))
    assert head.calls == 1, "ben thang thau phai chay capability that"


def test_analyst_declares_refusal_when_capability_lacks_evidence() -> None:
    """`PriceAnalyst` da bi go (12/08) nen test nay chuyen sang `DeliveryAnalyst`.

    Dieu duoc canh khong doi: mot analyst phai khai `has_evidence=False` o pha 1 khi
    nang luc nen cua no khong du du lieu — de bai toan phan bo ngan sach khong cap
    suat cho mot ben chac chan se tu choi o pha 2.
    """
    agent = DeliveryAnalyst(PriceSignal(min_samples=30).fit(_train()))
    case = _case()
    case.features["category"] = "unseen"
    reply = asyncio.run(agent.handle(_cfp(agent.agent_id, case)))
    assert reply.content["declaration"]["has_evidence"] is False
