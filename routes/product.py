from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, abort
from db.connection import get_connection
import cx_Oracle, io, json
from datetime import datetime


product_bp = Blueprint('product', __name__, url_prefix='/product')

@product_bp.route('/')
def list_products():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT product_id, product_name, unit_price, product_details, image_filename
            FROM products ORDER BY product_id
        """)
        products = cursor.fetchall()
        product_list = []
        for p in products:
            details_blob = p[3]
            details = ""
            if details_blob:
                try:
                    details = details_blob.read().decode('utf-8')
                except Exception:
                    details = "<BLOB data okunamadı>"
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
        conn.close()

from flask import request, redirect, url_for, render_template, flash
from db.connection import get_connection
import cx_Oracle

@product_bp.route('/add', methods=['GET', 'POST'])
def add_product():
    conn = get_connection()
    
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        details = request.form.get('details')
        file = request.files.get('product_image')

        if not name or not price:
            flash("Ürün adı ve fiyat zorunludur.", "error")
            return render_template('product_add.html')

        try:
            price = float(price)
        except ValueError:
            flash("Fiyat geçerli bir sayı olmalıdır.", "error")
            return render_template('product_add.html')

        image_blob = None
        image_mime = None
        image_filename = None

        if file and file.filename:
            image_blob = file.read()
            image_mime = file.mimetype
            image_filename = file.filename

        try:
            cursor = conn.cursor()

            # bytes -> cx_Oracle Binary
            details_blob = cursor.var(cx_Oracle.BLOB)
            image_blob = cursor.var(cx_Oracle.BLOB)

            args = [
                name,
                price,
                details_blob,
                image_blob,
                image_mime,
                image_filename,
                None  # image_charset
            ]

            # DEBUG:
            print("Calling ADD_PRODUCT with args:")
            for i, arg in enumerate(args):
                print(f"{i+1}: {type(arg).__name__} => {repr(arg)[:80]}")

            cursor.callproc("SYSTEM.ADD_PRODUCT", args)
            conn.commit()
            flash("Ürün başarıyla eklendi.", "success")
            return redirect(url_for('product.list_products'))

        except Exception as e:
            import traceback
            traceback.print_exc()
            flash(f"Hata oluştu: {str(e)}", "error")
            conn.rollback()
            return render_template('product_add.html')

        finally:
            cursor.close()
            conn.close()

    return render_template('product_add.html')



@product_bp.route('/<int:product_id>', methods=['GET', 'POST'])
def product_details(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        details = request.form.get('details')
        file = request.files.get('product_image')

        if not name or not price:
            flash("Ürün adı ve fiyat zorunludur.", "error")
            cursor.close()
            conn.close()
            return redirect(url_for('product.product_details', product_id=product_id))

        try:
            price = float(price)
        except ValueError:
            flash("Fiyat geçerli bir sayı olmalıdır.", "error")
            cursor.close()
            conn.close()
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
                    'details': cx_Oracle.Binary(details.encode('utf-8')) if details else None,
                    'image_blob': cx_Oracle.Binary(image_blob),
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
                    'details': cx_Oracle.Binary(details.encode('utf-8')) if details else None,
                    'pid': product_id
                })
            conn.commit()
            flash("Ürün başarıyla güncellendi.", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Güncelleme hatası: {str(e)}", "error")
        finally:
            cursor.close()
            conn.close()

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

        details_bytes = p[3]
        details = ''
        if details_bytes:
            try:
                details = details_bytes.read().decode('utf-8')
            except Exception:
                details = "<BLOB data okunamadı>"

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
        conn.close()

@product_bp.route('/image/<int:product_id>')
def get_image(product_id):
    conn = get_connection()
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
        conn.close()

@product_bp.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = get_connection()
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
        conn.close()
    return redirect(url_for('product.list_products'))

@product_bp.route('/delete_image/<int:product_id>', methods=['POST'])
def delete_product_image(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc("DELETE_PRODUCT_IMAGE", [product_id])
        conn.commit()
        flash("Ürün resmi başarıyla silindi.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Resim silme hatası: {str(e)}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('product.product_details', product_id=product_id))

@product_bp.route('/logs')
def products_log():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT log_id, product_id, operation, changed_by, changed_at, old_data, new_data
            FROM product_log
            ORDER BY changed_at DESC
            FETCH FIRST 100 ROWS ONLY
        """)
        columns = [col[0].lower() for col in cursor.description]
        rows = cursor.fetchall()
        logs = [dict(zip(columns, row)) for row in rows]
        for log in logs:
            log['table_name'] = 'PRODUCTS'
        return render_template('log_generic.html', logs=logs, log_type='products')
    except Exception as e:
        flash(f"Loglar alınırken hata oluştu: {str(e)}", "error")
        return render_template('log_generic.html', logs=[], log_type='products')
    finally:
        cursor.close()
        conn.close()

@product_bp.route('/reviews')
def reviews():
    search_term = request.args.get('search', '').strip()
    rating_filter = request.args.get('rating_filter', '')
    page = int(request.args.get('page', 1))
    per_page = 10

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT product_name, product_details FROM products")
        rows = cursor.fetchall()
        
        all_reviews = []

        for name, details_blob in rows:
            if not details_blob:
                continue
            
            try:
                blob_bytes = details_blob.read()
                details_json = blob_bytes.decode('utf-8')
                details_dict = json.loads(details_json)
                reviews = details_dict.get('reviews', [])
            except Exception as e:
                print(f"JSON parse error for product {name}: {e}")
                continue
            
            if not reviews:
                continue
            
            avg_rating = round(sum(r.get('rating', 0) for r in reviews) / len(reviews), 2)
            
            for r in reviews:
                all_reviews.append({
                    'product_name': name,
                    'rating': r.get('rating'),
                    'review': r.get('review'),
                    'avg_rating': avg_rating,
                    # Bu alanlar şablonun kullandığı için örnek veri verdim, gerekirse düzenle
                    'product_image': None,
                    'review_date': None,
                    'customer_name': None
                })
        
        # Filtreleme: rating_filter varsa ona göre filtrele
        if rating_filter.isdigit():
            filter_rating = int(rating_filter)
            all_reviews = [r for r in all_reviews if r['rating'] == filter_rating]

        # Filtreleme: search_term varsa review metninde veya ürün adında ara (küçük harf ile)
        if search_term:
            search_term_lower = search_term.lower()
            all_reviews = [r for r in all_reviews if search_term_lower in (r['review'] or '').lower() or search_term_lower in (r['product_name'] or '').lower()]
        
        total = len(all_reviews)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_reviews = all_reviews[start:end]

        print(f"Toplam review sayısı: {len(paginated_reviews)}")
        if paginated_reviews:
            print("İlk review:", paginated_reviews[0])
        else:
            print("Hiç review yok!")

        return render_template(
            'product_reviews.html',
            reviews=paginated_reviews,
            search_term=search_term,
            rating_filter=rating_filter,
            page=page,
            per_page=per_page,
            total=total
        )

    except Exception as e:
        flash(f"İncelemeler alınırken hata: {str(e)}", "error")
        return render_template('product_reviews.html', reviews=[])
    finally:
        cursor.close()
        conn.close()

@product_bp.route('/product/reviews/add', methods=['GET', 'POST'])
def add_review():
    conn = get_connection()
    if request.method == 'POST':
        product_id = request.form.get('product_id', type=int)
        customer_id = request.form.get('customer_id', type=int)
        rating = request.form.get('rating', type=int)
        review_text = request.form.get('review_text', '').strip()
        
        if not (product_id and customer_id and rating and review_text):
            flash("Tüm alanlar doldurulmalıdır.", "error")
            return redirect(url_for('product.add_review'))
        
        try:
            cursor = conn.cursor()
            cursor.callproc('add_review', [product_id, customer_id, rating, review_text])
            cursor.commit()
            cursor.close()
            flash("İnceleme başarıyla eklendi!", "success")
            return redirect(url_for('product.reviews'))
        except Exception as e:
            flash(f"Hata oluştu: {e}", "error")
            return redirect(url_for('product.add_review'))
        
    # GET isteğinde boş form gönder
    return render_template('add_review.html')