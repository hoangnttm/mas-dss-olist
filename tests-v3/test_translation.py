"""WP2 / T2.8 — Nap ban dich va sinh tep gan nhan vong 3.

Phuc vu: RQ3 (chat luong gold set).

Ban dich duoc tao BEN NGOAI nen khong tai tao duoc bang mot lenh. No la mot cong cu
do moi, va bo kiem tra o day la thu duy nhat chan duoc mot ban dich hong di vao gold
set — noi ma moi con so cua RQ3 se dua vao.
"""

from __future__ import annotations

import pandas as pd

from masdss.cli.freeze_translations import validate


def _frame(n: int = 10) -> pd.DataFrame:
    """Tep gan nhan vong 3: ban goc va ban dich nam trong CUNG mot tep."""
    return pd.DataFrame({
        "sample_id": [f"G{i:04d}" for i in range(n)],
        "review_content": [f"o produto nao chegou {i}" for i in range(n)],
        "review_content_en": [f"the product did not arrive {i}" for i in range(n)],
    })


def test_clean_translation_passes() -> None:
    assert validate(_frame()) == []


def test_missing_column_is_caught_first() -> None:
    bad = pd.DataFrame({"sample_id": ["G0001"]})
    problems = validate(bad)
    assert problems and "thieu cot" in problems[0]


def test_empty_translation_is_caught() -> None:
    """Loi thuc te hay gap nhat: quen DAN GIA TRI nen o cong thuc xuat ra rong."""
    frame = _frame()
    frame.loc[:3, "review_content_en"] = ""
    assert any("ban dich rong" in p for p in validate(frame))


def test_untranslated_passthrough_is_caught() -> None:
    """Ban dich trung y het ban goc la dau hieu cong thuc chua chay."""
    frame = _frame()
    frame["review_content_en"] = frame["review_content"]
    assert any("trung y het ban goc" in p for p in validate(frame))


def test_empty_source_needs_no_translation() -> None:
    """Dong khong co van ban goc thi ban dich rong la hop le."""
    frame = _frame(5)
    frame.loc[[1, 3], "review_content"] = ""
    frame.loc[[1, 3], "review_content_en"] = ""
    assert validate(frame) == []


def test_a_few_identical_rows_are_tolerated() -> None:
    """Mot vai dong trung nhau la binh thuong — vi du van ban chi co mot tu."""
    frame = _frame(30)
    frame.loc[:1, "review_content_en"] = frame.loc[:1, "review_content"]
    assert validate(frame) == []
