from flask import Blueprint, render_template, request, redirect, url_for, flash
from db.connection import conn

customer_bp = Blueprint('customer_bp', __name__, url_prefix='/customers')

PER_PAGE = 20

@customer_bp.route('/')
def list_customers():
    cursor = conn.cursor()
    search_term = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)

    try:
        # Toplam sayıyı al
        count_query = "SELECT COUNT(*) FROM customers"
        if search_term:
            count_query += " WHERE LOWER(full_name) LIKE :search OR LOWER(email_address) LIKE :search"
            cursor.execute(count_query, {'search': f"%{search_term.lower()}%"})
        else:
            cursor.execute(count_query)
        total = cursor.fetchone()[0]

        # Sayfalama ve filtreli veri çekme
        base_query = f"""
        SELECT * FROM (
            SELECT a.*, ROWNUM rnum FROM (
                SELECT customer_id, full_name, email_address FROM customers
                {f"WHERE customer_id LIKE :search OR LOWER(full_name) LIKE :search OR LOWER(email_address) LIKE :search" if search_term else ""}
                ORDER BY customer_id
            ) a
            WHERE ROWNUM <= :end_row
        )
        WHERE rnum > :start_row 
        """
        params = {
            'end_row': page * PER_PAGE,
            'start_row': (page - 1) * PER_PAGE
        }
        if search_term:
            params['search'] = f"%{search_term.lower()}%"

        cursor.execute(base_query, params)
        data = cursor.fetchall()

        return render_template("customers.html",
                               customers=data,
                               search_term=search_term,
                               page=page,
                               per_page=PER_PAGE,
                               total=total)
    finally:
        cursor.close()

@customer_bp.route('/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        cursor = conn.cursor()
        try:
            cursor.callproc("add_customer", [email, name])
            flash('Müşteri başarıyla eklendi', 'success')
            return redirect(url_for('customer_bp.list_customers'))
        except Exception as e:
            flash(f'Müşteri eklenirken hata oluştu: {str(e)}', 'error')
        finally:
            cursor.close()
    
    return render_template('customer_add.html')

@customer_bp.route('/edit/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        try:
            cursor.execute("""
                UPDATE customers SET full_name = :name, email_address = :email
                WHERE customer_id = :cid
            """, {'name': name, 'email': email, 'cid': customer_id})
            conn.commit()
            flash('Müşteri başarıyla güncellendi', 'success')
            return redirect(url_for('customer_bp.list_customers'))
        except Exception as e:
            flash(f'Güncelleme sırasında hata oluştu: {str(e)}', 'error')
        finally:
            cursor.close()

    try:
        cursor.execute("SELECT customer_id, full_name, email_address FROM customers WHERE customer_id = :cid",
                    {'cid': customer_id})
        customer = cursor.fetchone()
        if not customer:
            flash('Müşteri bulunamadı', 'error')
            return redirect(url_for('customer_bp.list_customers'))
        return render_template('customer_edit.html', customer=customer)
    finally:
        cursor.close()

@customer_bp.route('/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM customers WHERE customer_id = :cid", {'cid': customer_id})
        conn.commit()
        flash('Müşteri başarıyla silindi', 'success')
    except Exception as e:
        flash(f'Silme işlemi sırasında hata oluştu: {str(e)}', 'error')
    finally:
        cursor.close()
    return redirect(url_for('customer_bp.list_customers'))

@customer_bp.route('/logs')
def customers_log():
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT log_id, customer_id, operation, changed_by, changed_at, old_data, new_data
            FROM customer_log
            ORDER BY changed_at DESC
            FETCH FIRST 100 ROWS ONLY
        """)
        columns = [col[0].lower() for col in cursor.description]
        rows = cursor.fetchall()
        logs = [dict(zip(columns, row)) for row in rows]
        for log in logs:  
            log['table_name'] = 'CUSTOMERS'  
        return render_template('log_generic.html', logs=logs, log_type='customers')
    finally:
        cursor.close()