from pathlib import Path

import pandas as pd


RAW = Path("data/raw")
PROCESSED = Path("data/processed")
CHARTS = Path("dashboard/screenshots")


def svg_bar_chart(df, label_col, value_col, title, output_path, value_format="{:.1%}"):
    width = 960
    height = 500
    margin_left = 260
    margin_right = 90
    margin_top = 72
    bar_gap = 18
    bar_height = 42
    plot_width = width - margin_left - margin_right
    max_value = max(df[value_col].max(), 0.01)
    rows = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="32" y="42" font-family="Arial" font-size="24" font-weight="700" fill="#172033">{title}</text>',
    ]
    for idx, row in df.reset_index(drop=True).iterrows():
        y = margin_top + idx * (bar_height + bar_gap)
        bar_width = int((row[value_col] / max_value) * plot_width)
        rows.extend(
            [
                f'<text x="32" y="{y + 28}" font-family="Arial" font-size="15" fill="#172033">{row[label_col]}</text>',
                f'<rect x="{margin_left}" y="{y}" width="{bar_width}" height="{bar_height}" rx="4" fill="#ea580c"/>',
                f'<text x="{margin_left + bar_width + 12}" y="{y + 28}" font-family="Arial" font-size="15" fill="#172033">{value_format.format(row[value_col])}</text>',
            ]
        )
    rows.append("</svg>")
    output_path.write_text("\n".join(rows), encoding="utf-8")


def seller_tier(row):
    if row["late_delivery_rate"] <= 0.08 and row["avg_review_score"] >= 4.4:
        return "Top seller"
    if row["late_delivery_rate"] <= 0.16 and row["avg_review_score"] >= 4.0:
        return "Standard seller"
    return "Needs improvement"


def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    CHARTS.mkdir(parents=True, exist_ok=True)

    orders = pd.read_csv(RAW / "olist_orders_dataset.csv", parse_dates=["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"])
    items = pd.read_csv(RAW / "olist_order_items_dataset.csv")
    reviews = pd.read_csv(RAW / "olist_order_reviews_dataset.csv")
    customers = pd.read_csv(RAW / "olist_customers_dataset.csv")
    sellers = pd.read_csv(RAW / "olist_sellers_dataset.csv")
    products = pd.read_csv(RAW / "olist_products_dataset.csv")

    order_items = items.merge(products, on="product_id", how="left").merge(sellers, on="seller_id", how="left")
    df = (
        orders.merge(order_items, on="order_id", how="inner")
        .merge(reviews.groupby("order_id", as_index=False)["review_score"].mean(), on="order_id", how="left")
        .merge(customers, on="customer_id", how="left")
    )
    df["payment_value"] = df["price"] + df["freight_value"]
    df["delivery_days"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days
    df["delivery_delay_days"] = (df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]).dt.days.clip(lower=0)
    df["late_delivery_flag"] = (df["delivery_delay_days"] > 0).astype(int)
    df = df.sort_values(["customer_unique_id", "order_purchase_timestamp"])
    df["customer_order_number"] = df.groupby("customer_unique_id").cumcount() + 1
    df["repeat_customer_flag"] = (df["customer_order_number"] > 1).astype(int)

    seller_base = (
        df.groupby("seller_id", as_index=False)
        .agg(
            seller_orders=("order_id", "nunique"),
            late_delivery_rate=("late_delivery_flag", "mean"),
            avg_review_score=("review_score", "mean"),
        )
    )
    seller_base["seller_tier"] = seller_base.apply(seller_tier, axis=1)
    df = df.merge(seller_base[["seller_id", "seller_tier"]], on="seller_id", how="left")

    category_summary = (
        df.groupby("product_category_name", as_index=False)
        .agg(
            orders=("order_id", "nunique"),
            revenue=("payment_value", "sum"),
            avg_order_value=("payment_value", "mean"),
            avg_review_score=("review_score", "mean"),
            late_delivery_rate=("late_delivery_flag", "mean"),
        )
        .sort_values("revenue", ascending=False)
    )
    seller_summary = (
        df.groupby("seller_tier", as_index=False)
        .agg(
            sellers=("seller_id", "nunique"),
            orders=("order_id", "nunique"),
            revenue=("payment_value", "sum"),
            late_delivery_rate=("late_delivery_flag", "mean"),
            avg_review_score=("review_score", "mean"),
        )
        .sort_values("revenue", ascending=False)
    )
    state_summary = (
        df.groupby("customer_state", as_index=False)
        .agg(
            customers=("customer_unique_id", "nunique"),
            orders=("order_id", "nunique"),
            revenue=("payment_value", "sum"),
            repeat_customer_rate=("repeat_customer_flag", "mean"),
        )
        .sort_values("revenue", ascending=False)
    )
    delivery_review = (
        df.groupby("late_delivery_flag", as_index=False)
        .agg(
            orders=("order_id", "nunique"),
            avg_review_score=("review_score", "mean"),
            avg_delivery_delay_days=("delivery_delay_days", "mean"),
            revenue=("payment_value", "sum"),
        )
    )
    executive = pd.DataFrame(
        [
            {
                "total_orders": df["order_id"].nunique(),
                "total_revenue": round(df["payment_value"].sum(), 2),
                "avg_order_value": round(df["payment_value"].mean(), 2),
                "late_delivery_rate": round(df["late_delivery_flag"].mean(), 4),
                "avg_review_score": round(df["review_score"].mean(), 2),
                "repeat_customer_rate": round(df["repeat_customer_flag"].mean(), 4),
            }
        ]
    )

    df.to_csv(PROCESSED / "orders_enriched.csv", index=False)
    category_summary.to_csv(PROCESSED / "category_revenue_summary.csv", index=False)
    seller_summary.to_csv(PROCESSED / "seller_performance_summary.csv", index=False)
    state_summary.to_csv(PROCESSED / "state_customer_summary.csv", index=False)
    delivery_review.to_csv(PROCESSED / "delivery_review_summary.csv", index=False)
    executive.to_csv(PROCESSED / "executive_kpi_summary.csv", index=False)

    svg_bar_chart(
        category_summary.head(8),
        "product_category_name",
        "revenue",
        "Revenue by Product Category",
        CHARTS / "revenue_by_category.svg",
        value_format="{:.0f}",
    )
    svg_bar_chart(
        seller_summary,
        "seller_tier",
        "late_delivery_rate",
        "Late Delivery Rate by Seller Tier",
        CHARTS / "late_delivery_by_seller_tier.svg",
    )
    print("Created enriched order data, KPI summaries, and dashboard preview charts.")


if __name__ == "__main__":
    main()

