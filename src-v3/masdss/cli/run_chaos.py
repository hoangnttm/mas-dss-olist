"""WP9 / T9.2 — Chay toan bo chaos harness.

Chay:
    python -m masdss.cli.run_chaos --n 300

Sinh ra trong data/v3/chaos/:
    scenarios.csv          -> ket qua tung kich ban
    sensitivity_curve.csv  -> duong cong do nhay theo nhom va muc  <- RQ1(b)
    <scenario_id>/         -> dau ra chi tiet cua tung lan chay

Dau `*` truoc ten kich ban danh dau nhom loi ma guard KHONG duoc thiet ke rieng de
bat — chi nhung dong do moi mang thong tin moi.
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

import pandas as pd

from masdss.chaos.runner import run_all, sensitivity_curve
from masdss.chaos.scenarios import (ALL_SCENARIOS, MAS_ONLY_SCENARIOS,
                                    STAGE1_SCENARIOS, by_group)
from masdss.config import CONFIG


def main() -> None:
    parser = argparse.ArgumentParser(description="Chay chaos harness day du")
    parser.add_argument("--out", type=Path, default=CONFIG.paths.derived / "chaos")
    parser.add_argument("--n", type=int, default=300)
    parser.add_argument("--group", default=None,
                        help="chi chay mot nhom: crash | hang | byzantine_gross | drift | bias")
    parser.add_argument("--stage", type=int, default=2, choices=(1, 2),
                        help="moc quyet dinh: 1 = du bao @ T3, 2 = quy ket @ T4")
    parser.add_argument("--targets", default="shared", choices=("shared", "mas-only"),
                        help="be mat hong: `shared` = thanh phan ca hai kien truc deu "
                             "co · `mas-only` = 5 thanh phan chi MAS-DSS co")
    args = parser.parse_args()

    # H2 doi hoi CA HAI chieu: hai moc quyet dinh x hai be mat hong. Mot lan chay chi
    # phu MOT o cua bang do, va bang phai day du truoc khi phan quyet H2.
    if args.targets == "mas-only":
        scenarios = MAS_ONLY_SCENARIOS
    elif args.stage == 1:
        scenarios = STAGE1_SCENARIOS
    else:
        scenarios = ALL_SCENARIOS
    if args.group:
        scenarios = tuple(s for s in scenarios if s.group == args.group)

    be_mat = "5 thanh phan CHI MAS co" if args.targets == "mas-only" else "thanh phan dung chung"
    moc = "T3 du bao" if args.stage == 1 else "T4 quy ket"
    print(f"Giai doan {args.stage} @ {moc} · be mat: {be_mat}")
    print(f"Chay {len(scenarios)} kich ban + duong khoe, {args.n} case moi lan.\n")

    if args.targets == "mas-only":
        print("  LUU Y KHI DOC: `mono_silent` se bang 0 tren moi dong, va do KHONG phai")
        print("  chien thang cua MAS-DSS — kien truc don khoi khong co thanh phan nay de")
        print("  ma hong. Cot dang doc o day la `mas_silent`: guard cua MAS co phu duoc")
        print("  chinh phan be mat hong ma no tu tao ra hay khong.\n")

    table = asyncio.run(run_all(args.out, n_cases=args.n, scenarios=scenarios,
                                stage=args.stage))
    args.out.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.out / "scenarios.csv", index=False, encoding="utf-8-sig")

    curve = sensitivity_curve(table)
    curve.to_csv(args.out / "sensitivity_curve.csv", index=False, encoding="utf-8-sig")

    pd.set_option("display.width", 200)
    print("\n=== Ket qua tung kich ban ===")
    print(table[["scenario", "group", "level", "designed_for", "mas_changed_pct",
                 "mas_silent_pct", "mono_silent_pct", "detected",
                 "detection_latency"]].to_string(index=False))
    print("\n  mas_changed_pct = % case co dau ra KHAC duong chay khoe (tac dong that")
    print("  cua loi). mas_silent_pct la phan trong so do ma he KHONG canh bao gi.")

    healthy = table[table["group"] == "healthy"].iloc[0]
    print(f"\nDuong khoe: {healthy['mas_degraded_pct']}% case suy giam, "
          f"{healthy['guard_blocks']} guard chan, phat hien = {healthy['detected']}")
    print("  -> day la TY LE BAO DONG GIA. Phai bang 0 thi cac con so tren moi dung duoc.")

    print("\n=== Duong cong do nhay (RQ1b) ===")
    print(curve.to_string(index=False))
    print("\n  `designed_for = False` la hai nhom guard KHONG duoc thiet ke rieng de bat")
    print("  (drift, bias). Chi nhung dong do moi la ket qua thuc nghiem.")
    print(f"\n  -> {args.out / 'scenarios.csv'}")
    print(f"  -> {args.out / 'sensitivity_curve.csv'}")


if __name__ == "__main__":
    main()
