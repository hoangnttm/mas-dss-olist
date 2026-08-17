"""WP9 / T9.2, T9.3 — Chay toan bo danh muc kich ban tren HAI kien truc.

Phuc vu: RQ1(a) hong am tham, RQ1(b) do nhay va do tre phat hien, RQ1(d) chi phi.

DINH NGHIA HONG AM THAM — da duoc lam chat ba lan, moi lan vi mot loi do nham:

    v1  "co buoc tu bao cao that bai nhung van ra quyet dinh"
        -> MU voi loi Byzantine: chung khong raise exception nao ca.

    v2  "co tiem loi VA he van ra quyet dinh tu dong"
        -> Dem nham o nhom `hang`: mot lan goi bi treo lam he CHAM di chu khong lam
           SAI dau ra. Monolithic bi bao hong am tham 28,5% trong khi moi quyet dinh
           cua no van dung y het duong chay khoe. Do la that bai ve TINH SONG.

    v3  "DAU RA THUC SU KHAC duong chay khoe, VA khong co canh bao nao"   <- ban nay
        -> Duong khoe la SU THAT NEN, va ta co no vi ta chay no truoc moi kich ban.

Theo dinh nghia v3:
    MAS-DSS    : khac duong khoe VA degradation_level == 0 VA khong chuyen giao
    Monolithic : khac duong khoe  (kien truc nay khong co kenh canh bao nao)

BON DAI LUONG DUOC DO, ba trong so do la KET QUA THUC NGHIEM THAT:

    1. Ty le bao dong gia tren duong chay khoe            <- ket qua that
    2. Do nhay va do tre phat hien                        <- ket qua that o nhom
                                                             drift va bias
    3. Ty le hong am tham cua Monolithic-Complete         <- ket qua that
    4. Ty le hong am tham cua MAS-DSS                     <- kiem tra dac ta o nhom
                                                             crash/hang; ket qua that
                                                             o nhom drift/bias

Cot `designed_for` giu nguyen su phan biet do. Bao cao "guard bat duoc loi crash"
nhu mot phat hien la tu lua — ta viet guard de bat no.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from masdss.chaos.scenarios import ALL_SCENARIOS, HEALTHY, Scenario
from masdss.config import CONFIG


@dataclass(frozen=True)
class Baseline:
    """Anh chup duong chay khoe, dung lam su that nen cho moi kich ban."""

    mas: dict[str, tuple]
    mono: dict[str, tuple]

    @staticmethod
    def of(decisions: list[dict], baselines: list[dict]) -> "Baseline":
        return Baseline(
            mas={d["case_id"]: _mas_key(d) for d in decisions},
            mono={b["case_id"]: _mono_key(b["monolithic"]) for b in baselines},
        )


def _mas_key(decision: dict) -> tuple:
    """Phan NOI DUNG cua mot quyet dinh — bo qua co canh bao va muc suy giam."""
    return (
        decision["action"],
        tuple(sorted(c["cause"] for c in decision["causes"])),
        decision["risk"],
    )


def _mono_key(result: dict) -> tuple:
    return (result["action"], tuple(sorted(result["causes"])), result["risk"])


def _mono_warned(result: dict) -> bool:
    """Kien truc don khoi CO phat tin hieu hong — va phep dem phai ghi nhan dieu do.

    DAY LA CHO SUA CUA L37. Ban truoc coi MOI dau ra bi doi cua don khoi la "hong am
    tham", voi ly do "don khoi khong co co suy giam". Ly do do sai: no co
    `failed_steps`, va truong nay duoc dien day du khi mot buoc raise exception.

    Do lech khong nho va no nghieng ve phia CO LOI cho MAS-DSS:

        crash @ T4    doi dau ra 32 / 42 / 76 ca — CA 100% deu co `failed_steps`
        => "don khoi hong am tham 16,0 -> 32,0%" thuc ra la **0,0%**

    Sau khi sua, uu the cua MAS-DSS khong bien mat ma tro nen DUNG CHO HON: no nam o
    nhom loi KHONG raise exception (byzantine, bias) — dung nhom ma `try/except`
    khong giup gi va thang suy giam moi co tac dung.
    """
    return bool(result.get("failed_steps"))


@dataclass
class ScenarioResult:
    scenario: Scenario
    n_cases: int
    mas_silent: int
    mas_changed: int
    mas_degraded: int
    mono_silent: int
    mono_changed: int
    detected: bool
    detection_latency: int | None
    guard_blocks: int
    alerts: list[dict]
    latency_p50: float
    latency_p95: float
    mono_ms_per_case: float

    def to_row(self) -> dict:
        pct = lambda x: round(100 * x / self.n_cases, 1)  # noqa: E731
        return {
            "scenario": self.scenario.id,
            "group": self.scenario.group,
            "level": self.scenario.level,
            "designed_for": self.scenario.designed_for,
            "n_cases": self.n_cases,
            "mas_silent_pct": pct(self.mas_silent),
            "mono_changed_pct": pct(self.mono_changed),
            "mono_silent_pct": pct(self.mono_silent),
            "mas_changed_pct": pct(self.mas_changed),
            "mas_degraded_pct": pct(self.mas_degraded),
            "detected": self.detected,
            "detection_latency": self.detection_latency,
            "guard_blocks": self.guard_blocks,
            "latency_p50_ms": round(self.latency_p50, 3),
            "latency_p95_ms": round(self.latency_p95, 3),
            "mono_ms_per_case": round(self.mono_ms_per_case, 3),
            "description": self.scenario.description,
        }


def _read(out_dir: Path) -> tuple[list[dict], list[dict], dict]:
    decisions = [json.loads(line) for line in
                 (out_dir / "decisions.jsonl").read_text(encoding="utf-8").splitlines()]
    baselines = [json.loads(line) for line in
                 (out_dir / "baselines.jsonl").read_text(encoding="utf-8").splitlines()]
    reliability = json.loads(
        (out_dir / "reliability_report.json").read_text(encoding="utf-8"))
    return decisions, baselines, reliability


def _latency(out_dir: Path) -> tuple[float, float]:
    """Do tre p50/p95. KHONG tat dinh — chi dung cho RQ1(d), khong so sanh giua lan chay."""
    import sqlite3

    path = out_dir / "spans.sqlite"
    if not path.exists():
        return 0.0, 0.0
    conn = sqlite3.connect(path)
    values = [row[0] for row in
              conn.execute("SELECT duration_ms FROM spans ORDER BY duration_ms")]
    conn.close()
    if not values:
        return 0.0, 0.0
    return values[len(values) // 2], values[min(int(0.95 * len(values)), len(values) - 1)]


async def run_scenario(scenario: Scenario, out_root: Path, *, n_cases: int,
                       orders, capabilities, stage: int = 2,
                       baseline: Baseline | None = None,
                       reliability: bool = True) -> ScenarioResult:
    """`reliability=False` la DUONG ABLATION CUA DP1.

    Go ca tang chiu loi roi chay LAI CUNG kich ban loi: neu ty le hong am tham khong
    doi thi thang suy giam khong mua duoc gi, va DP1 chi la mot phat bieu. Tham so
    nay ton tai de nguyen ly do duoc KIEM CHUNG chu khong chi duoc tuyen bo.
    """
    from masdss.cli.run_system import run

    out_dir = out_root / scenario.id
    await run(out_dir, stage=stage, n_cases=n_cases, scenario=scenario,
              orders=orders, capabilities=capabilities, reliability=reliability)

    decisions, baselines, reliability = _read(out_dir)
    n = len(decisions)

    mas_silent = mas_changed = mono_silent = mono_changed = 0
    if baseline is not None:
        for d in decisions:
            reference = baseline.mas.get(d["case_id"])
            if reference is None or reference == _mas_key(d):
                continue
            mas_changed += 1
            warned = d["degradation_level"] > 0 or d["needs_human_review"] \
                or d["action"] == "escalate_to_human"
            if not warned:
                mas_silent += 1
        for b in baselines:
            reference = baseline.mono.get(b["case_id"])
            if reference is None or reference == _mono_key(b["monolithic"]):
                continue
            mono_changed += 1
            # Doi xung voi MAS-DSS: doi dau ra MA KHONG canh bao gi moi la am tham.
            if not _mono_warned(b["monolithic"]):
                mono_silent += 1

    alerts = reliability.get("health_alerts", [])
    p50, p95 = _latency(out_dir)

    return ScenarioResult(
        scenario=scenario, n_cases=n,
        mas_silent=mas_silent, mas_changed=mas_changed,
        mas_degraded=sum(1 for d in decisions if d["degradation_level"] > 0),
        mono_silent=mono_silent,
        mono_changed=mono_changed,
        detected=bool(alerts),
        detection_latency=alerts[0]["at_observation"] if alerts else None,
        guard_blocks=len(reliability.get("guard_violations", [])),
        alerts=alerts, latency_p50=p50, latency_p95=p95,
        mono_ms_per_case=float(reliability.get('mono_ms_per_case', 0.0)),
    )


async def run_all(out_root: Path, *, n_cases: int = 300,
                  scenarios: tuple[Scenario, ...] = ALL_SCENARIOS,
                  stage: int = 2) -> pd.DataFrame:
    """Chay duong khoe truoc de lay su that nen, roi toan bo danh muc kich ban.

    `stage` chon moc quyet dinh. H2 doi hoi ket qua o CA HAI moc: mot he chiu loi
    tot o T4 nhung hong am tham o T3 thi tuyen bo chiu loi phai thu hep lai. Duong
    co so duoc chay RIENG cho tung giai doan — so sanh voi duong co so cua giai doan
    kia se cho ra chenh lech gia.
    """
    from masdss.data.export import load_stage
    from masdss.system.app import Capabilities

    CONFIG.seed_everything()

    # Loc tong the CHI o giai doan 1, va su bat doi xung nay la co chu dich.
    #
    # Giai doan 1 @ T3 la DU BAO: mot don ma khach da viet danh gia truoc moc thi
    # khong con gi de du bao, va cham diem no la doc lai mot ket cuc da co (L33).
    #
    # Giai doan 2 @ T4 la QUY KET: dieu kien de vao day la "da co danh gia 1-2 sao",
    # khong phu thuoc vao viec T3 co kip nhin thay don do hay khong. Ap `reachable_at_t3`
    # o day se loai bo mot cach vo co nhung don dang can quy ket nguyen nhan nhat.
    #
    # LAP LUAN NAY DA THANG (13/08). Truoc do `export.py` ap phep loc cho ca hai giai
    # doan, va chu thich nay chi la mot loi canh bao khong ai doc. Nay no duoc cuong
    # che boi chinh cau truc tep: `load_stage("t4", ...)` khong loc, `("t3", ...)` co.
    orders = load_stage("t4" if stage == 2 else "t3", "test")
    t4_train, t4_val = load_stage("t4", "train"), load_stage("t4", "val")
    t3_train, t3_val = load_stage("t3", "train"), load_stage("t3", "val")
    capabilities = Capabilities.fit(t4_train, t4_val,
                                    risk_train=t3_train, risk_val=t3_val)

    healthy = await run_scenario(HEALTHY, out_root, n_cases=n_cases, stage=stage,
                                 orders=orders, capabilities=capabilities)
    decisions, baselines, _ = _read(out_root / HEALTHY.id)
    baseline = Baseline.of(decisions, baselines)
    rows = [healthy.to_row()]
    print(f"  {HEALTHY.id:18s} duong co so — {healthy.mas_degraded} case suy giam, "
          f"{healthy.guard_blocks} guard chan")

    for scenario in scenarios:
        result = await run_scenario(scenario, out_root, n_cases=n_cases, stage=stage,
                                    orders=orders, capabilities=capabilities,
                                    baseline=baseline)
        rows.append(result.to_row())
        mark = "  " if scenario.designed_for else "* "
        found = f"sau {result.detection_latency}" if result.detected else "khong"
        print(f"{mark}{scenario.id:18s} doi {result.mas_changed:3d}  "
              f"MAS am tham {result.mas_silent:3d}  Mono {result.mono_silent:3d}  "
              f"phat hien {found}")

    return pd.DataFrame(rows)


def sensitivity_curve(table: pd.DataFrame) -> pd.DataFrame:
    """Duong cong do nhay theo nhom va muc — dau ra chinh cho RQ1(b)."""
    faulty = table[table["group"] != "healthy"]
    return faulty[["group", "level", "designed_for", "detected", "detection_latency",
                   "mas_changed_pct", "mas_silent_pct", "mono_silent_pct"]].copy()
