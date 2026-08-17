"""WP10 — Duong ablation cua DP4: do DO PHAN KY giua hai cach dung trace.

Phuc vu: RQ2 — o cot "cach do" cua thuoc tinh *truy vet duoc*, dong thu hai ghi
*"do phan ky giua trace dung tu nhat ky va trace viet tay"*. Truoc module nay, ta
chung minh duoc trace **dung lai duoc** tu nhat ky, nhung chua do duoc no **khac gi**
so voi cach viet tay — tuc chua kiem chung DP4, chi moi phat bieu no.

HAI CACH DUNG TRACE.

    Tu NHAT KY  — `Explainer.build(conversation_id)`. Doc moi message that su da
                  di qua he thong: ca ban khai bi tu choi, ca REFUSE, ca lan guard
                  can thiep, ca lan critic phan bac.

    VIET TAY    — cach mot ky su binh thuong se lam: doc `Decision` cuoi cung roi
                  ke lai *"he thong du bao rui ro X, quy ket nguyen nhan Y, de xuat
                  hanh dong Z"*. Day KHONG phai mot rom nhan tao — no la dang trace
                  ma phan lon he thong san xuat that su co.

VI SAO HAI CACH KHAC NHAU, va vi sao khac biet do quan trong.

    `Decision` chi giu KET CUC. Moi thu bi loai tren duong di deu bien mat: analyst
    nao da tu choi va vi sao, analyst nao thua thau vi qua dat, bid nao duoi nguong,
    guard nao da chan. Mot trace viet tay tu ket cuc vi vay khong the noi doi — no
    chi don gian KHONG CO cach bieu dien nhung su kien do.

    Do la noi dung thuc chat cua DP4: trace viet tay khong sai o nhung gi no noi,
    no thieu o nhung gi no khong the noi. Va o mot he ho tro quyet dinh, "vi sao
    KHONG chon Y" thuong dang gia ngang "vi sao chon X".

CHI SO. Ty le su kien co trong nhat ky ma trace viet tay khong bieu dien duoc.
Chia theo LOAI su kien, vi mot con so gop se giau mat loai nao bi mat.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from masdss.core.message import Message, Performative

# Su kien mot trace viet tay tu `Decision` KHONG the bieu dien, kem ten doc duoc.
INVISIBLE_EVENTS = {
    "refusal": "analyst tu choi — va ly do tu choi",
    "declaration": "ban khai nang luc o pha 1 Contract Net",
    "award": "ket qua phan bo ngan sach (ai thang, ai thua thau)",
    "critique": "phan bac cua critic",
    # `arbitration` bi bo sot khoi danh sach nay cho toi 14/08, va do la mot loi dem.
    # `handwritten_trace()` sinh dung bon dong — rui ro, nguyen nhan, hanh dong, muc
    # suy giam — nen no KHONG the noi rang da co mot lan phan xu, cung khong noi duoc
    # rang buoc nao la quyet dinh. Hanh dong cuoi cung co phan anh ket qua phan xu,
    # nhung "vi sao hanh dong tu dong bi thu hoi" thi mat han.
    "arbitration": "phan xu cua arbiter — va rang buoc nao la quyet dinh",
}
# Su kien trace viet tay bieu dien duoc, vi chung nam trong `Decision`.
VISIBLE_EVENTS = {"prediction", "bid", "proposal", "decision", "context", "cfp", "order_case"}


@dataclass(frozen=True)
class DivergenceReport:
    n_conversations: int
    n_log_events: int
    n_handwritten_events: int
    per_kind: pd.DataFrame

    @property
    def divergence_rate(self) -> float:
        """Ty le su kien that ma trace viet tay khong bieu dien duoc."""
        if not self.n_log_events:
            return 0.0
        return 1.0 - self.n_handwritten_events / self.n_log_events

    def describe(self) -> str:
        return (f"{self.n_conversations} hoi thoai · {self.n_log_events} su kien that · "
                f"{self.n_handwritten_events} bieu dien duoc · "
                f"do phan ky = {self.divergence_rate:.1%}")


def handwritten_trace(decision: dict) -> tuple[str, ...]:
    """Trace ma mot ky su se viet tay tu `Decision` cuoi cung.

    Khong doc nhat ky. Do chinh la diem cua bai kiem tra: dung lai duoc bao nhieu
    tu rieng ket cuc.
    """
    causes = decision.get("causes") or []
    names = [c["cause"] if isinstance(c, dict) else str(c) for c in causes]
    lines = [f"du bao rui ro = {decision.get('risk')}"]
    if names:
        lines.append(f"quy ket nguyen nhan: {', '.join(sorted(names))}")
    else:
        lines.append("khong quy ket duoc nguyen nhan nao")
    lines.append(f"de xuat hanh dong: {decision.get('action')}")
    if decision.get("degradation_level"):
        lines.append(f"muc suy giam = {decision['degradation_level']}")
    return tuple(lines)


def compare(out_dir: Path) -> DivergenceReport:
    """Doi chieu hai cach dung trace tren mot lan chay hoan chinh."""
    from masdss.runtime.message_log import MessageLog

    log = MessageLog(out_dir / "messages.sqlite")
    conversation_ids = log.conversation_ids()

    counts: Counter[str] = Counter()
    invisible: Counter[str] = Counter()
    for conversation_id in conversation_ids:
        for message in log.conversation(conversation_id):
            kind = _kind_of(message)
            counts[kind] += 1
            if kind in INVISIBLE_EVENTS:
                invisible[kind] += 1
    log.close()

    n_log = sum(counts.values())
    n_invisible = sum(invisible.values())

    rows = []
    for kind, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        rows.append({
            "loai_su_kien": kind,
            "so_lan_trong_nhat_ky": count,
            "viet_tay_bieu_dien_duoc": kind not in INVISIBLE_EVENTS,
            "y_nghia_bi_mat": INVISIBLE_EVENTS.get(kind, ""),
        })

    return DivergenceReport(
        n_conversations=len(conversation_ids),
        n_log_events=n_log,
        n_handwritten_events=n_log - n_invisible,
        per_kind=pd.DataFrame(rows),
    )


def _kind_of(message: Message) -> str:
    """Phan loai su kien. `REFUSE` uu tien hon `ontology` vi no la hanh vi."""
    if message.performative is Performative.REFUSE:
        return "refusal"
    if message.performative in (Performative.ACCEPT_PROPOSAL, Performative.REJECT_PROPOSAL):
        return "award"
    return message.ontology


def worked_example(out_dir: Path, index: int = 0) -> tuple[str, str]:
    """Mot vi du cu the de dua vao Chuong 5 — hai trace cua CUNG mot case."""
    from masdss.runtime.message_log import MessageLog
    from masdss.system.explain import Explainer

    decisions = [json.loads(line) for line in
                 (out_dir / "decisions.jsonl").read_text(encoding="utf-8").splitlines()]
    decision = decisions[index]

    log = MessageLog(out_dir / "messages.sqlite")
    trace = Explainer(log).build(decision["conversation_id"])
    log.close()
    return trace.render(), "\n".join(handwritten_trace(decision))
