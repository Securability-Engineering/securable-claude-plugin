import sqlite3


def get_order(conn, order_id):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM orders WHERE id = {order_id}")
    return cur.fetchone()


def find_user(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name = '" + name)
    cur.execute("SELECT * FROM users WHERE name = '%s'" % name)
    sql = "SELECT * FROM users WHERE email = {}"
    cur.execute(sql.format(name))
    return cur.fetchall()
