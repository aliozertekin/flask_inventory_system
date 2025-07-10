import serial
import cx_Oracle
import time

# Seri port bağlantısı
ser = serial.Serial('COM3', 9600, timeout=1)

# Oracle bağlantı bilgileri
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="FREE")
conn = cx_Oracle.connect(user="system", password="admin", dsn=dsn)


def process_serial_line(line):
    try:
        cursor = conn.cursor()
        store_id_str, product_id_str, quantity_str = line.strip().split(",")
        store_id = int(store_id_str)
        product_id = int(product_id_str)
        quantity = int(quantity_str)

        old_amount = cursor.var(cx_Oracle.NUMBER)
        new_amount = cursor.var(cx_Oracle.NUMBER)

        cursor.callproc("ADD_INVENTORY", [
            store_id,
            product_id,
            quantity,
            old_amount,
            new_amount,
            "MACHINE"
        ])

        print(f"[✓] Store={store_id} Product={product_id} +{quantity} → New: {new_amount.getvalue()}")

        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"[Hata] {e}")

print("Dinleniyor...")

while True:
    try:
        cursor = conn.cursor()
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(f"Tarih: {time.strftime("%c")} Alındı: {line}")
                process_serial_line(line)
    except KeyboardInterrupt:
        print("Durduruluyor...")
        break
    except Exception as e:
        print(f"Okuma Hatası: {e}")
        time.sleep(1)
ser.close()
cursor.close()
