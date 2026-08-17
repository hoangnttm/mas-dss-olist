"""WP1 / T1.1 — Nap va ghep 9 bang Olist thanh bang don hang chuan hoa.

Phuc vu: ca ba RQ (nen du lieu).

HAI DIEU KHONG LAM O DAY, co chu dich:

  1. KHONG tinh `review_lag_days`. Day la ro ri nhan trang tron — no chi ton tai
     sau khi danh gia da duoc viet, ma diem danh gia chinh la nhan. Khong tinh
     ngay tu dau thi khong the vo tinh dung nham (build-plan.md T1.2).

  2. KHONG tao dac trung `has_comment` cho giai doan 1. Su hien dien cua binh
     luan tuong quan rat manh voi nhan (76,5% o muc 1 sao so voi 31,2% o muc 4
     sao), nen o T3 no la ro ri nhan ngang hang voi review_lag_days (rang buoc C4).
     Cot `tier` duoi day chi dung de PHAN TANG MAU gold set va de bao cao mo ta,
     khong bao gio duoc dua vao feature set cua T2/T3.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from masdss.config import CONFIG

DISSATISFIED_MAX_RATING = 2  # nguong chinh; phan tich do nhay dung <= 3


@dataclass(frozen=True)
class RawTables:
    reviews: pd.DataFrame
    orders: pd.DataFrame
    items: pd.DataFrame
    products: pd.DataFrame
    categories: pd.DataFrame
    sellers: pd.DataFrame
    customers: pd.DataFrame
    geolocation: pd.DataFrame
    payments: pd.DataFrame


def load_raw(raw_dir: Path | None = None) -> RawTables:
    root = raw_dir or CONFIG.paths.raw
    return RawTables(
        reviews=pd.read_csv(root / "olist_order_reviews.csv"),
        orders=pd.read_csv(root / "olist_orders_dataset.csv"),
        items=pd.read_csv(root / "olist_order_items_dataset.csv"),
        products=pd.read_csv(root / "olist_products_dataset.csv"),
        categories=pd.read_csv(root / "product_category_name_translation.csv",
                               encoding="utf-8-sig"),
        sellers=pd.read_csv(root / "olist_sellers_dataset.csv"),
        customers=pd.read_csv(root / "olist_customers_dataset.csv"),
        geolocation=pd.read_csv(root / "olist_geolocation_dataset.csv"),
        payments=pd.read_csv(root / "olist_order_payments_dataset.csv"),
    )


def _dedupe_reviews(reviews: pd.DataFrame) -> pd.DataFrame:
    """Mot don co the co nhieu ban ghi danh gia. Giu ban SOM NHAT, tat dinh."""
    out = reviews.sort_values(["order_id", "creation_timestamp", "review_id"])
    return out.drop_duplicates(subset="order_id", keep="first")


def _aggregate_items(items: pd.DataFrame, products: pd.DataFrame,
                     categories: pd.DataFrame) -> pd.DataFrame:
    """Gop dong hang ve muc don hang."""
    enriched = items.merge(products[["product_id", "product_category_name"]],
                           on="product_id", how="left")
    enriched = enriched.merge(categories, on="product_category_name", how="left")

    grouped = enriched.groupby("order_id").agg(
        n_items=("order_item_id", "count"),
        price=("price", "sum"),
        freight_value=("freight_value", "sum"),
        n_sellers=("seller_id", "nunique"),
        category=("product_category_name_english", "first"),
    ).reset_index()
    grouped["category"] = grouped["category"].fillna("unknown")
    return grouped


EARTH_RADIUS_KM = 6371.0


def _seller_features(items: pd.DataFrame, orders: pd.DataFrame, sellers: pd.DataFrame,
                     customers: pd.DataFrame, geolocation: pd.DataFrame) -> pd.DataFrame:
    """Ba dac trung phia nguoi ban, tat ca deu BIET DUOC TU LUC DAT HANG.

    `seller_prior_orders` la cho de sai nhat va da duoc do: dem luy tien theo thoi
    gian, CHI tinh nhung don mua TRUOC don hien tai. Cach lam thong thuong trong cac
    notebook Olist tren mang la dem tong so don cua nguoi ban tren TOAN TAP — do la
    ro ri thoi gian, vi no dung don tuong lai de du bao don hien tai.

    Do lech duoc do truc tiep: hai ban tuong quan 0,809, va ban toan tap thoi phong
    PR-AUC them 0,005. Xem L31.
    """
    import numpy as np

    x = items[["order_id", "seller_id", "shipping_limit_date", "price"]].merge(
        orders[["order_id", "order_purchase_timestamp", "customer_id"]],
        on="order_id", how="left")
    x["shipping_limit_date"] = pd.to_datetime(x["shipping_limit_date"], errors="coerce")

    # Thu tu TAT DINH truoc khi dem luy tien — hai don cung dau thoi gian phai luon
    # duoc xep cung mot thu tu, neu khong ket qua doi giua hai lan chay.
    x = x.sort_values(["order_purchase_timestamp", "order_id", "seller_id"],
                      kind="mergesort")
    x["seller_prior_orders"] = x.groupby("seller_id").cumcount()

    x["ships_in_days"] = (
        x["shipping_limit_date"] - x["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400

    centroid = geolocation.groupby("geolocation_zip_code_prefix")[
        ["geolocation_lat", "geolocation_lng"]].median()
    x = x.merge(sellers[["seller_id", "seller_zip_code_prefix"]], on="seller_id", how="left")
    x = x.merge(customers[["customer_id", "customer_zip_code_prefix"]],
                on="customer_id", how="left")
    coords = {}
    for side, column in (("s", "seller_zip_code_prefix"), ("c", "customer_zip_code_prefix")):
        found = centroid.reindex(x[column])
        coords[f"{side}_lat"] = np.radians(found["geolocation_lat"].to_numpy())
        coords[f"{side}_lng"] = np.radians(found["geolocation_lng"].to_numpy())
    cosine = (np.sin(coords["s_lat"]) * np.sin(coords["c_lat"])
              + np.cos(coords["s_lat"]) * np.cos(coords["c_lat"])
              * np.cos(coords["c_lng"] - coords["s_lng"]))
    x["seller_distance_km"] = EARTH_RADIUS_KM * np.arccos(np.clip(cosine, -1.0, 1.0))

    # Don nhieu nguoi ban (1,3%): lay truong hop XAU NHAT — xa nhat, han giao dai
    # nhat, nguoi ban it kinh nghiem nhat. Trung binh se lam nhoe dung tin hieu rui ro.
    return x.groupby("order_id").agg(
        ships_in_days=("ships_in_days", "max"),
        seller_distance_km=("seller_distance_km", "max"),
        seller_prior_orders=("seller_prior_orders", "min"),
    ).reset_index()


def _payment_features(payments: pd.DataFrame) -> pd.DataFrame:
    """Dac trung thanh toan — biet tu luc dat hang."""
    aggregated = payments.groupby("order_id").agg(
        payment_installments=("payment_installments", "max"),
        payment_sequences=("payment_sequential", "max"),
    ).reset_index()
    main = (payments.sort_values("payment_value", ascending=False)
            .drop_duplicates("order_id")[["order_id", "payment_type"]])
    merged = aggregated.merge(main, on="order_id", how="left")
    # `.eq()` sau merge co the ra dtype `object` khi co gia tri thieu, va LightGBM
    # tu choi dtype do. Ep ve bool tuong minh thay vi de no troi.
    merged["paid_by_credit_card"] = merged["payment_type"].eq("credit_card").astype(bool)
    return merged.drop(columns=["payment_type"])


def _deadline_features(df: pd.DataFrame, cutoff_days: int) -> pd.DataFrame:
    """Trang thai QUAN SAT DUOC tai moc T3 = NGAY MUA + `cutoff_days`.

    DAY LA CHO SUA CUA HAI LOI, L30 roi L33.

    L30: moc T3 truoc day duoc hieu la SU KIEN "sau khi giao xong", nen
    `delivery_delay_days` luon co gia tri. Voi nhung don chua toi, dung do tre thuc
    te la dua ket cuc tuong lai vao dau vao du bao — va do dung la nhom quan trong
    nhat (ty le bat man 71,4% dang van chuyen, 82,8% chua gui, so voi 9,5%).

    L33: ban sua cua L30 neo moc vao HAN GIAO DU KIEN (+3 ngay). Nhung 87,8% danh
    gia duoc viet TRUOC han du kien, nen voi 97,6% so don moc "du bao" nam SAU luc
    khach da viet danh gia. Neo lai vao NGAY MUA — mot moc luon biet truoc va khong
    phu thuoc vao bat ky ket cuc nao.

    Cach xu ly chung: KIEM DUYET BEN PHAI. Chi ghi nhan nhung gi da xay ra tinh den
    moc, va noi ro trang thai bang mot cot thay vi de gia tri thieu — de mo hinh
    khong hoc duoc "thieu du lieu nghia la xau", mau hinh khong ton tai luc trien khai.
    """
    import numpy as np

    cutoff = df["order_purchase_timestamp"] + pd.Timedelta(days=cutoff_days)
    df["t3_cutoff"] = cutoff

    delivered = df["order_delivered_customer_date"].notna() & (
        df["order_delivered_customer_date"] <= cutoff)
    handed_over = df["order_delivered_carrier_date"].notna() & (
        df["order_delivered_carrier_date"] <= cutoff)

    df["delivery_state"] = np.where(delivered, 0, np.where(handed_over, 1, 2))

    # Do tre quan sat duoc, do bang HAN DU KIEN lam goc. Neu da giao tinh den moc thi
    # do la do tre that (am = giao som). Neu chua, ta chi biet "tinh den moc, don dang
    # o cach han du kien chung nay ngay" — dung chinh chan do.
    #
    # Khac ban truoc: chan tren khong con la hang so `cutoff_days`. Voi moc neo theo
    # ngay mua, `cutoff - han du kien` THAY DOI theo tung don, va chinh do lech do la
    # tin hieu: don co han du kien gan hon thi tai moc T3 da sat han hon.
    delay = (df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]
             ).dt.total_seconds() / 86400
    censored = (cutoff - df["order_estimated_delivery_date"]).dt.total_seconds() / 86400
    df["observed_delay_days"] = np.where(delivered, delay, censored)

    # Thoi gian con lai den han cam ket, tinh tai moc. Am nghia la DA qua han ngay
    # tai thoi diem ra quyet dinh. Day la tin hieu "tien do van chuyen" ma rang buoc
    # C3 chi ra — khac han voi ket cuc giao hang, thu chi biet duoc sau T4.
    df["days_to_deadline"] = -censored

    handover = (df["order_delivered_carrier_date"] - df["order_purchase_timestamp"]
                ).dt.total_seconds() / 86400
    df["observed_handover_days"] = np.where(handed_over, handover, float(cutoff_days))
    return df


def build_order_table(raw: RawTables | None = None,
                      cutoff_days: int | None = None) -> pd.DataFrame:
    """Bang don hang chuan hoa: mot dong mot don co danh gia.

    KHONG LOC THEO `order_status`. 2.841 don (2,88%) chua bao gio duoc giao nhung
    van co danh gia, va ty le bat man cua chung la 77,9% so voi 12,8% cua don da
    giao. Loai chung di la vut bo dung nhom can can thiep nhat — va do la dieu ma
    ca hai cai dat tham chieu tren GitHub deu lam. Thay vao do, trang thai giao
    hang tai moc T3 duoc ma hoa tuong minh qua `delivery_state`. Xem L30.
    """
    raw = raw or load_raw()
    cutoff_days = CONFIG.t3_cutoff_days if cutoff_days is None else cutoff_days

    reviews = _dedupe_reviews(raw.reviews)
    orders = raw.orders.copy()
    for col in ("order_purchase_timestamp", "order_delivered_carrier_date",
                "order_delivered_customer_date", "order_estimated_delivery_date"):
        orders[col] = pd.to_datetime(orders[col], errors="coerce")

    df = reviews.merge(orders, on="order_id", how="inner")
    df = df.merge(_aggregate_items(raw.items, raw.products, raw.categories),
                  on="order_id", how="left")
    df = df.merge(_seller_features(raw.items, orders, raw.sellers,
                                   raw.customers, raw.geolocation),
                  on="order_id", how="left")
    df = df.merge(_payment_features(raw.payments), on="order_id", how="left")
    # DUNG MOT don trong 98.673 khong co ban ghi thanh toan nao. Merge trai bien ca
    # cot bool thanh `object`, va LightGBM tu choi dtype do. Ep lai tuong minh —
    # `False` o day nghia la "khong ro", va voi mot dong thi khong anh huong gi.
    df["paid_by_credit_card"] = df["paid_by_credit_card"].fillna(False).astype(bool)
    df = _deadline_features(df, cutoff_days)

    # --- dac trung thoi gian giao hang ---
    df["delivery_days"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
    df["delivery_delay_days"] = (
        df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400
    df["carrier_handover_days"] = (
        df["order_delivered_carrier_date"] - df["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
    df["is_late"] = df["delivery_delay_days"] > 0

    # --- dac trung gia ---
    import numpy as np

    total = df["price"].fillna(0) + df["freight_value"].fillna(0)
    df["freight_ratio"] = df["freight_value"] / total.replace(0, np.nan)

    # --- rang buoc o muc TONG THE, khong phai muc dac trung ---
    #
    # Mot moc quyet dinh rang buoc HAI thu: dac trung nao ton tai, va don nao da toi
    # duoc moc do. `FeatureSet(decision_point)` chi cuong che ve thu nhat. Ve thu hai
    # bo ngo la nguyen nhan goc cua CA L30 LAN L33 — hai lan lot cung mot cho.
    #
    # Mot don chi thuoc tong the du bao tai T3 neu danh gia cua no duoc viet SAU moc.
    # Neu khach da viet danh gia truoc do thi khong con gi de phuc hoi, va viec "du
    # bao" no chi la doc lai mot su kien da xay ra.
    df["review_created_at"] = pd.to_datetime(df["creation_timestamp"], errors="coerce")
    df["reachable_at_t3"] = df["review_created_at"] > df["t3_cutoff"]

    # --- nhan va phan tang ---
    df["is_dissatisfied"] = df["rating"] <= DISSATISFIED_MAX_RATING
    content = df["review_content"].fillna("").astype(str).str.strip()
    title = df["review_title"].fillna("").astype(str).str.strip()
    df["has_content"] = content.str.len() > 0
    df["has_title"] = title.str.len() > 0
    # Tang A/B lay theo review_content — phan van ban co gia tri phan tich.
    # Gop them title chi them 105 don, doi lai dua vao mot loai bang chung khac chat.
    df["tier"] = df["has_content"].map({True: "A", False: "B"})

    return df


def describe_m0(df: pd.DataFrame) -> dict:
    """Gate G1 — thong ke mo ta phai khop bang M0.

    Xem research-questions-objectives.md §0.1.
    """
    dissatisfied = df[df["is_dissatisfied"]]
    n_total, n_dis = len(df), len(dissatisfied)
    n_content = int(dissatisfied["has_content"].sum())
    n_either = int((dissatisfied["has_content"] | dissatisfied["has_title"]).sum())
    return {
        "n_reviews": n_total,
        "n_dissatisfied": n_dis,
        "pct_dissatisfied": round(100 * n_dis / n_total, 2),
        "tier_a_has_content": n_content,
        "pct_tier_a": round(100 * n_content / n_dis, 2),
        "tier_b_no_content": n_dis - n_content,
        "pct_tier_b": round(100 * (n_dis - n_content) / n_dis, 2),
        "no_text_at_all": n_dis - n_either,
        "pct_no_text_at_all": round(100 * (n_dis - n_either) / n_dis, 2),
    }


def comment_rate_by_rating(df: pd.DataFrame) -> pd.DataFrame:
    """Phan bo hinh chu U — phat hien phu dang dua vao Chuong 5."""
    out = df.groupby("rating").agg(
        n_reviews=("review_id", "count"),
        n_has_content=("has_content", "sum"),
    ).reset_index()
    out["pct"] = (100 * out["n_has_content"] / out["n_reviews"]).round(2)
    return out
