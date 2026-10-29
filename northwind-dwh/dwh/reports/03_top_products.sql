-- Топ-10 товаров по выручке.
SELECT
    product_name,
    category_name,
    round(sum(line_total), 2) AS revenue,
    sum(quantity)             AS units
FROM v_sales_flat
GROUP BY product_name, category_name
ORDER BY revenue DESC, product_name
LIMIT 10;
