
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

