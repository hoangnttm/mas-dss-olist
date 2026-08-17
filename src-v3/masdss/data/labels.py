"""WP1 / T1.5 — Nhan bat man va weak label nguyen nhan.

Phuc vu: RQ3 (rang buoc C2 — moi con so ve quy ket phai do tren gold set).

CO CHE CHONG VONG TRON: nhan duoc boc trong HAI KIEU KHAC NHAU.

    GoldLabels  -> nhan do NGUOI gan. Duy nhat duoc phep dung de danh gia.
    WeakLabels  -> nhan tu sinh bang tu khoa. CHI duoc dung de pre-train.

`evaluation/attribution.py` chi nhan `GoldLabels`; truyen `WeakLabels` vao se
raise `WeakLabelInEvaluation`. Day la cach cuong che bang KIEU DU LIEU — khong pho
mac ky luat ca nhan, vi vong tron danh gia rat de len ve sau ba thang.

VE CHINH BO TU KHOA: no co day du nhung khuyet diem ma adversarial-review.md da
chi ra — khong duoc kiem dinh, truot bien the chinh ta, va xu ly phu dinh so sai.
Do KHONG phai ly do de bo no, vi no chi lam TIN HIEU HUAN LUYEN CO NHIEU. Do lon
cua nhieu duoc DO TRUC TIEP so voi gold set (goldset/agreement.py) va bao cao nhu
mot threat duoc dinh luong.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

import pandas as pd

from masdss.core.errors import WeakLabelInEvaluation
from masdss.core.ontology import Cause

DISSATISFIED_MAX_RATING = 2

CAUSE_COLUMNS = ("cause_delivery", "cause_quality", "cause_service")

# Tu khoa tieng Bo. Danh sach nay CHUA duoc kiem dinh — xem docstring dau file.
LEXICON: dict[Cause, tuple[str, ...]] = {
    Cause.DELIVERY: (
        "nao chegou", "não chegou", "nao recebi", "não recebi", "ainda nao",
        "ainda não", "atraso", "atrasad", "demorou", "demora", "prazo",
        "extraviad", "nao entregue", "não entregue",
    ),
    Cause.QUALITY: (
        "quebrad", "danificad", "defeito", "nao funciona", "não funciona",
        "diferente", "qualidade ruim", "pessima qualidade", "péssima qualidade",
        "veio errado", "produto errado", "estragad",
        # `faltando` DA CHUYEN SANG DELIVERY — xem khoi chu thich duoi.
    ),
    Cause.SERVICE: (
        "nao responde", "não responde", "sem resposta", "atendimento", "descaso",
        "nao resolveram", "não resolveram", "reembolso", "estorno", "nenhuma solucao",
        "nenhuma solução",
        # --- MO RONG 13/08, xem khoi chu thich ngay duoi ---
        # (a) khong duoc phan hoi — phai la CUM, khong duoc la goc tu
        "nao respondeu", "không respondeu", "não respondeu",
        "nao responderam", "não responderam", "ninguém respondeu",
        "nenhuma resposta", "sem retorno",
        # (b) khach da chu dong lien he
        "entrei em contato", "tentei contato", "varias tentativas", "e-mail", "email",
        # (c) khieu nai va yeu cau da nop
        "reclamacao", "reclamação", "reclamei", "solicitei",
        "cancelamento", "cancelei",
        # (d) khong ai xu ly
        "ninguem", "ninguém",
    ),
}

# --------------------------------------------------------------------------
# VI SAO NHOM `service` DUOC MO RONG (13/08) — VA CACH CHON TU KHOA
#
# VAN DE: `service` chi co 232/7.641 = 3,04% duong tren tap train, thua hon
# `delivery` (45,07%) muoi lam lan. Head hoc mot lop qua thua nen o duong chay
# that, `ServiceAnalyst` thang thau 92 lan va TU CHOI ca 92 — nhan `service`
# khong bao gio quy ket duoc, tuc he thong mat MOT TRONG BON loai dau ra.
#
# CACH CHON — do lien ket, khong doan:
#   1. Lay n-gram pho bien trong nhom CHUA quy ket duoc, CHI tren tap TRAIN.
#   2. Voi moi ung vien, do lift = P(service | co tu) / P(service). Giu lift >= 2.
#   3. Sang loc ngu nghia: bo tu khong xac dinh duoc CO CHE hong.
#      Bi loai du lift >= 2: `empresa` (2,35x) — rong, khong chi co che nao.
#      Bi loai vi lift thap:  `retorno` 1,70x · `devoluç` 1,67x · `troca` 1,39x ·
#                             `nota fiscal` 0,39x · `devolver` 0,25x · `suporte` 0,00x
#
# BAY PHU DINH — day la diem ky thuat quan trong nhat cua nhom nay:
#
#     `_is_negated` LOAI BO khop khi co phu dinh dung truoc trong 25 ky tu. Voi
#     `service`, phu dinh THUONG CHINH LA NGHIA: "nao respondeu" = khong phan hoi
#     = that bai dich vu. Neu them goc tu `respondeu`, cum "nao respondeu" se khop
#     roi bi chinh bo phu dinh loai ra — dung nguoc.
#
#     Vi vay nhom (a) duoc them o dang CUM bat dau bang tu phu dinh: khi do vi tri
#     khop tro ngay tu "nao", va cua so nhin nguoc khong con thay phu dinh nao.
#
# KIEM CHUNG tren gold set — day la DANH GIA, khong phai huan luyen, nen khong vi
# pham C2. Bo nhan hien la `model_assisted_provisional` nen con so nay la KIEM TRA
# LANH MANH, KHONG duoc trich vao Chuong 5:
#
#     ban cu     : precision 0,500 · recall 0,128 · F1 0,203
#     ban mo rong: precision 0,562 · recall 0,383 · F1 0,456
#
# Precision TANG chu khong giam, nen day khong phai phep thoi phong do phu.
# --------------------------------------------------------------------------

# TU KHOA CUA `price` CU, DA DINH TUYEN LAI theo ba quy tac o `Cause`.
#
#   "frete caro" (phi van chuyen dat) -> DELIVERY: khach tra tien cho mot dich vu
#       giao tan nha khong duoc cung cap, khong phai phan xet gia san pham.
#   "nao vale" / "nao compensa" (khong dang tien) -> QUALITY: dung la phan xet
#       gia tri, tuc chat luong khong tuong xung so tien.
#
#   "caro" / "preco alto" tran KHONG duoc dinh tuyen: chung qua mo ho de xac dinh
#   co che hong, va gan bua se sinh nhieu. Bo han.
LEXICON[Cause.DELIVERY] = LEXICON[Cause.DELIVERY] + ("frete caro", "frete abusivo")

# --------------------------------------------------------------------------
# DINH TUYEN LAI THEO CODEBOOK (14/08) — `delivery` la DICH VU GIAO HANG, khong
# chi la "giao tre".
#
# Bo tu khoa cu chi coi `delivery` = tre / khong toi / that lac. Codebook thi rong
# hon, va su lech nay lam nhan huan luyen sai HE THONG chu khong phai lac dac.
#
# --- (a) QUY TAC 1: SO LUONG thuoc `delivery` ---
#
#     "Mon hang khach cam tren tay co dung thu ho dat khong?
#      Khong dung thu -> quality. Dung thu nhung THIEU MON -> delivery."
#
#     `faltando` truoc day nam o QUALITY. Do la sai theo codebook, va gold set xac
#     nhan: 12/12 dong chua `faltando` duoc nguoi gan `delivery` (100%), chi 1 dong
#     kem `quality`. Chuyen sang DELIVERY va bo sung cac bien the cung nghia.
#
# --- (b) VI DU 12: VO TRONG LUC GIAO -> `delivery` VA `quality` ---
#
#     "product broken on delivery" -> delivery + quality. Diem mau chot la NGU CANH
#     VAN CHUYEN, khong phai tu "vo": mot mon hang vo do loi san xuat chi la
#     `quality`. Vi vay nhom nay duoc them o dang CUM co ngu canh, va cac tu
#     `quebrad`/`danificad` TRAN van o lai QUALITY.
#
#     Doi chieu tren gold set: `quebrad` tran xuat hien 7 dong — 7/7 duoc gan
#     `quality`, chi 2/7 kem `delivery`. Neu chuyen ca `quebrad` sang delivery thi
#     precision cua `delivery` tut. Cum co ngu canh van chuyen chi xuat hien 1 dong
#     trong gold set nen KHONG KIEM CHUNG DUOC o do — phai ghi ro dieu nay. Tren tap
#     train chung co 92 dong, du de anh huong nhan huan luyen.
#
# --- NGOAI LE VI DU 13: thieu BO PHAN -> `quality` ---
#
#     "missing parts and the assembly was poorly explained" -> quality. Mot mon hang
#     DA den nhung thieu oc vit ben trong la loi san pham, khong phai loi giao hang.
#     Cac cum `faltando peca` (13 dong tren train) vi vay duoc giu o QUALITY; chung
#     van khop `faltando` nen se mang CA HAI nhan. Do la xap xi, va no la gioi han
#     cua mot bo tu khoa khong phan tich cu phap — phai neu o Threats to Validity.
# --------------------------------------------------------------------------
LEXICON[Cause.DELIVERY] = LEXICON[Cause.DELIVERY] + (
    # (a) so luong — mon hang thieu
    "faltando", "faltou", "falta um", "incompleto",
    "recebi apenas", "recebi somente", "so recebi", "só recebi",
    "veio apenas", "vieram apenas",
    # (b) vo/hu trong luc giao — CUM co ngu canh van chuyen
    "chegou quebrad", "veio quebrad", "quebrado na entrega", "quebrada na entrega",
    "chegou danificad", "veio danificad", "danificado no transporte",
    "caixa amassad", "chegou amassad", "veio amassad", "mal embalad", "violad",
)
LEXICON[Cause.QUALITY] = LEXICON[Cause.QUALITY] + (
    # Ngoai le Vi du 13 — thieu BO PHAN ben trong la loi san pham.
    "faltando peca", "faltando peça", "faltam peca", "faltam peça",
    "peca faltando", "peça faltando", "faltando parafuso",
)
LEXICON[Cause.QUALITY] = LEXICON[Cause.QUALITY] + (
    "nao vale", "não vale", "nao compensa", "não compensa")

# Phu dinh dung truoc tu khoa trong khoang nay thi dao nghia ca menh de.
_NEGATIONS = ("nao ", "não ", "naum ", "n ", "ñ ")
_NEGATION_WINDOW = 25  # so ky tu nhin nguoc lai

# Nguong tre toi thieu de suy ra nguyen nhan giao hang tu bang chung cau truc.
# Khop voi quy tac 2 cua codebook: tre duoi 3 ngay ma khong co binh luan -> unknown.
STRUCTURAL_DELAY_THRESHOLD_DAYS = 3.0


class Provenance(str, Enum):
    """Nhan do AI gan — va do quyet dinh con so co duoc trich vao luan van khong.

    Phan biet nay ton tai vi mot ly do cu the (L26): bo nhan 250 dong hien co do
    MOT MO HINH NGON NGU sinh, nguoi nghien cuu ra soat lai. Do la phuong phap hop
    le va co tien le, nhung do dung cua no CHUA duoc kiem chung tren mau doc lap.

    Bo nhan do van dung duoc — de chay het chu trinh, kiem tra luong thong tin va
    dung cac artifact. Cai KHONG duoc phep la de con so sinh ra tu no lan vao
    Chuong 5 nhu ket qua nghien cuu.

    Vi vay `provenance` KHONG CO GIA TRI MAC DINH: moi noi tao `GoldLabels` deu
    buoc phai khai bao. Cung ky luat voi `degradation_level` cua `Decision` — quen
    mot cho la loi tai cho, khong phai mot con so sai lang le di tiep.
    """

    HUMAN_INDEPENDENT = "human_independent"
    MODEL_ASSISTED_PROVISIONAL = "model_assisted_provisional"

    @property
    def citable(self) -> bool:
        """Con so do tren nguon nay co duoc trich vao luan van khong."""
        return self is Provenance.HUMAN_INDEPENDENT

    @property
    def banner(self) -> str:
        if self.citable:
            return "Gold set do nguoi gan doc lap — ket qua trich dan duoc."
        return ("!! TAM THOI: nhan do mo hinh sinh, nguoi ra soat; do dung CHUA kiem "
                "chung tren mau doc lap (L26). Moi con so duoi day dung de KIEM TRA "
                "LUONG THONG TIN, KHONG duoc trich vao Chuong 5.")


@dataclass(frozen=True)
class GoldLabels:
    """Nhan dung de danh gia. Weak label khong bao gio vao duoc day."""

    frame: pd.DataFrame
    provenance: Provenance
    source: str = "human_annotated"

    def __post_init__(self) -> None:
        missing = set(CAUSE_COLUMNS) - set(self.frame.columns)
        if missing:
            raise ValueError(f"gold set thieu cot nhan: {sorted(missing)}")
        if not isinstance(self.provenance, Provenance):
            raise TypeError("provenance phai la Provenance — khong nhan chuoi tu do")

    @property
    def citable(self) -> bool:
        return self.provenance.citable


@dataclass(frozen=True)
class WeakLabels:
    """Nhan tu sinh bang tu khoa. CHI duoc dung de pre-train."""

    frame: pd.DataFrame
    source: str = "keyword_lexicon"

    def for_evaluation(self):
        """Chan duong duy nhat co the lam weak label lot vao danh gia."""
        raise WeakLabelInEvaluation(
            "Weak label khong duoc dung lam thuoc do. Rang buoc C2: moi con so ve "
            "quy ket nguyen nhan phai do tren gold set do nguoi gan."
        )


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).lower().strip())


def _is_negated(text: str, position: int) -> bool:
    """Co tu phu dinh ngay truoc tu khoa hay khong."""
    window = text[max(0, position - _NEGATION_WINDOW):position]
    return any(neg in window for neg in _NEGATIONS)


def _match_causes(text: str) -> set[Cause]:
    found: set[Cause] = set()
    normalized = _normalize(text)
    if not normalized:
        return found
    for cause, keywords in LEXICON.items():
        for keyword in keywords:
            index = normalized.find(keyword)
            if index >= 0 and not _is_negated(normalized, index):
                found.add(cause)
                break
    return found


def label_dissatisfaction(df: pd.DataFrame, max_rating: int = DISSATISFIED_MAX_RATING) -> pd.Series:
    """Nhan muc tieu cua giai doan 1. Nguong mac dinh <=2; phan tich do nhay dung <=3."""
    return df["rating"] <= max_rating


def make_weak_labels(df: pd.DataFrame) -> WeakLabels:
    """Sinh weak label DA NHAN tu van ban, co bo sung bang chung cau truc.

    Khong dung argmax o bat ky buoc nao: mot don co the mang nhieu nguyen nhan, va
    do chinh la thu co che canh tranh sinh ra de bat (DP2).
    """
    text = (df.get("review_title", "").fillna("").astype(str) + " "
            + df.get("review_content", "").fillna("").astype(str))
    matches = text.map(_match_causes)

    out = pd.DataFrame(index=df.index)
    for cause in (Cause.DELIVERY, Cause.QUALITY, Cause.SERVICE):
        out[f"cause_{cause.value}"] = matches.map(lambda s, c=cause: int(c in s))

    # Bang chung cau truc: chi ap dung khi van ban khong noi len dieu gi, va chi khi
    # muc tre vuot nguong — giong quy tac 2 cua codebook cho nguoi gan nhan.
    silent = out[list(CAUSE_COLUMNS)].sum(axis=1) == 0
    late_enough = df["delivery_delay_days"] > STRUCTURAL_DELAY_THRESHOLD_DAYS
    out.loc[silent & late_enough, "cause_delivery"] = 1

    out["cause_unknown"] = (out[list(CAUSE_COLUMNS)].sum(axis=1) == 0).astype(int)
    out.insert(0, "order_id", df["order_id"].to_numpy())
    return WeakLabels(frame=out)


def load_gold_labels(path, *, provenance: Provenance) -> GoldLabels:
    """Nap gold set da gan nhan tu CSV.

    `provenance` la tham so BAT BUOC va khong co mac dinh — xem docstring cua
    `Provenance`. Nguoi goi phai noi ro nhan nay tu dau ra.
    """
    frame = pd.read_csv(path, encoding="utf-8-sig")
    for col in (*CAUSE_COLUMNS, "cause_unknown"):
        if col in frame.columns:
            frame[col] = pd.to_numeric(frame[col], errors="coerce").fillna(0).astype(int)
    return GoldLabels(frame=frame, provenance=provenance)
