"""WP1 / T1.6 — Chia tap THEO THOI GIAN.

Phuc vu: ca ba RQ (moi con so deu dua tren phep chia nay).

VI SAO KHONG CHIA NGAU NHIEN: dac trung thong ke theo seller va theo nhom hang
duoc hoc tu tap train. Neu chia ngau nhien, mot don thang 3/2018 co the nam trong
train con mot don thang 1/2018 nam trong test — mo hinh se biet truoc tuong lai.
Chia theo thoi gian mo phong dung tinh huong trien khai that: hoc tu qua khu,
du bao cho tuong lai.

Ba tap, khong hai tap:
    train — huan luyen mo hinh, hoc thong ke seller/nhom hang
    val   — HIEU CHUAN xac suat (isotonic) va chon nguong
    test  — chi cham diem, khong bao gio duoc nhin trong luc phat trien

Hieu chuan tren tap test se cho ket qua lac quan gia. Do la ly do co tap val rieng.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

TIME_COLUMN = "order_purchase_timestamp"


class SplitLeakageError(ValueError):
    """Ranh gioi thoi gian bi vi pham."""


@dataclass(frozen=True)
class Splits:
    train: pd.DataFrame
    val: pd.DataFrame
    test: pd.DataFrame

    @property
    def sizes(self) -> dict[str, int]:
        return {"train": len(self.train), "val": len(self.val), "test": len(self.test)}

    def boundaries(self) -> dict[str, tuple[str, str]]:
        out = {}
        for name, part in (("train", self.train), ("val", self.val), ("test", self.test)):
            out[name] = (str(part[TIME_COLUMN].min()), str(part[TIME_COLUMN].max()))
        return out


def time_split(df: pd.DataFrame, train_frac: float = 0.70,
               val_frac: float = 0.15) -> Splits:
    """Chia theo phan vi thoi gian. Tat dinh, khong co nguon ngau nhien nao."""
    if not 0 < train_frac < 1 or not 0 < val_frac < 1 or train_frac + val_frac >= 1:
        raise ValueError("ty le chia khong hop le")

    work = df.dropna(subset=[TIME_COLUMN]).sort_values([TIME_COLUMN, "order_id"])
    n = len(work)
    i_train = int(n * train_frac)
    i_val = int(n * (train_frac + val_frac))

    splits = Splits(
        train=work.iloc[:i_train].copy(),
        val=work.iloc[i_train:i_val].copy(),
        test=work.iloc[i_val:].copy(),
    )
    assert_no_time_leakage(splits)
    return splits


def assert_no_time_leakage(splits: Splits) -> None:
    """Cuong che trong ma nguon, khong pho mac ky luat.

    Dieu kien: moc muon nhat cua tap truoc phai <= moc som nhat cua tap sau.
    """
    chain = (("train", splits.train), ("val", splits.val), ("test", splits.test))
    for (name_a, part_a), (name_b, part_b) in zip(chain, chain[1:]):
        if part_a.empty or part_b.empty:
            continue
        latest_a = part_a[TIME_COLUMN].max()
        earliest_b = part_b[TIME_COLUMN].min()
        if latest_a > earliest_b:
            raise SplitLeakageError(
                f"ranh gioi {name_a}/{name_b} bi vi pham: {name_a} ket thuc {latest_a} "
                f"nhung {name_b} bat dau {earliest_b}"
            )
