from flask import Blueprint, render_template
from db.connection import get_connection

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
