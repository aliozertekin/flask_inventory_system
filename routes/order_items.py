from flask import Blueprint, render_template, request, jsonify, send_file, request
from db.connection import get_connection

order_items_bp = Blueprint('order_items', __name__, url_prefix='/order_items')

@order_items_bp.route('/logs')
def order_items_log():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT log_id, order_id, operation, changed_by, changed_at, old_data, new_data
            FROM order_items_log
            ORDER BY changed_at DESC
            FETCH FIRST 100 ROWS ONLY
        """)
        columns = [col[0].lower() for col in cursor.description]
        rows = cursor.fetchall()
        logs = [dict(zip(columns, row)) for row in rows]  # dict listesi
        for log in logs:  log['table_name'] = 'ORDER_ITEMS'  
        return render_template('log_generic.html', logs=logs, log_type='products')
    finally:
        cursor.close()