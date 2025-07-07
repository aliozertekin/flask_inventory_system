# Flask Inventory & Order Management System

A professional-grade inventory and order management system built using **Flask** and **Oracle PL/SQL**. This application allows seamless tracking and management of customers, products, orders, and stock levels across stores, backed by robust PL/SQL stored procedures.

---

## Features

- Customer Management  
  Add, edit, and view customers.

- Inventory Management  
  Add and track inventory per store. View inventory logs.

- Order Processing  
  Create new orders with automatic inventory checks and deduction. Supports multi-item orders via Oracle user-defined types.

- Product Management  
  Add, view, and edit product listings.

- Order Status Management  
  Supports order statuses: `OPEN`, `PAID`, `SHIPPED`, `COMPLETE`, `CANCELLED`, `REFUNDED`.

- Order Details View  
  Includes line item breakdown and order history.

- Oracle Integration  
  Uses stored procedures, packages, and views written in PL/SQL for backend logic.

- Modern UI  
  Built with HTML templates, CSS styling, and JavaScript enhancements.

---

## Technologies Used

- Python 3.13+
- Flask
- cx_Oracle
- Oracle Database 21c+
- HTML, CSS, JavaScript

### Key Database Concepts

- User-defined types: `ORDER_ITEM_REC`, `ORDER_ITEM_TABLE`
- Stored procedure: `ADD_ORDER`
- View: `ORDERS_VIEW`

---

## Project Structure

```
flask_inventory_system/
│
├── app.py                      # Main application entry point
├── db/
│   ├── connection.py           # Oracle DB connection setup
│   └── sql/                    # SQL scripts for schema and logic
│
├── routes/                     # Flask route handlers
├── templates/                  # HTML templates
├── static/                     # CSS and JavaScript
├── LICENSE
└── README.md
```

---

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/flask_inventory_system.git
cd flask_inventory_system
```

### 2. Install dependencies

```bash
pip install flask cx_Oracle
```

### 3. Configure Oracle connection

Edit `db/connection.py`:

```python
import cx_Oracle

dsn = cx_Oracle.makedsn("localhost", 1521, service_name="FREE")
conn = cx_Oracle.connect("your_user", "your_password", dsn=dsn)
```

### 4. Start the application

```bash
python app.py
```

Open your browser and go to [http://localhost:5000](http://localhost:5000)

---

## Sample API Usage

### Add Order

**POST** `/orders/add`

#### Request Body

```json
{
  "customer_id": 1,
  "store_id": 101,
  "items": [
    {
      "product_id": 2001,
      "quantity": 2,
      "unit_price": 50.0
    },
    {
      "product_id": 2002,
      "quantity": 1,
      "unit_price": 75.0
    }
  ]
}
```

---

## Included SQL Scripts

Located in `db/sql/`:

- `co_create.sql` – Create schema and base objects
- `co_install.sql` – Create procedures, types, packages, views
- `co_populate.sql` – Sample data population
- `methods/` – Modular scripts for database setup

---

## Future Improvements

- User authentication and role-based access
- Product categorization
- Search and filtering capabilities
- Full REST API support
- Unit tests and logging

---

## License

This project is licensed under the MIT License.

---

Built with Flask and Oracle PL/SQL
