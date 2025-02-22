import streamlit as st
import pandas as pd
from auth import Auth
from data_manager import DataManager
from visualization import create_progress_chart, create_average_progress_chart
from styles import apply_custom_styles
import os

# Initialize
data_manager = DataManager()
auth = Auth(data_manager)
apply_custom_styles()

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["role"] = None
    st.session_state["authentication_status"] = None

def login_callback():
    username = st.session_state.get("login_username", "")
    password = st.session_state.get("login_password", "")
    role = st.session_state.get("login_role", "student")

    if username and password:
        if auth.login(username, password, role):
            st.session_state["logged_in"] = True
            st.session_state["role"] = role
            st.session_state["authentication_status"] = True
            st.rerun()
        else:
            st.session_state["authentication_status"] = False

def register_callback():
    username = st.session_state.get("register_username", "")
    password = st.session_state.get("register_password", "")

    if username and password:
        if auth.register(username, password):
            st.session_state["register_status"] = "success"
        else:
            st.session_state["register_status"] = "error"

# Display logo if exists
if os.path.exists("assets/logo.png"):
    st.image("assets/logo.png", width=200)

# Main title with styling
st.markdown("""
    <h1 style='text-align: center; color: #1f77b4;'>
        📊 Data Science Progress Tracker
    </h1>
    """, unsafe_allow_html=True)

# Authentication section
if not st.session_state["logged_in"]:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px;'>
                <h3 style='text-align: center; color: #1f77b4;'>Login</h3>
            </div>
            """, unsafe_allow_html=True)

        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        role = st.selectbox("Role", ["student", "admin"], key="login_role")

        if st.button("Login", key="login_button", use_container_width=True):
            login_callback()

        if st.session_state.get("authentication_status") is False:
            st.error("Invalid username/password or role")

    with col2:
        st.markdown("""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px;'>
                <h3 style='text-align: center; color: #1f77b4;'>Register (Students Only)</h3>
            </div>
            """, unsafe_allow_html=True)

        username = st.text_input("Username", key="register_username")
        password = st.text_input("Password", type="password", key="register_password")

        if st.button("Register", key="register_button", use_container_width=True):
            register_callback()

        if st.session_state.get("register_status") == "success":
            st.success("Registration successful! Please login.")
        elif st.session_state.get("register_status") == "error":
            st.error("Username already exists")

else:
    # Logout button in sidebar
    with st.sidebar:
        st.write(f"👤 Welcome, {st.session_state['username']}!")
        st.write(f"Role: {st.session_state['role'].capitalize()}")
        if st.button("Logout", use_container_width=True):
            auth.logout()
            st.rerun()

    # Admin dashboard
    if st.session_state["role"] == "admin":
        st.markdown("""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                <h2 style='text-align: center; color: #1f77b4;'>Admin Dashboard</h2>
            </div>
            """, unsafe_allow_html=True)

        # Admin Settings
        with st.expander("⚙️ Admin Settings"):
            # Logo Upload
            logo_file = st.file_uploader("Upload Logo (PNG format)", type=['png'])
            if logo_file and st.button("Save Logo"):
                if data_manager.save_logo(logo_file):
                    st.success("Logo updated successfully!")
                    st.rerun()
                else:
                    st.error("Error saving logo")

            # CSV Upload for Topics
            st.markdown("### Upload Topics CSV")
            st.markdown("""
                CSV should have columns: 'Topic', 'Subtopic'
                Example:
                ```
                Topic,Subtopic
                Python Basics,Variables and Data Types
                Python Basics,Control Flow
                Data Analysis,Pandas Basics
                ```
            """)
            csv_file = st.file_uploader("Upload Topics CSV", type=['csv'])
            if csv_file and st.button("Update Topics"):
                if data_manager.save_topics_from_csv(csv_file):
                    st.success("Topics updated successfully!")
                else:
                    st.error("Error updating topics")

        # Progress Tracking
        progress_data = data_manager.get_all_progress()
        if progress_data:
            tab1, tab2, tab3 = st.tabs(["📊 Progress Chart", "📈 Average Progress", "📋 Detailed View"])

            with tab1:
                st.plotly_chart(create_progress_chart(progress_data), use_container_width=True)

            with tab2:
                st.plotly_chart(create_average_progress_chart(progress_data), use_container_width=True)

            with tab3:
                for student, topics in progress_data.items():
                    with st.expander(f"Student: {student}"):
                        for topic, subtopics in topics.items():
                            st.write(f"**{topic}**")
                            for subtopic, data in subtopics.items():
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.progress(data['progress'] / 100)
                                with col2:
                                    st.write(f"{data['progress']}%")
                                st.write(f"Subtopic: {subtopic}")
                            st.divider()
        else:
            st.info("No progress data available yet")

    # Student interface
    else:
        st.markdown("""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                <h2 style='text-align: center; color: #1f77b4;'>My Learning Progress</h2>
            </div>
            """, unsafe_allow_html=True)

        # Topic and Subtopic selection
        topics = data_manager.get_topics()
        if not topics:
            st.warning("No topics available. Please wait for the admin to upload the curriculum.")
        else:
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                topic = st.selectbox("📚 Select Topic", list(topics.keys()))

            with col2:
                subtopic = st.selectbox("📖 Select Subtopic", topics[topic])

            with col3:
                current_progress = data_manager.get_student_progress(
                    st.session_state["username"]
                ).get(topic, {}).get(subtopic, {}).get("progress", 0)
                progress = st.slider(
                    "Progress",
                    0, 100,
                    value=int(current_progress)
                )

            if st.button("📝 Update Progress", use_container_width=True):
                data_manager.save_progress(st.session_state["username"], topic, subtopic, progress)
                st.success("Progress updated successfully!")

            # Display current progress
            st.markdown("""
                <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-top: 20px;'>
                    <h3 style='text-align: center; color: #1f77b4;'>Current Progress</h3>
                </div>
                """, unsafe_allow_html=True)

            student_progress = data_manager.get_student_progress(st.session_state["username"])
            if student_progress:
                for topic, subtopics in student_progress.items():
                    st.write(f"**{topic}**")
                    for subtopic, data in subtopics.items():
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.progress(data['progress'] / 100)
                            st.write(f"Subtopic: {subtopic}")
                        with col2:
                            st.write(f"{data['progress']}%")
                    st.divider()
            else:
                st.info("No progress recorded yet. Start by updating your first topic!")