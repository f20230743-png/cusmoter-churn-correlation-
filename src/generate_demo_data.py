from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


np.random.seed(42)
out = Path("data/raw")
out.mkdir(parents=True, exist_ok=True)

categories = ["health_beauty", "sports_leisure", "computers_accessories", "furniture_decor", "watches_gifts", "housewares", "auto", "toys"]
states = ["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "DF"]

customers = pd.DataFrame(
    {
        "customer_id": [f"C{i:06d}" for i in range(1, 5201)],
        "customer_unique_id": [f"U{int(np.random.randint(1, 4700)):06d}" for _ in range(5200)],
        "customer_state": np.random.choice(states, 5200, p=[0.42, 0.14, 0.12, 0.08, 0.07, 0.06, 0.06, 0.05]),
    }
)
sellers = pd.DataFrame(
    {
        "seller_id": [f"S{i:05d}" for i in range(1, 501)],
        "seller_state": np.random.choice(states, 500, p=[0.50, 0.10, 0.11, 0.07, 0.07, 0.06, 0.05, 0.04]),
    }
)
products = pd.DataFrame(
    {
        "product_id": [f"P{i:06d}" for i in range(1, 1601)],
        "product_category_name": np.random.choice(categories, 1600),
    }
)

orders = []
items = []
reviews = []
start = datetime(2017, 1, 1)
for i in range(1, 8001):
    order_id = f"O{i:07d}"
    customer = customers.sample(1).iloc[0]
    seller = sellers.sample(1).iloc[0]
    product = products.sample(1).iloc[0]
    purchase = start + timedelta(days=int(np.random.randint(0, 420)), hours=int(np.random.randint(0, 24)))
    estimated_days = int(np.random.randint(6, 22))
    delivery_noise = int(np.random.normal(0, 4))
    delivered = purchase + timedelta(days=max(2, estimated_days + delivery_noise))
    estimated = purchase + timedelta(days=estimated_days)
    category_multiplier = {
        "computers_accessories": 1.8,
        "watches_gifts": 1.6,
        "health_beauty": 1.2,
        "sports_leisure": 1.1,
        "furniture_decor": 1.3,
        "housewares": 0.9,
        "auto": 1.4,
        "toys": 0.8,
    }[product["product_category_name"]]
    price = round(float(np.random.lognormal(mean=4.65, sigma=0.75) * category_multiplier), 2)
    freight = round(float(np.random.lognormal(mean=2.55, sigma=0.45)), 2)
    late = int(delivered.date() > estimated.date())
    review_score = int(np.clip(round(np.random.normal(4.45 - late * 1.15, 0.75)), 1, 5))
    orders.append(
        {
            "order_id": order_id,
            "customer_id": customer["customer_id"],
            "order_status": "delivered",
            "order_purchase_timestamp": purchase,
            "order_delivered_customer_date": delivered,
            "order_estimated_delivery_date": estimated,
        }
    )
    items.append(
        {
            "order_id": order_id,
            "product_id": product["product_id"],
            "seller_id": seller["seller_id"],
            "price": price,
            "freight_value": freight,
        }
    )
    reviews.append({"order_id": order_id, "review_score": review_score})

customers.to_csv(out / "olist_customers_dataset.csv", index=False)
sellers.to_csv(out / "olist_sellers_dataset.csv", index=False)
products.to_csv(out / "olist_products_dataset.csv", index=False)
pd.DataFrame(orders).to_csv(out / "olist_orders_dataset.csv", index=False)
pd.DataFrame(items).to_csv(out / "olist_order_items_dataset.csv", index=False)
pd.DataFrame(reviews).to_csv(out / "olist_order_reviews_dataset.csv", index=False)
print("Created synthetic Olist-style demo CSV files in data/raw/")

