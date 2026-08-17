"""WP10 — Phan tich do nhay: mot head HUAN LUYEN mua them duoc gi so voi TU KHOA.

    python -m masdss.cli.compare_heads

Phuc vu Chuong 5 o hai cho:

  1. **Bien minh cho mot quyet dinh thiet ke.** `TfidfCauseHead` tro thanh mac dinh
     tu 11/08. Mot quyet dinh thiet ke khong kem so do la mot so thich, khong phai
     mot ket qua Design Science.

  2. **Do lon cua mot khuyet diem da biet.** `data/labels.py` da ghi tu dau rang bo
     tu khoa "khong duoc kiem dinh, truot bien the chinh ta, xu ly phu dinh so sai".
     Lenh nay bien cau canh bao dinh tinh do thanh mot con so.

BA CHI SO, va chi so thu ba moi la cai quan trong nhat:

    macro-F1        — do chinh xac quy ket
    gia moi loi goi — do bang dong ho, KHONG lay tu `cost_ms` khai bao
    SO GIA TRI do tin cay khac nhau — mot head tra HANG SO thi `bid_entropy` cua DP2
                      vo nghia va hieu chuan (T7.3b) bat kha thi, du macro-F1 co the
                      chap nhan duoc. Day la ly do khong the chon head chi bang F1.

CANH BAO. Con so tuyet doi do tren gold set TAM THOI (L26) nen mang `citable=False`.
Nhung day la so sanh TUONG DOI giua hai head tren CUNG mot tap nhan, nen sai lech
cua nhan tac dong len ca hai nhu nhau — ket luan ve THU TU vung hon nhieu so voi gia
tri tuyet doi cua tung con so.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

import numpy as np
import pandas as pd

from masdss.config import CONFIG
from masdss.core.ontology import Cause, DecisionPoint, OrderCase
from masdss.data.labels import CAUSE_COLUMNS, Provenance, load_gold_labels

CAUSES = (Cause.DELIVERY, Cause.QUALITY, Cause.SERVICE)


def _prf(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[float, float, float]:
    true_positive = int(((y_true == 1) & (y_pred == 1)).sum())
    predicted, actual = int((y_pred == 1).sum()), int((y_true == 1).sum())
    precision = true_positive / predicted if predicted else 0.0
    recall = true_positive / actual if actual else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def latency_ms(head, cases: list[OrderCase], *, cause: Cause = Cause.QUALITY) -> tuple[float, float]:
    """Gia THAT moi loi goi. Do bang dong ho — `cost_ms` khai bao co the sai.

    No da tung sai: `TfidfCauseHead.cost_ms` bi dat 12,0 bang cam tinh trong khi gia
    that la 1,3, va sai lech do du de bai toan phan bo ngan sach loai han analyst
    van ban khoi case rui ro thap (loi L27).
    """
    samples = []
    for case in cases:
        started = time.perf_counter()
        head.score(case, cause)
        samples.append((time.perf_counter() - started) * 1000)
    samples.sort()
    return statistics.median(samples), samples[int(0.95 * len(samples))]


def main() -> None:
    goldset = CONFIG.paths.derived / "goldset"
    parser = argparse.ArgumentParser(description="Doi dau hai cause head")
    parser.add_argument("--gold", type=Path, default=goldset / "gold_labels.csv")
    parser.add_argument("--out", type=Path, default=CONFIG.paths.derived / "evaluation")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    from masdss.capabilities.cause_head import LexiconCauseHead
    from masdss.cli.build_goldset import meta_path
    from masdss.data.export import load_stage
    from masdss.system.app import Capabilities

    CONFIG.seed_everything()
    pd.set_option("display.width", 200)

    meta = meta_path(args.gold)
    provenance = (Provenance(json.loads(meta.read_text(encoding="utf-8"))["provenance"])
                  if meta.exists() else Provenance.MODEL_ASSISTED_PROVISIONAL)
    gold = load_gold_labels(args.gold, provenance=provenance)

    order_ids = set(gold.frame["order_id"])
    # Doi dau hai head la phep do QUY KET, nen no chay tren tong the T4 (day du).
    orders = pd.concat([load_stage("t4", s) for s in ("train", "val", "test")],
                       ignore_index=True)
    # Head huan luyen phai LOAI don cua gold set khoi tap train, neu khong phep do
    # thanh trong mau va bang so nay mat y nghia.
    trained = Capabilities.fit(load_stage("t4", "train"), load_stage("t4", "val"),
                               cause_head="tfidf",
                               exclude_order_ids=order_ids).cause_head

    truth = gold.frame.set_index("order_id").sort_index()
    rows = orders.set_index("order_id").loc[truth.index]
    cases = [
        OrderCase(case_id=str(index), decision_point=DecisionPoint.T4, features={},
                  review_text=(f"{r.review_title or ''} {r.review_content or ''}").strip())
        for index, r in rows.iterrows()
    ]

    detail, summary = [], []
    for name, head in (("Lexicon (tu khoa)", LexiconCauseHead()),
                       ("TF-IDF (huan luyen)", trained)):
        confidences = []
        f1_scores = []
        for cause in CAUSES:
            scores = np.array([head.score(case, cause)[0] for case in cases])
            confidences.append(scores)
            predicted = (scores >= CONFIG.tau_cause).astype(int)
            y_true = truth[f"cause_{cause.value}"].to_numpy()
            precision, recall, f1 = _prf(y_true, predicted)
            f1_scores.append(f1)
            detail.append({
                "head": name, "nguyen_nhan": cause.value,
                "n_duong_that": int(y_true.sum()), "n_du_doan": int(predicted.sum()),
                "precision": round(precision, 4), "recall": round(recall, 4),
                "f1": round(f1, 4),
            })

        p50, p95 = latency_ms(head, cases)
        summary.append({
            "head": name,
            "macro_f1": round(float(np.mean(f1_scores)), 4),
            "so_gia_tri_do_tin_cay": int(len(np.unique(np.round(np.vstack(confidences), 4)))),
            "gia_p50_ms": round(p50, 4),
            "gia_p95_ms": round(p95, 4),
            "cost_ms_khai_bao": head.cost_ms,
            "is_placeholder": head.is_placeholder,
        })

    detail_frame = pd.DataFrame(detail)
    summary_frame = pd.DataFrame(summary)
    for frame in (detail_frame, summary_frame):
        frame["citable"] = provenance.citable

    detail_frame.to_csv(args.out / "head_comparison_detail.csv", index=False,
                        encoding="utf-8-sig")
    summary_frame.to_csv(args.out / "head_comparison.csv", index=False, encoding="utf-8-sig")

    print("=" * 78)
    print("PHAN TICH DO NHAY — head huan luyen so voi danh sach tu khoa")
    print("=" * 78)
    print(provenance.banner)
    print(f"\n{len(cases)} don tang A · nguong tau_cause = {CONFIG.tau_cause}\n")
    print(summary_frame.to_string(index=False))
    print("\n[theo tung nguyen nhan]")
    print(detail_frame.to_string(index=False))
    print("\nCot `so_gia_tri_do_tin_cay` la cot quan trong nhat: mot head tra ve HANG SO")
    print("lam `bid_entropy` cua DP2 vo nghia va hieu chuan T7.3b bat kha thi.")
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
