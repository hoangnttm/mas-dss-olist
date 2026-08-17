"""IMP-1 va IMP-2 — Kiem tra tren TEP DAU RA THAT, khong chi tren don vi.

Xem docs/methodology-log.md §4.

VI SAO CAN TANG TEST NAY:

    Ba loi thiet ke nghiem trong nhat cua du an (L08, L10, L11) deu la BAT BIEN
    NGHIEP VU bi vi pham, va ca ba chi lo ra khi mot nguoi nhin vao `decisions.jsonl`
    bang mat. Khong test don vi nao bat duoc chung, vi tung thanh phan deu dung —
    cai sai nam o cho chung ghep lai.

    Rieng L08 khien 94,7% so case khong bao gio duoc phan tich, va RQ3 mat doi tuong
    nghien cuu. No ton tai trong mot thoi gian dai ma moi test van xanh.

HAI NHOM O DAY:

    IMP-1: lan chay KHOE phai im lang tuyet doi (0 canh bao, 0 suy giam).
           Bon loi L14-L17 deu la bao dong gia, va tat ca deu le ra phai lo ra
           ngay neu co dung mot phep thu nay.

    IMP-2: bat bien muc he thong tren tep dau ra that.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from masdss.cli.run_system import run

from conftest import N_CASES, N_CASES_MONITORING


def _decisions(out_dir: Path) -> list[dict]:
    return [json.loads(line) for line in
            (out_dir / "decisions.jsonl").read_text(encoding="utf-8").splitlines()]


def _reliability(out_dir: Path) -> dict:
    return json.loads((out_dir / "reliability_report.json").read_text(encoding="utf-8"))


# =============== IMP-1: lan chay khoe phai im lang ===============

def test_healthy_run_raises_no_alert(healthy_run_large: Path) -> None:
    """Bo giam sat phai IM LANG tuyet doi khi khong co loi nao.

    Day la phep thu le ra da bat duoc ca bon loi L14-L17. Mot bo giam sat khong im
    lang duoc tren du lieu khoe thi chua dung duoc, bat ke no bat loi tot den dau.
    """
    report = _reliability(healthy_run_large)
    assert report["health_alerts"] == [], (
        f"bao dong gia tren lan chay khong tiem loi: {report['health_alerts']}"
    )


def test_monitoring_run_is_large_enough_to_engage_psi(healthy_run_large: Path) -> None:
    """Chan loi T04: phep thu im lang chi co nghia khi bo giam sat thuc su chay.

    Voi 25 case, PSI khong bao gio duoc tinh — test im lang khi do la test RONG,
    xanh vi phep do khong chay chu khong phai vi he thong dung.
    """
    from masdss.system.reliability.health import MIN_PSI_OBSERVATIONS

    assert N_CASES_MONITORING >= MIN_PSI_OBSERVATIONS, (
        f"lan chay giam sat can it nhat {MIN_PSI_OBSERVATIONS} case de PSI duoc tinh"
    )
    assert len(_decisions(healthy_run_large)) >= MIN_PSI_OBSERVATIONS


def test_healthy_run_triggers_no_guard(healthy_run_large: Path) -> None:
    report = _reliability(healthy_run_large)
    assert report["guard_violations"] == [], (
        f"guard chan nham tren lan chay khoe: {report['guard_violations'][:3]}"
    )


def test_healthy_run_has_no_degraded_decision(healthy_run_large: Path) -> None:
    """Khong tiem loi thi khong duoc co case nao bi danh dau suy giam."""
    degraded = [d["case_id"] for d in _decisions(healthy_run_large) if d["degradation_level"] > 0]
    assert not degraded, f"{len(degraded)} case suy giam ma khong co loi nao duoc tiem"


def test_healthy_run_opens_no_circuit(healthy_run_large: Path) -> None:
    report = _reliability(healthy_run_large)
    opened = [b for b in report["breakers"] if b["opened_count"] > 0]
    assert not opened, f"breaker mo tren lan chay khoe: {opened}"


# =============== IMP-2: bat bien muc he thong ===============

def test_identified_cause_always_leads_to_action(normal_run: Path) -> None:
    """Da quy ket duoc nguyen nhan thi khong duoc phep khong lam gi.

    Day la bat bien le ra da bat duoc L10: luat `low_risk_default` cho `no_action`
    du da tim ra nguyen nhan giao hang ro rang, chi vi diem rui ro du bao thap.
    """
    offenders = [d["case_id"] for d in _decisions(normal_run)
                 if d["causes"] and d["action"] == "no_action"]
    assert not offenders, (
        f"{len(offenders)} case da quy ket duoc nguyen nhan nhung hanh dong la no_action"
    )


def test_attribution_actually_runs_on_most_cases(normal_run: Path) -> None:
    """Phai co mot ty le du lon di qua phien dau thau.

    Day la bat bien le ra da bat duoc L08: cong `risk >= MEDIUM` chan quy ket o T4
    khien 94,7% case khong bao gio duoc phan tich. Nguong 20% duoc dat thap co y —
    no khong nham do chat luong quy ket, ma nham bat truong hop co che quy ket bi
    VO HIEU HOA hoan toan.
    """
    decisions = _decisions(normal_run)
    with_causes = sum(1 for d in decisions if d["causes"])
    ratio = with_causes / len(decisions)
    assert ratio >= 0.20, (
        f"chi {100 * ratio:.1f}% case duoc quy ket nguyen nhan — nghi co dieu kien nao "
        f"dang chan phien dau thau"
    )


def test_escalation_always_marks_human_review(normal_run: Path) -> None:
    """Bat bien le ra da bat duoc L11."""
    for d in _decisions(normal_run):
        if d["action"] == "escalate_to_human":
            assert d["needs_human_review"], f"{d['case_id']}: escalate ma khong danh dau"


def test_degraded_decision_always_escalates(normal_run: Path) -> None:
    """DP1 tren tep dau ra that, khong chi trong constructor."""
    for d in _decisions(normal_run):
        if d["degradation_level"] > 0:
            assert d["needs_human_review"]
            assert d["action"] == "escalate_to_human"


def test_multi_cause_flag_matches_cause_count(normal_run: Path) -> None:
    """DP2: co tu hai nguyen nhan tro len thi phai gan co."""
    for d in _decisions(normal_run):
        distinct = {c["cause"] for c in d["causes"]} - {"unknown"}
        assert d["multi_cause"] == (len(distinct) >= 2), (
            f"{d['case_id']}: multi_cause={d['multi_cause']} nhung co {len(distinct)} nguyen nhan"
        )


def test_every_bid_carries_evidence(normal_run: Path) -> None:
    """Mot bid tran khong kiem chung duoc — no khong duoc phep vao quyet dinh.

    Loc theo ONTOLOGY chu khong theo PERFORMATIVE: Contract Net hai pha dung
    `PROPOSE` cho ca ban khai nang luc (`ontology="declaration"`, chua co bang chung)
    lan bid that (`ontology="bid"`, bat buoc co bang chung). Day la lan thu BA cung
    mot bai hoc — guard va Explainer cung tung khoa nham theo performative.
    """
    from masdss.runtime.message_log import MessageLog

    log = MessageLog(normal_run / "messages.sqlite")
    bare, declarations = [], 0
    for conversation_id in log.conversation_ids():
        for message in log.conversation(conversation_id):
            if message.ontology == "declaration":
                declarations += 1
            elif message.ontology == "bid" and not message.content.get("evidence"):
                bare.append(message.sender)
    log.close()
    assert declarations > 0, "khong thay ban khai nang luc nao — pha 1 co chay khong?"
    assert not bare, f"bid khong kem bang chung tu: {set(bare)}"


# =============== IMP-1: duoi tiem loi thi phai co canh bao ===============

def test_crash_injection_is_never_silent(tmp_path: Path, fixtures) -> None:
    """Doi xung voi test lan chay khoe: co loi thi KHONG duoc im lang."""
    orders, caps = fixtures
    out = tmp_path / "crash"
    asyncio.run(run(out, n_cases=N_CASES, inject="crash:prediction",
                    orders=orders, capabilities=caps))
    decisions = _decisions(out)
    silent = [d for d in decisions
              if d["degradation_level"] == 0 and not d["needs_human_review"]]
    assert not silent, f"{len(silent)} case hong am tham duoi loi crash"


def test_reliability_can_be_switched_off_for_ablation(tmp_path: Path, fixtures) -> None:
    """Duong ablation cho RQ1 phai la mot THAM SO, khong phai mot nhanh ma nguon."""
    orders, caps = fixtures
    out = tmp_path / "ablation"
    asyncio.run(run(out, n_cases=N_CASES, orders=orders, capabilities=caps,
                    reliability=False))
    assert _reliability(out)["reliability_enabled"] is False


# --------------------------------------------------------------------------
# L27 — hai artifact cua CUNG mot lan chay bieu dien `causes` khac nhau.
# --------------------------------------------------------------------------

def test_bo_doc_causes_nhan_ca_hai_dang_bieu_dien():
    """`decisions.jsonl` ghi [{cause, probability}], `baselines.jsonl` ghi ["ten"].

    Bat nhat nay da lam bang T10.2 bao MAS-DSS quy ket 0/250 trong khi that ra no
    quy ket 97 don — phep kiem tra `"delivery" in [{...}]` luon False. Test nay
    canh cho ca hai dang, va se do neu mot dang thu ba xuat hien.
    """
    from masdss.cli.run_attribution import _cause_names

    assert _cause_names(["delivery", "price"]) == {"delivery", "price"}
    assert _cause_names([{"cause": "delivery", "probability": 0.63}]) == {"delivery"}
    assert _cause_names([]) == set()
    assert _cause_names(None) == set()


def test_gold_labels_tu_choi_nguon_goc_dang_chuoi():
    """`provenance` phai la enum. Mot chuoi tu do se lam co `citable` vo nghia."""
    import pandas as pd
    import pytest

    from masdss.data.labels import GoldLabels, Provenance

    frame = pd.DataFrame({"order_id": ["o1"], "cause_delivery": [1],
                          "cause_quality": [0], "cause_service": [0], "cause_service": [0]})
    with pytest.raises(TypeError):
        GoldLabels(frame=frame, provenance="human")

    gold = GoldLabels(frame=frame, provenance=Provenance.MODEL_ASSISTED_PROVISIONAL)
    assert not gold.citable


def test_danh_gia_quy_ket_tu_choi_weak_label():
    """Rang buoc C2 duoc cuong che bang KIEU DU LIEU, khong bang ky luat ca nhan."""
    import pandas as pd
    import pytest

    from masdss.core.errors import WeakLabelInEvaluation
    from masdss.data.labels import WeakLabels
    from masdss.evaluation.attribution import evaluate

    weak = WeakLabels(frame=pd.DataFrame({"order_id": ["o1"], "cause_delivery": [1],
                                          "cause_quality": [0], "cause_service": [0],
                                          "cause_service": [0]}))
    with pytest.raises(WeakLabelInEvaluation):
        evaluate(weak, {})


def test_bang_ket_qua_luon_mang_theo_co_citable():
    """Con so khong bao gio duoc tach roi khoi nguon goc cua no."""
    import pandas as pd

    from masdss.data.labels import GoldLabels, Provenance
    from masdss.evaluation.attribution import evaluate

    frame = pd.DataFrame({
        "order_id": [f"o{i}" for i in range(6)], "tier": ["A"] * 6,
        "cause_delivery": [1, 1, 0, 0, 1, 0], "cause_quality": [0, 1, 1, 0, 0, 0],
        "cause_service": [0, 0, 0, 1, 0, 0], "cause_service": [0, 0, 0, 0, 0, 1],
    })
    gold = GoldLabels(frame=frame, provenance=Provenance.MODEL_ASSISTED_PROVISIONAL)
    result = evaluate(gold, {"he_A": frame.drop(columns=["tier"])})
    per_cause, per_slice = result.stamped()
    assert not result.citable
    assert (per_cause["citable"] == False).all()      # noqa: E712
    assert (per_slice["citable"] == False).all()      # noqa: E712


# --------------------------------------------------------------------------
# L28 — co `citable` phai bam theo DUNG tep gold duoc truyen vao.
# --------------------------------------------------------------------------

def test_meta_bam_theo_ten_tep_gold_khong_dat_cung(tmp_path):
    """Hai gold set trong cung thu muc KHONG duoc ghi de meta cua nhau.

    Truoc khi sua, `build_goldset --out <tep khac>` van ghi vao
    `gold_labels_meta.json`, va `run_attribution --gold <tep khac>` van doc dung
    tep do. Hau qua: co `citable` gan theo gold set MAC DINH chu khong theo gold
    set thuc su dang duoc do — sai duoc ca hai chieu, va khong co dau hieu nao.
    """
    from masdss.cli.build_goldset import meta_path

    a = meta_path(tmp_path / "gold_labels.csv")
    b = meta_path(tmp_path / "gold_labels_rehearsal.csv")
    assert a != b
    assert a.name == "gold_labels_meta.json"
    assert b.name == "gold_labels_rehearsal_meta.json"


def test_provenance_citable_phan_biet_dung_hai_trang_thai():
    from masdss.data.labels import Provenance

    assert Provenance.HUMAN_INDEPENDENT.citable
    assert not Provenance.MODEL_ASSISTED_PROVISIONAL.citable
    assert "trich dan duoc" in Provenance.HUMAN_INDEPENDENT.banner
    assert "KHONG duoc trich" in Provenance.MODEL_ASSISTED_PROVISIONAL.banner


def test_bang_ket_qua_doi_co_citable_khi_doi_nguon_goc():
    """Chuyen trang thai phai la MOT tham so, khong phai mot lan sua ma nguon."""
    import pandas as pd

    from masdss.data.labels import GoldLabels, Provenance
    from masdss.evaluation.attribution import evaluate

    frame = pd.DataFrame({
        "order_id": [f"o{i}" for i in range(6)], "tier": ["A"] * 6,
        "cause_delivery": [1, 1, 0, 0, 1, 0], "cause_quality": [0, 1, 1, 0, 0, 0],
        "cause_service": [0, 0, 0, 1, 0, 0], "cause_service": [0, 0, 0, 0, 0, 1],
    })
    predictions = {"he_A": frame.drop(columns=["tier"])}

    for provenance, mong_doi in ((Provenance.MODEL_ASSISTED_PROVISIONAL, False),
                                 (Provenance.HUMAN_INDEPENDENT, True)):
        result = evaluate(GoldLabels(frame=frame, provenance=provenance), predictions)
        per_cause, per_slice = result.stamped()
        assert result.citable is mong_doi
        assert (per_cause["citable"] == mong_doi).all()
        assert (per_slice["citable"] == mong_doi).all()


def test_so_performative_khop_voi_tai_lieu():
    """Chan truot giua ma nguon va tai lieu.

    Ba tep tai lieu dang hieu luc tung ghi "9 performative" trong khi ontology co
    10 — sai lech nay song sot nhieu thang vi khong co gi doi chieu hai ben. Test
    nay bien viec them mot performative thanh mot loi DO, nhac nguoi sua ca tai lieu.

    Neu con so doi that: sua o day VA o `research-questions-objectives.md` (A1,
    MT1.1), `build-plan.md` (T5.2), `technical-plan-v3.md` (bang RQ2).
    """
    from masdss.core.message import Performative

    assert len(Performative) == 10, (
        "So performative doi — phai cap nhat ca ba tep tai lieu neu trong docstring")
