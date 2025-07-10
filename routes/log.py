from flask import Blueprint, render_template, request
from db.connection import get_connection

log_bp = Blueprint('log', __name__, url_prefix='/log')

@log_bp.route('/')
def show_logs():
    conn = get_connection()
    cursor = conn.cursor()

    # 1️ Parametreleri al
    page     = request.args.get('page', 1, type=int)
    per_page = 500
    offset   = (page - 1) * per_page

    try:
        # 2️ Toplam kayıt sayısını çek
        cursor.execute("SELECT COUNT(*) FROM audit_log")
        total = cursor.fetchone()[0]

        # 3️ Sıralamayı log_id DESC ile sabitle, OFFSET/FETCH NEXT ile sayfala
        cursor.execute("""
            SELECT
              log_id,
              table_name,
              operation,
              changed_by,
              TO_CHAR(changed_at, 'YYYY-MM-DD HH24:MI:SS') AS changed_at,
              old_data,
              new_data
            FROM audit_log
            ORDER BY log_id DESC
            OFFSET :offset ROWS
            FETCH NEXT :per_page ROWS ONLY
        """, {'offset': offset, 'per_page': per_page})

        rows = cursor.fetchall()
        logs = [{
            'log_id':     r[0],
            'table_name': r[1],
            'operation':  r[2],
            'changed_by': r[3],
            'changed_at': r[4],
            'old_data':   r[5],
            'new_data':   r[6],
        } for r in rows]

        return render_template('log.html',
                               logs=logs,
                               page=page,
                               per_page=per_page,
                               total=total)
    finally:
        cursor.close()
