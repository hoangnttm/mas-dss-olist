"""WP10 / T10.1 — Chi so du bao va DIEU KIEN KIEM SOAT (H1).

Phuc vu: RQ1, gia thuyet H1.

MOT CAI BAY PHAI NOI RO TRUOC KHI DOC BAT KY CON SO NAO O DAY.

    H1 phat bieu: "MAS-DSS khong khac biet co y nghia so voi mo hinh don le ve
    accuracy / PR-AUC". Nghien cuu khai bao truoc rang ky vong H1 VO HIEU, va do la
    dieu mong muon.

    Nhung trong kien truc nay, MAS-DSS va Single-ML dung CHUNG MOT DOI TUONG
    `risk_model` — khong phai cung lop, khong phai cung tham so, ma cung mot doi
    tuong trong bo nho. Vi vay diem du bao cua chung GIONG NHAU TUNG BIT.

    Kiem dinh tuong duong tren hai day so giong het nhau la mot TAUTOLOGY. No khong
    phai bang chung ve dieu gi ca — no chi xac nhan rang ta da noi day dung.

    Vi vay module nay tach bach hai thu:

      `verify_shared_capability()`  — KIEM TRA DAC TA. Khang dinh hai kien truc thuc
                                      su dung chung mot mo hinh. Neu that bai, moi
                                      so sanh khac trong Chuong 5 deu mat hieu luc.

      `evaluate()`                  — KET QUA THAT. PR-AUC/ROC-AUC kem khoang tin cay
                                      bootstrap tren tap test, phan tich do nhay
                                      nguong nhan, va nguong quyet dinh chon theo
                                      CHI PHI chu khong mac dinh 0,5.

    Trinh bay tautology nhu mot phat hien la tu lua. Trinh bay no nhu mot dieu kien
    kiem soat DA DUOC KIEM CHUNG la trung thuc — va do moi la vai tro that cua H1.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from masdss.capabilities.risk_model import cost_optimal_threshold as _cost_optimal_threshold

DEFAULT_BOOTSTRAP = 1000
# Bien tuong duong cho PR-AUC. 0,01 la muc chenh lech ma o quy mo nay khong con y
# nghia nghiep vu — phai khai bao TRUOC khi nhin ket qua.
DEFAULT_EQUIVALENCE_MARGIN = 0.01


@dataclass(frozen=True)
class MetricWithCI:
    name: str
    value: float
    lower: float
    upper: float
    n: int

    def describe(self) -> str:
        return f"{self.name}: {self.value:.4f}  [{self.lower:.4f}, {self.upper:.4f}]"


@dataclass(frozen=True)
class EquivalenceResult:
    """Ket qua kiem dinh tuong duong (TOST)."""

    mean_difference: float
    lower: float
    upper: float
    margin: float
    equivalent: bool
    identical: bool
    note: str

    def describe(self) -> str:
        verdict = "TUONG DUONG" if self.equivalent else "KHONG ket luan duoc tuong duong"
        return (f"{verdict}: chenh lech {self.mean_difference:+.6f} "
                f"[{self.lower:+.6f}, {self.upper:+.6f}] vs bien +/-{self.margin}")


def bootstrap_ci(metric_fn, y_true: np.ndarray, y_score: np.ndarray, *,
                 name: str, n_boot: int = DEFAULT_BOOTSTRAP,
                 seed: int = 0, alpha: float = 0.05) -> MetricWithCI:
    """Khoang tin cay bootstrap cho mot chi so.

    Bao cao mot con so tran ma khong co khoang tin cay la che mat co mau: PR-AUC
    0,40 tren 300 case va tren 14.000 case la hai muc chac chan rat khac nhau.
    """
    rng = np.random.default_rng(seed)
    n = len(y_true)
    values = []
    for _ in range(n_boot):
        index = rng.integers(0, n, n)
        sample_y = y_true[index]
        if sample_y.min() == sample_y.max():   # bootstrap ra mot lop duy nhat
            continue
        values.append(metric_fn(sample_y, y_score[index]))
    if not values:
        point = float(metric_fn(y_true, y_score))
        return MetricWithCI(name, point, point, point, n)
    return MetricWithCI(
        name=name,
        value=float(metric_fn(y_true, y_score)),
        lower=float(np.quantile(values, alpha / 2)),
        upper=float(np.quantile(values, 1 - alpha / 2)),
        n=n,
    )


def verify_shared_capability(scores_mas: np.ndarray,
                             scores_single: np.ndarray) -> EquivalenceResult:
    """KIEM TRA DAC TA, khong phai ket qua nghien cuu.

    Hai kien truc phai dung chung mot mo hinh du bao. Neu khang dinh nay that bai,
    moi so sanh khac trong Chuong 5 deu mat hieu luc — vi khi do khac biet quan sat
    duoc co the den tu nang luc du bao chu khong tu kien truc.
    """
    difference = np.asarray(scores_mas, dtype=float) - np.asarray(scores_single, dtype=float)
    identical = bool(np.allclose(difference, 0.0, atol=1e-12))
    return EquivalenceResult(
        mean_difference=float(difference.mean()) if len(difference) else 0.0,
        lower=float(difference.min()) if len(difference) else 0.0,
        upper=float(difference.max()) if len(difference) else 0.0,
        margin=0.0,
        equivalent=identical,
        identical=identical,
        note=("Dung chung mot doi tuong mo hinh — tuong duong theo CAU TAO. "
              "Day la kiem tra dac ta, KHONG phai bang chung thuc nghiem."
              if identical else
              "CANH BAO: hai kien truc cho diem du bao khac nhau. Chung dang le phai "
              "dung chung mot doi tuong `risk_model`. Moi so sanh khac mat hieu luc "
              "cho toi khi sua."),
    )


def tost_equivalence(values_a: np.ndarray, values_b: np.ndarray, *,
                     margin: float = DEFAULT_EQUIVALENCE_MARGIN,
                     alpha: float = 0.05) -> EquivalenceResult:
    """Kiem dinh tuong duong hai mot phia (TOST) tren cap quan sat.

    KHONG dung t-test. Mot t-test khong bac bo duoc gia thuyet vo hieu chi noi rang
    ta THIEU BANG CHUNG ve khac biet — no khong noi rang hai ben tuong duong. Voi H1,
    dieu ta muon khang dinh la TUONG DUONG, nen phai dung kiem dinh duoc thiet ke cho
    dung menh de do.
    """
    from scipy import stats

    difference = np.asarray(values_a, dtype=float) - np.asarray(values_b, dtype=float)
    n = len(difference)
    if n < 2:
        raise ValueError("can it nhat 2 quan sat de kiem dinh")

    if np.allclose(difference, 0.0, atol=1e-12):
        return EquivalenceResult(
            mean_difference=0.0, lower=0.0, upper=0.0, margin=margin,
            equivalent=True, identical=True,
            note=("Hai day so giong het nhau — TOST tro nen tautology. Bao cao nhu "
                  "kiem tra dac ta, khong phai ket qua thuc nghiem."),
        )

    mean = float(difference.mean())
    stderr = float(difference.std(ddof=1) / np.sqrt(n))
    critical = stats.t.ppf(1 - alpha, df=n - 1)
    lower, upper = mean - critical * stderr, mean + critical * stderr
    return EquivalenceResult(
        mean_difference=mean, lower=lower, upper=upper, margin=margin,
        equivalent=bool(lower > -margin and upper < margin),
        identical=False,
        note="TOST tren cap quan sat, khoang tin cay 90% nam trong bien tuong duong.",
    )


# MOT CAI DAT, HAI NOI DUNG. Ham nay nam o `capabilities/risk_model.py` vi chinh
# `RiskModel` can no de suy ra thang rui ro, ma `capabilities/` khong duoc import
# `evaluation/` (test_layering.py). Nhan lai o day de ma nguon goi cu khong vo.
cost_optimal_threshold = _cost_optimal_threshold


def evaluate(y_true: np.ndarray, y_score: np.ndarray, *,
             seed: int = 0, n_boot: int = DEFAULT_BOOTSTRAP) -> pd.DataFrame:
    """PR-AUC va ROC-AUC kem khoang tin cay bootstrap.

    PR-AUC la chi so CHINH: lop duong chiem ~14,7% nen ROC-AUC de cho ve dep khong
    tuong xung voi gia tri nghiep vu.
    """
    from sklearn.metrics import average_precision_score, roc_auc_score

    y_true = np.asarray(y_true, dtype=int)
    y_score = np.asarray(y_score, dtype=float)
    rows = [
        bootstrap_ci(average_precision_score, y_true, y_score,
                     name="PR-AUC (chinh)", n_boot=n_boot, seed=seed),
        bootstrap_ci(roc_auc_score, y_true, y_score,
                     name="ROC-AUC (phu)", n_boot=n_boot, seed=seed),
    ]
    base_rate = float(y_true.mean())
    return pd.DataFrame([
        *({"metric": m.name, "value": round(m.value, 4),
           "ci_lower": round(m.lower, 4), "ci_upper": round(m.upper, 4), "n": m.n}
          for m in rows),
        {"metric": "ty le duong (nen)", "value": round(base_rate, 4),
         "ci_lower": np.nan, "ci_upper": np.nan, "n": len(y_true)},
        {"metric": "lift PR-AUC / nen", "value": round(rows[0].value / base_rate, 2),
         "ci_lower": np.nan, "ci_upper": np.nan, "n": len(y_true)},
    ])


def threshold_sensitivity(frame: pd.DataFrame, y_score: np.ndarray,
                          rating_column: str = "rating",
                          thresholds: tuple[int, ...] = (2, 3)) -> pd.DataFrame:
    """Do nhay theo NGUONG DINH NGHIA NHAN: `rating <= 2` so voi `<= 3`.

    Ket luan khong duoc phu thuoc vao mot lua chon nguong tuy y. Bao cao ca hai la
    cach chung minh dieu do thay vi khang dinh suong.
    """
    from sklearn.metrics import average_precision_score, roc_auc_score

    rows = []
    for threshold in thresholds:
        y = (frame[rating_column] <= threshold).astype(int).to_numpy()
        rows.append({
            "nguong_nhan": f"rating <= {threshold}",
            "ty_le_duong": round(float(y.mean()), 4),
            "pr_auc": round(float(average_precision_score(y, y_score)), 4),
            "roc_auc": round(float(roc_auc_score(y, y_score)), 4),
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# Chi so cho bai toan MAT CAN BANG. AUC mot minh khong du — no tom tat toan bo
# duong cong thanh mot so, trong khi quyet dinh nghiep vu chi dung MOT diem tren
# duong cong do: "mot doi cham soc xu ly duoc k% so don moi ngay".
# --------------------------------------------------------------------------

DEFAULT_K = (0.005, 0.01, 0.02, 0.05, 0.10, 0.20)


def precision_at_k(y_true: np.ndarray, y_score: np.ndarray,
                   ks: tuple[float, ...] = DEFAULT_K) -> pd.DataFrame:
    """Do CHINH XAC va DO PHU o dung nang luc xu ly that.

    Day la thuoc do khop voi cach he thong duoc dung. Doi cham soc khong xu ly ca
    11.322 don ky test; ho xu ly top k%. Cau hoi dung vi vay khong phai "PR-AUC bao
    nhieu" ma "trong 113 don duoc xep hang cao nhat, bao nhieu don thuc su bat man,
    va nhu the la gap may lan chon ngau nhien".

    `lift` la cot quan trong nhat: no la ty so giua chinh xac dat duoc va ty le nen.
    Lift 1,0 nghia la xep hang khong hon gi rut ngau nhien.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_score = np.asarray(y_score, dtype=float)
    n, n_pos = len(y_true), int(y_true.sum())
    nen = n_pos / n
    thu_tu = np.argsort(-y_score, kind="stable")

    rows = []
    for k in ks:
        lay = max(1, int(round(n * k)))
        chon = y_true[thu_tu[:lay]]
        trung = int(chon.sum())
        rows.append({
            "k": f"{k:.1%}",
            "so_don_xu_ly": lay,
            "so_don_bat_man_bat_duoc": trung,
            "precision": round(trung / lay, 4),
            "lift": round((trung / lay) / nen, 2),
            "recall": round(trung / n_pos, 4),
        })
    return pd.DataFrame(rows)


def decile_calibration(y_true: np.ndarray, y_prob: np.ndarray,
                       n_groups: int = 10) -> pd.DataFrame:
    """Bang hieu chuan theo thap phan vi — thu ECE mot con so che mat.

    ECE gop moi sai lech thanh mot so, nen no khong noi mo hinh sai o DAU. Bang nay
    noi: neu cot `du_bao` va `thuc_te` lech nhau o nhom cao nhat, do la loi nghiem
    trong hon nhieu so voi lech o nhom thap — nhom cao chinh la nhom duoc can thiep.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_prob = np.asarray(y_prob, dtype=float)
    thu_tu = np.argsort(y_prob, kind="stable")
    nhom = np.array_split(thu_tu, n_groups)

    rows = []
    for i, chi_so in enumerate(nhom, start=1):
        du_bao = float(y_prob[chi_so].mean())
        thuc_te = float(y_true[chi_so].mean())
        rows.append({
            "thap_phan_vi": i,
            "n": len(chi_so),
            "du_bao_tb": round(du_bao, 4),
            "thuc_te": round(thuc_te, 4),
            "lech": round(du_bao - thuc_te, 4),
        })
    return pd.DataFrame(rows)


def brier_vs_constant(y_true: np.ndarray, y_prob: np.ndarray) -> pd.DataFrame:
    """Doi chieu voi HANG SO NEN — phep thu re nhat va hay bi bo qua nhat.

    Mot mo hinh du bao xac suat tren du lieu mat can bang co the co Brier "tot" ma
    van THUA mot mo hinh chi tra ve ty le nen cho moi don. Neu khong dat canh nhau,
    con so Brier tu no khong noi len dieu gi.

    `brier_skill` = 1 - brier_mo_hinh / brier_hang_so. Duong la hon hang so, am la
    thua. Day la con so phai bao cao, khong phai Brier tho.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_prob = np.asarray(y_prob, dtype=float)
    nen = float(y_true.mean())

    brier_mo_hinh = float(np.mean((y_prob - y_true) ** 2))
    brier_hang_so = float(np.mean((nen - y_true) ** 2))
    skill = 1.0 - brier_mo_hinh / brier_hang_so if brier_hang_so > 0 else float("nan")

    return pd.DataFrame([
        {"mo_hinh": "du bao", "brier": round(brier_mo_hinh, 6)},
        {"mo_hinh": f"hang so = ty le nen ({nen:.4f})", "brier": round(brier_hang_so, 6)},
        {"mo_hinh": "brier skill score", "brier": round(skill, 4)},
    ])


def forecasting_report(y_true: np.ndarray, y_score: np.ndarray, *,
                       seed: int = 0, n_boot: int = DEFAULT_BOOTSTRAP) -> dict:
    """Bo chi so day du cho tang du bao, theo dung thu tu uu tien.

    Thu tu KHONG tuy y. PR-AUC va precision@k truoc vi chung do dung thu nghiep vu
    quan tam; ROC-AUC cuoi cung va duoc danh dau la phu, vi tren du lieu mat can
    bang no cho mot con so trong kha quan hon thuc te.
    """
    return {
        "1_tong_hop": evaluate(y_true, y_score, seed=seed, n_boot=n_boot),
        "2_precision_at_k": precision_at_k(y_true, y_score),
        "3_hieu_chuan_thap_phan_vi": decile_calibration(y_true, y_score),
        "4_doi_chieu_hang_so": brier_vs_constant(y_true, y_score),
    }
