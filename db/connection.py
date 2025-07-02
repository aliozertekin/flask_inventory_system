import cx_Oracle

dsn = cx_Oracle.makedsn("localhost", 1521, service_name="FREE")
conn = cx_Oracle.connect("system", "admin", dsn=dsn)