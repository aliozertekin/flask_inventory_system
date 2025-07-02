from flask import Blueprint, render_template, request, redirect, url_for
from db.connection import conn

customer_bp = Blueprint('customer_bp', __name__)

@customer_bp.route('/customers')
def list_customers():
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id, full_name, email_address FROM customers")
    data = cursor.fetchall()
    print("Veritabanından çekilen müşteriler:", data)  # Konsola yazdır
    return render_template('customers.html', customers=data)

@customer_bp.route('/customers/add', methods=['POST'])
def add_customer():
    name = request.form['name']
    email = request.form['email']
    cursor = conn.cursor()
    cursor.callproc("add_customer", [email, name])
    return redirect(url_for('customer_bp.list_customers'))