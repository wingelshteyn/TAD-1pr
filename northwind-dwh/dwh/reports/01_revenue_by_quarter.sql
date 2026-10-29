-- Динамика выручки по кварталам (roll-up по dim_date).
SELECT
    year,
    quarter,
    round(sum(line_total), 2)        AS revenue,
    sum(quantity)                    AS units,
    count(DISTINCT order_id)         AS orders
FROM v_sales_flat
GROUP BY year, quarter
ORDER BY year, quarter;
