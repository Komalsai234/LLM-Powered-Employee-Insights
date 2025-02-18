from backend.db import get_db_connection

def execute_query(sql_query):
    """Execute the SQL query and return results."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(sql_query)
        results = cur.fetchall()
        col_names = [desc[0] for desc in cur.description]
        return [dict(zip(col_names, row)) for row in results]
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()
