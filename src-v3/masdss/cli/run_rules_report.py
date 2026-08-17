"""WP11 — Tap luat ho tro quyet dinh: danh muc va hieu qua do duoc.

    python -m masdss.cli.run_rules_report

VI SAO LENH NAY TON TAI. Chuoi quyet dinh cua luan van co ba khau — du bao tai T3,
quy ket tai T4, roi DE XUAT HANH DONG theo tap luat. Hai khau dau da co bang so
rieng (`forecasting.csv`, `attribution_per_*.csv`); khau thu ba thi chua, nen phan
"tu do goi y hanh dong" moi chi duoc MO TA chu chua duoc DO.

BA BANG DUOC SINH:

  1_danh_muc      — tung luat: dieu kien, hanh dong, chi phi, ly do. Trich thang tu
                    `config/v3/rules.yaml` de bang trong luan van khong bao gio lech
                    khoi tap luat dang chay.
  2_t4_theo_luat  — o moc QUY KET: luat nao thuc su khop, tren bao nhieu don, va
                    hanh dong ket cuc la gi. Dung bang cach CHAY LAI rule engine tren
                    `decisions.jsonl`, khong doan tu ten hanh dong.
  3_t3_thang_hanh_dong — o moc DU BAO: do phu, ty le bat dung, va LIFT cua tung muc
                    can thiep tren toan bo tong the T3 test.

MOT LUU Y VE RANG BUOC C1. Bang 3 do CHAT LUONG KHUYEN NGHI — he thong co de xuat
dung loai hanh dong cho dung nhom don hay khong — chu KHONG do HIEU QUA CAN THIEP.
Bo du lieu Olist khong co bien treatment va khong co ket cuc phan thuc, nen moi phat
bieu dang "hanh dong nay giam bat man X%" deu vuot qua du lieu (ch3 §3.2.3).
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd
import yaml

from masdss.config import CONFIG


def _catalogue(path: Path) -> pd.DataFrame:
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    costs = {name: float(v.get("cost", 0.0)) for name, v in spec["actions"].items()}
    rows = []
    for kind, key in (("cuong che", "enforced"), ("thuong", "rules")):
        for rule in spec.get(key, []):
            rows.append({
                "loai": kind,
                "ma_luat": rule["id"],
                "moc": ("T3" if '"T3"' in rule["when"]
                        else "T4" if '"T4"' in rule["when"] else "ca hai"),
                "dieu_kien": rule["when"].strip(),
                "hanh_dong": rule["action"],
                "chi_phi": costs.get(rule["action"], 0.0),
                "ly_do": " ".join(rule.get("reason", "").split()),
            })
    rows.append({
        "loai": "mac dinh", "ma_luat": "default_action", "moc": "ca hai",
        "dieu_kien": "khong luat nao khop", "hanh_dong": spec["default_action"],
        "chi_phi": costs.get(spec["default_action"], 0.0),
        "ly_do": "hanh dong mac dinh khi khong luat nao khop",
    })
    return pd.DataFrame(rows)


def _t4_by_rule(run_dir: Path, engine) -> pd.DataFrame:
    """Luat nao thuc su khop o moc quy ket, va tren bao nhieu don.

    CHAY LAI rule engine tren tung quyet dinh thay vi suy tu ten hanh dong: nhieu
    luat cung tro toi mot hanh dong (`preemptive_ticket_open` co ba nguon), nen suy
    nguoc tu hanh dong se gop nham chung lai.
    """
    from masdss.capabilities.rules import facts_from

    decisions = [json.loads(line) for line in
                 (run_dir / "decisions.jsonl").read_text(encoding="utf-8").splitlines()]

    counter: Counter[tuple] = Counter()
    for d in decisions:
        causes = sorted(c["cause"] if isinstance(c, dict) else str(c)
                        for c in (d.get("causes") or []))
        facts = facts_from(risk=int(d["risk"]), causes=causes,
                           degradation_level=int(d["degradation_level"]),
                           decision_point=str(d["decision_point"]))
        outcome = engine.decide(facts)
        nhom = "+".join(causes) if causes else "(khong quy ket)"
        counter[(outcome.rule_id, outcome.action, nhom)] += 1

    n = len(decisions)
    rows = [{"ma_luat": rule, "hanh_dong": action, "nhom_nguyen_nhan": nhom,
             "so_don": count, "ty_le": round(count / n, 4)}
            for (rule, action, nhom), count in counter.items()]
    frame = pd.DataFrame(rows).sort_values(["so_don"], ascending=False)
    return frame.reset_index(drop=True)


def _t3_action_ladder(engine) -> pd.DataFrame:
    """Thang hanh dong o moc du bao, kem LIFT so voi ty le nen.

    Lift la cot quan trong nhat: mot muc can thiep phu 30% tong the ma chi bat duoc
    30% so don bat man thi no khong chon loc gi — bang dung ngau nhien.
    """
    import numpy as np

    from masdss.capabilities.rules import facts_from
    from masdss.core.ontology import DecisionPoint, OrderCase
    from masdss.data.export import load_stage
    from masdss.data.featureset import FeatureSet
    from masdss.system.app import Capabilities

    test = load_stage("t3", "test")
    t4_train, t4_val = load_stage("t4", "train"), load_stage("t4", "val")
    t3_train, t3_val = load_stage("t3", "train"), load_stage("t3", "val")
    capabilities = Capabilities.fit(t4_train, t4_val,
                                    risk_train=t3_train, risk_val=t3_val)

    feature_set = FeatureSet(DecisionPoint.T3)
    columns = [c for c in feature_set.names if c in test.columns]
    scores = capabilities.risk_model.predict_proba(test)
    y = test["is_dissatisfied"].astype(int).to_numpy()
    base_rate = float(y.mean())

    counter: Counter[tuple] = Counter()
    hits: Counter[tuple] = Counter()
    costs = {}
    for i, (_, row) in enumerate(test.iterrows()):
        case = OrderCase(case_id=str(row["order_id"]), decision_point=DecisionPoint.T3,
                         features={c: row[c] for c in columns})
        risk = int(capabilities.risk_model.to_risk_level(float(scores[i])))
        facts = facts_from(
            risk=risk, causes=[], degradation_level=0, decision_point="T3",
            context={
                "days_to_deadline": row.get("days_to_deadline"),
                "delivery_state": row.get("delivery_state"),
                "order_value": float(row.get("price", 0.0))
                + float(row.get("freight_value", 0.0)),
                "is_late": bool(row.get("days_to_deadline", 0) < 0),
            })
        outcome = engine.decide(facts)
        key = (outcome.rule_id, outcome.action)
        counter[key] += 1
        hits[key] += int(y[i])
        costs[outcome.action] = engine.action_cost(outcome.action) \
            if hasattr(engine, "action_cost") else 0.0

    n = len(test)
    n_dissatisfied = int(y.sum())
    rows = []
    for (rule, action), count in counter.most_common():
        caught = hits[(rule, action)]
        precision = caught / count if count else 0.0
        rows.append({
            "ma_luat": rule, "hanh_dong": action,
            "so_don": count, "do_phu": round(count / n, 4),
            "bat_dung": caught,
            "recall_tren_don_bat_man": round(caught / n_dissatisfied, 4),
            "precision": round(precision, 4),
            "lift": round(precision / base_rate, 3) if base_rate else float("nan"),
        })
    frame = pd.DataFrame(rows)
    frame.attrs["base_rate"] = base_rate
    frame.attrs["n"] = n
    frame.attrs["n_dissatisfied"] = n_dissatisfied
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(description="WP11 — bang tap luat ho tro quyet dinh")
    parser.add_argument("--rules", type=Path,
                        default=Path("config/v3/rules.yaml"))
    parser.add_argument("--run", type=Path, default=CONFIG.paths.runs / "goldset_v3")
    parser.add_argument("--out", type=Path, default=CONFIG.paths.derived / "evaluation")
    parser.add_argument("--skip-t3", action="store_true",
                        help="bo qua bang 3 (cham vi phai cham diem toan bo tong the)")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    from masdss.capabilities.rules import RuleEngine

    CONFIG.seed_everything()
    pd.set_option("display.width", 240)
    pd.set_option("display.max_colwidth", 64)
    engine = RuleEngine.load(args.rules)

    print("=" * 78)
    print("TAP LUAT HO TRO QUYET DINH — danh muc va hieu qua do duoc")
    print("=" * 78)

    catalogue = _catalogue(args.rules)
    catalogue.to_csv(args.out / "rules_1_danh_muc.csv", index=False, encoding="utf-8-sig")
    print("\n[1] Danh muc luat")
    print(catalogue.drop(columns=["ly_do"]).to_string(index=False))

    by_rule = _t4_by_rule(args.run, engine)
    by_rule.to_csv(args.out / "rules_2_t4_theo_luat.csv", index=False, encoding="utf-8-sig")
    print("\n[2] Moc T4 — luat nao khop, tren nhom nguyen nhan nao")
    print(by_rule.to_string(index=False))

    if not args.skip_t3:
        ladder = _t3_action_ladder(engine)
        ladder.to_csv(args.out / "rules_3_t3_thang_hanh_dong.csv",
                      index=False, encoding="utf-8-sig")
        print(f"\n[3] Moc T3 — thang hanh dong tren {ladder.attrs['n']} don "
              f"(ty le nen {ladder.attrs['base_rate']:.4f}, "
              f"{ladder.attrs['n_dissatisfied']} don bat man)")
        print(ladder.to_string(index=False))

    print("\n" + "=" * 78)
    print("RANG BUOC C1: bang tren do CHAT LUONG KHUYEN NGHI, KHONG do hieu qua can")
    print("thiep. Olist khong co bien treatment va khong co ket cuc phan thuc.")
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
