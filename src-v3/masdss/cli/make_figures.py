"""Sinh hinh minh hoa cho luan van tu SO LIEU THAT.

    python -m masdss.cli.make_figures

Nguyen tac: khong hinh nao ve tu so go tay. Moi hinh doc du lieu tu tep da xuat
hoac tinh lai tu `build_order_table()`, de hinh trong luan van khong bao gio lech
voi bang so lieu ben canh no.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from masdss.config import CONFIG

# Font co dau tieng Viet. Times New Roman khop voi ban Word cua luan van.
plt.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "figure.dpi": 200,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.6,
})

MUC = ["#1f3b57", "#c2410c", "#0f766e", "#7c3aed", "#a16207"]


def hinh_danh_doi_moc(out: Path) -> Path:
    """Hinh 3.3 — danh doi giua PHU SONG va CUONG DO TIN HIEU theo moc T3."""
    from masdss.data.load import build_order_table

    moc, phu, lift, nen = [], [], [], []
    for d in (3, 5, 7, 10, 14, 21):
        df = build_order_table(cutoff_days=d)
        r = df[df["reachable_at_t3"]]
        ty_le_nen = r["is_dissatisfied"].mean()
        g = r[r["delivery_state"] == 2]
        moc.append(d)
        phu.append(100 * df[df["is_dissatisfied"]]["reachable_at_t3"].mean())
        lift.append(g["is_dissatisfied"].mean() / ty_le_nen if len(g) else np.nan)
        nen.append(100 * ty_le_nen)

    fig, ax1 = plt.subplots(figsize=(7.2, 4.2))
    # Giu tham chieu tuong minh toi tung duong. `ax.get_lines()` se bat ca duong
    # thang dung ve sau va lam chu giai hien ra mot muc `_child1` vo nghia.
    d_phu, = ax1.plot(moc, phu, "o-", color=MUC[0], lw=2, ms=6,
                      label="Độ phủ đơn bất mãn (%)")
    ax1.set_xlabel("Mốc quyết định $T_3$ — số ngày kể từ ngày mua")
    ax1.set_ylabel("Độ phủ đơn bất mãn (%)", color=MUC[0])
    ax1.tick_params(axis="y", labelcolor=MUC[0])
    ax1.set_ylim(30, 102)

    ax2 = ax1.twinx()
    d_lift, = ax2.plot(moc, lift, "s--", color=MUC[1], lw=2, ms=6,
                       label="Lift nhóm chưa bàn giao 3PL")
    ax2.set_ylabel("Lift so với tỷ lệ nền", color=MUC[1])
    ax2.tick_params(axis="y", labelcolor=MUC[1])
    ax2.grid(False)
    ax2.set_ylim(1.0, 2.8)

    ax1.axvline(7, color="0.35", ls=":", lw=1.4)
    ax1.annotate("mốc được chọn\n(mua + 7)", xy=(7, 87.4), xytext=(9.4, 95),
                 fontsize=10, color="0.2",
                 arrowprops=dict(arrowstyle="->", color="0.45", lw=1))

    duong = [d_phu, d_lift]
    ax1.legend(duong, [l.get_label() for l in duong], loc="lower left",
               frameon=False, fontsize=10)
    ax1.set_xticks(moc)
    fig.tight_layout()

    p = out / "hinh-3-3-danh-doi-moc-t3.png"
    fig.savefig(p); plt.close(fig)
    return p


def hinh_troi_ty_le_nen(out: Path) -> Path:
    """Hinh 3.4 — ty le nen troi qua ba tap, va khoang cach ly."""
    import json
    m = json.loads((CONFIG.paths.derived / "features" / "manifest.json")
                   .read_text(encoding="utf-8"))
    tap = ["train", "val", "test"]
    nen = [100 * m["tap"][t]["ty_le_bat_man"] for t in tap]
    n = [m["tap"][t]["so_don"] for t in tap]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.9),
                                   gridspec_kw={"width_ratios": [1.15, 1]})

    ax1.bar(tap, nen, color=[MUC[0], MUC[2], MUC[1]], width=0.55)
    for i, (v, so) in enumerate(zip(nen, n)):
        ax1.text(i, v + 0.35, f"{v:.2f}%", ha="center", fontsize=10.5)
        ax1.text(i, 0.6, f"n = {so:,}".replace(",", "."), ha="center",
                 fontsize=9.5, color="white")
    ax1.set_ylabel("Tỷ lệ đơn bất mãn (%)")
    ax1.set_title("(a) Tỷ lệ nền trôi đơn điệu qua ba tập")
    ax1.set_ylim(0, 21)

    # Bang (b) so sanh HAI PHUONG AN cach ly, khong chi phuong an dang dung.
    #
    # Chi ve phuong an dang dung se lech voi van ban o §3.5.3: doan do giai thich
    # vi sao ban CHAT HON bi bac bo, va lap luan ay chi hien ra khi dat hai phuong
    # an canh nhau. Con so cua ban chat hon duoc tinh lai tai day tu chinh bang du
    # lieu, khong go tay.
    from masdss.data.load import build_order_table
    from masdss.data.splits import TIME_COLUMN, time_split

    df = build_order_table()
    sp = time_split(df[df["reachable_at_t3"]].copy())
    val_start = sp.val[TIME_COLUMN].min()
    test_start = sp.test[TIME_COLUMN].min()

    def loai_giu(moc_train, moc_val):
        bo = pd.concat([sp.train[sp.train["review_created_at"] >= moc_train],
                        sp.val[sp.val["review_created_at"] >= moc_val]])
        giu = pd.concat([sp.train[sp.train["review_created_at"] < moc_train],
                         sp.val[sp.val["review_created_at"] < moc_val]])
        return (100 * bo["is_dissatisfied"].mean() if len(bo) else 0.0,
                100 * giu["is_dissatisfied"].mean(), len(bo))

    ap_dung = loai_giu(test_start, test_start)
    chat_hon = loai_giu(val_start, test_start)

    x = np.arange(2)
    r = 0.36
    ax2.bar(x - r / 2, [ap_dung[0], chat_hon[0]], r, color=MUC[1],
            label="Dòng bị loại")
    ax2.bar(x + r / 2, [ap_dung[1], chat_hon[1]], r, color="0.66",
            label="Dòng giữ lại")
    for i, (bo, giu, n) in enumerate([ap_dung, chat_hon]):
        ax2.text(i - r / 2, bo + 0.8, f"{bo:.2f}%", ha="center", fontsize=10)
        ax2.text(i + r / 2, giu + 0.8, f"{giu:.2f}%", ha="center", fontsize=10)
        ax2.text(i, 1.0, f"loại {n:,} dòng".replace(",", "."), ha="center",
                 fontsize=9.5, color="0.25")
    ax2.set_xticks(x)
    ax2.set_xticklabels(["Phương án ÁP DỤNG\n(cách ly theo kỳ kiểm thử)",
                         "Phương án BỊ BÁC BỎ\n(cách ly theo kỳ kiểm định)"],
                        fontsize=9.5)
    ax2.set_ylabel("Tỷ lệ đơn bất mãn (%)")
    ax2.set_title("(b) Vì sao phương án cách ly chặt hơn bị bác bỏ")
    ax2.set_ylim(0, 36)
    ax2.legend(frameon=False, fontsize=9.5, loc="upper left")

    fig.tight_layout()
    p = out / "hinh-3-4-ty-le-nen-va-cach-ly.png"
    fig.savefig(p); plt.close(fig)
    return p


def hinh_thoi_diem_danh_gia(out: Path) -> Path:
    """Hinh 3.2 — phan bo thoi diem khach viet danh gia so voi hai moc.

    Day la hinh giai thich loi L33: moc cu neo vao han giao du kien roi vao SAU
    luc khach da viet danh gia voi phan lon so don.
    """
    from masdss.data.load import build_order_table
    df = build_order_table()
    review = pd.to_datetime(df["creation_timestamp"], errors="coerce")
    mua = df["order_purchase_timestamp"]
    han = df["order_estimated_delivery_date"]

    tu_luc_mua = (review - mua).dt.total_seconds() / 86400
    so_voi_han = (review - han).dt.total_seconds() / 86400

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.8, 3.9))

    # Bin CAN THEO NGAY. Dung mot so bin tuy y se cho rang cua: moi bin gom mot
    # phan cua hai ngay lien tiep, va do lech do bien thanh dao dong gia trong hinh.
    d = tu_luc_mua[(tu_luc_mua > 0) & (tu_luc_mua < 45)]
    ax1.hist(d, bins=np.arange(0, 46, 1), color=MUC[0], alpha=0.9)
    ax1.axvline(7, color=MUC[1], lw=2.2)
    ax1.annotate("$T_3$ = mua + 7", xy=(7.4, ax1.get_ylim()[1] * 0.93),
                 xytext=(13, ax1.get_ylim()[1] * 0.93), fontsize=10.5,
                 color=MUC[1], va="center",
                 arrowprops=dict(arrowstyle="->", color=MUC[1], lw=1.2))
    ax1.set_xlabel("Số ngày từ lúc mua đến lúc viết đánh giá")
    ax1.set_ylabel("Số đơn hàng")
    ax1.set_title("(a) Thời điểm viết đánh giá so với ngày mua")
    ax1.set_xlim(0, 45)

    d2 = so_voi_han[(so_voi_han > -45) & (so_voi_han < 12)]
    ax2.hist(d2, bins=np.arange(-45, 13, 1), color=MUC[2], alpha=0.9)
    ax2.axvline(0, color="0.25", lw=1.6, ls="--")
    ax2.axvline(3, color=MUC[1], lw=2.2)
    dinh = ax2.get_ylim()[1]
    ax2.set_ylim(0, dinh * 1.24)
    truoc_han = 100 * (so_voi_han < 0).mean()
    ax2.annotate(f"{truoc_han:.1f}% đánh giá viết\nTRƯỚC hạn dự kiến",
                 xy=(-43, dinh * 1.06), fontsize=10.5, color="0.15", va="top")
    ax2.annotate("mốc cũ (hạn + 3)", xy=(3.4, dinh * 1.12),
                 xytext=(-17, dinh * 1.18), fontsize=10.5, color=MUC[1],
                 va="center",
                 arrowprops=dict(arrowstyle="->", color=MUC[1], lw=1.2))
    ax2.set_xlabel("Số ngày từ hạn giao dự kiến đến lúc viết đánh giá")
    ax2.set_ylabel("Số đơn hàng")
    ax2.set_title("(b) Vì sao mốc neo vào hạn dự kiến là sai")
    ax2.set_xlim(-45, 12)

    fig.tight_layout()
    p = out / "hinh-3-2-thoi-diem-danh-gia.png"
    fig.savefig(p); plt.close(fig)
    return p


def hinh_be_mat_hong(out: Path) -> Path:
    """Hinh 4.4 — be mat hong cua hai kien truc, doc tu hang so trong ma nguon."""
    from masdss.core.components import MAS_ONLY_COMPONENTS, SHARED_COMPONENTS
    from masdss.system.plan import STAGE1_PLAN, STAGE2_PLAN

    goi_duoc = {s.agent for s in (*STAGE1_PLAN, *STAGE2_PLAN) if s.agent}
    from masdss.core.components import AGENT_TO_COMPONENT
    tp_goi_duoc = {AGENT_TO_COMPONENT[a].value for a in goi_duoc
                   if a in AGENT_TO_COMPONENT}
    # `AnalystPool` duoc goi qua fanout nen khong nam trong `Step.agent`.
    tp_goi_duoc |= {"cause_delivery", "cause_quality", "cause_service"}

    chi_mas_goi_duoc = [c for c in MAS_ONLY_COMPONENTS if c in tp_goi_duoc]
    chi_mas_khong_goi = [c for c in MAS_ONLY_COMPONENTS if c not in tp_goi_duoc]

    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    y = [1, 0]
    ax.barh(y, [len(SHARED_COMPONENTS)] * 2, 0.5, color=MUC[0],
            label="Thành phần dùng chung")
    ax.barh([1], [len(chi_mas_goi_duoc)], 0.5, left=[len(SHARED_COMPONENTS)],
            color=MUC[1], label="Chỉ kiến trúc đa tác tử có — gọi được")
    ax.barh([1], [len(chi_mas_khong_goi)], 0.5,
            left=[len(SHARED_COMPONENTS) + len(chi_mas_goi_duoc)],
            color="0.75", hatch="//",
            label="Chỉ kiến trúc đa tác tử có — không nằm trong kế hoạch nào")

    ax.set_yticks(y)
    ax.set_yticklabels(["Kiến trúc\nđa tác tử", "Kiến trúc\nđơn khối"])
    ax.set_xlabel("Số thành phần có thể hỏng")
    ax.set_xticks(range(0, 11))
    ax.text(len(SHARED_COMPONENTS) / 2, 1, f"{len(SHARED_COMPONENTS)}",
            ha="center", va="center", color="white", fontsize=12)
    ax.text(len(SHARED_COMPONENTS) / 2, 0, f"{len(SHARED_COMPONENTS)}",
            ha="center", va="center", color="white", fontsize=12)
    ax.text(len(SHARED_COMPONENTS) + len(chi_mas_goi_duoc) / 2, 1,
            f"{len(chi_mas_goi_duoc)}", ha="center", va="center",
            color="white", fontsize=12)
    ax.text(len(SHARED_COMPONENTS) + len(chi_mas_goi_duoc)
            + len(chi_mas_khong_goi) / 2, 1, f"{len(chi_mas_khong_goi)}",
            ha="center", va="center", color="0.2", fontsize=11)
    # Chu giai dat DUOI nhan truc x. `loc` mot minh khong du: khung chu giai va
    # nhan truc deu neo vao truc, nen chung chong len nhau neu khong chua cho.
    ax.legend(frameon=False, fontsize=9.5, loc="upper center",
              bbox_to_anchor=(0.5, -0.30), ncol=1, handlelength=1.6)
    ax.set_xlim(0, 10.4)
    ax.set_ylim(-0.55, 1.55)
    ax.grid(axis="y", visible=False)
    fig.subplots_adjust(bottom=0.42)

    p = out / "hinh-4-3-be-mat-hong.png"
    fig.savefig(p); plt.close(fig)
    return p


HINH = {
    "3.2": hinh_thoi_diem_danh_gia,
    "3.3": hinh_danh_doi_moc,
    "3.4": hinh_troi_ty_le_nen,
    "4.4": hinh_be_mat_hong,
}


def main() -> None:
    ap = argparse.ArgumentParser(description="Sinh hinh minh hoa cho luan van")
    ap.add_argument("--out", type=Path,
                    default=Path("docs/thesis/figures"))
    ap.add_argument("--only", default=None, help="chi sinh mot hinh, vi du 3.3")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    for ma, ham in HINH.items():
        if args.only and ma != args.only:
            continue
        p = ham(args.out)
        print(f"Hinh {ma} -> {p}")


if __name__ == "__main__":
    main()
