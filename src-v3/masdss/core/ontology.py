"""WP0 / T5.1 — Ontology dung chung giua moi tac tu.  [Artifact A1]

Phuc vu: RQ2 (giao thuc giao tiep), RQ3 (bid kem bang chung).

Diem thiet ke quan trong nhat o day: quy ket nguyen nhan la DA NHAN. Khong ton
tai kieu du lieu nao bieu dien "mot nguyen nhan duy nhat", vi nhu vay se mo duong
cho argmax quay lai (technical-plan-v3.md §A.3).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum


class Cause(str, Enum):
    """BA nhom nguyen nhan + truong hop khong quy ket duoc.

    `PRICE` DA BI GO BO (12/08). Ly do khong phai co mau nho ma la HE PHAN LOAI DAT
    SAI: khach hang da xac nhan mua, tuc da dong y voi gia niem yet, nen mot lo than
    sau khi mua khong the ve GIA SAN PHAM.

    Doc ca 12 dong duoc gan `price` trong gold set cho thay 10/12 than ve PHI VAN
    CHUYEN — tra tien ship roi van phai tu ra buu dien lay hang — va hai trong so do
    noi ro hang van tot (*"Quality merchandise, I just think the freight should be
    more affordable"*). Do la that bai giao hang, khong phai phan xet gia tri.

    BA QUY TAC DINH TUYEN thay cho `price` (codebook §Quy tac 7):

        phi van chuyen · doi hoan phi chung chung   -> DELIVERY
        "khong dang tien" · "chat luong khong xung" -> QUALITY
        doi hoan phi ma khong duoc phan hoi         -> SERVICE

    Chi 2/250 dong mat het nhan khi go `price`, va ca hai deu la than phi van chuyen
    thuan tuy nen ve DELIVERY.
    """

    DELIVERY = "delivery"
    QUALITY = "quality"
    SERVICE = "service"
    UNKNOWN = "unknown"


class RiskLevel(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2


class DecisionPoint(str, Enum):
    """Bon moc thoi diem. Xem research-questions-objectives.md §0.2.

    T3 = sau giao hang, TRUOC khi khach viet danh gia -> chua co bang chung van ban.
    T4 = khi danh gia 1-2 sao ve  -> co van ban voi 74,71% don bat man.
    """

    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"


class DegradationLevel(IntEnum):
    """Construct rieng cua luan van (A1).

    Buoc moi quyet dinh phai mang theo muc do dang tin cua he thong tai thoi diem
    sinh ra no. Van lieu DSS hau nhu khong co khai niem nay.
    """

    NORMAL = 0
    L1_FALLBACK = 1
    L2_HEURISTIC = 2
    L3_HUMAN = 3


@dataclass(frozen=True)
class Evidence:
    """Bang chung cu the di kem mot bid. Khong duoc rong."""

    kind: str  # "delivery_delay" | "freight_zscore" | "text_span" | ...
    detail: str
    value: float | None = None

    def __post_init__(self) -> None:
        if not self.kind or not self.detail:
            raise ValueError("Evidence phai co kind va detail khong rong")


@dataclass(frozen=True)
class Bid:
    """Mot phieu dau thau tu Analyst.

    `cost_ms` la dau vao cua bai toan phan bo ngan sach trong Contract Net —
    no la du lieu van hanh, khong phai chu thich (technical-plan-v3.md §A.2).
    """

    analyst: str
    cause: Cause
    confidence: float
    cost_ms: float
    evidence: tuple[Evidence, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence ngoai [0,1]: {self.confidence}")
        if self.cost_ms < 0:
            raise ValueError("cost_ms khong duoc am")
        if self.cause is not Cause.UNKNOWN and not self.evidence:
            raise ValueError("Bid co nguyen nhan cu the bat buoc phai kem bang chung")


@dataclass(frozen=True)
class CauseAssignment:
    """Mot nguyen nhan da duoc chap nhan sau khi loc nguong tau."""

    cause: Cause
    probability: float
    evidence: tuple[Evidence, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError(f"probability ngoai [0,1]: {self.probability}")


@dataclass(frozen=True)
class Critique:
    """Phan bien cua Policy Critic — engine rang buoc, khong phai engine EV.

    Critic khong tuyen bo "hanh dong nay se khong hieu qua" (khong biet duoc, xem
    rang buoc C1). No tuyen bo "hanh dong nay vi pham rang buoc X, do duoc ngay
    bay gio".
    """

    challenged: bool
    violated_constraints: tuple[str, ...] = ()
    note: str = ""


@dataclass(frozen=True)
class Action:
    """Mot hanh dong phuc hoi dich vu.

    `expedite_shipment` da bi loai vi bat kha thi ve mat thoi gian tai T3/T4.
    """

    name: str
    params: dict[str, object] = field(default_factory=dict)


ESCALATE = Action(name="escalate_to_human")


@dataclass(frozen=True)
class OrderCase:
    """Don vi nghiep vu di qua toan bo chuoi xu ly."""

    case_id: str
    decision_point: DecisionPoint
    features: dict[str, object] = field(default_factory=dict)
    review_text: str | None = None

    @property
    def has_text_evidence(self) -> bool:
        """Phan tang A/B. Tang B = 25,23% don bat man (M0, theo `review_content`).

        Day la dieu kien REFUSE kiem chung duoc cua Quality va Service Analyst.
        """
        return bool(self.review_text and self.review_text.strip())


@dataclass(frozen=True)
class Declaration:
    """Ban khai nang luc o pha 1 Contract Net.  [Artifact A1]

    Sinh ra ma KHONG chay capability dat — do la ranh gioi lam cho pha tham do re,
    va la dieu kien de bai toan phan bo tinh toan co y nghia.

    VI SAO KIEU NAY NAM O `core/` CHU KHONG PHAI `system/`: no la TU VUNG CHUNG giua
    tang agent (ben khai bao) va tang system (ben phan bo). Dat o `system/` se buoc
    `agents/` phai import `system/` — dung mui phan tang cua loi L18.
    """

    agent_id: str
    expected_confidence: float
    cost_ms: float
    has_evidence: bool
    reason: str = ""

    @property
    def information_gain(self) -> float:
        """Loi ich ky vong cua viec goi analyst nay.

        Khong co bang chung thi khong co loi ich, bat ke do tin cay tien nghiem cao
        den dau — do la cach `has_evidence` tham gia vao bai toan phan bo thay vi chi
        la mot co trang tri.
        """
        return self.expected_confidence if self.has_evidence else 0.0
