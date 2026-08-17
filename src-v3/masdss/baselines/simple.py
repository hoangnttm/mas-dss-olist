"""WP4 / T4.1, T4.2 — Hai baseline don gian.  [Artifact A6]

Phuc vu: RQ1 (mo ta khac biet chuc nang giua cac kien truc).

    MIS       — bao cao mo ta theo nguong. Khong mo hinh, khong quy ket, khong
                sinh hanh dong. Day la "cach lam hien tai" ma nhieu doanh nghiep
                thuc su dang dung.
    Single-ML — chi du bao. Dung CUNG doi tuong risk_model voi MAS-DSS, va do
                chinh la ly do H1 duoc khai bao truoc la KY VONG VO HIEU.

LUU Y KHI VIET CHUONG 5: hai baseline nay bang 0 o cac chi so "quy ket" va "sinh
hanh dong" theo DINH NGHIA, khong phai theo do do. Bao cao chenh lech do nhu bang
chung uu viet la tautology. Chung ton tai de MO TA khac biet chuc nang, con phep
so sanh that nam o Monolithic-Complete.
"""

from __future__ import annotations

from dataclasses import dataclass

from masdss.core.ontology import OrderCase

DEFAULT_DELAY_THRESHOLD_DAYS = 3.0


@dataclass
class SimpleResult:
    case_id: str
    flagged: bool
    risk: int | None = None
    note: str = ""
    # Diem du bao THO. Ton tai de nguoi doc khoi phai phan tich chuoi `note` —
    # chuoi do da lam tron 4 chu so, va viec doc no da tung lam kiem tra dieu kien
    # kiem soat bao sai lech +0,000014 tren hai day so von giong het nhau.
    score: float | None = None

    def to_row(self) -> dict:
        return {"case_id": self.case_id, "flagged": self.flagged,
                "risk": self.risk, "score": self.score, "note": self.note}


class MISBaseline:
    """Bao cao mo ta: gan co don tre qua nguong. Khong mo hinh nao."""

    name = "mis"

    def __init__(self, delay_threshold: float = DEFAULT_DELAY_THRESHOLD_DAYS) -> None:
        self.delay_threshold = delay_threshold

    def run(self, case: OrderCase) -> SimpleResult:
        delay = case.features.get("delivery_delay_days")
        late = delay is not None and float(delay) > self.delay_threshold
        return SimpleResult(
            case_id=case.case_id,
            flagged=bool(late),
            note=f"tre {delay} ngay" if late else "trong nguong",
        )


class SingleMLBaseline:
    """Chi du bao rui ro. Dung CUNG doi tuong risk_model voi MAS-DSS."""

    name = "single_ml"

    def __init__(self, capabilities) -> None:
        self.risk_model = capabilities.risk_model

    def run(self, case: OrderCase) -> SimpleResult:
        score = self.risk_model.run(case)
        level = int(self.risk_model.to_risk_level(score))
        return SimpleResult(
            case_id=case.case_id,
            flagged=level > 0,
            risk=level,
            score=float(score),
            note=f"risk_score={score:.4f}",
        )
