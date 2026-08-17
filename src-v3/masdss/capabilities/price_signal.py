"""WP3 / T3.5 — Tin hieu gia: z-score phi ship theo nhom hang.

Phuc vu: RQ3 (Price Analyst dau thau kem bang chung).

HAI RANG BUOC CHONG RO RI, ca hai deu cuong che trong ma nguon:

  1. `fit()` CHI nhan tap train. Thong ke theo nhom hang hoc tu toan bo du lieu se
     lam ro ri thong tin tuong lai vao tap test.
  2. `can_handle()` tra False khi nhom hang co duoi `min_samples` mau. Day la dieu
     kien REFUSE KIEM CHUNG DUOC cua Price Analyst (DP3) — khong phai mot cau tu
     choi cho co.

Capability nay RAT RE (~0,1ms) va do la thu lam cho Contract Net co ngan sach tro
nen co y nghia: o case rui ro thap, Orchestrator chi du tien moi Price va Delivery,
khong du cho BERTimbau.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from masdss.core.ontology import Cause, Evidence, OrderCase

DEFAULT_MIN_SAMPLES = 30
DEFAULT_Z_THRESHOLD = 1.5


@dataclass
class PriceSignal:
    """Z-score phi ship trong noi bo tung nhom hang."""

    min_samples: int = DEFAULT_MIN_SAMPLES
    z_threshold: float = DEFAULT_Z_THRESHOLD

    name: str = "price_signal"
    cost_ms: float = 0.1

    _stats: dict[str, tuple[float, float, int]] = field(default_factory=dict)
    prior_confidence: float = 0.55
    _fitted: bool = False

    def fit(self, train: pd.DataFrame, *, split_name: str = "train") -> "PriceSignal":
        """Hoc trung binh va do lech chuan cua freight_ratio theo nhom hang.

        Tham so `split_name` ton tai de bien y dinh thanh loi khi sai — goi ham nay
        voi tap khac train se raise, thay vi am tham lam ro ri.
        """
        if split_name != "train":
            raise ValueError(
                f"PriceSignal.fit() chi duoc nhan tap train, nhan duoc '{split_name}'. "
                "Hoc thong ke tu val/test la ro ri thong tin tuong lai."
            )

        grouped = train.dropna(subset=["freight_ratio"]).groupby("category")["freight_ratio"]
        self._stats = {
            str(category): (float(values.mean()), float(values.std(ddof=0)), int(len(values)))
            for category, values in grouped
        }
        self._fitted = True
        # Do tin cay TIEN NGHIEM cho pha 1 Contract Net: trung binh do tin cay cua
        # nhung lan analyst nay THUC SU phat bid tren tap train. Uoc luong nay re va
        # khong can chay capability o pha tham do.
        self._estimate_prior(train)
        return self

    def _estimate_prior(self, train: pd.DataFrame, sample: int = 3000) -> None:
        """Uoc luong do tin cay TIEN NGHIEM cho pha 1 Contract Net.

        Trung binh do tin cay cua nhung lan analyst nay THUC SU phat bid tren tap
        train. Tinh vector hoa tren DataFrame, khong dung `run()` — de uoc luong nay
        khong keo theo chi phi cua chinh capability dang duoc uoc luong.
        """
        subset = train.dropna(subset=["freight_ratio"]).head(sample)
        values: list[float] = []
        for category, group in subset.groupby("category"):
            stats = self._stats.get(str(category))
            if stats is None:
                continue
            mean, std, n = stats
            if n < self.min_samples or std <= 0:
                continue
            z = (group["freight_ratio"].astype(float) - mean) / std
            emitted = z[z >= self.z_threshold]
            if len(emitted):
                values.extend(
                    np.minimum(0.95, 0.5 + 0.15 * (emitted - self.z_threshold)).tolist()
                )
        if values:
            self.prior_confidence = float(np.mean(values))

    # --- giao dien Capability ---

    def can_handle(self, case: OrderCase) -> bool:
        """Dieu kien REFUSE: nhom hang qua it mau thi z-score khong dang tin."""
        if not self._fitted:
            return False
        category = str(case.features.get("category", ""))
        stats = self._stats.get(category)
        if stats is None:
            return False
        _, std, n = stats
        return n >= self.min_samples and std > 0

    def refusal_reason(self, case: OrderCase) -> str:
        category = str(case.features.get("category", ""))
        stats = self._stats.get(category)
        if stats is None:
            return f"nhom hang '{category}' khong co trong tap train"
        _, std, n = stats
        if n < self.min_samples:
            return f"nhom hang '{category}' chi co {n} mau (< {self.min_samples})"
        return f"phuong sai freight_ratio cua '{category}' bang 0"

    def run(self, case: OrderCase) -> tuple[float, tuple[Evidence, ...]]:
        """Tra (confidence, evidence). Thuan, tat dinh, khong side effect."""
        if not self.can_handle(case):
            return 0.0, ()

        category = str(case.features["category"])
        mean, std, _ = self._stats[category]
        ratio = case.features.get("freight_ratio")
        if ratio is None or (isinstance(ratio, float) and np.isnan(ratio)):
            return 0.0, ()

        z = (float(ratio) - mean) / std
        if z < self.z_threshold:
            return 0.0, ()

        # Anh xa z-score sang do tin cay, chan tren o 0.95.
        confidence = float(min(0.95, 0.5 + 0.15 * (z - self.z_threshold)))
        evidence = (
            Evidence(
                kind="freight_zscore",
                detail=(f"phi ship chiem {float(ratio):.1%} tong thanh toan, "
                        f"cao hon trung binh nhom '{category}' {z:.1f} do lech chuan"),
                value=round(z, 3),
            ),
        )
        return confidence, evidence

    @property
    def cause(self) -> Cause:
        return Cause.DELIVERY

    def coverage(self) -> pd.DataFrame:
        """Bao nhieu nhom hang du dieu kien — dung de bao cao ty le REFUSE."""
        rows = [
            {"category": category, "n": n, "std": round(std, 4),
             "eligible": n >= self.min_samples and std > 0}
            for category, (_, std, n) in sorted(self._stats.items())
        ]
        return pd.DataFrame(rows)
