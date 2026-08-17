"""WP1 / T1.3 — FeatureSet loc theo moc quyet dinh.

Phuc vu: RQ3, phan tich do nhay T3/T4 (research-questions-objectives.md §5.3).

Doi giua cac moc chi bang MOT thay doi cau hinh, khong phan nhanh ma nguon:

    FeatureSet(DecisionPoint.T3)   # giai doan 1 — du bao rui ro, chua co van ban
    FeatureSet(DecisionPoint.T4)   # giai doan 2 — quy ket nguyen nhan, co van ban

Nho vay khong the vo tinh ro ri dac trung cua moc muon vao moc som hon, va thi
nghiem do nhay la mot lan doi cau hinh chu khong phai mot lan viet lai pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from masdss.core.ontology import DecisionPoint
from masdss.data.features import BANNED_FEATURES, FeatureSpec, available_at_or_before


class LeakageError(ValueError):
    """Mot dac trung cua moc muon lot vao moc som hon, hoac mot dac trung bi cam."""


@dataclass(frozen=True)
class FeatureSet:
    decision_point: DecisionPoint

    @property
    def specs(self) -> tuple[FeatureSpec, ...]:
        return available_at_or_before(self.decision_point)

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(spec.name for spec in self.specs)

    @property
    def numeric_names(self) -> tuple[str, ...]:
        return tuple(s.name for s in self.specs if s.kind in ("numeric", "boolean"))

    def select(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cat bang du lieu xuong dung nhung cot hop le tai moc nay."""
        self.assert_no_leakage(df.columns)
        present = [name for name in self.names if name in df.columns]
        return df[present].copy()

    def assert_no_leakage(self, columns) -> None:
        """Chan hai loai vi pham truoc khi du lieu di vao mo hinh."""
        cols = set(columns)
        banned = cols & BANNED_FEATURES & set(self.names)
        if banned:
            raise LeakageError(f"dac trung bi cam co mat trong feature set: {sorted(banned)}")

    def excluded_because_too_late(self) -> tuple[str, ...]:
        """Dac trung ton tai trong he thong nhung CHUA co tai moc nay."""
        from masdss.data.features import REGISTRY

        allowed = set(self.names)
        return tuple(spec.name for spec in REGISTRY if spec.name not in allowed)
