"""WP11 / T11.3 — Bon duong ablation cho bon nguyen ly thiet ke.

    python -m masdss.cli.run_ablations

VI SAO LENH NAY TON TAI. Tieu chi hoan thanh cua MT2.3 doi moi nguyen ly phai co
**mot co che cuong che trong ma nguon** VA **mot thi nghiem ablation** — de nguyen
ly duoc KIEM CHUNG chu khong chi duoc PHAT BIEU. Truoc lenh nay, ba trong bon con
so ablation chi ton tai trong van ban tai lieu, hoac duoc do tren bo nhan tam nen
mang co `citable = False`.

BON DUONG, va moi duong go DUNG MOT co che:

  DP1  suy giam minh bach   -> `reliability=False`: go ca tang chiu loi, chay LAI
                               cung kich ban loi. Neu ty le hong am tham khong doi
                               thi thang suy giam khong mua duoc gi.
  DP2  da nhan, canh tranh  -> doi chung don khoi DA NHAN, cung nguong, cung head.
                               Do bang SO DON hai he cho ket qua khac nhau.
  DP3  tu choi thay vi doan -> `allow_refuse=False`: cam moi analyst phat REFUSE,
                               buoc chung tra loi ke ca khi khong co bang chung.
  DP4  nguon goc tu giao tiep -> dung trace theo hai cach roi do DO PHAN KY.

MOT LUU Y VE DP1. Ablation cua no chi co nghia DUOI DIEU KIEN LOI — chay duong khoe
roi tat tang chiu loi thi khong co gi de bat, va con so 0 se bi doc nham thanh "tang
chiu loi vo dung". Vi vay DP1 chay tren kich ban `byzantine`, dung nhom loi ma
`try/except` khong giup gi.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

import pandas as pd

from masdss.config import CONFIG


def _dp4_trace_divergence(run_dir: Path, out: Path) -> dict:
    """DP4 — do phan ky giua trace dung tu nhat ky va trace viet tay."""
    from masdss.evaluation import trace_divergence

    report = trace_divergence.compare(run_dir)
    report.per_kind.to_csv(out / "ablation_dp4_trace_divergence.csv",
                           index=False, encoding="utf-8-sig")

    day_du, viet_tay = trace_divergence.worked_example(run_dir)
    (out / "ablation_dp4_vi_du.txt").write_text(
        "=== TRACE DUNG TU NHAT KY ===\n" + day_du
        + "\n\n=== TRACE VIET TAY TU `Decision` ===\n" + viet_tay + "\n",
        encoding="utf-8")

    return {
        "nguyen_ly": "DP4",
        "ten": "nguon goc tu giao tiep",
        "co_che_bi_go": "trace dung tu `Decision` thay vi tu nhat ky message",
        "chi_so": "do phan ky",
        "co_co_che": round(0.0, 4),
        "go_co_che": round(report.divergence_rate, 4),
        "ghi_chu": (f"{report.n_conversations} hoi thoai · {report.n_log_events} su kien "
                    f"that · {report.n_handwritten_events} bieu dien duoc"),
    }


def _dp3_no_refuse(gold, run_root: Path, out: Path, capabilities, orders) -> dict:
    """DP3 — cam quyen tu choi, do cai gia."""
    from masdss.cli.run_attribution import (_predictions_from_baseline,
                                            _predictions_from_decisions)
    from masdss.cli.run_system import run
    from masdss.evaluation import attribution, selective

    order_ids = set(gold.frame["order_id"])
    run_dir = run_root / "dp3_no_refuse"
    asyncio.run(run(run_dir, stage=2, orders=orders, capabilities=capabilities,
                    order_ids=order_ids, allow_refuse=False))

    predictions = {
        "MAS-DSS": _predictions_from_decisions(run_dir / "decisions.jsonl"),
        "Monolithic-Complete": _predictions_from_baseline(
            run_dir / "baselines.jsonl", "monolithic"),
    }
    result = attribution.evaluate(gold, predictions)
    per_cause, per_slice = result.stamped()
    per_cause.to_csv(out / "ablation_dp3_per_cause.csv", index=False, encoding="utf-8-sig")
    per_slice.to_csv(out / "ablation_dp3_per_slice.csv", index=False, encoding="utf-8-sig")
    _, summary = selective.report(gold, predictions)
    summary.to_csv(out / "ablation_dp3_selective.csv", index=False, encoding="utf-8-sig")

    mas = summary[summary["he_thong"] == "MAS-DSS"].iloc[0]
    return {
        "nguyen_ly": "DP3",
        "ten": "tu choi thay vi doan",
        "co_che_bi_go": "performative REFUSE cua analyst",
        "chi_so": "quy ket SAI khi con nguoi bo trong",
        "go_co_che": round(float(mas["quy_ket_sai_khi_nguoi_bo_trong"]), 4),
        "ghi_chu": (f"do phu {mas['do_phu']:.4f} · macro-F1 toan bo "
                    f"{mas['f1_toan_bo']:.4f} · tren phan da tra loi "
                    f"{mas['f1_da_tra_loi']:.4f}"),
    }


def _dp1_no_reliability(out: Path, run_root: Path, n_cases: int) -> dict:
    """DP1 — go tang chiu loi, chay LAI cung kich ban loi Byzantine."""
    from masdss.chaos.runner import Baseline, _read, run_scenario
    from masdss.chaos.scenarios import ALL_SCENARIOS, HEALTHY
    from masdss.data.export import load_stage
    from masdss.system.app import Capabilities

    byzantine = next(s for s in ALL_SCENARIOS
                     if s.group == "byzantine_gross" and s.level == 2)

    orders = load_stage("t4", "test")
    t4_train, t4_val = load_stage("t4", "train"), load_stage("t4", "val")
    t3_train, t3_val = load_stage("t3", "train"), load_stage("t3", "val")
    capabilities = Capabilities.fit(t4_train, t4_val,
                                    risk_train=t3_train, risk_val=t3_val)

    async def _go(reliability: bool):
        root = run_root / ("dp1_on" if reliability else "dp1_off")
        await run_scenario(HEALTHY, root, n_cases=n_cases, orders=orders,
                           capabilities=capabilities, reliability=reliability)
        decisions, baselines, _ = _read(root / HEALTHY.id)
        base = Baseline.of(decisions, baselines)
        return await run_scenario(byzantine, root, n_cases=n_cases, orders=orders,
                                  capabilities=capabilities, baseline=base,
                                  reliability=reliability)

    bat = asyncio.run(_go(True))
    tat = asyncio.run(_go(False))

    def pct(result) -> float:
        return round(100.0 * result.mas_silent / result.n_cases, 2)

    pd.DataFrame([
        {"tang_chiu_loi": "BAT", "kich_ban": byzantine.id, "n_case": bat.n_cases,
         "quyet_dinh_doi": bat.mas_changed, "hong_am_tham": bat.mas_silent,
         "hong_am_tham_pct": pct(bat), "guard_chan": bat.guard_blocks,
         "case_suy_giam": bat.mas_degraded, "phat_hien": bat.detected},
        {"tang_chiu_loi": "TAT", "kich_ban": byzantine.id, "n_case": tat.n_cases,
         "quyet_dinh_doi": tat.mas_changed, "hong_am_tham": tat.mas_silent,
         "hong_am_tham_pct": pct(tat), "guard_chan": tat.guard_blocks,
         "case_suy_giam": tat.mas_degraded, "phat_hien": tat.detected},
    ]).to_csv(out / "ablation_dp1_chiu_loi.csv", index=False, encoding="utf-8-sig")

    return {
        "nguyen_ly": "DP1",
        "ten": "suy giam minh bach",
        "co_che_bi_go": "tang chiu loi (guard · breaker · thang suy giam)",
        "chi_so": "ty le hong am tham (%) duoi loi Byzantine",
        "co_co_che": pct(bat),
        "go_co_che": pct(tat),
        "ghi_chu": (f"{bat.mas_changed} vs {tat.mas_changed} quyet dinh doi · "
                    f"guard chan {bat.guard_blocks} vs {tat.guard_blocks}"),
    }


def _dp2_from_attribution(out: Path) -> dict:
    """DP2 — doc lai ket qua doi dau da sinh boi `run_attribution`."""
    path = out / "attribution_compare.csv"
    if not path.exists():
        return {"nguyen_ly": "DP2", "ten": "da nhan, canh tranh khi tham quyen chong lap",
                "co_che_bi_go": "—", "chi_so": "so o bat dong giua hai kien truc",
                "ghi_chu": "chua chay `run_attribution` — khong co so"}
    row = pd.read_csv(path, encoding="utf-8-sig").iloc[0]
    return {
        "nguyen_ly": "DP2",
        "ten": "da nhan, canh tranh khi tham quyen chong lap",
        "co_che_bi_go": "so voi doi chung don khoi DA NHAN, cung head, cung nguong",
        "chi_so": "so o bat dong giua hai kien truc",
        "co_co_che": float(row["n_o_bat_dong"]),
        "go_co_che": float(row["n_o_bat_dong"]),
        "ghi_chu": (f"chenh lech macro-F1 = {row['chenh_lech_macro_f1']} · "
                    f"KTC [{row['ci_lower']}; {row['ci_upper']}] · "
                    f"{int(row['n_don'])} don"),
    }


def main() -> None:
    goldset = CONFIG.paths.derived / "goldset"
    parser = argparse.ArgumentParser(description="T11.3 — bon ablation cho bon DP")
    parser.add_argument("--gold", type=Path, default=goldset / "gold_labels.csv")
    parser.add_argument("--run", type=Path, default=CONFIG.paths.runs / "goldset_v3")
    parser.add_argument("--run-root", type=Path, default=CONFIG.paths.runs / "ablations")
    parser.add_argument("--out", type=Path, default=CONFIG.paths.derived / "evaluation")
    parser.add_argument("--n", type=int, default=200,
                        help="so case cho ablation DP1 (chay duoi tiem loi)")
    parser.add_argument("--only", default=None, choices=("dp1", "dp2", "dp3", "dp4"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    args.run_root.mkdir(parents=True, exist_ok=True)

    from masdss.cli.build_goldset import meta_path
    from masdss.data.labels import Provenance, load_gold_labels

    meta = meta_path(args.gold)
    if not meta.exists():
        raise SystemExit(f"Thieu tep meta cho {args.gold.name}: can {meta.name}")
    provenance = Provenance(json.loads(meta.read_text(encoding="utf-8"))["provenance"])
    gold = load_gold_labels(args.gold, provenance=provenance)

    CONFIG.seed_everything()
    pd.set_option("display.width", 220)
    print("=" * 78)
    print("T11.3 — BON DUONG ABLATION CHO BON NGUYEN LY THIET KE")
    print("=" * 78)
    print(provenance.banner)

    rows = []

    if args.only in (None, "dp4"):
        print("\n[DP4] do phan ky trace ...")
        rows.append(_dp4_trace_divergence(args.run, args.out))

    if args.only in (None, "dp2"):
        print("[DP2] doc lai ket qua doi dau ...")
        rows.append(_dp2_from_attribution(args.out))

    if args.only in (None, "dp3"):
        print("[DP3] chay lai gold set voi REFUSE bi cam ...")
        from masdss.data.export import load_stage
        from masdss.system.app import Capabilities

        orders = load_stage("t4", "test")
        t4_train, t4_val = load_stage("t4", "train"), load_stage("t4", "val")
        t3_train, t3_val = load_stage("t3", "train"), load_stage("t3", "val")
        capabilities = Capabilities.fit(t4_train, t4_val,
                                        risk_train=t3_train, risk_val=t3_val,
                                        cause_head="tfidf",
                                        exclude_order_ids=set(gold.frame["order_id"]))
        rows.append(_dp3_no_refuse(gold, args.run_root, args.out, capabilities, orders))

    if args.only in (None, "dp1"):
        print(f"[DP1] chay Byzantine voi tang chiu loi BAT/TAT ({args.n} case) ...")
        rows.append(_dp1_no_reliability(args.out, args.run_root, args.n))

    table = pd.DataFrame(rows)
    table["provenance"] = provenance.value
    table["citable"] = provenance.citable

    # `--only` GOP vao bang cu thay vi ghi de. Neu ghi de, chay lai mot duong ablation
    # se lang le xoa ba duong con lai, va bang trong luan van chi con mot dong ma
    # khong co gi bao. Sap theo thu tu DP de bang on dinh giua cac lan chay.
    path = args.out / "ablations.csv"
    if args.only and path.exists():
        cu = pd.read_csv(path, encoding="utf-8-sig")
        cu = cu[~cu["nguyen_ly"].isin(table["nguyen_ly"])]
        table = pd.concat([cu, table], ignore_index=True)
    table = table.sort_values("nguyen_ly").reset_index(drop=True)
    table.to_csv(path, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 78)
    print(table.drop(columns=["provenance"]).to_string(index=False))
    print("=" * 78)
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
