from flask import Blueprint, render_template, request, jsonify
from db.connection import conn  # cx_Oracle bağlantısı
import cx_Oracle

order_bp = Blueprint('orders', __name__, url_prefix='/orders')


# Siparişleri listele
@order_bp.route('/')
def list_orders():
    cursor = conn.cursor()
    query = """
        SELECT o.order_id, o.order_tms, o.order_status, c.full_name, s.store_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN stores s ON o.store_id = s.store_id
        ORDER BY o.order_tms DESC
    """
    cursor.execute(query)
    orders = cursor.fetchall()

    # orders: list of tuples [(order_id, order_tms, order_status, full_name, store_name), ...]
    return render_template('orders.html', orders=orders)


@order_bp.route('/add', methods=['GET', 'POST'])
def add_order():
    if request.method == 'GET':
        # Sipariş ekleme formunu göster
        return render_template('orders_add.html')

    if request.method == 'POST':
        # JSON ile gelen sipariş verisini işle
        data = request.json
        customer_id = data.get('customer_id')
        store_id = data.get('store_id')
        items = data.get('items')

        if not customer_id or not store_id or not items:
            return jsonify({'status': 'error', 'message': 'Eksik parametre'}), 400

        cursor = conn.cursor()
        order_item_rec = conn.gettype("ORDER_ITEM_REC")
        order_item_table = conn.gettype("ORDER_ITEM_TABLE")

        order_items_obj = order_item_table.newobject()

        for item in items:
            obj = order_item_rec.newobject()
            obj.PRODUCT_ID = item['product_id']
            obj.QUANTITY = item['quantity']
            obj.UNIT_PRICE = item['unit_price']
            order_items_obj.append(obj)

        order_id_var = cursor.var(cx_Oracle.NUMBER)

        try:
            cursor.callproc('ADD_ORDER', [customer_id, store_id, order_items_obj, order_id_var])
            conn.commit()
            return jsonify({'status': 'success', 'order_id': int(order_id_var.getvalue())})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400