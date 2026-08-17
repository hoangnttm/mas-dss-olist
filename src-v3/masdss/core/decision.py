"""WP0 / T5.3 — Decision: noi RQ2 va DP1 duoc CUONG CHE bang kieu du lieu.

Phuc vu: RQ2 (trung thuc ve do tin cay), RQ1 (khong hong am tham).

Hai rang buoc duoc cai dat o day, khong phai o tang nghiep vu:

  1. `degradation_level` KHONG CO GIA TRI MAC DINH. Nguoi viet ma buoc phai khai
     bao muc suy giam o moi noi tao Decision. Quen mot cho la loi tai cho.

  2. Bat bien DP1: `degradation_level > 0` ==> `needs_human_review is True`.
     "He thong khong bao gio duoc im lang cho ra quyet dinh rac."

`causes` la DAY (co the rong, co the nhieu phan tu). Khong ton tai truong `cause`
so it — do la cach chan argmax quay lai o tang kieu du lieu.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from uuid import UUID

from masdss.core.ontology import (
    Action,
    CauseAssignment,
    Cause,
    DecisionPoint,
    DegradationLevel,
    RiskLevel,
)


class DegradedAutonomyError(ValueError):
    """Vi pham DP1: sinh quyet dinh tu dong tren nen he thong dang suy giam."""


@dataclass(frozen=True)
class Decision:
    case_id: str
    decision_point: DecisionPoint
    risk: RiskLevel
    causes: tuple[CauseAssignment, ...]
    action: Action
    degradation_level: int  # BAT BUOC — khong dat gia tri mac dinh
    needs_human_review: bool
    conversation_id: UUID
    multi_cause: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not DegradationLevel.NORMAL <= self.degradation_level <= DegradationLevel.L3_HUMAN:
            raise ValueError(f"degradation_level ngoai mien: {self.degradation_level}")

        # --- Bat bien DP1 ---
        if self.degradation_level > 0 and not self.needs_human_review:
            raise DegradedAutonomyError(
                f"degradation_level={self.degradation_level} nhung needs_human_review=False. "
                "Khong quyet dinh tu dong nao duoc sinh ra tren nen he thong dang suy giam."
            )

        # Hanh dong chuyen giao thi bat buoc danh dau chuyen giao — neu khong,
        # bao cao va hanh vi thuc te phan ky.
        if self.action.name == "escalate_to_human" and not self.needs_human_review:
            raise DegradedAutonomyError(
                "action=escalate_to_human nhung needs_human_review=False — mau thuan noi bo"
            )

        # Quy ket that bai thi phai chuyen cho nguoi — hanh vi DUNG ve tri thuc luan.
        # Chi ap dung o T4: do la moc DUY NHAT co nhiem vu quy ket nguyen nhan
        # (research-questions-objectives.md §0.2). O T3 chua he co nhiem vu do, nen
        # `causes` rong la binh thuong chu khong phai that bai.
        if self.decision_point is DecisionPoint.T4:
            unknown_only = self.causes and all(c.cause is Cause.UNKNOWN for c in self.causes)
            if (not self.causes or unknown_only) and not self.needs_human_review:
                raise DegradedAutonomyError(
                    "cause=unknown tai T4 nhung needs_human_review=False. "
                    "Khong co bang chung quy ket thi phai chuyen giao cho nguoi."
                )

        # Co du hai nguyen nhan vuot nguong thi phai gan co da nguyen nhan (DP2).
        if len({c.cause for c in self.causes} - {Cause.UNKNOWN}) >= 2 and not self.multi_cause:
            raise ValueError(
                "Co tu 2 nguyen nhan tro len nhung multi_cause=False — mat thong tin "
                "ma co che canh tranh sinh ra de bat"
            )

    def to_row(self) -> dict:
        """Bieu dien CHINH TAC de kiem tra tinh tai lap.

        Khong chua dau thoi gian, khong chua do tre — hai lan chay cung cau hinh
        phai sinh ra chuoi JSON giong het nhau.
        """
        return {
            "case_id": self.case_id,
            "decision_point": self.decision_point.value,
            "risk": int(self.risk),
            "causes": [
                {"cause": c.cause.value, "probability": round(c.probability, 6)}
                for c in sorted(self.causes, key=lambda c: c.cause.value)
            ],
            "action": self.action.name,
            "degradation_level": int(self.degradation_level),
            "needs_human_review": self.needs_human_review,
            "multi_cause": self.multi_cause,
            "conversation_id": str(self.conversation_id),
            "notes": list(self.notes),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_row(), ensure_ascii=False, sort_keys=True)
