-- Топ-10 клиентов по выручке и их средний заказ.
SELECT
    customer,
    country,
    count(DISTINCT order_id) AS orders,
    round(sum(line_total), 2) AS revenue,
    round(sum(line_total) / count(DISTINCT order_id), 2) AS avg_order
FROM v_sales_flat
GROUP BY customer, country
ORDER BY revenue DESC, customer
LIMIT 10;
