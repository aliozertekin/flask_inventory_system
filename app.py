from flask import Flask, render_template, session, redirect, url_for, request
from modules.utilities import get_secret
from routes.customers import customer_bp
from routes.orders import order_bp
from routes.index import index_bp
from routes.inventory import inventory_bp
from routes.log import log_bp
from routes.product import product_bp
from routes.terms import terms_bp
from routes.privacy import privacy_bp
from routes.store import store_bp
from routes.shipments import shipments_bp
from routes.order_items import order_items_bp
from routes.auth import auth_bp

app = Flask(__name__)

app.secret_key = get_secret()

app.register_blueprint(customer_bp)
app.register_blueprint(order_bp)
app.register_blueprint(index_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(log_bp)
app.register_blueprint(product_bp)
app.register_blueprint(terms_bp)
app.register_blueprint(privacy_bp)
app.register_blueprint(store_bp)
app.register_blueprint(shipments_bp)
app.register_blueprint(order_items_bp)
app.register_blueprint(auth_bp)

# Genel 500 Internal Server Error için
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, show_details=True, error_details=str(e)), 500

# 404 Not Found için
@app.errorhandler(404)
def not_found_error(e):
    return render_template('error.html', error_code=404, show_details=False), 404

@app.errorhandler(Exception)
def handle_exception(e):
    # Geliştirme modunda detay göster, değilse gösterme
    show_details = app.debug
    return render_template('error.html', error_code="ERR", show_details=show_details, error_details=str(e)), 500

@app.before_request
def require_login():
    allowed_paths = ['/login', '/static/','/help','/forgot_password']
    if request.path.startswith(tuple(allowed_paths)):
        return
    if 'user' not in session and not request.path.startswith('/login'):
        return redirect(url_for('auth.login'))

if __name__ == "__main__":
    app.run(debug=True)
