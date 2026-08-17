"""WP7 / T7.3b — Hieu chuan do tin cay tung analyst.

Chi so nay RQ3 §2.2 yeu cau dich danh, doc lap voi ket cuc cua H2.
"""

from __future__ import annotations

import numpy as np
import pytest

from masdss.capabilities.calibration import (BidCalibrator,
                                             MIN_POSITIVES_FOR_CALIBRATION,
                                             expected_calibration_error)
from masdss.core.ontology import Cause


def _lech_he_thong(n=400, seed=0):
    """Diem tu tin qua muc: xac suat that chi bang mot nua diem bao ra."""
    rng = np.random.default_rng(seed)
    score = rng.uniform(0.05, 0.95, n)
    truth = rng.binomial(1, score / 2)
    return score, truth


def test_ece_bang_khong_khi_da_hieu_chuan_hoan_hao():
    y_prob = np.repeat([0.2, 0.8], 500)
    y_true = np.concatenate([np.repeat([1, 0], [100, 400]), np.repeat([1, 0], [400, 100])])
    assert expected_calibration_error(y_true, y_prob) == pytest.approx(0.0, abs=0.02)


def test_ece_bat_duoc_tu_tin_qua_muc():
    score, truth = _lech_he_thong()
    assert expected_calibration_error(truth, score) > 0.15


def test_hieu_chuan_giam_ece_va_do_NGOAI_MAU():
    """Loi L04: hieu chuan roi do tren chinh du lieu do cho ECE gan 0 gia tao.

    `fit_out_of_fold` phai bao cao con so NGOAI MAU. Test nay khang dinh no giam
    that — va giam mot muc hop ly, khong phai giam ve 0.
    """
    score, truth = _lech_he_thong()
    reports = BidCalibrator(seed=0).fit_out_of_fold(
        {Cause.DELIVERY: score}, {Cause.DELIVERY: truth})
    report = reports[0]
    assert report.calibrated and not report.in_sample
    assert report.ece_after < report.ece_before
    assert report.brier_after <= report.brier_before

    # Nguong 0,01 KHONG phai so tuy tien — no do duoc tren chinh fixture nay:
    #     ECE tho        0,2751
    #     ECE trong mau  0,00004   <- isotonic khop lai chinh du lieu no da hoc
    #     ECE ngoai mau  0,0457
    # Khang dinh dau tien toi viet la `> 0.0`, va no XANH ca khi thay K-fold bang
    # khop trong mau — vi 0,00004 van lon hon 0. Do dung la kieu test rong ma T04
    # mo ta. Nguong nay nam giua hai che do nen no phan biet duoc chung.
    assert report.ece_after > 0.01, (
        "ECE ngoai mau qua nho — dau hieu dang do TRONG MAU (loi L04)")


def test_tu_choi_hieu_chuan_khi_qua_it_duong_VA_neu_ly_do():
    """Duoi nguong, isotonic chi hoc thuoc nhieu. Tu choi phai CO LY DO ghi ra."""
    rng = np.random.default_rng(1)
    score = rng.uniform(0, 1, 300)
    truth = np.zeros(300, dtype=int)
    truth[:MIN_POSITIVES_FOR_CALIBRATION - 1] = 1

    report = BidCalibrator(seed=0).fit_out_of_fold(
        {Cause.SERVICE: score}, {Cause.SERVICE: truth})[0]
    assert not report.calibrated
    assert str(MIN_POSITIVES_FOR_CALIBRATION) in report.reason
    assert report.ece_after == report.ece_before      # giu nguyen diem tho


def test_khong_hieu_chuan_thi_transform_tra_ve_nguyen_diem():
    calibrator = BidCalibrator(seed=0)
    assert calibrator.transform(Cause.SERVICE, 0.42) == pytest.approx(0.42)


def test_hieu_chuan_don_dieu_nen_KHONG_doi_thu_tu():
    """Ket qua nay la ly do T7.3b KHONG pha duoc dang thuc L27.

    Isotonic don dieu khong giam ⟹ dat nguong tren diem da hieu chuan tuong duong
    dat MOT nguong khac tren diem tho. Hai kien truc dung chung head va chung nguong
    vi vay van cho ket qua giong het nhau sau khi hieu chuan.
    """
    score, truth = _lech_he_thong()
    calibrator = BidCalibrator(seed=0).fit({Cause.DELIVERY: score},
                                           {Cause.DELIVERY: truth})
    calibrated = np.array([calibrator.transform(Cause.DELIVERY, v) for v in score])

    quyet_dinh = calibrated >= 0.35
    assert quyet_dinh.any() and not quyet_dinh.all()
    nguong_tuong_duong = score[quyet_dinh].min()
    assert np.array_equal(quyet_dinh, score >= nguong_tuong_duong)


# --------------------------------------------------------------------------
# L27 (phan 2) — ngan sach phai dat theo BOI SO chi phi, khong theo so tuyet doi.
# --------------------------------------------------------------------------

def test_ngan_sach_muc_thap_van_du_cho_MOT_analyst_van_ban():
    """Chan viec cong rui ro quay lai mot cach ngam qua ngan sach.

    Cach dat cu dung so tuyet doi (2,0 ms cho case rui ro thap). Khi cause head doi
    tu ban tam (0,0093 ms) sang ban huan luyen (1,3 ms), muc do khong con du cho bat
    ky analyst van ban nao — va don rui ro thap khong bao gio duoc phan tich van ban.
    Do la loi L27.
    """
    from masdss.system.plan import BUDGET_RATIO, FULL_ANALYST_COST_MS

    ngan_sach_thap = FULL_ANALYST_COST_MS * BUDGET_RATIO["low"]
    gia_cau_truc = 0.3                             # delivery
    gia_mot_analyst_van_ban = 1.3

    assert ngan_sach_thap >= gia_cau_truc + gia_mot_analyst_van_ban, (
        "muc rui ro thap khong mua noi mot analyst van ban — cong rui ro da quay lai")
    assert ngan_sach_thap < FULL_ANALYST_COST_MS, (
        "muc rui ro thap mua duoc het thi Contract Net khong con phai phan bo gi")


def test_ngan_sach_muc_cao_du_chay_het():
    from masdss.system.plan import BUDGET_RATIO, FULL_ANALYST_COST_MS

    assert FULL_ANALYST_COST_MS * BUDGET_RATIO["high"] >= FULL_ANALYST_COST_MS


def test_cost_ms_khai_bao_phai_gan_gia_do_duoc():
    """`cost_ms` la dau vao cua bai toan phan bo. Khai sai la phan bo sai.

    Da tung sai gan 10 lan (khai 12,0 trong khi gia that 1,3), va sai lech do du de
    lam macro-F1 cua MAS-DSS tut 0,14 duoi doi chung.
    """
    from masdss.capabilities.cause_head import LexiconCauseHead, TfidfCauseHead

    # p95 do duoc: Lexicon 0,016 ms · TF-IDF 1,26 ms
    assert 0.5 <= TfidfCauseHead().cost_ms <= 3.0
    assert LexiconCauseHead().cost_ms <= 1.0
    assert TfidfCauseHead().cost_ms > LexiconCauseHead().cost_ms


# --------------------------------------------------------------------------
# Doi chieu HANG SO NEN. Do la phep thu re nhat cho mot mo hinh xac suat, va
# tren du lieu mat can bang no la phep thu DUY NHAT lam lo ra van de: o moc
# `ngay mua + 7`, diem THO co Brier 0,1139 so voi 0,1111 cua hang so.
# --------------------------------------------------------------------------

def _bao_cao(brier_before, brier_after, brier_constant):
    from masdss.capabilities.risk_model import CalibrationReport
    return CalibrationReport(
        split="test", in_sample=False, pr_auc=0.25, roc_auc=0.65,
        brier_before=brier_before, brier_after=brier_after,
        ece_before=0.07, ece_after=0.03, n=11322, brier_constant=brier_constant)


def test_brier_skill_am_khi_mo_hinh_thua_hang_so():
    """Con so THAT do duoc tren tap test o moc moi, khong phai fixture bia ra."""
    bao_cao = _bao_cao(0.113862, 0.107657, 0.111141)
    assert bao_cao.brier_skill_before == pytest.approx(-0.0245, abs=1e-4)
    assert bao_cao.brier_skill_after == pytest.approx(0.0314, abs=1e-4)


def test_canh_bao_phat_ra_khi_diem_tho_thua_hang_so():
    """Diem tho thua hang so => hieu chuan la BAT BUOC, va phai noi ro dieu do."""
    canh_bao = _bao_cao(0.113862, 0.107657, 0.111141).canh_bao()
    assert canh_bao is not None
    assert "TRUOC hieu chuan" in canh_bao and "BAT BUOC" in canh_bao


def test_canh_bao_nghiem_trong_hon_khi_ca_sau_hieu_chuan_van_thua():
    bao_cao = _bao_cao(0.130, 0.125, 0.111141)
    canh_bao = bao_cao.canh_bao()
    assert canh_bao is not None and "SAU hieu chuan" in canh_bao


def test_khong_canh_bao_khi_mo_hinh_hon_hang_so_o_ca_hai_muc():
    assert _bao_cao(0.100, 0.095, 0.111141).canh_bao() is None


def test_bang_bao_cao_LUON_co_dong_hang_so_va_skill():
    """Neu hang so khong nam trong bang thi nguoi doc phai tu di tim no — va se khong.

    Bo mot chi so khoi bang bao cao la cach re nhat de mot ket qua bat loi bien mat
    ma khong ai noi doi cau nao.
    """
    bang = _bao_cao(0.113862, 0.107657, 0.111141).to_frame()
    ten = set(bang["metric"])
    assert any("HANG SO" in t for t in ten), "bang thieu moc doi chieu hang so"
    assert sum("Brier skill" in t for t in ten) == 2


def test_predict_proba_KHONG_chay_duoc_neu_chua_hieu_chuan():
    """Hieu chuan la bat buoc o muc KIEU DU LIEU, khong phai o muc ky luat."""
    from masdss.capabilities.risk_model import RiskModel
    from masdss.core.ontology import DecisionPoint
    from masdss.data.featureset import FeatureSet

    with pytest.raises(RuntimeError, match="chua duoc huan luyen"):
        RiskModel(feature_set=FeatureSet(DecisionPoint.T3)).predict_proba(None)
