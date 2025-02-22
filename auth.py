import streamlit as st
import hashlib

class Auth:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, username, password):
        user = self.data_manager.get_user(username)
        if user and user["password"] == self.hash_password(password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = user["role"]
            return True
        return False

    def register(self, username, password):
        if self.data_manager.get_user(username):
            return False
        self.data_manager.save_user(username, self.hash_password(password))
        return True

    def logout(self):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["role"] = None
