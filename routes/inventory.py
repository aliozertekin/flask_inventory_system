from flask import Blueprint, render_template, request, jsonify
from db.connection import conn
import cx_Oracle

# Blueprint adını 'inventory_bp' olarak değiştiriyoruz
inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')
INVENTORY_VIEW = "inventory_view"

@inventory_bp.route('/')
def list_orders():
    cursor = conn.cursor()
    search_term = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    try:
        # Oracle için sayfalama sorgusu
        base_query = f"""
        SELECT * FROM (
            SELECT a.*, ROWNUM rnum FROM (
                SELECT * FROM {INVENTORY_VIEW}
                {f"WHERE LOWER(store_name) LIKE LOWER(:search) OR LOWER(product_name) LIKE LOWER(:search) OR TO_CHAR(inventory_id) LIKE :search" if search_term else ""}
                ORDER BY inventory_id
            ) a
            WHERE ROWNUM <= :end_row
        )
        WHERE rnum > :start_row
        """
        
        params = {
            'end_row': page * per_page,
            'start_row': (page - 1) * per_page
        }
        
        if search_term:
            params['search'] = f'%{search_term}%'
        
        # Toplam kayıt sayısı için sorgu
        count_query = f"SELECT COUNT(*) FROM {INVENTORY_VIEW}"
        if search_term:
            count_query += " WHERE LOWER(store_name) LIKE LOWER(:search) OR LOWER(product_name) LIKE LOWER(:search) OR TO_CHAR(inventory_id) LIKE :search"
            cursor.execute(count_query, {'search': f'%{search_term}%'})
        else:
            cursor.execute(count_query)
        
        total = cursor.fetchone()[0]
        
        # Verileri çek
        cursor.execute(base_query, params)
        inventory = cursor.fetchall()
        
        return render_template('inventory.html',
                            inventory=inventory,
                            search_term=search_term,
                            page=page,
                            per_page=per_page,
                            total=total)
    
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print("Oracle Hatası:", error.message)
        return f"Veritabanı hatası: {error.message}", 500
    except Exception as e:
        print("Genel Hata:", str(e))
        return "Bir hata oluştu", 500
    finally:
        cursor.close()

@inventory_bp.route('/get_price/<int:product_id>')
def get_price(product_id):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT unit_price FROM inventory_view WHERE product_id = :pid FETCH FIRST 1 ROWS ONLY", {'pid': product_id})
        row = cursor.fetchone()
        if row:
            return jsonify({'status': 'success', 'unit_price': float(row[0])})
        else:
            return jsonify({'status': 'error', 'message': 'Ürün bulunamadı'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()

from flask import jsonify, request

@inventory_bp.route('/get_product_info/<int:store_id>/<int:product_id>')
def get_product_info(store_id, product_id):
    cursor = conn.cursor()
    try:
        # Get total stock and min price
        cursor.execute(f"""
            SELECT 
                MIN(unit_price) AS min_price,  -- Oldest price (FIFO)
                SUM(product_inventory) AS total_stock
            FROM {INVENTORY_VIEW}
            WHERE store_id = :store_id AND product_id = :product_id
        """, {'store_id': store_id, 'product_id': product_id})
        
        row = cursor.fetchone()

        if row and row[1] is not None:  # Check if total_stock exists
            return jsonify({
                'status': 'success',
                'unit_price': float(row[0]) if row[0] else 0,
                'quantity': int(row[1])
            })
        else:
            return jsonify({'status': 'error', 'message': 'Product not found in inventory'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()