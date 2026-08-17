"""WP10 / T11.1 — Sinh bang so cho Chuong 5 bang MOT lenh.

Chay:
    python -m masdss.cli.run_evaluation

Sinh ra trong data/v3/evaluation/:
    forecasting.csv          T10.1 — PR-AUC/ROC-AUC kem khoang tin cay
    threshold_sensitivity.csv T10.1 — do nhay nguong nhan <=2 vs <=3
    control_condition.txt     T10.1 — kiem tra dac ta H1
    coordination.csv          T10.4 — chi phi va loi ich cua phoi hop
    coordination_detail.csv   T10.4 — theo tung case
    cost_*.csv                T10.6 — chi phi kien truc

BA NHOM CHI SO NAY KHONG CAN GOLD SET. Hai nhom con lai — quy ket nguyen nhan
(T10.2) va selective prediction (T10.3) — CAN gold set nen nam o lenh rieng
`run_attribution`, va ket qua cua chung mang theo co `citable` theo nguon goc nhan.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from masdss.config import CONFIG


def main() -> None:
    parser = argparse.ArgumentParser(description="Sinh bang so cho Chuong 5")
    parser.add_argument("--run", type=Path, default=CONFIG.paths.runs / "stage2",
                        help="thu muc mot lan chay he thong")
    parser.add_argument("--out", type=Path, default=CONFIG.paths.derived / "evaluation")
    parser.add_argument("--boot", type=int, default=1000)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    from masdss.data.export import load_stage
    from masdss.evaluation import coordination, cost, forecasting
    from masdss.system.app import Capabilities

    CONFIG.seed_everything()
    pd.set_option("display.width", 200)

    # ---------- T10.1: du bao ----------
    print("=" * 72)
    print("T10.1 — DU BAO (H1: dieu kien kiem soat)")
    print("=" * 72)

    # Du bao duoc cham diem tren tong the T3 — nhung don CON KIP CAN THIEP. Cham
    # diem tren tong the day du la doc lai mot ket cuc da co voi 23,5% so don (L33).
    t3_train, t3_val = load_stage("t3", "train"), load_stage("t3", "val")
    # `rating` duoc xin TUONG MINH cho tap test: phan tich do nhay nguong nhan
    # (`<= 2` so voi `<= 3`) can chinh cot nguon sinh ra nhan. Moi noi khac khong
    # duoc keo no vao — do la ly do `load_stage` mac dinh chi tra `is_dissatisfied`.
    test = load_stage("t3", "test", labels=("is_dissatisfied", "rating"))
    t4_train, t4_val = load_stage("t4", "train"), load_stage("t4", "val")
    capabilities = Capabilities.fit(t4_train, t4_val,
                                    risk_train=t3_train, risk_val=t3_val)
    scores = capabilities.risk_model.predict_proba(test)
    y_true = test["is_dissatisfied"].astype(int).to_numpy()

    metrics = forecasting.evaluate(y_true, scores, seed=CONFIG.seed, n_boot=args.boot)
    metrics.to_csv(args.out / "forecasting.csv", index=False, encoding="utf-8-sig")
    print(metrics.to_string(index=False))

    # Kiem tra dac ta: hai kien truc phai dung CHUNG MOT mo hinh.
    from masdss.baselines.simple import SingleMLBaseline
    from masdss.core.ontology import DecisionPoint, OrderCase
    from masdss.data.featureset import FeatureSet

    feature_set = FeatureSet(DecisionPoint.T3)
    columns = [c for c in feature_set.names if c in test.columns]
    sample = test.head(200)
    single = SingleMLBaseline(capabilities)
    cases = [OrderCase(case_id=str(r["order_id"]), decision_point=DecisionPoint.T3,
                       features={c: r[c] for c in columns})
             for _, r in sample.iterrows()]
    mas_scores = np.array([capabilities.risk_model.run(c) for c in cases])
    single_scores = np.array([single.run(c).score for c in cases])

    control = forecasting.verify_shared_capability(mas_scores, single_scores)

    # KIEM DINH TUONG DUONG (TOST) — bien tuong duong 0,01 KHAI BAO TRUOC (ch3 §3.6.3).
    #
    # `verify_shared_capability` chi so sanh tung bit, nen no tra loi "co giong het
    # khong" chu khong tra loi "co tuong duong trong bien da khai bao khong". Hai cau
    # hoi khac nhau, va ch3 dac ta cau thu hai. Ham TOST da ton tai tu truoc nhung ket
    # qua cua no chua bao gio duoc xuat ra tep — tuc mot phep kiem dinh da khai bao ma
    # khong co artifact nao chung minh no da chay.
    tost = forecasting.tost_equivalence(mas_scores, single_scores)
    pd.DataFrame([{
        "phep_do": "PR-AUC score tai T3 — MAS-DSS vs Single-ML",
        "n": len(mas_scores),
        "bien_tuong_duong": forecasting.DEFAULT_EQUIVALENCE_MARGIN,
        "chenh_lech_tb": round(float(tost.mean_difference), 8),
        "ci_lower": round(float(tost.lower), 8),
        "ci_upper": round(float(tost.upper), 8),
        "tuong_duong": bool(tost.equivalent),
        "giong_het": bool(control.identical),
        "loai_bang_chung": "kiem tra dac ta",
        "ghi_chu": tost.note,
    }]).to_csv(args.out / "control_condition.csv", index=False, encoding="utf-8-sig")

    text = (
        "DIEU KIEN KIEM SOAT (H1)\n"
        f"{control.describe()}\n\n{control.note}\n\n"
        f"TOST (bien +/-{forecasting.DEFAULT_EQUIVALENCE_MARGIN}, khai bao truoc): "
        f"{'TUONG DUONG' if tost.equivalent else 'CHUA KET LUAN'}\n"
        f"  {tost.note}\n\n"
        "H1 khai bao truoc rang KY VONG VO HIEU, va do la dieu mong muon: neu hai\n"
        "kien truc khac nhau ve nang luc du bao thi moi khac biet quan sat duoc o cac\n"
        "chi so khac khong quy duoc cho kien truc.\n"
    )
    (args.out / "control_condition.txt").write_text(text, encoding="utf-8")
    print(f"\n{control.describe()}")
    print(f"  {control.note}")
    print(f"  TOST: {'TUONG DUONG' if tost.equivalent else 'CHUA KET LUAN'} — {tost.note}")

    sensitivity = forecasting.threshold_sensitivity(test, scores)
    sensitivity.to_csv(args.out / "threshold_sensitivity.csv", index=False,
                       encoding="utf-8-sig")
    print("\nDo nhay nguong dinh nghia nhan:")
    print(sensitivity.to_string(index=False))

    threshold, expected_cost = forecasting.cost_optimal_threshold(y_true, scores)
    print(f"\nNguong quyet dinh theo chi phi: {threshold:.3f} "
          f"(chi phi ky vong {expected_cost:.0f}; mac dinh 0,5 KHONG toi uu vi lop "
          f"mat can bang va hai loai sai co gia khac nhau)")

    # ---------- T10.4: phoi hop ----------
    if (args.run / "messages.sqlite").exists():
        print("\n" + "=" * 72)
        print("T10.4 — PHOI HOP (MIS va Single-ML khong du tu cach tham gia)")
        print("=" * 72)
        summary, detail = coordination.report(args.run)
        summary.to_csv(args.out / "coordination.csv", index=False, encoding="utf-8-sig")
        detail.to_csv(args.out / "coordination_detail.csv", index=False,
                      encoding="utf-8-sig")
        print(summary.to_string(index=False))

        per_ms = coordination.attribution_per_ms(args.run)
        print(f"\nQuy ket / ms: {per_ms['causes_per_ms']}  "
              f"({per_ms['causes_found']} nguyen nhan / {per_ms['total_ms']} ms)")
        print(f"  !! {per_ms['caveat']}")

        # ---------- T10.6: chi phi ----------
        print("\n" + "=" * 72)
        print("T10.6 — CHI PHI KIEN TRUC (H5: khai bao truoc la KY VONG THUA)")
        print("=" * 72)
        src_root = Path(__file__).resolve().parents[1]
        tables = cost.report(args.run, src_root)
        for name, table in tables.items():
            table.to_csv(args.out / f"cost_{name}.csv", index=False, encoding="utf-8-sig")
            print(f"\n[{name}]")
            print(table.to_string(index=False))
    else:
        print(f"\nChua co ket qua chay he thong tai {args.run} — bo qua T10.4 va T10.6.")
        print("Chay truoc: python -m masdss.cli.run_system --stage 2 --n 300")

    print("\n" + "=" * 72)
    # Thong bao nay tung ghi "BI CHAN cho toi khi co gold set". Hai task do nay da
    # chay duoc; de nguyen cau cu se lam nguoi doc tuong chung chua ton tai.
    print("T10.2 (macro-F1 quy ket) va T10.3 (selective prediction) KHONG chay o day —")
    print("chung can gold set nen co lenh rieng, va ket qua mang theo co `citable`:")
    print("    python -m masdss.cli.run_attribution --gold <tep> --run <thu muc>")
    print("=" * 72)
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
