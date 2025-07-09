import cx_Oracle
from flask import session

def get_connection():
    if 'user' not in session or 'password' not in session:
        raise Exception("Oturum bilgileri eksik")

    # "FREE" adlı TNS alias ile bağlanıyoruz
    dsn = cx_Oracle.makedsn("localhost", 1521, service_name="FREE")
    conn = cx_Oracle.connect(user=session['user'], password=session['password'], dsn=dsn)
    return conn
