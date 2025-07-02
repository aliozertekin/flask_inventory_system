create or replace NONEDITIONABLE TYPE order_item_rec AS OBJECT (
  product_id NUMBER,
  quantity NUMBER,
  unit_price NUMBER
);
/
create or replace NONEDITIONABLE TYPE order_item_table AS TABLE OF order_item_rec;
/