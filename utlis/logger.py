import streamlit as st
from datetime import datetime


class AppLogger:
    def __init__(self):
        if "logs" not in st.session_state:
            st.session_state["logs"] = []

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}"

        # Ensure exists
        if "logs" not in st.session_state:
            st.session_state["logs"] = []

        st.session_state["logs"].append(formatted)

        print(formatted)

    def clear(self):
        st.session_state["logs"] = []

    def get_logs(self):
        return st.session_state.get("logs", [])
