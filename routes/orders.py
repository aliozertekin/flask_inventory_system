from flask import Blueprint, render_template, request, jsonify
from db.connection import conn  # cx_Oracle bağlantısı
import cx_Oracle

order_bp = Blueprint('orders', __name__, url_prefix='/orders')
ORDERS_VIEW = "orders_view"

# Siparişleri listele
@order_bp.route('/')
def list_orders():
    cursor = conn.cursor()
    query = f"SELECT * FROM {ORDERS_VIEW} ORDER BY order_tms DESC"
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


@order_bp.route('/<int:order_id>', methods=['GET'])
def get_order_details(order_id):
    cursor = conn.cursor()

    # Sipariş bilgilerini, sipariş kalemlerini ve paket durumunu çek
    sql = """
        SELECT o.order_id, o.order_tms, o.order_status, o.customer_id, o.store_id,
               oi.line_item_id, oi.product_id, oi.quantity, oi.unit_price,
               s.shipment_status, s.shipment_id
        FROM orders o
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        LEFT JOIN shipments s ON oi.shipment_id = s.shipment_id
        WHERE o.order_id = :order_id
    """
    cursor.execute(sql, order_id=order_id)
    rows = cursor.fetchall()

    if not rows:
        return jsonify({'status': 'error', 'message': 'Sipariş bulunamadı'}), 404

    # Verileri anlamlı şekilde grupla
    order_info = {
        'order_id': rows[0][0],
        'order_tms': rows[0][1].strftime("%Y-%m-%d %H:%M:%S"),
        'order_status': rows[0][2],
        'customer_id': rows[0][3],
        'store_id': rows[0][4],
        'items': [],
    }

    shipments = {}
    for r in rows:
        item = {
            'line_item_id': r[5],
            'product_id': r[6],
            'quantity': r[7],
            'unit_price': float(r[8]) if r[8] is not None else None,
        }
        order_info['items'].append(item)
        if r[9]:
            shipments[r[9]] = r[10]  # shipment_id: shipment_status

    order_info['shipments'] = shipments

    return jsonify({'status': 'success', 'order': order_info})


@order_bp.route('/<int:order_id>/update_status', methods=['GET', 'POST'])
def update_order_status(order_id):
    if request.method == 'GET':
        cursor = conn.cursor()
        cursor.execute("""
            SELECT order_id, order_tms, order_status, customer_id, store_id
            FROM orders
            WHERE order_id = :order_id
        """, {'order_id': order_id})
        row = cursor.fetchone()

        if not row:
            return "Sipariş bulunamadı", 404

        # İsteğe bağlı olarak ürün kalemlerini de çekebilirsin
        cursor.execute("""
            SELECT product_id, quantity, unit_price
            FROM order_items
            WHERE order_id = :order_id
        """, {'order_id': order_id})
        items = cursor.fetchall()

        order = {
            'order_id': row[0],
            'order_tms': row[1],
            'order_status': row[2],
            'customer_id': row[3],
            'store_id': row[4],
            'items': [{'product_id': i[0], 'quantity': i[1], 'unit_price': i[2]} for i in items]
        }

        return render_template('orders_details.html', order=order)
    
    if request.method == 'POST':
        data = request.get_json()
        new_status = data.get('order_status')

        allowed_statuses = ['OPEN', 'PAID', 'SHIPPED', 'COMPLETE', 'CANCELLED', 'REFUNDED']
        if new_status not in allowed_statuses:
            return jsonify({'status': 'error', 'message': 'Geçersiz durum'}), 400

        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE orders SET order_status = :new_status WHERE order_id = :order_id
            """, {'new_status': new_status, 'order_id': order_id})
            conn.commit()
            return jsonify({'status': 'success'})
        except Exception as e:
            conn.rollback()
            return jsonify({'status': 'error', 'message': str(e)})
