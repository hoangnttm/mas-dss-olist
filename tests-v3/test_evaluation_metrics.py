"""WP10 — Kiem thu ba module do luong khong can gold set.

Cac module nay SINH RA CON SO CHO CHUONG 5, nen mot bug o day khong lam chuong
trinh do — no lam luan van sai. Do la ly do chung can kiem thu rieng, va la ly do
moi test o day co mot dong ghi ro no chan dieu gi.
"""

from __future__ import annotations

import ast
import json
import math
from pathlib import Path

import numpy as np
import pytest

from masdss.evaluation import coordination, cost, forecasting


# --------------------------------------------------------------------------
# T10.4 — bid_entropy
# --------------------------------------------------------------------------

def test_bid_entropy_bang_khong_khi_mot_analyst_ap_dao():
    """Mot bid duy nhat khong phai la "da nguyen nhan" — entropy phai la 0."""
    assert coordination.bid_entropy([0.9]) == 0.0
    assert coordination.bid_entropy([]) == 0.0


def test_bid_entropy_bang_mot_khi_cac_analyst_tu_tin_ngang_nhau():
    """Chuan hoa theo log(k): tu tin deu nhau phai cho dung 1,0 voi MOI k.

    Neu bo chuan hoa thi k=4 cho 1,386 con k=2 cho 0,693, va hai case khong con
    so sanh duoc voi nhau — dung cai lam chi so nay vo dung.
    """
    for k in (2, 3, 4):
        assert coordination.bid_entropy([0.5] * k) == pytest.approx(1.0)


def test_bid_entropy_giam_khi_phan_bo_lech():
    lech = coordination.bid_entropy([0.9, 0.1])
    deu = coordination.bid_entropy([0.5, 0.5])
    assert 0.0 < lech < deu


def test_bid_entropy_bo_qua_bid_khong_duong():
    """Do tin cay 0 khong phai mot y kien — no khong duoc lam loang entropy."""
    assert coordination.bid_entropy([0.5, 0.5, 0.0]) == pytest.approx(1.0)


# --------------------------------------------------------------------------
# T10.1 — tuong duong va dieu kien kiem soat
# --------------------------------------------------------------------------

def test_dieu_kien_kiem_soat_phat_hien_hai_mo_hinh_khac_nhau():
    """Chi so quan trong nhat cua T10.1: neu hai kien truc KHONG dung chung mot
    mo hinh, ham nay phai keu len. Moi so sanh khac trong Chuong 5 phu thuoc vao
    khang dinh nay.
    """
    giong = forecasting.verify_shared_capability(
        np.array([0.1, 0.5, 0.9]), np.array([0.1, 0.5, 0.9]))
    assert giong.identical and giong.equivalent

    lech = forecasting.verify_shared_capability(
        np.array([0.1, 0.5, 0.9]), np.array([0.1, 0.5, 0.8]))
    assert not lech.identical and not lech.equivalent
    assert "CANH BAO" in lech.note


def test_dieu_kien_kiem_soat_khong_bi_qua_mat_boi_lam_tron():
    """Loi that da xay ra: doc diem du bao tu chuoi da lam tron 4 chu so lam ham
    nay bao lech +0,000014 tren hai day so von giong het nhau. Nguong 1e-12 phai
    du chat de KHONG coi sai so lam tron la "giong nhau".
    """
    goc = np.array([0.123456789, 0.987654321])
    tron = np.round(goc, 4)
    assert not forecasting.verify_shared_capability(goc, tron).identical


def test_tost_khong_ket_luan_tuong_duong_khi_chenh_lech_vuot_bien():
    a = np.linspace(0.0, 1.0, 50)
    ket_qua = forecasting.tost_equivalence(a, a - 0.05, margin=0.01)
    assert not ket_qua.equivalent


def test_tost_ket_luan_tuong_duong_khi_chenh_lech_nho_hon_bien():
    rng = np.random.default_rng(0)
    a = rng.normal(0.5, 0.1, 200)
    ket_qua = forecasting.tost_equivalence(a, a - 0.001, margin=0.01)
    assert ket_qua.equivalent and not ket_qua.identical


def test_tost_danh_dau_tautology_khi_hai_day_giong_het():
    """Khong duoc tra ve "tuong duong" tron nhu mot ket qua thuc nghiem."""
    a = np.linspace(0.0, 1.0, 20)
    ket_qua = forecasting.tost_equivalence(a, a.copy())
    assert ket_qua.equivalent and ket_qua.identical
    assert "tautology" in ket_qua.note


def test_tost_tu_choi_co_mau_qua_nho():
    with pytest.raises(ValueError):
        forecasting.tost_equivalence(np.array([0.5]), np.array([0.4]))


# --------------------------------------------------------------------------
# T10.1 — nguong theo chi phi
# --------------------------------------------------------------------------

def test_nguong_theo_chi_phi_thap_hon_khi_bo_sot_dat_hon():
    """Bo sot dat gap 5 lan canh bao thua ⟹ nguong phai HA XUONG duoi 0,5.

    Day chinh la ly do khong duoc dung mac dinh 0,5: no ngam gia dinh hai loai
    sai co gia bang nhau, dieu khong dung trong bai toan nay.
    """
    rng = np.random.default_rng(0)
    y = rng.binomial(1, 0.15, 2000)
    score = np.clip(rng.normal(0.3 + 0.35 * y, 0.15), 0.0, 1.0)

    nguong_lech, _ = forecasting.cost_optimal_threshold(
        y, score, cost_false_negative=5.0, cost_false_positive=1.0)
    nguong_can, _ = forecasting.cost_optimal_threshold(
        y, score, cost_false_negative=1.0, cost_false_positive=1.0)
    assert nguong_lech < nguong_can


def test_nguong_theo_chi_phi_tra_ve_chi_phi_toi_thieu_that():
    """Chi phi tra ve phai la nho nhat trong cac ung vien, khong phai mot gia tri
    bat ky tren duong quet."""
    rng = np.random.default_rng(1)
    y = rng.binomial(1, 0.2, 500)
    score = np.clip(rng.normal(0.3 + 0.3 * y, 0.2), 0.0, 1.0)
    nguong, chi_phi = forecasting.cost_optimal_threshold(y, score)

    for ung_vien in np.unique(np.round(score, 3)):
        du_doan = score >= ung_vien
        khac = (5.0 * int(((~du_doan) & (y == 1)).sum())
                + 1.0 * int((du_doan & (y == 0)).sum()))
        assert khac >= chi_phi - 1e-9
    assert 0.0 <= nguong <= 1.0


# --------------------------------------------------------------------------
# T10.1 — khoang tin cay
# --------------------------------------------------------------------------

def test_khoang_tin_cay_bootstrap_bao_lay_gia_tri_diem_va_tat_dinh():
    from sklearn.metrics import roc_auc_score

    rng = np.random.default_rng(2)
    y = rng.binomial(1, 0.3, 400)
    score = np.clip(rng.normal(0.4 + 0.2 * y, 0.2), 0.0, 1.0)

    lan_1 = forecasting.bootstrap_ci(roc_auc_score, y, score, name="roc",
                                     n_boot=200, seed=7)
    lan_2 = forecasting.bootstrap_ci(roc_auc_score, y, score, name="roc",
                                     n_boot=200, seed=7)
    assert lan_1 == lan_2                       # cung seed ⟹ cung ket qua
    assert lan_1.lower <= lan_1.value <= lan_1.upper
    assert lan_1.lower < lan_1.upper            # khoang khong duoc sup thanh diem


def test_evaluate_bao_cao_ca_nen_va_lift():
    """PR-AUC tran khong doc duoc neu khong biet ty le duong lam nen."""
    rng = np.random.default_rng(3)
    y = rng.binomial(1, 0.15, 600)
    score = np.clip(rng.normal(0.35 + 0.3 * y, 0.2), 0.0, 1.0)
    bang = forecasting.evaluate(y, score, n_boot=100)

    chi_so = set(bang["metric"])
    assert {"PR-AUC (chinh)", "ROC-AUC (phu)", "ty le duong (nen)",
            "lift PR-AUC / nen"} <= chi_so
    nen = float(bang.loc[bang["metric"] == "ty le duong (nen)", "value"].iloc[0])
    assert nen == pytest.approx(float(y.mean()), abs=1e-4)


# --------------------------------------------------------------------------
# T10.6 — dem dong ma
# --------------------------------------------------------------------------

def test_dem_dong_ma_loai_docstring_va_comment(tmp_path: Path):
    """Du an nay comment rat day. Neu dem dong tho, "cai gia cua kha nang chiu
    loi" bi thoi phong len nhieu lan va con so trong Chuong 5 thanh vo nghia.
    """
    nguon = tmp_path / "mau.py"
    nguon.write_text(
        '"""Docstring module\ntrai ba dong\nnhu the nay."""\n'
        "\n"
        "# mot comment\n"
        "def f():\n"
        '    """Docstring ham."""\n'
        "    return 1\n",
        encoding="utf-8",
    )
    ma, tong = cost._count_code_lines(nguon)
    assert ma == 2                  # `def f():` va `return 1`
    assert tong == 8
    assert ma < tong


def test_dem_dong_ma_khong_bao_gio_am(tmp_path: Path):
    """File chi co docstring: phep tru co the ra so am neu khong chan."""
    nguon = tmp_path / "chi_docstring.py"
    nguon.write_text('"""Chi\nco\ndocstring\nma thoi."""\n', encoding="utf-8")
    ma, _ = cost._count_code_lines(nguon)
    assert ma == 0


def test_danh_sach_module_chi_phi_deu_ton_tai():
    """Mot module bi doi ten se lam bang chi phi ngam bo qua no, va tong so dong
    tut xuong ma khong bao loi. Test nay bien loi im lang do thanh loi on ao.
    """
    goc = Path(cost.__file__).resolve().parents[1]
    thieu = [m for m in cost.RELIABILITY_MODULES + cost.COORDINATION_MODULES
             if not (goc / m).exists()]
    assert not thieu, f"module da doi ten hoac bi xoa: {thieu}"


def test_bang_chi_phi_ma_nguon_dem_du_module():
    goc = Path(cost.__file__).resolve().parents[1]
    bang = cost.source_cost(goc)
    theo_tang = dict(zip(bang["tang"], bang["so_module"]))
    assert theo_tang["chiu loi"] == len(cost.RELIABILITY_MODULES)
    assert theo_tang["phoi hop"] == len(cost.COORDINATION_MODULES)
    assert (bang["dong_ma"] > 0).all()
    assert (bang["dong_ma"] <= bang["tong_dong"]).all()


def test_moi_module_evaluation_deu_phan_tich_duoc():
    """Chan loi cu phap trong chinh cac module sinh so cho Chuong 5."""
    goc = Path(cost.__file__).resolve().parent
    for path in goc.glob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"))


def _dung_run_gia(thu_muc: Path, *, mas_ms: float, mono_ms: float,
                  span_ms: list[float]) -> Path:
    """Mot thu muc run toi thieu du cho `cost.latency()` doc."""
    import sqlite3

    thu_muc.mkdir(parents=True, exist_ok=True)
    (thu_muc / "decisions.jsonl").write_text(
        "\n".join('{"case_id": "x"}' for _ in range(2)) + "\n", encoding="utf-8")
    (thu_muc / "reliability_report.json").write_text(
        json.dumps({"mas_ms_per_case": mas_ms, "mono_ms_per_case": mono_ms}),
        encoding="utf-8")
    conn = sqlite3.connect(thu_muc / "spans.sqlite")
    conn.execute("CREATE TABLE spans (name TEXT, duration_ms REAL)")
    conn.executemany("INSERT INTO spans VALUES (?, ?)",
                     [("buoc", v) for v in span_ms])
    conn.commit()
    conn.close()
    return thu_muc


def test_hai_ve_do_tre_phai_CUNG_MOT_CO_SO_do(tmp_path: Path):
    """L46 — bat bien: cot `ms_moi_case` cua CA HAI kien truc phai lay tu
    wall-clock trong `reliability_report.json`, KHONG lay tu tong span.

    Ban truoc lay `sum(span.duration_ms)` cho MAS va wall-clock cho baseline. Hai
    ve khong cung co so, va ca hai sai lech deu co loi cho MAS: span bo qua glue
    dieu phoi va phan ghi nhat ky. Test nay dung so lieu co `sum(span)` LECH HAN
    wall-clock, nen no do neu ai do noi lai duong cu.
    """
    run = _dung_run_gia(tmp_path / "run", mas_ms=100.0, mono_ms=8.0,
                        span_ms=[1.0, 2.0, 3.0])      # sum(span)/2 case = 3.0 ms
    bang = cost.latency(run)
    theo_kien_truc = dict(zip(bang["kien_truc"], bang["ms_moi_case"]))

    assert theo_kien_truc["MAS-DSS"] == 100.0, "MAS phai lay wall-clock"
    assert theo_kien_truc["Monolithic-Complete"] == 8.0

    # Tong span van duoc bao cao, nhung o COT RIENG va o vai tro chan duoi.
    chan_duoi = float(bang.loc[bang["kien_truc"] == "MAS-DSS",
                               "sum_span_ms_moi_case"].iloc[0])
    assert chan_duoi == 3.0
    assert chan_duoi < theo_kien_truc["MAS-DSS"]


def test_run_system_do_wall_clock_cho_ca_hai_kien_truc():
    """Chan viec go mat mot trong hai dong ho: neu chi con mot ve duoc do bang
    wall-clock thi Bang 5.24 quay ve tinh trang so hai dai luong khac co so.
    """
    nguon = (Path(cost.__file__).resolve().parents[1]
             / "cli" / "run_system.py").read_text(encoding="utf-8")
    for khoa in ("mas_ms_per_case", "mono_ms_per_case",
                 "mas_seconds", "mono_seconds"):
        assert khoa in nguon, f"thieu phep do `{khoa}` trong run_system"


# --------------------------------------------------------------------------
# T10.3 — duong cong risk-coverage
# --------------------------------------------------------------------------

def _gold_va_du_doan_xep_nguoc():
    """Dung mot vi du ma DO TIN CAY va THU TU DONG di NGUOC nhau.

    Bon don, gold noi ca bon deu la `delivery`. He thong quy ket dung ba don va sai
    mot don — nhung don SAI lai la don DAU TIEN theo thu tu `order_id`, va la don he
    thong KEM tu tin nhat.

    Mot duong risk-coverage dung phai bo don sai ra TRUOC khi cat xuong muc phu thap,
    nen F1 o muc phu 0,5 phai CAO HON o muc phu 1,0. Neu phep cat di theo thu tu dong,
    no giu lai dung don sai va F1 se KHONG tang.
    """
    import pandas as pd

    from masdss.data.labels import GoldLabels, Provenance

    gold = GoldLabels(
        frame=pd.DataFrame({
            "order_id": ["a", "b", "c", "d"],
            "tier": ["A"] * 4,
            "cause_delivery": [1, 1, 1, 1],
            "cause_quality": [0, 0, 0, 0],
            "cause_service": [0, 0, 0, 0],
        }),
        provenance=Provenance.HUMAN_INDEPENDENT,
    )
    du_doan = pd.DataFrame({
        "order_id": ["a", "b", "c", "d"],
        "cause_delivery": [0, 1, 1, 1],   # 'a' bi quy ket sai nhan
        "cause_quality": [1, 0, 0, 0],
        "cause_service": [0, 0, 0, 0],
        "confidence": [0.10, 0.90, 0.85, 0.80],   # 'a' kem tu tin nhat
    })
    return gold, {"he": du_doan}


def test_duong_risk_coverage_cat_theo_do_tin_cay_chu_khong_theo_thu_tu_dong():
    """Chan dung loi ma ban truoc mac: cat muc phu bang vi tri dong trong DataFrame.

    Khung da `sort_index()` theo `order_id`, nen cat theo vi tri la cat NGAU NHIEN CO
    HE THONG. Khi do chi so nay khong con do dieu no tuyen bo do — va no chinh la chi
    so RQ3 dat ra de DP3 khong tu tru diem chinh no.
    """
    from masdss.evaluation import selective

    gold, du_doan = _gold_va_du_doan_xep_nguoc()
    curve, _ = selective.report(gold, du_doan)

    thap = curve[curve["muc_phu_muc_tieu"] == 0.4]["macro_f1"].iloc[0]
    day_du = curve[curve["muc_phu_muc_tieu"] == 1.0]["macro_f1"].iloc[0]
    assert thap > day_du, (
        "Cat muc phu phai bo don KEM TU TIN NHAT truoc. F1 o muc phu thap khong cao "
        "hon o muc phu day du nghia la phep cat khong nhin vao do tin cay."
    )


def test_duong_risk_coverage_bao_loi_khi_thieu_cot_do_tin_cay():
    """Thieu do tin cay thi phai DUNG, khong duoc lang le quay ve cat theo thu tu dong.

    Day la khac biet giua mot bug bi bat va mot bug song sot: ban truoc khong co cot
    nay va cung khong keu len, nen tep `selective_curve.csv` van duoc sinh ra va van
    duoc doc nhu mot duong risk-coverage.
    """
    import pytest as _pytest

    from masdss.evaluation import selective

    gold, du_doan = _gold_va_du_doan_xep_nguoc()
    thieu = {"he": du_doan["he"].drop(columns=["confidence"])}
    with _pytest.raises(ValueError, match="do tin cay"):
        selective.report(gold, thieu)


# --------------------------------------------------------------------------
# T10.4 — do sau cay hoi thoai
# --------------------------------------------------------------------------

def test_do_sau_cay_hoi_thoai_theo_in_reply_to():
    """Do sau phai dung tu quan he cha con, khong phai dem so message."""
    from uuid import uuid4

    from masdss.core.message import Performative, new_request

    goc = new_request(conversation_id=uuid4(), sender="orchestrator", receiver="a",
                      ontology="cfp", content={})
    tra_loi = goc.reply(sender="a", performative=Performative.PROPOSE,
                        ontology="declaration", content={})
    tra_loi_2 = tra_loi.reply(sender="orchestrator",
                              performative=Performative.ACCEPT_PROPOSAL,
                              ontology="award", content={})
    assert coordination._depth([goc]) == 0
    assert coordination._depth([goc, tra_loi]) == 1
    assert coordination._depth([goc, tra_loi, tra_loi_2]) == 2
