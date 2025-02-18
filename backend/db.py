import sqlite3

def get_db_connection():
    """Establish SQLite database connection."""
    conn = sqlite3.connect("employee_data.db")  # SQLite database file
    conn.row_factory = sqlite3.Row  # Allows dictionary-like access to row data
    return conn
