-- Поставщики: выручка товаров, которые они поставляют (атрибуты dim_product).
SELECT
    supplier_name,
    supplier_country,
    count(DISTINCT product_key) AS products,
    round(sum(line_total), 2)   AS revenue
FROM v_sales_flat
GROUP BY supplier_name, supplier_country
ORDER BY revenue DESC
LIMIT 10;
