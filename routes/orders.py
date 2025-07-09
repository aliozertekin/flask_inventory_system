from flask import Blueprint, render_template, request, jsonify, send_file, request
from db.connection import get_connection
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import ttfonts
from reportlab.lib.pagesizes import A4, letter
from modules.utilities import get_font_path
from datetime import datetime
from io import BytesIO
import cx_Oracle, os

order_bp = Blueprint('orders', __name__, url_prefix='/orders')
ORDERS_VIEW = "orders_view"
PER_PAGE = 20

# Siparişleri listele
@order_bp.route('/')
def list_orders():
    conn = get_connection()
    cursor = conn.cursor()
    search_term = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)

    try:
        # Toplam sipariş sayısı
        count_query = f"SELECT COUNT(*) FROM {ORDERS_VIEW}"
        if search_term:
            count_query += """
            WHERE LOWER(customer_name) LIKE :search
               OR LOWER(store_name) LIKE :search
               OR TO_CHAR(order_id) LIKE :search
               OR LOWER(order_status) LIKE :search
            """
            cursor.execute(count_query, {'search': f'%{search_term.lower()}%'})
        else:
            cursor.execute(count_query)
        total = cursor.fetchone()[0]

        # Sipariş verilerini çek
        base_query = f"""
        SELECT * FROM (
            SELECT a.*, ROWNUM rnum FROM (
                SELECT * FROM {ORDERS_VIEW}
                {f"WHERE LOWER(customer_name) LIKE :search OR LOWER(store_name) LIKE :search OR TO_CHAR(order_id) LIKE :search OR LOWER(order_status) LIKE :search" if search_term else ""}
                ORDER BY order_tms DESC
            ) a WHERE ROWNUM <= :end_row
        ) WHERE rnum > :start_row
        """
        params = {
            'end_row': page * PER_PAGE,
            'start_row': (page - 1) * PER_PAGE
        }
        if search_term:
            params['search'] = f'%{search_term.lower()}%'

        cursor.execute(base_query, params)
        orders = cursor.fetchall()

        return render_template('orders.html',
                               orders=orders,
                               search_term=search_term,
                               page=page,
                               per_page=PER_PAGE,
                               total=total)
    except Exception as e:
        print("Hata:", str(e))
        return "Bir hata oluştu", 500
    finally:
        cursor.close()

@order_bp.route('/add', methods=['GET', 'POST'])
def add_order():
    if request.method == 'GET':
        return render_template('orders_add.html')

    if request.method == 'POST':
        data = request.json
        customer_id = data.get('customer_id')
        store_id = data.get('store_id')
        items = data.get('items')
        delivery_address = data.get('delivery_address')
        if not delivery_address:
            return jsonify({'status': 'error', 'message': 'Teslimat adresi gerekli'}), 400
        if not customer_id or not store_id or not items:
            return jsonify({'status': 'error', 'message': 'Eksik parametre'}), 400

        conn = get_connection()
        cursor = conn.cursor()

        # Her ürün için stok kontrolü
        for item in items:
            product_id = item['product_id']
            quantity = item['quantity']

            # Envanterde ürün var mı ve yeterli miktar var mı sorgusu
            stock_query = """
                SELECT SUM(product_inventory)
                FROM inventory
                WHERE product_id = :product_id AND store_id = :store_id
            """
            cursor.execute(stock_query, {'product_id': product_id, 'store_id': store_id})
            stock = cursor.fetchone()

            if stock[0] is None or stock[0] < quantity:
                return jsonify({'status': 'error', 'message': f"Ürün ID {product_id} için yeterli stok yok. Mevcut: {stock[0] or 0}"}), 400

        # Eğer stok kontrolü geçtiyse siparişi eklemeye devam et
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
            cursor.callproc('ADD_ORDER', [customer_id, store_id, order_items_obj, delivery_address, order_id_var])
            conn.commit()
            return jsonify({'status': 'success', 'order_id': int(order_id_var.getvalue())})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400


@order_bp.route('/<int:order_id>', methods=['GET'])
def get_order_details(order_id):
    conn = get_connection()
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
        conn = get_connection()
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
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE orders SET order_status = :new_status WHERE order_id = :order_id
            """, {'new_status': new_status, 'order_id': order_id})
            conn.commit()
            return jsonify({'status': 'success'})
        except Exception as e:
            conn.rollback()
            return jsonify({'status': 'error', 'message': str(e)})

font_path = get_font_path()
pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))

@order_bp.route('/<int:order_id>/invoice')
def generate_invoice(order_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # DejaVuSans.ttf fontunu kaydet ve kullanıma hazırla
        font_path = "static/fonts/DejaVuSans.ttf"  # font dosyanın gerçek yolu
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))

        # Veri sorgusu
        cursor.execute("""
            SELECT 
                o.order_id,
                o.order_tms,
                o.order_status,
                
                c.customer_id,
                c.full_name,
                c.email_address,
                
                s.store_id,
                s.store_name,
                s.physical_address,
                
                sh.delivery_address,
                sh.shipment_status,
                
                oi.line_item_id,
                p.product_name,
                oi.quantity,
                oi.unit_price,
                (oi.quantity * oi.unit_price) AS line_total

            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN stores s ON o.store_id = s.store_id
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            LEFT JOIN shipments sh ON sh.shipment_id = oi.shipment_id

            WHERE o.order_id = :order_id
            ORDER BY oi.line_item_id
        """, {'order_id': order_id})

        rows = cursor.fetchall()
        if not rows:
            return "Sipariş bulunamadı", 404

        # PDF başlat
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setTitle(f"Fatura - Sipariş {order_id}")

        y = 750
        pdf.setFont("DejaVuSans", 16)
        pdf.drawString(50, y, f"Fatura - Sipariş #{order_id}")
        y -= 30

        # Genel bilgiler
        row = rows[0]
        order_date = row[1].strftime('%Y-%m-%d %H:%M:%S')
        pdf.setFont("DejaVuSans", 12)
        pdf.drawString(50, y, f"Tarih: {order_date}")
        y -= 20
        pdf.drawString(50, y, f"Durum: {row[2]}")
        y -= 30

        # Müşteri Bilgileri
        pdf.setFont("DejaVuSans", 12)
        pdf.drawString(50, y, "Müşteri Bilgileri:")
        y -= 20
        pdf.drawString(60, y, f"Ad Soyad: {row[4]}")
        y -= 20
        pdf.drawString(60, y, f"E-posta: {row[5]}")
        y -= 30

        # Mağaza Bilgileri
        pdf.drawString(50, y, "Mağaza Bilgileri:")
        y -= 20
        pdf.drawString(60, y, f"Mağaza: {row[7]}")
        y -= 20
        pdf.drawString(60, y, f"Adres: {row[8]}")
        y -= 30

        # Teslimat Bilgileri
        pdf.drawString(50, y, "Teslimat Bilgileri:")
        y -= 20
        pdf.drawString(60, y, f"Adres: {row[9] or 'Bilinmiyor'}")
        y -= 20
        pdf.drawString(60, y, f"Durum: {row[10] or 'Belirsiz'}")
        y -= 30

        # Ürünler
        pdf.drawString(50, y, "Ürünler:")
        y -= 20

        total = 0
        for r in rows:
            pname = r[12]
            quantity = r[13]
            unit_price = float(r[14])
            line_total = float(r[15])
            total += line_total

            pdf.drawString(60, y, f"{pname} - Adet: {quantity}, Birim Fiyat: {unit_price:.2f} $, Toplam: {line_total:.2f} $")
            y -= 20

            if y < 100:
                pdf.showPage()
                pdf.setFont("DejaVuSans", 12)
                y = 750

        # Genel Toplam
        y -= 10
        pdf.setFont("DejaVuSans", 12)
        pdf.drawString(50, y, f"Genel Toplam: {total:.2f} $")

        pdf.showPage()
        pdf.save()
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"fatura_{order_id}.pdf",
            mimetype='application/pdf'
        )

    finally:
        cursor.close()

@order_bp.route('/logs')
def orders_log():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT log_id, order_id, operation, changed_by, changed_at, old_data, new_data
            FROM order_log
            ORDER BY changed_at DESC
            FETCH FIRST 100 ROWS ONLY
        """)
        columns = [col[0].lower() for col in cursor.description]
        rows = cursor.fetchall()
        logs = [dict(zip(columns, row)) for row in rows]  # dict listesi
        for log in logs:  log['table_name'] = 'ORDERS'  
        return render_template('log_generic.html', logs=logs, log_type='orders')
    finally:
        cursor.close()

