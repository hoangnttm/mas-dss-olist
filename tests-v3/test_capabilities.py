"""WP3 / T3.1, T3.2, T3.5, T3.6 — Tang capability.

Phuc vu: RQ2 (chot hanh dong), RQ3 (bang chung dau thau), RQ1 (cuong che DP1).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from masdss.capabilities.ood import OODDetector
from masdss.capabilities.price_signal import PriceSignal
from masdss.capabilities.risk_model import RiskModel, expected_calibration_error
from masdss.capabilities.rules import RuleEngine, facts_from
from masdss.config import CONFIG
from masdss.core.ontology import DecisionPoint, OrderCase


# =============== T3.6 rule engine ===============

@pytest.fixture(scope="module")
def engine() -> RuleEngine:
    return RuleEngine.load()


def _facts(**kwargs) -> dict:
    base = dict(risk=1, causes=["delivery"], degradation_level=0, decision_point="T4")
    base.update(kwargs)
    return facts_from(**base)


def test_expedite_shipment_is_gone(engine: RuleEngine) -> None:
    """Bat kha thi ve mat thoi gian tai T3/T4 — giu lai chi de hoi dong bat loi."""
    assert "expedite_shipment" not in engine.actions


def test_degraded_system_always_escalates(engine: RuleEngine) -> None:
    """DP1 — luat cuong che thang moi luat nghiep vu."""
    outcome = engine.decide(_facts(degradation_level=1, risk=2, causes=["quality"]))
    assert outcome.action == "escalate_to_human"
    assert outcome.enforced


def test_unknown_cause_escalates_at_t4_only(engine: RuleEngine) -> None:
    """DP3 tai T4. Tai T3 chua he co nhiem vu quy ket nen khong ap dung."""
    assert engine.decide(_facts(causes=[], decision_point="T4")).action == "escalate_to_human"
    assert engine.decide(_facts(causes=[], decision_point="T3")).action != "escalate_to_human"


def test_multi_cause_high_risk_gets_human_callback(engine: RuleEngine) -> None:
    outcome = engine.decide(_facts(risk=2, causes=["delivery", "quality"]))
    assert outcome.rule_id == "multi_cause_high_risk"


def test_first_matching_rule_wins(engine: RuleEngine) -> None:
    outcome = engine.decide(_facts(risk=1, causes=["quality"]))
    assert outcome.action == "return_replacement_offer"


def test_rule_engine_does_not_use_eval(engine: RuleEngine) -> None:
    """Bieu thuc lay tu tep cau hinh khong duoc di qua eval()."""
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(RuleEngine))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
    names = {getattr(c.func, "id", "") for c in calls}
    assert "eval" not in names and "exec" not in names


def test_every_action_has_declared_cost(engine: RuleEngine) -> None:
    for rule in (*engine.enforced, *engine.rules):
        assert rule.action in engine.actions, f"luat '{rule.id}' tro toi hanh dong chua khai bao"


# =============== T3.5 tin hieu gia ===============

def _price_frame(n: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "category": ["toys"] * n + ["rare_cat"] * 5,
        "freight_ratio": np.concatenate([rng.normal(0.2, 0.05, n), rng.normal(0.2, 0.05, 5)]),
    })


def test_price_signal_refuses_to_fit_on_non_train() -> None:
    """Hoc thong ke tu val/test la ro ri — phai bao loi, khong am tham cho qua."""
    with pytest.raises(ValueError):
        PriceSignal().fit(_price_frame(), split_name="test")


def test_price_signal_refuses_thin_category() -> None:
    """Dieu kien REFUSE kiem chung duoc cua Price Analyst (DP3)."""
    signal = PriceSignal(min_samples=30).fit(_price_frame())
    thin = OrderCase(case_id="c1", decision_point=DecisionPoint.T4,
                     features={"category": "rare_cat", "freight_ratio": 0.9})
    assert not signal.can_handle(thin)
    assert "5 mau" in signal.refusal_reason(thin)


def test_price_signal_emits_evidence_when_it_bids() -> None:
    """Bid khong duoc phep la mot con so tran — phai kem bang chung."""
    signal = PriceSignal(min_samples=30).fit(_price_frame())
    outlier = OrderCase(case_id="c2", decision_point=DecisionPoint.T4,
                        features={"category": "toys", "freight_ratio": 0.6})
    confidence, evidence = signal.run(outlier)
    assert confidence > 0.5 and evidence
    assert evidence[0].kind == "freight_zscore"


def test_price_signal_stays_silent_on_normal_freight() -> None:
    signal = PriceSignal(min_samples=30).fit(_price_frame())
    normal = OrderCase(case_id="c3", decision_point=DecisionPoint.T4,
                       features={"category": "toys", "freight_ratio": 0.2})
    assert signal.run(normal)[0] == 0.0


# =============== T3.2 phat hien OOD ===============

def _ood_frame(n: int = 500) -> pd.DataFrame:
    rng = np.random.default_rng(1)
    return pd.DataFrame({"a": rng.normal(0, 1, n), "b": rng.normal(5, 2, n)})


def test_ood_refuses_to_fit_on_non_train() -> None:
    with pytest.raises(ValueError):
        OODDetector().fit(_ood_frame(), ("a", "b"), split_name="val")


def test_ood_detection_rises_with_perturbation() -> None:
    """Ket qua that: bo phat hien chi bat chac loai nhieu loan lon."""
    train = _ood_frame()
    detector = OODDetector(quantile=0.99).fit(train, ("a", "b"))

    baseline = detector.detection_rate(train)
    shifted = train.copy()
    shifted["a"] = shifted["a"] + 6.0
    assert baseline < 0.03
    assert detector.detection_rate(shifted) > baseline * 5


def test_ood_threshold_matches_quantile() -> None:
    train = _ood_frame()
    detector = OODDetector(quantile=0.99).fit(train, ("a", "b"))
    assert 0.005 <= detector.detection_rate(train) <= 0.02


# =============== T3.1 hieu chuan ===============

def test_ece_is_zero_for_perfect_calibration() -> None:
    y_true = np.array([0, 0, 1, 1])
    assert expected_calibration_error(y_true, np.array([0.0, 0.0, 1.0, 1.0])) == 0.0


def test_ece_detects_overconfidence() -> None:
    y_true = np.array([0, 1, 0, 1])
    overconfident = np.array([0.99, 0.99, 0.99, 0.99])
    assert expected_calibration_error(y_true, overconfident) > 0.4


def test_calibration_report_flags_in_sample() -> None:
    """Con so do tren tap da dung de hieu chuan phai duoc danh dau ro."""
    from masdss.capabilities.risk_model import CalibrationReport

    report = CalibrationReport(split="val", in_sample=True, pr_auc=0.4, roc_auc=0.7,
                               brier_before=0.09, brier_after=0.08,
                               ece_before=0.01, ece_after=0.0, n=100)
    text = report.to_frame().to_string()
    assert "IN-SAMPLE" in text


def test_risk_thresholds_map_to_levels() -> None:
    """Mo hinh CHUA huan luyen dung thang du phong (0,40 / 0,70)."""
    from masdss.core.ontology import DecisionPoint, RiskLevel
    from masdss.data.featureset import FeatureSet

    model = RiskModel(feature_set=FeatureSet(DecisionPoint.T3))
    assert model.risk_thresholds == (0.40, 0.70)
    assert model.to_risk_level(0.1) is RiskLevel.LOW
    assert model.to_risk_level(0.5) is RiskLevel.MEDIUM
    assert model.to_risk_level(0.9) is RiskLevel.HIGH


def test_thang_rui_ro_duoc_suy_ra_tu_val_va_PHAN_BIET_duoc(fitted_risk_model) -> None:
    """Bat bien that su cua thang rui ro: no phai PHAN BIET duoc.

    Ban cu dat hai hang so 0,40 / 0,70 tren diem DA HIEU CHUAN, nen 97,52% case roi
    vao LOW va ty le bat man cua bang do (13,90%) gan nhu bang tong the (14,82%) —
    thang chay nhung khong noi len dieu gi.

    Bai nay khong kiem hai con so cu the (chung phu thuoc du lieu) ma kiem TINH CHAT:
    ba bang phai khac nhau, va ty le bat man thuc te phai TANG DAN theo muc rui ro.
    Mot thang khong thoa tinh chat nay thi vo dung du con so co dep den dau.
    """
    model, val = fitted_risk_model
    low, high = model.risk_thresholds
    assert 0.0 < low < high < 1.0

    scores = model.predict_proba(val)
    y = val["is_dissatisfied"].astype(int).to_numpy()
    ty_le = []
    for lo, hi in ((0.0, low), (low, high), (high, 1.01)):
        band = (scores >= lo) & (scores < hi)
        assert band.any(), f"bang [{lo}, {hi}) rong — thang khong phan biet duoc"
        ty_le.append(float(y[band].mean()))

    assert ty_le[0] < ty_le[1] < ty_le[2], (
        f"ty le bat man khong tang dan theo muc rui ro: {ty_le}")


# --------------------------------------------------------------------------
# Luat giai doan 1 @ T3 — phuc hoi dich vu CHU DONG
#
# Truoc 13/08 KHONG co luat nao viet cho T3: ca 8 luat deu khoa theo `has_cause_*`
# ma nguyen nhan chi ton tai o T4. Hau qua la moi don T3 roi vao `default_action`,
# va MEDIUM voi HIGH nhan cung mot hanh dong.
# --------------------------------------------------------------------------

def _t3(risk: int, days_to_deadline: float, order_value: float = 200.0) -> dict:
    return facts_from(
        risk=risk, causes=[], degradation_level=0, decision_point="T3",
        context={"days_to_deadline": days_to_deadline, "delivery_state": 1.0,
                 "order_value": order_value, "is_late": days_to_deadline < 0},
    )


def test_t3_qua_han_va_rui_ro_cao_duoc_hanh_dong_manh_nhat(engine) -> None:
    """Nhom 58,97% bat man (4,63x) — dat nhat nhung cung dang nhat."""
    out = engine.decide(_t3(risk=2, days_to_deadline=-2.0))
    assert out.rule_id == "t3_qua_han_rui_ro_cao"
    assert out.action == "proactive_apology_with_coupon"


def test_t3_qua_han_khong_can_mo_hinh_xac_nhan(engine) -> None:
    """Tre hen la SU KIEN DA XAY RA, khong phai du bao.

    Ngay nhom risk=0 da qua han van co 18,57% bat man — tren ty le nen 12,74%. Do
    la ly do luat nay khong khoa theo muc rui ro.
    """
    out = engine.decide(_t3(risk=0, days_to_deadline=-5.0))
    assert out.rule_id == "t3_qua_han"
    assert out.action == "cs_callback_within_24h"


def test_t3_don_gia_tri_thap_khong_duoc_cap_phieu_giam_gia(engine) -> None:
    """Nguong 42,86 = 15,0 / 0,35 — suy tu `max_cost_ratio`, khong phai so bia.

    Don 30 tien khong the chiu mot phieu giam gia gia 15: no vuot 35% gia tri don.
    """
    out = engine.decide(_t3(risk=2, days_to_deadline=-2.0, order_value=30.0))
    assert out.action != "proactive_apology_with_coupon"
    assert out.rule_id == "t3_qua_han"      # tut xuong hanh dong re hon


def test_t3_rui_ro_cao_nhung_giao_hang_dung_tien_do(engine) -> None:
    out = engine.decide(_t3(risk=2, days_to_deadline=30.0))
    assert out.rule_id == "t3_rui_ro_cao"
    assert out.action == "preemptive_ticket_open"


def test_t3_rui_ro_thap_va_khong_tre_thi_khong_can_thiep(engine) -> None:
    out = engine.decide(_t3(risk=0, days_to_deadline=30.0))
    assert out.action == "no_action"


def test_luat_T3_KHONG_khop_o_T4_va_nguoc_lai(engine) -> None:
    """Hai bo luat phai roi nhau, neu khong mot moc se cuop luat cua moc kia."""
    t4 = facts_from(risk=2, causes=["delivery"], degradation_level=0,
                    decision_point="T4",
                    context={"days_to_deadline": -2.0, "order_value": 200.0})
    assert not engine.decide(t4).rule_id.startswith("t3_")

    # O T3 khong ton tai nguyen nhan, nen moi luat khoa theo `has_cause_*` phai im.
    assert engine.decide(_t3(risk=2, days_to_deadline=-2.0)).rule_id.startswith("t3_")


def test_thieu_moc_thoi_gian_thi_luat_T3_khong_khop_thay_vi_doan(engine) -> None:
    """Su kien vang mat phai lam luat KHONG khop, khong duoc mac dinh ve 0.

    Dat 0 cho `days_to_deadline` thieu se vo tinh thoa `>= 0 and <= 3` va cap mot
    hanh dong dua tren du lieu khong ton tai.
    """
    facts = facts_from(risk=2, causes=[], degradation_level=0, decision_point="T3",
                       context={"order_value": 200.0})
    assert "days_to_deadline" not in facts
    assert engine.decide(facts).rule_id == "t3_rui_ro_cao"
