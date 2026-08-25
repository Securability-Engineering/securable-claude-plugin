def cleanup(path):
    try:
        path.unlink()
    except:
        pass


def close(conn):
    try:
        conn.close()
    except Exception:
        pass
