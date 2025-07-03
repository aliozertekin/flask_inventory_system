from flask import Blueprint, render_template, jsonify
from db.connection import conn
import cx_Oracle

index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def index():
    return render_template('index.html')


@index_bp.route('/api/dashboard')
def api_dashboard():
    cursor = conn.cursor()
    
    try:
        stats_cursor = cursor.callfunc('dashboard_pkg.get_dashboard_stats', cx_Oracle.CURSOR)
        stats = stats_cursor.fetchone()

        changes_cursor = cursor.callfunc('dashboard_pkg.get_monthly_changes', cx_Oracle.CURSOR)
        changes = changes_cursor.fetchall()

        return jsonify({
            'user_count': stats[0],
            'product_count': stats[1],
            'inventory_value': float(stats[2]),
            'order_count': stats[3],
            'order_value': float(stats[4]),
            'low_stock_items': stats[5],
            'monthly_changes': [
                {
                    'month': row[0],  # zaten string, strftime'e gerek yok
                    'order_change_pct': float(row[4] or 0),
                    'value_change_pct': float(row[5] or 0),
                    'user_change_pct': float(row[6] or 0)
                } for row in changes
            ]
        })
    finally:
        cursor.close()