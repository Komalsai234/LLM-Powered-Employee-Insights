from fastapi import FastAPI, Query
from backend.groq_handler import should_query_db, generate_sql_query, generate_summary
from backend.query_executor import execute_query

app = FastAPI()

chat_memory = {}

MODIFICATION_KEYWORDS = {"DELETE", "UPDATE", "INSERT", "DROP", "ALTER"}

@app.get("/query/")
def query(user_input: str = Query(..., description="User's natural language query")):
    global chat_memory

    if any(keyword in user_input.upper() for keyword in MODIFICATION_KEYWORDS):
        return {"error": "Modification of data is not allowed."}

    # Step 1: Check if we can reuse previous data
    reuse_decision = should_query_db(user_input, chat_memory)
    
    if reuse_decision["use_cache"]:
        return {"summary": reuse_decision["cached_response"]}

    # Step 2: Generate SQL Query if needed
    sql_query = generate_sql_query(user_input)
    if not sql_query:
        return {"error": "Failed to generate SQL query."}

    # Step 3: Execute SQL Query
    db_results = execute_query(sql_query)
    if not db_results:
        return {"error": "No relevant data found."}

    # Step 4: Generate Summary
    summary = generate_summary(db_results)

    # Step 5: Store response in memory
    chat_memory[user_input] = summary
    print(chat_memory)
    return {"summary": summary}
