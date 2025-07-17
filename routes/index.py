from flask import Blueprint, render_template, jsonify
from db.connection import get_connection
import cx_Oracle

index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def index():
    return render_template('index.html')


@index_bp.route('/api/dashboard')
def api_dashboard():
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get dashboard stats
        stats_cursor = cursor.callfunc('dashboard_pkg.get_dashboard_stats', cx_Oracle.CURSOR)
        stats = stats_cursor.fetchone()
        
        # Get monthly changes
        changes_cursor = cursor.callfunc('dashboard_pkg.get_monthly_changes', cx_Oracle.CURSOR)
        changes = changes_cursor.fetchall()

        return jsonify({
            # Top section stats
            'store_count': stats[0],
            'product_count': stats[1],
            'customer_count': stats[2],
            'order_count': stats[3],
            'shipment_count': stats[4],
            'inventory_value': float(stats[5] or 0),
            'total_sales': float(stats[6] or 0),
            'low_stock_items': stats[7],
            
            # Bottom section stats
            'avg_order_value': float(stats[8] or 0),
            'avg_customer_spending': float(stats[9] or 0),
            'max_order_value': float(stats[10] or 0),
            'total_stock': float(stats[11] or 0),
            'active_customers': stats[12],
            'delivered_shipments': stats[13],
            'in_transit_shipments': stats[14],
            'preparing_shipments': stats[15],
            
            # Monthly changes
            'monthly_changes': [
                {
                    'month': row[0],
                    'order_change_pct': float(row[4] or 0),
                    'value_change_pct': float(row[5] or 0),
                    'user_change_pct': float(row[6] or 0)
                } for row in changes
            ]
        })
    finally:
        cursor.close()