import src.config as c
import sqlite3
from sqlite3 import Error, Connection
import dataclasses


def submit(conn: sqlite3.Connection, query: str) -> int:
    # If you're curious about the status of the execute
    # you can check the return value -- it will indicate
    # the current row the cursor is at for the next 
    # insert - 1 (total number of rows in table)
    
    run = conn.cursor().execute(query)
    conn.commit()
    return run.rowcount


# def schema(conn: sqlite3.Connection, job_name: str):
#     # Define schema
    
#     # Create generic jobs table
    
    
#     # Create query results table per job
#     fields = []
#     for i in [f.name for f in dataclasses.fields(QueryReport)]:
#         if i != "uid":
#             fields.append(f"[{i}] STRING")
#         else:
#             fields.append(f"[{i}] STRING PRIMARY KEY")
            
#     q = f"""
#         CREATE TABLE IF NOT EXISTS {job_name}
#         (
#             {','.join(map(str,fields))}
#         )
#         """
#     submit(conn=conn, query=q)


def establish(file=c.DB_FILE, job_name=c.JOB_NAME) -> Connection:
    conn = None

    try:
        conn = sqlite3.connect(file)
    except Error as e:
        print(e)
        
    return conn
