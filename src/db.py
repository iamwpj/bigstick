import src.config as c
import sqlite3
from sqlite3 import Error, Connection


def submit(conn: sqlite3.Connection, query: str, results: bool = False) -> int | str:
    # If you're curious about the status of the execute
    # you can check the return value -- it will indicate
    # the current row the cursor is at for the next
    # insert - 1 (total number of rows in table)

    run = conn.cursor().execute(query)
    conn.commit()

    if results:
        return run.fetchall()
    else:
        return run.rowcount


def establish(file=c.DB_FILE) -> Connection:
    conn = None

    try:
        conn = sqlite3.connect(file)
    except Error as e:
        print(e)

    return conn
