"""WP10 / T10.6 — Chi phi cua kien truc.

Phuc vu: RQ1 ve (d), gia thuyet H5.

DAY LA NHOM CHI SO BAT LOI CHO ARTIFACT, va no bat buoc phai duoc bao cao.

    H5 khai bao TRUOC khi chay thi nghiem: "MAS-DSS chiu overhead do tre cao hon kien
    truc don khoi" — ky vong THUA. Viec khai bao truoc mot gia thuyet minh ky vong
    thua la bien phap bao dam tinh khach quan: no chan truoc don phan bien "anh dang
    co chung minh cai minh muon tin".

    Kha nang chiu loi KHONG MIEN PHI. Bao cao cai gia phai tra — do tre, so thanh
    phan, quy mo ma nguon — lam cho ket luan ve uu diem dang tin hon nhieu so voi mot
    bao cao chi khoe uu diem.

BA NHOM CHI PHI:

    THOI GIAN   — do tre p50/p95 tren moi case, MAS-DSS so voi Monolithic
    CAU TRUC    — so thanh phan, so loai message, so tang phai hieu de sua mot bug
    MA NGUON    — so dong cua tang chiu loi, tuc phan ma ton tai CHI de xu ly loi

Nhom thu ba dang chu y nhat: no tra loi cau hoi "phai viet them bao nhieu ma de co
duoc con so hong am tham 0%".
"""

from __future__ import annotations

import ast
import json
import sqlite3
from pathlib import Path

import pandas as pd

# Tang ton tai CHI de xu ly loi va giam sat. Day la phan ma khong ton tai trong
# kien truc don khoi, nen no la cai gia truc tiep cua kha nang chiu loi.
RELIABILITY_MODULES = (
    "system/reliability/guards.py",
    "system/reliability/health.py",
    "system/reliability/breaker.py",
    "system/reliability/pipeline.py",
    "system/reliability/reference.py",
    "runtime/faults.py",
)

# Tang ton tai de cac tac tu noi chuyen duoc voi nhau.
COORDINATION_MODULES = (
    "core/message.py",
    "core/components.py",
    "runtime/actor.py",
    "runtime/message_log.py",
    "system/orchestrator.py",
    "system/plan.py",
    "system/blackboard.py",
    "system/contract_net.py",
    "system/explain.py",
)


def _count_code_lines(path: Path) -> tuple[int, int]:
    """Tra ve (dong ma thuc, tong dong).

    Dem bang AST thay vi dem dong tho: docstring va comment trong du an nay rat day,
    va tinh chung vao se thoi phong cai gia len nhieu lan. Bao cao ca hai de nguoi
    doc thay chenh lech.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    tree = ast.parse(text)

    # Dung VI TRI DONG that cua node docstring thay vi uoc luong tu do dai chuoi.
    # Cach uoc luong truoc day cong them 2 cho cap dau nhay, nhung dong mo va dong
    # dong thuong da nam trong chinh noi dung chuoi, nen no tru trung va co the day
    # so dong ma xuong am — luc do `max(..., 0)` bien loi thanh so 0 im lang.
    docstring_lines: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.FunctionDef,
                                 ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        body = getattr(node, "body", None)
        if not body:
            continue
        first = body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) \
                and isinstance(first.value.value, str):
            docstring_lines.update(range(first.lineno, (first.end_lineno or first.lineno) + 1))

    code = sum(
        1 for number, line in enumerate(lines, start=1)
        if line.strip() and not line.strip().startswith("#")
        and number not in docstring_lines
    )
    return code, len(lines)


def source_cost(src_root: Path) -> pd.DataFrame:
    """Quy mo ma nguon cua tung tang."""
    rows = []
    for label, modules in (("chiu loi", RELIABILITY_MODULES),
                           ("phoi hop", COORDINATION_MODULES)):
        code = total = 0
        present = 0
        for relative in modules:
            path = src_root / relative
            if not path.exists():
                continue
            present += 1
            c, t = _count_code_lines(path)
            code += c
            total += t
        rows.append({"tang": label, "so_module": present,
                     "dong_ma": code, "tong_dong": total})
    return pd.DataFrame(rows)


def latency(out_dir: Path) -> pd.DataFrame:
    """Do tre p50/p95, MAS-DSS so voi Monolithic-Complete.

    KHONG TAT DINH — co dong ho tham gia. Khong dung de so sanh giua hai lan chay,
    chi dung de bao cao do lon (RQ1 ve d).

    L46 — cot `ms_moi_case` cua CA HAI hang lay tu WALL-CLOCK do trong cung mot tien
    trinh, tren cung tap case. Ban truoc lay `sum(span.duration_ms)` cho MAS va
    wall-clock cho baseline: span bo qua glue dieu phoi va phan ghi nhat ky, con
    dong ho baseline lai om ca hai baseline khac cong phan serialize. Hai sai lech
    nguoc chieu nhau nhung CUNG co loi cho MAS.

    `sum_span_ms_moi_case` van duoc giu, nhung o vai tro MO TA: no la phan thoi gian
    nam TRONG cac lenh goi capability, tuc mot CHAN DUOI cua chi phi MAS.
    """
    rows = []

    span_path = out_dir / "spans.sqlite"
    n_cases = 0
    decisions_path = out_dir / "decisions.jsonl"
    if decisions_path.exists():
        n_cases = len(decisions_path.read_text(encoding="utf-8").splitlines())

    report: dict = {}
    report_path = out_dir / "reliability_report.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))

    if span_path.exists():
        conn = sqlite3.connect(span_path)
        values = [r[0] for r in
                  conn.execute("SELECT duration_ms FROM spans ORDER BY duration_ms")]
        conn.close()
        if values:
            total = sum(values)
            rows.append({
                "kien_truc": "MAS-DSS",
                "p50_ms_moi_loi_goi": round(values[len(values) // 2], 4),
                "p95_ms_moi_loi_goi": round(
                    values[min(int(0.95 * len(values)), len(values) - 1)], 4),
                "so_loi_goi": len(values),
                "ms_moi_case": report.get("mas_ms_per_case", float("nan")),
                "sum_span_ms_moi_case": round(total / max(n_cases, 1), 3),
            })

    if "mono_ms_per_case" in report:
        rows.append({
            "kien_truc": "Monolithic-Complete",
            "p50_ms_moi_loi_goi": float("nan"),
            "p95_ms_moi_loi_goi": float("nan"),
            "so_loi_goi": float("nan"),
            "ms_moi_case": report["mono_ms_per_case"],
            "sum_span_ms_moi_case": float("nan"),
        })
    return pd.DataFrame(rows)


def structural_cost(src_root: Path) -> pd.DataFrame:
    """So thanh phan phai hieu de sua mot bug trong tung kien truc."""
    from masdss.core.components import AGENT_TO_COMPONENT
    from masdss.core.message import Performative

    return pd.DataFrame([
        {"hang_muc": "so tac tu", "mas_dss": len(AGENT_TO_COMPONENT), "monolithic": 0},
        {"hang_muc": "so loai message", "mas_dss": len(Performative), "monolithic": 0},
        {"hang_muc": "so tang phai hieu",
         "mas_dss": len(["core", "runtime", "agents", "system", "capabilities"]),
         "monolithic": len(["capabilities", "baselines"])},
        {"hang_muc": "co truong bieu dien muc suy giam", "mas_dss": 1, "monolithic": 0},
    ])


# Tong the du bao tai T3 = ngay mua + 7. Chi phi phai bao cao o QUY MO NAY, khong
# phai o quy mo mot case: 1 mili giay moi case nghe khong dang ke, va do chinh la
# ly do no khong duoc phep la don vi bao cao duy nhat.
BATCH_SIZE = 75_480


def failure_surface() -> pd.DataFrame:
    """Be mat hong — thuoc do CHINH cua chi phi kien truc.

    Do tre va so dong ma la nhung thu de do nen hay duoc bao cao. Nhung cai gia THAT
    cua mot kien truc da tac tu khong nam o do: no nam o so thanh phan CO THE HONG.
    Nam thanh phan chi MAS-DSS moi co la be mat hong ma kien truc nay TU TAO RA.

    Va day la nhan dinh phai noi thang trong Chuong 5: mot phan kha nang chiu loi cua
    MAS-DSS ton tai de quan ly chinh rui ro ma no tao ra. H2 la phep thu cho dieu do.
    """
    from masdss.core.components import MAS_ONLY_COMPONENTS, SHARED_COMPONENTS

    return pd.DataFrame([
        {"hang_muc": "thanh phan dung chung", "mas_dss": len(SHARED_COMPONENTS),
         "monolithic": len(SHARED_COMPONENTS),
         "chi_tiet": ", ".join(SHARED_COMPONENTS)},
        {"hang_muc": "thanh phan CHI MAS co", "mas_dss": len(MAS_ONLY_COMPONENTS),
         "monolithic": 0, "chi_tiet": ", ".join(MAS_ONLY_COMPONENTS)},
        {"hang_muc": "TONG be mat hong",
         "mas_dss": len(SHARED_COMPONENTS) + len(MAS_ONLY_COMPONENTS),
         "monolithic": len(SHARED_COMPONENTS), "chi_tiet": "so thanh phan co the hong"},
    ])


def latency_at_scale(out_dir: Path, batch_size: int = BATCH_SIZE) -> pd.DataFrame:
    """Do tre quy ve QUY MO LO, tinh bang giay — khong bao cao dang phan tram.

    Vi sao khong dung phan tram: phan tram tren mot nen nho lam sai lech nhan thuc ve
    do lon, va nguoi doc khong co cach nao doi nguoc lai neu ta khong dua nen ra. Bang
    nay vi vay luon dua CA HAI ve o don vi tuyet doi.

    L46 — ban truoc cua docstring nay minh hoa bang chenh lech "1,016 ms tren nen
    9,4 ms = +10,8%". So do do SAI CO SO (xem `latency()`), va lap luan "chenh lech
    khong dang ke" dua tren no da bi rut. Do lai dung cach: MAS 115-130 ms/case so
    voi don khoi 6,8-9,2 ms/case, tuc CHAM HON 12,5-17,9 LAN.

    Bang nay dua ca hai kien truc ve cung mot don vi ma nguoi van hanh phan quyet
    duoc: bao lau de chay het mot lo. Khong co nguong "chap nhan duoc" nao duoc khai
    bao truoc, nen KHONG phan quyet ho nguoi doc — xem L29.
    """
    bang = latency(out_dir)
    if bang.empty:
        return bang
    out = bang[["kien_truc", "ms_moi_case"]].copy()
    out["giay_moi_lo"] = (out["ms_moi_case"] * batch_size / 1000).round(1)
    out["phut_moi_lo"] = (out["giay_moi_lo"] / 60).round(1)

    nen = out.loc[out["kien_truc"] == "Monolithic-Complete", "giay_moi_lo"]
    if not nen.empty:
        out["chenh_lech_giay"] = (out["giay_moi_lo"] - float(nen.iloc[0])).round(1)
    return out


def report(out_dir: Path, src_root: Path) -> dict[str, pd.DataFrame]:
    """Ba thuoc do, theo dung thu tu uu tien.

    `be_mat_hong` dung dau vi no la thuoc do chinh. `ma_nguon` xuong cuoi va chi con
    vai tro MO TA: so dong ma khong phai mot dai luong co nghia de so sanh kien truc
    — no phu thuoc vao van phong, chu thich va muc do tach ham nhieu hon la vao thiet
    ke. Giu lai vi no van cho nguoi doc mot cam nhan ve quy mo cong viec.
    """
    return {
        "1_be_mat_hong": failure_surface(),
        "2_do_tre_theo_lo": latency_at_scale(out_dir),
        "3_do_tre_chi_tiet": latency(out_dir),
        "4_cau_truc": structural_cost(src_root),
        "5_ma_nguon_MO_TA": source_cost(src_root),
    }
