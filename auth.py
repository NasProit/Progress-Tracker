import streamlit as st
import hashlib

class Auth:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(str(password).encode()).hexdigest()

    def login(self, username, password, role="student"):
        """
        Authenticate user with username, password and role
        """
        if not username or not password:
            return False

        user = self.data_manager.get_user(username)
        if not user:
            st.error(f"User {username} not found")
            return False

        hashed_input = self.hash_password(password)
        stored_hash = user["password"]

        # Debug information
        print(f"Input Password: {password}")
        print(f"Hashed Input: {hashed_input}")
        print(f"Stored Hash: {stored_hash}")

        if hashed_input == stored_hash:
            if role == "admin" and user["role"] != "admin":
                st.error("You don't have admin privileges")
                return False
            if role == "student" and user["role"] == "admin":
                st.error("Please use admin login for admin account")
                return False

            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = user["role"]
            st.session_state["authentication_status"] = True
            return True

        st.error("Invalid password")
        return False

    def register(self, username, password):
        """Register a new student user"""
        if not username or not password:
            return False

        if self.data_manager.get_user(username):
            return False

        self.data_manager.save_user(username, self.hash_password(password), "student")
        return True

    def logout(self):
        """Clear all authentication related session state"""
        keys_to_clear = ["logged_in", "username", "role", "authentication_status"]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]