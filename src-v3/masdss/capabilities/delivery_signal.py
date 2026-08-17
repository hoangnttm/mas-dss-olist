"""WP3 — Tin hieu giao hang: z-score muc tre theo nhom hang.

Phuc vu: RQ3 (Delivery Analyst dau thau kem bang chung).

Cung hinh dang voi `price_signal.py` va co chu dich: hai analyst re nay phai so
sanh duoc voi nhau trong phien dau thau, nen do tin cay cua chung phai duoc sinh
ra theo cung mot co che (z-score trong noi bo nhom hang) va duoc hieu chuan bang
cung mot phuong phap o T7.3.

Vi sao z-score theo nhom hang chu khong phai nguong tre tuyet doi: 5 ngay tre voi
do noi that cong kenh khac han 5 ngay tre voi mot mon phu kien. Chuan hoa trong
noi bo nhom hang lam cho bang chung co nghia.

RANG BUOC CHONG RO RI: `fit()` chi nhan tap train, cuong che bang tham so
`split_name`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from masdss.core.ontology import Cause, Evidence, OrderCase

DEFAULT_MIN_SAMPLES = 30
DEFAULT_Z_THRESHOLD = 0.5


@dataclass
class DeliverySignal:
    """Z-score cua `delivery_delay_days` trong noi bo tung nhom hang."""

    min_samples: int = DEFAULT_MIN_SAMPLES
    z_threshold: float = DEFAULT_Z_THRESHOLD

    name: str = "delivery_signal"
    cost_ms: float = 0.3

    _stats: dict[str, tuple[float, float, int]] = field(default_factory=dict)
    prior_confidence: float = 0.55
    _fitted: bool = False

    def fit(self, train: pd.DataFrame, *, split_name: str = "train") -> "DeliverySignal":
        if split_name != "train":
            raise ValueError(
                f"DeliverySignal.fit() chi duoc nhan tap train, nhan '{split_name}'"
            )
        grouped = (train.dropna(subset=["delivery_delay_days"])
                        .groupby("category")["delivery_delay_days"])
        self._stats = {
            str(category): (float(v.mean()), float(v.std(ddof=0)), int(len(v)))
            for category, v in grouped
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
        subset = train.dropna(subset=["delivery_delay_days"]).head(sample)
        values: list[float] = []
        for category, group in subset.groupby("category"):
            stats = self._stats.get(str(category))
            if stats is None:
                continue
            mean, std, n = stats
            if n < self.min_samples or std <= 0:
                continue
            z = (group["delivery_delay_days"].astype(float) - mean) / std
            emitted = z[z >= self.z_threshold]
            if len(emitted):
                values.extend(
                    np.minimum(0.95, 0.45 + 0.2 * (emitted - self.z_threshold)).tolist()
                )
        if values:
            self.prior_confidence = float(np.mean(values))

    # --- giao dien Capability ---

    def can_handle(self, case: OrderCase) -> bool:
        """Dieu kien REFUSE: thieu moc thoi gian giao hang thi khong co gi de noi."""
        if not self._fitted:
            return False
        delay = case.features.get("delivery_delay_days")
        if delay is None or (isinstance(delay, float) and np.isnan(delay)):
            return False
        stats = self._stats.get(str(case.features.get("category", "")))
        return stats is not None and stats[2] >= self.min_samples and stats[1] > 0

    def refusal_reason(self, case: OrderCase) -> str:
        delay = case.features.get("delivery_delay_days")
        if delay is None or (isinstance(delay, float) and np.isnan(delay)):
            return "thieu moc thoi gian giao hang"
        category = str(case.features.get("category", ""))
        stats = self._stats.get(category)
        if stats is None:
            return f"nhom hang '{category}' khong co trong tap train"
        return f"nhom hang '{category}' chi co {stats[2]} mau (< {self.min_samples})"

    def run(self, case: OrderCase) -> tuple[float, tuple[Evidence, ...]]:
        if not self.can_handle(case):
            return 0.0, ()

        category = str(case.features["category"])
        mean, std, _ = self._stats[category]
        delay = float(case.features["delivery_delay_days"])
        z = (delay - mean) / std
        if z < self.z_threshold:
            return 0.0, ()

        confidence = float(min(0.95, 0.45 + 0.2 * (z - self.z_threshold)))
        evidence = (
            Evidence(
                kind="delivery_delay",
                detail=(f"giao tre {delay:.1f} ngay so voi du kien, "
                        f"cao hon trung binh nhom '{category}' {z:.1f} do lech chuan"),
                value=round(z, 3),
            ),
        )
        return confidence, evidence

    @property
    def cause(self) -> Cause:
        return Cause.DELIVERY


@dataclass
class CombinedDeliverySignal:
    """HOP hai nguon bang chung cho `delivery`: cau truc VA van ban.

    VI SAO CAN. Codebook dinh nghia `delivery` la DICH VU GIAO HANG — tre hen,
    khong toi, that lac, thieu mon, vo trong luc giao. `DeliverySignal` chi do MOT
    mat: z-score do tre so voi trung binh nhom hang. Do tren gold set, nhanh cau
    truc dat F1 0,4074 trong khi bo phan loai van ban cua `CauseHead` — von da duoc
    huan luyen san nhung KHONG tac tu nao cam vao — dat 0,7526.

    Hop hai nguon cho recall cao nhat va giu duoc mot tinh chat ma phuong an "thay
    han bang van ban" danh mat:

        `DeliverySignal` la nguon bang chung DUY NHAT khong phu thuoc van ban. Neu
        ca ba analyst cung doc mot `CauseHead`, thi khi head do hong CA BA hong cung
        luc — mot tuong quan loi ma RQ1 quan tam truc tiep. Giu nhanh cau truc lam
        cho `delivery` van con tieng noi khi tang van ban sup.

    DAT O `capabilities/` CHU KHONG O `agents/`: day la logic ket hop bang chung,
    va no phai duoc MAS-DSS lan Monolithic-Complete dung CHUNG. Neu chi MAS duoc
    nguon hop nhat thi doi chung bi lam yeu — dung loi ma nghien cuu da cam ket
    tranh (technical-plan-v3.md §A.10).
    """

    structural: DeliverySignal
    head: object                      # CauseHead — nhanh `delivery` cua no
    name: str = "delivery_combined"
    _fitted: bool = True

    @property
    def cost_ms(self) -> float:
        """Cong don: phai chay CA HAI nguon moi ket luan duoc."""
        return float(self.structural.cost_ms) + float(getattr(self.head, "cost_ms", 0.0))

    @property
    def prior_confidence(self) -> float:
        """Tien nghiem cua nguon MANH HON.

        Hop hai nguon khong the te hon nguon tot nhat, nen `max` la can duoi dung.
        Day van la mot tien nghiem cua TONG THE — no khong doi theo tung don, va do
        la gioi han da ghi o build-plan §0.10(c).
        """
        return max(float(self.structural.prior_confidence),
                   float(getattr(self.head, "prior_confidence", 0.0)))

    # --- giao dien Signal ---

    def can_handle(self, case: OrderCase) -> bool:
        """Du dieu kien neu IT NHAT MOT nguon noi duoc dieu gi."""
        return bool(self.structural.can_handle(case) or self.head.can_handle(case))

    def refusal_reason(self, case: OrderCase) -> str:
        return (f"ca hai nguon deu khong ap dung — "
                f"cau truc: {self.structural.refusal_reason(case)}; "
                f"van ban: khong co binh luan")

    def run(self, case: OrderCase) -> tuple[float, tuple[Evidence, ...]]:
        """Do tin cay = MAX; bang chung = HOP.

        Lay `max` chu khong lay trung binh: hai nguon do hai mat khac nhau cua cung
        mot that bai, nen mot nguon im lang KHONG phai bang chung phu dinh. Trung
        binh se phat mot don co bang chung van ban ro rang chi vi don do khong tre
        so voi trung binh nhom hang.

        Bang chung duoc GHEP ca hai de trace noi ro he thong da dua vao gi.
        """
        c1, e1 = (self.structural.run(case)
                  if self.structural.can_handle(case) else (0.0, ()))
        c2, e2 = (self.head.score(case, Cause.DELIVERY)
                  if self.head.can_handle(case) else (0.0, ()))
        return max(float(c1), float(c2)), tuple(e1) + tuple(e2)

    @property
    def cause(self) -> Cause:
        return Cause.DELIVERY
