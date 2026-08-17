"""WP6 — Noi day he thong: capability -> agent -> ke hoach.

Phuc vu: RQ3, RQ1 (tinh cong bang cua phep so sanh).

DAY LA NOI QUY TAC "DUNG CHUNG CAPABILITY" TRO THANH HIEN THUC.

`Capabilities` duoc dung MOT LAN, roi truyen vao ca MAS-DSS lan moi baseline. Vi
chung nhan CUNG DOI TUONG (khong phai cung lop, khong phai cung tham so — cung
doi tuong), khong ton tai kha nang "vo tinh cho MAS mo hinh tot hon".

Test `test_baseline_parity.py` kiem tra dung dieu do bang phep so sanh dinh danh
doi tuong (`is`), khong phai so sanh gia tri.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from masdss.agents.analysts.pool import (
    DeliveryAnalyst,
    QualityAnalyst,
    ServiceAnalyst,
)
from masdss.agents.critic import ArbiterAgent, PolicyCriticAgent
from masdss.agents.core_agents import (
    AnalyticsAgent,
    CaseManagerAgent,
    PredictionAgent,
    RecommendationAgent,
    RuleAgent,
)
from masdss.capabilities.cause_head import LexiconCauseHead, TfidfCauseHead
from masdss.capabilities.delivery_signal import CombinedDeliverySignal, DeliverySignal
from masdss.capabilities.ood import OODDetector
from masdss.capabilities.price_signal import PriceSignal
from masdss.capabilities.risk_model import RiskModel
from masdss.capabilities.rules import RuleEngine
from masdss.config import CONFIG
from masdss.core.decision import Decision
from masdss.core.message import Message, Performative
from masdss.core.ontology import (
    Action,
    Cause,
    CauseAssignment,
    DecisionPoint,
    Evidence,
    RiskLevel,
)
from masdss.data.featureset import FeatureSet
from masdss.system.blackboard import Blackboard
from masdss.system.orchestrator import Registry


def _build_cause_head(kind: str, train: pd.DataFrame, exclude: set | None):
    """Chon va huan luyen cause head.

    Ban `tfidf` chi hoc tu WEAK LABEL tren tap train — gold set khong tham gia
    huan luyen o bat ky buoc nao. Do la rang buoc C2, va no duoc giu o day chu
    khong o tai lieu.
    """
    if kind == "lexicon":
        return LexiconCauseHead()
    if kind != "tfidf":
        raise ValueError(f"cause head khong biet: {kind!r}")

    from masdss.core.ontology import Cause
    from masdss.data.labels import CAUSE_COLUMNS, make_weak_labels

    frame = train[train["is_dissatisfied"] & train["review_content"].notna()].copy()
    if exclude:
        frame = frame[~frame["order_id"].isin(exclude)]
    weak = make_weak_labels(frame).frame
    texts = (frame["review_title"].fillna("").astype(str) + " "
             + frame["review_content"].fillna("").astype(str)).tolist()
    labels = {Cause(c.replace("cause_", "")): weak[c].tolist() for c in CAUSE_COLUMNS}
    return TfidfCauseHead().fit(texts, labels, seed=CONFIG.seed)


@dataclass
class Capabilities:
    """Tap nang luc nen. Dung chung giua MAS-DSS va moi baseline."""

    risk_model: RiskModel
    ood: OODDetector
    delivery: CombinedDeliverySignal
    price: PriceSignal
    cause_head: object
    rules: RuleEngine

    @staticmethod
    def fit(train: pd.DataFrame, val: pd.DataFrame,
            decision_point: DecisionPoint = DecisionPoint.T3,
            *, cause_head: str = "tfidf",
            exclude_order_ids: set | None = None,
            risk_train: pd.DataFrame | None = None,
            risk_val: pd.DataFrame | None = None) -> "Capabilities":
        """Huan luyen tap nang luc nen.

        HAI TONG THE, VA SU TACH BACH NAY LA BAT BUOC.

            `train`/`val`            -> tong the T4 (DAY DU). Nang luc QUY KET hoc
                                        o day: cause head, tin hieu giao hang, gia.
            `risk_train`/`risk_val`  -> tong the T3 (CON KIP CAN THIEP). Mo hinh du
                                        bao va bo phat hien OOD hoc o day.

        Vi sao khong dung chung mot tong the: mo hinh du bao chi bao gio duoc cham
        diem tren nhung don CON KIP CAN THIEP tai T3, nen hoc tren nhung don da co
        danh gia truoc moc la hoc mot tong the no khong bao gio gap (L33). Nguoc lai,
        cause head hoc TOT HON tren tong the day du: nhom bi loai giao som hon 13,2
        ngay va co van ban nhieu hon, tuc chua dung nhung khieu nai KHONG do giao
        hang ma tang quy ket can nhat.

        Mac dinh `risk_* = train/val` de moi loi goi cu van chay — nhung khi do ca
        hai deu hoc tren cung mot tong the, va do la trach nhiem cua ben goi.

        MAC DINH LA `tfidf` — ban T3.4 da huan luyen. Doi tu `lexicon` sang tu
        11/08 sau khi do doi dau tren 250 dong gold: macro-F1 0,2196 -> 0,4730, va
        `lexicon` chi sinh duoc DUNG HAI gia tri do tin cay nen `bid_entropy` cua
        DP2 va viec hieu chuan (T7.3b) deu vo nghia tren no.

        `cause_head="lexicon"` van giu duoc de chay phan tich do nhay cho Chuong 5.

        `exclude_order_ids` loai cac don nam trong gold set ra khoi tap huan luyen
        cua cause head. Nhan gold KHONG bao gio duoc dung de huan luyen (rang buoc
        C2), nhung neu chinh VAN BAN do da nam trong tap train thi phep do tren gold
        set khong con la ngoai mau — nen loai truoc cho sach.
        """
        feature_set = FeatureSet(decision_point)
        numeric = feature_set.numeric_names
        r_train = train if risk_train is None else risk_train
        r_val = val if risk_val is None else risk_val
        head = _build_cause_head(cause_head, train, exclude_order_ids)

        # `delivery` HOP hai nguon: z-score cau truc VA nhanh van ban cua cause head.
        #
        # Phep hop dat o DAY chu khong o `build_registry` la co chu dich: `Capabilities`
        # duoc truyen NGUYEN VEN cho ca MAS-DSS lan moi baseline, nen ca hai kien truc
        # nhan CUNG MOT doi tuong. Neu chi MAS duoc nguon hop nhat thi doi chung bi lam
        # yeu — va `test_baseline_parity.py` so sanh bang dinh danh doi tuong (`is`) se
        # bat duoc ngay.
        return Capabilities(
            risk_model=RiskModel(feature_set=feature_set).fit(r_train, r_val),
            ood=OODDetector().fit(r_train, numeric),
            delivery=CombinedDeliverySignal(structural=DeliverySignal().fit(train),
                                            head=head),
            price=PriceSignal().fit(train),
            cause_head=head,
            rules=RuleEngine.load(),
        )

    @staticmethod
    def load(models_dir=None) -> "Capabilities":
        """Nap mo hinh da huan luyen. Cac signal re duoc khop lai tu train."""
        return RiskModel.load(models_dir or CONFIG.paths.models)


def build_registry(capabilities: Capabilities, *, allow_refuse: bool = True) -> Registry:
    """Anh xa ten trong ke hoach -> tac tu. Orchestrator chi biet ten.

    `allow_refuse=False` la DUONG ABLATION CUA DP3: cam moi analyst phat REFUSE,
    buoc chung tra loi ke ca khi khong co bang chung. Khong phai che do van hanh —
    no ton tai de do cai gia cua viec bo quyen tu choi.
    """
    return Registry(
        agents={
            "Analytics": AnalyticsAgent(),
            "Prediction": PredictionAgent(capabilities.risk_model, capabilities.ood),
            "Recommendation": RecommendationAgent(capabilities.rules),
            "PolicyCritic": PolicyCriticAgent(capabilities.rules),
            "Arbiter": ArbiterAgent(capabilities.rules),
            "RuleAgent": RuleAgent(capabilities.rules),
            "CaseManager": CaseManagerAgent(),
        },
        pools={
            "AnalystPool": (
                DeliveryAnalyst(capabilities.delivery, allow_refuse=allow_refuse),
                QualityAnalyst(capabilities.cause_head, allow_refuse=allow_refuse),
                ServiceAnalyst(capabilities.cause_head, allow_refuse=allow_refuse),
            )
        },
    )


def reduce_reply(bb: Blackboard, step: str, reply: Message) -> None:
    """Ghi ket qua cua mot buoc vao blackboard.

    Cho DA NHAN duoc quyet dinh: moi bid vuot nguong tau deu vao `causes`. Khong co
    phep argmax nao o day, va do la co y — `idxmax` khi hoa diem thien vi theo thu
    tu bang chu cai, mot bug that trong ban v0.
    """
    content = reply.content

    if "context" in content:
        bb.context.update(content["context"])

    if "risk" in content:
        bb.risk = RiskLevel(int(content["risk"]))
        bb.risk_score = content.get("risk_score")

    if reply.performative is Performative.PROPOSE and "cause" in content:
        evidence = tuple(
            Evidence(kind=e["kind"], detail=e["detail"], value=e.get("value"))
            for e in content.get("evidence", [])
        )
        assignment = CauseAssignment(
            cause=Cause(content["cause"]),
            probability=float(content["confidence"]),
            evidence=evidence,
        )
        if assignment.probability >= CONFIG.tau_cause:
            bb.causes.append(assignment)
            bb.multi_cause = len({c.cause for c in bb.causes}) >= 2

    if "proposal" in content:
        bb.proposal = content["proposal"]

    if "challenged" in content:
        from masdss.core.ontology import Critique

        bb.critique = Critique(
            challenged=bool(content["challenged"]),
            violated_constraints=tuple(content.get("violated", [])),
        )

    if "override_action" in content:
        # Arbiter dung ve phia Critic -> ghi de hanh dong ung vien.
        bb.context["action"] = content["override_action"]
        bb.context["arbitration"] = content.get("decisive_constraint")

    if "action" in content:
        bb.context["action"] = content["action"]
        bb.context["rule_id"] = content.get("rule_id")
        bb.context["rule_enforced"] = content.get("enforced", False)


def build_decision(bb: Blackboard, conversation_id) -> Decision:
    """Chuyen blackboard thanh Decision.

    Ba bat bien cua DP1/DP3 duoc kiem tra ngay trong constructor cua `Decision`,
    nen ham nay khong the "quen" chung.
    """
    degraded = bb.degradation_level > 0
    risk = bb.risk if bb.risk is not None else RiskLevel.LOW
    action_name = str(bb.context.get("action", "no_action"))

    if degraded or bb.risk is None:
        action_name = "escalate_to_human"

    causes = tuple(bb.causes)
    at_t4 = bb.case.decision_point is DecisionPoint.T4
    if at_t4 and not causes:
        action_name = "escalate_to_human"

    # Arbiter da dung ve phia Critic thi hanh dong tu dong bi thu hoi.
    if bb.critique is not None and bb.critique.challenged and "arbitration" in bb.context:
        action_name = "escalate_to_human"

    return Decision(
        case_id=bb.case.case_id,
        decision_point=bb.case.decision_point,
        risk=risk,
        causes=causes,
        action=Action(name=action_name),
        degradation_level=bb.degradation_level,
        needs_human_review=(action_name == "escalate_to_human"),
        conversation_id=conversation_id,
        multi_cause=len({c.cause for c in causes}) >= 2,
        notes=tuple(bb.notes),
    )
