"""WP6 — Chay MAS-DSS va cac baseline tren du lieu Olist that.

Chay:
    python -m masdss.cli.run_system --stage 2 --n 300
    python -m masdss.cli.run_system --stage 2 --n 300 --inject crash:Prediction

Bon tep dau ra, tach bach co chu dich:
    decisions.jsonl   -> CHINH TAC, tat dinh, la doi tuong cua test tai lap
    baselines.jsonl   -> ket qua ba baseline tren CUNG tap case
    messages.sqlite   -> nhat ky, nguon duy nhat de dung trace
    spans.sqlite      -> do tre; KHONG so sanh giua hai lan chay (co dong ho)
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

import pandas as pd

from masdss.baselines.monolithic import MonolithicComplete, is_silent_failure
from masdss.baselines.simple import MISBaseline, SingleMLBaseline
from masdss.chaos.injector import (
    BiasInjector,
    ConstantOutputInjector,
    CrashInjector,
    NullInjector,
)
from masdss.config import CONFIG, deterministic_uuid
from masdss.core.ontology import DecisionPoint, OrderCase
from masdss.data.export import load_stage
from masdss.data.featureset import FeatureSet
from masdss.runtime.faults import invoke
from masdss.runtime.message_log import MessageLog
from masdss.runtime.tracing import SpanRecorder
from masdss.system.app import Capabilities, build_decision, build_registry, reduce_reply
from masdss.system.explain import Explainer
from masdss.system.orchestrator import execute
from masdss.system.plan import (BUDGET_ENABLED_BY_DEFAULT, STAGE1_PLAN, STAGE2_PLAN,
                                with_budget, with_budget_scale,
                                with_deadline)
from masdss.system.reliability.guards import default_chain
from masdss.system.reliability.health import HealthMonitor
from masdss.system.reliability.pipeline import ReliabilityLayer
from masdss.system.reliability.reference import install_references


def _co_van_ban(df: pd.DataFrame) -> pd.Series:
    """Don co binh luan — dieu kien de vao giai doan 2.

    MOT CAI DAT DUY NHAT cho phep phan tang A/B. `OrderCase.has_text_evidence` dung
    dung phep kiem nay o tang case; ham nay la ban vector hoa cho tang bang. Neu hai
    noi dinh nghia khac nhau thi mau so cua chi so va hanh vi cua tac tu se lech.
    """
    if "review_content" not in df.columns:
        return pd.Series(False, index=df.index)
    text = df["review_content"]
    return text.notna() & (text.astype(str).str.strip() != "")


def cases_from(df: pd.DataFrame, decision_point: DecisionPoint,
               feature_set: FeatureSet) -> list[OrderCase]:
    """Chuyen bang don hang thanh OrderCase. Thu tu tat dinh theo order_id."""
    columns = [c for c in feature_set.names if c in df.columns]
    ordered = df.sort_values("order_id")
    cases = []
    for _, row in ordered.iterrows():
        cases.append(OrderCase(
            case_id=str(row["order_id"]),
            decision_point=decision_point,
            features={c: row[c] for c in columns},
            review_text=(None if pd.isna(row.get("review_content"))
                         else str(row.get("review_content"))),
        ))
    return cases


def make_injector(spec: str | None):
    """Cu phap: `kind:target[:field]`.

    Truong `field` cho phep chi dinh o nao trong ket qua bi dau doc. Mac dinh la
    `risk_score`, nhung de quan sat duoc anh huong tren quyet dinh cuoi cung thi
    thuong phai nham vao `risk` — o ma he thong thuc su tieu thu.
    """
    if not spec:
        return NullInjector()
    from masdss.core.components import normalize_target

    parts = spec.split(":")
    kind = parts[0]
    target = normalize_target(parts[1]) if len(parts) > 1 else ""
    field = parts[2] if len(parts) > 2 else "risk_score"

    targets = (target,) if target else ()
    if kind == "crash":
        return CrashInjector(targets=targets, deterministic=True, seed=CONFIG.seed)
    if kind == "transient":
        return CrashInjector(targets=targets, deterministic=False, seed=CONFIG.seed)
    if kind == "constant":
        return ConstantOutputInjector(targets=targets, field_name=field,
                                      constant=1 if field == "risk" else 0.5)
    if kind == "bias":
        return BiasInjector(targets=targets, field_name=field)
    if kind == "hang":
        from masdss.chaos.injector import HangInjector

        return HangInjector(targets=targets, delay=20.0)
    raise SystemExit(f"khong biet kieu tiem loi: {kind}")


async def run(out_dir: Path, *, stage: int = 2, n_cases: int = 300,
              inject: str | None = None, orders=None, capabilities=None,
              reliability: bool = True, scenario=None,
              text_cost_ms: float | None = None,
              order_ids: set | None = None,
              budget_scale: float | None = None,
              budget: bool = BUDGET_ENABLED_BY_DEFAULT,
              allow_refuse: bool = True) -> Path:
    """Chay he thong.

    `orders` va `capabilities` co the tiem tu ngoai vao de test khoi phai nap lai
    du lieu va huan luyen lai mo hinh o moi lan goi — chung tat dinh nen dung lai
    khong lam thay doi ket qua.
    """
    CONFIG.seed_everything()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Moi lan chay bat dau tu nhat ky SACH. Vi msg_id duoc sinh TAT DINH, chay lai
    # vao cung thu muc se dung khoa UNIQUE — do la rang buoc append-only lam dung
    # viec cua no, khong phai loi. Cach xu ly dung la lam moi, khong phai noi long
    # rang buoc.
    for name in ("messages.sqlite", "spans.sqlite"):
        (out_dir / name).unlink(missing_ok=True)

    # NAP QUA `load_stage`, mot lan goi quyet dinh CA luoc do lan tong the.
    #
    #   stage 1 -> "t3": cot T1..T3, tong the CON KIP CAN THIEP  (du bao)
    #   stage 2 -> "t4": cot T1..T4, tong the DAY DU             (quy ket)
    #
    # Ban truoc goi `build_order_table()` roi `time_split()` va cap `FeatureSet(T3)`
    # cho CA HAI giai doan. Hai hau qua, ca hai deu im lang:
    #
    #   1. Bo qua khoang cach ly va phep loc `reachable_at_t3` -> ty le nen bi lam
    #      loang, PR-AUC test 0,389 thay vi 0,238.
    #   2. `delivery_delay_days` la dac trung T4, nen o stage 2 no KHONG duoc cap
    #      -> `DeliverySignal.can_handle()` tra False voi 100% don, va nhan
    #      `delivery` — nhom nguyen nhan LON NHAT — khong bao gio quy ket duoc.
    #
    # `tests-v3/test_data_entrypoint.py` chan duong cu quay lai.
    stage_key = "t4" if stage == 2 else "t3"
    if orders is None:
        # Nang luc quy ket hoc tren tong the T4 (day du); mo hinh du bao va OOD hoc
        # tren tong the T3 (con kip can thiep). Xem `Capabilities.fit`.
        t4_train, t4_val = load_stage("t4", "train"), load_stage("t4", "val")
        t3_train, t3_val = load_stage("t3", "train"), load_stage("t3", "val")
        pool_all = load_stage(stage_key, "test")
    else:
        t4_train = t4_val = t3_train = t3_val = pool_all = orders
    if capabilities is None:
        capabilities = Capabilities.fit(t4_train, t4_val,
                                        risk_train=t3_train, risk_val=t3_val)

    # MO PHONG chi phi cua BERTimbau truoc khi T3.4 hoan thanh.
    #
    # `LexiconCauseHead` la ban tam thoi chi ton 0,4ms, nen ngan sach tinh toan khong
    # bao gio rang buoc va bai toan phan bo khong quyet dinh gi. Tham so nay dat chi
    # phi khai bao cua analyst van ban ve muc thuc te cua BERTimbau (~45ms) DE KIEM
    # CHUNG CO CHE phan bo.
    #
    # Moi con so sinh ra voi tham so nay la KET QUA MO PHONG, phai ghi ro nhu vay va
    # KHONG duoc trinh bay nhu ket qua do tren he thong that.
    if text_cost_ms is not None:
        capabilities.cause_head.cost_ms = text_cost_ms

    decision_point = DecisionPoint.T4 if stage == 2 else DecisionPoint.T3
    # Rang buoc ngan sach MAC DINH TAT — xem `plan.BUDGET_ENABLED_BY_DEFAULT`. Bat
    # lai bang `--budget` de chay phan tich do nhay (§5.11).
    plan = with_budget(STAGE2_PLAN if stage == 2 else STAGE1_PLAN, budget)
    plan = with_budget_scale(plan, budget_scale if budget else None)

    # DAC TRUNG CAP CHO CASE PHAI THEO MOC, khong duoc ghim cung o T3.
    #
    # Ban truoc ghim `FeatureSet(T3)` cho ca hai giai doan kem chu thich "dac trung
    # bang, dung cho ca hai". Ke tu khi `delivery_delay_days` chuyen sang T4 (12/08),
    # chu thich do sai va hau qua thi im lang: `DeliverySignal.can_handle()` tra False
    # voi 100% don o stage 2, nen `DeliveryAnalyst` khai "khong co bang chung" trong
    # MOI phien dau thau va nhan `delivery` khong bao gio quy ket duoc.
    #
    # Cap `FeatureSet(T4)` o giai doan 2 KHONG lam ro ri: tai T4 danh gia da ve nen
    # ket cuc giao hang la bang chung hop le, va `RiskModel` ghim `self._columns` tai
    # luc fit nen no van chi doc dung cot T3 da hoc.
    feature_set = FeatureSet(decision_point)

    # Chi lay don bat man tu tap TEST — moc T4 chi ton tai khi danh gia da ve.
    if order_ids is not None:
        # Duong danh gia tren GOLD SET. Ho ung vien sinh tu `t4_test` (xem
        # `export_feature_files`), nen chon tu chinh tap test — khong con tinh huong
        # "don roi vao ky train" nhu ban truoc.
        pool = pool_all[pool_all["is_dissatisfied"] & pool_all["order_id"].isin(order_ids)]
        cases = cases_from(pool, decision_point, feature_set)
    else:
        if stage == 2:
            # TANG B NAM NGOAI PHAM VI DE TAI (quyet dinh 13/08).
            #
            # Giai doan 2 chi nhan don bat man DA DUOC DANH GIA DAY DU, tuc co
            # `review_content`. Don khong binh luan (22,47% so don bat man) tach
            # thanh nhanh rieng va KHONG duoc xu ly o day.
            #
            # Truoc quyet dinh nay chung van di vao chuoi, roi Quality/Service luon
            # REFUSE vi khong co van ban — 48/69 don tang B ket thuc o `unknown`.
            # Tron chung vao lam mau so cua moi chi so phan loai bi thoi len ma
            # khong noi len dieu gi ve nang luc quy ket.
            pool = pool_all[pool_all["is_dissatisfied"] & _co_van_ban(pool_all)]
        else:
            pool = pool_all
        cases = cases_from(pool.head(n_cases), decision_point, feature_set)

    # Kich ban chaos (T9.2) go bo ba thu cung mot luc: bo tiem, drift o tang case,
    # va han chot rut ngan cho nhom `hang`.
    if scenario is not None:
        from masdss.chaos.injector import drift_cases

        injector = scenario.make_injector()
        if scenario.drift:
            cases = drift_cases(cases, scenario.drift, seed=CONFIG.seed)
        plan = with_deadline(plan, scenario.deadline_ms)
    else:
        injector = make_injector(inject)

    log = MessageLog(out_dir / "messages.sqlite")
    spans = SpanRecorder(out_dir / "spans.sqlite")
    registry = build_registry(capabilities, allow_refuse=allow_refuse)

    async def raw_invoke(handler, message):
        with spans.span(str(message.trace_id), message.content["step"], handler.agent_id):
            return await invoke(handler, message, injector=injector)

    # Tang chiu loi la mot LOP BOC, khong phai mot nhanh ma nguon. `reliability=False`
    # tra ve nguyen ham goc — day la duong ablation cho RQ1.
    health = HealthMonitor()

    # PHAN PHOI THAM CHIEU PHAI LAY TU CUNG MOT TONG THE voi luong duoc giam sat.
    #
    # Mot loi kinh dien da xay ra va da duoc sua o day: ban dau tham chieu lay tu
    # TOAN BO tap validation, trong khi giai doan 2 chi xu ly don BAT MAN. Hai tong
    # the do co phan phoi diem rui ro khac han nhau theo dung ban chat cua chung,
    # nen PSI = 0,807 tren mot lan chay hoan toan khoe manh — 93,7% bao dong gia.
    #
    # Do la chon mau, khong phai drift. Mot bo giam sat drift so sanh nham tong the
    # se bao dong lien tuc va nhanh chong bi nguoi van hanh phot lo — dung kieu that
    # bai ma RQ1(c) quan tam.
    # T7.3a — nap tham chieu cho MOI thanh phan co the giam sat duoc, khong chi
    # `prediction`. Bao cao pham vi phu duoc ghi ra tep de dua vao Chuong 5: mot bo
    # giam sat chi phu duoc mot phan he thong thi ket qua do nhay chi noi ve phan do.
    # Tap val cua DUNG giai doan dang chay: tham chieu phai cung tong the voi luong
    # duoc giam sat, va hai giai doan nay co tong the khac nhau.
    coverage = install_references(
        health, capabilities, t4_val if stage == 2 else t3_val,
        feature_columns=list(feature_set.names), stage=stage,
    )

    layer = ReliabilityLayer(guards=default_chain(health), enabled=reliability)
    invoke_fn = layer.wrap(raw_invoke)

    # L46 — do WALL-CLOCK cho ca hai kien truc, tren CUNG tap case va trong CUNG
    # tien trinh. Ban truoc so `sum(span.duration_ms)` cua MAS voi wall-clock cua
    # vong lap baseline; hai ve khong cung co so va CA HAI sai lech deu co loi cho
    # MAS (span bo qua glue va ghi nhat ky; vong lap baseline con om ca hai baseline
    # khac cong phan serialize). Xem `methodology-log.md`.
    import time as _time

    decisions: list[str] = []
    allocations: list[dict] = []
    mas_started = _time.perf_counter()
    for case in cases:
        conversation_id = deterministic_uuid("conv", case.case_id)
        bb = await execute(
            plan, case, invoke_fn, registry,
            reducer=reduce_reply, conversation_id=conversation_id,
            on_message=log.append,
        )
        decisions.append(build_decision(bb, conversation_id).to_json())
        if bb.allocation:
            allocations.append(bb.allocation)
    mas_seconds = _time.perf_counter() - mas_started

    decisions_path = out_dir / "decisions.jsonl"
    decisions_path.write_text("\n".join(decisions) + "\n", encoding="utf-8")

    # --- baseline tren CUNG tap case, dung CUNG capability ---
    #
    # Do thoi gian tuong tu MAS-DSS de RQ1(d) so sanh duoc. Voi kich ban `hang`, day
    # la cho duy nhat nhin thay duoc that bai ve TINH SONG cua Monolithic: no khong
    # co han chot nao nen chi cham di, khong bi huy.
    mis, single, mono = (MISBaseline(), SingleMLBaseline(capabilities),
                         MonolithicComplete(capabilities, injector))
    rows = []
    mono_seconds = 0.0
    for case in cases:
        # Dong ho chi om `mono.run` — KHONG om `mis`/`single` va KHONG om serialize.
        started = _time.perf_counter()
        result = mono.run(case)
        mono_seconds += _time.perf_counter() - started
        rows.append(json.dumps({
            "case_id": case.case_id,
            "mis": mis.run(case).to_row(),
            "single_ml": single.run(case).to_row(),
            "monolithic": result.to_row(),
            "monolithic_silent_failure": is_silent_failure(result),
        }, ensure_ascii=False, sort_keys=True))
    (out_dir / "baselines.jsonl").write_text("\n".join(rows) + "\n", encoding="utf-8")

    # Chung minh DP4 tren mot case that.
    trace = Explainer(log).build(deterministic_uuid("conv", cases[0].case_id))
    (out_dir / "trace_sample.txt").write_text(trace.render(), encoding="utf-8")

    report = layer.report()
    report["health_alerts"] = health.report()
    report["monitoring_coverage"] = [
        {"component": c.component, "metric": c.metric, "n_samples": c.n_samples,
         "variance": round(c.variance, 6), "installed": c.installed, "reason": c.reason}
        for c in coverage
    ]
    report["reliability_enabled"] = reliability
    if allocations:
        n = len(allocations)
        n_declared = sum(a["n_declared"] for a in allocations)
        n_accepted = sum(len(a["accepted"]) for a in allocations)
        report["contract_net"] = {
            # Ghi lai TRANG THAI CONG TAC ngay trong artifact. Neu khong, mot bang
            # `budget_binds_rate = 0` khong phan biet duoc hai tinh huong rat khac
            # nhau: ngan sach da TAT, hay ngan sach BAT ma khong rang buoc gi (dieu
            # dang le phai keu len — chinh la loi L27).
            "budget_enabled": bool(budget),
            "n_sessions": n,
            "avg_declared": round(n_declared / n, 2),
            "avg_accepted": round(n_accepted / n, 2),
            "rejection_rate": round(1 - n_accepted / max(n_declared, 1), 4),
            # Ngan sach co THUC SU rang buoc khong. Neu ty le nay bang 0 thi giao thuc
            # chay nhung khong quyet dinh gi, va moi con so ve phan bo tinh toan la rong.
            "budget_binds_rate": round(
                sum(1 for a in allocations if a["budget_binds"]) / n, 4),
            # `None` khi ngan sach khong duoc khai bao — trung binh cua "khong co
            # rang buoc" la vo nghia, va dien 0 vao do se doc thanh "ngan sach bang
            # khong", tuc dung nguoc y nghia.
            "avg_budget_ms": (
                round(sum(a["budget_ms"] for a in allocations) / n, 3)
                if all(a["budget_ms"] is not None for a in allocations) else None),
            "avg_spent_ms": round(sum(a["spent_ms"] for a in allocations) / n, 3),
            "avg_utilisation": round(sum(a["utilisation"] for a in allocations) / n, 4),
        }
    report["mono_seconds_total"] = round(mono_seconds, 3)
    report["mono_ms_per_case"] = round(1000 * mono_seconds / max(len(cases), 1), 3)
    report["mas_seconds_total"] = round(mas_seconds, 3)
    report["mas_ms_per_case"] = round(1000 * mas_seconds / max(len(cases), 1), 3)
    (out_dir / "reliability_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    log.close()
    spans.close()
    return decisions_path


def _print_contract_net(out_dir: Path) -> None:
    path = out_dir / "reliability_report.json"
    if not path.exists():
        return
    cnp = json.loads(path.read_text(encoding="utf-8")).get("contract_net")
    if not cnp:
        return
    enabled = cnp.get("budget_enabled", True)
    print("\n=== Contract Net hai pha (T7.1/T7.2) ===")
    print(f"  rang buoc ngan sach  : {'BAT' if enabled else 'TAT (cau hinh bao cao)'}")
    print(f"  phien dau thau       : {cnp['n_sessions']}")
    print(f"  khai bao / phien     : {cnp['avg_declared']}")
    print(f"  thang thau / phien   : {cnp['avg_accepted']}")
    print(f"  ty le loai           : {100 * cnp['rejection_rate']:.1f}%")
    ngan_sach = cnp["avg_budget_ms"]
    print(f"  ngan sach TB         : "
          f"{'khong rang buoc' if ngan_sach is None else f'{ngan_sach} ms'}")
    print(f"  chi phi TB           : {cnp['avg_spent_ms']} ms "
          f"({100 * cnp['avg_utilisation']:.1f}% ngan sach)")
    binds = cnp["budget_binds_rate"]
    print(f"  ngan sach RANG BUOC  : {100 * binds:.1f}% so phien")
    if not enabled:
        # Ngan sach tat CO CHU DICH — day la ghi chu, khong phai canh bao. Nhung no
        # van phai duoc in ra: mot nguoi doc bang `coordination.csv` can biet rang
        # pha 1 cua giao thuc dang chay ma khong quyet dinh gi.
        print("\n  (i) Ngan sach TAT theo cau hinh bao cao — quyet dinh pham vi 14/08.")
        print("      Moi analyst du dieu kien deu duoc goi; `allocate()` suy bien thanh")
        print("      ham hang va `REJECT_PROPOSAL` khong bao gio duoc phat. Pha 1 van")
        print("      ton message nhung KHONG quyet dinh gi — phai noi ro o Chuong 5.")
        print("      Bat lai bang `--budget` de chay phan tich do nhay.")
    elif binds < 0.01:
        print("\n  !! Ngan sach BAT nhung KHONG BAO GIO rang buoc trong lan chay nay.")
        print("     Giao thuc van chay dung hai pha, nhung bai toan phan bo khong")
        print("     quyet dinh gi — moi analyst deu duoc goi. Nguyen nhan thuong gap:")
        print("     chi phi khai bao cua cause_head thap hon nhieu so voi BERTimbau.")
        print("     Con so 've phan bo tinh toan' vi vay CHUA dung duoc cho RQ3.")


def _print_reliability(out_dir: Path) -> None:
    path = out_dir / "reliability_report.json"
    if not path.exists():
        return
    rel = json.loads(path.read_text(encoding="utf-8"))
    print("\n=== Tang chiu loi ===")
    print(f"  trang thai           : {'BAT' if rel['reliability_enabled'] else 'TAT (ablation)'}")
    print(f"  guard chan           : {len(rel['guard_violations'])} lan")
    print(f"  breaker mo           : {sum(b['opened_count'] for b in rel['breakers'])} lan")
    print(f"  lenh goi tiet kiem   : {rel['skipped_calls']}")
    cov = rel.get("monitoring_coverage", [])
    if cov:
        installed = sum(c["installed"] for c in cov)
        print(f"  pham vi giam sat     : {installed}/{len(cov)} thanh phan")
        for c in cov:
            mark = "co  " if c["installed"] else "KHONG"
            print(f"      {mark} {c['component']:16s} n={c['n_samples']:5d} — {c['reason']}")
    for alert in rel["health_alerts"]:
        print(f"  canh bao: {alert['component']}.{alert['metric']} sau "
              f"{alert['at_observation']} quan sat")
        print(f"      {alert['detail']}")


def summarize(out_dir: Path, inject: str | None = None) -> None:
    decisions = [json.loads(line) for line in
                 (out_dir / "decisions.jsonl").read_text(encoding="utf-8").splitlines()]
    baselines = [json.loads(line) for line in
                 (out_dir / "baselines.jsonl").read_text(encoding="utf-8").splitlines()]
    n = len(decisions)

    print(f"\n=== MAS-DSS ({n} case) ===")
    print(f"  can nguoi xem lai      : {sum(d['needs_human_review'] for d in decisions)}")
    print(f"  suy giam (level > 0)   : {sum(d['degradation_level'] > 0 for d in decisions)}")
    print(f"  da nguyen nhan         : {sum(d['multi_cause'] for d in decisions)}")
    print(f"  khong quy ket duoc     : {sum(not d['causes'] for d in decisions)}")
    actions = pd.Series([d["action"] for d in decisions]).value_counts()
    print("  hanh dong:")
    for name, count in actions.items():
        print(f"      {name:32s} {count}")

    print(f"\n=== Monolithic-Complete ({n} case) ===")
    silent = sum(b["monolithic_silent_failure"] for b in baselines)
    print(f"  buoc that bai          : {sum(bool(b['monolithic']['failed_steps']) for b in baselines)}")
    print(f"  HONG AM THAM           : {silent}  ({100 * silent / n:.1f}%)")
    if inject:
        print(f"     (da chiu CUNG kich ban loi '{inject}' voi MAS-DSS — T9.3)")
    print(f"  da nguyen nhan         : {sum(len(set(b['monolithic']['causes'])) >= 2 for b in baselines)}")

    if inject:
        from masdss.core.components import normalize_target
        from masdss.evaluation.resilience import compare

        component = normalize_target(inject.split(":")[1]) if ":" in inject else None
        print("\n=== RQ1(a): hong am tham duoi CUNG kich ban loi ===")
        print(f"  thanh phan bi tiem loi: {component}")
        for report in compare(decisions, baselines, component):
            print("  " + report.describe())
        print("\n  Dinh nghia dua tren SU THAT NEN cua thi nghiem (ta biet da tiem vao dau),")
        print("  khong dua tren viec he thong tu bao cao la no hong — mot he hong am tham")
        print("  se luon tu bao cao la binh thuong.")

    _print_reliability(out_dir)
    _print_contract_net(out_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Chay MAS-DSS tren du lieu that")
    parser.add_argument("--out", type=Path, default=CONFIG.paths.runs / "stage2")
    parser.add_argument("--stage", type=int, default=2, choices=[1, 2])
    parser.add_argument("--n", type=int, default=300)
    parser.add_argument("--text-cost-ms", type=float, default=None,
                        help="MO PHONG chi phi analyst van ban (BERTimbau ~45ms) "
                             "de kiem chung co che phan bo ngan sach")
    parser.add_argument("--no-reliability", action="store_true",
                        help="tat tang chiu loi — duong ablation cho RQ1")
    parser.add_argument("--no-refuse", action="store_true",
                        help="cam analyst phat REFUSE — duong ablation cho DP3")
    parser.add_argument("--budget", action="store_true",
                        help="bat rang buoc ngan sach Contract Net (mac dinh TAT — "
                             "xem plan.BUDGET_ENABLED_BY_DEFAULT). Dung cho phan tich "
                             "do nhay, khong phai cau hinh bao cao.")
    parser.add_argument("--budget-scale", type=float, default=None,
                        help="nhan ngan sach voi mot he so; chi co tac dung khi --budget")
    parser.add_argument("--inject", default=None,
                        help="crash:Agent | transient:Agent | constant:Agent | bias:Agent")
    args = parser.parse_args()

    path = asyncio.run(run(args.out, stage=args.stage, n_cases=args.n, inject=args.inject,
                           reliability=not args.no_reliability,
                           allow_refuse=not args.no_refuse,
                           budget=args.budget, budget_scale=args.budget_scale,
                           text_cost_ms=args.text_cost_ms))
    summarize(args.out, args.inject)
    print(f"\ndecisions -> {path}")


if __name__ == "__main__":
    main()
