"""WP0 / T0.2 — Cau hinh tap trung va seed toan cuc.

Phuc vu: ca ba RQ (dieu kien cua tinh tai lap).

Hai quy tac bat buoc (technical-plan-v3.md §8):
  - Moi nguon ngau nhien nhan seed tu day, khong tu khoi tao.
  - Khong dung dong ho he thong trong logic nghiep vu; moi moc thoi gian lay tu
    du lieu. Tracing co dung perf_counter nhung ket qua do KHONG nam trong tep
    dau ra chinh tac (xem runtime/tracing.py).
"""

from __future__ import annotations

import os
import random
import uuid
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Namespace de sinh UUID TAT DINH. uuid4() bi cam trong toan bo codebase vi no
# pha tinh tai lap — dung uuid5 tren namespace nay thay the.
UUID_NAMESPACE = uuid.UUID("6f1d2a4e-0000-5000-8000-000000000001")


@dataclass(frozen=True)
class Paths:
    """Duong dan. Dau ra v3 tach hoan toan khoi artifact cu."""

    raw: Path = ROOT / "data" / "raw"
    derived: Path = ROOT / "data" / "v3"
    models: Path = ROOT / "models" / "v3"
    conf: Path = ROOT / "config" / "v3"
    runs: Path = ROOT / "data" / "v3" / "runs"

    def ensure(self) -> None:
        for p in (self.derived, self.models, self.runs):
            p.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Config:
    seed: int = 20260809
    paths: Paths = field(default_factory=Paths)

    # Nguong quy ket nguyen nhan; giu moi bid vuot nguong nay (da nhan, khong argmax)
    tau_cause: float = 0.35
    # Han chot mac dinh cho mot loi goi tac tu, tinh bang mili giay (KHONG phai
    # dau thoi gian tuyet doi — dung thoi luong de giu tinh tat dinh)
    default_deadline_ms: float = 5_000.0

    # Moc quyet dinh T3 = NGAY MUA + so ngay nay.
    #
    # T3 la MOT MOC THOI GIAN, khong phai su kien "da giao xong". Dinh nghia theo su
    # kien khien nhung don chua toi khong co T3, va do dung la nhom co ty le bat man
    # cao nhat (xem L30).
    #
    # NEO VAO NGAY MUA, KHONG NEO VAO HAN GIAO DU KIEN. Cach neo cu (`han du kien + 3`)
    # dat T3 SAU T4 voi 97,6% so don — tuc "du bao" chay sau chinh ket cuc no du bao.
    # Ly do: 87,8% danh gia duoc viet TRUOC han du kien, va trung vi chi 6,2 gio sau
    # luc giao. Han du kien khong phai mot moc kha dung de ra quyet dinh phuc hoi.
    # Xem L33 va rang buoc C3.
    #
    # Chon 7 ngay theo phep DANH DOI giua do phu va cuong do tin hieu. So do lai tren
    # TOAN DAI (Chuong 3, Bang 3.5) — bang nay THAY cho bang cu o day:
    #
    #   moc      tong the   do phu don bat man   ty le nen   lift nhom chua ban giao
    #   +3        95.087           98,1%           14,93%            1,32
    #   +5        87.166           94,0%           15,61%            1,67
    #   +7        75.480           87,4%           16,77%            2,12   <- chon
    #   +10       54.717           75,4%           19,96%            2,39   <- lift dinh
    #   +14       34.163           61,5%           26,04%            2,36
    #   +21       14.576           41,5%           41,25%            1,86
    #
    # MOC +7 KHONG PHAI MOC CHO TIN HIEU MANH NHAT, va bang tren noi ro dieu do. Lift
    # con tang toi +10 (2,39) roi moi giam. Ban cu cua chu thich nay ghi "+7 · lift
    # 2,19 · dat dinh" va "+10 · lift 2,11" — SAI CA HAI VE khi do lai toan dai; do
    # chinh la loi L35, va no da song sot trong ma nguon sau khi Chuong 3 sua.
    #
    # Chon +7 vi no CAN BANG: day sang +10 mua them 0,27 don vi lift nhung danh mat
    # 12 diem phan tram do phu, tuong duong ~1.700 don bat man khong con kip can thiep.
    # Voi mot he thong phuc hoi dich vu, so don tiep can duoc mang y nghia nghiep vu
    # truc tiep; mot thu hang tot hon tren mot tong the da bi thu hep khong bu lai duoc.
    #
    # Moc +10 duoc giu lai lam phan tich do nhay (Chuong 5 §5.11).
    t3_cutoff_days: int = 7

    def seed_everything(self) -> None:
        """Gan seed cho moi nguon ngau nhien dang co mat."""
        random.seed(self.seed)
        os.environ["PYTHONHASHSEED"] = str(self.seed)
        try:  # numpy co the chua duoc cai o Dot 0
            import numpy as np

            np.random.seed(self.seed)
        except ImportError:  # pragma: no cover
            pass


CONFIG = Config()


def deterministic_uuid(*parts: object) -> uuid.UUID:
    """Sinh UUID tat dinh tu cac thanh phan dinh danh.

    Thay the cho uuid4(): cung dau vao luon cho cung dinh danh, nen hai lan chay
    cung cau hinh sinh ra cung tep dau ra.
    """
    return uuid.uuid5(UUID_NAMESPACE, "|".join(str(p) for p in parts))
