# Flask Inventory & Order Management System

A professional-grade inventory and order management system built with **Flask** and **Oracle PL/SQL**. This system allows managing customers, inventory, and orders with a focus on database procedures and performance via PL/SQL integration.

## 🔧 Features

- 📦 **Customer Management** – Add, view, and list customer records.
- 🏬 **Inventory Control** – Track product stock per store.
- 🛒 **Order Processing** – Place orders and automatically:
  - Check stock availability
  - Deduct stock upon order
  - Save order details and line items
- 🔁 **Order Status Management** – Update order statuses (`OPEN`, `PAID`, `SHIPPED`, `COMPLETE`, `CANCELLED`, `REFUNDED`) via the UI or API.
- 📊 **Oracle Integration** – Uses PL/SQL stored procedures and user-defined types for advanced backend processing.
- 💡 **Modern UI** – Clean and user-friendly interface with responsive design.

## ⚙️ Technologies Used

- Python 3.13+
- Flask (Routing, Templates)
- Oracle Database 21c+
- cx_Oracle (Python–Oracle DB API)
- HTML, CSS (Frontend)

## 🧠 Key Database Concepts

- **PL/SQL Stored Procedures**:
  - `ADD_ORDER` – Adds a new order, checks and updates inventory.
- **User-defined Types**:
  - `ORDER_ITEM_REC`, `ORDER_ITEM_TABLE` – Used to pass structured order item data to stored procedures.
- **Views**:
  - `ORDERS_VIEW` – Combines order data with customer and store info for frontend use.

## ▶️ Running the Project

### 1. Clone and set up

```bash
git clone https://github.com/your-username/flask_inventory_system.git
cd flask_inventory_system
```

### 2. Install dependencies

```bash
pip install flask cx_Oracle
```

### 3. Configure Oracle Connection

Update `db/connection.py`:

```python
import cx_Oracle

dsn = cx_Oracle.makedsn("localhost", 1521, service_name="FREE")  # Or your custom name
conn = cx_Oracle.connect("your_username", "your_password", dsn=dsn)
```

### 4. Start the server

```bash
python app.py
```

Visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## 🧪 Sample API: Add Order

`POST /orders/add`

**Payload:**
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

## 📌 Notes

- All order processing logic is handled via Oracle procedures for consistency and performance.
- Order IDs are generated via a sequence in the database.
- Orders can only be updated if their status is `OPEN`.

## 📎 Future Improvements

- Authentication and user roles (admin/operator)
- Product/category management
- RESTful API expansion
- Search & filtering
- Unit tests and logging

## 📄 License

MIT License

---

**Built with ❤️ using Flask & Oracle.**
