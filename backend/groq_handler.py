import os
from groq import Groq
import json
import re

from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

def validate_user_query(user_input):
    """LLM determines if requested data exists before querying the database."""
    prompt = f"""
    You are an AI assistant with knowledge of a structured employee database. Your task is to validate user queries before generating SQL queries. 
    The database contains the following tables:
    
    1. employee_details (employee_id, first_name, last_name, email, phone)
    2. employee_work (work_id, employee_id, role, department, office_location, projects, performance_summary)
    
    The user has asked: "{user_input}"
    
    - If the requested information (e.g., family details) does not exist in the database, return: "Data not available"
    - If the user provides only a partial name (e.g., "Mahesh" instead of "Mahesh Kumar"), return: "Provide full employee name"
    - If the query is valid, return: "valid"
    
    Ensure the response is concise and directly answers whether the query can proceed or needs clarification.
    """
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=GROQ_MODEL,
    )
    
    return response.choices[0].message.content.strip()

def generate_sql_query(user_input):
    """Uses Groq LLM to generate an optimized SQLite query from user input."""
    
    prompt = f"""
    You are an expert SQL assistant. Convert the following user request into a **valid SQLite query**.
    
    - The database contains:
      1. employee_details (employee_id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, email TEXT, phone TEXT)
      2. employee_work (work_id INTEGER PRIMARY KEY, employee_id INTEGER, role TEXT, department TEXT, office_location TEXT, projects TEXT, performance_summary TEXT)
    
    - Strictly follow these rules:
      1. **Only return JSON output. No extra text.**
      2. **Use proper SQL syntax for SQLite.**
      3. **Ensure the query is efficient.**
      4. **Do not include NULL values in the response.**
      5. **If an employee name is provided, match `first_name` and `last_name`.**
      6. **If the name is incomplete, return: {{ "error": "Provide full employee name" }}**
    
    User request: "{user_input}"
    
    **Expected output format (JSON only):**
    {{
      "sql_query": "SELECT ... FROM employee_details JOIN employee_work ... LIMIT 1"
    }}
    """

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=GROQ_MODEL,
    )

    raw_response = response.choices[0].message.content.strip()
    cleaned_response = re.sub(r"```json|```", "", raw_response).strip()

    try:
        json_response = json.loads(cleaned_response)
        if "sql_query" in json_response:
            return json_response["sql_query"]
        else:
            return None  
    except json.JSONDecodeError as e:
        print(f"JSON Parsing Error: {e}")
        return None




def generate_summary(data):
    """LLM generates a professional summary from the retrieved data."""
    prompt = f"""
    You are an expert in summarizing structured employee data. Ensure response remains **strictly relevant** to the given data. Answer only in English. Do NOT add unnecessary explanations or filler content Given the following extracted information, generate a clear, informative, and professional summary:
    
    {data}
    
    Ensure the summary is well-structured and provides meaningful insights.
    """
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=GROQ_MODEL,
    )
    
    return response.choices[0].message.content

def extract_json_response(response):
    response_content = response.choices[0].message.content.strip()

    # Check if the response starts with a JSON block
    if response_content.startswith('```json'):
        # Extract the JSON content inside the block
        try:
            json_start = response_content.index('```json') + len('```json')
            json_end = response_content.index('```', json_start)
            json_response = response_content[json_start:json_end].strip()

            return json.loads(json_response)
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error parsing JSON: {e}")
            return None
    else:
        print("Response format not recognized.")
        return None


def should_query_db(user_input, chat_memory):
    """
    Determines whether to use cached history or generate a new SQL query based on the user's question.
    """
    history_context = "\n".join([f"- {q}: {a}" for q, a in chat_memory.items()])
    
    prompt = f"""
    You are a memory-aware assistant designed to determine whether the user's new question can be answered using previous conversation history.

    **User's New Question:**
    "{user_input}"

    **Previous Conversation History:**
    {history_context}

    **Instructions:**
    - If the new question can be answered using information from past responses, return ONLY the relevant portion of the previous answer that directly addresses the user's current question.
    - If the new question requires new information, return:
      ```json
      {{"use_cache": false}}
      ```

    **Response Format:**
    - If using cached information:
      ```json
      {{"use_cache": true, "cached_response": "<RELEVANT_ANSWER>"}}
      ```
    - If new data is needed:
      ```json
      {{"use_cache": false}}
      ```

    Respond ONLY with the JSON output. Do not add any additional explanations or context.
    """

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=GROQ_MODEL,
    )

    try:
        return extract_json_response(response)
    except json.JSONDecodeError:
        return {"use_cache": False}  # Default to querying DB if parsing fails
