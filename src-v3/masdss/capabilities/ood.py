"""WP3 / T3.2 — Phat hien ngoai phan phoi huan luyen.

Phuc vu: RQ3 (DP3 — quyen tu choi), RQ1 (phat hien drift).

Day la co so KIEM CHUNG DUOC cua quyen REFUSE: khi vector dac trung cua mot case
nam ngoai phan phoi ma mo hinh da hoc, tac tu phat REFUSE thay vi doan bua. Chi phi
chuyen giao cho nguoi thap hon nhieu chi phi cua mot hanh dong sai.

CHON PHUONG PHAP: khoang cach Mahalanobis tren dac trung so, khong dung
IsolationForest. Ba ly do:
  - Tat dinh hoan toan, khong co thanh phan ngau nhien nao can seed.
  - Re (~0,1ms) nen khong lam meo phep do overhead cua RQ1 ve (d).
  - Nguong dat theo PHAN VI cua chinh tap train, nen giai thich duoc bang mot cau:
    "case nay xa tam phan phoi hon 99% du lieu da hoc".

Cung ham nay duoc Health Monitor dung lai o Dot 3 de phat hien drift phan phoi —
mot chi so, hai muc dich, khong phai hai cai dat.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from masdss.core.ontology import OrderCase

DEFAULT_QUANTILE = 0.99


@dataclass
class OODDetector:
    """Khoang cach Mahalanobis so voi tam cua tap train."""

    quantile: float = DEFAULT_QUANTILE
    name: str = "ood_detector"
    cost_ms: float = 0.1

    _columns: tuple[str, ...] = ()
    _mean: np.ndarray | None = None
    _inv_cov: np.ndarray | None = None
    _threshold: float = float("inf")
    _medians: dict[str, float] = field(default_factory=dict)

    def fit(self, train: pd.DataFrame, columns: tuple[str, ...],
            *, split_name: str = "train") -> "OODDetector":
        if split_name != "train":
            raise ValueError(
                f"OODDetector.fit() chi duoc nhan tap train, nhan '{split_name}'"
            )

        self._columns = tuple(c for c in columns if c in train.columns)
        frame = train[list(self._columns)].astype(float)
        self._medians = {c: float(frame[c].median()) for c in self._columns}
        filled = frame.fillna(pd.Series(self._medians))

        self._mean = filled.mean().to_numpy()
        covariance = np.cov(filled.to_numpy(), rowvar=False)
        # Ridge nho de ma tran luon kha nghich, ke ca khi co cot gan nhu hang so.
        covariance += np.eye(covariance.shape[0]) * 1e-6
        self._inv_cov = np.linalg.inv(covariance)

        distances = self._distance(filled.to_numpy())
        self._threshold = float(np.quantile(distances, self.quantile))
        return self

    def _distance(self, matrix: np.ndarray) -> np.ndarray:
        centered = matrix - self._mean
        return np.sqrt(np.einsum("ij,jk,ik->i", centered, self._inv_cov, centered))

    def score(self, df: pd.DataFrame) -> np.ndarray:
        """Khoang cach Mahalanobis. Cang lon cang xa phan phoi da hoc."""
        if self._mean is None:
            raise RuntimeError("OODDetector chua duoc huan luyen")
        frame = df.reindex(columns=list(self._columns)).astype(float)
        filled = frame.fillna(pd.Series(self._medians))
        return self._distance(filled.to_numpy())

    def is_ood(self, df: pd.DataFrame) -> np.ndarray:
        return self.score(df) > self._threshold

    # --- giao dien Capability ---

    def can_handle(self, case: OrderCase) -> bool:
        return self._mean is not None

    def run(self, case: OrderCase) -> bool:
        """True nghia la case nam NGOAI phan phoi -> tac tu nen phat REFUSE."""
        return bool(self.is_ood(pd.DataFrame([case.features]))[0])

    @property
    def threshold(self) -> float:
        return self._threshold

    def detection_rate(self, df: pd.DataFrame) -> float:
        """Ty le bi danh dau OOD — dung de doi chieu binh thuong voi nhieu loan."""
        return float(self.is_ood(df).mean())
