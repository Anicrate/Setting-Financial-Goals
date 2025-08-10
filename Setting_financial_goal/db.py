import oracledb as cx_Oracle

def get_connection():
    conn = cx_Oracle.connect(
        user="system",
        password="dbms",
        dsn="localhost/XE"
    )
    return conn
