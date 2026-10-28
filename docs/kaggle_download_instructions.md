# Kaggle Download Instructions

Dataset: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

## Manual Download

1. Open the Kaggle dataset page.
2. Click **Download**.
3. Extract the ZIP file.
4. Copy the CSV files into:

```text
data/raw/
```

Expected Kaggle files include:

- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_customers_dataset.csv`
- `olist_sellers_dataset.csv`
- `olist_products_dataset.csv`
- `product_category_name_translation.csv`

## Kaggle API Option

If the Kaggle API is configured:

```powershell
kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw --unzip
```

If Kaggle download is not available, run:

```powershell
python src/generate_demo_data.py
```

