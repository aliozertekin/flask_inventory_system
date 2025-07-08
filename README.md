
# Oracle Inventory, Order & Shipment Management System

This project is a complete **Inventory, Order, and Shipment Management System** built on **Oracle SQL and PL/SQL** with a **Flask** frontend. It manages product stocks, orders, shipments, customers, and stores using relational database structures with triggers, sequences, views, stored procedures, and audit logging.

Created by **aliozertekin**.

---

## Features

- Inventory management per store and product  
- Full order and order item tracking  
- Shipment handling and status tracking  
- Audit log tables for change tracking  
- JSON-supported product details  
- Blob/image storage for product and store visuals  
- Identity columns and sequences for auto-incrementing keys  
- Data integrity via foreign key and check constraints  
- Summary views for customer orders and purchased products  
- Automatic restock trigger on order cancel/refund  
- Modern UI with Flask, HTML, CSS, JavaScript  
- Oracle backend with PL/SQL stored procedures and packages  

---

## Technologies Used

- Python 3.13+  
- Flask  
- cx_Oracle  
- Oracle Database 21c+  
- HTML, CSS, JavaScript  

---

## Schema Overview

### Core Tables

| Table Name    | Description                          |
|---------------|------------------------------------|
| PRODUCTS      | Stores product data with images and JSON details |
| STORES        | Physical or virtual store information |
| CUSTOMERS     | Customer identity and contact information |
| ORDERS       | Customer orders                     |
| ORDER_ITEMS   | Line items within orders            |
| SHIPMENTS     | Delivery records linked to orders  |
| INVENTORY    | Stock levels per product and store |

### Logging Tables

| Table Name       | Description                 |
|------------------|-----------------------------|
| ORDER_LOG        | Logs order-level changes    |
| ORDER_ITEMS_LOG  | Logs order item changes     |
| PRODUCT_LOG      | Logs product changes        |
| INVENTORY_LOG    | Logs inventory changes      |
| SHIPMENTS_LOG    | Logs shipment updates       |
| STORE_LOG        | Logs store-level changes    |
| CUSTOMER_LOG     | Logs customer changes       |
| AUDIT_LOG        | General audit trail         |

---

## Views

- `CUSTOMER_ORDER_PRODUCTS`  
  Summarizes each order with customer and purchased product details.

- `INVENTORY_VIEW`  
  Displays stock levels by store and product.

- `ORDERS_VIEW`  
  Overview of orders and their statuses.

- `PRODUCT_ORDERS`  
  Counts orders per product for popularity analysis.

- `PRODUCT_REVIEWS`  
  Aggregates product reviews (if applicable).

- `STORE_ORDERS`  
  Lists orders grouped by store.

- `VW_INVENTORY_STATS`  
  Inventory statistical summaries such as averages and minimum stock.

- `VW_ORDER_STATS`  
  Summarized order statistics including totals and cancellation rates.

- `VW_USER_COUNT`  
  Summarized counts of users/customers.

---

## Triggers

- `TRG_RESTOCK_ON_CANCEL_AND_REFUND`  
  Automatically restocks inventory when an order is canceled or refunded.

- `TRG_AUDIT_CUSTOMERS`  
  Audits all insert, update, delete operations on the `CUSTOMERS` table.

- `TRG_AUDIT_INVENTORY`  
  Tracks changes on the `INVENTORY` table.

- `TRG_AUDIT_ORDER_ITEMS`  
  Logs changes to order items.

- `TRG_AUDIT_ORDERS`  
  Audits changes on the `ORDERS` table.

- `TRG_AUDIT_PRODUCTS`  
  Audits changes on the `PRODUCTS` table.

- `TRG_AUDIT_SHIPMENTS`  
  Logs shipment status and data changes.

- `TRG_AUDIT_STORES`  
  Audits changes on the `STORES` table.

- `TRG_LOG_CUSTOMERS`, `TRG_LOG_INVENTORY`, `TRG_LOG_ORDER_ITEMS`, `TRG_LOG_ORDERS`, `TRG_LOG_PRODUCTS`, `TRG_LOG_SHIPMENTS`, `TRG_LOG_STORES`  
  Additional logging triggers that record detailed changes to their respective log tables.

---

## Stored Procedures

- `ADD_CUSTOMER`  
  Adds a new customer record.

- `ADD_INVENTORY`  
  Inserts or updates inventory stock.

- `ADD_ORDER`  
  Creates new orders and manages related tables.

- `ADD_PRODUCT`  
  Adds a new product.

- `ADD_SHIPMENT`  
  Adds shipment details for an order.

- `ADD_STORE`  
  Inserts a new store record.

- `DELETE_CUSTOMER`  
  Deletes a customer record (soft/hard as per business rules).

- `DELETE_INVENTORY`  
  Deletes or updates inventory records.

- `DELETE_ORDER`  
  Deletes an order and its items.

- `DELETE_PRODUCT`  
  Deletes a product.

- `DELETE_PRODUCT_IMAGE`  
  Deletes images associated with products.

- `DELETE_SHIPMENT`  
  Deletes shipment records.

- `DELETE_STORE`  
  Deletes a store record.

- `PRINT_ORDER_TOTAL`  
  Calculates and outputs the total amount for an order.

- `RESTOCK_ORDER_PRODUCTS`  
  Restores inventory for canceled or refunded orders (used by restock trigger).

---

## Sequence Generators

| Sequence Name   | Starting Value |
|-----------------|----------------|
| INVENTORY_SEQ   | 568            |
| SHIPMENT_SEQ    | 2029           |
| SHIPMENTS_SEQ   | 2029           |
| STORE_SEQ       | 31             |

---

## Installation & Setup

1. Ensure Oracle Database 21c+ is running and accessible.  
2. Clone this repository:
   ```bash
   git clone https://github.com/your-username/flask_inventory_system.git
   cd flask_inventory_system
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   If you don’t want a separate file, you can also install them directly with:
   ```bash
   pip install flask cx_Oracle reportlab python-dotenv wtforms flask-wtf email-validator
   ```
5. Configure Oracle connection in `db/connection.py`:
   ```python
   import cx_Oracle

   dsn = cx_Oracle.makedsn("localhost", 1521, service_name="FREE")
   conn = cx_Oracle.connect("your_user", "your_password", dsn=dsn)
   ```
6. Run the SQL scripts in `db/sql/` folder (in order) to create schema, procedures, views, and populate sample data. Example:
   ```sql
   @co_create.sql
   @co_install.sql
   @co_populate.sql
   ```
5. Run the SQL script all_queries in `db/sql/methods` folder to create user defined schema, procedures, views. Example:
   ```sql
   @all_queries.sql
   ```
7. Start the Flask application:
   ```bash
   python app.py
   ```
8. Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## Sample API Usage

### Add Order

**POST** `/orders/add`

**Request Body Example:**

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

## Project Structure

```
flask_inventory_system/
│
├── app.py                      # Main application entry point
├── db/
│   ├── connection.py           # Oracle DB connection setup
│   └── sql/                    # SQL scripts for schema and logic
│
├── images/                     # Images of the website
├── modules/                    # Modules for easier handling
├── routes/                     # Flask route handlers
├── templates/                  # HTML templates
├── static/                     # CSS and JavaScript assets
├── LICENSE
└── README.md
```

---

## License

This project is licensed under the MIT License.

---

Built with Flask and Oracle PL/SQL  
Created and maintained by aliozertekin.
