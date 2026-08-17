"""WP3 / T3.4 — Head quy ket nguyen nhan tren van ban.

Phuc vu: RQ3 (tang A — 74,77% don bat man co van ban).

BA CAI DAT, MOT GIAO DIEN. Quality Analyst va Service Analyst phu thuoc vao GIAO
DIEN `CauseHead` chu khong vao cai dat, nen doi head la doi MOT THAM SO — khong
dong nao trong `agents/` phai sua.

| Lop                   | Trang thai | Do tin cay      | macro-F1 tren gold |
|-----------------------|------------|-----------------|--------------------|
| `LexiconCauseHead`    | ban tam    | HANG SO (2 gia tri) | 0,2196         |
| `TfidfCauseHead`      | **MAC DINH** | xac suat that (253 gia tri) | **0,4730** |
| `BERTimbauCauseHead`  | chua cai   | —               | —                  |

TU 11/08, MAC DINH LA `TfidfCauseHead`. Ly do do duoc, khong phai suy doan:

  * macro-F1 tren 250 dong gold: **0,2196 -> 0,4730**, thang o CA BON nguyen nhan.
    Chenh lon nhat o recall cua `delivery` (0,269 -> 0,703) — dung co che du doan:
    danh sach tu khoa bo sot moi cach dien dat khong nam trong danh sach.
  * `LexiconCauseHead` sinh ra DUNG HAI gia tri do tin cay tren toan bo 250 don x 4
    nguyen nhan. Hau qua: `bid_entropy` — chi so rieng cua DP2 — vo nghia vi moi bid
    tu tin bang nhau, va hieu chuan (T7.3b) bat kha thi tren dau ra hai gia tri.

`LexiconCauseHead` KHONG bi xoa, va no giu hai vai tro that:

  1. Sinh WEAK LABEL de huan luyen chinh `TfidfCauseHead` (`data/labels.py`).
  2. Mot phan tich do nhay cho Chuong 5: *"mot head huan luyen mua them duoc gi so
     voi mot danh sach tu khoa"* — 0,2196 -> 0,4730 la cau tra loi dinh luong.

Thuoc tinh `is_placeholder` phan biet hai vai tro do va duoc test canh.
Do lai toan bo bang tren: `python -m masdss.cli.compare_heads`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from masdss.core.ontology import Cause, Evidence, OrderCase
from masdss.data.labels import LEXICON, _match_causes


@runtime_checkable
class CauseHead(Protocol):
    """Giao dien ma Quality/Service Analyst phu thuoc vao."""

    name: str
    cost_ms: float
    is_placeholder: bool
    prior_confidence: float

    def can_handle(self, case: OrderCase) -> bool: ...

    def score(self, case: OrderCase, cause: Cause) -> tuple[float, tuple[Evidence, ...]]: ...


@dataclass
class LexiconCauseHead:
    """[TAM THOI] Quy ket tu bo tu khoa. Se bi thay boi BERTimbau o T3.4.

    Do tin cay tra ve la HANG SO co chu dich: mot bo tu khoa khong sinh ra duoc
    xac suat co y nghia, va gia vo rang no lam duoc se lam sai lech toan bo phien
    dau thau. Hang so nay chi vua du vuot nguong tau de chuoi xu ly chay duoc.
    """

    name: str = "lexicon_cause_head"
    cost_ms: float = 0.4
    is_placeholder: bool = True
    fixed_confidence: float = 0.55
    prior_confidence: float = 0.55   # pha 1 Contract Net

    def can_handle(self, case: OrderCase) -> bool:
        """Dieu kien REFUSE cua Quality/Service Analyst: khong co van ban.

        Day la ranh gioi tang A / tang B, va la tinh huong kho (b) cua RQ3.
        """
        return case.has_text_evidence

    def score(self, case: OrderCase, cause: Cause) -> tuple[float, tuple[Evidence, ...]]:
        if not self.can_handle(case):
            return 0.0, ()

        matched = _match_causes(case.review_text or "")
        if cause not in matched:
            return 0.0, ()

        keyword = next(
            (k for k in LEXICON[cause] if k in (case.review_text or "").lower()),
            cause.value,
        )
        evidence = (
            Evidence(
                kind="text_span",
                detail=f"binh luan chua '{keyword}'",
                value=None,
            ),
        )
        return self.fixed_confidence, evidence


@dataclass
class TfidfCauseHead:
    """T3.4 — head da nhan HUAN LUYEN, khong con la bo tu khoa.

    VI SAO TF-IDF CHU KHONG PHAI BERTimbau. Ban BERTimbau can `torch` (~1,5 GB) va
    chua duoc cai. Ban nay dung TF-IDF tren n-gram tu va ky tu, mot lop hoi quy
    logistic cho MOI nguyen nhan (one-vs-rest). N-gram ky tu quan trong hon binh
    thuong o day: tieng Bo trong du lieu Olist sai chinh ta rat nhieu (`nao`/`não`,
    `n`, `naum`), va n-gram ky tu chiu duoc bien the do — dung khuyet diem ma bo
    tu khoa mac phai.

    BA DIEU LAM DUOC MA `LexiconCauseHead` KHONG:

      1. Do tin cay la XAC SUAT THAT, khac nhau theo tung don. Bo tu khoa tra hang
         so, va mot hang so lam moi phien dau thau mat y nghia (`bid_entropy` cua
         no luon bang nhau).
      2. DA NHAN thuc su: bon bo phan loai doc lap, khong `argmax`. Do la dieu kien
         de DP2 co gi de chung minh.
      3. BANG CHUNG lay tu chinh mo hinh — token co dong gop duong lon nhat va co
         mat trong cau. Bo tu khoa chi noi duoc "co chua tu X".

    RANH GIOI PHAI GIU. Huan luyen tren WEAK LABEL (tu khoa) tren tap train lon;
    gold set KHONG duoc dung de huan luyen o day. Do la rang buoc C2, va no duoc
    giu bang cach `fit()` chi nhan weak label. Danh gia tren gold set nam o
    `evaluation/attribution.py`, va o do dung du doan OUT-OF-FOLD (loi L04).
    """

    name: str = "tfidf_cause_head"
    # Gia DO DUOC, khong phai gia uoc luong: p95 = 1,275 ms moi loi goi tren 400 case
    # that (p50 = 0,897). Con so cu la 12,0 — toi dat bang cam tinh va no sai gan 10
    # lan, du de bai toan phan bo ngan sach loai han analyst van ban khoi case rui ro
    # thap. Do la nguon goc cua loi L27. Do lai bang:
    #     python -m masdss.cli.compare_heads
    cost_ms: float = 1.3
    is_placeholder: bool = False
    prior_confidence: float = 0.5
    min_confidence: float = 0.15   # duoi muc nay coi nhu khong co bang chung

    def __post_init__(self) -> None:
        self._models: dict[Cause, object] = {}
        self._vectorizer = None
        self._feature_names = None

    # -- huan luyen ---------------------------------------------------------

    def fit(self, texts, labels: dict[Cause, list[int]], *, seed: int = 0) -> "TfidfCauseHead":
        """Huan luyen tren WEAK LABEL. Gold set khong duoc vao day (rang buoc C2)."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import FeatureUnion

        texts = [str(t or "") for t in texts]
        self._vectorizer = FeatureUnion([
            ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=3, sublinear_tf=True)),
            ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                                     min_df=3, sublinear_tf=True)),
        ])
        matrix = self._vectorizer.fit_transform(texts)
        self._feature_names = self._vectorizer.get_feature_names_out()

        for cause, y in labels.items():
            if sum(y) < 10:      # qua it duong de hoc bat cu dieu gi
                continue
            model = LogisticRegression(max_iter=2000, C=1.0, random_state=seed,
                                       class_weight="balanced")
            model.fit(matrix, y)
            self._models[cause] = model
        return self

    @property
    def fitted(self) -> bool:
        return bool(self._models)

    def predict_proba(self, texts) -> dict[Cause, list[float]]:
        matrix = self._vectorizer.transform([str(t or "") for t in texts])
        return {cause: model.predict_proba(matrix)[:, 1].tolist()
                for cause, model in self._models.items()}

    # -- giao dien CauseHead ------------------------------------------------

    def can_handle(self, case: OrderCase) -> bool:
        return self.fitted and case.has_text_evidence

    def score(self, case: OrderCase, cause: Cause) -> tuple[float, tuple[Evidence, ...]]:
        if not self.can_handle(case) or cause not in self._models:
            return 0.0, ()

        text = case.review_text or ""
        matrix = self._vectorizer.transform([text])
        probability = float(self._models[cause].predict_proba(matrix)[0, 1])
        if probability < self.min_confidence:
            return 0.0, ()
        return probability, self._evidence(matrix, cause)

    def _evidence(self, matrix, cause: Cause) -> tuple[Evidence, ...]:
        """Token dong gop duong lon nhat CO MAT trong cau.

        Day la bang chung cua chinh mo hinh, khong phai mot tu khoa cai san. Chi
        lay n-gram tu — n-gram ky tu giup phan loai nhung khong doc duoc voi nguoi.
        """
        import numpy as np

        coefficients = self._models[cause].coef_[0]
        row = matrix.tocoo()
        contributions = [(coefficients[j] * v, self._feature_names[j])
                         for j, v in zip(row.col, row.data)]
        readable = [(c, name) for c, name in contributions
                    if c > 0 and not name.startswith("char__")]
        readable.sort(reverse=True)
        return tuple(
            Evidence(kind="text_span", detail=f"'{name.split('__', 1)[-1]}'",
                     value=round(float(contribution), 4))
            for contribution, name in readable[:3]
        )


@dataclass
class BERTimbauCauseHead:
    """[CHUA CAI DAT] Ban that cua T3.4.

    Giu lop rong o day de ranh gioi thay the la tuong minh: khi T3.4 xong, chi
    dien vao lop nay va doi mot dong o `system/app.py`.
    """

    name: str = "bertimbau_cause_head"
    cost_ms: float = 45.0
    is_placeholder: bool = False
    prior_confidence: float = 0.5

    def can_handle(self, case: OrderCase) -> bool:
        raise NotImplementedError("T3.4 — can `torch` va gold set da gan nhan")

    def score(self, case: OrderCase, cause: Cause) -> tuple[float, tuple[Evidence, ...]]:
        raise NotImplementedError("T3.4 — can `torch` va gold set da gan nhan")
