from flask import Blueprint, render_template, request, redirect, url_for, flash
from db.connection import conn
import cx_Oracle

store_bp = Blueprint('store', __name__, url_prefix='/store')

@store_bp.route('/')
def list_stores():
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