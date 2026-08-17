"""CLI — sinh chin tep dac trung/nhan va manifest.

    python -m masdss.cli.export_features
"""

from __future__ import annotations

import argparse
from pathlib import Path

from masdss.data.export import export_feature_files


def main() -> None:
    ap = argparse.ArgumentParser(description="Xuat tep dac trung tach theo moc va tap")
    ap.add_argument("--out", type=Path, default=None, help="thu muc dich")
    ap.add_argument("--goldset-size", type=int, default=300)
    args = ap.parse_args()

    m = export_feature_files(out_dir=args.out, goldset_size=args.goldset_size)

    moc = m["moc_quyet_dinh"]
    tt = m["tong_the"]
    print(f"Moc T3 : {moc['t3']}")
    print(f"Tong the T3: {tt['con_kip_can_thiep_tai_t3']:,} / {tt['tat_ca_don_co_danh_gia']:,} "
          f"don ({tt['ty_le_giu_lai']:.1%}) — dieu kien `{tt['dieu_kien']}`")
    print(f"Tong the T4: {tt['tat_ca_don_co_danh_gia']:,} don — KHONG loc ({tt['ap_cho']})")

    e = m["khoang_cach_ly"]
    print(f"Cach ly : train -{e['train_dropped']} dong · val -{e['val_dropped']} dong")
    print()
    print(f"{'tap':6} {'T3':>9} {'T4':>9} {'ngay mua tu':>21} {'den':>21} "
          f"{'bat man T3':>11} {'bat man T4':>11}")
    for ten, t in m["tap"].items():
        print(f"{ten:6} {t['so_don_t3']:>9,} {t['so_don_t4']:>9,} "
              f"{t['ngay_mua_tu'][:19]:>21} {t['den'][:19]:>21} "
              f"{t['ty_le_bat_man']:>10.2%} {t['ty_le_bat_man_t4']:>10.2%}")
    print()
    print(f"Cot T3: {len(m['cot']['t3'])} · cot T4: {len(m['cot']['t4'])}")
    print(f"Ho gold set: {m['goldset_pool']['so_ung_vien']:,} ung vien tu "
          f"{m['goldset_pool']['nguon']} "
          f"({m['goldset_pool']['so_ung_vien_con_kip_can_thiep']:,} con kip can thiep tai T3)")
    print(f"\n{len(m['tep'])} tep da ghi.")


if __name__ == "__main__":
    main()
