-- Продажи сотрудников и их руководитель (атрибут измерения, не отдельная таблица).
SELECT
    employee,
    employee_title,
    coalesce(manager_name, '—')   AS manager,
    count(DISTINCT customer_key)  AS customers,
    count(DISTINCT order_id)      AS orders,
    round(sum(line_total), 2)     AS revenue
FROM v_sales_flat
GROUP BY employee, employee_title, manager_name
ORDER BY revenue DESC;
