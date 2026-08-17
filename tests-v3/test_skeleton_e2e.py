"""WP6 — Tieu chi ra: he thong chay end-to-end tren du lieu Olist that.

Nam dieu kien o implementation-plan.md §4, moi dieu kien mot test:
  1. Moi case di tron chuoi va sinh ra Decision hop le.
  2. Trace dung lai duoc CHI tu conversation_id (DP4).
  3. Tiem duoc loi crash MA KHONG sua dong nao trong system/ hay agents/.
  4. Tiem duoc loi Byzantine, cung dieu kien nhu tren.
  5. Nhat ky message la append-only.

Day la ban day du cua Gate G4 va G5 (build-plan.md §8) — khac ban thu nho o Dot 0
o cho no chay tren du lieu that voi capability that.
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
from pathlib import Path

import pytest

from masdss.cli.run_system import run
from masdss.config import deterministic_uuid
from masdss.core.message import Performative
from masdss.runtime.message_log import MessageLog
from masdss.system.explain import Explainer

from conftest import N_CASES


def _decisions(out_dir: Path) -> list[dict]:
    return [json.loads(line) for line in
            (out_dir / "decisions.jsonl").read_text(encoding="utf-8").splitlines()]


def _first_conversation(out_dir: Path):
    return deterministic_uuid("conv", _decisions(out_dir)[0]["case_id"])


# --- 1. Moi case di tron chuoi ---

def test_every_case_produces_a_decision(normal_run: Path) -> None:
    rows = _decisions(normal_run)
    assert len(rows) == N_CASES
    assert all(r["degradation_level"] == 0 for r in rows)
    assert all("action" in r for r in rows)


def test_decisions_respect_dp1_invariant(normal_run: Path) -> None:
    """Bat bien duoc kiem tra trong constructor, nhung van xac nhan tren dau ra that."""
    for row in _decisions(normal_run):
        if row["degradation_level"] > 0 or row["action"] == "escalate_to_human":
            assert row["needs_human_review"]


def test_unattributed_cases_are_escalated(normal_run: Path) -> None:
    """DP3 tai T4: khong quy ket duoc thi chuyen giao, khong doan bua."""
    for row in _decisions(normal_run):
        if not row["causes"]:
            assert row["action"] == "escalate_to_human"


# --- 2. DP4: trace dung lai duoc chi tu conversation_id ---

def test_trace_is_rebuilt_from_log_alone(normal_run: Path) -> None:
    log = MessageLog(normal_run / "messages.sqlite")
    trace = Explainer(log).build(_first_conversation(normal_run))
    log.close()
    assert trace.nodes, "trace rong"
    senders = {n.sender for n in trace.nodes}
    assert {"Orchestrator", "Analytics", "Prediction", "RuleAgent"} <= senders


def test_trace_contains_the_bidding_session(normal_run: Path) -> None:
    """Phien dau thau phai nhin thay duoc trong nhat ky — bang chung cho RQ3."""
    log = MessageLog(normal_run / "messages.sqlite")
    conversations = [Explainer(log).build(c) for c in log.conversation_ids()]
    log.close()

    performatives = {n.performative for t in conversations for n in t.nodes}
    assert Performative.PROPOSE in performatives, "khong analyst nao dau thau"
    assert Performative.REFUSE in performatives, "khong analyst nao tu choi"


def test_explainer_build_accepts_only_conversation_id() -> None:
    """Rang buoc chu ky ham CHINH LA DP4."""
    import inspect

    params = list(inspect.signature(Explainer.build).parameters)
    assert params == ["self", "conversation_id"], (
        f"Explainer.build khong duoc nhan them tham so nao: {params}"
    )


# --- 3 & 4. Seam tiem loi dat dung cho ---

def test_crash_injection_degrades_transparently(tmp_path: Path, fixtures) -> None:
    """Prediction chet -> he SUY GIAM MINH BACH, khong hong am tham."""
    orders, caps = fixtures
    asyncio.run(run(tmp_path / "crash", n_cases=N_CASES, inject="crash:Prediction",
                    orders=orders, capabilities=caps))
    rows = _decisions(tmp_path / "crash")
    assert all(r["degradation_level"] > 0 for r in rows)
    assert all(r["needs_human_review"] for r in rows)
    assert all(r["action"] == "escalate_to_human" for r in rows)


def test_byzantine_injection_passes_through_seam(tmp_path: Path, fixtures) -> None:
    """Loi Byzantine: ket qua HOP LE nhung sai — khong exception, khong log do.

    He thong hien CHUA co output guard nen no khong phat hien duoc. Test nay chi
    chung minh seam tiem duoc loai loi nay; viec phat hien thuoc WP8 / T8.1.
    """
    orders, caps = fixtures
    asyncio.run(run(tmp_path / "byz", n_cases=N_CASES, inject="constant:Prediction:risk",
                    orders=orders, capabilities=caps))
    rows = _decisions(tmp_path / "byz")
    assert all(r["degradation_level"] == 0 for r in rows), "khong exception -> chua suy giam"
    assert len({r["risk"] for r in rows}) == 1, "moi case bi ep ve cung mot muc rui ro"


def test_injection_requires_no_change_to_system_or_agents() -> None:
    """Tang nghiep vu khong duoc IMPORT chaos."""
    import ast

    src = Path(__file__).resolve().parents[1] / "src-v3" / "masdss"
    offenders: list[str] = []
    for folder in ("system", "agents"):
        for file in (src / folder).rglob("*.py"):
            tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                else:
                    continue
                if any(n.startswith("masdss.chaos") for n in names):
                    offenders.append(f"{file.relative_to(src)}:{node.lineno}")
    assert not offenders, f"seam bi ro ri vao tang nghiep vu: {offenders}"


# --- 5. Nhat ky append-only ---

def test_message_log_rejects_update_and_delete(normal_run: Path) -> None:
    conn = sqlite3.connect(normal_run / "messages.sqlite")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE messages SET sender = 'x'")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM messages")
    conn.close()


def test_payload_is_never_written_to_log(normal_run: Path) -> None:
    """`payload` la tham chieu trong tien trinh, khong duoc ro ri vao nhat ky."""
    log = MessageLog(normal_run / "messages.sqlite")
    messages = log.conversation(_first_conversation(normal_run))
    log.close()
    assert messages
    assert all(m.payload is None for m in messages)
    assert any(m.performative is Performative.INFORM for m in messages)
