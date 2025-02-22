import streamlit as st
from auth import Auth
from data_manager import DataManager
from visualization import create_progress_chart, create_average_progress_chart
from styles import apply_custom_styles

# Initialize
data_manager = DataManager()
auth = Auth(data_manager)
apply_custom_styles()

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["role"] = None

# Main title
st.title("Student Progress Tracker")

# Authentication section
if not st.session_state["logged_in"]:
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if auth.login(username, password):
                st.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        st.subheader("Register")
        username = st.text_input("Username", key="register_username")
        password = st.text_input("Password", type="password", key="register_password")
        if st.button("Register"):
            if auth.register(username, password):
                st.success("Registration successful! Please login.")
            else:
                st.error("Username already exists")

else:
    # Logout button
    col1, col2 = st.columns([6,1])
    with col2:
        if st.button("Logout"):
            auth.logout()
            st.experimental_rerun()
    
    with col1:
        st.write(f"Welcome, {st.session_state['username']}!")

    # Admin dashboard
    if st.session_state["role"] == "admin":
        st.subheader("Admin Dashboard")
        
        progress_data = data_manager.get_all_progress()
        
        if progress_data:
            st.plotly_chart(create_progress_chart(progress_data))
            st.plotly_chart(create_average_progress_chart(progress_data))
            
            # Detailed progress table
            st.subheader("Detailed Progress")
            for student, courses in progress_data.items():
                st.write(f"Student: {student}")
                for course, data in courses.items():
                    st.write(f"Course: {course}, Progress: {data['progress']}%")
                st.divider()
        else:
            st.info("No progress data available yet")

    # Student interface
    else:
        st.subheader("My Progress")
        
        # Course progress update
        course = st.selectbox(
            "Select Course",
            ["Mathematics", "Science", "History", "English"]
        )
        
        progress = st.slider(
            "Update Progress",
            0, 100,
            value=int(data_manager.get_student_progress(st.session_state["username"]).get(course, {}).get("progress", 0))
        )
        
        if st.button("Update Progress"):
            data_manager.save_progress(st.session_state["username"], course, progress)
            st.success("Progress updated successfully!")

        # Display current progress
        st.subheader("Current Progress")
        student_progress = data_manager.get_student_progress(st.session_state["username"])
        
        if student_progress:
            for course, data in student_progress.items():
                st.write(f"{course}: {data['progress']}%")
                st.progress(data['progress'] / 100)
        else:
            st.info("No progress recorded yet")
