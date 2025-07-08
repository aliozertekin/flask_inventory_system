import os, smtplib, secrets
from email.message import EmailMessage

def get_base_dir():
    # modules klasörünün bir üst dizini: flask_inventory_system/flask_inventory_system
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_font_path(font_name='DejaVuSans.ttf'):
    base_dir = get_base_dir()
    # Mutlak yol oluşturuyoruz
    font_path = os.path.join(base_dir, 'static', 'fonts', font_name)
    return font_path

def send_invoice_email(to_email, subject, body, pdf_buffer, filename="invoice.pdf"):
    # Gönderen bilgileri (çevresel değişkenlere almak daha güvenli olur)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    from_email = "seninmailin@gmail.com"
    password = "uygulama_sifresi"  # Gmail kullanıyorsan uygulama şifresi kullanmalısın

    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        msg.set_content(body)

        # PDF'yi ekle
        pdf_buffer.seek(0)
        msg.add_attachment(
            pdf_buffer.read(),
            maintype='application',
            subtype='pdf',
            filename=filename
        )

        # SMTP ile gönder
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(from_email, password)
            smtp.send_message(msg)

        print("E-posta başarıyla gönderildi.")
        return True

    except Exception as e:
        print(f"E-posta gönderim hatası: {e}")
        return False

def get_secret():
    return secrets.token_hex(16) # Gizli anahtar oluştur.