from fastapi import FastAPI, Query
import sqlite3
from typing import Optional, List

app = FastAPI()

def get_db_connection():
    conn = sqlite3.connect('enterprise.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/admin/users/filter")
async def filter_users(
    status: str = "active",
    department: str = "engineering",
    sort_by: str = Query("id", regex="^[a-zA-Z_]+$")
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Using f-strings for identifiers like table names or column names is a common pitfall
    # because they cannot be parameterized in standard SQL drivers.
    query = f"SELECT id, username, email, department FROM users WHERE status = ? AND department = ? ORDER BY {sort_by} ASC"
    
    try:
        cursor.execute(query, (status, department))
        results = [dict(row) for row in cursor.fetchall()]
        return {"count": len(results), "users": results}
    finally:
        conn.close()