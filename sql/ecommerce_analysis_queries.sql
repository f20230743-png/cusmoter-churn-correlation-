-- Executive KPIs
SELECT
  COUNT(DISTINCT order_id) AS total_orders,
  SUM(payment_value) AS total_revenue,
  AVG(payment_value) AS avg_order_value,
  AVG(late_delivery_flag) AS late_delivery_rate,
  AVG(review_score) AS avg_review_score,
  AVG(repeat_customer_flag) AS repeat_customer_rate
FROM orders_enriched;

-- Revenue by product category
SELECT
  product_category_name,
  COUNT(DISTINCT order_id) AS orders,
  SUM(payment_value) AS revenue,
  AVG(review_score) AS avg_review_score,
  AVG(late_delivery_flag) AS late_delivery_rate
FROM orders_enriched
GROUP BY product_category_name
ORDER BY revenue DESC;

-- Seller performance
SELECT
  seller_tier,
  COUNT(DISTINCT seller_id) AS sellers,
  COUNT(DISTINCT order_id) AS orders,
  AVG(late_delivery_flag) AS late_delivery_rate,
  AVG(review_score) AS avg_review_score,
  SUM(payment_value) AS revenue
FROM orders_enriched
GROUP BY seller_tier
ORDER BY revenue DESC;

-- Delivery and review relationship
SELECT
  late_delivery_flag,
  COUNT(DISTINCT order_id) AS orders,
  AVG(review_score) AS avg_review_score,
  AVG(delivery_delay_days) AS avg_delivery_delay_days,
  SUM(payment_value) AS revenue
FROM orders_enriched
GROUP BY late_delivery_flag;

-- State-level customer summary
SELECT
  customer_state,
  COUNT(DISTINCT customer_id) AS customers,
  COUNT(DISTINCT order_id) AS orders,
  SUM(payment_value) AS revenue,
  AVG(repeat_customer_flag) AS repeat_customer_rate
FROM orders_enriched
GROUP BY customer_state
ORDER BY revenue DESC;

