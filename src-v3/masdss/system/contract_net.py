"""WP7 / T7.1, T7.2 — Contract Net hai pha co rang buoc ngan sach tinh toan.

Phuc vu: RQ3 — day la co che khien giao thuc tro nen LOAD-BEARING.

DON PHAN BIEN CAN TRA LOI. Ai doc Smith (1980) se noi ngay: "cac analyst cung lam
mot viec, bid do tin cay cua minh, orchestrator lay argmax — do la softmax co gan
nhan giao thuc, khong phai phan bo tac vu." Va ho dung, neu khong co rang buoc tai
nguyen.

CACH GIAI: hai pha, voi mot rang buoc that.

    PHA 1 — THAM DO (re, moi analyst deu tham gia)
        Orchestrator ──CFP(case, budget=B)──▶ 3 Analyst
        Moi Analyst tra BAN KHAI NANG LUC, KHONG chay capability dat:
            (expected_confidence, cost_ms, has_evidence)

    PHA 2 — PHAN BO DUOI RANG BUOC NGAN SACH
        max  Σ expected_information_gain(a)   s.t.   Σ cost_ms(a) ≤ B
        ──ACCEPT_PROPOSAL──▶ analyst thang thau  (chi ho moi chay capability dat)
        ──REJECT_PROPOSAL──▶ analyst thua thau

Ngan sach B do Orchestrator cap theo muc rui ro. Bo giao thuc di thi he thong MAT
mot nang luc that — kha nang phan bo tinh toan theo gia tri case — chu khong chi mat
mot cai ten.

CHI SO MOI SINH RA TU DAY: chat luong quy ket dat duoc TREN MOI MS TINH TOAN. Mot
ensemble khong co chi so nay vi no khong co khai niem lua chon.

GIAI BAI TOAN BANG VET CAN, KHONG PHAI THAM LAM. Voi 3 analyst chi co 8 to hop, nen
vet can cho nghiem TOI UU va TAT DINH. Thuat toan tham lam theo ty so gain/cost la xap
xi, va o quy mo nay khong co ly do gi phai chap nhan mot nghiem xap xi.

(`PriceAnalyst` da bi go 12/08 cung nhan `price` — xem `core/ontology.Cause`. Vet can
van la lua chon dung neu pool tro lai 4-5 analyst: 2^n voi n nho van re hon moi thu.)
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from masdss.core.ontology import Declaration


@dataclass(frozen=True)
class Allocation:
    """Ket qua phan bo o pha 2."""

    accepted: tuple[str, ...]
    rejected: tuple[str, ...]
    budget_ms: float | None
    spent_ms: float
    expected_gain: float

    @property
    def utilisation(self) -> float:
        if self.budget_ms is None or self.budget_ms <= 0:
            return 0.0
        return self.spent_ms / self.budget_ms

    def to_row(self) -> dict:
        return {
            "accepted": list(self.accepted),
            "rejected": list(self.rejected),
            "budget_ms": None if self.budget_ms is None else round(self.budget_ms, 3),
            "spent_ms": round(self.spent_ms, 3),
            "utilisation": round(self.utilisation, 4),
            "expected_gain": round(self.expected_gain, 4),
        }


def allocate(declarations: list[Declaration], budget_ms: float | None) -> Allocation:
    """Giai bai toan knapsack nho: toi da hoa loi ich duoi rang buoc ngan sach.

    Vet can tren moi tap con. Voi 3 analyst la 8 to hop — nghiem TOI UU, TAT DINH,
    va khong ton kem gi.

    Quy tac pha vo the can: khi hai tap con cho cung loi ich, chon tap RE HON; neu
    van bang nhau, chon theo thu tu bang chu cai cua agent_id. Khong co quy tac nay
    thi ket qua phu thuoc thu tu duyet, va tinh tai lap bi pha vo mot cach am tham.

    `budget_ms=None` nghia la KHONG CO RANG BUOC — khac han `budget_ms=0`.

        Phan biet nay bat buoc phai ro rang, va ly do la mot loi that: khi rang buoc
        ngan sach duoc go khoi cau hinh bao cao (14/08), buoc dau thau khong con ham
        `budget`, nen `bb.budget_ms_left` giu gia tri mac dinh 0,0 va `allocate()` di
        vao dung nhanh "khong du tien" — TU CHOI TOAN BO analyst. Ket qua: 0% case
        duoc quy ket nguyen nhan, va giao thuc van chay du hai pha nen khong co gi
        bao dong.

        `test_output_invariants.test_attribution_actually_runs_on_most_cases` bat
        duoc ngay. Do la bat bien duoc viet cho loi L08, va no bat mot loi khac han
        — dung ly do de kiem tra bat bien tren DAU RA chu khong chi tren don vi.

        Bai hoc: "khong khai bao ngan sach" va "ngan sach bang 0" la hai trang thai
        NGUOC NHAU ve y nghia. De chung cung mot bieu dien la moi cho mot loi im lang.
    """
    usable = [d for d in declarations if d.information_gain > 0]
    if budget_ms is None:
        # Khong rang buoc: moi khai bao co loi ich duong deu duoc nhan. Khong co bai
        # toan phan bo nao duoc giai o day, va `budget_binds` se bao dung dieu do.
        everyone = {d.agent_id for d in declarations}
        accepted = tuple(sorted(d.agent_id for d in usable))
        return Allocation(
            accepted=accepted,
            rejected=tuple(sorted(everyone - set(accepted))),
            budget_ms=None,
            spent_ms=sum(d.cost_ms for d in usable),
            expected_gain=sum(d.information_gain for d in usable),
        )
    if not usable or budget_ms <= 0:
        return Allocation(
            accepted=(),
            rejected=tuple(sorted(d.agent_id for d in declarations)),
            budget_ms=budget_ms, spent_ms=0.0, expected_gain=0.0,
        )

    feasible: list[tuple[float, float, tuple[str, ...]]] = []
    for size in range(len(usable) + 1):
        for subset in combinations(usable, size):
            cost = sum(d.cost_ms for d in subset)
            if cost > budget_ms:
                continue
            gain = sum(d.information_gain for d in subset)
            feasible.append((gain, cost, tuple(sorted(d.agent_id for d in subset))))

    # Thu tu uu tien: loi ich CAO nhat -> chi phi THAP nhat -> ten theo bang chu cai.
    # Viet duoi dang khoa sap xep thay vi so sanh tay, vi so sanh tay khong the "dao
    # chieu" mot truong chuoi va do la cho ban dau bi sai: `Zulu` thang `Alpha` du
    # quy tac noi phai chon theo bang chu cai.
    gain, cost, accepted = min(feasible, key=lambda item: (-item[0], item[1], item[2]))
    everyone = {d.agent_id for d in declarations}
    return Allocation(
        accepted=accepted,
        rejected=tuple(sorted(everyone - set(accepted))),
        budget_ms=budget_ms, spent_ms=cost, expected_gain=gain,
    )


def budget_binds(declarations: list[Declaration], budget_ms: float | None) -> bool:
    """Ngan sach co THUC SU rang buoc khong, hay moi analyst deu duoc goi?

    Neu ngan sach khong bao gio rang buoc thi giao thuc chay nhung khong quyet dinh
    gi — va moi con so ve "phan bo tinh toan" tro nen rong. Ham nay ton tai de bao
    cao trung thuc dieu do thay vi de no am tham.

    `budget_ms=None` (khong khai bao rang buoc) luon cho False: khong co rang buoc
    nao thi khong the noi no rang buoc.
    """
    if budget_ms is None:
        return False
    total = sum(d.cost_ms for d in declarations if d.information_gain > 0)
    return total > budget_ms
