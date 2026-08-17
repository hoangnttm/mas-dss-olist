"""WP0 / T6.4 — Blackboard: working memory cua mot case.

Phuc vu: RQ2, RQ3.

Khong chi la cho chua du lieu. No la KHONG GIAN LAM VIEC CHUNG de tac tu doc ket
qua CUA NHAU ma khong goi truc tiep: Recommendation doc `causes` do nhom Analyst
ghi, Critic doc `proposal` cua Recommendation, Arbiter doc `critique` cua Critic.

GIOI HAN PHAI NOI THANG — CAC ANALYST KHONG DOC BID CUA NHAU.

    Phac thao ban dau neu mot vi du phoi hop manh hon: mot analyst doc bid cua
    Delivery truoc khi bid ("da tre 9 ngay thi phi ship khong phai nguyen nhan
    chinh, ha confidence cua minh xuong"). Co che do KHONG duoc cai dat. Analyst
    chi doc `message.payload` (chinh `OrderCase`); chung khong doc `content` va
    khong nhin thay bid cua nhau.

    He qua truc tiep, va no chinh la goc cua L27: cac analyst PHAN CHIA khong gian
    nhan chu khong TRANH CHAP no. DP2 phat bieu "quy ket bang canh tranh", nhung
    co che canh tranh duy nhat dang ton tai la RANG BUOC NGAN SACH o pha 2 —
    analyst tranh nhau SUAT TINH TOAN, khong tranh nhau NHAN.

    Chuong 4 phai mo ta dung nhu vay. Viet "tac tu doc bid cua nhau" la mo ta mot
    co che khong co ma nguon tuong ung.

MOT NGUON SU THAT: day la noi duy nhat giu trang thai trung gian cua case. Neu
thay minh ghi cung mot du lieu vao hai cho, do la bug.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from masdss.core.ontology import Bid, CauseAssignment, Critique, OrderCase, RiskLevel


@dataclass
class Blackboard:
    """Trang thai cua mot case trong suot vong doi xu ly."""

    case: OrderCase

    # --- cac o ket qua, moi o do mot nhom tac tu ghi ---
    context: dict[str, Any] = field(default_factory=dict)      # Analytics
    risk: RiskLevel | None = None                              # Prediction
    risk_score: float | None = None                            # Prediction
    bids: list[Bid] = field(default_factory=list)              # Analyst pool
    causes: list[CauseAssignment] = field(default_factory=list) # sau khi loc nguong
    multi_cause: bool = False
    proposal: Any = None                                        # Recommendation
    critique: Critique | None = None                            # Policy Critic

    # --- trang thai dieu phoi va suc khoe ---
    plan_state: dict[str, str] = field(default_factory=dict)   # buoc -> ket qua
    allocation: dict[str, Any] | None = None                   # ket qua Contract Net
    # `None` = KHONG co rang buoc ngan sach; `0.0` = ngan sach bang khong.
    # Hai trang thai nay NGUOC NHAU ve y nghia — xem `contract_net.allocate`.
    budget_ms_left: float | None = None
    degradation_level: int = 0
    notes: list[str] = field(default_factory=list)

    def record_step(self, step: str, outcome: str) -> None:
        self.plan_state[step] = outcome

    def degrade(self, level: int, reason: str) -> None:
        """Nang muc suy giam. Chi tang, khong bao gio giam trong mot case."""
        if level > self.degradation_level:
            self.degradation_level = level
        self.notes.append(f"degraded->{level}: {reason}")

    @property
    def completed_steps(self) -> tuple[str, ...]:
        return tuple(self.plan_state)
