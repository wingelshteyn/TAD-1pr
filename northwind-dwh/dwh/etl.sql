-- ============================================================================
--  ETL: northwind (OLTP) -> northwind_dwh (звезда)
--  Extract: postgres_fdw, только чтение источника.
--  Transform + Load: SQL. Запускать в базе northwind_dwh после schema.sql.
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS postgres_fdw;

DROP SERVER IF EXISTS oltp_srv CASCADE;
DROP SCHEMA IF EXISTS oltp CASCADE;

CREATE SERVER oltp_srv
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host '127.0.0.1', dbname 'northwind', port '5432');

CREATE USER MAPPING FOR CURRENT_USER
    SERVER oltp_srv
    OPTIONS (user 'dwh', password 'dwh');

CREATE SCHEMA oltp;
IMPORT FOREIGN SCHEMA public
    LIMIT TO (
        categories, customers, employees, orders, order_details,
        products, shippers, suppliers
    )
    FROM SERVER oltp_srv
    INTO oltp;

TRUNCATE fact_order_line, dim_customer, dim_product, dim_employee, dim_shipper, dim_date
    RESTART IDENTITY CASCADE;

-- Календарь на диапазон дат заказов
INSERT INTO dim_date (date_key, full_date, day, month, month_name, quarter, year)
SELECT
    to_char(d, 'YYYYMMDD')::integer,
    d::date,
    EXTRACT(DAY FROM d)::smallint,
    EXTRACT(MONTH FROM d)::smallint,
    (ARRAY[
        'Январь','Февраль','Март','Апрель','Май','Июнь',
        'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'
    ])[EXTRACT(MONTH FROM d)::integer],
    EXTRACT(QUARTER FROM d)::smallint,
    EXTRACT(YEAR FROM d)::smallint
FROM generate_series(
    (SELECT min(order_date) FROM oltp.orders),
    (SELECT max(order_date) FROM oltp.orders),
    interval '1 day'
) AS d;

INSERT INTO dim_customer (customer_id, company_name, contact_name, city, region, country)
SELECT
    customer_id,
    company_name,
    contact_name,
    coalesce(city, 'Не указан'),
    coalesce(region, 'Не указан'),
    coalesce(country, 'Не указана')
FROM oltp.customers;

INSERT INTO dim_product (
    product_id, product_name, category_name, supplier_name,
    supplier_country, quantity_per_unit, discontinued
)
SELECT
    p.product_id,
    p.product_name,
    coalesce(c.category_name, 'Без категории'),
    coalesce(s.company_name, 'Не указан'),
    coalesce(s.country, 'Не указана'),
    p.quantity_per_unit,
    p.discontinued <> 0
FROM oltp.products p
LEFT JOIN oltp.categories c ON c.category_id = p.category_id
LEFT JOIN oltp.suppliers  s ON s.supplier_id = p.supplier_id;

INSERT INTO dim_employee (employee_id, full_name, title, city, country, manager_name)
SELECT
    e.employee_id,
    e.first_name || ' ' || e.last_name,
    e.title,
    coalesce(e.city, 'Не указан'),
    coalesce(e.country, 'Не указана'),
    m.first_name || ' ' || m.last_name
FROM oltp.employees e
LEFT JOIN oltp.employees m ON m.employee_id = e.reports_to;

INSERT INTO dim_shipper (shipper_id, company_name)
SELECT shipper_id, company_name
FROM oltp.shippers;

-- Позиция заказа. Строки без даты, клиента, сотрудника или перевозчика не грузим:
-- для звезды каждый факт должен иметь все координаты.
INSERT INTO fact_order_line (
    order_id, date_key, customer_key, product_key, employee_key, shipper_key,
    quantity, unit_price, discount, line_total, discount_amount, order_freight
)
SELECT
    o.order_id,
    to_char(o.order_date, 'YYYYMMDD')::integer,
    cu.customer_key,
    pr.product_key,
    em.employee_key,
    sh.shipper_key,
    od.quantity,
    round(od.unit_price::numeric, 2),
    round(od.discount::numeric, 4),
    round((od.quantity * od.unit_price * (1 - od.discount))::numeric, 2),
    round((od.quantity * od.unit_price * od.discount)::numeric, 2),
    round(coalesce(o.freight, 0)::numeric, 2)
FROM oltp.order_details od
JOIN oltp.orders o       ON o.order_id = od.order_id
JOIN dim_date d          ON d.full_date = o.order_date
JOIN dim_customer cu     ON cu.customer_id = o.customer_id
JOIN dim_product pr      ON pr.product_id = od.product_id
JOIN dim_employee em     ON em.employee_id = o.employee_id
JOIN dim_shipper sh      ON sh.shipper_id = o.ship_via
WHERE o.order_date IS NOT NULL;
