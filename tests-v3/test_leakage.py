"""WP1 / T1.4 — Test chong ro ri nhan.

Phuc vu: RQ3 (moi con so ve du bao va quy ket deu dua tren feature set nay).

Hai loai vi pham bi chan:
  1. Dac trung cua moc MUON lot vao mot moc som hon.
  2. Dac trung bi CAM VINH VIEN: review_lag_days, has_comment va cac bien the.
"""

from __future__ import annotations

import pytest

from masdss.core.ontology import DecisionPoint
from masdss.data.features import BANNED_FEATURES, REGISTRY, FeatureSpec, spec_of
from masdss.data.featureset import FeatureSet, LeakageError


def test_every_feature_declares_available_at() -> None:
    assert REGISTRY
    for spec in REGISTRY:
        assert isinstance(spec.available_at, DecisionPoint)


def test_review_lag_days_does_not_exist() -> None:
    """Ro ri nhan trang tron — khong duoc ton tai duoi bat ky moc nao."""
    assert "review_lag_days" in BANNED_FEATURES
    with pytest.raises(KeyError):
        spec_of("review_lag_days")


def test_declaring_a_banned_feature_raises() -> None:
    """Khong the khai bao dac trung bi cam, ke ca voi moc muon nhat."""
    for name in ("review_lag_days", "has_comment", "rating"):
        with pytest.raises(ValueError):
            FeatureSpec(name, DecisionPoint.T4, "numeric")


@pytest.mark.parametrize(
    "point,forbidden",
    [
        (DecisionPoint.T1, {"carrier_handover_days", "delivery_delay_days", "review_content"}),
        (DecisionPoint.T2, {"delivery_delay_days", "delivery_days", "review_content"}),
        (DecisionPoint.T3, {"review_content", "review_title"}),
    ],
)
def test_feature_set_excludes_later_features(point, forbidden) -> None:
    names = set(FeatureSet(point).names)
    assert not (names & forbidden), f"{point} chua dac trung cua moc muon: {names & forbidden}"


def test_t3_has_no_text_derived_feature() -> None:
    """Rang buoc C4: tai T3 chua ton tai bang chung van ban nao.

    `has_comment` nguy hiem va de lot: ty le de lai binh luan la 76,6% o muc 1 sao
    so voi 31,2% o muc 4 sao, nen su hien dien cua binh luan tu no da la tin hieu
    manh ve nhan.
    """
    names = set(FeatureSet(DecisionPoint.T3).names)
    assert not any("review" in n or "comment" in n or "text" in n for n in names)
    assert not (names & BANNED_FEATURES)


def test_t4_is_the_only_point_with_text() -> None:
    assert "review_content" in FeatureSet(DecisionPoint.T4).names


def test_feature_sets_are_nested_by_time() -> None:
    """Moc muon hon phai bao ham moc som hon — khong duoc mat dac trung."""
    chain = [DecisionPoint.T1, DecisionPoint.T2, DecisionPoint.T3, DecisionPoint.T4]
    for earlier, later in zip(chain, chain[1:]):
        assert set(FeatureSet(earlier).names) <= set(FeatureSet(later).names)


def test_select_drops_banned_columns_present_in_dataframe() -> None:
    """Bang tho CO chua nhan va cac cot bi cam — select() khong duoc de chung lot qua.

    Day la tinh huong that: `build_order_table()` tra ve ca `rating`, `has_content`,
    `tier`. Chung can cho thong ke mo ta va lay mau, nhung tuyet doi khong duoc di
    vao mo hinh.
    """
    import pandas as pd

    raw_like = pd.DataFrame({
        "price": [10.0],
        "delivery_delay_days": [2.0],
        "rating": [1],            # NHAN
        "has_content": [True],    # ro ri theo C4
        "tier": ["A"],            # dan xuat tu has_content
        "review_content": ["x"],  # chi hop le tu T4
    })

    selected = FeatureSet(DecisionPoint.T3).select(raw_like)
    # `delivery_delay_days` da chuyen sang T4 (L30): no la KET CUC, chi biet sau khi
    # hang toi, nen khong duoc co mat o T3.
    assert set(selected.columns) == {"price"}
    assert "delivery_delay_days" not in selected.columns
    assert not (set(selected.columns) & BANNED_FEATURES)


def test_assert_no_leakage_is_a_real_guard() -> None:
    """Guard phai bao loi that khi bi ep vao trang thai vi pham."""
    fs = FeatureSet(DecisionPoint.T3)
    with pytest.raises(LeakageError):
        # Ep truc tiep: gia su co ai do them dac trung bi cam vao registry.
        FeatureSet.assert_no_leakage(
            _FakeFeatureSet(names=fs.names + ("rating",)), {"rating", "price"}
        )


class _FakeFeatureSet:
    """Thay the toi thieu de kiem tra chinh guard, khong phai kiem tra registry."""

    def __init__(self, names: tuple[str, ...]) -> None:
        self.names = names


# --------------------------------------------------------------------------
# L30 — moc quyet dinh o tang TONG THE, khong chi o tang dac trung.
# L31 — ro ri THOI GIAN trong thong ke tich luy.
# --------------------------------------------------------------------------

def test_dac_trung_ket_cuc_giao_hang_khong_co_o_T3():
    """`delivery_delay_days` va ho hang chi biet duoc SAU KHI hang toi.

    Tai moc T3 co 7,97% don chua toi — va do la nhom co ty le bat man 71-83%. Dua
    do tre thuc te cua chung vao dau vao du bao la dua ket cuc tuong lai vao mo
    hinh, dung o nhom quan trong nhat. Xem L30.
    """
    from masdss.core.ontology import DecisionPoint
    from masdss.data.featureset import FeatureSet

    ket_cuc = {"delivery_delay_days", "delivery_days", "is_late", "carrier_handover_days"}
    o_T3 = set(FeatureSet(DecisionPoint.T3).names)
    assert not (ket_cuc & o_T3), f"dac trung ket cuc lot vao T3: {sorted(ket_cuc & o_T3)}"
    assert ket_cuc <= set(FeatureSet(DecisionPoint.T4).names), "T4 van phai giu chung"


def test_T3_co_dac_trung_kiem_duyet_thay_the():
    """Bo dac trung ket cuc khong duoc lam mat tin hieu giao hang o T3 —
    no phai duoc thay bang phien ban KIEM DUYET tai moc."""
    from masdss.core.ontology import DecisionPoint
    from masdss.data.featureset import FeatureSet

    assert {"delivery_state", "observed_delay_days",
            "observed_handover_days"} <= set(FeatureSet(DecisionPoint.T3).names)


def test_bang_don_hang_KHONG_loc_theo_trang_thai_giao_hang(fixtures):
    """2.841 don chua bao gio duoc giao co ty le bat man 77,9%.

    Ca hai cai dat tham chieu tren GitHub deu loai chung (`is_delivered == True`),
    va lam vay la vut bo dung nhom can can thiep nhat. Test nay chan viec do quay lai.
    """
    orders, _ = fixtures
    assert (orders["delivery_state"] == 2).sum() > 0, (
        "khong con don 'chua gui' nao — bang co the da bi loc theo order_status")
    chua_toi = orders["delivery_state"] > 0
    assert chua_toi.mean() > 0.05, f"chi {chua_toi.mean():.2%} don chua toi han — nghi bi loc"


def test_delivery_state_don_dieu_theo_muc_bat_man(fixtures):
    """Kiem tra tin hieu dung chieu: cang xa viec giao hang, cang bat man.

    Nguong phat bieu theo LIFT chu khong theo ty le tuyet doi, va do la co chu dich.
    Ban truoc viet `ty_le[2] > 0.70` — con so do dung voi moc cu (`han du kien + 3`,
    nen trang thai 2 nghia la "chua gui ma DA qua han"). Khi moc doi sang `ngay mua
    + 7`, trang thai 2 chi con nghia "chua ban giao 3PL sau 7 ngay" va ty le tut ve
    35,8%. Ty le tuyet doi do vay do NGU NGHIA CUA MOC lan chat luong tin hieu tron
    lai voi nhau.

    Lift tach hai thu do ra: no hoi "nhom nay bat man gap may lan ty le nen", va cau
    tra loi khong doi khi ty le nen troi. Nguong duoi day van do that — ha lift cua
    trang thai 2 xuong 1,5 la test do.
    """
    orders, _ = fixtures
    ty_le = orders.groupby("delivery_state")["is_dissatisfied"].mean()
    nen = orders["is_dissatisfied"].mean()
    assert ty_le[0] < ty_le[1] < ty_le[2], "tin hieu khong con don dieu theo trang thai"
    assert ty_le[2] / nen >= 2.0, (
        f"lift cua nhom 'chua ban giao 3PL' chi {ty_le[2] / nen:.2f} — tin hieu qua yeu")
    assert ty_le[0] / nen <= 0.6, (
        f"lift cua nhom 'da giao dung han' la {ty_le[0] / nen:.2f} — dang le phai thap")


def test_seller_prior_orders_khong_dung_don_tuong_lai(fixtures):
    """L31 — dem luy tien phai CHI tinh don mua truoc do.

    Cach lam thong thuong (tong so don cua nguoi ban tren toan tap) la ro ri thoi
    gian. Dau hieu nhan biet re nhat: voi ban DUNG, don DAU TIEN cua moi nguoi ban
    phai co gia tri 0, va gia tri phai khong giam theo thoi gian trong cung nguoi ban.
    """
    orders, _ = fixtures
    assert orders["seller_prior_orders"].min() == 0, (
        "khong don nao co 0 don truoc do — nghi dang dem tren toan tap")
    # Voi don som nhat theo thoi gian, so don truoc do phai rat nho.
    som_nhat = orders.nsmallest(50, "order_purchase_timestamp")
    assert som_nhat["seller_prior_orders"].median() < 5, (
        "don som nhat lai co nhieu don truoc do — dem khong theo thu tu thoi gian")


# --------------------------------------------------------------------------
# L33 — moc T3 phai nam TRUOC moc T4. Truoc day khong co gi canh dieu nay, va
# hau qua la 97,6% so don co "du bao" chay sau chinh ket cuc no du bao.
# --------------------------------------------------------------------------

def test_moc_T3_nam_truoc_luc_khach_viet_danh_gia(fixtures):
    """Bat bien o muc TONG THE, khong phai muc dac trung.

    Day la cho ma CA L30 LAN L33 lot qua. `FeatureSet(decision_point)` cuong che
    duoc "dac trung nao ton tai tai moc", nhung khong noi gi ve "don nao da toi
    duoc moc". Moc T3 la mot tham so cau hinh, va khong co bat bien nao doi chieu
    no voi `creation_timestamp` — nen khi no truot ra sau T4, moi thu van xanh.

    Test nay doi chieu truc tiep. Neu doi `t3_cutoff_days` ve cach neo cu (han giao
    du kien + 3) thi ty le "con kip" tut tu 76,5% xuong 2,4% va test do.
    """
    orders, _ = fixtures
    con_kip = orders["reachable_at_t3"]

    assert con_kip.mean() > 0.5, (
        f"chi {con_kip.mean():.1%} don co T3 nam truoc T4 — moc quyet dinh dang nam "
        f"SAU ket cuc no du bao, xem L33")

    # Voi chinh nhung don thuoc tong the, quan he phai dung TUNG DONG, khong chi dung
    # trung binh. Mot khang dinh tren ty le tong co the xanh trong khi mot phan don
    # van vi pham.
    trong_tong_the = orders[con_kip]
    assert (trong_tong_the["review_created_at"] > trong_tong_the["t3_cutoff"]).all()


def test_tong_the_du_bao_van_giu_duoc_da_so_don_bat_man(fixtures):
    """Moc muon hon cho tin hieu manh hon nhung bo sot nhieu don hon.

    Doi lay tin hieu bang cach de mat doi tuong can cuu la mot danh doi TE. Nguong
    0,8 chan viec day moc ra xa de lam dep PR-AUC.
    """
    orders, _ = fixtures
    bat_man = orders[orders["is_dissatisfied"]]
    phu = bat_man["reachable_at_t3"].mean()
    assert phu > 0.8, (
        f"moc T3 chi con kip {phu:.1%} so don bat man — dang danh doi doi tuong "
        f"nghien cuu de lay chi so dep")


def test_days_to_deadline_khong_dung_ket_cuc_giao_hang(fixtures):
    """`days_to_deadline` phai tinh tu HAI moc deu biet truoc luc dat hang.

    Neu no vo tinh duoc tinh tu `order_delivered_customer_date` thi no se thieu gia
    tri o dung nhung don chua giao — dau hieu nhan biet re nhat.
    """
    orders, _ = fixtures
    assert orders["days_to_deadline"].notna().all(), (
        "co gia tri thieu — nghi dang tinh tu ngay giao thuc te thay vi han du kien")
    chua_giao = orders[orders["delivery_state"] == 2]
    assert len(chua_giao) > 0 and chua_giao["days_to_deadline"].notna().all()
