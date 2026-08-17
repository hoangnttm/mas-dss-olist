"""WP1 / T1.7 — Bat bien LUOC DO cua cac tep dac trung.

Phuc vu: RQ1, RQ3.

Bon bat bien duoi day thay cho viec ra soat tung dac trung bang mat. Chung khong
kiem tra "dac trung nay co dung khong" — chung kiem tra rang mot vi pham CO CAU
truc khong the ton tai:

    1. t3_* KHONG chua cot T4          — chieu chan L30
    2. khong tep dac trung nao chua cot nhan
    3. t3_* ⊆ t4_* theo order_id       — hai giai doan khong xe ranh gioi
    4. goldset_pool ⊆ t4_test          — bo nhan sinh tu dung ky test

BAT BIEN 1 DA DUOC PHAT BIEU LAI (13/08), va viec do lam no DUNG HON chu khong
yeu di. Ban truoc phat bieu hai chieu — *"t3_* ∩ t4_* = {order_id}"* — bang cach
khong cho `t4_*` lay lai cot T3. Nghe manh hon, nhung no keo theo mot he qua khong
ai chon: giai doan 2 phai NOI hai tep, phep noi la INNER, nen tong the T4 bi keo
ve dung tong the T3 va 1.819 don bat man (12,6%) bien mat khoi tang quy ket —
phan lon la khieu nai KHONG do giao hang.

Tuc mot bat bien ve LUOC DO da am tham quyet dinh mot van de ve TONG THE. Chieu
that su chan ro ri chi la mot: `t3_*` khong duoc chua cot T4.

Ly do chung ton tai: L30 va L33 deu la loi IM LANG lot qua vi rang buoc chi duoc
cuong che o mot muc. Mot bat bien cau truc khong the "quen chay".
"""

from __future__ import annotations

import pandas as pd
import pytest

from masdss.core.ontology import DecisionPoint
from masdss.data.export import (KEY, LABEL_COLUMNS, SPLITS, STAGES, ExportError,
                                load_labels, load_manifest, load_split)
from masdss.data.features import REGISTRY


# --- bat bien 1: t3_* khong chua cot T4 ---

@pytest.mark.parametrize("split", SPLITS)
def test_tep_T3_khong_chua_bat_ky_cot_T4_nao(exported, split):
    """Chieu DUY NHAT chan duoc ro ri, va no mot chieu.

    Kiem tra khong bang mot danh sach viet tay ma bang chinh so dang ky dac trung:
    moi `FeatureSpec` co `available_at == T4` deu phai vang mat khoi tep T3. Nho vay
    them mot dac trung T4 moi ma quen loc se lam test do ngay.
    """
    base, _ = exported
    cot_t4 = {s.name for s in REGISTRY if s.available_at is DecisionPoint.T4}
    lot = cot_t4 & set(load_split("t3", split, base=base).columns)
    assert not lot, f"t3_{split} chua cot cua T4: {sorted(lot)}"


def test_dac_trung_ket_cuc_giao_hang_KHONG_nam_trong_tep_T3(exported):
    """Bon dac trung nay chi xac dinh duoc sau khi hang toi — chung thuoc T4.

    Day dung la nhom da gay ra L30. Neu chung quay lai tep T3, mo hinh du bao se
    doc duoc ket cuc ma no dang phai du bao.

    Trung mot phan voi bai tren, va su trung do la CO CHU DICH: bai tren doc so dang
    ky nen no theo duoc moi thay doi; bai nay ghim TEN NGUYEN VAN nen no van do ke
    ca khi ai do vo tinh doi `available_at` cua chung ve T3.
    """
    base, _ = exported
    ket_cuc = {"delivery_days", "delivery_delay_days", "is_late", "carrier_handover_days"}
    for split in SPLITS:
        co_mat = ket_cuc & set(load_split("t3", split, base=base).columns)
        assert not co_mat, f"t3_{split} chua dac trung ket cuc: {sorted(co_mat)}"


def test_tep_T4_la_bang_lam_viec_DAY_DU_cua_giai_doan_2(exported):
    """Quy ket nguyen nhan can CA dac trung T1..T3 lan T4.

    `DeliverySignal` doc `delivery_delay_days` (T4) VA `category` (T1); Policy Critic
    doc `price` va `freight_value` (T1). Neu `t4_*` chi chua cot T4 thi giai doan 2
    buoc phai noi hai tep, va phep noi INNER se am tham keo tong the T4 ve tong the
    T3 — dung cai bay da xay ra va duoc sua ngay 13/08.
    """
    base, _ = exported
    cols = set(load_split("t4", "test", base=base).columns)
    for ten in ("category", "price", "freight_value", "delivery_delay_days"):
        assert ten in cols, f"t4_test thieu `{ten}` — giai doan 2 se phai noi tep"


# --- bat bien 2: khong tep dac trung nao chua nhan ---

@pytest.mark.parametrize("stage", STAGES)
@pytest.mark.parametrize("split", SPLITS)
def test_tep_dac_trung_khong_chua_cot_nhan(exported, stage, split):
    base, _ = exported
    cols = set(load_split(stage, split, base=base).columns)
    nhan = cols & (set(LABEL_COLUMNS) - {KEY})
    assert not nhan, f"{stage}_{split} chua cot nhan: {sorted(nhan)}"
    assert "rating" not in cols and "is_dissatisfied" not in cols


def test_load_split_tu_chan_ke_ca_khi_tep_bi_sua_tay(exported, tmp_path):
    """Cuong che HAI LAN: luc xuat va luc nap.

    Tep parquet co the bi ghi de bang tay hoac bi sinh boi mot phien ban cu. Kiem
    tra luc nap la lop chan cuoi, va no phai bao loi chu khong im lang di tiep.
    """
    base, _ = exported
    frame = load_split("t3", "train", base=base)
    frame["is_dissatisfied"] = True

    ban_hong = tmp_path / "hong"
    ban_hong.mkdir()
    (ban_hong / "manifest.json").write_text("{}", encoding="utf-8")
    frame.to_parquet(ban_hong / "t3_train.parquet", index=False)

    with pytest.raises(ExportError, match="cot nhan"):
        load_split("t3", "train", base=ban_hong)


# --- bat bien 3: hai giai doan khong xe ranh gioi ---

@pytest.mark.parametrize("split", SPLITS)
def test_tong_the_T3_nam_tron_trong_tong_the_T4(exported, split):
    """Mot don khong bao gio duoc roi vao hai tap khac nhau o hai giai doan.

    Hai tong the khac nhau (T3 loc `reachable_at_t3`, T4 khong) nhung ranh gioi thoi
    gian PHAI la mot. Neu chung lech, mot don co the o `t3_train` va `t4_val`, va moi
    phep so sanh giua hai giai doan mat co so.
    """
    base, _ = exported
    t3 = set(load_split("t3", split, base=base)[KEY])
    t4 = set(load_split("t4", split, base=base)[KEY])
    assert t3 <= t4, f"{len(t3 - t4)} don trong t3_{split} khong co trong t4_{split}"
    assert len(t4) >= len(t3)


def test_tong_the_T4_thuc_su_rong_hon_T3(exported):
    """Neu hai tong the bang nhau thi quyet dinh bat doi xung da khong duoc ap.

    Day la bai kiem tra chan viec AM THAM quay ve ban cu: neu ai do khoi phuc phep
    loc `reachable_at_t3` cho ca hai giai doan, moi bai khac van xanh — chi bai nay do.
    """
    base, manifest = exported
    t3 = len(load_split("t3", "test", base=base))
    t4 = len(load_split("t4", "test", base=base))
    assert t4 > t3, (
        "t4_test khong rong hon t3_test — phep loc `reachable_at_t3` da bi ap nham "
        "cho giai doan 2, va tang quy ket dang mat nhom khieu nai giao-hang-nhanh")
    assert manifest["tong_the"]["ap_cho"].startswith("CHI giai doan 1")


# --- bat bien 4: gold set sinh tu dung ky test ---

def test_ho_gold_set_nam_tron_trong_ky_test(exported):
    """Gan nhan mot don thuoc ky train roi dung no de cham diem la ro ri im lang.

    Ho ung vien lay tu `t4_test` chu khong `t3_test`: neu no bi gioi han o nhom "con
    kip can thiep" thi bo nhan chuan tro thanh mot mau LECH — thieu he thong nhom
    khieu nai giao-hang-nhanh, dung nhom ma quy ket nguyen nhan kho nhat.
    """
    base, manifest = exported
    ho = pd.read_parquet(base / "goldset_pool.parquet")
    t4_test = set(load_split("t4", "test", base=base)[KEY])
    thua = set(ho[KEY]) - t4_test
    assert not thua, f"{len(thua)} don trong ho gold set khong thuoc t4_test"
    assert len(ho) > 0
    assert manifest["goldset_pool"]["nguon"].startswith("t4_test")


def test_ho_gold_set_CHI_gom_don_co_binh_luan(exported):
    """Tang B nam ngoai pham vi de tai — ho ung vien phai khop pham vi do.

    Gan nhan 300 dong roi cham diem mot he thong khong bao gio xu ly mot phan trong
    so chung se lam mau so cua moi chi so quy ket bi sai.
    """
    base, manifest = exported
    ho = pd.read_parquet(base / "goldset_pool.parquet")
    trong = ho["review_content"].isna() | (ho["review_content"].astype(str).str.strip() == "")
    assert not trong.any(), f"{int(trong.sum())} don trong ho gold set khong co binh luan"
    assert manifest["goldset_pool"]["tang_b_bi_loai"] > 0, (
        "khong don tang B nao bi loai — phep loc co the da khong chay")


@pytest.mark.parametrize("stage", STAGES)
def test_ba_tap_khong_chung_mot_don_nao(exported, stage):
    base, _ = exported
    tap = {s: set(load_split(stage, s, base=base)[KEY]) for s in SPLITS}
    assert not tap["train"] & tap["val"]
    assert not tap["val"] & tap["test"]
    assert not tap["train"] & tap["test"]


# --- ranh gioi thoi gian va khoang cach ly ---

def test_khoang_cach_ly_chan_nhan_den_sau_khi_ky_test_bat_dau(exported):
    """Bat bien nay re, nen no duoc cai san thay vi doi den luc no dat.

    O bo du lieu hien tai chi 1 dong train vi pham. Nhung neu du lieu duoc cap nhat
    hoac ty le chia doi, con so do co the tang ma khong ai nhan ra.
    """
    base, manifest = exported
    test_start = pd.Timestamp(manifest["khoang_cach_ly"]["moc_cach_ly"])
    for split in ("train", "val"):
        y = load_labels(split, base=base)
        muon = y["review_created_at"] >= test_start
        assert not muon.any(), (
            f"{int(muon.sum())} dong {split} co nhan den sau khi ky test bat dau")


def test_manifest_ghi_du_thu_can_de_tai_lap(exported):
    base, manifest = exported
    assert manifest == load_manifest(base=base)
    for khoa in ("moc_quyet_dinh", "tong_the", "khoang_cach_ly", "tep", "cot", "tap"):
        assert khoa in manifest, f"manifest thieu `{khoa}`"
    assert manifest["moc_quyet_dinh"]["t3_cutoff_days"] == 7
    for ten, t in manifest["tep"].items():
        assert len(t["sha256"]) == 64, f"{ten} thieu sha256"
    # Ty le nen tung tap phai co mat — no la bang chung cua drift, khong phai chi tiet.
    for split in SPLITS:
        assert 0 < manifest["tap"][split]["ty_le_bat_man"] < 1
        assert manifest["tap"][split]["so_don_t4"] >= manifest["tap"][split]["so_don_t3"]


def test_tong_the_T3_chi_gom_don_con_kip_can_thiep(exported):
    """Ve THU HAI cua rang buoc moc quyet dinh — ve ma L30 va L33 deu bo ngo.

    Kiem tren TEP T3 chu khong tren tep nhan: tep nhan nay phu tong the day du vi no
    phuc vu ca hai giai doan, nen `reachable_at_t3` la mot COT trong do chu khong con
    la mot dieu kien da duoc ap.
    """
    base, manifest = exported
    for split in SPLITS:
        y = load_labels(split, base=base).set_index(KEY)
        t3_ids = load_split("t3", split, base=base)[KEY]
        assert y.loc[t3_ids, "reachable_at_t3"].all(), (
            f"t3_{split} chua don da co danh gia truoc moc T3")
        assert (y.loc[t3_ids, "review_created_at"] > y.loc[t3_ids, "t3_cutoff"]).all()
    assert manifest["tong_the"]["con_kip_can_thiep_tai_t3"] < \
        manifest["tong_the"]["tat_ca_don_co_danh_gia"]


def test_anh_chup_ma_tran_thiet_ke_khong_chua_cot_moc_muon():
    """Chan ro ri bang mot phep kiem MO TEP RA DEM COT, khong bang lap luan.

    Ba co che duoc neu ra de bao dam dac trung moc muon khong lot vao mo hinh T3 —
    `available_at`, tach tep vat ly, ghim `_columns` luc `fit` — deu la lap luan ve
    CO CHE. Va hai trong ba im lang khi bi vi pham: `LeakageError` khong kich hoat
    duoc qua duong di binh thuong, con `select()` loai bo cot la ma khong bao.

    Bai kiem thu nay lam viec tren chinh ma tran da di vao `LGBMClassifier.fit()`.
    """
    import pandas as pd

    from masdss.capabilities.risk_model import RiskModel
    from masdss.core.ontology import DecisionPoint
    from masdss.data.features import REGISTRY, spec_of
    from masdss.data.featureset import FeatureSet

    hop_le = {DecisionPoint.T1, DecisionPoint.T2, DecisionPoint.T3}
    khung = pd.DataFrame({
        **{s.name: ([0.0] * 4 if s.kind != "categorical" else ["x"] * 4)
           for s in REGISTRY},
        "order_id": [f"o{i}" for i in range(4)],
        "is_dissatisfied": [0, 1, 0, 1],
    })

    model = RiskModel(feature_set=FeatureSet(DecisionPoint.T3))
    # Ghim thu tu cot dung cach `fit` lam, khong goi ca LightGBM cho nhanh.
    model._design_matrix(khung, fit=True)
    ma_tran = model.design_matrix(khung)

    assert ma_tran.index.name == "order_id", "khoa phai la CHI MUC, khong phai mot cot"
    assert "order_id" not in ma_tran.columns

    muon = [c for c in ma_tran.columns if spec_of(c).available_at not in hop_le]
    assert not muon, (
        f"anh chup ma tran thiet ke T3 chua cot cua moc muon hon: {muon} — "
        "mo hinh dang nhin thay thong tin chua ton tai luc ra quyet dinh")
