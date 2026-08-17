"""WP8 / T8.2 — Health Monitor: phat hien tac tu SAI MA KHONG CHET.

Phuc vu: RQ1(b) — do nhay va do tre phat hien cua bo giam sat.

Day la thanh phan ma khong engine dieu phoi nao co. LangGraph, Airflow, Prefect —
tat ca deu bat duoc exception, va tat ca deu MU voi mot tac tu tra ve ket qua hop
le nhung sai. Loai loi do khong co log do, khong co canh bao, chi la quyet dinh sai
hang loat. Do la ly do §6.1 xep no la loai loi giet he thong trong thuc te.

HAI CO CHE, va chung khac nhau ve dieu kien ap dung:

  Phuong sai bang khong  — phat hien duoc BAT KE co du lieu tham chieu hay khong.
                           Mot dai luong dang le phai bien thien ma dung yen la
                           bat thuong tu no.

  PSI so voi tham chieu  — can mot phan phoi tham chieu SACH. Neu tham chieu duoc
                           dung tu chinh lan chay dang bi tiem loi thi no da nhiem,
                           va guard mu. Han che nay duoc ghi ro chu khong giau —
                           no la mot phan cua duong cong do nhay ma RQ1 do.

`detection_delay` ghi lai da xu ly bao nhieu case truoc khi canh bao dau tien noi
len. Day la mot trong ba con so ma RQ1 goi la KET QUA THUC NGHIEM THAT.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field

import numpy as np

DEFAULT_WINDOW = 200          # du lon de PSI on dinh
MIN_OBSERVATIONS = 20         # du cho phep kiem tra phuong sai
MIN_PSI_OBSERVATIONS = 100    # PSI can nhieu mau hon nhieu
# NGUONG PSI DUOC HIEU CHUAN TREN LAN CHAY KHOE, khong lay theo quy uoc.
#
# Quy uoc pho bien trong nganh la 0,25. Nguong do KHONG dung duoc o day: giua tap
# validation va tap test co dich chuyen tong the theo thoi gian that (Olist trai
# dai 2016-2018), va PSI tren mot lan chay hoan toan khoe manh da la 0,466. Lay
# nguong 0,25 thi 66% case bi danh dau suy giam trong khi khong co loi nao.
#
# Quy trinh hieu chuan, va no phai duoc mo ta trong Chuong 5:
#   1. Chay he thong KHONG tiem loi   -> PSI = 0,466  (drift thoi gian tu nhien)
#   2. Chay voi lech he thong +0,15   -> PSI = 2,512
#   3. Dat nguong o giua, co bien an toan ve ca hai phia -> 1,0
#
# Day khong phai vong tron: nguong duoc chon tu duong chay khoe, roi do do nhay
# tren cac duong CO loi. Do chinh la phan tich do nhay/do dac hieu ma RQ1(b) yeu cau.
PSI_THRESHOLD = 1.0
VARIANCE_EPSILON = 1e-9


@dataclass(frozen=True)
class Alert:
    component: str
    metric: str
    detail: str
    at_observation: int


@dataclass
class ComponentHealth:
    """Cua so truot cho mot dai luong cua mot thanh phan."""

    component: str
    metric: str
    window: deque = field(default_factory=lambda: deque(maxlen=DEFAULT_WINDOW))
    reference: np.ndarray | None = None
    n_seen: int = 0

    def observe(self, value: float) -> None:
        self.window.append(float(value))
        self.n_seen += 1

    @property
    def variance(self) -> float:
        return float(np.var(self.window)) if len(self.window) >= MIN_OBSERVATIONS else -1.0

    @property
    def variance_check_applies(self) -> bool:
        """Phep kiem tra phuong sai CHI co nghia khi co tham chieu chung to dai
        luong nay dang le phai bien thien.

        MOT LOI NGUYEN LY DA DUOC SUA O DAY. Ban dau guard ket luan "phuong sai
        bang khong => nang luc nen hong" cho MOI dai luong. Nhung mot dai luong co
        the la hang so DO THIET KE — vi du mot capability tra ve do tin cay co dinh.
        Ket luan no hong la sai, va tren lan chay khoe no tao ra 93,7% bao dong gia,
        khien he thong khong dung duoc.

        Menh de dung phai co tien de: "mot dai luong DA BIEN THIEN TRONG HUAN LUYEN
        ma dung yen khi van hanh la bat thuong". Khong co phan phoi tham chieu thi
        khong co tien de, va khong ket luan gi ca.

        HE QUA CAN GHI RO: pham vi phu cua guard bi gioi han o nhung thanh phan co
        phan phoi tham chieu sach. Mo rong sang nhom Analyst doi hoi mot buoc hieu
        chuan rieng (T7.3). Day la gioi han that, khong duoc giau khi bao cao RQ1(b).
        """
        return self.reference is not None and float(np.var(self.reference)) > VARIANCE_EPSILON

    def psi(self, bins: int = 10) -> float:
        """Population Stability Index so voi phan phoi tham chieu.

        HAI SAI LAM DA DUOC SUA O DAY, ca hai deu lam PSI bung no tren du lieu hoan
        toan binh thuong:

        1. KHOANG CHIA CO DINH tren [0,1]. Diem rui ro tap trung manh o vung thap,
           nen phan lon khoang o vung cao rong khong o ca hai phia. Ty le 0 bi chan
           duoi bang mot hang so cuc nho, va log cua ty so giua hai so cuc nho cho
           ra gia tri lon tuy y. Sua: chia khoang theo PHAN VI CUA THAM CHIEU, nen
           moi khoang chua xap xi 10% du lieu tham chieu theo dinh nghia.

        2. CUA SO QUA NHO. Voi 50 quan sat tren 10 khoang, moi khoang trung binh chi
           5 mau — bien dong lay mau tu no da du lam PSI vuot nguong. Sua: yeu cau
           it nhat `MIN_PSI_OBSERVATIONS` quan sat, va chan duoi ty le theo co mau
           thay vi bang mot hang so tuyet doi.

        Truoc khi sua, mot lan chay hoan toan khoe manh cho PSI = 2,911 va 93,7%
        case bi danh dau suy giam.
        """
        if self.reference is None or len(self.window) < MIN_PSI_OBSERVATIONS:
            return -1.0

        quantiles = np.linspace(0.0, 1.0, bins + 1)
        edges = np.unique(np.quantile(self.reference, quantiles))
        if len(edges) < 3:  # tham chieu gan nhu la hang so — PSI khong co nghia
            return -1.0
        edges[0], edges[-1] = -np.inf, np.inf

        ref, _ = np.histogram(self.reference, bins=edges)
        cur, _ = np.histogram(np.array(self.window), bins=edges)
        n_ref, n_cur = max(ref.sum(), 1), max(cur.sum(), 1)
        # Chan duoi theo co mau: mot khoang rong trong cua so nho khong duoc coi la
        # bang khong tuyet doi.
        ref_pct = np.clip(ref / n_ref, 0.5 / n_ref, None)
        cur_pct = np.clip(cur / n_cur, 0.5 / n_cur, None)
        return float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))


@dataclass
class HealthMonitor:
    """Theo doi suc khoe cua tung thanh phan qua cua so truot."""

    window_size: int = DEFAULT_WINDOW
    psi_threshold: float = PSI_THRESHOLD
    _states: dict[tuple[str, str], ComponentHealth] = field(default_factory=dict)
    alerts: list[Alert] = field(default_factory=list)
    _alerted: set[tuple[str, str]] = field(default_factory=set)
    _observations: int = 0

    def set_reference(self, component: str, metric: str, values) -> None:
        """Nap phan phoi tham chieu SACH, lay tu du lieu huan luyen."""
        state = self._state(component, metric)
        state.reference = np.asarray(values, dtype=float)

    def _state(self, component: str, metric: str) -> ComponentHealth:
        key = (component, metric)
        if key not in self._states:
            self._states[key] = ComponentHealth(
                component=component, metric=metric,
                window=deque(maxlen=self.window_size),
            )
        return self._states[key]

    def observe(self, component: str, metric: str, value: float) -> list[Alert]:
        """Ghi nhan mot quan sat va tra ve canh bao MOI (neu co)."""
        self._observations += 1
        state = self._state(component, metric)
        state.observe(value)

        new_alerts: list[Alert] = []
        key = (component, metric)
        if key in self._alerted:
            return new_alerts

        variance = state.variance
        if state.variance_check_applies and 0 <= variance < VARIANCE_EPSILON:
            reference_variance = float(np.var(state.reference))
            new_alerts.append(Alert(
                component, metric,
                f"phuong sai = {variance:.2e} tren {len(state.window)} quan sat, "
                f"trong khi phuong sai tham chieu = {reference_variance:.4f} "
                f"— dai luong dung yen bat thuong, nghi nang luc nen hong",
                state.n_seen,
            ))

        psi = state.psi()
        if psi > self.psi_threshold:
            new_alerts.append(Alert(
                component, metric,
                f"PSI = {psi:.3f} > {self.psi_threshold} so voi phan phoi huan luyen "
                f"— phan phoi da lech",
                state.n_seen,
            ))

        if new_alerts:
            self._alerted.add(key)
            self.alerts.extend(new_alerts)
        return new_alerts

    def is_unhealthy(self, component: str) -> bool:
        return any(a.component == component for a in self.alerts)

    def detection_delay(self, component: str) -> int | None:
        """So case da xu ly truoc khi canh bao dau tien cho thanh phan nay noi len."""
        for alert in self.alerts:
            if alert.component == component:
                return alert.at_observation
        return None

    def report(self) -> list[dict]:
        return [
            {"component": a.component, "metric": a.metric,
             "at_observation": a.at_observation, "detail": a.detail}
            for a in self.alerts
        ]
