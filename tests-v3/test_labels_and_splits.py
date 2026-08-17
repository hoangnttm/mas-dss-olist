"""WP1 / T1.5, T1.6 — Nhan va chia tap.

Phuc vu: RQ3 (rang buoc C2 va chong ro ri thoi gian).
"""

from __future__ import annotations

import pandas as pd
import pytest

from masdss.core.errors import WeakLabelInEvaluation
from masdss.data.labels import (
    CAUSE_COLUMNS,
    GoldLabels,
    Provenance,
    WeakLabels,
    make_weak_labels,
    label_dissatisfaction,
)
from masdss.data.splits import SplitLeakageError, Splits, assert_no_time_leakage, time_split


def _frame(texts, delays=None):
    n = len(texts)
    return pd.DataFrame({
        "order_id": [f"o{i}" for i in range(n)],
        "review_title": [""] * n,
        "review_content": texts,
        "delivery_delay_days": delays if delays is not None else [0.0] * n,
    })


# --- T1.5: hai kieu nhan tach biet ---

def test_weak_labels_cannot_be_used_for_evaluation() -> None:
    """Rang buoc C2 duoc cuong che bang KIEU DU LIEU, khong bang ky luat."""
    weak = make_weak_labels(_frame(["produto quebrado"]))
    assert isinstance(weak, WeakLabels)
    with pytest.raises(WeakLabelInEvaluation):
        weak.for_evaluation()


def test_gold_labels_require_cause_columns() -> None:
    with pytest.raises(ValueError):
        GoldLabels(frame=pd.DataFrame({"order_id": ["o1"]}),
                   provenance=Provenance.HUMAN_INDEPENDENT)


def test_weak_labels_are_multi_label() -> None:
    """`produto quebrado na entrega` — vua quality vua delivery, khong duoc ep mot."""
    weak = make_weak_labels(_frame(["produto chegou quebrado, atraso de 10 dias"]))
    row = weak.frame.iloc[0]
    assert row["cause_quality"] == 1
    assert row["cause_delivery"] == 1


def test_negation_is_respected() -> None:
    """`nao chegou quebrado` = hang KHONG bi vo — khong duoc gan quality."""
    weak = make_weak_labels(_frame(["produto nao chegou quebrado"]))
    assert weak.frame.iloc[0]["cause_quality"] == 0


def test_structural_evidence_only_above_threshold() -> None:
    """Khop quy tac 2 cua codebook: tre duoi 3 ngay ma khong co chu -> unknown."""
    weak = make_weak_labels(_frame(["", ""], delays=[1.0, 18.0]))
    assert weak.frame.iloc[0]["cause_unknown"] == 1
    assert weak.frame.iloc[1]["cause_delivery"] == 1


def test_unknown_is_mutually_exclusive() -> None:
    weak = make_weak_labels(_frame(["produto quebrado", ""], delays=[0.0, 0.0]))
    both = weak.frame[list(CAUSE_COLUMNS)].sum(axis=1) > 0
    assert (weak.frame.loc[both, "cause_unknown"] == 0).all()
    assert (weak.frame.loc[~both, "cause_unknown"] == 1).all()


def test_dissatisfaction_threshold_is_configurable() -> None:
    df = pd.DataFrame({"rating": [1, 2, 3, 4, 5]})
    assert label_dissatisfaction(df).tolist() == [True, True, False, False, False]
    assert label_dissatisfaction(df, max_rating=3).tolist() == [True, True, True, False, False]


# --- T1.6: chia tap theo thoi gian ---

def _timed(n: int) -> pd.DataFrame:
    return pd.DataFrame({
        "order_id": [f"o{i:03d}" for i in range(n)],
        "order_purchase_timestamp": pd.date_range("2017-01-01", periods=n, freq="D"),
    })


def test_time_split_preserves_chronology() -> None:
    splits = time_split(_timed(100))
    assert splits.sizes == {"train": 70, "val": 15, "test": 15}
    assert splits.train["order_purchase_timestamp"].max() <= \
        splits.val["order_purchase_timestamp"].min()
    assert splits.val["order_purchase_timestamp"].max() <= \
        splits.test["order_purchase_timestamp"].min()


def test_leakage_guard_catches_shuffled_split() -> None:
    """Chia ngau nhien phai bi bat — day chinh la loi ma guard sinh ra de chan."""
    df = _timed(100)
    shuffled = df.sample(frac=1.0, random_state=0)
    bad = Splits(train=shuffled.iloc[:70], val=shuffled.iloc[70:85], test=shuffled.iloc[85:])
    with pytest.raises(SplitLeakageError):
        assert_no_time_leakage(bad)


def test_time_split_is_deterministic() -> None:
    a, b = time_split(_timed(100)), time_split(_timed(100))
    assert a.train["order_id"].tolist() == b.train["order_id"].tolist()
