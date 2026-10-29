-- Выручка и доля по категориям товаров (срез по category_name).
SELECT
    category_name,
    round(sum(line_total), 2) AS revenue,
    sum(quantity)             AS units,
    round(
        100.0 * sum(line_total) / sum(sum(line_total)) OVER (),
        2
    ) AS share_pct
FROM v_sales_flat
GROUP BY category_name
ORDER BY revenue DESC;
