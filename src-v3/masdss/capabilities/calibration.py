"""WP7 / T7.3b — Hieu chuan do tin cay cua tung analyst.

Phuc vu: RQ3 §2.2 yeu cau dich danh *"ECE va Brier score cua tung analyst truoc va
sau hieu chuan"*. Day la chi so BAT BUOC cua RQ3, doc lap voi ket cuc cua H2.

VI SAO PHAI HIEU CHUAN RIENG TUNG ANALYST.

    Ba analyst chay tren ba bo phan loai khac nhau, tren cac lop co ty le duong
    rat khac nhau (delivery 58%, service 18,8%). Mot diem 0,6 cua DeliveryAnalyst va
    mot diem 0,6 cua ServiceAnalyst KHONG cung nghia. Khi ca hai cung dau thau, phien
    dau thau dang so hai dai luong khong cung don vi — va `bid_entropy`, chi so
    rieng cua DP2, tinh tren cac con so khong cung don vi thi khong doc duoc.

MOT CANH BAO PHAI DOC TRUOC KHI DIEN GIAI BAT KY CON SO NAO O DAY.

    Hieu chuan la thuoc tinh cua NANG LUC NEN, khong phai cua kien truc. Doi chung
    don khoi dung chung cause head, nen no cung duoc hieu chuan y het. Neu chi hieu
    chuan cho MAS-DSS roi bao cao chenh lech nhu uu the kien truc thi do la baseline
    bi lam yeu — dung loi ma nghien cuu da cam ket tranh (RQ3 §2.2).

    Vi vay `apply_to` nhan CA HAI kien truc, va bang ECE bao cao ca hai.

KY LUAT DO LUONG — loi L04 da xay ra mot lan va khong duoc lap lai.

    Hieu chuan tren gold set roi do ECE tren chinh gold set cho ECE = 0 mot cach
    gia tao. `fit_out_of_fold` dung K-fold: moi quan sat duoc hieu chuan boi mot mo
    hinh KHONG nhin thay no. Con so bao cao lay tu do.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from masdss.core.ontology import Cause

DEFAULT_FOLDS = 5
# Duoi muc nay, isotonic chi hoc thuoc nhieu. Nhan do bi tu choi hieu chuan va giu
# nguyen diem tho — tu choi co ly do, khong im lang tra ve mot duong cong vo nghia.
MIN_POSITIVES_FOR_CALIBRATION = 15


@dataclass(frozen=True)
class CalibrationReport:
    """ECE/Brier truoc va sau. `in_sample` ton tai vi loi L04."""

    cause: str
    n: int
    n_positive: int
    ece_before: float
    ece_after: float
    brier_before: float
    brier_after: float
    calibrated: bool
    reason: str = ""
    in_sample: bool = False

    def to_row(self) -> dict:
        return {
            "nguyen_nhan": self.cause, "n": self.n, "n_duong": self.n_positive,
            "ece_truoc": round(self.ece_before, 4), "ece_sau": round(self.ece_after, 4),
            "brier_truoc": round(self.brier_before, 4), "brier_sau": round(self.brier_after, 4),
            "da_hieu_chuan": self.calibrated,
            "trong_mau": self.in_sample,
            "ly_do": self.reason,
        }


def expected_calibration_error(y_true, y_prob, *, n_bins: int = 10) -> float:
    """ECE voi chia bin deu tren [0,1].

    Bin rong deu chu khong theo phan vi: o day ta muon biet "khi he thong noi 0,8
    thi no dung 80% so lan khong", va cau hoi do gan voi GIA TRI chu khong voi thu
    hang.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_prob = np.asarray(y_prob, dtype=float)
    if len(y_true) == 0:
        return 0.0
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    total = 0.0
    for low, high in zip(edges[:-1], edges[1:]):
        mask = (y_prob > low) & (y_prob <= high) if low > 0 else (y_prob >= low) & (y_prob <= high)
        if not mask.any():
            continue
        total += mask.mean() * abs(y_true[mask].mean() - y_prob[mask].mean())
    return float(total)


def _brier(y_true, y_prob) -> float:
    return float(np.mean((np.asarray(y_prob, dtype=float)
                          - np.asarray(y_true, dtype=float)) ** 2))


@dataclass
class BidCalibrator:
    """Hieu chuan isotonic, MOT duong cong cho MOI nguyen nhan."""

    folds: int = DEFAULT_FOLDS
    seed: int = 0
    _models: dict[Cause, object] = field(default_factory=dict)
    _reports: dict[Cause, CalibrationReport] = field(default_factory=dict)

    def fit(self, scores: dict[Cause, np.ndarray],
            truth: dict[Cause, np.ndarray]) -> "BidCalibrator":
        """Khop duong cong tren TOAN BO gold set — dung de VAN HANH.

        Con so bao cao KHONG duoc lay tu day; dung `fit_out_of_fold`.
        """
        from sklearn.isotonic import IsotonicRegression

        for cause, y_score in scores.items():
            y_true = np.asarray(truth[cause], dtype=int)
            if int(y_true.sum()) < MIN_POSITIVES_FOR_CALIBRATION:
                continue
            model = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
            model.fit(np.asarray(y_score, dtype=float), y_true)
            self._models[cause] = model
        return self

    def fit_out_of_fold(self, scores: dict[Cause, np.ndarray],
                        truth: dict[Cause, np.ndarray]) -> list[CalibrationReport]:
        """Hieu chuan cheo K-fold. **Day la nguon duy nhat cua con so bao cao.**

        Moi quan sat duoc hieu chuan boi mot mo hinh khong nhin thay no, nen ECE
        sau hieu chuan la ngoai mau. Khop hoan toan (`fit`) tren cung du lieu se
        cho ECE gan 0 mot cach gia tao — do la loi L04.
        """
        from sklearn.isotonic import IsotonicRegression
        from sklearn.model_selection import StratifiedKFold

        reports: list[CalibrationReport] = []
        for cause, raw in scores.items():
            y_score = np.asarray(raw, dtype=float)
            y_true = np.asarray(truth[cause], dtype=int)
            n_positive = int(y_true.sum())

            ece_before = expected_calibration_error(y_true, y_score)
            brier_before = _brier(y_true, y_score)

            if n_positive < MIN_POSITIVES_FOR_CALIBRATION:
                report = CalibrationReport(
                    cause=cause.value, n=len(y_true), n_positive=n_positive,
                    ece_before=ece_before, ece_after=ece_before,
                    brier_before=brier_before, brier_after=brier_before,
                    calibrated=False,
                    reason=(f"chi {n_positive} duong, duoi nguong "
                            f"{MIN_POSITIVES_FOR_CALIBRATION} — tu choi hieu chuan"),
                )
                reports.append(report)
                self._reports[cause] = report
                continue

            out_of_fold = np.zeros_like(y_score)
            splitter = StratifiedKFold(n_splits=min(self.folds, n_positive),
                                       shuffle=True, random_state=self.seed)
            for train_index, test_index in splitter.split(y_score.reshape(-1, 1), y_true):
                model = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
                model.fit(y_score[train_index], y_true[train_index])
                out_of_fold[test_index] = model.predict(y_score[test_index])

            report = CalibrationReport(
                cause=cause.value, n=len(y_true), n_positive=n_positive,
                ece_before=ece_before,
                ece_after=expected_calibration_error(y_true, out_of_fold),
                brier_before=brier_before, brier_after=_brier(y_true, out_of_fold),
                calibrated=True, in_sample=False,
            )
            reports.append(report)
            self._reports[cause] = report
        return reports

    def transform(self, cause: Cause, probability: float) -> float:
        model = self._models.get(cause)
        if model is None:
            return float(probability)
        return float(model.predict([probability])[0])

    @property
    def calibrated_causes(self) -> tuple[Cause, ...]:
        return tuple(self._models)
