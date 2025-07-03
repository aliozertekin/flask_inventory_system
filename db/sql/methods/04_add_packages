CREATE OR REPLACE PACKAGE dashboard_pkg AS
    -- Dashboard için tüm istatistikleri getiren fonksiyon
    FUNCTION get_dashboard_stats RETURN SYS_REFCURSOR;
    
    -- Aylık değişim verilerini getiren fonksiyon
    FUNCTION get_monthly_changes RETURN SYS_REFCURSOR;
END dashboard_pkg;
/

CREATE OR REPLACE PACKAGE BODY dashboard_pkg AS
    FUNCTION get_dashboard_stats RETURN SYS_REFCURSOR IS
        v_cursor SYS_REFCURSOR;
    BEGIN
        OPEN v_cursor FOR
        SELECT 
            (SELECT customer_id FROM vw_user_count) AS user_count,
            (SELECT total_products FROM vw_inventory_stats) AS product_count,
            (SELECT total_value FROM vw_inventory_stats) AS inventory_value,
            (SELECT total_orders FROM vw_order_stats) AS order_count,
            (SELECT total_cost FROM vw_order_stats) AS order_value,
            (SELECT COUNT(*) FROM inventory i WHERE i.product_inventory < 10) AS low_stock_items
            -- Min stock seviyesi için sabit değer kullanıldı
        FROM dual;
        
        RETURN v_cursor;
    END;
    
    FUNCTION get_monthly_changes RETURN SYS_REFCURSOR IS
        v_cursor SYS_REFCURSOR;
    BEGIN
        OPEN v_cursor FOR
        WITH monthly_data AS (
            SELECT 
                TRUNC(o.order_tms, 'MM') AS month,
                COUNT(DISTINCT o.order_id) AS order_count,
                SUM(oi.quantity * oi.unit_price) AS order_value,
                0 AS new_customers -- Müşteri kayıt tarihi olmadığı için 0 olarak ayarlandı
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_tms >= ADD_MONTHS(TRUNC(SYSDATE, 'MM'), -12)
              AND o.order_status NOT IN ('CANCELLED', 'REFUNDED')
            GROUP BY TRUNC(o.order_tms, 'MM')
        )
        SELECT 
            TO_CHAR(month, 'YYYY-MM') AS month,
            order_count,
            order_value,
            new_customers,
            ROUND((order_count - LAG(order_count) OVER (ORDER BY month)) / 
                  NULLIF(LAG(order_count) OVER (ORDER BY month), 0) * 100, 2) AS order_change_pct,
            ROUND((order_value - LAG(order_value) OVER (ORDER BY month)) / 
                  NULLIF(LAG(order_value) OVER (ORDER BY month), 0) * 100, 2) AS value_change_pct,
            0 AS customer_change_pct -- Müşteri kayıt tarihi olmadığı için 0
        FROM monthly_data
        ORDER BY month DESC;
        
        RETURN v_cursor;
    END;
END dashboard_pkg;
/