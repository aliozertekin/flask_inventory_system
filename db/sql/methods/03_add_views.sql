CREATE OR REPLACE VIEW orders_view AS
SELECT
    o.order_id,
    o.order_tms,
    o.order_status,
    c.full_name AS customer_name,
    s.store_name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN stores s ON o.store_id = s.store_id
ORDER BY o.order_tms DESC;
/