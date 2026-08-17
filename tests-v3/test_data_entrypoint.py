"""WP1 / T1.7 — `load_split()` la DUONG VAO DUY NHAT cho mo hinh.

Phuc vu: RQ1, RQ3 (moi con so ve du bao va quy ket deu doc qua day).

VAN DE MA TEP TEST NAY CHAN.

    `data/export.py` tach du lieu thanh chin tep vat ly co luoc do roi nhau, ap
    khoang cach ly, va loc tong the ve nhung don CON KIP CAN THIEP tai T3. Ba co
    che do chi co gia tri neu he thong THUC SU nap qua chung.

    Ngay 13/08 phat hien: tang do da duoc xay day du nhung GAN NHU KHONG GI DUNG
    no. Sau diem chay van goi `build_order_table()` roi `time_split()` truc tiep —
    dung mau ma chinh docstring cua `export.py` mo ta la nguyen nhan cua L30 va
    L33. Do duoc tren duong cu:

        2.211 dong val co danh gia den SAU `test_start`, va isotonic duoc khop
        tren chinh tap val do  ->  bo hieu chuan nhin thay nhan cua ky test

        23.193 don (23,5%) khong con kip can thiep tai T3 bi keo vao huan luyen;
        ty le bat man cua nhom nay la 7,84% so voi 17,45% cua nhom giu lai
        ->  ty le nen bi lam loang mot cach he thong, va PR-AUC duoc doc so voi
            nen nen no TRONG DEP HON THUC TE

    Ca hai deu lech ve phia co loi cho artifact cua chinh nghien cuu — cung huong
    voi L24 va L37.

VI SAO PHAI LA TEST TINH CHU KHONG PHAI KY LUAT.

    Rang buoc nay da duoc phat bieu tuong minh trong docstring cua `export.py`
    ("`load_split()` la DUONG VAO DUY NHAT") va van bi vi pham o sau tep. Mot rang
    buoc chi ton tai trong van xuoi thi khong phai rang buoc. Day la lan thu hai
    trong du an — lan truoc la `BidCalibrator`: nang luc ton tai, he thong khong
    dung — nen bien phap phai la co che, khong phai ghi nho.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src-v3" / "masdss"

# Ham nap du lieu THO. Chung dung dan o dung mot cho: ben trong `data/`, noi tep
# dac trung duoc SINH RA. Moi noi khac phai di qua `load_split()`.
RAW_LOADERS = {"build_order_table", "time_split"}

# Nhung tep duoc phep goi truc tiep, kem ly do. Danh sach nay la mot HOP DONG:
# them mot dong vao day phai kem lap luan, khong phai de lam test xanh tro lai.
ALLOWED: dict[str, str] = {
    "data/load.py": "noi dinh nghia build_order_table()",
    "data/splits.py": "noi dinh nghia time_split()",
    "data/export.py": "noi SINH RA tep dac trung — phai doc du lieu tho",
    # `make_figures` ve hinh MO TA DU LIEU (do nhay moc T3, ty le nen, phan bo
    # tang A/B). Chung tinh tren TONG THE truoc khi loc, nen doc du lieu tho la
    # dung ban chat — day khong phai duong nap cho mo hinh.
    "cli/make_figures.py": "hinh mo ta tong the, khong phai duong nap cho mo hinh",
}


def _python_files() -> list[Path]:
    return sorted(p for p in SRC.rglob("*.py") if "__pycache__" not in p.parts)


def _calls_raw_loader(path: Path) -> set[str]:
    """Ten ham nap tho ma tep nay GOI (khong tinh import suong)."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = getattr(func, "id", None) or getattr(func, "attr", None)
            if name in RAW_LOADERS:
                found.add(name)
    return found


def test_khong_diem_chay_nao_nap_du_lieu_tho_truc_tiep() -> None:
    """Moi duong nap cho mo hinh phai di qua `load_split()`.

    Vi pham o day KHONG phai chuyen phong cach ma nguon: no co nghia la khoang
    cach ly va phep loc tong the bi bo qua, tuc con so sinh ra bi ro ri.
    """
    violations: list[str] = []
    for path in _python_files():
        rel = path.relative_to(SRC).as_posix()
        if rel in ALLOWED:
            continue
        called = _calls_raw_loader(path)
        if called:
            violations.append(f"{rel} goi {sorted(called)}")

    assert not violations, (
        "Cac tep sau nap du lieu THO thay vi qua `load_split()`, nen chung bo qua "
        "khoang cach ly va phep loc `reachable_at_t3`:\n  "
        + "\n  ".join(violations)
        + "\n\nSua bang cach nap qua `masdss.data.export.load_split()`. Neu mot tep "
          "THUC SU can du lieu tho, them no vao `ALLOWED` KEM LY DO."
    )


def test_danh_sach_mien_tru_khong_phinh_ra() -> None:
    """Chan viec lam test xanh bang cach them vao `ALLOWED`.

    Bon muc hien tai la tran ngan sach. Muon them thi phai sua chinh con so nay,
    va viec do buoc nguoi sua phai doi mat voi cau hoi *"vi sao lai them mot ngoai
    le nua"* thay vi lang le noi dai danh sach.
    """
    assert len(ALLOWED) <= 4, (
        f"Danh sach mien tru da phinh len {len(ALLOWED)} muc. Moi ngoai le la mot "
        f"duong vong qua khoang cach ly — hay sua duong nap thay vi noi dai danh sach."
    )


@pytest.mark.parametrize("rel", sorted(ALLOWED))
def test_moi_muc_mien_tru_deu_ton_tai(rel: str) -> None:
    """Mien tru cho mot tep khong con ton tai la mot lo hong dang ngu yen."""
    assert (SRC / rel).exists(), f"muc mien tru tro toi tep khong ton tai: {rel}"
