create or replace NONEDITIONABLE TYPE order_item_rec AS OBJECT (
  product_id NUMBER,
  quantity NUMBER,
  unit_price NUMBER
);
/
create or replace NONEDITIONABLE TYPE order_item_table AS TABLE OF order_item_rec;
/
create or replace NONEDITIONABLE TYPE t_stock_row AS OBJECT (
    inventory_id NUMBER(38,0),
    product_inventory NUMBER(38,0)
);
/



-- ADD INDEXES

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_orders_order_tms ON orders(order_tms);


-- DROP TRIGGER komutları
DROP TRIGGER trg_update_dashboard_stats_orders;
DROP TRIGGER trg_update_dashboard_stats_order_items;
DROP TRIGGER trg_update_dashboard_stats_inventory;
DROP TRIGGER trg_update_dashboard_stats_products;
DROP TRIGGER trg_update_dashboard_stats_customers;
DROP TRIGGER trg_update_dashboard_stats_stores;


-- CREATE TRIGGER komutları

CREATE OR REPLACE TRIGGER trg_update_dashboard_stats_orders
AFTER INSERT OR UPDATE OR DELETE ON orders
BEGIN
    DBMS_MVIEW.REFRESH('mv_daily_stats', 'C');
END;
/

CREATE OR REPLACE TRIGGER trg_update_dashboard_stats_order_items
AFTER INSERT OR UPDATE OR DELETE ON order_items
BEGIN
    DBMS_MVIEW.REFRESH('mv_daily_stats', 'C');
END;
/

CREATE OR REPLACE TRIGGER trg_update_dashboard_stats_inventory
AFTER INSERT OR UPDATE OR DELETE ON inventory
BEGIN
    DBMS_MVIEW.REFRESH('mv_daily_stats', 'C');
END;
/

CREATE OR REPLACE TRIGGER trg_update_dashboard_stats_products
AFTER INSERT OR UPDATE OR DELETE ON products
BEGIN
    DBMS_MVIEW.REFRESH('mv_daily_stats', 'C');
END;
/

CREATE OR REPLACE TRIGGER trg_update_dashboard_stats_customers
AFTER INSERT OR UPDATE OR DELETE ON customers
BEGIN
    DBMS_MVIEW.REFRESH('mv_daily_stats', 'C');
END;
/

CREATE OR REPLACE TRIGGER trg_update_dashboard_stats_stores
AFTER INSERT OR UPDATE OR DELETE ON stores
BEGIN
    DBMS_MVIEW.REFRESH('mv_daily_stats', 'C');
END;
/