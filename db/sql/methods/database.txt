# Database Schema Documentation

## Overview
This database schema models an e-commerce system with inventory management, order processing, auditing, and reporting capabilities. Key features include:
- Customer, product, and store management
- Inventory tracking across multiple stores
- Order processing with shipment tracking
- Comprehensive audit logging
- Materialized views for reporting
- PL/SQL packages for business logic

## Core Tables

### `CUSTOMERS`
- Stores customer information
- **Columns**: `customer_id` (PK), `email_address` (unique), `full_name`

### `PRODUCTS`
- Manages product catalog
- **Columns**: `product_id` (PK), `product_name`, `unit_price`, `product_details` (JSON BLOB), image-related columns
- **Constraint**: `product_details` must be valid JSON

### `STORES`
- Tracks physical/virtual stores
- **Columns**: `store_id` (PK), `store_name` (unique), `web_address`, `physical_address`, geolocation fields
- **Constraint**: Must have at least one address type

### `INVENTORY`
- Manages stock levels
- **Columns**: `inventory_id` (PK), `store_id` (FK), `product_id` (FK), `product_inventory`
- **Relations**: Links products to stores

### `ORDERS`
- Handles order headers
- **Columns**: `order_id` (PK), `order_tms`, `customer_id` (FK), `order_status`, `store_id` (FK)
- **Valid Statuses**: OPEN, PAID, SHIPPED, COMPLETE, CANCELLED, REFUNDED

### `ORDER_ITEMS`
- Contains order line items
- **Columns**: `order_id` (PK/FK), `line_item_id` (PK), `product_id` (FK), `unit_price`, `quantity`, `shipment_id` (FK)

### `AUDIT_LOG`
- Tracks all data changes
- **Columns**: `log_id` (PK), `table_name`, `operation`, `changed_by`, `changed_at`, `old_data`, `new_data`

## Key Views

### `CUSTOMER_ORDER_PRODUCTS`
- Combines orders with customer details and product lists
- **Columns**: Order details, customer info, `order_total`, aggregated `items`

### `PRODUCT_REVIEWS`
- Extracts reviews from product JSON details
- **Columns**: `product_name`, `rating`, `avg_rating`, `review`

### `STORE_ORDERS`
- Sales analytics by store
- **Columns**: Store details, `order_status`, `order_count`, `total_sales` with rollups

### `VW_ORDER_STATS`
- Key order metrics
- **Columns**: `total_orders`, `total_cost` (excludes cancellations)

## Materialized View

### `MV_DAILY_STATS`
- Daily business snapshot
- **Columns**: `report_date`, `user_count`, inventory stats, daily sales
- **Refresh**: Complete on demand

## Key Procedures

### Order Processing
- `ADD_ORDER`: Creates new orders with inventory checks (FIFO allocation)
- `RESTOCK_ORDER_PRODUCTS`: Replenishes inventory on cancellations/refunds

### Inventory Management
- `ADD_INVENTORY`: Updates stock levels with audit logging
- `ADD_INVENTORY` params: `store_id`, `product_id`, `product_amount`, outputs old/new quantities

### CRUD Operations
- `ADD_CUSTOMER`/`DELETE_CUSTOMER`: Customer lifecycle management
- `ADD_PRODUCT`/`DELETE_PRODUCT`: Product catalog management

## Auditing System
- Triggers (`trg_audit_*`) automatically log changes to:
  - Customers, Products, Orders, Order Items, Inventory, Shipments, Stores
- Captures before/after states in `AUDIT_LOG`
- Tracks: operation type, user, timestamp

## Dashboard Package
### `DASHBOARD_PKG`
- `GET_DASHBOARD_STATS`: Returns key metrics (user count, inventory value, orders)
- `GET_MONTHLY_CHANGES`: Provides YoY comparison of sales metrics

## Design Patterns
1. **Inventory Tracking**: FIFO-based stock allocation in orders
2. **Data Auditing**: Comprehensive change tracking via triggers
3. **JSON Handling**: Product details/reviews stored as JSON
4. **Reporting Optimization**: Materialized views for aggregated data
5. **Modular Logic**: PL/SQL packages encapsulate business rules