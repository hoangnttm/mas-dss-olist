"""Fixture dung chung cho ca phien test.

Nap du lieu Olist va huan luyen capability MOT LAN. Chung tat dinh nen dung lai
khong lam thay doi ket qua, nhung tiet kiem vai phut moi lan chay suite.
"""

from __future__ import annotations

import pytest

N_CASES = 25   # du de bat khac biet, du nho de test chay nhanh

# Cua so PSI can it nhat 100 quan sat. Mot lan chay 25 case KHONG kich hoat duoc bo
# giam sat, nen moi test "lan chay khoe phai im lang" tren co mau do deu RONG — no
# xanh vi phep do khong chay, khong phai vi he thong dung.
# Day la loi T04 trong docs/methodology-log.md.
N_CASES_MONITORING = 200


@pytest.fixture(scope="session")
def fixtures():
    from masdss.data.load import build_order_table
    from masdss.data.splits import time_split
    from masdss.system.app import Capabilities

    orders = build_order_table()
    splits = time_split(orders)
    return orders, Capabilities.fit(splits.train, splits.val)


@pytest.fixture(scope="session")
def fitted_risk_model(fixtures):
    """Mo hinh da huan luyen kem CHINH tap val da dung de suy thang rui ro.

    Tra ve ca hai vi thang rui ro la tham so DUOC HOC: kiem no ma khong co tap da
    sinh ra no thi chi kiem duoc kieu du lieu, khong kiem duoc tinh chat.
    """
    from masdss.data.splits import time_split

    orders, caps = fixtures
    return caps.risk_model, time_split(orders).val


@pytest.fixture(scope="session")
def normal_run(tmp_path_factory, fixtures):
    """Mot lan chay binh thuong, dung chung cho moi test can ket qua that."""
    import asyncio

    from masdss.cli.run_system import run

    orders, caps = fixtures
    out = tmp_path_factory.mktemp("normal")
    asyncio.run(run(out, n_cases=N_CASES, orders=orders, capabilities=caps))
    return out


@pytest.fixture(scope="session")
def healthy_run_large(tmp_path_factory, fixtures):
    """Lan chay khoe DU LON de bo giam sat thuc su duoc kich hoat.

    Dung cho cac test IMP-1. Voi 25 case, PSI khong bao gio duoc tinh nen test im
    lang la test rong.
    """
    import asyncio

    from masdss.cli.run_system import run

    orders, caps = fixtures
    out = tmp_path_factory.mktemp("healthy_large")
    asyncio.run(run(out, n_cases=N_CASES_MONITORING, orders=orders, capabilities=caps))
    return out


@pytest.fixture(scope="session")
def exported(tmp_path_factory, fixtures):
    """Xuat tep dac trung MOT LAN vao thu muc tam.

    Ghi ra `tmp_path` chu khong ghi de `data/v3/features/`: test khong duoc pha
    artifact that. Duong dan duoc truyen qua `base=` chu khong qua bien toan cuc.
    """
    from masdss.data.export import export_feature_files

    orders, _ = fixtures
    out = tmp_path_factory.mktemp("features")
    manifest = export_feature_files(df=orders, out_dir=out)
    return out, manifest
