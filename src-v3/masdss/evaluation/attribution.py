"""WP10 / T10.2 — Do quy ket nguyen nhan tren gold set. **Chi so chinh cua RQ3.**

Phuc vu: RQ3, gia thuyet H2.

HAI CO CHE CHONG TU LUA, ca hai cuong che bang MA NGUON chu khong bang ky luat:

  1. CHI NHAN `GoldLabels`. Truyen `WeakLabels` vao se raise. Vong tron
     *sinh nhan -> huan luyen -> danh gia bang chinh nhan da sinh* rat de len lai
     sau vai thang, va mot cau ghi chu trong tai lieu khong chan duoc no.

  2. MANG THEO `Provenance`. Bo nhan hien tai do mot mo hinh ngon ngu sinh va
     nguoi ra soat (L26), nen moi bang ket qua deu mang co `citable=False`. So
     dung duoc de kiem tra luong thong tin; khong duoc trich vao Chuong 5. Khi
     vong gan nhan doc lap xong, doi mot tham so la co tu doi.

YEU CAU CONG BANG VOI DOI CHUNG — RQ3 §2.2 phat bieu ro. Doi chung don khoi phai
la bo phan loai DA NHAN, dung CHUNG cause head, CHUNG nguong. Neu no bi chan khong
cho tra ve nhieu nhan thi co che da tac tu thang o tinh huong (a) THEO CAU TAO, va
do dung la loi baseline bu nhin ma nghien cuu da cam ket tranh. Khac biet duy nhat
duoc phep la CACH TO CHUC: dau thau, phan xu, quyen tu choi, ngan sach.

CAT LOP LA BAT BUOC, khong phai tuy chon. Macro-F1 gop che mat dung hai tinh huong
kho ma RQ3 neu dich danh: (a) don da nguyen nhan, (b) don khong co van ban.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from masdss.core.errors import WeakLabelInEvaluation
from masdss.data.labels import CAUSE_COLUMNS, GoldLabels, Provenance

CAUSES = tuple(c.replace("cause_", "") for c in CAUSE_COLUMNS)


@dataclass(frozen=True)
class AttributionResult:
    """Ket qua kem NGUON GOC. Con so khong bao gio di mot minh."""

    per_cause: pd.DataFrame
    per_slice: pd.DataFrame
    provenance: Provenance

    @property
    def citable(self) -> bool:
        return self.provenance.citable

    def stamped(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Hai bang, moi bang deu co cot `citable` — de khong tach roi khoi nguon."""
        per_cause = self.per_cause.copy()
        per_slice = self.per_slice.copy()
        for frame in (per_cause, per_slice):
            frame["provenance"] = self.provenance.value
            frame["citable"] = self.provenance.citable
        return per_cause, per_slice


def _require_gold(labels) -> GoldLabels:
    """Duong duy nhat nhan vao module nay. Khong co cua sau."""
    if isinstance(labels, GoldLabels):
        return labels
    raise WeakLabelInEvaluation(
        f"Danh gia quy ket chi nhan GoldLabels, nhan duoc {type(labels).__name__}. "
        "Rang buoc C2: moi con so ve quy ket phai do tren nhan do nguoi gan."
    )


def _prf(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[float, float, float]:
    true_positive = int(((y_true == 1) & (y_pred == 1)).sum())
    predicted = int((y_pred == 1).sum())
    actual = int((y_true == 1).sum())
    precision = true_positive / predicted if predicted else 0.0
    recall = true_positive / actual if actual else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return precision, recall, f1


def _score_block(truth: pd.DataFrame, predicted: pd.DataFrame,
                 system: str) -> list[dict]:
    rows = []
    for cause in CAUSES:
        column = f"cause_{cause}"
        y_true = truth[column].to_numpy()
        y_pred = predicted[column].to_numpy()
        precision, recall, f1 = _prf(y_true, y_pred)
        rows.append({
            "he_thong": system, "nguyen_nhan": cause,
            "n_duong_that": int(y_true.sum()), "n_duong_du_doan": int(y_pred.sum()),
            "precision": round(precision, 4), "recall": round(recall, 4),
            "f1": round(f1, 4),
        })
    return rows


def _macro_f1(truth: pd.DataFrame, predicted: pd.DataFrame) -> float:
    """Macro-F1 tren BA nguyen nhan `CAUSE_COLUMNS`. Khong tinh `unknown`.

    `unknown` la HE QUA cua viec khong quy ket duoc, khong phai mot nguyen nhan
    thu tu. Dua no vao macro se thuong cho he thong nao im lang nhieu nhat.

    (Docstring nay tung ghi "bon nguyen nhan" — con lai tu truoc khi nhan `price`
    bi go ngay 12/08. So nguyen nhan luon lay tu `CAUSE_COLUMNS`, khong viet cung.)
    """
    values = [_prf(truth[f"cause_{c}"].to_numpy(), predicted[f"cause_{c}"].to_numpy())[2]
              for c in CAUSES]
    return float(np.mean(values))


def mcnemar_exact(truth: pd.DataFrame, a: pd.DataFrame, b: pd.DataFrame) -> dict:
    """Kiem dinh McNemar dang NHI THUC CHINH XAC tren cap du doan cua hai he thong.

    VI SAO HAM NAY PHAI TON TAI. Bao cao truoc day dan hai con so — McNemar
    (n = 6, p = 0,219) va khoang tin cay bootstrap cho chenh lech macro-F1 — nhung
    KHONG mot ham nao trong ma nguon tinh duoc chung. Chung duoc tinh ngoai roi go
    tay vao tai lieu, vi pham dung hop dong "khong con so nao trong luan van duoc go
    tay" (00-muc-luc §2). Mot con so khong tai lap duoc bang lenh thi khong kiem
    chung duoc, du no dung hay sai.

    Dung nhi thuc CHINH XAC chu khong dung xap xi chi-binh-phuong: so o bat dong
    thuong rat nho (bac cau 6/250 o ban do truoc), va xap xi khong dung o co mau do.

    Don vi dem la (don x nguyen nhan) — moi o la mot du doan nhi phan. Bat dong tinh
    tren nhung o ma dung MOT trong hai he doan dung.
    """
    from scipy import stats

    y = np.concatenate([truth[c].to_numpy() for c in CAUSE_COLUMNS])
    pa = np.concatenate([a[c].to_numpy() for c in CAUSE_COLUMNS])
    pb = np.concatenate([b[c].to_numpy() for c in CAUSE_COLUMNS])

    a_dung_b_sai = int(((pa == y) & (pb != y)).sum())
    b_dung_a_sai = int(((pb == y) & (pa != y)).sum())
    n_bat_dong = a_dung_b_sai + b_dung_a_sai

    if n_bat_dong == 0:
        return {
            "n_bat_dong": 0, "a_dung_b_sai": 0, "b_dung_a_sai": 0, "p_value": None,
            "ghi_chu": ("Khong o nao bat dong — hai he thong cho ket qua GIONG HET "
                        "nhau. McNemar tro thanh tautology: khong co gi de kiem dinh. "
                        "Bao cao nhu mot dang thuc, KHONG nhu mot ket qua thong ke."),
        }
    p = float(stats.binomtest(a_dung_b_sai, n_bat_dong, 0.5).pvalue)
    return {
        "n_bat_dong": n_bat_dong, "a_dung_b_sai": a_dung_b_sai,
        "b_dung_a_sai": b_dung_a_sai, "p_value": round(p, 6),
        "ghi_chu": "Nhi thuc chinh xac hai phia tren cac o bat dong.",
    }


def bootstrap_macro_f1_diff(truth: pd.DataFrame, a: pd.DataFrame, b: pd.DataFrame, *,
                            n_boot: int = 1000, seed: int = 0,
                            alpha: float = 0.05) -> dict:
    """Khoang tin cay bootstrap cho CHENH LECH macro-F1 giua hai he thong.

    Lay mau lai theo DON, khong theo o: hai he thong duoc cham diem tren cung mot
    don nen chung phai duoc lay mau CUNG NHAU (bootstrap theo cap). Lay mau doc lap
    se lam khoang tin cay rong ra mot cach gia tao.

    Ghi lai `n_boot_hieu_dung` — so lan lap thuc su dung duoc. `bootstrap_ci` o
    `forecasting.py` BO QUA mau don-lop ma khong ghi lai, nen so lan lap thuc te co
    the nho hon con so khai bao ma khong ai biet.
    """
    rng = np.random.default_rng(seed)
    n = len(truth)
    diffs = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        t, fa, fb = truth.iloc[idx], a.iloc[idx], b.iloc[idx]
        diffs.append(_macro_f1(t, fa) - _macro_f1(t, fb))
    diffs = np.asarray(diffs, dtype=float)
    diffs = diffs[np.isfinite(diffs)]
    point = _macro_f1(truth, a) - _macro_f1(truth, b)
    if len(diffs) == 0:
        return {"chenh_lech": round(point, 6), "ci_lower": None, "ci_upper": None,
                "n_boot_hieu_dung": 0, "chua_khong": None}
    lower = float(np.quantile(diffs, alpha / 2))
    upper = float(np.quantile(diffs, 1 - alpha / 2))
    return {
        "chenh_lech": round(point, 6),
        "ci_lower": round(lower, 6), "ci_upper": round(upper, 6),
        "n_boot_hieu_dung": int(len(diffs)),
        "chua_khong": bool(lower <= 0.0 <= upper),
    }


def compare_systems(gold, predictions: dict[str, pd.DataFrame], *,
                    key: str = "order_id", seed: int = 0,
                    n_boot: int = 1000) -> pd.DataFrame:
    """Doi dau TUNG CAP he thong: McNemar + KTC bootstrap cho chenh lech macro-F1.

    Day la bang tra loi truc tiep cau hoi cua RQ3 — "co danh doi do chinh xac
    khong" — va la bang duy nhat trong `evaluation/` co tinh KIEM DINH. Moi bang
    khac la MO TA, va su phan biet do phai duoc giu khi viet Chuong 5: mot bang mo
    ta khong can hieu chinh da kiem dinh, mot bang kiem dinh thi can.
    """
    labels = _require_gold(gold)
    truth = labels.frame.set_index(key).sort_index()

    aligned: dict[str, pd.DataFrame] = {}
    for system, frame in predictions.items():
        frame = frame.set_index(key).reindex(truth.index).fillna(0)
        for column in CAUSE_COLUMNS:
            frame[column] = frame[column].astype(int)
        aligned[system] = frame

    names = list(aligned)
    rows = []
    for i, first in enumerate(names):
        for second in names[i + 1:]:
            mc = mcnemar_exact(truth, aligned[first], aligned[second])
            bs = bootstrap_macro_f1_diff(truth, aligned[first], aligned[second],
                                         n_boot=n_boot, seed=seed)
            rows.append({
                "he_thong_a": first, "he_thong_b": second,
                "n_don": len(truth),
                "n_o_bat_dong": mc["n_bat_dong"],
                "a_dung_b_sai": mc["a_dung_b_sai"],
                "b_dung_a_sai": mc["b_dung_a_sai"],
                "mcnemar_p": mc["p_value"],
                "chenh_lech_macro_f1": bs["chenh_lech"],
                "ci_lower": bs["ci_lower"], "ci_upper": bs["ci_upper"],
                "ktc_chua_khong": bs["chua_khong"],
                "n_boot_hieu_dung": bs["n_boot_hieu_dung"],
                "ghi_chu": mc["ghi_chu"],
                "provenance": labels.provenance.value,
                "citable": labels.provenance.citable,
            })
    return pd.DataFrame(rows)


def evaluate(gold, predictions: dict[str, pd.DataFrame], *,
             key: str = "order_id") -> AttributionResult:
    """So sanh nhieu he thong tren cung gold set.

    `predictions` la {ten he thong -> DataFrame co `key` va ba cot `cause_*`}.
    """
    labels = _require_gold(gold)
    truth = labels.frame.set_index(key).sort_index()

    per_cause_rows: list[dict] = []
    per_slice_rows: list[dict] = []

    # Cat lop: (a) da nguyen nhan, (b) tang B — hai tinh huong kho cua RQ3.
    multi = truth[list(CAUSE_COLUMNS)].sum(axis=1) >= 2
    tier = truth["tier"] if "tier" in truth.columns else pd.Series("A", index=truth.index)
    slices = {
        "toan bo": pd.Series(True, index=truth.index),
        "(a) da nguyen nhan": multi,
        "don nguyen nhan": ~multi,
        "(b) tang B — khong van ban": tier == "B",
        "tang A — co van ban": tier == "A",
    }

    for system, frame in predictions.items():
        aligned = frame.set_index(key).reindex(truth.index).fillna(0)
        for column in CAUSE_COLUMNS:
            aligned[column] = aligned[column].astype(int)
        per_cause_rows.extend(_score_block(truth, aligned, system))

        for name, mask in slices.items():
            if not mask.any():
                continue
            per_slice_rows.append({
                "he_thong": system, "cat_lop": name, "n": int(mask.sum()),
                "macro_f1": round(_macro_f1(truth[mask], aligned[mask]), 4),
                "ty_le_khong_quy_ket": round(float(
                    (aligned[mask][list(CAUSE_COLUMNS)].sum(axis=1) == 0).mean()), 4),
            })

    return AttributionResult(
        per_cause=pd.DataFrame(per_cause_rows),
        per_slice=pd.DataFrame(per_slice_rows),
        provenance=labels.provenance,
    )
