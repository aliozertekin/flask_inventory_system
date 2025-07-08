# routes/shipments.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db.connection import conn

shipments_bp = Blueprint('shipments', __name__, url_prefix='/shipments')
PER_PAGE = 20
    

@shipments_bp.route('/')
def list_shipments():
    cursor = conn.cursor()
    search = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)

    try:
        count_query = "SELECT COUNT(*) FROM shipments WHERE 1=1"
        params = {}

        base_filter = ""

        if search:
            if search.isdigit():
                # Sayısal arama: ID alanlarına eşitlik kontrolü (tam eşleşme)
                base_filter += """ AND (
                    shipment_id = :search_num
                    OR store_id = :search_num
                    OR customer_id = :search_num
                    OR LOWER(delivery_address) LIKE :search_text
                )"""
                params['search_num'] = int(search)
                params['search_text'] = f"%{search.lower()}%"
            else:
                # Metinsel arama sadece adres üzerinde LIKE
                base_filter += " AND LOWER(delivery_address) LIKE :search_text"
                params['search_text'] = f"%{search.lower()}%"

        if status_filter:
            base_filter += " AND LOWER(shipment_status) = :status"
            params['status'] = status_filter.lower()

        count_query += base_filter
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]

        total_pages = (total + PER_PAGE - 1) // PER_PAGE

        base_query = f"""
            SELECT * FROM (
                SELECT a.*, ROWNUM rnum FROM (
                    SELECT shipment_id, store_id, customer_id, delivery_address, shipment_status
                    FROM shipments
                    WHERE 1=1 {base_filter}
                    ORDER BY shipment_id DESC
                ) a WHERE ROWNUM <= :end_row
            ) WHERE rnum > :start_row
        """

        params.update({
            'end_row': page * PER_PAGE,
            'start_row': (page - 1) * PER_PAGE
        })

        cursor.execute(base_query, params)
        shipments = cursor.fetchall()

        shipment_list = [
            {
                'id': row[0],
                'store_id': row[1],
                'customer_id': row[2],
                'address': row[3],
                'status': row[4]
            }
            for row in shipments
        ]

        return render_template(
            'shipments.html',
            shipments=shipment_list,
            query=search,
            status_filter=status_filter,
            page=page,
            per_page=PER_PAGE,
            total=total,
            total_pages=total_pages
        )

    except Exception as e:
        flash(f"Hata oluştu: {str(e)}", "error")
        return render_template(
            'shipments.html',
            shipments=[],
            query=search,
            status_filter=status_filter,
            page=page,
            per_page=PER_PAGE,
            total=0,
            total_pages=0
        )
    finally:
        cursor.close()



@shipments_bp.route('/add', methods=['GET', 'POST'])
def add_shipment():
    if request.method == 'POST':
        store_id = request.form.get('store_id')
        customer_id = request.form.get('customer_id')
        delivery_address = request.form.get('delivery_address')
        shipment_status = request.form.get('shipment_status')

        if not store_id or not customer_id or not delivery_address or not shipment_status:
            flash("Tüm alanlar zorunludur.", "error")
            return render_template('shipments_add.html')

        cursor = conn.cursor()
        try:
            cursor.callproc("ADD_SHIPMENT", [
                int(store_id),
                int(customer_id),
                delivery_address,
                shipment_status
            ])
            conn.commit()
            flash("Kargo başarıyla eklendi.", "success")
            return redirect(url_for('shipments.list_shipments'))
        except Exception as e:
            conn.rollback()
            flash(f"Ekleme hatası: {str(e)}", "error")
            return render_template('shipments_add.html')
        finally:
            cursor.close()

    return render_template('shipments_add.html')

@shipments_bp.route('/<int:shipment_id>')
def shipment_details(shipment_id):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT shipment_id, store_id, customer_id, delivery_address, shipment_status
            FROM shipments WHERE shipment_id = :id
        """, {'id': shipment_id})
        row = cursor.fetchone()
        if not row:
            flash("Kargo bulunamadı.", "error")
            return redirect(url_for('shipments.list_shipments'))

        shipment = {
            'id': row[0],
            'store_id': row[1],
            'customer_id': row[2],
            'address': row[3],
            'status': row[4]
        }
        return render_template('shipment_details.html', shipment=shipment)
    except Exception as e:
        flash(f"Hata oluştu: {str(e)}", "error")
        return redirect(url_for('shipments.list_shipments'))
    finally:
        cursor.close()

@shipments_bp.route('/<int:shipment_id>/update_status', methods=['POST'])
def update_shipment_status(shipment_id):
    new_status = request.form.get('shipment_status')

    if not new_status:
        flash("Durum bilgisi eksik.", "error")
        return redirect(url_for('shipments.shipment_details', shipment_id=shipment_id))

    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE shipments
            SET shipment_status = :new_status
            WHERE shipment_id = :shipment_id
        """, {'new_status': new_status, 'shipment_id': shipment_id})
        conn.commit()
        flash("Durum başarıyla güncellendi.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Durum güncellenemedi: {str(e)}", "error")
    finally:
        cursor.close()

    return redirect(url_for('shipments.shipment_details', shipment_id=shipment_id))

@shipments_bp.route('/logs')
def shipments_log():
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT log_id, shipment_id, operation, changed_by, changed_at, old_data, new_data
            FROM shipments_log
            ORDER BY changed_at DESC
            FETCH FIRST 100 ROWS ONLY
        """)
        columns = [col[0].lower() for col in cursor.description]
        rows = cursor.fetchall()
        logs = [dict(zip(columns, row)) for row in rows]  # dict listesi
        for log in logs:  log['table_name'] = 'SHIPMENTS'  
        return render_template('log_generic.html', logs=logs, log_type='shipments')
    finally:
        cursor.close()