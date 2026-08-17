"""WP0 / T5.4 — Phan loai loi: transient hay deterministic.

Phuc vu: RQ1 (chinh sach retry co y nghia).

Day khong phai chi tiet cai dat. Bang v0 retry cung batch, cung input, tren model
tat dinh — loi lap lai y het ba lan roi bi bo qua. Chinh sach dung:

  - Loi TRANSIENT (I/O, tranh chap tai nguyen): retry co backoff va jitter.
  - Loi DETERMINISTIC (model chet, schema sai): KHONG retry — thu ba lan cung chet
    ba lan. Di thang xuong thang suy giam.
"""

from __future__ import annotations


class MasDssError(Exception):
    """Goc cua moi loi trong he thong."""


class TransientError(MasDssError):
    """Loi nhat thoi — dang retry."""


class DeterministicError(MasDssError):
    """Loi tat dinh — retry vo nghia, phai xuong thang suy giam."""


class AgentTimeout(TransientError):
    """Tac tu khong tra loi truoc han chot. Task da bi HUY, khong phai do sau khi xong."""


class CapabilityUnavailable(DeterministicError):
    """Nang luc nen khong dung duoc: model chua nap, tep trong so hong."""


class OntologyMismatch(DeterministicError):
    """Payload sai ontology — tuong ung performative NOT_UNDERSTOOD."""


class GuardViolation(DeterministicError):
    """Output guard chan mot ket qua hop le ve kieu nhung sai ve chat."""


class WeakLabelInEvaluation(MasDssError):
    """Truyen weak label vao ham danh gia quy ket nguyen nhan.

    Rang buoc C2: moi con so ve quy ket nguyen nhan phai do tren gold set do nguoi
    gan. Loi nay la cach CUONG CHE trong ma nguon, khong pho mac ky luat ca nhan.
    """
