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