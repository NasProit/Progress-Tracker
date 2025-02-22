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
    st.session_state["current_page"] = "login"

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

def register_callback():
    username = st.session_state.get("register_username", "")
    password = st.session_state.get("register_password", "")

    if username and password:
        if auth.register(username, password):
            st.session_state["register_status"] = "success"
            st.session_state["current_page"] = "login"
            st.rerun()
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
    # Navigation buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Login Page", use_container_width=True, 
                    type="primary" if st.session_state["current_page"] == "login" else "secondary"):
            st.session_state["current_page"] = "login"
            st.rerun()
    with col2:
        if st.button("Register Page", use_container_width=True,
                    type="primary" if st.session_state["current_page"] == "register" else "secondary"):
            st.session_state["current_page"] = "register"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state["current_page"] == "login":
        st.markdown("""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px;'>
                <h3 style='text-align: center; color: #1f77b4;'>Login</h3>
            </div>
            """, unsafe_allow_html=True)

        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        role = st.selectbox("Role", ["student", "admin"], key="login_role")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔐 Login", key="login_button", use_container_width=True):
            login_callback()

        # Admin credentials hint
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center; color: #666;'>
                <small>Admin Login: MdNasir / Password: 125Nasir</small>
            </div>
            """, unsafe_allow_html=True)

    else:  # Register page
        st.markdown("""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px;'>
                <h3 style='text-align: center; color: #1f77b4;'>Register (Students Only)</h3>
            </div>
            """, unsafe_allow_html=True)

        username = st.text_input("Username", key="register_username")
        password = st.text_input("Password", type="password", key="register_password")
        password_confirm = st.text_input("Confirm Password", type="password", key="register_password_confirm")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📝 Register", key="register_button", use_container_width=True):
            if password != password_confirm:
                st.error("Passwords do not match!")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long!")
            else:
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

            # Topic Management
            st.markdown("### Topic Management")

            # Add Topic
            new_topic = st.text_input("Add New Topic")
            if new_topic and st.button("Add Topic"):
                if data_manager.add_topic(new_topic):
                    st.success(f"Topic '{new_topic}' added successfully!")
                    st.rerun()
                else:
                    st.error("Topic already exists")

            # Add Subtopic
            topics = data_manager.get_topics()
            if topics:
                selected_topic = st.selectbox("Select Topic for Subtopic", list(topics.keys()))
                new_subtopic = st.text_input("Add New Subtopic")
                if new_subtopic and st.button("Add Subtopic"):
                    if data_manager.add_subtopic(selected_topic, new_subtopic):
                        st.success(f"Subtopic '{new_subtopic}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Subtopic already exists")

            # Remove Topic/Subtopic
            st.markdown("### Remove Topics/Subtopics")
            remove_topic = st.selectbox("Select Topic to Remove", [""] + list(topics.keys()))
            if remove_topic:
                if st.button(f"Remove Topic: {remove_topic}"):
                    if data_manager.remove_topic(remove_topic):
                        st.success(f"Topic '{remove_topic}' removed successfully!")
                        st.rerun()
                    else:
                        st.error("Error removing topic")

                subtopics = topics.get(remove_topic, [])
                if subtopics:
                    remove_subtopic = st.selectbox("Select Subtopic to Remove", [""] + subtopics)
                    if remove_subtopic and st.button(f"Remove Subtopic: {remove_subtopic}"):
                        if data_manager.remove_subtopic(remove_topic, remove_subtopic):
                            st.success(f"Subtopic '{remove_subtopic}' removed successfully!")
                            st.rerun()
                        else:
                            st.error("Error removing subtopic")

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
            st.warning("No topics available. Please wait for the admin to add the curriculum.")
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