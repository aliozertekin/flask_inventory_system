from flask import Flask
from routes.orders import order_bp
from routes.customers import customer_bp
from routes.index import index_bp
from routes.inventory import inventory_bp
from routes.log import log_bp
from routes.product import product_bp
from routes.terms import terms_bp
from routes.privacy import privacy_bp

import secrets


app = Flask(__name__)


app.secret_key = secrets.token_hex(16) # Gizli anahtar oluştur.

app.register_blueprint(inventory_bp)
app.register_blueprint(log_bp)
app.register_blueprint(index_bp)
app.register_blueprint(order_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(product_bp)
app.register_blueprint(terms_bp)
app.register_blueprint(privacy_bp)


if __name__ == "__main__":
    app.run(debug=True)
