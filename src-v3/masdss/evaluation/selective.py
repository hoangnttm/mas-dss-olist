"""WP10 / T10.3 — Selective prediction: do chinh xac o CUNG MUC DO PHU.

Phuc vu: RQ3, nguyen ly DP3.

VI SAO CHI SO NAY LA BAT BUOC, KHONG PHAI BO SUNG.

    Macro-F1 thuan tuy PHAT viec tu choi tra loi. Neu MAS-DSS phat `REFUSE` tren
    phan lon nhung don thieu bang chung thi recall cua no o do tien ve 0, va no
    THUA THEO CAU TAO — trong khi tu choi moi la hanh vi dung ve mat tri thuc luan.
    Do la DP3 tu tru diem chinh no.

    Cach sua khong phai bo macro-F1 ma la doc no CUNG voi do phu: bao cao dong thoi
    *do chinh xac tren phan da tra loi* va *ty le da tra loi*, roi doi chieu hai
    kien truc o CUNG MUC PHU. Hai he tra loi 100% so nhau bang F1 la cong bang; mot
    he tra loi 40% va mot he tra loi 100% thi khong.

DOC BANG KET QUA THE NAO.

    `do_phu`      — ty le don ma he thong co dua ra it nhat mot quy ket
    `f1_da_tra_loi` — macro-F1 tinh RIENG tren nhung don do
    `f1_toan_bo`  — macro-F1 tren tat ca, tu choi tinh la bo sot

    Chenh lech giua hai cot F1 chinh la cai gia cua viec im lang. Neu `f1_da_tra_loi`
    cao hon han trong khi do phu thap, he thong dang tu choi DUNG CHO — no im lang o
    nhung don no khong biet. Neu hai cot bang nhau, viec tu choi khong mang thong tin.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from masdss.data.labels import CAUSE_COLUMNS

from .attribution import _macro_f1, _require_gold

# Cac muc do phu de doi chieu hai kien truc tai cung mot diem.
COVERAGE_GRID = (0.2, 0.4, 0.6, 0.8, 1.0)


# Ten cot do tin cay ma moi khung du doan phai mang theo. Xem `_rank_by_confidence`.
CONFIDENCE_COLUMN = "confidence"


def _answered(frame: pd.DataFrame) -> pd.Series:
    """Don duoc coi la 'da tra loi' khi he thong dua ra it nhat mot quy ket."""
    return frame[list(CAUSE_COLUMNS)].sum(axis=1) > 0


def _rank_by_confidence(frame: pd.DataFrame, system: str) -> pd.Series:
    """Thu hang cua tung don theo do tin cay GIAM DAN — 0 la tu tin nhat.

    VI SAO HAM NAY TON TAI, va vi sao no NEM LOI thay vi co gia tri mac dinh.

        Ban truoc cat muc do phu bang VI TRI DONG trong DataFrame:

            mask = answered & (pd.Series(np.arange(len(answered)), ...) < int(level * n))

        Khung da duoc `sort_index()` theo `order_id`, nen phep cat do la cat NGAU
        NHIEN CO HE THONG chu khong phai selective prediction. Mot duong risk-coverage
        chi co nghia khi he thong duoc phep GIU LAI nhung don no TU TIN NHAT: do dung
        la thu ma "do chinh xac o cung muc do phu" hoi.

        Bug nay song sot duoc vi no khong bao gio keu len — tep `selective_curve.csv`
        van duoc sinh ra va van doc duoc nhu mot duong risk-coverage. Vi vay o day
        thieu cot do tin cay la LOI DUNG HAN, khong phai canh bao.

    Phep xep hang dung `kind="stable"` de tat dinh khi hai don bang diem (Gate G5).
    """
    if CONFIDENCE_COLUMN not in frame.columns:
        raise ValueError(
            f"khung du doan cua '{system}' thieu cot do tin cay "
            f"'{CONFIDENCE_COLUMN}' — khong dung duoc duong risk-coverage. "
            "Xem `evaluation/selective._rank_by_confidence`."
        )
    scores = pd.to_numeric(frame[CONFIDENCE_COLUMN], errors="coerce").fillna(0.0)
    order = np.argsort(-scores.to_numpy(), kind="stable")
    rank = np.empty(len(order), dtype=int)
    rank[order] = np.arange(len(order))
    return pd.Series(rank, index=frame.index)


def report(gold, predictions: dict[str, pd.DataFrame], *,
           key: str = "order_id") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Tra ve (duong cong risk-coverage, bang tom tat)."""
    labels = _require_gold(gold)
    truth = labels.frame.set_index(key).sort_index()
    tier = truth["tier"] if "tier" in truth.columns else pd.Series("A", index=truth.index)

    summary_rows, curve_rows = [], []
    for system, frame in predictions.items():
        if CONFIDENCE_COLUMN not in frame.columns:
            raise ValueError(
                f"khung du doan cua '{system}' thieu cot do tin cay "
                f"'{CONFIDENCE_COLUMN}' — khong dung duoc duong risk-coverage. "
                "Xem `evaluation/selective._rank_by_confidence`."
            )
        aligned = frame.set_index(key).reindex(truth.index).fillna(0)
        for column in CAUSE_COLUMNS:
            aligned[column] = aligned[column].astype(int)

        answered = _answered(aligned)
        rank = _rank_by_confidence(aligned, system)
        coverage = float(answered.mean())
        f1_all = _macro_f1(truth, aligned)
        f1_answered = _macro_f1(truth[answered], aligned[answered]) if answered.any() else 0.0

        # Ty le quy ket SAI khi con nguoi bo trong — chi so trung tam cua tang B,
        # noi su that nen la "khong quy ket duoc". Mot he khong biet tu choi se an
        # diem phat o day, va do dung la dieu DP3 tuyen bo.
        human_silent = truth[list(CAUSE_COLUMNS)].sum(axis=1) == 0
        false_attribution = (float(answered[human_silent].mean())
                             if human_silent.any() else float("nan"))

        summary_rows.append({
            "he_thong": system,
            "do_phu": round(coverage, 4),
            "f1_da_tra_loi": round(f1_answered, 4),
            "f1_toan_bo": round(f1_all, 4),
            "gia_cua_im_lang": round(f1_answered - f1_all, 4),
            "quy_ket_sai_khi_nguoi_bo_trong": (round(false_attribution, 4)
                                               if not np.isnan(false_attribution) else None),
            "do_phu_tang_B": (round(float(answered[tier == "B"].mean()), 4)
                              if (tier == "B").any() else None),
        })

        for level in COVERAGE_GRID:
            # Giu lai `level` phan tram don MA HE THONG TU TIN NHAT. Don khong tra
            # loi mang do tin cay 0 nen tu roi xuong cuoi bang xep hang.
            mask = answered if level >= 1.0 else (
                answered & (rank < int(level * len(answered))))
            if not mask.any():
                continue
            curve_rows.append({
                "he_thong": system, "muc_phu_muc_tieu": level,
                "do_phu_that": round(float(mask.mean()), 4),
                "macro_f1": round(_macro_f1(truth[mask], aligned[mask]), 4),
            })

    return pd.DataFrame(curve_rows), pd.DataFrame(summary_rows)
