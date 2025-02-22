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
        📊 Proitbridge Milestone Tracker
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
                <small>Admin Login: ME / Password: Something</small>
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
        st.markdown("""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                <h3 style='text-align: center; color: #1f77b4;'>Topic Management</h3>
            </div>
            """, unsafe_allow_html=True)

        # Topics section
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 📚 Add New Topic")
            new_topic = st.text_input("Topic Name (e.g., Python, SQL, ML)", key="new_topic")
            new_topic_desc = st.text_area("Topic Description (optional)", key="topic_desc", height=100)

            if st.button("➕ Add Topic", use_container_width=True):
                if new_topic:
                    if data_manager.add_topic(new_topic):
                        st.success(f"Topic '{new_topic}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Topic already exists")
                else:
                    st.warning("Please enter a topic name")

        with col2:
            st.markdown("### 📖 Add Subtopics")
            topics = data_manager.get_topics()
            if topics:
                selected_topic = st.selectbox("Select Topic", list(topics.keys()), key="topic_for_subtopic")
                new_subtopic = st.text_input("Subtopic Name", key="new_subtopic")
                subtopic_desc = st.text_area("Subtopic Description (optional)", key="subtopic_desc", height=100)

                if st.button("➕ Add Subtopic", use_container_width=True):
                    if new_subtopic:
                        if data_manager.add_subtopic(selected_topic, new_subtopic):
                            st.success(f"Subtopic '{new_subtopic}' added successfully!")
                            st.rerun()
                        else:
                            st.error("Subtopic already exists")
                    else:
                        st.warning("Please enter a subtopic name")

        # Current Topics and Subtopics Overview
        st.markdown("""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 20px 0;'>
                <h3 style='text-align: center; color: #1f77b4;'>Current Curriculum Structure</h3>
            </div>
            """, unsafe_allow_html=True)

        topics = data_manager.get_topics()
        if topics:
            for topic in topics:
                with st.expander(f"📚 {topic}", expanded=True):
                    st.markdown(f"**Topic: {topic}**")

                    # Display subtopics in columns
                    subtopics = topics[topic]
                    if subtopics:
                        cols = st.columns(3)
                        for idx, subtopic in enumerate(subtopics):
                            with cols[idx % 3]:
                                st.markdown(f"- {subtopic}")
                                if st.button(f"🗑 Remove", key=f"remove_{topic}_{subtopic}"):
                                    if data_manager.remove_subtopic(topic, subtopic):
                                        st.success(f"Removed subtopic: {subtopic}")
                                        st.rerun()
                    else:
                        st.info("No subtopics added yet")

                    if st.button(f"🗑 Remove Topic: {topic}", key=f"remove_topic_{topic}"):
                        if data_manager.remove_topic(topic):
                            st.success(f"Removed topic: {topic}")
                            st.rerun()
        else:
            st.info("No topics added yet. Start by adding your first topic!")

        # Example Topics Helper
        with st.expander("📋 Example Topics for Data Science"):
            st.markdown("""
            ### Suggested Topics and Subtopics:

            1. **Python Fundamentals**
               - Variables and Data Types
               - Control Flow
               - Functions and Methods
               - Object-Oriented Programming

            2. **SQL & Databases**
               - Basic SQL Queries
               - Joins and Relationships
               - Database Design
               - Query Optimization

            3. **Machine Learning**
               - Supervised Learning
               - Unsupervised Learning
               - Model Evaluation
               - Feature Engineering

            4. **Deep Learning**
               - Neural Networks Basics
               - CNN
               - RNN and LSTM
               - Transfer Learning
            """)

        # Progress Tracking
        progress_data = data_manager.get_all_progress()
        if progress_data:
            st.markdown("""
                <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 20px 0;'>
                    <h3 style='text-align: center; color: #1f77b4;'>Student Progress Dashboard</h3>
                </div>
                """, unsafe_allow_html=True)

            tab1, tab2, tab3 = st.tabs(["📊 Combined Progress", "👤 Individual Progress", "📈 Analytics"])

            with tab1:
                # Combined progress view
                st.markdown("### Overall Progress Chart")
                st.plotly_chart(create_progress_chart(progress_data), use_container_width=True)

                st.markdown("### Average Progress by Student")
                st.plotly_chart(create_average_progress_chart(progress_data), use_container_width=True)

            with tab2:
                # Individual student progress
                st.markdown("### Individual Student Progress")
                for student in progress_data.keys():
                    with st.expander(f"📚 Student: {student}", expanded=False):
                        student_data = {student: progress_data[student]}

                        # Individual progress chart
                        st.plotly_chart(create_progress_chart(student_data), use_container_width=True)

                        # Detailed progress table
                        st.markdown("#### Detailed Progress")
                        for topic, subtopics in progress_data[student].items():
                            st.write(f"**{topic}**")
                            for subtopic, data in subtopics.items():
                                col1, col2, col3 = st.columns([3, 1, 1])
                                with col1:
                                    st.write(f"- {subtopic}")
                                with col2:
                                    st.progress(data['progress'] / 100)
                                with col3:
                                    st.write(f"{data['progress']}%")
                            st.divider()

            with tab3:
                # Analytics view
                st.markdown("### Progress Analytics")

                # Calculate completion statistics
                total_students = len(progress_data)
                topic_completion = {}

                for student, topics in progress_data.items():
                    for topic, subtopics in topics.items():
                        if topic not in topic_completion:
                            topic_completion[topic] = {"total": 0, "count": 0}

                        topic_total = sum(data['progress'] for data in subtopics.values())
                        topic_count = len(subtopics)

                        topic_completion[topic]["total"] += topic_total
                        topic_completion[topic]["count"] += topic_count

                # Display topic-wise completion
                st.markdown("#### Topic-wise Completion Rate")
                for topic, data in topic_completion.items():
                    avg_completion = data["total"] / (data["count"] * total_students) if data["count"] > 0 else 0
                    st.write(f"**{topic}**")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.progress(avg_completion / 100)
                    with col2:
                        st.write(f"{avg_completion:.1f}%")
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
