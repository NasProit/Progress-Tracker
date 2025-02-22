import streamlit as st
import hashlib

class Auth:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, username, password, role="student"):
        user = self.data_manager.get_user(username)
        if user and user["password"] == self.hash_password(password):
            if role == "admin" and user["role"] != "admin":
                return False
            if role == "student" and user["role"] == "admin":
                return False
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = user["role"]
            return True
        return False

    def register(self, username, password):
        if self.data_manager.get_user(username):
            return False
        self.data_manager.save_user(username, self.hash_password(password), "student")
        return True

    def logout(self):
        for key in ["logged_in", "username", "role", "authentication_status"]:
            if key in st.session_state:
                del st.session_state[key]