-- Где скидка съедает цену: доля скидки от суммы до скидки, по категориям.
SELECT
    category_name,
    round(sum(line_total), 2)      AS revenue,
    round(sum(discount_amount), 2) AS discount_amount,
    round(
        100.0 * sum(discount_amount)
        / nullif(sum(line_total) + sum(discount_amount), 0),
        2
    ) AS discount_pct
FROM v_sales_flat
GROUP BY category_name
ORDER BY discount_pct DESC, category_name;
