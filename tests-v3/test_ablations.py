"""WP10 — Hai duong ablation cua RQ2: DP3 (tu choi) va DP4 (nguon goc trace).

Mot Design Principle khong duoc kiem chung thi khong phai dong gop. Hai test file
nay canh cho co che ablation ton tai VA thuc su lam thay doi hanh vi — mot co ablation
khong doi gi la mot co vo dung, va no van "chay duoc".
"""

from __future__ import annotations

import asyncio

import pytest

from masdss.core.message import Performative, new_request
from masdss.core.ontology import Cause, DecisionPoint, OrderCase


class _KhongCoBangChung:
    """Capability luon tra ve rong — dung de ep nhanh REFUSE."""

    name = "trong"
    cost_ms = 1.0
    prior_confidence = 0.5

    def can_handle(self, case) -> bool:
        return False

    def refusal_reason(self, case) -> str:
        return "khong co bang chung"

    def run(self, case):
        return 0.0, ()

    def score(self, case, cause):
        """`CauseHead` dung `score(case, cause)`; `Signal` dung `run(case)`."""
        return 0.0, ()


def _case() -> OrderCase:
    return OrderCase(case_id="c1", decision_point=DecisionPoint.T4, features={},
                     review_text=None)


def _goi(agent, case):
    from uuid import uuid4
    message = new_request(conversation_id=uuid4(), sender="Orchestrator",
                          receiver=agent.agent_id, content={"step": "x"},
                          payload=case)
    return asyncio.run(agent.handle(message))


# --------------------------------------------------------------------------
# DP3 — "tu choi thay vi doan"
# --------------------------------------------------------------------------

def test_dp3_bat_thi_analyst_phat_refuse():
    from masdss.agents.analysts.pool import DeliveryAnalyst

    agent = DeliveryAnalyst(_KhongCoBangChung(), allow_refuse=True)
    reply = _goi(agent, _case())
    assert reply.performative is Performative.REFUSE


def test_dp3_tat_thi_analyst_buoc_phai_doan():
    """Ablation phai THUC SU doi hanh vi, khong chi doi mot co."""
    from masdss.agents.analysts.pool import DeliveryAnalyst

    agent = DeliveryAnalyst(_KhongCoBangChung(), allow_refuse=False)
    reply = _goi(agent, _case())
    assert reply.performative is Performative.PROPOSE
    assert reply.ontology == "bid"
    assert reply.content["cause"] == Cause.DELIVERY.value


def test_dp3_phong_doan_bi_ep_phai_duoc_ghi_ro_trong_bang_chung():
    """Trace khong duoc noi doi ve co so cua quyet dinh.

    Neu he thong bi ep doan ma bang chung khong ghi dieu do, thi trace bao cao mot
    quy ket trong nhu co can cu — dung loai bat trung thuc ma DP1 va DP4 nham chan.
    """
    from masdss.agents.analysts.pool import DeliveryAnalyst

    agent = DeliveryAnalyst(_KhongCoBangChung(), allow_refuse=False)
    reply = _goi(agent, _case())
    kinds = {e["kind"] for e in reply.content["evidence"]}
    assert "forced_guess" in kinds


def test_dp3_phong_doan_phai_vuot_nguong_moi_co_y_nghia():
    """Bid 0,0 se bi arbiter loc va bien ablation thanh vo nghia."""
    from masdss.agents.analysts.pool import DeliveryAnalyst
    from masdss.config import CONFIG

    agent = DeliveryAnalyst(_KhongCoBangChung(), allow_refuse=False)
    reply = _goi(agent, _case())
    assert reply.content["confidence"] >= CONFIG.tau_cause


def test_dp3_analyst_van_ban_o_tang_B_cung_bi_ep():
    """Tang B khong co van ban — day la truong hop dat gia nhat cua ablation."""
    from masdss.agents.analysts.pool import QualityAnalyst

    agent = QualityAnalyst(_KhongCoBangChung(), allow_refuse=False)
    reply = _goi(agent, _case())
    assert reply.performative is Performative.PROPOSE


# --------------------------------------------------------------------------
# DP4 — "nguon goc tu giao tiep"
# --------------------------------------------------------------------------

def test_dp4_trace_viet_tay_khong_bieu_dien_duoc_su_kien_bi_loai():
    """Trace viet tay tu `Decision` chi giu KET CUC.

    No khong sai o nhung gi no noi — no thieu o nhung gi no khong the noi. Do
    chinh la noi dung thuc chat cua DP4.
    """
    from masdss.evaluation.trace_divergence import INVISIBLE_EVENTS, handwritten_trace

    decision = {"risk": 1, "causes": [{"cause": "delivery", "probability": 0.63}],
                "action": "preemptive_ticket_open", "degradation_level": 0}
    lines = handwritten_trace(decision)
    text = " ".join(lines).lower()

    assert "delivery" in text and "preemptive_ticket_open" in text
    for tu_khoa in ("refuse", "tu choi", "khai bao", "thua thau", "phan bac"):
        assert tu_khoa not in text
    assert {"refusal", "declaration", "award", "critique"} <= set(INVISIBLE_EVENTS)


def test_dp4_trace_viet_tay_khong_thay_doi_khi_bo_bid_bi_loai():
    """Hai lan chay khac han ve qua trinh nhung cung ket cuc -> trace viet tay
    GIONG HET nhau. Do la do phan ky, do thanh mot vi du cu the."""
    from masdss.evaluation.trace_divergence import handwritten_trace

    ket_cuc = {"risk": 1, "causes": [{"cause": "delivery", "probability": 0.63}],
               "action": "preemptive_ticket_open", "degradation_level": 0}
    assert handwritten_trace(ket_cuc) == handwritten_trace(dict(ket_cuc))


def test_dp4_phan_loai_refuse_theo_HANH_VI_khong_theo_ontology():
    """`REFUSE` mang `ontology='refusal'`, nhung phan loai phai uu tien performative.

    Da co ba lan trong du an nay mot phep kiem tra khoa nham vao performative thay
    vi ontology (hoac nguoc lai) va lam sai ca mot bang ket qua.
    """
    from uuid import uuid4

    from masdss.evaluation.trace_divergence import _kind_of

    goc = new_request(conversation_id=uuid4(), sender="O", receiver="A",
                      content={}, ontology="order_case")
    tu_choi = goc.reply(sender="A", performative=Performative.REFUSE,
                        content={}, ontology="bat_ky")
    trao = goc.reply(sender="O", performative=Performative.ACCEPT_PROPOSAL,
                     content={}, ontology="award")
    assert _kind_of(tu_choi) == "refusal"
    assert _kind_of(trao) == "award"
