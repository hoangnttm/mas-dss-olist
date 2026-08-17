"""WP8 / T8.1 — Output guard: chan ket qua hop le ve kieu nhung sai ve chat.

Phuc vu: RQ1(a) — keo ty le hong am tham xuong.

BON TANG GUARD, moi tang bat mot loai loi khac nhau:

    Schema       — sai kieu, ngoai mien, thieu bang chung.  Bat loi CAI DAT.
    Sanity       — dai luong dung yen tren cua so truot.     Bat MODEL CHET.
    Calibration  — phan phoi lech so voi tham chieu (PSI).   Bat DRIFT.
    Consistency  — mau thuan giua cac tac tu.                Bat SAI LECH NOI BO.

NGUYEN TAC THIET KE QUAN TRONG NHAT — va no la dieu kien de ket qua RQ1 co gia tri:

    Guard duoc viet theo NGUYEN LY TONG QUAT, khong duoc viet de bat dung mot bo
    tiem loi cu the. Neu guard biet truoc `ConstantOutputInjector` dat gia tri 0.5
    roi di kiem tra "co phai 0.5 khong", ta khong do duoc gi ca — ta chi kiem tra
    rang minh da viet dung cai minh vua nghi ra.

    Vi vay: `SanityGuard` khong biet gi ve hang so nao; no chi biet rang mot dai
    luong dang le phai bien thien ma dung yen la bat thuong. Nho vay ty le phat
    hien tren nhom "Byzantine tinh vi" moi la KET QUA THUC NGHIEM.

Guard vi pham phat `GuardViolation` — von la mot `DeterministicError`. Orchestrator
da xu ly loai loi do bang cach ha hai bac suy giam, nen khong dong nao trong
orchestrator phai sua.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from masdss.core.errors import GuardViolation
from masdss.core.message import Message, Performative
from masdss.system.reliability.health import HealthMonitor


@dataclass(frozen=True)
class GuardResult:
    ok: bool
    guard: str = ""
    reason: str = ""

    @staticmethod
    def passed() -> "GuardResult":
        return GuardResult(ok=True)


class Guard(Protocol):
    name: str

    def check(self, component: str, message: Message) -> GuardResult: ...


# --- Tang 1: schema ---

@dataclass
class SchemaGuard:
    """Kieu du lieu va mien gia tri. Bat loi cai dat va loi tuan tu hoa."""

    name: str = "schema"

    def check(self, component: str, message: Message) -> GuardResult:
        content = message.content

        for field_name in ("risk_score", "confidence"):
            if field_name in content:
                value = content[field_name]
                if not isinstance(value, (int, float)) or not 0.0 <= float(value) <= 1.0:
                    return GuardResult(False, self.name,
                                       f"{field_name} = {value!r} ngoai mien [0,1]")

        if "risk" in content and content["risk"] is not None:
            if int(content["risk"]) not in (0, 1, 2):
                return GuardResult(False, self.name,
                                   f"risk = {content['risk']!r} khong thuoc {{0,1,2}}")

        # Bid phai kem bang chung — mot bid tran khong kiem chung duoc.
        #
        # Rang buoc nay khoa theo ONTOLOGY chu khong theo PERFORMATIVE, va do la mot
        # sua loi. Contract Net hai pha dung `PROPOSE` cho CA HAI viec:
        #     ontology="declaration" — ban khai nang luc o pha 1, CHUA co bang chung
        #     ontology="bid"         — bid that o pha 2, BAT BUOC co bang chung
        # Khoa theo performative se chan sach moi ban khai va lam sap phien dau thau.
        if message.ontology == "bid" and not content.get("evidence"):
            return GuardResult(False, self.name, "bid khong kem bang chung")

        # Ban khai nang luc phai day du truong, neu khong bai toan phan bo se nhan
        # dau vao rac ma khong ai biet.
        if message.ontology == "declaration":
            declaration = content.get("declaration")
            required = {"agent_id", "expected_confidence", "cost_ms", "has_evidence"}
            if not isinstance(declaration, dict) or not required <= set(declaration):
                return GuardResult(False, self.name, "ban khai nang luc thieu truong")

        return GuardResult.passed()


# --- Tang 2 va 3: sanity va calibration, cung dua tren Health Monitor ---

@dataclass
class StatisticalGuard:
    """Phuong sai bang khong (sanity) va PSI (calibration).

    Hai co che chia se cung cua so truot nen gop vao mot guard, nhung ly do canh
    bao van duoc phan biet ro trong thong diep.
    """

    health: HealthMonitor
    name: str = "statistical"

    # Dai luong duoc theo doi theo tung loai message.
    TRACKED: tuple[str, ...] = ("risk_score", "confidence")

    def check(self, component: str, message: Message) -> GuardResult:
        for metric in self.TRACKED:
            if metric not in message.content:
                continue
            value = message.content[metric]
            if not isinstance(value, (int, float)):
                continue
            alerts = self.health.observe(component, metric, float(value))
            if alerts:
                return GuardResult(False, self.name, alerts[0].detail)

        # TRANG THAI SUC KHOE LA BEN VUNG, khong phai mot su kien mot lan.
        #
        # Health Monitor chi phat canh bao MOI dung mot lan cho moi (thanh phan,
        # dai luong) — de do duoc DO TRE PHAT HIEN. Nhung mot thanh phan da bi ket
        # luan la hong thi khong duoc phuc vu tiep nhu chua co chuyen gi: neu guard
        # chi chan dung case dau tien, 299 case sau van hong am tham y nguyen.
        if self.health.is_unhealthy(component):
            return GuardResult(
                False, self.name,
                f"{component} da bi danh dau bat thuong o mot canh bao truoc do — "
                f"khong phuc vu tiep cho toi khi duoc khoi phuc",
            )
        return GuardResult.passed()


# --- Tang 4: consistency ---

@dataclass
class ConsistencyGuard:
    """Mau thuan giua ket qua cua cac tac tu khac nhau.

    Vi du: Prediction bao rui ro cao nhung khong analyst nao tim ra bang chung nao,
    va Analytics cung khong thay bat thuong. Mot trong hai ben dang sai.
    """

    name: str = "consistency"

    def check_blackboard(self, bb) -> GuardResult:
        from masdss.core.ontology import RiskLevel

        if bb.risk is None:
            return GuardResult.passed()

        if bb.risk >= RiskLevel.HIGH and not bb.causes and bb.plan_state.get("contract_net"):
            if not bb.context.get("is_late", False):
                return GuardResult(
                    False, self.name,
                    "Prediction bao rui ro CAO nhung khong analyst nao tim ra bang chung, "
                    "va Analytics khong thay bat thuong nao",
                )
        return GuardResult.passed()


# --- Ap dung ---

@dataclass
class GuardChain:
    """Chuoi guard chay theo thu tu. Vi pham dau tien la dung lai."""

    guards: tuple[Guard, ...] = ()
    violations: list[dict] = field(default_factory=list)

    def check(self, component: str, message: Message) -> None:
        """Phat `GuardViolation` khi co vi pham.

        `GuardViolation` la `DeterministicError`, nen orchestrator tu dong ha hai
        bac suy giam — khong can sua orchestrator.
        """
        for guard in self.guards:
            result = guard.check(component, message)
            if not result.ok:
                self.violations.append({
                    "component": component, "guard": result.guard, "reason": result.reason,
                })
                raise GuardViolation(f"[{result.guard}] {component}: {result.reason}")

    def report(self) -> list[dict]:
        return list(self.violations)


def default_chain(health: HealthMonitor) -> GuardChain:
    return GuardChain(guards=(SchemaGuard(), StatisticalGuard(health)))
