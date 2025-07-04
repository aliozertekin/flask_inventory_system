from flask import Blueprint, render_template
from db.connection import conn

log_bp = Blueprint('log', __name__, url_prefix='/log')

@log_bp.route('/')
def show_logs():
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT log_id, table_name, operation, changed_by, changed_at, old_data, new_data
            FROM audit_log
            ORDER BY changed_at DESC
            FETCH FIRST 100 ROWS ONLY
        """)
        logs = cursor.fetchall()
        logs_list = []
        for l in logs:
            logs_list.append({
                'log_id': l[0],
                'table_name': l[1],
                'operation': l[2],
                'changed_by': l[3],
                'changed_at': l[4],
                'old_data': l[5],
                'new_data': l[6]
            })
        return render_template('log.html', logs=logs_list)
    finally:
        cursor.close()
