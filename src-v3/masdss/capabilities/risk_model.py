"""WP3 / T3.1 — Mo hinh rui ro: LightGBM + hieu chuan isotonic.

Phuc vu: RQ2 (giai doan 1 @ T3), H1 (dieu kien kiem soat).

BA QUYET DINH PHUONG PHAP, moi cai deu se bi hoi khi bao ve:

  1. HIEU CHUAN TREN TAP VAL, khong phai train, cang khong phai test. Hieu chuan
     tren train cho ket qua lac quan gia vi mo hinh da nhin thay chinh du lieu do;
     hieu chuan tren test la ro ri truc tiep.

  2. PR-AUC LA CHI SO CHINH, ROC-AUC chi la phu. Lop duong chiem ~14,7% nen ROC-AUC
     de cho ve dep khong tuong xung voi gia tri thuc te.

  3. BAO CAO ECE TRUOC VA SAU hieu chuan. Day khong phai chi tiet phu: toan bo co
     che Contract Net dua tren viec so sanh do tin cay giua cac analyst, nen mot mo
     hinh "tu tin qua muc" se lam sai lech moi phien dau thau (§A.3).

Mo hinh nay DUNG CHUNG giua MAS-DSS, Single-ML va Monolithic-Complete. Do la ly do
H1 duoc khai bao truoc la KY VONG VO HIEU — ba he dung chung mot nang luc du bao
thi khong the khac nhau ve accuracy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from masdss.config import CONFIG
from masdss.core.ontology import OrderCase, RiskLevel
from masdss.data.featureset import FeatureSet

# Thang du phong cho mo hinh CHUA huan luyen. Mo hinh da huan luyen dung thang
# DUOC SUY RA TU TAP VAL — xem `RiskModel._derive_thresholds`.
#
# VI SAO BAN CU (0,40 / 0,70) LA SAI, va no sai IM LANG:
#
#     Hai con so do duoc dat nhu the diem la mot xac suat tho chua hieu chuan. Sau
#     isotonic, diem bam quanh ty le nen (12,7-17,9%), nen vuot 0,40 doi nam o duoi
#     cung cua duoi phan phoi. Do duoc tren tap val:
#
#         LOW     97,52% so case  — ty le bat man thuc te 13,90%
#         MEDIUM   2,27%          — 47,09%
#         HIGH     0,21%          — 94,74%
#
#     Tuc bang LOW gan nhu KHONG PHAN BIET voi tong the (nen 14,82%): thang rui ro
#     chay nhung khong noi len dieu gi. Hau qua lan sang Contract Net — moi case deu
#     nhan ngan sach muc LOW nen phien dau thau luon o che do "phai chon".
QUANTILE_HIGH = 0.95              # ranh gioi HIGH: 5% case cao diem nhat cua tap val
COST_FALSE_NEGATIVE = 5.0         # bo sot mot don sap bat man
COST_FALSE_POSITIVE = 1.0         # can thiep thua mot don
FALLBACK_THRESHOLDS = (0.40, 0.70)

# Giu ten cu de ma nguon ngoai khong vo. No la BAN DU PHONG, khong phai thang dang dung.
#
# `RISK_THRESHOLDS` DA BI GO. Ten cu tro toi ban DU PHONG, nen bat ky ma nguon nao
# nhap no deu am tham dung mot thang KHONG PHAI thang da hoc tu tap kiem dinh — mot
# lop bay giu lai chi de "khong lam vo ma nguon ngoai", trong khi khong con ma nguon
# ngoai nao dung no. Can thang dang dung thi doc `model.risk_thresholds`.


def cost_optimal_threshold(y_true: np.ndarray, y_score: np.ndarray, *,
                           cost_false_negative: float = COST_FALSE_NEGATIVE,
                           cost_false_positive: float = COST_FALSE_POSITIVE
                           ) -> tuple[float, float]:
    """Chon nguong quyet dinh theo CHI PHI, khong mac dinh 0,5.

    Nguong 0,5 chi toi uu khi hai loai sai co chi phi bang nhau va lop can bang. O
    day khong dieu nao dung: lop duong chiem ~12,7%, va bo sot mot don sap bat man
    dat hon nhieu so voi mot lan can thiep thua.

    Ham nay nam o `capabilities/` chu khong `evaluation/` vi `RiskModel` can no de
    suy ra thang rui ro, ma `capabilities/` khong duoc import `evaluation/`
    (test_layering.py). `evaluation/forecasting.py` import lai tu day — mot cai dat,
    hai noi dung.

    Tra ve (nguong, chi phi ky vong nho nhat).
    """
    y_true = np.asarray(y_true, dtype=int)
    y_score = np.asarray(y_score, dtype=float)
    candidates = np.unique(np.round(y_score, 3))
    best = (0.5, float("inf"))
    for threshold in candidates:
        predicted = y_score >= threshold
        false_negative = int(((~predicted) & (y_true == 1)).sum())
        false_positive = int((predicted & (y_true == 0)).sum())
        cost = cost_false_negative * false_negative + cost_false_positive * false_positive
        if cost < best[1]:
            best = (float(threshold), float(cost))
    return best


@dataclass
class CalibrationReport:
    """Bao cao hieu chuan tren MOT tap cu the.

    Truong `in_sample` la load-bearing: khi bao cao duoc tinh tren chinh tap da
    dung de khop bo hieu chuan (tap val), ECE sau hieu chuan gan nhu chac chan
    bang 0 va con so do VO NGHIA. Chi so dang tin la con so do tren tap TEST.
    Danh dau tuong minh de khong ai — ke ca tac gia sau ba thang — trich nham.
    """

    split: str
    in_sample: bool
    pr_auc: float
    roc_auc: float
    brier_before: float
    brier_after: float
    ece_before: float
    ece_after: float
    n: int
    # Brier cua mo hinh HANG SO: tra ve ty le nen cho moi don, khong nhin dac trung.
    # Day la moc doi chieu re nhat va hay bi bo qua nhat — xem `brier_skill_*`.
    brier_constant: float = float("nan")

    @property
    def brier_skill_before(self) -> float:
        return 1.0 - self.brier_before / self.brier_constant

    @property
    def brier_skill_after(self) -> float:
        return 1.0 - self.brier_after / self.brier_constant

    def to_frame(self) -> pd.DataFrame:
        note = " [IN-SAMPLE — khong dung de bao cao]" if self.in_sample else ""
        return pd.DataFrame([
            {"split": self.split, "metric": "PR-AUC (chinh)", "value": round(self.pr_auc, 4)},
            {"split": self.split, "metric": "ROC-AUC (phu)", "value": round(self.roc_auc, 4)},
            {"split": self.split, "metric": "Brier truoc hieu chuan",
             "value": round(self.brier_before, 4)},
            {"split": self.split, "metric": "Brier sau hieu chuan" + note,
             "value": round(self.brier_after, 4)},
            {"split": self.split, "metric": "Brier HANG SO (ty le nen)",
             "value": round(self.brier_constant, 4)},
            {"split": self.split, "metric": "Brier skill truoc hieu chuan",
             "value": round(self.brier_skill_before, 4)},
            {"split": self.split, "metric": "Brier skill sau hieu chuan" + note,
             "value": round(self.brier_skill_after, 4)},
            {"split": self.split, "metric": "ECE truoc hieu chuan",
             "value": round(self.ece_before, 4)},
            {"split": self.split, "metric": "ECE sau hieu chuan" + note,
             "value": round(self.ece_after, 4)},
        ])

    def canh_bao(self) -> str | None:
        """Loi canh bao khi mo hinh THUA hang so nen. Tra ve None neu khong co.

        Day khong phai kha nang ly thuyet. O moc `ngay mua + 7`, diem THO cua mo
        hinh co Brier 0,1139 so voi 0,1111 cua hang so — tuc **skill am (-0,0245)**,
        mo hinh thua. Chi sau isotonic no moi duong (+0,0314).

        Neu chi bao cao Brier tho ma khong dat canh hang so, con so 0,1139 trong
        rat binh thuong. Doi chieu nay la thu duy nhat lam lo ra van de.
        """
        if self.brier_skill_after < 0:
            return (f"Brier skill SAU hieu chuan am ({self.brier_skill_after:+.4f}): mo hinh "
                    f"du bao xac suat THUA mot hang so bang ty le nen. Khong duoc trinh bay "
                    f"xac suat nay nhu mot uoc luong dang tin.")
        if self.brier_skill_before < 0:
            return (f"Brier skill TRUOC hieu chuan am ({self.brier_skill_before:+.4f}): diem "
                    f"tho thua hang so nen. Hieu chuan isotonic la BAT BUOC, khong phai "
                    f"tuy chon — khong duoc bo qua khi tai su dung mo hinh.")
        return None


def expected_calibration_error(y_true: np.ndarray, y_prob: np.ndarray, bins: int = 10) -> float:
    """ECE — sai lech giua xac suat du bao va ty le thuc te, trung binh co trong so.

    CHUYEN TIEP SANG MOT CAI DAT DUY NHAT (`capabilities/calibration.py`).

        Truoc day module nay co ban cai dat rieng, va no khac ban kia DUNG MOT CHO:
        bien duoi cua bin dau tien. Ban cu dung `(p > low) & (p <= high)` cho moi
        bin, nen mot diem bang DUNG 0,0 roi ra ngoai MOI bin va bi bo qua im lang.

        Hai ham cung ten, cung muc dich, khac hanh vi o bien la dung loai bat nhat
        khong bao gio lam chuong trinh do — no chi lam hai con so trong luan van
        khong so sanh duoc voi nhau. Nay ca hai di qua mot cai dat.
    """
    from masdss.capabilities.calibration import expected_calibration_error as _ece

    return _ece(y_true, y_prob, n_bins=bins)


@dataclass
class RiskModel:
    """LightGBM + isotonic. Deterministic: seed co dinh, single thread."""

    feature_set: FeatureSet
    name: str = "risk_model"
    cost_ms: float = 0.8

    _booster: object | None = None
    _calibrator: object | None = None
    _columns: tuple[str, ...] = ()
    _categories: dict[str, list[str]] = field(default_factory=dict)
    _risk_thresholds: tuple[float, float] | None = None
    report: CalibrationReport | None = None

    # --- huan luyen ---

    def _design_matrix(self, df: pd.DataFrame, *, fit: bool = False) -> pd.DataFrame:
        frame = self.feature_set.select(df)
        for spec in self.feature_set.specs:
            if spec.kind != "categorical" or spec.name not in frame.columns:
                continue
            if fit:
                self._categories[spec.name] = sorted(frame[spec.name].dropna().unique())
            frame[spec.name] = pd.Categorical(
                frame[spec.name], categories=self._categories.get(spec.name, [])
            )
        if fit:
            self._columns = tuple(frame.columns)
        return frame[list(self._columns)]

    def design_matrix(self, df: pd.DataFrame, *, key: str = "order_id") -> pd.DataFrame:
        """DUNG thu mo hinh nhin thay, xuat ra duoc de nguoi khac kiem tra.

        VI SAO PHUONG THUC NAY TON TAI — mot lo hong trong cach chung minh chong ro ri.

            Ba co che duoc neu ra de bao dam dac trung cua moc muon khong lot vao mo
            hinh T3: `available_at` trong so dang ky, tach tep vat ly, va viec ghim
            `self._columns` luc `fit`. Ca ba deu dung, nhung ca ba deu la LAP LUAN VE
            CO CHE — khong co artifact nao de MO RA XEM.

            Te hon, hai trong ba co che im lang khi bi vi pham: `LeakageError` tren
            thuc te khong kich hoat duoc qua duong di binh thuong (constructor cua
            `FeatureSpec` da chan ten cam tu truoc), va `select()` LOAI BO KHONG BAO
            khi gap cot la — no loc giao chu khong nem loi.

        Ham nay bien cau "khong cot T4 nao lot vao" tu mot lap luan thanh mot phep
        kiem MO MOT TEP RA DEM COT. Cot tra ve la DUNG `self._columns` theo DUNG thu
        tu da ghim, bien hang muc da ma hoa theo bang muc da ghim — tuc dung ma tran
        da di vao `LGBMClassifier.fit()`.

        `key` duoc dat lam CHI MUC chu khong phai mot cot: no khong bao gio duoc dua
        vao mo hinh, va de no thanh cot se lam chinh phep kiem tren tro nen mo ho.
        """
        if not self._columns:
            raise RuntimeError("RiskModel chua duoc huan luyen — chua co thu tu cot")
        matrix = self._design_matrix(df)
        if key in df.columns:
            matrix = matrix.set_index(pd.Index(df[key].to_numpy(), name=key))
        return matrix

    def fit(self, train: pd.DataFrame, val: pd.DataFrame, target: str = "is_dissatisfied"):
        import lightgbm as lgb
        from sklearn.isotonic import IsotonicRegression

        x_train = self._design_matrix(train, fit=True)
        y_train = train[target].astype(int).to_numpy()

        self._booster = lgb.LGBMClassifier(
            n_estimators=300, learning_rate=0.05, num_leaves=31,
            random_state=CONFIG.seed, n_jobs=1, verbose=-1,
            deterministic=True, force_row_wise=True,
        ).fit(x_train, y_train)

        # Hieu chuan tren VAL — khong phai train, cang khong phai test.
        raw_val = self._booster.predict_proba(self._design_matrix(val))[:, 1]
        y_val = val[target].astype(int).to_numpy()
        self._calibrator = IsotonicRegression(out_of_bounds="clip").fit(raw_val, y_val)

        # Thang rui ro SUY RA TU VAL, khong phai hai hang so dat bang cam tinh.
        self._risk_thresholds = self._derive_thresholds(
            np.asarray(self._calibrator.predict(raw_val), dtype=float), y_val)

        # Bao cao in-sample, giu lai de doi chieu nhung KHONG dung de bao cao.
        self.report = self.evaluate(val, split="val", target=target)
        return self

    @staticmethod
    def _derive_thresholds(scores: np.ndarray, y: np.ndarray) -> tuple[float, float]:
        """Suy thang rui ro tu phan phoi diem tren tap VAL.

        MOI RANH GIOI CO MOT NGHIA VAN HANH, va do la dieu kien de thang nay bien
        luan duoc truoc hoi dong:

            LOW / MEDIUM = nguong toi uu theo CHI PHI. Duoi muc nay, chi phi ky vong
                           cua viec can thiep vuot loi ich — khong dang mo phien dau
                           thau day du.
            MEDIUM / HIGH = phan vi 95 cua diem tren val. Nhom 5% cao diem nhat la
                           nhom dang duoc cap ngan sach tinh toan 1,5x.

        TINH TREN VAL, KHONG TREN TEST. Dat nguong tren tap test roi cham diem cung
        tren do la ro ri — no chon tham so sau khi da nhin thay ket qua.

        Bat bien duoc kiem ngay tai day: hai ranh gioi phai tach nhau va nam trong
        (0,1). Neu phan phoi diem suy bien den muc khong tach duoc, tra ve ban du
        phong thay vi mot thang vo nghia.
        """
        low, _ = cost_optimal_threshold(y, scores)
        high = float(np.quantile(scores, QUANTILE_HIGH))
        if not 0.0 < low < high < 1.0:
            return FALLBACK_THRESHOLDS
        return round(low, 4), round(high, 4)

    def evaluate(self, df: pd.DataFrame, *, split: str,
                 target: str = "is_dissatisfied") -> CalibrationReport:
        """Do hieu chuan tren mot tap bat ky.

        Goi voi `split="test"` de co con so dang tin: bo hieu chuan chua nhin thay
        tap do bao gio.
        """
        from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

        raw = self._booster.predict_proba(self._design_matrix(df))[:, 1]
        calibrated = np.asarray(self._calibrator.predict(raw), dtype=float)
        y = df[target].astype(int).to_numpy()

        nen = float(y.mean())
        return CalibrationReport(
            split=split,
            in_sample=(split == "val"),
            brier_constant=float(np.mean((nen - y) ** 2)),
            pr_auc=float(average_precision_score(y, calibrated)),
            roc_auc=float(roc_auc_score(y, calibrated)),
            brier_before=float(brier_score_loss(y, raw)),
            brier_after=float(brier_score_loss(y, calibrated)),
            ece_before=expected_calibration_error(y, raw),
            ece_after=expected_calibration_error(y, calibrated),
            n=len(y),
        )

    # --- suy dien ---

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        if self._booster is None or self._calibrator is None:
            raise RuntimeError("RiskModel chua duoc huan luyen")
        raw = self._booster.predict_proba(self._design_matrix(df))[:, 1]
        return np.asarray(self._calibrator.predict(raw), dtype=float)

    @property
    def risk_thresholds(self) -> tuple[float, float]:
        """Thang dang dung. Mo hinh chua huan luyen thi tra ban du phong."""
        return self._risk_thresholds or FALLBACK_THRESHOLDS

    def to_risk_level(self, probability: float) -> RiskLevel:
        """Anh xa diem da hieu chuan sang muc rui ro.

        Day la PHUONG THUC CUA THE HIEN chu khong con la `staticmethod`: thang rui ro
        la mot tham so DUOC HOC tu tap val, nen no thuoc ve mo hinh chu khong thuoc
        ve module. Moi loi goi hien co deu qua the hien (`self.risk_model.to_risk_level`)
        nen khong cho nao phai sua — va ba kien truc van dung CHUNG mot thang, dieu
        kien de phep so sanh cua H1 con nghia.
        """
        low, high = self.risk_thresholds
        if probability >= high:
            return RiskLevel.HIGH
        if probability >= low:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    # --- giao dien Capability ---

    def can_handle(self, case: OrderCase) -> bool:
        return self._booster is not None

    def run(self, case: OrderCase) -> float:
        frame = pd.DataFrame([case.features])
        for column in self._columns:
            if column not in frame.columns:
                frame[column] = np.nan
        return float(self.predict_proba(frame)[0])

    # --- luu tru ---

    def save(self, directory: Path) -> None:
        import joblib

        directory.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {"booster": self._booster, "calibrator": self._calibrator,
             "columns": self._columns, "categories": self._categories,
             "risk_thresholds": self._risk_thresholds,
             "decision_point": self.feature_set.decision_point},
            directory / "risk_model.joblib",
        )

    @staticmethod
    def load(directory: Path) -> "RiskModel":
        import joblib

        blob = joblib.load(Path(directory) / "risk_model.joblib")
        model = RiskModel(feature_set=FeatureSet(blob["decision_point"]))
        model._booster = blob["booster"]
        model._calibrator = blob["calibrator"]
        model._columns = blob["columns"]
        model._categories = blob["categories"]
        # Mo hinh luu truoc 13/08 khong co truong nay — nap lai se dung ban du phong,
        # va do la hanh vi dung: thang phai duoc suy ra tu val, khong duoc doan.
        model._risk_thresholds = blob.get("risk_thresholds")
        return model
