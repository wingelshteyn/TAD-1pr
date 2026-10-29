-- Аналитический слой: одна плоская витрина поверх звезды.
-- Соединений мало: факт и пять измерений, без цепочки страна → регион → город.

DROP VIEW IF EXISTS v_sales_flat CASCADE;

CREATE OR REPLACE VIEW v_sales_flat AS
SELECT
    f.order_line_key,
    f.order_id,
    f.quantity,
    f.unit_price,
    f.discount,
    f.line_total,
    f.discount_amount,
    f.order_freight,
    d.full_date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    c.customer_key,
    c.company_name     AS customer,
    c.city,
    c.region,
    c.country,
    p.product_key,
    p.product_name,
    p.category_name,
    p.supplier_name,
    p.supplier_country,
    p.discontinued,
    e.employee_key,
    e.full_name        AS employee,
    e.title            AS employee_title,
    e.manager_name,
    s.company_name     AS shipper
FROM fact_order_line f
JOIN dim_date     d ON d.date_key     = f.date_key
JOIN dim_customer c ON c.customer_key = f.customer_key
JOIN dim_product  p ON p.product_key  = f.product_key
JOIN dim_employee e ON e.employee_key = f.employee_key
JOIN dim_shipper  s ON s.shipper_key  = f.shipper_key;
