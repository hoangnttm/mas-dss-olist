"""WP4 / T4.3 — Monolithic-Complete.  [Artifact A6]

Phuc vu: RQ3, RQ1. **Khong co baseline nay thi ca Chuong 5 mat gia tri.**

NGUYEN TAC XAY DUNG — phai cong bang, neu khong lai la bu nhin lan hai:

| Dung chung voi MAS-DSS          | Khong co                          |
|---------------------------------|-----------------------------------|
| CUNG doi tuong risk_model       | Message passing                   |
| CUNG doi tuong cause_head       | Contract Net, ngan sach tinh toan |
| CUNG doi tuong delivery/price   | Blackboard                        |
| CUNG tap luat YAML              | Supervisor, circuit breaker, guard |
| CUNG feature set, cung split    | Thang suy giam, quyen REFUSE      |

HAI DIEM PHAI GIU DUNG, va chung keo theo nhau:

  1. DA NHAN, khong argmax. Neu doi chung bi chan khong cho tra ve nhieu nhan thi
     MAS-DSS thang o tinh huong (a) cua RQ3 THEO CAU TAO — dung loi baseline bu
     nhin ma nghien cuu da cam ket tranh. Doi chung dung CUNG nguong tau.

  2. Viet theo cach TU NHIEN NHAT ma mot ky su gioi se viet: mot quy trinh tuan
     tu, gap exception thi ghi log roi di tiep. KHONG co tang chiu loi. Chinh vi
     khong co tinh lam cho no hong nen ty le hong am tham cua no la KET QUA THUC
     NGHIEM THAT, khong phai dan dung.

Diem thu hai la ly do file nay trong "cau tha" so voi phan con lai cua codebase.
Do la co y: no dai dien cho mot kien truc doi chung, khong phai cho tieu chuan ky
thuat cua nghien cuu.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from masdss.capabilities.rules import facts_from
from masdss.core.components import Component
from masdss.config import CONFIG
from masdss.core.ontology import Cause, OrderCase
from masdss.runtime.faults import guard_call

logger = logging.getLogger("monolithic")

ALL_CAUSES = (Cause.DELIVERY, Cause.QUALITY, Cause.SERVICE)

# Moi nguyen nhan ung voi mot THANH PHAN LOGIC — cung ten ma MAS-DSS dung, nen mot
# kich ban loi ap duoc len ca hai kien truc (T9.3).
CAUSE_COMPONENT = {
    Cause.DELIVERY: Component.CAUSE_DELIVERY.value,
    Cause.QUALITY: Component.CAUSE_QUALITY.value,
    Cause.SERVICE: Component.CAUSE_SERVICE.value,
}


@dataclass
class MonolithicResult:
    case_id: str
    risk: int
    causes: list[str]
    action: str
    failed_steps: list[str]
    # Do tin cay cua nhung nguyen nhan DA PHAT. Giu lai vi duong risk-coverage
    # (T10.3) can xep hang case theo do tin cay cua CHINH he thong do — MAS-DSS von
    # da ghi `probability` trong `decisions.jsonl`, nen neu doi chung khong ghi thi
    # hai he khong so sanh duoc o cung muc do phu. Do la mot dieu kien cong bang,
    # khong phai mot truong tien ich.
    confidences: dict[str, float] | None = None

    def to_row(self) -> dict:
        return {
            "case_id": self.case_id,
            "risk": self.risk,
            "causes": sorted(self.causes),
            "action": self.action,
            # Khong co truong `degradation_level`: kien truc nay khong co khai niem do.
            # Do chinh la thu RQ1 do luong.
            "failed_steps": self.failed_steps,
            "confidences": {k: round(float(v), 6)
                            for k, v in sorted((self.confidences or {}).items())},
        }


class MonolithicComplete:
    """Quy trinh tuan tu day du chuc nang, khong co tang chiu loi."""

    name = "monolithic_complete"

    def __init__(self, capabilities, injector=None) -> None:
        # CUNG doi tuong voi MAS-DSS — khong tao ban sao, khong huan luyen lai.
        self.risk_model = capabilities.risk_model
        self.delivery = capabilities.delivery
        self.price = capabilities.price
        self.cause_head = capabilities.cause_head
        self.rules = capabilities.rules
        # Bo tiem loi chi de CHIU loi, khong de xu ly loi. Kien truc nay van khong
        # co guard, khong co thang suy giam, khong co truong nao bao he dang hong.
        self.injector = injector

    def run(self, case: OrderCase) -> MonolithicResult:
        failed: list[str] = []

        # --- buoc 1: du bao rui ro ---
        risk = 0
        try:
            score = guard_call(Component.PREDICTION.value, self.risk_model.run, case,
                               injector=self.injector)
            risk = int(self.risk_model.to_risk_level(score))
        except Exception as exc:  # noqa: BLE001 — cach mot ky su binh thuong se viet
            logger.warning("prediction that bai cho %s: %s", case.case_id, exc)
            failed.append("prediction")

        # --- buoc 2: quy ket nguyen nhan, DA NHAN, cung nguong tau ---
        causes: list[str] = []
        confidences: dict[str, float] = {}
        for cause in ALL_CAUSES:
            try:
                confidence = self._score_cause(case, cause)
            except Exception as exc:  # noqa: BLE001
                logger.warning("quy ket %s that bai cho %s: %s", cause.value, case.case_id, exc)
                failed.append(f"cause_{cause.value}")
                continue
            if confidence >= CONFIG.tau_cause:
                causes.append(cause.value)
                confidences[cause.value] = float(confidence)

        # --- buoc 3: chot hanh dong bang CUNG tap luat YAML ---
        action = "no_action"
        try:
            guard_call(Component.RULES.value, lambda: None, injector=self.injector)
            facts = facts_from(
                risk=risk,
                causes=causes,
                degradation_level=0,  # kien truc nay khong theo doi suy giam
                decision_point=case.decision_point.value,
            )
            action = self.rules.decide(facts).action
        except Exception as exc:  # noqa: BLE001
            logger.warning("rule engine that bai cho %s: %s", case.case_id, exc)
            failed.append("rules")

        return MonolithicResult(
            case_id=case.case_id, risk=risk, causes=causes,
            action=action, failed_steps=failed, confidences=confidences,
        )

    def _score_cause(self, case: OrderCase, cause: Cause) -> float:
        component = CAUSE_COMPONENT[cause]
        if cause is Cause.DELIVERY:
            result = guard_call(component, self.delivery.run, case, injector=self.injector)
        else:
            result = guard_call(component, self.cause_head.score, case, cause,
                                injector=self.injector)
        return result[0] if isinstance(result, tuple) else float(result)


def is_silent_failure(result: MonolithicResult) -> bool:
    """Hong am tham: co buoc that bai nhung ket qua van duoc dua ra binh thuong.

    Day la chi so trung tam cua RQ1 ve (a). Voi kien truc nay, moi that bai deu am
    tham theo dinh nghia: khong co truong nao trong dau ra bao cho nguoi dung biet
    rang mot phan he thong da hong.
    """
    return bool(result.failed_steps) and result.action != "escalate_to_human"
