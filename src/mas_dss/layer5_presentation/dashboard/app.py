"""5.1 Manager Dashboard (Streamlit).

Bốn khối, bám đúng đề xuất kiến trúc: KPI — case rủi ro — phân bố nguyên nhân — hành động
khuyến nghị; cộng một tab so sánh MAS-DSS với báo cáo kiểu MIS để nhà quản lý thấy trực
tiếp phần "giá trị tăng thêm" của hệ đa tác tử.

Chạy: streamlit run src/mas_dss/layer5_presentation/dashboard/app.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from mas_dss.common.config import PROJECT_ROOT, load_config  # noqa: E402
from mas_dss.layer1_data_integration.feature_store import FeatureStore  # noqa: E402

st.set_page_config(page_title="MAS-DSS | E-Commerce", layout="wide")

RESULTS = PROJECT_ROOT / "reports/results"


@st.cache_data
def load_cases() -> pd.DataFrame:
    path = RESULTS / "intervention_cases.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data
def load_orders() -> pd.DataFrame:
    try:
        return FeatureStore(load_config()).load_frame()
    except FileNotFoundError:
        return pd.DataFrame()


@st.cache_data
def load_json(name: str) -> dict | list | None:
    path = RESULTS / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


cases = load_cases()
orders = load_orders()

st.title("Hệ hỗ trợ ra quyết định đa tác tử — Thương mại điện tử")

if cases.empty:
    st.warning(
        "Chưa có dữ liệu case. Chạy lần lượt: `build_dataset` → `train_models` → `run_pipeline`."
    )
    st.stop()

tab_kpi, tab_cases, tab_bench = st.tabs(
    ["KPI & Nguyên nhân", "Case cần can thiệp", "MAS-DSS vs MIS"]
)

with tab_kpi:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Đơn được xử lý", f"{len(cases):,}")
    c2.metric("Case khẩn cấp", int((cases["status"] == "urgent").sum()))
    c3.metric("Rủi ro cao", int((cases["risk_level"] == "high").sum()))
    c4.metric("Rủi ro TB (risk score)", f"{cases['risk_score'].mean():.2f}")

    left, right = st.columns(2)
    with left:
        st.subheader("Phân bố nguyên nhân rủi ro")
        dist = cases["cause_label"].value_counts().reset_index()
        dist.columns = ["cause", "n"]
        st.plotly_chart(
            px.pie(dist, names="cause", values="n", hole=0.45), use_container_width=True
        )
    with right:
        st.subheader("Hành động được khuyến nghị")
        actions = (
            cases["actions"].str.split("|").explode().value_counts().head(10).reset_index()
        )
        actions.columns = ["action", "n"]
        st.plotly_chart(
            px.bar(actions, x="n", y="action", orientation="h"), use_container_width=True
        )

    st.subheader("Rủi ro theo nhóm sản phẩm")
    by_cat = (
        cases.groupby("product_category")
        .agg(n_cases=("order_id", "count"), avg_risk=("risk_score", "mean"))
        .sort_values("n_cases", ascending=False)
        .head(15)
        .reset_index()
    )
    st.plotly_chart(
        px.bar(by_cat, x="product_category", y="n_cases", color="avg_risk"),
        use_container_width=True,
    )

with tab_cases:
    st.subheader("Danh sách can thiệp")
    f1, f2, f3 = st.columns(3)
    sev = f1.multiselect("Mức độ", sorted(cases["severity"].unique()))
    cause = f2.multiselect("Nguyên nhân", sorted(cases["cause_label"].dropna().unique()))
    status = f3.multiselect("Trạng thái", sorted(cases["status"].unique()))

    view = cases.copy()
    if sev:
        view = view[view["severity"].isin(sev)]
    if cause:
        view = view[view["cause_label"].isin(cause)]
    if status:
        view = view[view["status"].isin(status)]

    view = view.sort_values("risk_score", ascending=False)
    st.dataframe(
        view[
            [
                "order_id",
                "risk_level",
                "risk_score",
                "cause_label",
                "cause_probability",
                "actions",
                "severity",
                "escalate_to",
                "status",
            ]
        ],
        use_container_width=True,
        height=380,
    )

    st.subheader("Decision trace — vì sao có khuyến nghị này")
    if len(view):
        oid = st.selectbox("Chọn đơn", view["order_id"].head(200))
        row = view[view["order_id"] == oid].iloc[0]
        st.info(row["narrative"])
        st.caption(f"Luật kích hoạt: {row['matched_rules']} | Chuyển tới: {row['escalate_to']}")

with tab_bench:
    st.subheader("So sánh MAS-DSS với MIS và mô hình ML đơn lẻ")
    bench = load_json("benchmark.json")
    if not bench:
        st.warning("Chưa có kết quả. Chạy: `python -m mas_dss.pipelines.run_evaluation`")
    else:
        bdf = pd.DataFrame(bench)
        cols = [
            c
            for c in [
                "system",
                "accuracy",
                "macro_f1",
                "recall",
                "roc_auc",
                "detection_rate",
                "pipeline_completeness",
                "action_cause_fit",
                "latency_per_case_ms",
            ]
            if c in bdf.columns
        ]
        st.dataframe(bdf[cols].round(4), use_container_width=True)
        st.plotly_chart(
            px.bar(bdf, x="system", y="macro_f1", color="system", title="Macro F1"),
            use_container_width=True,
        )
        st.caption(
            "MIS và single-model có `pipeline_completeness = 0` vì chúng không phân loại "
            "nguyên nhân và không sinh hành động quản trị — đó chính là khoảng cách mà "
            "kiến trúc MAS-DSS lấp đầy."
        )

    if not orders.empty:
        st.subheader("Báo cáo kiểu MIS (đối chứng)")
        st.dataframe(
            orders.groupby("product_category")
            .agg(
                orders=("order_id", "count"),
                dissatisfaction_rate=("is_dissatisfied", "mean"),
                avg_review=("review_score", "mean"),
            )
            .sort_values("orders", ascending=False)
            .head(15)
            .round(3),
            use_container_width=True,
        )
