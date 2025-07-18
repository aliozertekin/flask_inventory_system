from flask import Blueprint, render_template, send_file, abort
from barcode.writer import ImageWriter
from db.connection import get_connection
import io
import cx_Oracle
import barcode

lot_bp = Blueprint('lots', __name__, url_prefix='/lots')

@lot_bp.route('/logs')
def lots_log():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT log_id, lot_id, action AS operation, user_name AS changed_by, action_date AS changed_at,
                   NULL AS old_data, description AS new_data
            FROM lot_logs
            ORDER BY log_id DESC
            FETCH FIRST 100 ROWS ONLY
        """)
        columns = [col[0].lower() for col in cursor.description]
        rows = cursor.fetchall()
        logs = [dict(zip(columns, row)) for row in rows]
        for log in logs:
            log['table_name'] = 'LOTS'
        return render_template('log_generic.html', logs=logs, log_type='lots')
    finally:
        cursor.close()

@lot_bp.route('/')
def list_lots():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.lot_id, l.inventory_id, l.product_id, l.amount, TO_CHAR(l.exp_date, 'YYYY-MM-DD'), l.barcode
        FROM lots l
        ORDER BY lot_id DESC
    """)
    lots = cursor.fetchall()
    return render_template('lots.html', lots=lots)

@lot_bp.route('/barcode/<int:lot_id>')
def generate_barcode(lot_id):
    # Barkod içeriği: sabit prefix + lot_id (örnek: LOT000123)
    code_str = f"LOT{str(lot_id).zfill(6)}"
    try:
        barcode_obj = barcode.get('code128', code_str, writer=ImageWriter())
        buffer = io.BytesIO()
        barcode_obj.write(buffer)
        buffer.seek(0)
        return send_file(buffer, mimetype='image/png')
    except Exception as e:
        abort(404, description=f"Barkod oluşturulamadı: {e}")
