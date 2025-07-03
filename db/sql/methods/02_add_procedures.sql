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

CREATE OR REPLACE PROCEDURE add_order (
  p_customer_id IN NUMBER,
  p_store_id IN NUMBER,
  p_order_items IN order_item_table,
  p_order_id OUT NUMBER
) AS
  v_line_item_id NUMBER := 1;
BEGIN
  -- Yeni sipariş ekle
  INSERT INTO orders(order_tms, customer_id, order_status, store_id)
  VALUES (SYSTIMESTAMP, p_customer_id, 'OPEN', p_store_id)
  RETURNING order_id INTO p_order_id;

  -- Her sipariş kalemi için
  FOR i IN 1 .. p_order_items.COUNT LOOP
    DECLARE
      v_quantity_needed NUMBER := p_order_items(i).quantity;
      v_total_stock NUMBER := 0;

      -- Önce toplam stoğu hesapla
      CURSOR c_sum_stock IS
        SELECT NVL(SUM(product_inventory), 0) total
        FROM inventory
        WHERE store_id = p_store_id AND product_id = p_order_items(i).product_id;

      -- FIFO için stok satırlarını sırayla al
      CURSOR c_stock IS
        SELECT inventory_id, product_inventory
        FROM inventory
        WHERE store_id = p_store_id AND product_id = p_order_items(i).product_id
        ORDER BY inventory_id
        FOR UPDATE;
    BEGIN
      -- Toplam stok kontrolü
      OPEN c_sum_stock;
      FETCH c_sum_stock INTO v_total_stock;
      CLOSE c_sum_stock;

      IF v_total_stock < v_quantity_needed THEN
        RAISE_APPLICATION_ERROR(-20001, 'Yeterli stok yok: Ürün ' || p_order_items(i).product_id || ', Mevcut toplam stok: ' || v_total_stock);
      END IF;

      -- FIFO mantığı ile stok azaltma
      OPEN c_stock;
      LOOP
        FETCH c_stock INTO v_stock_row;
        EXIT WHEN c_stock%NOTFOUND OR v_quantity_needed <= 0;

        IF v_stock_row.product_inventory <= v_quantity_needed THEN
          -- Satırdaki stok tamamen tükeniyor, satırı sil
          DELETE FROM inventory WHERE inventory_id = v_stock_row.inventory_id;
          v_quantity_needed := v_quantity_needed - v_stock_row.product_inventory;
        ELSE
          -- Satırdan sadece ihtiyaç kadar stok düş
          UPDATE inventory
          SET product_inventory = product_inventory - v_quantity_needed
          WHERE inventory_id = v_stock_row.inventory_id;
          v_quantity_needed := 0;
        END IF;
      END LOOP;
      CLOSE c_stock;

      -- Sipariş kalemini ekle
      INSERT INTO order_items(order_id, line_item_id, product_id, unit_price, quantity)
      VALUES (p_order_id, v_line_item_id, p_order_items(i).product_id,
              p_order_items(i).unit_price, p_order_items(i).quantity);

      v_line_item_id := v_line_item_id + 1;
    END;
  END LOOP;

  COMMIT;
EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
    RAISE;
END;
/

create or replace NONEDITIONABLE PROCEDURE print_order_total(p_order_id IN NUMBER) IS
  v_total NUMBER := 0;
BEGIN
  SELECT SUM(unit_price * quantity)
  INTO v_total
  FROM order_items
  WHERE order_id = p_order_id;

  DBMS_OUTPUT.PUT_LINE('Total: ' || NVL(v_total, 0));
END;
