"""WP10 / T10.5 — Chi so chiu loi.

Phuc vu: RQ1(a) — ty le he thong cho ra quyet dinh sai ma khong canh bao.

MOT LOI DINH NGHIA DA DUOC SUA O DAY, va no quan trong hon ve ngoai:

    Ban dau `silent_failure` duoc dinh nghia la "co buoc TU BAO CAO that bai nhung
    van ra quyet dinh". Dinh nghia do MU voi dung loai loi ma RQ1 quan tam nhat:
    loi Byzantine khong raise exception nao ca — do chinh la ly do no nguy hiem.
    Do bang cach hoi he thong "anh co hong khong" thi mot he thong hong am tham se
    luon tra loi "khong".

    Dinh nghia dung phai dua tren SU THAT NEN cua thi nghiem: ta BIET da tiem loi
    vao thanh phan nao, vi chinh ta tiem. Mot case duoc tinh la hong am tham khi:

        (1) thanh phan bi tiem loi NAM TREN duong thuc thi cua case do, VA
        (2) he thong van sinh quyet dinh tu dong, VA
        (3) dau ra khong mang bat ky dau hieu nao cho biet nang luc da suy giam.

    Voi Monolithic-Complete, dieu kien (3) LUON dung — kien truc do khong co truong
    nao bieu dien muc suy giam. Do khong phai thien vi trong cach do; do la thu
    dang duoc do.

!! DAY KHONG PHAI CHI SO CHINH TAC CUA CHUONG 5. Doc muc duoi truoc khi trich.

    Con so hong am tham dua vao luan van duoc sinh boi `chaos/runner.py`, KHONG boi
    module nay. Hai noi dinh nghia khac nhau o mot cho co that:

        module nay      "co tiem loi vao thanh phan tren duong chay + van ra quyet
                        dinh tu dong"  -> dem tren TOAN BO tap case bi phoi nhiem
        chaos/runner.py "dau ra THUC SU KHAC lan chay khoe + khong canh bao gi"
                        -> dem tren nhung case CO DOI dau ra

    Ban cua `chaos/runner.py` chat hon va dung hon, vi no co mot LAN CHAY KHOE lam
    su that nen. Module nay khong co doi chieu do — no chi nhin mot lan chay — nen
    no UOC LUONG QUA CAO: mot case ma loi khong he anh huong toi ket qua van bi dem
    la "hong am tham".

    Vi vay module nay chi con dung cho phan in nhanh ra man hinh cua `run_system
    --inject`, va con so cua no KHONG duoc trich. Giu lai thay vi xoa vi
    `test_chaos_parity.py` dung no de canh mot bat bien khac: dinh nghia hong am
    tham khong duoc dua tren TU BAO CAO cua he thong.

    Sua cua L37 truoc day chi duoc ap o `chaos/runner.py`; ham
    `monolithic_silent_failures` duoi day van con dem theo ban cu cho toi hom nay.
"""

from __future__ import annotations

from dataclasses import dataclass

# Thanh phan nao nam tren duong thuc thi cua moi case, theo tung ke hoach.
# Ca hai kien truc deu chay het cac thanh phan nay tren MOI case, nen mot loi tiem
# vao bat ky thanh phan nao trong danh sach deu "phoi nhiem" toan bo tap case.
STAGE2_COMPONENTS = frozenset({
    "analytics", "prediction", "cause_delivery",
    "cause_quality", "cause_service", "recommendation", "critic", "rules",
})


@dataclass(frozen=True)
class SilentFailureReport:
    architecture: str
    injected: str | None
    n_cases: int
    n_exposed: int
    n_silent: int

    @property
    def rate(self) -> float:
        return self.n_silent / self.n_exposed if self.n_exposed else 0.0

    def describe(self) -> str:
        if self.injected is None:
            return f"{self.architecture}: khong tiem loi — khong ap dung"
        return (f"{self.architecture:20s}: {self.n_silent:4d} / {self.n_exposed:4d} "
                f"({100 * self.rate:5.1f}%)")


def _is_exposed(injected: str | None) -> bool:
    """Thanh phan bi tiem loi co nam tren duong thuc thi khong."""
    return injected is not None and injected in STAGE2_COMPONENTS


def mas_silent_failures(decisions: list[dict], injected: str | None) -> SilentFailureReport:
    """MAS-DSS: dau hieu suy giam la `degradation_level` va `needs_human_review`."""
    exposed = _is_exposed(injected)
    n_exposed = len(decisions) if exposed else 0
    silent = 0
    if exposed:
        silent = sum(
            1 for d in decisions
            if d["degradation_level"] == 0
            and not d["needs_human_review"]
            and d["action"] != "escalate_to_human"
        )
    return SilentFailureReport("MAS-DSS", injected, len(decisions), n_exposed, silent)


def monolithic_silent_failures(rows: list[dict], injected: str | None) -> SilentFailureReport:
    """Monolithic-Complete: khong co truong suy giam, NHUNG co `failed_steps`.

    SUA L37 — ap muon, va day la lan ap dau tien o module nay.

        Ban cu dem MOI case ra quyet dinh tu dong la hong am tham, voi ly do "don
        khoi khong co co suy giam". Ly do do sai: no CO `failed_steps`, va truong
        nay duoc dien day du moi khi mot buoc raise exception. Voi nhom loi crash va
        hang, 100% so ca bi doi dau ra deu co `failed_steps` — tuc don khoi CO phat
        tin hieu, va dem chung la "am tham" lam lech ket qua ve phia CO LOI cho
        MAS-DSS.

        `chaos/runner.py` da sua cho nay tu truoc; module nay thi chua, nen hai noi
        cho hai con so khac nhau tren cung mot lan chay. Nay ca hai hoi cung mot cau.

    Viec don khoi doi khi VAN escalate la nho dung chung tap luat YAML
    (`unknown_cause_must_escalate`) — mot lop bao ve TINH CO, khong phai do kien truc.
    """
    exposed = _is_exposed(injected)
    n_exposed = len(rows) if exposed else 0
    silent = 0
    if exposed:
        silent = sum(
            1 for r in rows
            if r["monolithic"]["action"] != "escalate_to_human"
            and not r["monolithic"].get("failed_steps")
        )
    return SilentFailureReport("Monolithic-Complete", injected, len(rows), n_exposed, silent)


def compare(decisions: list[dict], baselines: list[dict],
            injected: str | None) -> list[SilentFailureReport]:
    return [
        mas_silent_failures(decisions, injected),
        monolithic_silent_failures(baselines, injected),
    ]
