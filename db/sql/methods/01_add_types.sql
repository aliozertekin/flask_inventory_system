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


-- ADD TRIGGERS

-- Orders tablosu değişikliklerinde
CREATE OR REPLACE TRIGGER trg_update_dashboard_stats_orders
AFTER INSERT OR UPDATE OR DELETE ON orders
DECLARE
BEGIN
    DBMS_MVIEW.REFRESH('mv_daily_stats', 'C');
    DBMS_MVIEW.REFRESH('vw_order_stats', 'C');
END;
/

-- Order_items tablosu değişikliklerinde
CREATE OR REPLACE TRIGGER trg_update_dashboard_stats_order_items
AFTER INSERT OR UPDATE OR DELETE ON order_items
DECLARE
BEGIN
    DBMS_MVIEW.REFRESH('mv_daily_stats', 'C');
    DBMS_MVIEW.REFRESH('vw_order_stats', 'C');
END;
/

-- Inventory tablosu değişikliklerinde
CREATE OR REPLACE TRIGGER trg_update_dashboard_stats_inventory
AFTER INSERT OR UPDATE OR DELETE ON inventory
DECLARE
BEGIN
    DBMS_MVIEW.REFRESH('mv_daily_stats', 'C');
    DBMS_MVIEW.REFRESH('vw_inventory_stats', 'C');
    DBMS_MVIEW.REFRESH('inventory_view', 'C');
END;
/

-- Products tablosu değişikliklerinde
CREATE OR REPLACE TRIGGER trg_update_dashboard_stats_products
AFTER INSERT OR UPDATE OR DELETE ON products
DECLARE
BEGIN
    DBMS_MVIEW.REFRESH('mv_daily_stats', 'C');
    DBMS_MVIEW.REFRESH('vw_inventory_stats', 'C');
    DBMS_MVIEW.REFRESH('inventory_view', 'C');
END;
/

-- Customers tablosu değişikliklerinde
CREATE OR REPLACE TRIGGER trg_update_dashboard_stats_customers
AFTER INSERT OR UPDATE OR DELETE ON customers
DECLARE
BEGIN
    DBMS_MVIEW.REFRESH('mv_daily_stats', 'C');
    DBMS_MVIEW.REFRESH('vw_user_count', 'C');
    DBMS_MVIEW.REFRESH('orders_view', 'C');
END;
/

-- Stores tablosu değişikliklerinde
CREATE OR REPLACE TRIGGER trg_update_dashboard_stats_stores
AFTER INSERT OR UPDATE OR DELETE ON stores
DECLARE
BEGIN
    DBMS_MVIEW.REFRESH('mv_daily_stats', 'C');
    DBMS_MVIEW.REFRESH('orders_view', 'C');
    DBMS_MVIEW.REFRESH('inventory_view', 'C');
END;
/