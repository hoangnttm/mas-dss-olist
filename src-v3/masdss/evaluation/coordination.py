"""WP10 / T10.4 — Chi so phoi hop.

Phuc vu: RQ3 — day la nhom chi so ma MIS va Single-ML KHONG DU TU CACH tham gia,
vi chung khong co khai niem phoi hop nao ca.

MOI CHI SO O DAY TINH TU NHAT KY MESSAGE, khong do them gi. Do la he qua truc tiep
cua DP4: neu nhat ky du de dung lai decision trace, no cung du de do phoi hop. Neu
phai cai them mot duong do rieng thi nhat ky da khong day du, va DP4 co van de.

HAI NHOM CHI SO, va phai bao cao ca hai:

    CAI GIA  — so message/case, do sau cay hoi thoai, chi phi dieu phoi (ms)
    LOI ICH  — ty le di duong tat, bid_entropy, ty le REFUSE co can cu

Bao cao mot ve ma giau ve kia la khong trung thuc. Phoi hop da tac tu KHONG mien phi,
va con so chi phi lam cho phan loi ich dang tin hon nhieu.

`bid_entropy` la chi so rieng cua co che canh tranh: entropy cao nghia la nhieu
analyst cung tu tin ngang nhau, tuc don co NHIEU NGUYEN NHAN dong thoi — dung tinh
huong (a) cua RQ3 ma mot bo phan loai don khoi lam mat thong tin bang phep argmax.
"""

from __future__ import annotations

import json
import math
import sqlite3
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from masdss.core.message import Message, Performative
from masdss.runtime.message_log import MessageLog


@dataclass(frozen=True)
class ConversationStats:
    conversation_id: str
    n_messages: int
    depth: int
    n_declarations: int
    n_bids: int
    n_refusals: int
    bid_entropy: float
    causes: tuple[str, ...]

    @property
    def multi_cause(self) -> bool:
        return len(set(self.causes)) >= 2


def _depth(messages: list[Message]) -> int:
    """Do sau cay hoi thoai — dung `in_reply_to` de dung lai quan he cha con."""
    depth_of: dict[str, int] = {}
    deepest = 0
    for message in messages:
        parent = str(message.in_reply_to) if message.in_reply_to else None
        depth = depth_of.get(parent, -1) + 1 if parent else 0
        depth_of[str(message.msg_id)] = depth
        deepest = max(deepest, depth)
    return deepest


def bid_entropy(confidences: list[float]) -> float:
    """Entropy chuan hoa cua phan bo do tin cay giua cac analyst.

    0 nghia la mot analyst ap dao — nguyen nhan don. Tien ve 1 nghia la nhieu analyst
    tu tin ngang nhau — DA NGUYEN NHAN, va do la thong tin ma `argmax` xoa mat.

    Chuan hoa theo log(k) de so sanh duoc giua cac case co so luong bid khac nhau.
    """
    values = [c for c in confidences if c > 0]
    if len(values) < 2:
        return 0.0
    total = sum(values)
    probabilities = [v / total for v in values]
    entropy = -sum(p * math.log(p) for p in probabilities)
    return entropy / math.log(len(values))


def conversation_stats(messages: list[Message]) -> ConversationStats:
    confidences: list[float] = []
    causes: list[str] = []
    declarations = bids = refusals = 0

    for message in messages:
        if message.ontology == "declaration":
            declarations += 1
        elif message.ontology == "bid":
            bids += 1
            confidences.append(float(message.content.get("confidence", 0.0)))
            causes.append(str(message.content.get("cause", "")))
        if message.performative is Performative.REFUSE:
            refusals += 1

    return ConversationStats(
        conversation_id=str(messages[0].conversation_id) if messages else "",
        n_messages=len(messages),
        depth=_depth(messages),
        n_declarations=declarations,
        n_bids=bids,
        n_refusals=refusals,
        bid_entropy=round(bid_entropy(confidences), 4),
        causes=tuple(causes),
    )


def coordination_overhead_ms(out_dir: Path) -> dict:
    """Chi phi dieu phoi: tong thoi gian cua cac span, tach theo buoc.

    Day la CAI GIA cua phoi hop da tac tu. No khong tat dinh (co dong ho) nen khong
    dung de so sanh giua hai lan chay, chi dung de bao cao do lon.
    """
    path = out_dir / "spans.sqlite"
    if not path.exists():
        return {}
    conn = sqlite3.connect(path)
    rows = conn.execute(
        "SELECT name, COUNT(*), SUM(duration_ms) FROM spans GROUP BY name"
    ).fetchall()
    total = conn.execute("SELECT SUM(duration_ms) FROM spans").fetchone()[0] or 0.0
    conn.close()
    return {
        "total_ms": round(float(total), 2),
        "by_step": {name: {"n": int(n), "ms": round(float(ms), 2)} for name, n, ms in rows},
    }


def report(out_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Bang chi so phoi hop + bang chi tiet theo case."""
    log = MessageLog(out_dir / "messages.sqlite")
    stats = [conversation_stats(log.conversation(cid)) for cid in log.conversation_ids()]
    log.close()

    decisions = [json.loads(line) for line in
                 (out_dir / "decisions.jsonl").read_text(encoding="utf-8").splitlines()]
    n = len(stats) or 1

    shortcut = sum(1 for d in decisions if d["action"] == "no_action")
    unattributed = sum(1 for d in decisions if not d["causes"])
    multi = sum(1 for s in stats if s.multi_cause)
    overhead = coordination_overhead_ms(out_dir)

    summary = pd.DataFrame([
        # --- CAI GIA cua phoi hop ---
        {"nhom": "cai gia", "chi_so": "message / case",
         "gia_tri": round(sum(s.n_messages for s in stats) / n, 2)},
        {"nhom": "cai gia", "chi_so": "do sau cay hoi thoai (TB)",
         "gia_tri": round(sum(s.depth for s in stats) / n, 2)},
        {"nhom": "cai gia", "chi_so": "chi phi dieu phoi tong (ms)",
         "gia_tri": overhead.get("total_ms", 0.0)},
        {"nhom": "cai gia", "chi_so": "chi phi dieu phoi / case (ms)",
         "gia_tri": round(overhead.get("total_ms", 0.0) / n, 3)},
        # --- LOI ICH cua phoi hop ---
        {"nhom": "loi ich", "chi_so": "ban khai / case (pha 1 CNP)",
         "gia_tri": round(sum(s.n_declarations for s in stats) / n, 2)},
        {"nhom": "loi ich", "chi_so": "bid that / case (pha 2 CNP)",
         "gia_tri": round(sum(s.n_bids for s in stats) / n, 2)},
        {"nhom": "loi ich", "chi_so": "REFUSE / case",
         "gia_tri": round(sum(s.n_refusals for s in stats) / n, 2)},
        {"nhom": "loi ich", "chi_so": "bid_entropy TB (chi case co >=2 bid)",
         "gia_tri": round(
             sum(s.bid_entropy for s in stats if s.n_bids >= 2)
             / max(sum(1 for s in stats if s.n_bids >= 2), 1), 4)},
        {"nhom": "loi ich", "chi_so": "ty le da nguyen nhan",
         "gia_tri": round(multi / n, 4)},
        {"nhom": "loi ich", "chi_so": "ty le di duong tat (no_action)",
         "gia_tri": round(shortcut / max(len(decisions), 1), 4)},
        {"nhom": "loi ich", "chi_so": "ty le khong quy ket duoc",
         "gia_tri": round(unattributed / max(len(decisions), 1), 4)},
    ])

    detail = pd.DataFrame([
        {"conversation_id": s.conversation_id, "n_messages": s.n_messages,
         "depth": s.depth, "n_declarations": s.n_declarations, "n_bids": s.n_bids,
         "n_refusals": s.n_refusals, "bid_entropy": s.bid_entropy,
         "multi_cause": s.multi_cause, "causes": ",".join(s.causes)}
        for s in stats
    ])
    return summary, detail


def attribution_per_ms(out_dir: Path) -> dict:
    """Chi so rieng cua Contract Net co ngan sach: quy ket dat duoc tren moi ms.

    CANH BAO PHAI DOC. "Chat luong quy ket" dung nghia phai do tren GOLD SET, va gold
    set chua san sang. Con so o day dung SO NGUYEN NHAN TIM DUOC lam bien thay the —
    no do NANG SUAT, khong do DO DUNG. Mot he thong quy ket bua tat ca se an diem cao
    o chi so nay.

    Chi duoc thay bang chi so that sau khi T3.4 va T10.2 hoan thanh.
    """
    log = MessageLog(out_dir / "messages.sqlite")
    stats = [conversation_stats(log.conversation(cid)) for cid in log.conversation_ids()]
    log.close()
    overhead = coordination_overhead_ms(out_dir)
    total_ms = overhead.get("total_ms", 0.0) or 1.0
    causes = sum(len(set(s.causes)) for s in stats)
    return {
        "causes_found": causes,
        "total_ms": round(total_ms, 2),
        "causes_per_ms": round(causes / total_ms, 4),
        "caveat": ("Bien thay the: dem SO nguyen nhan, khong do DO DUNG. Chi so DO DUNG "
                   "nam o `run_attribution` (T10.2) va mang theo co `citable`. "
                   "Khong duoc trich con so nay vao Chuong 5."),
    }
