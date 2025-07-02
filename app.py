from flask import Flask
from routes.orders import order_bp
from routes.customers import customer_bp

app = Flask(__name__)
app.register_blueprint(customer_bp)
app.register_blueprint(order_bp)

if __name__ == "__main__":
    app.run(debug=True)