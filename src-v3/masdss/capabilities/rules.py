"""WP3 / T3.6 — Rule engine doc YAML.

Phuc vu: RQ2 (chot hanh dong), RQ1 (cuong che DP1).

DUNG CHUNG giua MAS-DSS va Monolithic-Complete: ca hai nap dung tep YAML nay. Do
la mot trong cac dieu kien de phep so sanh cua RQ3/RQ1 khong phai so voi baseline
bi lam yeu.

HAI TANG LUAT, va thu tu giua chung la co che chu khong phai quy uoc:

  enforced -> kiem tra TRUOC, khong the bi ghi de. Day la noi DP1 va DP3 song.
  rules    -> luat nghiep vu, danh gia theo thu tu, luat dau tien khop se thang.

Bieu thuc dieu kien duoc danh gia bang mot bo INTERPRETER TOI GIAN, khong dung
`eval()`. Ly do: `eval` tren chuoi lay tu tep cau hinh la mot duong thuc thi ma
tuy y, va no cung lam ket qua phu thuoc vao trang thai Python luc chay — pha tinh
tai lap.
"""

from __future__ import annotations

import operator
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from masdss.config import CONFIG

_COMPARATORS = {
    ">=": operator.ge, "<=": operator.le, "==": operator.eq,
    "!=": operator.ne, ">": operator.gt, "<": operator.lt,
}
_TOKEN = re.compile(r'^\s*(\w+)\s*(>=|<=|==|!=|>|<)\s*("?[\w.\-]+"?)\s*$')


@dataclass(frozen=True)
class Rule:
    id: str
    when: str
    action: str
    reason: str
    enforced: bool = False


@dataclass(frozen=True)
class RuleOutcome:
    action: str
    rule_id: str
    reason: str
    enforced: bool


@dataclass
class RuleEngine:
    """Nap va ap tap luat. Deterministic, khong co nguon ngau nhien nao."""

    enforced: tuple[Rule, ...] = ()
    rules: tuple[Rule, ...] = ()
    actions: dict[str, dict] = field(default_factory=dict)
    constraints: tuple[dict, ...] = ()
    arbitration_priority: tuple[str, ...] = ()
    default_action: str = "preemptive_ticket_open"

    name: str = "rule_engine"
    cost_ms: float = 0.05

    @staticmethod
    def load(path: Path | None = None) -> "RuleEngine":
        target = path or (CONFIG.paths.conf / "rules.yaml")
        spec = yaml.safe_load(Path(target).read_text(encoding="utf-8"))

        if "expedite_shipment" in spec.get("actions", {}):
            raise ValueError(
                "`expedite_shipment` bat kha thi ve mat thoi gian tai T3/T4 — da bi loai"
            )

        return RuleEngine(
            enforced=tuple(Rule(**r, enforced=True) for r in spec.get("enforced", [])),
            rules=tuple(Rule(**r) for r in spec.get("rules", [])),
            actions=spec.get("actions", {}),
            constraints=tuple(spec.get("constraints", [])),
            arbitration_priority=tuple(spec.get("arbitration_priority", [])),
            default_action=spec.get("default_action", "preemptive_ticket_open"),
        )

    # --- danh gia bieu thuc, khong dung eval() ---

    def _evaluate(self, expression: str, facts: dict) -> bool:
        clauses = [c.strip() for c in expression.split(" and ")]
        return all(self._clause(c, facts) for c in clauses)

    def _clause(self, clause: str, facts: dict) -> bool:
        match = _TOKEN.match(clause)
        if match:
            name, symbol, raw = match.groups()
            left = facts.get(name)
            right = self._literal(raw)
            if left is None:
                return False
            return bool(_COMPARATORS[symbol](left, right))
        # Menh de boolean tran, vi du `multi_cause` hoac `has_cause_quality`
        return bool(facts.get(clause.strip(), False))

    @staticmethod
    def _literal(raw: str):
        text = raw.strip('"')
        try:
            return int(text)
        except ValueError:
            pass
        try:
            return float(text)
        except ValueError:
            return text

    # --- ap luat ---

    def decide(self, facts: dict) -> RuleOutcome:
        """Tra ve hanh dong. Luat cuong che luon duoc xet truoc."""
        for rule in self.enforced:
            if self._evaluate(rule.when, facts):
                return RuleOutcome(rule.action, rule.id, rule.reason.strip(), enforced=True)

        for rule in self.rules:
            if self._evaluate(rule.when, facts):
                return RuleOutcome(rule.action, rule.id, rule.reason.strip(), enforced=False)

        return RuleOutcome(self.default_action, "default", "khong luat nao khop", False)

    def cost_of(self, action: str) -> float:
        return float(self.actions.get(action, {}).get("cost", 0.0))


def facts_from(*, risk: int, causes: list[str], degradation_level: int,
               decision_point: str, seller_flagged: bool = False,
               context: dict | None = None) -> dict:
    """Chuyen trang thai case thanh tap su kien cho rule engine.

    Tach ham nay ra de Monolithic-Complete dung DUNG bo su kien nay — neu hai he
    xay su kien khac nhau thi phep so sanh khong con cong bang.

    `context` la bo chi bao do Analytics sinh ra. Cac su kien cua GIAI DOAN 1 den tu
    day, va chung duoc dua vao o dang GIA TRI THO chu khong phai co dan xuat:

        days_to_deadline · delivery_state · order_value · is_late

    Vi sao tho chu khong phai `qua_han` / `sap_qua_han`: nguong nam trong CHINH luat
    o `rules.yaml`, canh chi phi hanh dong ma no phuc vu. Bien nguong thanh mot co
    boolean o day se giau tham so trong ma nguon, dung cho ma khong ai doc no.

    Gia tri thieu duoc BO HAN thay vi dat 0: `_clause` tra False khi su kien vang
    mat, nen luat khoa theo no se khong khop — dung hon la dat 0 roi vo tinh thoa
    mot phep so sanh `< 0`.
    """
    distinct = {c for c in causes if c != "unknown"}
    facts = {
        "risk": int(risk),
        "n_causes": len(distinct),
        "multi_cause": len(distinct) >= 2,
        "degradation_level": int(degradation_level),
        "decision_point": decision_point,
        "seller_flagged": bool(seller_flagged),
        **{f"has_cause_{c}": True for c in distinct},
    }
    for ten in ("days_to_deadline", "delivery_state", "order_value"):
        gia_tri = (context or {}).get(ten)
        if gia_tri is not None:
            facts[ten] = float(gia_tri)
    if (context or {}).get("is_late"):
        facts["is_late"] = True
    return facts
