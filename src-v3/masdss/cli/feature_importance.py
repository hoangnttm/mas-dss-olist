"""Phu luc A — Do quan trong dac trung cua mo hinh du bao tai moc T3.

    python -m masdss.cli.feature_importance

HAI PHEP DO, VA LY DO PHAI LA HAI CHU KHONG MOT.

    Hai dac trung cua moc T3 — `observed_delay_days` va `days_to_deadline` — CONG
    TUYEN gan nhu hoan toan: tren nhom chua giao chung dung bang +/- cung mot dai
    luong, va nhom do chiem 96,68% tap huan luyen. Voi mot cap nhu vay, moi phep do
    do quan trong deu hong — nhung chung hong theo HAI KIEU NGUOC NHAU:

        gain / split  — chia CONG LAO mot cach tuy y giua hai dac trung. Cai nao
                        duoc cay chon truoc thi an gan het diem.
        permutation   — DANH GIA THAP CA HAI. Hoan vi mot cai khong lam giam diem,
                        vi cai con lai van mang nguyen thong tin do.

    Dat canh nhau, hai phep bo lo lan nhau: mot dac trung co gain cao ma permutation
    gan 0 la dau hieu gan nhu chac chan cua cong tuyen, chu khong phai dau hieu no vo
    dung. Bao cao mot phep thoi se dan toi ket luan sai theo huong nay hay huong kia.

VI SAO DO TREN TAP KIEM DINH CHU KHONG TAP KIEM THU.

    Tap kiem thu chi dung de CHAM DIEM (ch3 §3.5.1). Dung no cho mot phan tich mo ta
    khong lam sai con so nao, nhung no lam mo ky luat da tuyen bo — va ky luat do chi
    con gia tri khi khong co ngoai le nao.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from masdss.config import CONFIG

DEFAULT_REPEATS = 20


def _permutation(model, frame: pd.DataFrame, target: str, n_repeats: int, seed: int):
    """Do quan trong theo phep hoan vi, tren diem DA HIEU CHUAN.

    Dung chinh `predict_proba` cua `RiskModel` chu khong dung thang booster: do la
    dai luong ma he thong thuc su su dung de ra quyet dinh. Hoan vi tren thang tho se
    tra loi mot cau hoi khac cau hoi dang duoc dat.
    """
    from sklearn.metrics import average_precision_score

    y = frame[target].astype(int).to_numpy()
    goc = float(average_precision_score(y, model.predict_proba(frame)))

    rng = np.random.default_rng(seed)
    ket_qua = {}
    for cot in model.design_matrix(frame.head(1)).columns:
        giam = []
        for _ in range(n_repeats):
            xao = frame.copy()
            xao[cot] = frame[cot].to_numpy()[rng.permutation(len(frame))]
            giam.append(goc - float(average_precision_score(y, model.predict_proba(xao))))
        ket_qua[cot] = (float(np.mean(giam)), float(np.std(giam, ddof=1)))
    return goc, ket_qua


def main() -> None:
    parser = argparse.ArgumentParser(description="Phu luc A — do quan trong dac trung")
    parser.add_argument("--out", type=Path, default=CONFIG.paths.derived / "evaluation")
    parser.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    from masdss.capabilities.risk_model import RiskModel
    from masdss.data.export import load_stage
    from masdss.data.features import spec_of

    CONFIG.seed_everything()
    pd.set_option("display.width", 200)

    model = RiskModel.load(CONFIG.paths.models)
    val = load_stage("t3", "val")

    print("=" * 78)
    print("DO QUAN TRONG DAC TRUNG — mo hinh du bao tai moc T3")
    print("=" * 78)
    print(f"Do tren tap KIEM DINH ({len(val)} don) — tap kiem thu chi de cham diem.")

    booster = model._booster
    ten_cot = list(model._columns)
    gain = dict(zip(ten_cot, booster.booster_.feature_importance(importance_type="gain")))
    split = dict(zip(ten_cot, booster.booster_.feature_importance(importance_type="split")))
    tong_gain = sum(gain.values()) or 1.0

    goc, hoan_vi = _permutation(model, val, "is_dissatisfied", args.repeats, CONFIG.seed)
    print(f"PR-AUC goc tren tap kiem dinh: {goc:.4f}\n")

    rows = []
    for cot in ten_cot:
        tb, do_lech = hoan_vi[cot]
        rows.append({
            "dac_trung": cot,
            "moc": spec_of(cot).available_at.name,
            "kieu": spec_of(cot).kind,
            "gain": round(float(gain[cot]), 2),
            "gain_ty_le": round(float(gain[cot]) / tong_gain, 4),
            "split": int(split[cot]),
            "permutation_tb": round(tb, 6),
            "permutation_do_lech": round(do_lech, 6),
        })
    bang = pd.DataFrame(rows).sort_values("permutation_tb", ascending=False)
    bang.insert(0, "hang", range(1, len(bang) + 1))
    bang.to_csv(args.out / "feature_importance.csv", index=False, encoding="utf-8-sig")

    print(bang.to_string(index=False))
    print()
    print("=" * 78)
    print("DOC BANG NAY THE NAO")
    print("=" * 78)
    print("`observed_delay_days` va `days_to_deadline` CONG TUYEN (tuong quan -0,9998")
    print("tren toan tap; dung bang +/- cung mot dai luong tren 96,68% so dong).")
    print("  - gain CHIA cong lao tuy y giua hai cai")
    print("  - permutation DANH GIA THAP CA HAI: hoan vi mot cai khong giam diem vi")
    print("    cai con lai van mang nguyen thong tin do")
    print("Khong doc rieng le hai dong nay. Xem Phu luc A §A.10.")
    print(f"\n-> {args.out / 'feature_importance.csv'}")


if __name__ == "__main__":
    main()
