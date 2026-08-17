"""WP1 / T1.2 — Khai bao dac trung kem `available_at`.

Phuc vu: RQ3 (chong ro ri nhan), phan tich do nhay T3/T4.

MOI dac trung phai khai bao no ton tai tu moc nao. Day la co che duy nhat bao dam
mot dac trung cua moc muon khong lot vao mot moc som hon — va no duoc kiem tra tu
dong boi tests-v3/test_leakage.py, khong pho mac ky luat ca nhan.

Hai dac trung bi CAM VINH VIEN, khong phai chi bi gan moc muon:

  review_lag_days : ro ri nhan trang tron — chi ton tai sau khi danh gia da viet,
                    ma diem danh gia chinh la nhan.
  has_comment     : su hien dien cua binh luan tuong quan rat manh voi nhan
                    (76,6% o muc 1 sao so voi 31,2% o muc 4 sao). O T3 no chua ton
                    tai; dua vao la ro ri ngang hang voi review_lag_days (C4).
"""

from __future__ import annotations

from dataclasses import dataclass

from masdss.core.ontology import DecisionPoint

# Dac trung bi cam trong MOI feature set, o MOI moc.
BANNED_FEATURES: frozenset[str] = frozenset({
    "review_lag_days",
    "has_comment",
    "has_content",
    "has_title",
    "tier",
    "rating",              # la NHAN, khong phai dac trung
    "is_dissatisfied",     # la NHAN
})


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    available_at: DecisionPoint
    kind: str  # "numeric" | "categorical" | "boolean"
    note: str = ""

    def __post_init__(self) -> None:
        if self.name in BANNED_FEATURES:
            raise ValueError(f"'{self.name}' nam trong danh sach cam, khong duoc khai bao")


REGISTRY: tuple[FeatureSpec, ...] = (
    # --- T1: co ngay luc dat hang ---
    FeatureSpec("price", DecisionPoint.T1, "numeric", "tong gia tri hang"),
    FeatureSpec("freight_value", DecisionPoint.T1, "numeric", "tong phi van chuyen"),
    FeatureSpec("freight_ratio", DecisionPoint.T1, "numeric", "phi ship / tong thanh toan"),
    FeatureSpec("n_items", DecisionPoint.T1, "numeric", "so dong hang"),
    FeatureSpec("n_sellers", DecisionPoint.T1, "numeric", "so nguoi ban trong don"),
    FeatureSpec("category", DecisionPoint.T1, "categorical", "nhom hang (tieng Anh)"),

    FeatureSpec("ships_in_days", DecisionPoint.T1, "numeric",
                "han ban giao 3PL cam ket cho nguoi ban, tinh tu luc dat"),
    FeatureSpec("seller_distance_km", DecisionPoint.T1, "numeric",
                "khoang cach nguoi ban - nguoi mua theo tam ma buu chinh"),
    FeatureSpec("seller_prior_orders", DecisionPoint.T1, "numeric",
                "so don TRUOC DO cua nguoi ban — dem luy tien theo thoi gian, "
                "KHONG phai tong tren toan tap (xem L31)"),
    FeatureSpec("payment_installments", DecisionPoint.T1, "numeric", "so ky tra gop"),
    FeatureSpec("payment_sequences", DecisionPoint.T1, "numeric", "so lan thanh toan"),
    FeatureSpec("paid_by_credit_card", DecisionPoint.T1, "boolean",
                "phuong thuc thanh toan chinh la the tin dung"),

    # --- T3: tai MOC THOI GIAN = NGAY MUA + `t3_cutoff_days` ---
    #
    # Bon dac trung nay thay cho `delivery_days` / `delivery_delay_days` / `is_late`
    # o moc T3. Ly do: ba cai do chi biet duoc SAU KHI hang toi, ma tai T3 nhieu don
    # CHUA toi. Dung chung o T3 la dua thong tin tuong lai vao mo hinh — dung nhom
    # don quan trong nhat (ty le bat man 71-83%). Xem L30.
    #
    # Moc neo vao NGAY MUA, khong vao han giao du kien: han du kien roi vao sau luc
    # khach viet danh gia voi 97,6% so don, nen no khong phai mot moc ra quyet dinh
    # kha dung. Xem L33 va rang buoc C3.
    #
    # Cach xu ly dung la KIEM DUYET BEN PHAI: chi ghi nhan nhung gi quan sat duoc
    # tinh den moc, va ghi ro bang mot cot trang thai thay vi de gia tri thieu.
    FeatureSpec("delivery_state", DecisionPoint.T3, "numeric",
                "trang thai tai moc: 0 da giao · 1 dang van chuyen · 2 chua ban giao 3PL"),
    FeatureSpec("observed_delay_days", DecisionPoint.T3, "numeric",
                "do tre so voi han du kien, QUAN SAT DUOC tinh den moc; neu chua giao "
                "thi la khoang cach tu han du kien den moc (kiem duyet ben phai)"),
    FeatureSpec("observed_handover_days", DecisionPoint.T3, "numeric",
                "so ngay den luc ban giao 3PL, kiem duyet tai moc"),
    FeatureSpec("days_to_deadline", DecisionPoint.T3, "numeric",
                "so ngay con lai den han giao cam ket, tinh TAI MOC; am nghia la da "
                "qua han ngay luc ra quyet dinh — day la 'tien do', khong phai ket cuc"),

    # --- T4: khi danh gia da ve ---
    #
    # Ba dac trung ket cuc giao hang nam o day chu khong o T3: chung chi xac dinh
    # duoc sau khi hang da toi. Tai T4 chung hop le cho viec QUY KET nguyen nhan
    # (`DeliverySignal`), nhung van thieu voi 2.841 don khong bao gio duoc giao.
    FeatureSpec("carrier_handover_days", DecisionPoint.T4, "numeric",
                "so ngay tu luc dat den luc ban giao 3PL — ket cuc, khong phai du bao"),
    FeatureSpec("delivery_days", DecisionPoint.T4, "numeric", "tong thoi gian giao — ket cuc"),
    FeatureSpec("delivery_delay_days", DecisionPoint.T4, "numeric",
                "thuc te tru du kien; duong la tre — ket cuc"),
    FeatureSpec("is_late", DecisionPoint.T4, "boolean", "co tre hen hay khong — ket cuc"),

    # --- T4: khi danh gia da ve (chi giai doan 2 duoc dung) ---
    FeatureSpec("review_content", DecisionPoint.T4, "categorical",
                "van ban binh luan — bang chung cua Quality/Service Analyst"),
    FeatureSpec("review_title", DecisionPoint.T4, "categorical", "tieu de binh luan"),
)

_ORDER = {DecisionPoint.T1: 1, DecisionPoint.T2: 2, DecisionPoint.T3: 3, DecisionPoint.T4: 4}


def available_at_or_before(point: DecisionPoint) -> tuple[FeatureSpec, ...]:
    """Dac trung da ton tai tai `point`."""
    limit = _ORDER[point]
    return tuple(spec for spec in REGISTRY if _ORDER[spec.available_at] <= limit)


def spec_of(name: str) -> FeatureSpec:
    for spec in REGISTRY:
        if spec.name == name:
            return spec
    raise KeyError(f"dac trung chua duoc khai bao available_at: '{name}'")
