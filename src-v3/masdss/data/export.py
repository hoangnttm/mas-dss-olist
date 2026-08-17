"""WP1 / T1.7 — Tach du lieu thanh TEP VAT LY theo moc quyet dinh va vai tro tap.

Phuc vu: RQ1, RQ3 (moi con so ve du bao va quy ket deu doc qua day).

VI SAO CAN MODULE NAY. Ranh gioi du lieu truoc day chi duoc cuong che LUC CHAY:
`build_order_table()` sinh mot bang rong chua moi cot, roi `FeatureSet(decision_point)`
loc lai. Ai dung thang bang rong la bo qua duoc — va do khong phai gia thuyet, do la
chuyen da xay ra HAI LAN:

    L30  rang buoc cuong che o muc DAC TRUNG nhung bo ngo o muc TONG THE
    L33  moc T3 la mot tham so cau hinh, khong bat bien nao doi chieu no voi T4

Ca hai deu la loi IM LANG: khong ngoai le, khong canh bao, chi la mot con so dep hon
thuc te. Cach chan duy nhat dang tin la lam cho vi pham tro nen KHONG BIEU DAT DUOC —
dac trung T4 khong nam trong tep T3, nen khong nap nham duoc.

| Rui ro | Cuong che luc chay | Tach tep vat ly |
|---|---|---|
| Dac trung T4 lot vao mo hinh T3 | loi im lang | khong nap duoc cot |
| `rating` dung lam dac trung | phai nho cam | nam o tep khac |
| Huan luyen tren tap test | phai nho chia dung | tep khac |
| Gan nhan nham tap | khong phat hien duoc | goldset chi sinh tu `*_test` |

Muoi artifact:

    t3_{train,val,test}.parquet   cot T1..T3 · tong the CON KIP CAN THIEP tai T3
    t4_{train,val,test}.parquet   cot T1..T4 · tong the DAY DU
    y_{train,val,test}.parquet    nhan + moc thoi gian + `reachable_at_t3`, tong the day du
    goldset_pool.parquet          ung vien gan nhan, tu ky test cua tong the T4
    manifest.json                 ranh gioi ngay, so dong, danh sach cot, ty le nen

HAI TRUC TACH BIET, va lan sua 13/08 la de go chung ra khoi nhau:

    LUOC DO  — `t3_*` khong chua cot T4. Mot chieu, va day la chieu chan L30.
    TONG THE — T3 loc `reachable_at_t3`; T4 KHONG loc.

Ban truoc gop hai truc lam mot bang cach khong cho `t4_*` lay lai cot T3. Nghe manh
hon (hai luoc do roi nhau) nhung no keo theo mot he qua khong ai chon: giai doan 2
phai NOI hai tep, phep noi la INNER, nen tong the T4 bi keo ve dung tong the T3 va
1.819/14.475 don bat man (12,6%) bien mat khoi tang quy ket — phan lon la khieu nai
KHONG do giao hang. Mot bat bien ve luoc do da am tham quyet dinh mot van de ve
tong the. Xem `_stage_columns()` va `export_feature_files()`.

`load_split()` la DUONG VAO DUY NHAT cho mo hinh, va `load_stage()` la ham ma cac
diem chay nen goi. `tests-v3/test_data_entrypoint.py` cuong che dieu do.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from masdss.config import CONFIG
from masdss.core.ontology import DecisionPoint
from masdss.data.features import REGISTRY
from masdss.data.load import build_order_table
from masdss.data.splits import TIME_COLUMN, time_split

STAGES = ("t3", "t4")
SPLITS = ("train", "val", "test")

KEY = "order_id"

# Cot nhan — KHONG duoc xuat hien trong bat ky tep dac trung nao.
LABEL_COLUMNS = (KEY, "rating", "is_dissatisfied", "tier", "has_content")

# Cot moc thoi gian di kem tep nhan de kiem tra duoc ranh gioi, khong phai dac trung.
TIME_COLUMNS = (TIME_COLUMN, "t3_cutoff", "review_created_at")


class ExportError(RuntimeError):
    """Bat bien luoc do bi vi pham luc xuat hoac luc nap."""


T3_AVAILABLE = (DecisionPoint.T1, DecisionPoint.T2, DecisionPoint.T3)

# Dac trung KET CUC giao hang. Chung chi xac dinh duoc sau khi hang toi, nen su co
# mat cua chung trong mot tep T3 la dinh nghia cua loi L30.
KET_CUC_GIAO_HANG = ("delivery_days", "delivery_delay_days", "is_late",
                     "carrier_handover_days")


def _stage_columns(stage: str) -> tuple[str, ...]:
    """Cot cua tung giai doan.

    BAT BIEN THAT SU CHONG RO RI la mot chieu, khong phai hai chieu:

        `t3_*` KHONG duoc chua cot T4.

    Ban truoc phat bieu no manh hon — hai luoc do ROI NHAU — bang cach khong cho
    `t4_*` lay lai cot T3. Cach do dep nhung sai muc dich: no buoc giai doan 2 phai
    NOI hai tep, ma phep noi la INNER nen tong the T4 bi keo ve dung tong the T3.
    Tuc mot bat bien ve LUOC DO da am tham quyet dinh mot van de ve TONG THE.

    Nay `t4_*` la bang lam viec DAY DU cua giai doan 2: cot T1..T3 va cot T4. Chieu
    con lai — `t3_*` khong chua cot T4 — van duoc giu, va no moi la chieu chan duoc
    L30.
    """
    if stage == "t3":
        names = [s.name for s in REGISTRY if s.available_at in T3_AVAILABLE]
    elif stage == "t4":
        names = [s.name for s in REGISTRY]      # ca T1..T3 lan T4
    else:
        raise ValueError(f"stage khong hop le: {stage!r}")
    return (KEY, *names)


@dataclass(frozen=True)
class EmbargoReport:
    """So dong bi loai o moi ranh gioi vi nhan cua chung den qua muon."""

    train_dropped: int
    val_dropped: int
    test_start: str
    dropped_dissatisfaction: float
    kept_dissatisfaction: float

    def as_dict(self) -> dict:
        return {
            "train_dropped": self.train_dropped,
            "val_dropped": self.val_dropped,
            "moc_cach_ly": self.test_start,
            # Hai con so nay phai duoc bao cao, khong duoc de im: dong bi loai KHONG
            # phai mau ngau nhien, nguoi viet danh gia muon bat man nhieu hon han.
            "ty_le_bat_man_dong_bi_loai": round(self.dropped_dissatisfaction, 4),
            "ty_le_bat_man_dong_giu_lai": round(self.kept_dissatisfaction, 4),
        }


def _apply_embargo(splits) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, EmbargoReport]:
    """Khoang cach ly: mot dong huan luyen phai co NHAN da hoan tat truoc ky sau.

    Chia theo thoi gian dung `order_purchase_timestamp`, nhung nhan chi ton tai luc
    khach viet danh gia — MUON hon luc mua. Mot don mua cuoi ky train ma danh gia
    den giua ky val se dua thong tin cua ky sau vao qua trinh huan luyen.

    MOC CACH LY LA `test_start`, KHONG PHAI `val_start`. Toi da cai ban chat hon
    truoc (train cach ly theo `val_start`) va do do cai gia cua no:

        5.789 dong bi loai, ty le bat man 29,52% so voi 16,28% o phan giu lai

    Tuc ban chat hon cat di dung nhom kho nhat, va lam ty le nen cua tap huan luyen
    dich xuong mot cach he thong. Cai gia do khong mua duoc gi: mot dong train co
    danh gia den trong ky VAL khong he chua thong tin nao ve ky TEST, ma test moi la
    noi moi con so cong bo duoc do.

    Mo phong trien khai dung la: mo hinh cham diem ky test se duoc huan luyen tai
    `test_start`, voi moi nhan da biet tinh den luc do. Vay dieu kien dung cho ca
    train lan val la `review_created_at < test_start`.
    """
    train, val, test = splits.train, splits.val, splits.test
    test_start = test[TIME_COLUMN].min()

    giu_train = train["review_created_at"] < test_start
    giu_val = val["review_created_at"] < test_start

    bi_loai = pd.concat([train[~giu_train], val[~giu_val]])
    giu_lai = pd.concat([train[giu_train], val[giu_val]])

    report = EmbargoReport(
        train_dropped=int((~giu_train).sum()),
        val_dropped=int((~giu_val).sum()),
        test_start=str(test_start),
        dropped_dissatisfaction=(float(bi_loai["is_dissatisfied"].mean())
                                 if len(bi_loai) else 0.0),
        kept_dissatisfaction=float(giu_lai["is_dissatisfied"].mean()))
    return train[giu_train].copy(), val[giu_val].copy(), test.copy(), report


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def export_feature_files(df: pd.DataFrame | None = None,
                         out_dir: Path | None = None,
                         goldset_size: int = 300) -> dict:
    """Sinh chin artifact dac trung/nhan cong manifest. Tra ve noi dung manifest.

    Tong the: CHI nhung don con kip can thiep tai T3 (`reachable_at_t3`). Day la ve
    thu hai cua rang buoc moc quyet dinh — ve ma L30 va L33 deu bo ngo.
    """
    df = build_order_table() if df is None else df
    out = Path(out_dir) if out_dir is not None else CONFIG.paths.derived / "features"
    out.mkdir(parents=True, exist_ok=True)

    if "reachable_at_t3" not in df.columns:
        raise ExportError("bang thieu cot `reachable_at_t3` — build_order_table() da cu?")

    # --- HAI TONG THE, va su bat doi xung nay la mot QUYET DINH NGHIEN CUU ---
    #
    # T3 la DU BAO. Mot don ma khach da viet danh gia truoc moc thi khong con gi de
    # du bao, va cham diem no la doc lai mot ket cuc da co (L33). Nen tong the T3 =
    # nhung don CON KIP CAN THIEP.
    #
    # T4 la QUY KET. Dieu kien de vao day la "da co danh gia 1-2 sao", khong phu
    # thuoc vao viec T3 co kip nhin thay don do hay khong. Ap `reachable_at_t3` o
    # day loai di 1.819/14.475 don bat man (12,6%), va nhom bi loai KHONG ngau
    # nhien: chung duoc giao som hon trung binh 13,2 ngay va co van ban nhieu hon
    # (81,6% so voi 73,8%), tuc phan lon la khieu nai KHONG do giao hang. Loc chung
    # di se lam phan bo nguyen nhan lech ve phia `delivery`.
    #
    # BAN TRUOC AP PHEP LOC CHO CA HAI, va do la mot quyet dinh khong ai chon: no
    # la HE QUA PHU cua viec `t4_*` khong chua cot T3, khien giai doan 2 phai noi
    # INNER hai tep va tong the bi keo ve theo. Xem `_stage_columns`.
    tong_the_t3 = df[df["reachable_at_t3"]].copy()

    # Ranh gioi thoi gian lay TU phep chia cua T3, roi ap NGUYEN VEN cho tong the
    # day du. Nho vay mot don khong bao gio roi vao hai tap khac nhau o hai giai
    # doan, va con so cua T3 khong xe dich khi tong the T4 mo rong.
    splits_t3 = time_split(tong_the_t3)
    val_start = splits_t3.val[TIME_COLUMN].min()
    test_start_mua = splits_t3.test[TIME_COLUMN].min()

    def _chia(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
        t = frame[TIME_COLUMN]
        return {
            "train": frame[t < val_start].copy(),
            "val": frame[(t >= val_start) & (t < test_start_mua)].copy(),
            "test": frame[t >= test_start_mua].copy(),
        }

    day_du = _chia(df.dropna(subset=[TIME_COLUMN]))
    _, _, _, embargo = _apply_embargo(splits_t3)

    # Khoang cach ly ap cho CA HAI tong the, cung mot moc: mot dong huan luyen phai
    # co NHAN da hoan tat truoc ky test. Voi tang quy ket, "nhan" la van ban danh
    # gia — no cung den tu tuong lai y het.
    moc_cach_ly = pd.Timestamp(embargo.test_start)
    # Dem RIENG so dong bi loai tren tong the DAY DU.
    #
    # `embargo` o tren duoc tinh tren `splits_t3`, nen `train_dropped`/`val_dropped`
    # cua no chi noi ve tong the DU BAO. Tong the QUY KET rong hon va mat nhieu hon:
    # 1 + 2.351 thay vi 1 + 2.245 — chenh 106 dong la nhung don `reachable_at_t3 =
    # False` co danh gia den sau moc. Bao cao mot con so ma khong noi no thuoc tong
    # the nao se khien phep tru 98.673 - 96.321 khong khop voi manifest.
    cach_ly_t4: dict[str, int] = {"train_dropped": 0, "val_dropped": 0}
    for ten in ("train", "val"):
        truoc = len(day_du[ten])
        day_du[ten] = day_du[ten][day_du[ten]["review_created_at"] < moc_cach_ly].copy()
        cach_ly_t4[f"{ten}_dropped"] = truoc - len(day_du[ten])

    phan_t4 = day_du
    phan_t3 = {k: v[v["reachable_at_t3"]].copy() for k, v in day_du.items()}

    for split in SPLITS:
        thua = set(phan_t3[split][KEY]) - set(phan_t4[split][KEY])
        if thua:
            raise ExportError(
                f"t3_{split} co {len(thua)} don khong nam trong t4_{split} — hai tong "
                f"the da lech ranh gioi, phep so sanh giua hai giai doan mat co so")

    manifest: dict = {
        "moc_quyet_dinh": {
            "t3": f"ngay mua + {CONFIG.t3_cutoff_days} ngay",
            "t4": "khi danh gia da ve",
            "t3_cutoff_days": CONFIG.t3_cutoff_days,
        },
        "tong_the": {
            "tat_ca_don_co_danh_gia": int(len(df)),
            "con_kip_can_thiep_tai_t3": int(len(tong_the_t3)),
            "ty_le_giu_lai": round(len(tong_the_t3) / len(df), 4),
            "dieu_kien": "review_created_at > t3_cutoff",
            "ap_cho": "CHI giai doan 1 (T3). Giai doan 2 (T4) dung tong the day du "
                      "— xem docstring cua export_feature_files()",
        },
        # Con so cua embargo phai ghi RO NO THUOC TONG THE NAO. Hai tong the mat hai
        # luong khac nhau, va truoc 14/08 chi con so cua T3 duoc ghi — khien phep tru
        # tren tong the T4 khong khop voi manifest.
        "khoang_cach_ly": {**embargo.as_dict(), "tong_the": "t3 (con kip can thiep)"},
        "khoang_cach_ly_t4": {**cach_ly_t4, "moc_cach_ly": embargo.test_start,
                              "tong_the": "t4 (day du)"},
        "tep": {},
        "cot": {stage: list(_stage_columns(stage)) for stage in STAGES},
        "seed": CONFIG.seed,
    }

    for split in SPLITS:
        for stage, phan in (("t3", phan_t3), ("t4", phan_t4)):
            part = phan[split]
            cols = [c for c in _stage_columns(stage) if c in part.columns]
            thieu = set(_stage_columns(stage)) - set(cols)
            if thieu:
                raise ExportError(f"{stage}_{split}: thieu cot {sorted(thieu)}")
            # Chan o CA HAI dau, khong chi luc nap. Bat bien nay duoc phat bieu bang
            # TEN COT NGUYEN VAN chu khong qua `LABEL_COLUMNS`: neu ca phep loc lan
            # phep kiem tra cung doc mot hang so, thi sua hang so do se lam ca hai
            # cung mu, va bai kiem tra tro nen rong.
            ro_ri = {"rating", "is_dissatisfied", "review_lag_days", "has_comment"} & set(cols)
            if ro_ri:
                raise ExportError(f"{stage}_{split}: cot nhan lot vao tep dac trung: "
                                  f"{sorted(ro_ri)}")
            if stage == "t3":
                ket_cuc = set(KET_CUC_GIAO_HANG) & set(cols)
                if ket_cuc:
                    raise ExportError(
                        f"t3_{split}: dac trung KET CUC giao hang lot vao tep T3: "
                        f"{sorted(ket_cuc)} — day dung la loi L30")
            path = out / f"{stage}_{split}.parquet"
            part[cols].to_parquet(path, index=False)
            manifest["tep"][path.name] = {
                "so_dong": int(len(part)), "so_cot": len(cols), "sha256": _sha256(path)}

        # Tep nhan phu TONG THE DAY DU, vi no phuc vu ca hai giai doan. Cot
        # `reachable_at_t3` di kem de phep loc cua T3 kiem tra duoc tu ben ngoai.
        part = phan_t4[split]
        y_cols = [c for c in (*LABEL_COLUMNS, *TIME_COLUMNS, "reachable_at_t3")
                  if c in part.columns]
        path = out / f"y_{split}.parquet"
        part[y_cols].to_parquet(path, index=False)
        manifest["tep"][path.name] = {
            "so_dong": int(len(part)), "so_cot": len(y_cols), "sha256": _sha256(path)}

        manifest.setdefault("tap", {})[split] = {
            "so_don_t3": int(len(phan_t3[split])),
            "so_don_t4": int(len(part)),
            "ngay_mua_tu": str(part[TIME_COLUMN].min()),
            "den": str(part[TIME_COLUMN].max()),
            "ty_le_bat_man": round(float(phan_t3[split]["is_dissatisfied"].mean()), 4),
            "ty_le_bat_man_t4": round(float(part["is_dissatisfied"].mean()), 4),
        }

    # --- ho ung vien gold set: tu ky test cua TONG THE T4 ---
    #
    # Rang buoc "goldset ⊆ t4_test" duoc cuong che o day, tai cho SINH RA no, chu
    # khong phai bang mot loi dan trong tai lieu. Gan nhan mot don thuoc ky train
    # roi dung no de cham diem la ro ri, va no khong de lai dau vet nao.
    #
    # Lay tu tong the T4 chu khong T3: neu ho ung vien bi gioi han o nhom "con kip
    # can thiep" thi bo nhan chuan tro thanh mot mau LECH — thieu he thong nhom
    # khieu nai giao-hang-nhanh, dung nhom ma quy ket nguyen nhan kho nhat.
    #
    # CHI TANG A. Don khong co `review_content` (tang B) nam NGOAI pham vi de tai
    # (quyet dinh 13/08): chung tach thanh nhanh rieng va khong duoc xu ly o giai
    # doan 2. Ho ung vien phai khop pham vi do — gan nhan 300 dong roi cham diem mot
    # he thong khong bao gio xu ly mot phan trong so chung se lam mau so sai.
    test = phan_t4["test"]
    co_van_ban = test["review_content"].notna() & \
        (test["review_content"].astype(str).str.strip() != "")
    ung_vien = test[test["is_dissatisfied"] & co_van_ban].copy()
    manifest["goldset_pool"] = {
        "nguon": "t4_test · CHI tang A (co review_content)",
        "so_ung_vien": int(len(ung_vien)),
        "so_dong_se_gan_nhan": goldset_size,
        "so_ung_vien_con_kip_can_thiep": int(ung_vien["reachable_at_t3"].sum()),
        "tang_b_bi_loai": int((test["is_dissatisfied"] & ~co_van_ban).sum()),
    }
    path = out / "goldset_pool.parquet"
    cols = [c for c in (KEY, *TIME_COLUMNS, "rating", "delivery_state", "reachable_at_t3",
                        "review_title", "review_content", "tier") if c in ung_vien.columns]
    ung_vien[cols].to_parquet(path, index=False)
    manifest["tep"][path.name] = {
        "so_dong": int(len(ung_vien)), "so_cot": len(cols), "sha256": _sha256(path)}

    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


# --------------------------------------------------------------------------
# Duong vao DUY NHAT
# --------------------------------------------------------------------------

def _features_dir(base: Path | None = None) -> Path:
    d = Path(base) if base is not None else CONFIG.paths.derived / "features"
    if not (d / "manifest.json").exists():
        raise ExportError(
            f"chua co tep dac trung o {d} — chay `python -m masdss.cli.export_features` truoc")
    return d


def load_split(stage: str, split: str, base: Path | None = None) -> pd.DataFrame:
    """Nap dac trung cua mot (giai doan, tap). Duong vao duy nhat cho mo hinh.

    Kiem tra luoc do NGAY LUC NAP, khong pho mac vao viec tep duoc sinh dung. Hai
    lan cuong che cho cung mot bat bien la co chu dich: tep co the bi ghi de bang
    tay, va thong bao loi luc nap la thu nguoi dung thuc su doc duoc.
    """
    if stage not in STAGES:
        raise ValueError(f"stage phai thuoc {STAGES}, nhan duoc {stage!r}")
    if split not in SPLITS:
        raise ValueError(f"split phai thuoc {SPLITS}, nhan duoc {split!r}")

    frame = pd.read_parquet(_features_dir(base) / f"{stage}_{split}.parquet")
    ro_ri = set(frame.columns) & (set(LABEL_COLUMNS) - {KEY})
    if ro_ri:
        raise ExportError(f"tep {stage}_{split} chua cot nhan: {sorted(ro_ri)}")
    return frame


def load_labels(split: str, base: Path | None = None) -> pd.DataFrame:
    if split not in SPLITS:
        raise ValueError(f"split phai thuoc {SPLITS}, nhan duoc {split!r}")
    return pd.read_parquet(_features_dir(base) / f"y_{split}.parquet")


# Nhan mac dinh khi nap bang lam viec. CHI `is_dissatisfied` — `rating` la nguon
# sinh ra chinh nhan do, nen keo no vao mac dinh la mo lai dung canh cua ma viec
# tach tep sinh ra de dong.
DEFAULT_LABELS = ("is_dissatisfied",)


def load_stage(stage: str, split: str, *,
               labels: tuple[str, ...] = DEFAULT_LABELS,
               times: bool = False,
               base: Path | None = None) -> pd.DataFrame:
    """Bang lam viec cho MOT giai doan. Day la ham ma cac diem chay nen goi.

        stage="t3"  ->  cot T1..T3, tong the CON KIP CAN THIEP   (du bao)
        stage="t4"  ->  cot T1..T4, tong the DAY DU              (quy ket)

    HAI TRUC KHAC NHAU, dung mot lan goi. Doi `stage` la doi CA hai:

      - LUOC DO: `t3_*` khong chua cot T4. Day la chieu chan L30, va no duoc giu
        boi chinh cau truc tep — cot khong co thi khong doc nham duoc.
      - TONG THE: T3 loc `reachable_at_t3`, T4 khong. Xem lap luan day du o
        `export_feature_files()`.

    Bat bien "mo hinh T3 khong nhin thay cot T4" duoc giu boi hai co che doc lap:
    tep T3 khong chua cot do, va `RiskModel` ghim `self._columns` tai luc `fit` nen
    ke ca khi duoc dua mot bang rong hon o giai doan 2, no van chi doc cot da hoc.

    `labels` mac dinh chi keo `is_dissatisfied`. Muon `rating` / `tier` /
    `has_content` thi phai xin tuong minh — chung la nhan hoac dan xuat cua nhan.
    """
    if stage not in STAGES:
        raise ValueError(f"stage phai thuoc {STAGES}, nhan duoc {stage!r}")
    frame = load_split(stage, split, base=base)

    wanted = list(labels) + ([*TIME_COLUMNS] if times else [])
    if wanted:
        y = load_labels(split, base=base)
        thieu = set(wanted) - set(y.columns)
        if thieu:
            raise ExportError(f"tep nhan y_{split} thieu cot {sorted(thieu)}")
        frame = frame.merge(y[[KEY, *wanted]], on=KEY, how="inner", validate="one_to_one")
    return frame


def load_manifest(base: Path | None = None) -> dict:
    return json.loads((_features_dir(base) / "manifest.json").read_text(encoding="utf-8"))
