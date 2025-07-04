from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, abort
from db.connection import conn
import cx_Oracle
import io
from datetime import datetime

product_bp = Blueprint('product', __name__, url_prefix='/product')

@product_bp.route('/')
def list_products():
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT product_id, product_name, unit_price, product_details, image_filename
            FROM products ORDER BY product_id
        """)
        products = cursor.fetchall()
        product_list = []
        for p in products:
            # product_details BLOB ise stringe çevir
            details_blob = p[3]
            details = details_blob.read().decode('utf-8') if details_blob else ""

            product_list.append({
                'id': p[0],
                'name': p[1],
                'price': float(p[2]) if p[2] is not None else 0,
                'details': details,
                'image_filename': p[4]
            })
        return render_template('product.html', products=product_list)
    except Exception as e:
        flash(f"Hata oluştu: {str(e)}", "error")
        return render_template('product.html', products=[])
    finally:
        cursor.close()

@product_bp.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        details = request.form.get('details')  # Metin, JSON ya da blob olabilir, uygulamaya göre ayarla
        file = request.files.get('product_image')

        if not name or not price:
            flash("Ürün adı ve fiyat zorunludur.", "error")
            return render_template('product_add.html')

        try:
            price = float(price)
        except ValueError:
            flash("Fiyat geçerli bir sayı olmalıdır.", "error")
            return render_template('product_add.html')

        # Dosya ile ilgili değişkenler
        image_blob = None
        image_mime = None
        image_filename = None
        image_charset = None  # Genellikle None
        image_last_updated = None  # Prosedürde sysdate kullandığın için bunu gönderme zorunda değilsin

        if file and file.filename != '':
            image_blob = file.read()
            image_mime = file.mimetype
            image_filename = file.filename
            image_charset = None

        cursor = conn.cursor()
        try:
            # Prosedürü çağırırken opsiyonel parametreler için None gönderiyoruz
            cursor.callproc("ADD_PRODUCT", [
                name,
                price,
                details.encode('utf-8') if details else None,  # details BLOB ise encode et (opsiyonel)
                image_blob,
                image_mime,
                image_filename,
                image_charset
            ])
            conn.commit()
            flash("Ürün başarıyla eklendi.", "success")
            return redirect(url_for('product.list_products'))
        except Exception as e:
            conn.rollback()
            flash(f"Hata oluştu: {str(e)}", "error")
            return render_template('product_add.html')
        finally:
            cursor.close()

    return render_template('product_add.html')

@product_bp.route('/<int:product_id>', methods=['GET', 'POST'])
def product_details(product_id):
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        details = request.form.get('details')
        file = request.files.get('product_image')

        if not name or not price:
            flash("Ürün adı ve fiyat zorunludur.", "error")
            return redirect(url_for('product.product_details', product_id=product_id))

        try:
            price = float(price)
        except ValueError:
            flash("Fiyat geçerli bir sayı olmalıdır.", "error")
            return redirect(url_for('product.product_details', product_id=product_id))

        image_blob = None
        image_mime = None
        image_filename = None
        image_charset = None
        image_last_updated = None

        if file and file.filename != '':
            image_blob = file.read()
            image_mime = file.mimetype
            image_filename = file.filename
            image_charset = None
            image_last_updated = datetime.now()

        try:
            if image_blob:
                cursor.execute("""
                    UPDATE products SET
                        product_name = :name,
                        unit_price = :price,
                        product_details = :details,
                        product_image = :image_blob,
                        image_mime_type = :image_mime,
                        image_filename = :image_filename,
                        image_charset = :image_charset,
                        image_last_updated = :image_last_updated
                    WHERE product_id = :pid
                """, {
                    'name': name,
                    'price': price,
                    'details': details,
                    'image_blob': image_blob,
                    'image_mime': image_mime,
                    'image_filename': image_filename,
                    'image_charset': image_charset,
                    'image_last_updated': image_last_updated,
                    'pid': product_id
                })
            else:
                cursor.execute("""
                    UPDATE products SET
                        product_name = :name,
                        unit_price = :price,
                        product_details = :details
                    WHERE product_id = :pid
                """, {
                    'name': name,
                    'price': price,
                    'details': details,
                    'pid': product_id
                })
            conn.commit()
            flash("Ürün başarıyla güncellendi.", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Güncelleme hatası: {str(e)}", "error")
        finally:
            cursor.close()

        return redirect(url_for('product.product_details', product_id=product_id))
    # GET kısmı
    try:
        cursor.execute("""
            SELECT product_id, product_name, unit_price, product_details, image_filename
            FROM products WHERE product_id = :pid
        """, {'pid': product_id})
        p = cursor.fetchone()
        if p is None:
            flash("Ürün bulunamadı.", "error")
            return redirect(url_for('product.list_products'))
    
        # product_details BLOB olarak geliyorsa decode et
        details_bytes = p[3]
        if details_bytes:
            try:
                details = details_bytes.read().decode('utf-8')
            except Exception:
                details = "<BLOB data>"
        else:
            details = ''
    
        product = {
            'id': p[0],
            'name': p[1],
            'price': float(p[2]) if p[2] is not None else 0,
            'details': details,
            'image_filename': p[4]
        }
        return render_template('product_details.html', product=product)
    except Exception as e:
        flash(f"Hata oluştu: {str(e)}", "error")
        return redirect(url_for('product.list_products'))
    finally:
        cursor.close()


@product_bp.route('/image/<int:product_id>')
def get_image(product_id):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT product_image, image_mime_type
            FROM products
            WHERE product_id = :pid AND product_image IS NOT NULL
        """, {'pid': product_id})
        row = cursor.fetchone()
        if row:
            blob_data = row[0].read()
            mime_type = row[1] or 'application/octet-stream'
            return send_file(
                io.BytesIO(blob_data),
                mimetype=mime_type,
                as_attachment=False,
                download_name=f'image_{product_id}'
            )
        else:
            abort(404)
    except Exception:
        abort(404)
    finally:
        cursor.close()

@product_bp.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM products WHERE product_id = :pid", {'pid': product_id})
        if cursor.rowcount == 0:
            flash("Silinecek ürün bulunamadı.", "error")
        else:
            conn.commit()
            flash("Ürün başarıyla silindi.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Silme hatası: {str(e)}", "error")
    finally:
        cursor.close()
    return redirect(url_for('product.list_products'))
