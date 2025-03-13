import streamlit as st
import json
import os
import datetime
import data_manager
import auth
import plotly.express as px
import pandas as pd

# Constants
USER_DATA_FILE = "user_data.json"
APP_TITLE = "📊 ProITbridge Milestone Tracker"
APP_THEME_COLOR = "#1f77b4"

# Initialize Data
manager = data_manager.DataManager()
auth_instance = auth.Auth(manager)

# Helper Functions
def load_json_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                data = f.read().strip()
                return json.loads(data) if data else {}
        except json.JSONDecodeError:
            return {}
    return {}

def save_json_data(data, file_path):
    temp_file = file_path + ".tmp"
    with open(temp_file, "w") as f:
        json.dump(data, f, indent=4)
    os.replace(temp_file, file_path)

# Session State Setup
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False,
        "username": None,
        "role": None,
        "current_page": "login",
        "selected_student": None
    })

# UI Components
def render_header():
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=700)
    st.markdown(f"<h1 style='text-align: center; color: {APP_THEME_COLOR};'>{APP_TITLE}</h1>", unsafe_allow_html=True)

def render_auth_pages():
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

    if st.session_state["current_page"] == "login":
        render_login_form()
    else:
        render_register_form()

def render_login_form():
    st.text_input("Username", key="login_username")
    st.text_input("Password", type="password", key="login_password")
    role = st.selectbox("Role", ["student", "admin"], key="login_role")

    if st.button("🔐 Login", key="login_button"):
        username = st.session_state.get("login_username", "")
        password = st.session_state.get("login_password", "")
        role = st.session_state.get("login_role", "student")
        if username and password:
            st.info(f"Attempting login for {username}...")
            success = auth_instance.login(username, password, role)
            if success:
                st.success(f"Login successful as {role}")
                st.session_state.update({
                    "logged_in": True,
                    "username": username,
                    "role": role,
                    "authentication_status": True
                })
                st.rerun()
            else:
                st.error("Login failed - please check your credentials")

def render_register_form():
    st.text_input("Username", key="register_username")
    st.text_input("Password", type="password", key="register_password")
    st.text_input("Confirm Password", type="password", key="register_password_confirm")

    if st.button("📝 Register", key="register_button"):
        if st.session_state["register_password"] != st.session_state["register_password_confirm"]:
            st.error("Passwords do not match!")
        else:
            username = st.session_state.get("register_username", "")
            password = st.session_state.get("register_password", "")
            confirm_password = st.session_state.get("register_password_confirm", "")
            if username and password:
                st.info("Processing registration...")
                if auth_instance.register(username, password, confirm_password):
                    st.success(f"Registration successful for {username}")
                    st.session_state["current_page"] = "login"
                    st.rerun()
                else:
                    st.error("Registration failed - please try again")

def render_sidebar(user_data):
    with st.sidebar:
        st.write(f"👤 Welcome, {st.session_state['username']}!")
        st.write(f"Role: {st.session_state['role'].capitalize()}")
        
        # Admin: Student Selection
        if st.session_state["role"] == "admin":
            all_users = [user for user in user_data.keys() if user_data[user].get("career_path") is not None]
            if all_users:
                selected_student = st.selectbox("View Student Progress", 
                                              ["All Students"] + all_users,
                                              index=0)
                st.session_state["selected_student"] = selected_student
            else:
                st.info("No student data available yet.")
        
        if st.button("Logout", use_container_width=True):
            auth_instance.logout()
            st.rerun()

def select_career_path(user_data, current_username):
    st.markdown("## 🎯 Select Your Career Path")
    st.warning("This selection is permanent and cannot be changed later!")
    
    selected_track = st.selectbox("Choose a Track", ["Data Analyst", "Data Scientist"], 
                                index=None, placeholder="Select a Career Path")
    
    if selected_track and st.button("Confirm Career Path Selection", type="primary"):
        user_data[current_username]["career_path"] = selected_track
        save_json_data(user_data, USER_DATA_FILE)
        st.success(f"You have selected {selected_track} as your career path")
        st.rerun()

def render_subtopic_progress(subtopic, subtopic_key, subtopic_data, viewing_user, is_viewing_other):
    col1, col2, col3 = st.columns([3, 1, 2])

    with col1:
        st.markdown(f"**{subtopic}**")

    with col2:
        # Replace the slider with a radio button group
        status_options = ["Not Started", "In Progress", "Completed"]
        
        # Convert numerical completion to status
        current_status = "Not Started"
        completion = subtopic_data.get("completion", 0)
        if completion == 100:
            current_status = "Completed"
        elif completion > 0:
            current_status = "In Progress"
        
        # Add some CSS to fix the alignment
        st.markdown(
            """
            <style>
            div[data-testid="stHorizontalBlock"] div[data-testid="column"] div.row-widget.stRadio > div {
                flex-direction: row;
                align-items: center;
            }
            div[data-testid="stHorizontalBlock"] div[data-testid="column"] div.row-widget.stRadio > div > label {
                padding: 0 10px;
                white-space: nowrap;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        status = st.radio(
            "",
            options=status_options,
            index=status_options.index(current_status),
            key=f"{viewing_user}_{subtopic_key}_status",
            disabled=is_viewing_other,
            horizontal=True
        )
        
        # Convert status back to percentage for compatibility with existing code
        percentage = 0
        if status == "In Progress":
            percentage = 50
        elif status == "Completed":
            percentage = 100

    with col3:
        prev_dates = subtopic_data.get("deadlines", [])
        
        # Date input
        latest_date = None
        if prev_dates:
            try:
                latest_date = datetime.datetime.strptime(prev_dates[-1], "%Y-%m-%d").date()
            except (ValueError, IndexError):
                latest_date = None
                
        current_date = st.date_input("Deadline", 
                                  value=latest_date, 
                                  key=f"date_{viewing_user}_{subtopic_key}",
                                  disabled=is_viewing_other)

        # Update dates if we have a new one and user has permission
        if current_date and not is_viewing_other:
            current_date_str = str(current_date)
            if not prev_dates or prev_dates[-1] != current_date_str:
                prev_dates.append(current_date_str)
                
        # Format and display deadline history
        if prev_dates:
            st.markdown("##### Deadline History:")
            timeline_html = ""
            
            for i, date in enumerate(prev_dates):
                if i < len(prev_dates) - 1:
                    size = max(70 - (len(prev_dates) - i - 1) * 5, 50)
                    timeline_html += f"<span style='text-decoration:line-through;font-size:{size}%;color:gray;'>{date}</span> → "
                else:
                    timeline_html += f"<span style='font-weight:bold;font-size:110%;color:{APP_THEME_COLOR};'>{date}</span>"
            
            st.markdown(timeline_html, unsafe_allow_html=True)
    
    return percentage, prev_dates

def visualize_topic_progress(topic_name, topic_progress):
    st.markdown("#### Topic Progress")
    
    # Convert percentages to status labels for better visualization
    status_mapping = {
        0: "Not Started",
        50: "In Progress",
        100: "Completed"
    }
    
    # Create DataFrame for better visualization
    topic_df = pd.DataFrame({
        'Subtopic': list(topic_progress.keys()),
        'Completion': list(topic_progress.values()),
        'Status': [status_mapping.get(progress, "Unknown") for progress in topic_progress.values()]
    })
    
    fig_topic = px.bar(
        topic_df,
        x='Subtopic',
        y='Completion',
        title=f"{topic_name} Progress",
        color='Status',
        color_discrete_map={
            "Not Started": "#e0e0e0",
            "In Progress": "#ffb74d",
            "Completed": APP_THEME_COLOR
        },
        labels={"Completion": "Completion (%)", "Status": "Status"}
    )
    fig_topic.update_layout(height=300)
    st.plotly_chart(fig_topic, use_container_width=True)

def visualize_phase_progress(phase_name, phase_progress):
    st.markdown(f"### {phase_name} Phase Summary")
    
    # Create DataFrame for visualization
    phase_df = pd.DataFrame({
        'Topic': list(phase_progress.keys()),
        'Completion': list(phase_progress.values())
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart for detailed progress
        fig_phase_bar = px.bar(
            phase_df,
            x='Topic',
            y='Completion',
            title=f"{phase_name} Topics Completion",
            color='Completion',
            color_continuous_scale='Blues',
            text=[f"{v:.1f}%" for v in phase_df['Completion']]
        )
        fig_phase_bar.update_layout(height=350)
        st.plotly_chart(fig_phase_bar, use_container_width=True)
    
    with col2:
        # Pie chart for proportion
        fig_phase_pie = px.pie(
            phase_df,
            values='Completion',
            names='Topic',
            title=f"{phase_name} Topics Distribution"
        )
        fig_phase_pie.update_layout(height=350)
        st.plotly_chart(fig_phase_pie, use_container_width=True)

def visualize_overall_progress(current_track, overall_progress):
    st.markdown("## 📊 Overall Career Progress")
    
    # Create DataFrame for visualization
    overall_df = pd.DataFrame({
        'Phase': list(overall_progress.keys()),
        'Completion': list(overall_progress.values())
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart for detailed progress
        fig_overall_bar = px.bar(
            overall_df,
            x='Phase',
            y='Completion',
            title=f"{current_track} Overall Progress by Phase",
            color='Completion',
            color_continuous_scale='Blues',
            text=[f"{v:.1f}%" for v in overall_df['Completion']]
        )
        fig_overall_bar.update_layout(height=400)
        st.plotly_chart(fig_overall_bar, use_container_width=True)
    
    with col2:
        # Calculate average overall progress
        total_completion = sum(overall_progress.values()) / len(overall_progress)
        
        # Create gauge chart for overall progress
        fig_gauge = px.pie(
            values=[total_completion, 100-total_completion],
            names=["Completed", "Remaining"],
            hole=0.7,
            title=f"Overall Completion: {total_completion:.1f}%"
        )
        fig_gauge.update_layout(
            height=400,
            annotations=[dict(text=f"{total_completion:.1f}%", x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        fig_gauge.update_traces(marker=dict(colors=[APP_THEME_COLOR, '#e0e0e0']))
        st.plotly_chart(fig_gauge, use_container_width=True)

def process_career_path_topics(topics_data, viewing_user, user_data, is_viewing_other, current_track):
    # Track overall progress data for final summary
    overall_progress = {}
    
    # Create tabs for each phase
    phase_tabs = st.tabs(list(topics_data.keys()))
    
    # Process each phase in its own tab
    for tab_idx, phase_name in enumerate(topics_data.keys()):
        with phase_tabs[tab_idx]:
            st.markdown(f"### Phase: {phase_name}")
            
            # Initialize phase progress tracking
            phase_progress = {}
            topics = topics_data[phase_name]
            
            # Create a subtab for each topic in this phase
            topic_tabs = st.tabs(list(topics.keys()))
            
            for topic_idx, topic_name in enumerate(topics.keys()):
                with topic_tabs[topic_idx]:
                    subtopics = topics[topic_name]
                    topic_progress = {}
                    
                    if isinstance(subtopics, list):
                        for subtopic in subtopics:
                            # Create unique key for this subtopic
                            subtopic_key = f"{current_track}_{phase_name}_{topic_name}_{subtopic}"
                            
                            # Get existing data for this subtopic
                            if "progress" not in user_data[viewing_user]:
                                user_data[viewing_user]["progress"] = {}
                            
                            subtopic_data = user_data[viewing_user]["progress"].get(subtopic_key, {"completion": 0, "deadlines": []})
                            
                            # Render the subtopic progress UI
                            percentage, prev_dates = render_subtopic_progress(
                                subtopic, subtopic_key, subtopic_data, viewing_user, is_viewing_other
                            )
                            topic_progress[subtopic] = percentage
                            
                            # Update user data
                            if not is_viewing_other:
                                user_data[viewing_user]["progress"][subtopic_key] = {
                                    "completion": percentage,
                                    "deadlines": prev_dates,
                                    "timestamp": datetime.datetime.now().isoformat()
                                }
                    
                    # Topic progress visualization
                    if topic_progress:
                        visualize_topic_progress(topic_name, topic_progress)
                        # Add to phase progress
                        phase_progress[topic_name] = sum(topic_progress.values()) / len(topic_progress)
            
            # Phase progress visualization after all topics are processed
            if phase_progress:
                visualize_phase_progress(phase_name, phase_progress)
                overall_progress[phase_name] = sum(phase_progress.values()) / len(phase_progress)
    
    return overall_progress

def admin_class_summary(user_data, manager):
    # Get all students with their career path selected
    students = [user for user in user_data.keys() if user_data[user].get("career_path") is not None]
    
    if not students:
        st.info("No student data available yet.")
        return
    
    # Calculate progress data for all students
    student_data = []
    
    for student in students:
        career_path = user_data[student].get("career_path")
        if career_path and "progress" in user_data[student]:
            # Get topics for this career path
            topics_data = manager.get_topics(career_path)
            
            # Calculate progress for each phase
            phase_progress = {}
            
            for phase_name in topics_data.keys():
                phase_topics = topics_data[phase_name]
                all_subtopics_progress = []
                
                for topic_name, subtopics in phase_topics.items():
                    if isinstance(subtopics, list):
                        for subtopic in subtopics:
                            subtopic_key = f"{career_path}_{phase_name}_{topic_name}_{subtopic}"
                            if subtopic_key in user_data[student]["progress"]:
                                all_subtopics_progress.append(
                                    user_data[student]["progress"][subtopic_key].get("completion", 0)
                                )
                
                if all_subtopics_progress:
                    phase_progress[phase_name] = sum(all_subtopics_progress) / len(all_subtopics_progress)
            
            # Calculate overall progress
            if phase_progress:
                overall = sum(phase_progress.values()) / len(phase_progress)
                
                # Add to student data
                student_data.append({
                    "Student": student,
                    "Career Path": career_path,
                    "Overall Progress": overall,
                    **phase_progress  # Add each phase as a separate column
                })
    
    if not student_data:
        st.info("No progress data available yet.")
        return
        
    # Create DataFrame
    student_df = pd.DataFrame(student_data)
    
    # Summary statistics
    st.subheader("Class Progress Summary")
    
    # Career path distribution
    career_counts = student_df["Career Path"].value_counts().reset_index()
    career_counts.columns = ["Career Path", "Count"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Career path distribution pie chart
        fig_career = px.pie(
            career_counts,
            values="Count",
            names="Career Path",
            title="Career Path Distribution"
        )
        st.plotly_chart(fig_career, use_container_width=True)
    
    with col2:
        # Average progress by career path
        avg_by_career = student_df.groupby("Career Path")["Overall Progress"].mean().reset_index()
        
        fig_avg = px.bar(
            avg_by_career,
            x="Career Path",
            y="Overall Progress",
            title="Average Progress by Career Path",
            color="Career Path",
            text=[f"{v:.1f}%" for v in avg_by_career["Overall Progress"]]
        )
        st.plotly_chart(fig_avg, use_container_width=True)
    
    # Progress distribution histogram
    fig_hist = px.histogram(
        student_df,
        x="Overall Progress",
        nbins=10,
        title="Distribution of Student Progress",
        color="Career Path"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

def admin_student_comparison(user_data, manager):
    # Get all students with their career path selected
    students = [user for user in user_data.keys() if user_data[user].get("career_path") is not None]
    
    if not students:
        st.info("No student data available yet.")
        return
    
    # Career paths for filtering
    career_paths = list(set(user_data[student].get("career_path") for student in students if user_data[student].get("career_path")))
    
    # Filters
    selected_career = st.selectbox("Filter by Career Path", ["All"] + career_paths)
    
    # Filtered students
    filtered_students = students
    if selected_career != "All":
        filtered_students = [s for s in students if user_data[s].get("career_path") == selected_career]
    
    # Limit to avoid overcrowding
    max_students = st.slider("Maximum students to display", min_value=5, max_value=20, value=10)
    if len(filtered_students) > max_students:
        filtered_students = filtered_students[:max_students]
    
    if not filtered_students:
        st.info("No students match the selected filters.")
        return
    
    # Create comparison data
    comparison_data = []
    
    for student in filtered_students:
        career_path = user_data[student].get("career_path")
        if career_path and "progress" in user_data[student]:
            # Get topics data for this career path
            topics_data = manager.get_topics(career_path)
            
            # Process each phase
            for phase_name in topics_data.keys():
                phase_topics = topics_data[phase_name]
                all_subtopics_progress = []
                
                for topic_name, subtopics in phase_topics.items():
                    if isinstance(subtopics, list):
                        for subtopic in subtopics:
                            subtopic_key = f"{career_path}_{phase_name}_{topic_name}_{subtopic}"
                            if subtopic_key in user_data[student]["progress"]:
                                all_subtopics_progress.append(
                                    user_data[student]["progress"][subtopic_key].get("completion", 0)
                                )
                
                if all_subtopics_progress:
                    phase_avg = sum(all_subtopics_progress) / len(all_subtopics_progress)
                    comparison_data.append({
                        "Student": student,
                        "Career Path": career_path,
                        "Phase": phase_name,
                        "Progress": phase_avg
                    })
    
    if not comparison_data:
        st.info("No progress data available for the selected students.")
        return
    
    # Create DataFrame
    comparison_df = pd.DataFrame(comparison_data)
    
    # Plot student comparison
    fig_compare = px.bar(
        comparison_df,
        x="Student",
        y="Progress",
        color="Phase",
        barmode="group",
        title="Student Progress by Phase",
        labels={"Progress": "Completion (%)"},
        hover_data=["Career Path"]
    )
    st.plotly_chart(fig_compare, use_container_width=True)
    
    # Show tabular data
    st.subheader("Detailed Progress Data")
    st.dataframe(comparison_df, use_container_width=True)
    
    # Add download button for CSV export
    csv = comparison_df.to_csv(index=False)
    st.download_button(
        label="Download Progress Data as CSV",
        data=csv,
        file_name="student_progress.csv",
        mime="text/csv"
    )

def admin_dashboard(user_data, manager):
    st.markdown("## 📈 Students' Progress Overview")
    
    # Create a tab view for different admin views
    tab1, tab2 = st.tabs(["Class Summary", "Student Comparison"])
    
    with tab1:
        admin_class_summary(user_data, manager)
    
    with tab2:
        admin_student_comparison(user_data, manager)

# Main Application
def main():
    # Load saved user data
    user_data = load_json_data(USER_DATA_FILE)
    
    # Display header
    render_header()
    
    # Authentication Flow
    if not st.session_state["logged_in"]:
        render_auth_pages()
    else:
        # Initialize user's data if not exists
        current_username = st.session_state['username']
        if current_username not in user_data:
            user_data[current_username] = {"career_path": None, "progress": {}}
        
        # Render Sidebar
        render_sidebar(user_data)
        
        # Determine which user's data to display/edit
        viewing_user = current_username
        is_viewing_other = False
        
        if st.session_state["role"] == "admin" and st.session_state.get("selected_student") not in [None, "All Students"]:
            viewing_user = st.session_state["selected_student"]
            is_viewing_other = True
            st.info(f"You are viewing {viewing_user}'s progress as admin")

        # Career Path Selection - Required for first-time users
        if user_data[current_username].get("career_path") is None and not is_viewing_other:
            select_career_path(user_data, current_username)
        else:
            # Get the career path
            if is_viewing_other:
                current_track = user_data[viewing_user].get("career_path")
                if current_track is None:
                    st.warning(f"User {viewing_user} has not selected a career path yet.")
                    st.stop()
            else:
                current_track = user_data[current_username].get("career_path")
            
            st.markdown(f"## 🎓 {current_track} Career Path")
            
            # Get topics for the selected track
            topics_data = manager.get_topics(current_track)
            
            # Process the topics and track progress
            overall_progress = process_career_path_topics(
                topics_data, viewing_user, user_data, is_viewing_other, current_track
            )
            
            # Save all data
            save_json_data(user_data, USER_DATA_FILE)
            
            # Overall Progress Visualization
            if overall_progress:
                visualize_overall_progress(current_track, overall_progress)

        # Admin View: Monitor Student Progress
        if st.session_state["role"] == "admin":
            admin_dashboard(user_data, manager)

if __name__ == "__main__":
    main()