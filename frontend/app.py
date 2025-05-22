# app.py
import streamlit as st
import requests
from typing import List, Dict

st.set_page_config(page_title="TravelMate AI", page_icon="🎒", layout="wide")

API_URL = "http://localhost:8000"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_id" not in st.session_state:
    st.session_state.user_id = ""

st.sidebar.text_input(
    "Enter User ID",
    key="user_id",
    placeholder="Enter your User ID here",
    help="Enter your User ID for your chat session",
)

if not st.session_state.user_id:
    st.warning("Please enter a User ID in the sidebar to start chatting.")
    st.stop()

st.title("🎒 TravelMate AI - Your Smart Travel Guide")

def send_message(user_query: str) -> Dict:
    payload = {
        "user_id": st.session_state.user_id,
        "user_query": user_query
    }
    try:
        res = requests.post(f"{API_URL}/chat", json=payload)
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        st.error(f"Failed to connect to backend: {e}")
        return {}

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            if isinstance(message["content"], dict):
                summary = message["content"].get("summary")
                table = message["content"].get("table")
                if summary:
                    st.markdown("### ✨ Summary")
                    st.markdown(summary, unsafe_allow_html=True)
                if table:
                    st.markdown("### 📋 Tourist Information")
                    st.markdown(table, unsafe_allow_html=True)
            else:
                st.markdown(message["content"], unsafe_allow_html=True)
        else:
            st.write(message["content"])

if prompt := st.chat_input("Where do you want to explore today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    response = send_message(prompt)
    if response:
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            if summary := response.get("summary"):
                st.markdown("### ✨ Summary")
                st.markdown(summary)
            if table := response.get("table"):
                st.markdown("### 📋 Tourist Information")
                st.markdown(table, unsafe_allow_html=True)

if st.sidebar.button("🧹 Clear Chat History"):
    st.session_state.messages = []
    st.empty()
