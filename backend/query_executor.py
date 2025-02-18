from backend.db import get_db_connection

def execute_query(sql_query):
    """Execute the SQL query and return results."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(sql_query)
        results = cur.fetchall()
        col_names = [desc[0] for desc in cur.description] if cur.description else []
        
        return [dict(zip(col_names, row)) for row in results] if col_names else []
    
    except Exception as e:
        return {"error": str(e)}
    
    finally:
        cur.close()
        conn.close()
