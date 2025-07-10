import time
import serial
import random

# COM port (örnek: COM5 veya /dev/ttyUSB0)
ser = serial.Serial('COM4', 9600)

# Store ve Product ID listeleri
store_ids = list(range(1, 23))       # Mağaza 1-23
product_ids = list(range(1, 46))    # Ürün 1-46

print("Makine simülasyonu başlatıldı...")

while True:
    store_id = random.choice(store_ids)
    product_id = random.choice(product_ids)
    quantity = random.randint(1, 50)

    # Veri formatı: store_id,product_id,quantity
    data = f"{store_id},{product_id},{quantity}\n"
    ser.write(data.encode('utf-8'))
    print(f"Tarih: {time.strftime("%c")} Gönderildi: {f"Store_ID = {store_id}, Product_ID = {product_id}, Miktar = {quantity}\n"}")

    time.sleep(random.randint(1, 60))  # 1-60 saniye arası bekle
