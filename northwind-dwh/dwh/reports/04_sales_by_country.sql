-- Продажи по стране клиента (атрибут dim_customer, не отдельное измерение).
SELECT
    country,
    count(DISTINCT customer_key) AS customers,
    count(DISTINCT order_id)     AS orders,
    round(sum(line_total), 2)    AS revenue
FROM v_sales_flat
GROUP BY country
ORDER BY revenue DESC;
