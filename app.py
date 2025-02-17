import streamlit as st
import requests
import json

API_URL = "http://localhost:8000/query/"

st.set_page_config(page_title="Employee Info Retrieval", layout="wide")

st.markdown("""
    <style>
    .stTextInput>div>div>input { font-size: 18px; }
    .stButton>button { font-size: 18px; padding: 10px 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 Employee Information Retrieval")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

MODIFICATION_KEYWORDS = {"DELETE", "UPDATE", "INSERT", "DROP", "ALTER"}

user_input = st.text_input("Ask a question about an employee:", "")

if st.button("Search"):
    if user_input:
        if any(keyword in user_input.upper() for keyword in MODIFICATION_KEYWORDS):
            st.error("Modification of data is not allowed.")
        elif user_input in st.session_state.chat_history:
            st.subheader("📄 Summary (Cached)")
            st.write(st.session_state.chat_history[user_input])
        else:
            with st.spinner("Processing..."):
                response = requests.get(API_URL, params={"user_input": user_input})
                if response.status_code == 200:
                    result = response.json()
                    
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        summary = result["summary"]
                        st.subheader("📄 Summary")
                        st.write(summary)
                        st.session_state.chat_history[user_input] = summary
                else:
                    st.error("Error fetching response from the backend.")
    else:
        st.warning("Please enter a query.")
