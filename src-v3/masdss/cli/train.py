"""WP3 — Huan luyen capability that va bao cao hieu chuan.

Chay:
    python -m masdss.cli.train

Sinh ra trong models/v3/ va data/v3/:
    risk_model.joblib        -> mo hinh rui ro da hieu chuan
    calibration_report.csv   -> PR-AUC, ROC-AUC, ECE/Brier truoc va sau
    price_coverage.csv       -> ty le nhom hang du dieu kien (ty le REFUSE cua Price)
    ood_report.csv           -> doi chieu ty le phat hien binh thuong vs nhieu loan
    splits_report.csv        -> ranh gioi thoi gian cua ba tap

Moi buoc deu chay tren FeatureSet(T3): giai doan 1 khong duoc thay bang chung
van ban (rang buoc C4).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from masdss.capabilities.ood import OODDetector
from masdss.capabilities.price_signal import PriceSignal
from masdss.capabilities.risk_model import RiskModel
from masdss.config import CONFIG
from masdss.core.ontology import DecisionPoint
from masdss.data.export import load_stage
from masdss.data.featureset import FeatureSet
from masdss.data.splits import TIME_COLUMN


def _xuat_anh_chup(model: RiskModel, train: pd.DataFrame, val: pd.DataFrame) -> None:
    """Xuat DUNG ma tran ma mo hinh da nhin thay, kem sha256 vao manifest.

    VI SAO CAN. Ba co che duoc neu ra de bao dam dac trung cua moc muon khong lot vao
    mo hinh T3 — `available_at`, tach tep vat ly, ghim `_columns` luc `fit` — deu la
    LAP LUAN VE CO CHE. Khong artifact nao mo ra xem duoc. Va hai trong ba co che im
    lang khi bi vi pham: `LeakageError` khong kich hoat duoc qua duong di binh thuong,
    con `select()` loai bo cot la ma khong bao.

    Hai tep duoi day bien cau "khong cot T4 nao lot vao" thanh mot phep kiem MO TEP RA
    DEM COT — dang bang chung nguoi doc kiem duoc trong ba muoi giay.
    """
    import hashlib
    import json

    thu_muc = CONFIG.paths.derived / "features"
    thu_muc.mkdir(parents=True, exist_ok=True)

    ghi_chu = {}
    for ten, phan in (("train", train), ("val", val)):
        duong_dan = thu_muc / f"t3_design_{ten}.parquet"
        ma_tran = model.design_matrix(phan)
        ma_tran.to_parquet(duong_dan)
        ghi_chu[duong_dan.name] = {
            "so_dong": int(len(ma_tran)),
            "so_cot": int(ma_tran.shape[1]),
            "sha256": hashlib.sha256(duong_dan.read_bytes()).hexdigest(),
        }

    manifest_path = thu_muc / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["anh_chup_ma_tran_thiet_ke"] = {
            "mo_ta": ("DUNG ma tran da di vao LGBMClassifier.fit() va vao buoc hieu "
                      "chuan isotonic. Chi muc la order_id (KHONG dua vao mo hinh); "
                      "cot la RiskModel._columns theo dung thu tu da ghim."),
            "cot": list(model.design_matrix(train.head(1)).columns),
            "tep": ghi_chu,
        }
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                                 encoding="utf-8")

    print("\n=== Anh chup ma tran thiet ke ===")
    for ten, meta in ghi_chu.items():
        print(f"  {ten:26s} {meta['so_dong']:6d} dong x {meta['so_cot']:2d} cot  "
              f"sha256 {meta['sha256'][:16]}...")


def perturb(df: pd.DataFrame, columns: tuple[str, ...], scale: float,
            seed: int) -> pd.DataFrame:
    """Nhieu loan co kiem soat de kiem tra do nhay cua bo phat hien OOD."""
    rng = np.random.default_rng(seed)
    out = df.copy()
    for column in columns:
        if column not in out.columns:
            continue
        values = out[column].astype(float)
        spread = values.std(ddof=0) or 1.0
        out[column] = values + rng.normal(scale * spread, spread * 0.1, size=len(values))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Huan luyen capability v3")
    parser.add_argument("--decision-point", default="T3", choices=["T2", "T3", "T4"])
    args = parser.parse_args()

    CONFIG.seed_everything()
    CONFIG.paths.ensure()

    # NAP QUA `load_stage`, KHONG qua `build_order_table()` + `time_split()`.
    #
    # Duong cu bo qua hai co che cua T1.7 va ca hai deu lam so lieu dep hon thuc te:
    #   - khoang cach ly: 2.245 dong val co danh gia den SAU `test_start`, va isotonic
    #     duoc khop tren chinh tap val do -> bo hieu chuan nhin thay nhan ky test
    #     (con so tren tong the DAY DU la 2.351; xem `manifest.khoang_cach_ly`)
    #   - phep loc `reachable_at_t3`: 23.193 don (23,5%) khong con kip can thiep bi keo
    #     vao, ty le bat man 7,84% so voi 17,45% -> ty le nen bi lam loang he thong
    # Xem `tests-v3/test_data_entrypoint.py`.
    train = load_stage("t3", "train", times=True)
    val = load_stage("t3", "val", times=True)
    test = load_stage("t3", "test", times=True)
    feature_set = FeatureSet(DecisionPoint(args.decision_point))

    print(f"Feature set @ {args.decision_point}: {list(feature_set.names)}")
    print(f"Kich thuoc tap: train={len(train)} val={len(val)} test={len(test)}")

    report_rows = [
        {"split": name, "n": len(part),
         "tu": str(part[TIME_COLUMN].min()), "den": str(part[TIME_COLUMN].max()),
         "ty_le_nen": round(float(part["is_dissatisfied"].mean()), 4)}
        for name, part in (("train", train), ("val", val), ("test", test))
    ]
    pd.DataFrame(report_rows).to_csv(CONFIG.paths.derived / "splits_report.csv",
                                     index=False, encoding="utf-8-sig")

    # --- T3.1 mo hinh rui ro ---
    model = RiskModel(feature_set=feature_set).fit(train, val)
    model.save(CONFIG.paths.models)
    _xuat_anh_chup(model, train, val)

    val_report = model.evaluate(val, split="val")
    test_report = model.evaluate(test, split="test")
    combined = pd.concat([val_report.to_frame(), test_report.to_frame()], ignore_index=True)

    print("\n=== Hieu chuan ===")
    print(combined.to_string(index=False))
    print("\nCon so dung de bao cao la dong 'test'. Dong 'val' la in-sample: bo hieu")
    print("chuan duoc khop tren chinh tap do, nen ECE sau hieu chuan gan nhu bang 0")
    print("theo cau tao chu khong phai theo chat luong mo hinh.")
    combined.to_csv(CONFIG.paths.derived / "calibration_report.csv",
                    index=False, encoding="utf-8-sig")

    # --- T3.5 tin hieu gia ---
    price = PriceSignal().fit(train)
    coverage = price.coverage()
    coverage.to_csv(CONFIG.paths.derived / "price_coverage.csv",
                    index=False, encoding="utf-8-sig")
    eligible = int(coverage["eligible"].sum())
    print(f"\nPrice Analyst: {eligible}/{len(coverage)} nhom hang du dieu kien "
          f"-> REFUSE tren {100 * (1 - eligible / len(coverage)):.1f}% nhom hang")

    # --- T3.2 phat hien OOD ---
    numeric = feature_set.numeric_names
    detector = OODDetector().fit(train, numeric)
    rows = [
        {"tap": "train", "muc_nhieu_loan": 0.0,
         "ty_le_phat_hien": round(detector.detection_rate(train), 4)},
        {"tap": "test", "muc_nhieu_loan": 0.0,
         "ty_le_phat_hien": round(detector.detection_rate(test), 4)},
    ]
    for scale in (1.0, 2.0, 4.0):
        shifted = perturb(test, numeric, scale, CONFIG.seed)
        rows.append({"tap": "test + nhieu loan", "muc_nhieu_loan": scale,
                     "ty_le_phat_hien": round(detector.detection_rate(shifted), 4)})
    ood_report = pd.DataFrame(rows)
    ood_report.to_csv(CONFIG.paths.derived / "ood_report.csv",
                      index=False, encoding="utf-8-sig")
    print("\n=== Bo phat hien OOD ===")
    print(ood_report.to_string(index=False))

    print(f"\nMo hinh -> {CONFIG.paths.models}")


if __name__ == "__main__":
    main()
