create or replace NONEDITIONABLE PROCEDURE add_customer (
  p_email IN VARCHAR2,
  p_name  IN VARCHAR2
) IS
BEGIN
  INSERT INTO customers (email_address, full_name)
  VALUES (p_email, p_name);
  COMMIT;
END;
/
create or replace NONEDITIONABLE PROCEDURE add_order(
  p_customer_id IN NUMBER,
  p_store_id IN NUMBER,
  p_order_items IN order_item_table,
  p_order_id OUT NUMBER
) AS
  v_stock NUMBER;
  v_line_item_id NUMBER := 1;
BEGIN
  -- 1. Yeni sipariş ekle
  INSERT INTO orders(order_tms, customer_id, order_status, store_id)
  VALUES (SYSTIMESTAMP, p_customer_id, 'OPEN', p_store_id)
  RETURNING order_id INTO p_order_id;

  -- 2. Her ürün için stok kontrolü ve sipariş kalemi ekleme
  FOR i IN 1 .. p_order_items.COUNT LOOP
    -- Stok kontrolü
    SELECT product_inventory INTO v_stock
    FROM inventory
    WHERE store_id = p_store_id AND product_id = p_order_items(i).product_id
    FOR UPDATE; -- satırı kilitle

    IF v_stock < p_order_items(i).quantity THEN
      RAISE_APPLICATION_ERROR(-20001, 'Yeterli stok yok: Ürün ' || p_order_items(i).product_id);
    END IF;

    -- Stoktan düş
    UPDATE inventory
    SET product_inventory = product_inventory - p_order_items(i).quantity
    WHERE store_id = p_store_id AND product_id = p_order_items(i).product_id;

    -- Sipariş kalemini ekle
    INSERT INTO order_items(order_id, line_item_id, product_id, unit_price, quantity)
    VALUES (p_order_id, v_line_item_id, p_order_items(i).product_id, p_order_items(i).unit_price, p_order_items(i).quantity);

    v_line_item_id := v_line_item_id + 1;
  END LOOP;

  -- İşlem başarılıysa commit et
  COMMIT;
EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
    RAISE;
END;
/