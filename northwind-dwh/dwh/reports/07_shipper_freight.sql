-- Перевозчики. Фрахт сначала схлопывается до заказа, иначе он посчитается столько раз,
-- сколько позиций в заказе.
WITH orders AS (
    SELECT
        order_id,
        shipper,
        max(order_freight) AS freight,
        sum(line_total)    AS revenue
    FROM v_sales_flat
    GROUP BY order_id, shipper
)
SELECT
    shipper,
    count(*)                  AS orders,
    round(sum(revenue), 2)    AS revenue,
    round(sum(freight), 2)    AS freight,
    round(avg(freight), 2)    AS avg_freight
FROM orders
GROUP BY shipper
ORDER BY revenue DESC;
