import sqlite3

def create_tables():
    conn = sqlite3.connect("employee_data.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS employee_details (
            employee_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS employee_work (
            work_id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            role TEXT,
            department TEXT,
            office_location TEXT,
            projects TEXT,
            performance_summary TEXT,
            FOREIGN KEY(employee_id) REFERENCES employee_details(employee_id)
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("SQLite database setup completed.")
