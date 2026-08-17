"""WP2 / T2.10 — Canh ba dieu kien lay mau cua vong gan nhan cuoi.

Ca ba deu KHONG SUA DUOC sau khi da gan xong, nen chung phai duoc canh bang test
chu khong bang tri nho.
"""

from __future__ import annotations

import pandas as pd
import pytest

FILE = "data/v3/goldset/goldset_v2_A.csv"


@pytest.fixture(scope="module")
def sheet():
    """Phieu gan nhan SINH LAI TU MA NGUON, khong doc tep da ghi.

    Ban dau fixture nay doc `goldset_v2_A.csv`. Hau qua: sua ma nguon — bo phan
    tang, doi ky lay mau — khong lam test nao do, vi tep tren dia van con nguyen.
    Do la phep thu RONG, dung kieu loi T04.

    Kiem chung bang mutation: ha `ALLOCATION` ve {100,100,100} phai lam
    `test_trong_so_khoi_phuc_dung_ty_le_tong_the` DO.
    """
    from masdss.cli.build_goldset_v2 import candidate_pool, draw, to_sheet

    return to_sheet(draw(candidate_pool(), _bo_nhan_cu(), seed=20260811))


@pytest.fixture(scope="module")
def ho_ung_vien():
    """Ho ma TRONG SO duoc tinh tren. Phai dung DINH NGHIA voi `draw()`.

    Test kiem trong so tung so sanh voi mot ho khac (`test[is_dissatisfied]`), va
    phep so sanh do that bai vi ly do sai: khong phai trong so tinh sai, ma hai ben
    dang dem tren hai tap khac nhau. Mot phep thu so hai dai luong khong cung dinh
    nghia thi khong noi len dieu gi.
    """
    from masdss.cli.build_goldset_v2 import candidate_pool

    ho = candidate_pool()
    cu = _bo_nhan_cu()
    return ho[
        ho["review_content"].notna()
        & (ho["review_content"].astype(str).str.strip() != "")
        & ~ho["order_id"].isin(cu)
    ]


def _bo_nhan_cu() -> set:
    """Bo nhan cua VONG TRUOC — tap ma phep lay mau phai tranh.

    TRO TOI TEP CUA VONG 3, KHONG TRO TOI `gold_labels.csv`. Ban dau no doc
    `gold_labels.csv` va dieu do dung — luc ay tep do giu bo nhan cu 250 dong.

    Sau khi vong cuoi duoc chot (14/08), `gold_labels.csv` giu chinh 300 dong DO
    PHEP LAY MAU NAY SINH RA, nen tham chieu tro thanh TU THAM CHIEU: fixture loai
    tru dung nhung dong no vua rut, tang `delivery_state == 0` (chi co 45 don, va
    ca 45 deu da duoc rut) cong lai bang rong, va tam bai do voi
    `SystemExit: tang 0 chi co 0 don`.

    Do khong phai loi cua phep lay mau — no la tham chieu tro nham sau khi trang
    thai du an tien len mot buoc.
    """
    from pathlib import Path

    for ten in ("gold_annotation_A_en.csv", "gold_annotator_A.csv"):
        cu = Path("data/v3/goldset") / ten
        if cu.exists():
            return set(pd.read_csv(cu, encoding="utf-8-sig")["order_id"])
    return set()


def test_moi_dong_deu_nam_trong_ky_test(sheet):
    """Dieu kien 1. Bo nhan cu co 199/250 dong trong ky train, nen mo hinh rui ro
    la TRONG MAU voi chung va danh gia chuoi dau-cuoi khong hop le.

    Doi chieu voi TEP `t3_test.parquet` chu khong dung lai `time_split()`. Dung lai
    phep chia chi kiem tra "hai lan goi cung ham cho cung ket qua" — mot dieu luon
    dung. Doi chieu voi tep kiem dung thu can kiem: mau co nam trong tap ma mo hinh
    KHONG duoc huan luyen tren hay khong.
    """
    from masdss.data.export import load_split

    trong_test = set(load_split("t3", "test")["order_id"])
    ngoai = set(sheet["order_id"]) - trong_test
    assert not ngoai, f"{len(ngoai)} dong nam ngoai ky test"


def test_khong_trung_voi_bo_nhan_cu(sheet):
    """Bo nhan cuoi phai la tap kiem thu DOC LAP — khong dong nao tung tham gia
    qua trinh phat trien."""
    cu = _bo_nhan_cu()
    if not cu:
        pytest.skip("khong co bo nhan cu de doi chieu")
    trung = set(sheet["order_id"]) & cu
    assert not trung, f"{len(trung)} don trung voi bo nhan cu"


def test_moi_tang_du_n_de_uoc_luong_rieng(sheet):
    """Dieu kien 2 — rang buoc THAT cua phan tang, khong phai con so tuy y.

    Khang dinh `dem == ALLOCATION` la tautology: no so hang so voi chinh no. Rang
    buoc that la moi tang phai du n de uoc luong RIENG duoc, va 43 la con so tinh
    ra tu yeu cau KTC precision ±0,15 (1,96² × 0,25 / 0,15²).
    """
    dem = sheet.groupby("stratum").size()
    assert set(dem.index) == {0, 1, 2}, f"thieu tang: {sorted(dem.index)}"
    thieu = dem[dem < 43]
    assert thieu.empty, f"tang khong du 43 dong nen khong uoc luong rieng duoc: {dict(thieu)}"


def test_trong_so_co_mat_va_nhat_quan_trong_tung_tang(sheet):
    """Dieu kien 3. Thieu trong so thi moi chi so o muc tong the bi thoi phong."""
    assert "weight" in sheet.columns
    assert (sheet["weight"] > 0).all()
    assert (sheet.groupby("stratum")["weight"].nunique() == 1).all()


def test_hieu_qua_thiet_ke_khong_qua_thap(sheet):
    """Phan tang qua lech lam PHUONG SAI cua uoc luong tong the tang vot.

    Trong so sua duoc THIEN LECH nhung khong sua duoc PHUONG SAI: mot mau 100/100/100
    van cho uoc luong dung, nhung KTC rong hon nhieu. Do bang co mau hieu dung
    n_eff = (sum w)^2 / sum(w^2). Nguong 0,70 loai duoc phan bo deu (0,60) trong khi
    van chap nhan phan bo hien tai (0,79).
    """
    w = sheet["weight"].to_numpy()
    n_eff = w.sum() ** 2 / (w ** 2).sum()
    ty_le = n_eff / len(sheet)
    assert ty_le >= 0.70, (
        f"co mau hieu dung chi {n_eff:.0f}/{len(sheet)} ({ty_le:.2f}) — phan tang qua lech")


def test_trong_so_khoi_phuc_dung_ty_le_tong_the(sheet, ho_ung_vien):
    """Nhan trong so phai tra ve dung ty le nen cua tong the, sai so duoi 2 diem %."""
    that = ho_ung_vien.groupby("delivery_state").size() / len(ho_ung_vien)

    uoc = sheet.groupby("stratum")["weight"].sum()
    uoc = uoc / uoc.sum()
    for state in (0, 1, 2):
        assert abs(uoc[state] - that[state]) < 0.02, (
            f"tang {state}: uoc {uoc[state]:.3f} vs that {that[state]:.3f}")


def test_khong_dien_san_nhan_hay_ghi_chu(sheet):
    """L26 — hai nguoi gan phai DOC LAP. Dien san bat cu gi la pha tinh doc lap."""
    for column in ("cause_delivery", "cause_quality", "cause_service",
                   "cause_unknown", "notes", "confidence"):
        assert sheet[column].isna().all() or (sheet[column].astype(str).str.strip() == "").all(), (
            f"cot `{column}` da co du lieu — pha tinh doc lap")


def test_don_khong_bao_gio_giao_duoc_noi_ro_bang_chu(sheet):
    """77/300 don khong bao gio duoc giao nen `delivery_delay_days` la o TRONG.

    Mot o trong de bi hieu la loi du lieu, va nguoi gan se bo qua dung nhung don
    nang nhat. Cot `ket_cuc_cuoi_cung` phai noi thang.
    """
    khong_giao = sheet["delivery_delay_days"].isna()
    assert khong_giao.sum() > 0, "khong con don nao chua giao — nghi mau bi loc"
    assert (sheet.loc[khong_giao, "ket_cuc_cuoi_cung"]
            == "KHONG BAO GIO DUOC GIAO").all()
    assert sheet["ket_cuc_cuoi_cung"].notna().all()


def test_hai_tep_da_ghi_giong_het_nhau():
    """Hai nguoi gan phai nhin CUNG mot du lieu — khac biet duy nhat duoc phep la
    phan doan cua ho. Test nay doi chieu HAI TEP DA GHI (khac cac test tren)."""
    from pathlib import Path
    if not Path(FILE).exists():
        pytest.skip("chua sinh goldset_v2")
    a = pd.read_csv(FILE, encoding="utf-8-sig")
    b = pd.read_csv("data/v3/goldset/goldset_v2_B.csv", encoding="utf-8-sig")
    pd.testing.assert_frame_equal(a, b)


def test_lay_mau_tat_dinh():
    """Chay lai cung seed phai cho cung tap don."""
    from masdss.cli.build_goldset_v2 import draw
    from masdss.data.load import build_order_table

    orders = build_order_table()
    a = draw(orders, set(), seed=123)
    b = draw(orders, set(), seed=123)
    assert list(a["order_id"]) == list(b["order_id"])
