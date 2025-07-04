
  CREATE OR REPLACE FORCE NONEDITIONABLE VIEW "SYSTEM"."ORDERS_VIEW" ("ORDER_ID", "ORDER_TMS", "ORDER_STATUS", "CUSTOMER_NAME", "STORE_NAME") AS 
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


  CREATE OR REPLACE FORCE NONEDITIONABLE VIEW "SYSTEM"."INVENTORY_VIEW" ("INVENTORY_ID", "STORE_ID", "STORE_NAME", "PRODUCT_ID", "PRODUCT_NAME", "UNIT_PRICE", "PRODUCT_INVENTORY") AS 
  SELECT
  i.inventory_id,
  s.store_id,
  s.store_name,
  p.product_id,
  p.product_name,
  p.unit_price,
  i.product_inventory
FROM inventory i
JOIN products p ON i.product_id = p.product_id
JOIN stores s ON i.store_id = s.store_id
ORDER BY i.inventory_id ASC;
/

-- Kullanıcı sayısı için view
CREATE OR REPLACE VIEW vw_user_count AS
SELECT COUNT(*) AS customer_id FROM customers;

/

-- Depodaki ürün miktarı ve toplam değer için view
CREATE OR REPLACE VIEW vw_inventory_stats AS
SELECT 
    SUM(i.product_inventory) AS total_products,
    SUM(i.product_inventory * p.unit_price) AS total_value
FROM 
    inventory i
JOIN 
    products p ON i.product_id = p.product_id;

/

CREATE OR REPLACE VIEW vw_order_stats AS
SELECT 
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity * oi.unit_price) AS total_cost
FROM 
    order_items oi
JOIN 
    orders o ON oi.order_id = o.order_id 
WHERE 
    o.order_status NOT IN ('CANCELLED', 'REFUNDED');
    
/

CREATE MATERIALIZED VIEW mv_daily_stats
REFRESH COMPLETE ON DEMAND
AS
SELECT 
  TRUNC(SYSDATE) AS report_date,
  c.user_count,
  i.total_products,
  i.total_value,
  o.today_orders,
  o.today_sales
FROM 
  (SELECT COUNT(*) AS user_count FROM customers) c,
  (SELECT 
     SUM(product_inventory) AS total_products,
     SUM(product_inventory * unit_price) AS total_value
   FROM inventory i JOIN products p ON i.product_id = p.product_id) i,
  (SELECT 
     COUNT(*) AS today_orders,
     NVL(SUM(oi.quantity * oi.unit_price), 0) AS today_sales
   FROM order_items oi JOIN orders o ON oi.order_id = o.order_id
   WHERE TRUNC(o.order_tms) = TRUNC(SYSDATE)) o;
