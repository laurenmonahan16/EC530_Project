import sqlite3

def get_connection(db_path: str) -> sqlite3.Connection:
    """
    create and return a connection to the sql database
    """
    conn = sqlite3.connect(db_path)
    return conn


def close_connection(conn: sqlite3.Connection) -> None:
    """
    close the connection to the sql database
    """
    conn.close()