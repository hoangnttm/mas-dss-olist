"""WP10 / T10.2 + T10.3 — Chay ca hai kien truc tren gold set va do quy ket.

    python -m masdss.cli.run_attribution

Day la duong duy nhat sinh ra chi so CHINH cua RQ3. Bon dieu kien cong bang duoc
thiet lap ngay trong lenh nay, khong pho mac cho nguoi doc tin:

  1. CUNG cause head da huan luyen — MAS-DSS va Monolithic dung chung mot doi tuong.
  2. CUNG nguong `tau_cause`.
  3. Doi chung la bo phan loai DA NHAN, khong `argmax`.
  4. Cause head KHONG duoc huan luyen tren cac don nam trong gold set.

Khac biet duy nhat con lai la CACH TO CHUC — dau thau canh tranh, phan xu, quyen
tu choi, ngan sach tinh toan. Do dung la thu RQ3 hoi.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

import pandas as pd

from masdss.config import CONFIG
from masdss.data.labels import CAUSE_COLUMNS, Provenance, load_gold_labels


def _max_confidence(value, fallback: dict | None = None) -> float:
    """Do tin cay CAO NHAT trong so cac nguyen nhan da phat; 0,0 neu khong phat gi.

    Duong risk-coverage (T10.3) xep hang case theo do tin cay cua CHINH he thong dang
    duoc cham diem, nen ca hai kien truc deu phai cung cap dai luong nay. MAS-DSS ghi
    `probability` ngay trong `decisions.jsonl`; doi chung ghi o truong `confidences`.

    Lay MAX chu khong lay trung binh: dai luong can la "he thong tu tin den dau ve
    ket luan no dua ra", va mot quy ket chac chan khong bi lam nhat di boi mot quy
    ket yeu di kem.
    """
    best = 0.0
    for item in value or ():
        if isinstance(item, dict) and item.get("probability") is not None:
            best = max(best, float(item["probability"]))
        elif fallback:
            name = str(item["cause"]) if isinstance(item, dict) else str(item)
            best = max(best, float(fallback.get(name, 0.0)))
    return best


def _cause_names(value) -> set[str]:
    """Chuan hoa truong `causes` ve mot tap ten.

    HAI ARTIFACT CUA CUNG MOT LAN CHAY BIEU DIEN KHAC NHAU, va do la mot bat nhat
    that phat hien duoc nho chay het chu trinh:

        decisions.jsonl  (MAS)        -> [{"cause": "delivery", "probability": 0.63}]
        baselines.jsonl  (Monolithic) -> ["delivery"]

    Ca hai deu hop ly rieng le — MAS mang theo xac suat vi Chuong 5 can no. Cai
    khong hop ly la de nguoi doc phai biet truoc dang nao thuoc tep nao. Ham nay
    nhan ca hai, va `test_output_invariants` canh cho de dang thu ba khong len.
    """
    names = set()
    for item in value or ():
        names.add(str(item["cause"]) if isinstance(item, dict) else str(item))
    return names


def _predictions_from_decisions(path: Path) -> pd.DataFrame:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        decision = json.loads(line)
        causes = _cause_names(decision["causes"])
        row = {"order_id": decision["case_id"],
               "confidence": _max_confidence(decision["causes"])}
        for column in CAUSE_COLUMNS:
            row[column] = int(column.replace("cause_", "") in causes)
        rows.append(row)
    return pd.DataFrame(rows)


def _predictions_from_baseline(path: Path, name: str) -> pd.DataFrame:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        block = record.get(name, {})
        raw = block.get("causes", [])
        causes = _cause_names(raw)
        row = {"order_id": record["case_id"],
               "confidence": _max_confidence(raw, block.get("confidences"))}
        for column in CAUSE_COLUMNS:
            row[column] = int(column.replace("cause_", "") in causes)
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    goldset = CONFIG.paths.derived / "goldset"
    parser = argparse.ArgumentParser(description="T10.2/T10.3 — quy ket tren gold set")
    parser.add_argument("--gold", type=Path, default=goldset / "gold_labels.csv")
    parser.add_argument("--run", type=Path, default=CONFIG.paths.runs / "goldset")
    parser.add_argument("--out", type=Path, default=CONFIG.paths.derived / "evaluation")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    # Nguon goc phai doc tu meta DI KEM dung tep gold duoc truyen vao.
    #
    # Ban dau dong nay tro toi mot duong dan DAT CUNG, nen `--gold <tep khac>` van
    # lay nguon goc cua gold set mac dinh. Do la loi nguy hiem nhat co the xay ra
    # trong co che nay: no gan sai co `citable` — theo ca hai chieu — ma khong co
    # dau hieu nao tren man hinh. Lan chay dien tap dau tien chinh la thu bat duoc no.
    #
    # Thieu meta thi DUNG HAN, khong mac dinh "tam thoi" mot cach im lang: khong biet
    # nhan tu dau ra thi moi con so phia sau deu khong dien giai duoc.
    from masdss.cli.build_goldset import meta_path

    meta = meta_path(args.gold)
    if not meta.exists():
        raise SystemExit(
            f"Thieu tep meta cho {args.gold.name}: can {meta.name}\n"
            "Chay truoc: python -m masdss.cli.build_goldset --source <phieu> "
            "--provenance <human_independent|model_assisted_provisional> --out <tep>"
        )
    provenance = Provenance(json.loads(meta.read_text(encoding="utf-8"))["provenance"])
    gold = load_gold_labels(args.gold, provenance=provenance)

    print("=" * 78)
    print("T10.2 — QUY KET NGUYEN NHAN TREN GOLD SET  (chi so chinh cua RQ3)")
    print("=" * 78)
    print(provenance.banner)
    print()

    from masdss.cli.run_system import run
    from masdss.data.export import load_stage
    from masdss.evaluation import attribution, selective
    from masdss.system.app import Capabilities

    CONFIG.seed_everything()
    pd.set_option("display.width", 220)

    order_ids = set(gold.frame["order_id"])
    # Quy ket chay tren tong the T4 (day du); mo hinh du bao van hoc tren tong the
    # T3. Gold set sinh tu `t4_test` nen moi don duoc cham diem deu nam trong tap
    # test — khong con tinh huong "don roi vao ky train" nhu ban truoc.
    orders = load_stage("t4", "test")
    t4_train, t4_val = load_stage("t4", "train"), load_stage("t4", "val")
    t3_train, t3_val = load_stage("t3", "train"), load_stage("t3", "val")

    # Cause head da huan luyen (T3.4), CO LOAI cac don cua gold set khoi tap train.
    capabilities = Capabilities.fit(t4_train, t4_val,
                                    risk_train=t3_train, risk_val=t3_val,
                                    cause_head="tfidf", exclude_order_ids=order_ids)
    print(f"Cause head : {capabilities.cause_head.name} "
          f"(is_placeholder={capabilities.cause_head.is_placeholder})")
    print(f"Gold set   : {len(order_ids)} don · nguong tau_cause = {CONFIG.tau_cause}")

    asyncio.run(run(args.run, stage=2, orders=orders, capabilities=capabilities,
                    order_ids=order_ids))

    mas = _predictions_from_decisions(args.run / "decisions.jsonl")
    mono = _predictions_from_baseline(args.run / "baselines.jsonl", "monolithic")
    predictions = {"MAS-DSS": mas, "Monolithic-Complete": mono}

    result = attribution.evaluate(gold, predictions)
    per_cause, per_slice = result.stamped()
    per_cause.to_csv(args.out / "attribution_per_cause.csv", index=False, encoding="utf-8-sig")
    per_slice.to_csv(args.out / "attribution_per_slice.csv", index=False, encoding="utf-8-sig")

    print("\n[theo tung nguyen nhan]")
    print(per_cause.drop(columns=["provenance"]).to_string(index=False))
    print("\n[theo cat lop — hai tinh huong kho cua RQ3]")
    print(per_slice.drop(columns=["provenance"]).to_string(index=False))

    # Bang DUY NHAT mang tinh kiem dinh trong toan bo `evaluation/`. Moi bang khac
    # la MO TA — phan biet nay quyet dinh viec co phai hieu chinh da kiem dinh hay
    # khong, va phai duoc giu nguyen khi viet Chuong 5.
    compare = attribution.compare_systems(gold, predictions, seed=CONFIG.seed)
    compare.to_csv(args.out / "attribution_compare.csv", index=False, encoding="utf-8-sig")
    print("\n[doi dau tung cap — McNemar + KTC bootstrap cho chenh lech macro-F1]")
    print(compare.drop(columns=["provenance", "ghi_chu"]).to_string(index=False))
    for note in compare["ghi_chu"].unique():
        print(f"  ghi chu: {note}")

    print("\n" + "=" * 78)
    print("T10.3 — SELECTIVE PREDICTION  (dieu kien de DP3 khong tu tru diem)")
    print("=" * 78)
    curve, summary = selective.report(gold, predictions)
    curve.to_csv(args.out / "selective_curve.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(args.out / "selective_summary.csv", index=False, encoding="utf-8-sig")
    print(summary.to_string(index=False))

    print("\n" + "=" * 78)
    if not result.citable:
        print(provenance.banner)
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
