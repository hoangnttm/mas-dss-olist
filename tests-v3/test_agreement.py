"""WP2 / T2.4 — Cohen's kappa va Gate G2.

Phuc vu: RQ3 (gold set la dieu kien tien quyet).
"""

from __future__ import annotations

import pandas as pd
import pytest

from masdss.goldset.agreement import (
    AnnotationFormatError,
    agreement_report,
    gate_g2,
    validate_annotation,
    weak_label_noise,
)

LABELS = ("cause_delivery", "cause_quality", "cause_service", "cause_unknown")


def _annotation(rows: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    for column in LABELS:
        if column not in frame.columns:
            frame[column] = 0
    return frame


# --- kiem tra dinh dang ---

def test_missing_label_column_raises() -> None:
    with pytest.raises(AnnotationFormatError):
        validate_annotation(pd.DataFrame({"sample_id": ["G0001"]}))


def test_unknown_conflicting_with_specific_cause_is_flagged() -> None:
    """Quy tac §2 codebook: danh unknown thi phai de trong bon nguyen nhan kia."""
    frame = _annotation([
        {"sample_id": "G0001", "cause_delivery": 1, "cause_unknown": 1},
    ])
    report = validate_annotation(frame)
    assert not report.ok
    assert "unknown" in report.problems[0]


def test_out_of_range_value_is_flagged() -> None:
    frame = _annotation([{"sample_id": "G0001", "cause_delivery": 3}])
    assert not validate_annotation(frame).ok


def test_incomplete_annotation_flagged_only_when_required() -> None:
    frame = _annotation([{"sample_id": "G0001"}, {"sample_id": "G0002", "cause_service": 1}])
    assert validate_annotation(frame).ok
    assert not validate_annotation(frame, require_complete=True).ok


# --- kappa ---

def _mean_kappa(report):
    row = report[report["label"].str.startswith("TRUNG BINH")]
    return row["cohen_kappa"].iloc[0]


def test_perfect_agreement_gives_kappa_one() -> None:
    """Can du luot gan duong de kappa co y nghia — xem MIN_POSITIVES_FOR_KAPPA."""
    rows = [{"sample_id": f"G{i:04d}", "cause_delivery": i % 2,
             "cause_quality": (i + 1) % 2} for i in range(60)]
    a = b = _annotation(rows)
    report = agreement_report(a, b)
    assert _mean_kappa(report) == pytest.approx(1.0)
    assert gate_g2(report)[0]


def test_rare_label_is_excluded_from_the_mean() -> None:
    """Nghich ly kappa: nhan cuc hiem cho kappa vo dinh du dong y gan tuyet doi.

    Vong gan nhan thu nhat cho vi du that: nhan `price` (nay da bi go) dong y 98,7% nhung kappa
    = -0,006, vi ca hai nguoi gop lai chi gan duong 5 lan tren 798 luot. Neu dua vao
    trung binh, no keo con so tong tu 0,547 xuong 0,436 va bi bao nham la "nguyen
    nhan bat dong nhat".
    """
    rows_a, rows_b = [], []
    for i in range(60):
        rows_a.append({"sample_id": f"G{i:04d}", "cause_delivery": i % 2,
                       "cause_service": 1 if i == 0 else 0})
        rows_b.append({"sample_id": f"G{i:04d}", "cause_delivery": i % 2,
                       "cause_service": 1 if i == 1 else 0})
    report = agreement_report(_annotation(rows_a), _annotation(rows_b))

    price = report[report["label"] == "cause_service"].iloc[0]
    assert not price["kappa_reliable"], "nhan chi co 2 luot duong phai bi danh dau khong dang tin"

    delivery = report[report["label"] == "cause_delivery"].iloc[0]
    assert delivery["kappa_reliable"]

    # Trung binh chi tinh tren nhan dang tin, nen no khong bi keo tut.
    assert _mean_kappa(report) == pytest.approx(1.0)


def test_gate_message_names_the_rare_label_separately() -> None:
    """Nhan hiem phai duoc neu rieng, khong bi goi la 'bat dong nhat'."""
    rows_a, rows_b = [], []
    for i in range(60):
        rows_a.append({"sample_id": f"G{i:04d}", "cause_delivery": i % 2,
                       "cause_quality": i % 3 == 0, "cause_service": 1 if i == 0 else 0})
        rows_b.append({"sample_id": f"G{i:04d}", "cause_delivery": i % 2,
                       "cause_quality": i % 4 == 0, "cause_service": 0})
    report = agreement_report(_annotation(rows_a), _annotation(rows_b))
    _, message = gate_g2(report)
    assert "cause_service" in message
    assert "hiem" in message


def test_disagreement_lowers_kappa_and_blocks_gate() -> None:
    a = _annotation([
        {"sample_id": f"G{i:04d}", "cause_delivery": i % 2} for i in range(60)
    ])
    b = _annotation([
        {"sample_id": f"G{i:04d}", "cause_delivery": (i + 1) % 2} for i in range(60)
    ])
    report = agreement_report(a, b)
    passed, message = gate_g2(report)
    assert not passed
    assert "codebook" in message


def test_kappa_is_reported_per_cause_not_only_overall() -> None:
    """Kappa gop se che mat viec hai nguoi bat dong o dung nguyen nhan nao."""
    a = _annotation([{"sample_id": f"G{i:04d}", "cause_delivery": 1,
                      "cause_service": i % 2} for i in range(60)])
    b = _annotation([{"sample_id": f"G{i:04d}", "cause_delivery": 1,
                      "cause_service": (i + 1) % 2} for i in range(60)])
    report = agreement_report(a, b)
    assert set(LABELS) <= set(report["label"])
    service = report.loc[report["label"] == "cause_service", "cohen_kappa"].iloc[0]
    assert service < 0


def test_no_common_rows_raises() -> None:
    a = _annotation([{"sample_id": "G0001", "cause_delivery": 1}])
    b = _annotation([{"sample_id": "G9999", "cause_delivery": 1}])
    with pytest.raises(AnnotationFormatError):
        agreement_report(a, b)


# --- do nhieu weak label ---

def test_weak_label_noise_is_quantified() -> None:
    """Day la lan duy nhat weak label duoc dat canh gold — de DO NHIEU."""
    from masdss.data.labels import Provenance, GoldLabels, WeakLabels

    gold = GoldLabels(provenance=Provenance.HUMAN_INDEPENDENT, frame=_annotation([
        {"sample_id": "G0001", "order_id": "o1", "cause_delivery": 1},
        {"sample_id": "G0002", "order_id": "o2", "cause_quality": 1},
    ]))
    weak = WeakLabels(frame=_annotation([
        {"sample_id": "G0001", "order_id": "o1", "cause_delivery": 1},
        {"sample_id": "G0002", "order_id": "o2", "cause_delivery": 1},
    ]))
    noise = weak_label_noise(gold, weak)
    delivery = noise.loc[noise["label"] == "cause_delivery"].iloc[0]
    assert delivery["weak_recall"] == pytest.approx(1.0)
    assert delivery["weak_precision"] == pytest.approx(0.5)

    quality = noise.loc[noise["label"] == "cause_quality"].iloc[0]
    assert quality["weak_recall"] == pytest.approx(0.0)


# --------------------------------------------------------------------------
# L26 — kappa gia dinh hai nguoi do DOC LAP. Neu gia dinh do sai thi kappa van
# cho ra mot con so dep, va do la chO nguy hiem. Bon test duoi canh cho do.
# --------------------------------------------------------------------------

def _frame(labels, notes, confidence="80%"):
    import pandas as pd
    return pd.DataFrame({
        "sample_id": [f"V{i:04d}" for i in range(1, len(labels) + 1)],
        "cause_delivery": [r[0] for r in labels],
        "cause_quality": [r[1] for r in labels],
        "cause_service": [r[2] for r in labels],
        "cause_unknown": [r[3] for r in labels],
        "notes": notes,
        "confidence": [confidence] * len(labels),
    })


def test_kiem_tra_doc_lap_chan_hai_ban_cung_nguon():
    """Tai lap dung tinh huong vong 3: ghi chu trung 96%, kappa 0,957 vo nghia.

    Fixture co CHU Y de hang nhan KHONG trung 100% (12 dong khac nhau), de test
    nay that su canh NGUONG GHI CHU chu khong di nho nhanh kiem tra hang nhan.
    Ban dau toi viet fixture trung 100% ca hai — nen no van xanh khi nguong ghi
    chu bi noi len 0,99, tuc no khong canh gi.
    """
    from masdss.cli.check_validation import independence_check

    nguoi = [(1, 0, 0, 0)] * 40 + [(0, 1, 0, 0)] * 40
    mo_hinh = [(1, 0, 0, 0)] * 40 + [(0, 1, 0, 0)] * 28 + [(0, 0, 1, 0)] * 12
    # 60/80 ghi chu trung — tren nguong 0,30, duoi 0,99.
    chung = [f"Giao hang — su co giao nhan: dong {i}" for i in range(60)]
    ok, message = independence_check(
        _frame(nguoi, chung + [f"nguoi rieng {i}" for i in range(20)]),
        _frame(mo_hinh, chung + [f"mo hinh rieng {i}" for i in range(20)]),
    )
    assert not ok
    assert "KHONG DOC LAP" in message and "notes" in message


def test_kiem_tra_doc_lap_cho_qua_hai_ban_that_su_khac():
    """Hai nguoi doc cung mot cau co the ra cung nhan — nhung khong viet cung
    mot cau ghi chu. Ghi chu khac nhau la dau hieu re nhat cua tinh doc lap."""
    from masdss.cli.check_validation import independence_check

    labels_a = [(1, 0, 0, 0)] * 40 + [(0, 1, 0, 0)] * 40
    labels_b = [(1, 0, 0, 0)] * 35 + [(0, 0, 1, 0)] * 5 + [(0, 1, 0, 0)] * 40
    ok, _ = independence_check(
        _frame(labels_a, [f"nguoi doc: {i}" for i in range(80)], "70%"),
        _frame(labels_b, [f"mo hinh: {i}" for i in range(80)], "90%"),
    )
    assert ok


def test_kiem_tra_doc_lap_chan_ca_khi_ghi_chu_de_trong():
    """Bo trong cot ghi chu khong duoc dung de vuot qua kiem tra: hang nhan
    trung khop 100% tu no da la bang chung chung nguon."""
    from masdss.cli.check_validation import independence_check

    labels = [(1, 0, 0, 0)] * 50 + [(0, 1, 0, 0)] * 30
    ok, message = independence_check(_frame(labels, [""] * 80, ""),
                                     _frame(labels, [""] * 80, ""))
    assert not ok
    assert "hang nhan trung khop" in message


def test_huong_lech_tach_duoc_them_va_bo_sot():
    """Mot kappa tron che mat viec mo hinh quy ket NHIEU hon hay IT hon nguoi."""
    from masdss.cli.check_validation import direction_report

    nguoi = [(1, 0, 0, 0)] * 30 + [(0, 0, 0, 1)] * 10
    mo_hinh = [(1, 0, 0, 0)] * 30 + [(1, 0, 0, 0)] * 10   # bien unknown thanh delivery
    bang = direction_report(_frame(nguoi, [f"a{i}" for i in range(40)]),
                            _frame(mo_hinh, [f"b{i}" for i in range(40)]))
    delivery = bang[bang["nhan"] == "delivery"].iloc[0]
    assert delivery["mo_hinh_them"] == 10 and delivery["mo_hinh_bo_sot"] == 0
    unknown = bang[bang["nhan"] == "unknown"].iloc[0]
    assert unknown["mo_hinh_bo_sot"] == 10
