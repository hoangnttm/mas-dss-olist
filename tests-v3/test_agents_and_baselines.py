"""WP6, WP4 — Tac tu that va tap baseline.

Phuc vu: RQ2 (chuoi quyet dinh), RQ3 (dau thau va quyen tu choi),
         RQ1 (tinh cong bang cua phep so sanh).
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
from masdss.baselines.monolithic import MonolithicComplete, is_silent_failure
from masdss.baselines.simple import MISBaseline, SingleMLBaseline
from masdss.capabilities.cause_head import LexiconCauseHead
from masdss.capabilities.delivery_signal import DeliverySignal
from masdss.capabilities.price_signal import PriceSignal
from masdss.capabilities.rules import RuleEngine
from masdss.config import deterministic_uuid
from masdss.core.message import Performative, new_request
from masdss.core.ontology import Cause, DecisionPoint, OrderCase

CONV = deterministic_uuid("test", "agents")


def _train() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    n = 200
    return pd.DataFrame({
        "category": ["toys"] * n,
        "freight_ratio": rng.normal(0.2, 0.05, n),
        "delivery_delay_days": rng.normal(-10, 5, n),
    })


def _case(*, text: str | None = None, delay: float = 20.0,
          freight: float = 0.2, price: float = 100.0) -> OrderCase:
    return OrderCase(
        case_id="c1", decision_point=DecisionPoint.T4,
        features={"category": "toys", "freight_ratio": freight,
                  "delivery_delay_days": delay, "price": price, "freight_value": 10.0},
        review_text=text,
    )


def _ask(agent, case):
    message = new_request(conversation_id=CONV, sender="Orchestrator",
                          receiver=agent.agent_id, content={"step": "t"},
                          seq=1, payload=case)
    return asyncio.run(agent.handle(message))


# =============== T6.6 Analyst pool ===============

def test_delivery_analyst_bids_with_evidence() -> None:
    """Bid khong duoc phep la con so tran — phai kem bang chung kiem chung duoc."""
    agent = DeliveryAnalyst(DeliverySignal().fit(_train()))
    reply = _ask(agent, _case(delay=40.0))
    assert reply.performative is Performative.PROPOSE
    assert reply.content["cause"] == Cause.DELIVERY.value
    assert reply.content["evidence"][0]["kind"] == "delivery_delay"


def test_text_analysts_refuse_on_tier_b() -> None:
    """Tang B (25,23% don) khong co van ban — day la tinh huong kho (b) cua RQ3."""
    head = LexiconCauseHead()
    for agent in (QualityAnalyst(head), ServiceAnalyst(head)):
        reply = _ask(agent, _case(text=None))
        assert reply.performative is Performative.REFUSE
        assert "tang B" in reply.content["reason"]


def test_quality_analyst_bids_on_matching_text() -> None:
    agent = QualityAnalyst(LexiconCauseHead())
    reply = _ask(agent, _case(text="produto chegou quebrado"))
    assert reply.performative is Performative.PROPOSE
    assert reply.content["cause"] == Cause.QUALITY.value


def test_analyst_never_bids_outside_its_cause() -> None:
    """Moi analyst phu trach DUNG mot nguyen nhan — dieu kien de bid_entropy co nghia."""
    head = LexiconCauseHead()
    agent = ServiceAnalyst(head)
    reply = _ask(agent, _case(text="produto chegou quebrado"))  # tin hieu quality
    assert reply.performative is Performative.REFUSE




def test_agents_stay_thin() -> None:
    """Vuot ~80 dong la dau hieu logic bi dat sai tang (technical-plan-v3 §3)."""
    import inspect

    from masdss.agents import core_agents
    from masdss.agents.analysts import pool

    for module in (pool, core_agents):
        for name, obj in vars(module).items():
            if not (inspect.isclass(obj) and obj.__module__ == module.__name__):
                continue
            lines = len(inspect.getsource(obj).splitlines())
            assert lines <= 80, f"{name} dai {lines} dong — kiem tra xem co logic dat sai tang"


# =============== WP4 baseline ===============

@pytest.fixture(scope="module")
def capabilities():
    from dataclasses import dataclass

    @dataclass
    class Caps:
        risk_model: object
        ood: object
        delivery: object
        price: object
        cause_head: object
        rules: object

    class StubRisk:
        cost_ms = 0.5

        def can_handle(self, case):
            return True

        def run(self, case):
            return 0.8

        @staticmethod
        def to_risk_level(p):
            from masdss.core.ontology import RiskLevel

            return RiskLevel.HIGH if p >= 0.7 else RiskLevel.LOW

    return Caps(
        risk_model=StubRisk(), ood=None,
        delivery=DeliverySignal().fit(_train()),
        price=PriceSignal().fit(_train()),
        cause_head=LexiconCauseHead(),
        rules=RuleEngine.load(),
    )


def test_baseline_shares_the_same_capability_objects(capabilities) -> None:
    """Dieu kien cong bang: khong phai cung lop, khong phai cung tham so — CUNG DOI TUONG."""
    mono = MonolithicComplete(capabilities)
    single = SingleMLBaseline(capabilities)

    assert mono.risk_model is capabilities.risk_model
    assert single.risk_model is capabilities.risk_model
    assert mono.delivery is capabilities.delivery
    assert mono.price is capabilities.price
    assert mono.cause_head is capabilities.cause_head
    assert mono.rules is capabilities.rules


def test_monolithic_is_multi_label(capabilities) -> None:
    """Doi chung PHAI da nhan.

    Neu no bi chan chi tra mot nhan, MAS-DSS thang o tinh huong (a) cua RQ3 THEO
    CAU TAO — dung loi baseline bu nhin ma nghien cuu da cam ket tranh.
    """
    result = MonolithicComplete(capabilities).run(
        _case(text="produto chegou quebrado, atraso enorme", delay=40.0)
    )
    assert len(result.causes) >= 2


def test_monolithic_has_no_degradation_concept(capabilities) -> None:
    """Kien truc doi chung khong co truong nao bao rang mot phan he thong da hong."""
    row = MonolithicComplete(capabilities).run(_case()).to_row()
    assert "degradation_level" not in row
    assert "needs_human_review" not in row


def test_silent_failure_definition(capabilities) -> None:
    from masdss.baselines.monolithic import MonolithicResult

    healthy = MonolithicResult("c1", 2, ["delivery"], "preemptive_ticket_open", [])
    broken = MonolithicResult("c2", 0, [], "no_action", ["prediction"])
    assert not is_silent_failure(healthy)
    assert is_silent_failure(broken)


def test_mis_baseline_uses_no_model() -> None:
    mis = MISBaseline(delay_threshold=3.0)
    assert mis.run(_case(delay=10.0)).flagged
    assert not mis.run(_case(delay=1.0)).flagged
    assert mis.run(_case()).risk is None


# =============== Cam argmax ===============

def test_no_argmax_in_attribution_path() -> None:
    """`idxmax` thien vi theo thu tu bang chu cai khi hoa diem — bug that trong ban v0."""
    import ast
    from pathlib import Path

    src = Path(__file__).resolve().parents[1] / "src-v3" / "masdss"
    targets = [
        *(src / "agents").rglob("*.py"),
        src / "baselines" / "monolithic.py",
        src / "system" / "app.py",
    ]
    offenders: list[str] = []
    for file in targets:
        tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if name in {"argmax", "idxmax"}:
                offenders.append(f"{file.name}:{node.lineno}")
    assert not offenders, f"phep argmax trong duong quy ket nguyen nhan: {offenders}"


def test_placeholder_cause_head_is_flagged() -> None:
    """Ban tam thoi phai tu khai bao la tam thoi, de khong ai trich so tu no."""
    assert LexiconCauseHead().is_placeholder is True
