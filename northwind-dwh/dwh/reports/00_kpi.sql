-- KPI оптовой торговли: выручка, скидки, заказы, средний заказ.
SELECT
    round(sum(line_total), 2)                          AS revenue,
    round(sum(discount_amount), 2)                     AS discounts,
    sum(quantity)                                      AS units,
    count(DISTINCT order_id)                           AS orders,
    count(DISTINCT customer_key)                       AS customers,
    round(sum(line_total) / count(DISTINCT order_id), 2) AS avg_order,
    min(full_date)                                     AS first_order,
    max(full_date)                                     AS last_order
FROM v_sales_flat;
