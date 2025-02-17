import streamlit as st
import requests

API_URL = "http://localhost:8000/query/"

st.set_page_config(page_title="Employee Chatbot", layout="wide", page_icon="🤖")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

MODIFICATION_KEYWORDS = {"DELETE", "UPDATE", "INSERT", "DROP", "ALTER"}

st.title("👨‍💼 Employee Info Chatbot")

col1, col2 = st.columns([9, 1])
with col2:
    if st.button("🗑️ Delete Chat", key="clear_chat", help="Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun() 


for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.write(chat["message"])

user_input = st.chat_input("🔎 Ask about an employee...")

if user_input:
    if any(keyword in user_input.upper() for keyword in MODIFICATION_KEYWORDS):
        with st.chat_message("assistant"):
            st.error("❌ Modification of data is not allowed.")
        st.session_state.chat_history.append({"role": "assistant", "message": "❌ Modification of data is not allowed."})
    else:
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.chat_history.append({"role": "user", "message": user_input})
        cached_response = next((chat["message"] for chat in st.session_state.chat_history if chat["role"] == "assistant" and chat["message"].startswith("📄")), None)

        if cached_response:
            with st.chat_message("assistant"):
                st.write("✅ Using cached response")
                st.write(cached_response)
            st.session_state.chat_history.append({"role": "assistant", "message": cached_response})
        else:
            with st.spinner("⏳ Fetching details..."):
                response = requests.get(API_URL, params={"user_input": user_input})

            if response.status_code == 200:
                result = response.json()
                if "error" in result:
                    bot_response = f"❌ {result['error']}"
                else:
                    bot_response = f"{result['summary']}"

                with st.chat_message("assistant"):
                    st.write(bot_response)
                st.session_state.chat_history.append({"role": "assistant", "message": bot_response})
            else:
                error_message = "⚠️ Error fetching response from the backend."
                with st.chat_message("assistant"):
                    st.error(error_message)
                st.session_state.chat_history.append({"role": "assistant", "message": error_message})

