from flask import Blueprint, render_template, request, redirect, url_for, flash
from db.connection import get_connection
import cx_Oracle

store_bp = Blueprint('store', __name__, url_prefix='/store')


@store_bp.route('/')
def list_stores():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT store_id, store_name, web_address, physical_address
            FROM stores
            ORDER BY store_id
        """)
        stores = cursor.fetchall()
        store_list = [{
            'id': s[0],
            'name': s[1],
            'web_address': s[2],          # Burada alan ismi değiştirildi
            'physical_address': s[3]      # Burada alan ismi değiştirildi
        } for s in stores]

        return render_template('store.html', stores=store_list)
    except Exception as e:
        flash(f"Hata oluştu: {str(e)}", "error")
        return render_template('store.html', stores=[])
    finally:
        cursor.close()

@store_bp.route('/add', methods=['GET', 'POST'])
def add_store():
    if request.method == 'POST':
        name = request.form.get('name')
        web = request.form.get('web_address')
        address = request.form.get('physical_address')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        if not name or not address:
            flash("Mağaza adı ve adres zorunludur.", "error")
            return render_template('store_add.html')

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.setinputsizes(
                cx_Oracle.STRING,
                cx_Oracle.STRING,
                cx_Oracle.STRING,
                cx_Oracle.NUMBER,
                cx_Oracle.NUMBER,
                cx_Oracle.BLOB,
                cx_Oracle.STRING,
                cx_Oracle.STRING,
                cx_Oracle.STRING
            )

            params = [
                name,
                web,
                address,
                to_float_or_none(latitude),
                to_float_or_none(longitude),
                None,  # BLOB için None kabul edilebilir
                None,
                None,
                None
            ]

            cursor.callproc("ADD_STORE", params)

            conn.commit()
            flash("Mağaza başarıyla eklendi.", "success")
            return redirect(url_for('store.list_stores'))
        except Exception as e:
            conn.rollback()
            flash(f"Hata oluştu: {str(e)}", "error")
            return render_template('store_add.html')
        finally:
            cursor.close()

    return render_template('store_add.html')

def to_float_or_none(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


@store_bp.route('/delete/<int:store_id>', methods=['POST'])
def delete_store(store_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc("DELETE_STORE", [store_id])
        conn.commit()
        flash("Mağaza silindi.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Silme hatası: {str(e)}", "error")
    finally:
        cursor.close()
    return redirect(url_for('store.list_stores'))

def to_float_or_none(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None
    
@store_bp.route('/logs')
def stores_log():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT log_id, store_id, operation, changed_by, changed_at, old_data, new_data
            FROM store_log
            ORDER BY changed_at DESC
            FETCH FIRST 100 ROWS ONLY
        """)
        columns = [col[0].lower() for col in cursor.description]
        rows = cursor.fetchall()
        logs = [dict(zip(columns, row)) for row in rows]  # dict listesi
        for log in logs:  log['table_name'] = 'STORES'  
        return render_template('log_generic.html', logs=logs, log_type='stores')
    finally:
        cursor.close()

@store_bp.route('/details/<int:store_id>', methods=['GET', 'POST'])
def store_details(store_id):
    conn = get_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        # Formdan gelen verileri al
        name = request.form.get('name')
        web = request.form.get('web_address')
        address = request.form.get('physical_address')
        latitude = to_float_or_none(request.form.get('latitude'))
        longitude = to_float_or_none(request.form.get('longitude'))

        # Zorunlu alan kontrolü
        if not name or not address:
            flash("Mağaza adı ve fiziksel adres zorunludur.", "error")
            return redirect(url_for('store.store_details', store_id=store_id))

        try:
            # Veritabanında güncelle
            cursor.execute("""
                UPDATE stores
                SET store_name = :name,
                    web_address = :web,
                    physical_address = :address,
                    latitude = :lat,
                    longitude = :lon
                WHERE store_id = :id
            """, {
                'name': name,
                'web': web,
                'address': address,
                'lat': latitude,
                'lon': longitude,
                'id': store_id
            })
            conn.commit()
            flash("Mağaza bilgileri başarıyla güncellendi.", "success")
            return redirect(url_for('store.store_details', store_id=store_id))
        except Exception as e:
            conn.rollback()
            flash(f"Güncelleme hatası: {str(e)}", "error")
            return redirect(url_for('store.store_details', store_id=store_id))
        finally:
            cursor.close()

    # GET isteği ise mevcut mağaza verisini çek ve göster
    try:
        cursor.execute("""
            SELECT store_id, store_name, web_address, physical_address, latitude, longitude
            FROM stores
            WHERE store_id = :id
        """, id=store_id)
        row = cursor.fetchone()
        if not row:
            flash("Mağaza bulunamadı.", "error")
            return redirect(url_for('store.list_stores'))
        
        store = {
            'id': row[0],
            'name': row[1],
            'web_address': row[2],
            'physical_address': row[3],
            'latitude': row[4],
            'longitude': row[5]
        }
        return render_template('store_details.html', store=store)
    except Exception as e:
        flash(f"Hata oluştu: {str(e)}", "error")
        return redirect(url_for('store.list_stores'))
    finally:
        cursor.close()


def to_float_or_none(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None
