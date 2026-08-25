import sqlite3


def get_order(conn, order_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    return cur.fetchone()
