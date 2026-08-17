"""WP2 / T2.1 — Lay mau phan tang cho gold set.

Phuc vu: RQ3 (dieu kien tien quyet — pha vong tron tu tham chieu).

LAY MAU KHONG CAN XUNG, va day la quyet dinh co chu dich:

    Tang B chi chiem ~25% tong the. Neu lay mau theo dung ty le thi 400 don chi
    cho khoang 100 mau tang B — qua mong de ket luan ve tinh huong kho (b) cua
    RQ3 ("don khong co bang chung van ban"). Phan bo 250 tang A / 150 tang B,
    kem hieu chinh trong so khi bao cao chi so tren toan bo tong the.

Phan tang phu ben trong moi tang: nhom hang x muc tre giao. Bao dam mau phu duoc
ca ba chieu ma research-questions-objectives.md §MT2.2 yeu cau.

Toan bo qua trinh nhan SEED — chay lai cho dung tap mau, khong bao gio "lay mau
lai cho ra ket qua dep hon".
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from masdss.config import CONFIG

DELAY_BUCKETS = [(-np.inf, 0, "dung_han"), (0, 3, "tre_1_3"),
                 (3, 10, "tre_4_10"), (10, np.inf, "tre_tren_10")]


@dataclass(frozen=True)
class SamplePlan:
    """Phan bo mau. Con so mac dinh theo research-questions-objectives.md §MT2.2."""

    n_tier_a: int = 250
    n_tier_b: int = 150
    seed: int = CONFIG.seed

    @property
    def total(self) -> int:
        return self.n_tier_a + self.n_tier_b


def _delay_bucket(days: float) -> str:
    if pd.isna(days):
        return "khong_ro"
    for low, high, label in DELAY_BUCKETS:
        if low < days <= high:
            return label
    return "khong_ro"


def _top_categories(df: pd.DataFrame, k: int = 8) -> set[str]:
    return set(df["category"].value_counts().head(k).index)


def _allocate(counts: pd.Series, total: int) -> dict:
    """Phan bo theo ty le voi phuong phap phan du lon nhat.

    Bao dam tong dung bang `total` va moi tang co mat co ton tai trong tong the
    deu duoc lay it nhat mot mau.
    """
    weights = counts / counts.sum()
    exact = weights * total
    base = np.floor(exact).astype(int)
    base = np.maximum(base, 1)  # moi tang phai co it nhat 1 mau

    while base.sum() > total and (base > 1).any():
        base[base.idxmax()] -= 1
    remainder = total - base.sum()
    if remainder > 0:
        order = (exact - base).sort_values(ascending=False).index
        for key in list(order) * (remainder // len(order) + 1):
            if remainder == 0:
                break
            base[key] += 1
            remainder -= 1
    return base.to_dict()


def _sample_tier(df: pd.DataFrame, n: int, rng: np.random.Generator,
                 top_categories: set[str]) -> pd.DataFrame:
    work = df.copy()
    work["delay_bucket"] = work["delivery_delay_days"].map(_delay_bucket)
    work["cat_group"] = work["category"].where(work["category"].isin(top_categories), "khac")
    work["stratum"] = work["cat_group"] + " | " + work["delay_bucket"]

    counts = work["stratum"].value_counts()
    quota = _allocate(counts, n)

    picked: list[pd.DataFrame] = []
    for stratum, want in quota.items():
        pool = work[work["stratum"] == stratum].sort_values("order_id")
        take = min(want, len(pool))
        idx = rng.choice(len(pool), size=take, replace=False)
        picked.append(pool.iloc[np.sort(idx)])

    out = pd.concat(picked, ignore_index=True)
    if len(out) > n:  # cat phan thua mot cach tat dinh
        out = out.sort_values("order_id").head(n)
    return out


def draw_sample(orders: pd.DataFrame, plan: SamplePlan | None = None) -> pd.DataFrame:
    """Rut mau gold set tu bang don hang chuan hoa."""
    plan = plan or SamplePlan()
    dissatisfied = orders[orders["is_dissatisfied"]].copy()
    top_categories = _top_categories(dissatisfied)

    rng = np.random.default_rng(plan.seed)
    tier_a = _sample_tier(dissatisfied[dissatisfied["tier"] == "A"],
                          plan.n_tier_a, rng, top_categories)
    tier_b = _sample_tier(dissatisfied[dissatisfied["tier"] == "B"],
                          plan.n_tier_b, rng, top_categories)

    sample = pd.concat([tier_a, tier_b], ignore_index=True)

    # Xao tron TAT DINH: nguoi gan nhan khong duoc thay mot khoi tang A roi mot
    # khoi tang B — thu tu do se tao thien lech he thong.
    shuffled = sample.sample(frac=1.0, random_state=plan.seed).reset_index(drop=True)
    shuffled.insert(0, "sample_id", [f"G{i:04d}" for i in range(1, len(shuffled) + 1)])
    return shuffled


def sampling_report(sample: pd.DataFrame, population: pd.DataFrame) -> pd.DataFrame:
    """Bang doi chieu mau va tong the — dung de hieu chinh trong so khi bao cao."""
    dissatisfied = population[population["is_dissatisfied"]]
    rows = []
    for tier in ("A", "B"):
        n_pop = int((dissatisfied["tier"] == tier).sum())
        n_smp = int((sample["tier"] == tier).sum())
        rows.append({
            "tier": tier,
            "n_population": n_pop,
            "pct_population": round(100 * n_pop / len(dissatisfied), 2),
            "n_sample": n_smp,
            "pct_sample": round(100 * n_smp / len(sample), 2),
            "weight": round((n_pop / len(dissatisfied)) / (n_smp / len(sample)), 4),
        })
    return pd.DataFrame(rows)
