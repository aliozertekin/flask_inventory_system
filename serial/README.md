# Serial-Based Inventory Import System

This project simulates a real-time inventory update system using a **serial port** to transfer data from a virtual machine or device into an **Oracle Database** using **Python**.

## Overview

- One Python script listens to a serial port and imports the received inventory data into an Oracle database using a stored procedure.
- Another Python script simulates a machine sending random inventory data to the serial port for testing purposes.

## Requirements

### Python Packages
Install the required packages using:
```bash
pip install pyserial cx_Oracle
```

### Oracle Database
Ensure you have:
- Oracle XE running (e.g., service name `FREE`)
- A procedure called `ADD_INVENTORY` with the following signature:
```plsql
PROCEDURE ADD_INVENTORY(
    p_store_id   IN NUMBER,
    p_product_id IN NUMBER,
    p_quantity   IN NUMBER,
    p_old_amount OUT NUMBER,
    p_new_amount OUT NUMBER,
    p_source     IN VARCHAR2
);
```

## How It Works

### receiver.py
This script:
- Connects to `COM3` at 9600 baud.
- Reads lines in the format:
  ```
  store_id,product_id,quantity
  ```
- Calls `ADD_INVENTORY` in Oracle with parsed data.
- Prints results and commits to DB.

Example output:
```
Tarih: Tue Jul 16 10:12:45 2025 Alındı: 5,17,25
[✓] Store=5 Product=17 +25 → New: 125
```

### simulator.py
This script:
- Connects to `COM4`.
- Randomly generates store/product/quantity values.
- Sends them over serial every 1–60 seconds.

Example output:
```
Tarih: Tue Jul 16 10:15:20 2025 Gönderildi: Store_ID = 8, Product_ID = 22, Miktar = 14, Makine İsmi = MACHINE
```

## How to Run

### 1. Start Oracle and ensure `ADD_INVENTORY` exists.

### 2. Open one terminal and run the receiver:
```bash
python receiver.py
```

### 3. Open another terminal and run the simulator:
```bash
python simulator.py
```

> Make sure `COM3` and `COM4` are linked using a virtual COM port tool like com0com.

## File Overview

| File                 | Description                                |
|----------------------|--------------------------------------------|
| `receiver.py`        | Receives data from serial and updates DB   |
| `simulator.py`       | Sends test inventory data via serial       |
| `README.md`          | Project documentation                      |
| `serial_settings.png`| Settings for serial port                   |

## Notes

- This is a test setup using simulated serial communication.
- Replace `COM3` and `COM4` with the appropriate port names on your system.
