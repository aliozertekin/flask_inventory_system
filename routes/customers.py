from flask import Blueprint, render_template, request, redirect, url_for
from db.connection import conn

customer_bp = Blueprint('customer_bp', __name__)
PER_PAGE = 20

@customer_bp.route('/customers')
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

@customer_bp.route('/customers/add', methods=['POST'])
def add_customer():
    name = request.form['name']
    email = request.form['email']
    cursor = conn.cursor()
    cursor.callproc("add_customer", [email, name])
    return redirect(url_for('customer_bp.list_customers'))

@customer_bp.route('/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        cursor.execute("""
            UPDATE customers SET full_name = :name, email_address = :email
            WHERE customer_id = :cid
        """, {'name': name, 'email': email, 'cid': customer_id})
        conn.commit()
        return redirect(url_for('customer_bp.list_customers'))

    cursor.execute("SELECT customer_id, full_name, email_address FROM customers WHERE customer_id = :cid",
                   {'cid': customer_id})
    customer = cursor.fetchone()
    cursor.close()
    return render_template('customer_edit.html', customer=customer)

@customer_bp.route('/customers/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE customer_id = :cid", {'cid': customer_id})
    conn.commit()
    cursor.close()
    return redirect(url_for('customer_bp.list_customers'))
