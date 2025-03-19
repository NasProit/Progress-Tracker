import streamlit as st
import json
import os
import datetime
import data_manager  
import auth  
import plotly.express as px
import pandas as pd
from visualization import create_progress_chart, create_average_progress_chart

# File for storing user data
USER_DATA_FILE = "user_data.json"

# Initialize Data
manager = data_manager.DataManager()
auth_instance = auth.Auth(manager)

# Function to Load Data from JSON
def load_json_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                data = f.read().strip()
                return json.loads(data) if data else {}  # Empty JSON if file is empty
        except json.JSONDecodeError:
            return {}  # Return empty dictionary if JSON is corrupt
    return {}

# Function to Save Data to JSON
def save_json_data(data, file_path):
    temp_file = file_path + ".tmp"
    with open(temp_file, "w") as f:
        json.dump(data, f, indent=4)
    os.replace(temp_file, file_path)  # Safely replace original file

# Load saved user data
user_data = load_json_data(USER_DATA_FILE)

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False,
        "username": None,
        "role": None,
        "current_page": "login",
        "selected_phase": None,
        "selected_topic": None,
        "selected_student": None
    })

# Display Logo
if os.path.exists("assets/logo.png"):
    st.image("assets/logo.png", width=700)

# Main Title
st.markdown("<h1 style='text-align: center; color: #1f77b4;'>📊 ProITbridge Milestone Tracker</h1>", unsafe_allow_html=True)

# Authentication
if not st.session_state["logged_in"]:
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Login Page", use_container_width=True, type="primary" if st.session_state["current_page"] == "login" else "secondary"):
            st.session_state["current_page"] = "login"
            st.rerun()
    with col2:
        if st.button("Register Page", use_container_width=True, type="primary" if st.session_state["current_page"] == "register" else "secondary"):
            st.session_state["current_page"] = "register"
            st.rerun()

    if st.session_state["current_page"] == "login":
        st.text_input("Username", key="login_username")
        st.text_input("Password", type="password", key="login_password")
        role = st.selectbox("Role", ["student", "admin"], key="login_role")

        if st.button("🔐 Login", key="login_button"):
            username = st.session_state.get("login_username", "")
            password = st.session_state.get("login_password", "")
            role = st.session_state.get("login_role", "student")
            if username and password:
                st.info(f"Attempting login for {username}...")  # Debug feedback
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
    else:
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
                    st.info("Processing registration...")  # Debug feedback
                    if auth_instance.register(username, password, confirm_password):
                        st.success(f"Registration successful for {username}")
                        st.session_state["current_page"] = "login"
                        st.session_state["register_status"] = "success"
                        st.rerun()
                    else:
                        st.error("Registration failed - please try again")
                        st.session_state["register_status"] = "error"
else:
    # Load user data
    user_data = load_json_data(USER_DATA_FILE)
    current_username = st.session_state['username']

    # Initialize user's data if not exists
    if current_username not in user_data:
        user_data[current_username] = {"career_path": None, "progress": {}}

    with st.sidebar:
        st.write(f"👤 Welcome, {current_username}!")
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

    # Determine which user's data to display/edit
    viewing_user = current_username
    is_viewing_other = False

    if st.session_state["role"] == "admin" and st.session_state.get("selected_student") not in [None, "All Students"]:
        viewing_user = st.session_state["selected_student"]
        is_viewing_other = True
        st.info(f"You are viewing {viewing_user}'s progress as admin")

    # Career Path Selection - Fixed once chosen
    if user_data[current_username].get("career_path") is None and not is_viewing_other:
        st.markdown("## 🎯 Select Your Career Path")
        st.warning("This selection is permanent and cannot be changed later!")

        selected_track = st.selectbox("Choose a Track", ["Data Analyst", "Data Scientist"], index=None, placeholder="Select a Career Path")
        # Add this new selection right after the career path selection
        course_type = st.selectbox("Choose Course Type", [
            "Full Data Science Course", 
            "Full Data Analyst Course", 
            "Mentorship for Data Science", 
            "Mentorship for Data Analyst"
        ], index=None, placeholder="Select Course Type")

        if selected_track and course_type and st.button("Confirm Career Path Selection", type="primary"):
            user_data[current_username]["career_path"] = selected_track
            user_data[current_username]["course_type"] = course_type  # Store the course type
            save_json_data(user_data, USER_DATA_FILE)
            st.success(f"You have selected {selected_track} ({course_type}) as your career path")
            st.rerun()
    else:
        # Get the career path
        if is_viewing_other:
            current_track = user_data[viewing_user].get("career_path")
            if current_track is None:
                st.warning(f"User {viewing_user} has not selected a career path yet.")
                st.stop()
        else:
            current_track = user_data[current_username].get("career_path")

       
        # Right after this line: st.markdown(f"## 🎓 {current_track} Career Path")

        # Get the course type
        if is_viewing_other:
            course_type = user_data[viewing_user].get("course_type", "Not specified")
        else:
            course_type = user_data[current_username].get("course_type", "Not specified")

        # Display both career path and course type
        st.markdown(f"## 🎓 {current_track} Career Path - {course_type}")

        # Get topics for the selected track
        topics_data = manager.get_topics(current_track)

        # Profile Summary Section
        with st.expander("📋 Profile Summary", expanded=True):
            profile_key = f"{current_track}_profile_summary"
            current_summary = user_data[viewing_user].get("profile_summary", "")
            new_summary = st.text_area(
                "Your Professional Summary",
                value=current_summary,
                height=150,
                placeholder="Write your professional summary here...",
                disabled=is_viewing_other
            )
            if new_summary != current_summary and not is_viewing_other:
                user_data[viewing_user]["profile_summary"] = new_summary
                save_json_data(user_data, USER_DATA_FILE)

        # Create tabs for each phase
        phase_tabs = st.tabs(list(topics_data.keys()))

        # Track overall progress data for final summary
        overall_progress = {}

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

                                # Initialize columns
                                col1, col2, col3 = st.columns([3, 1, 2])

                                with col1:
                                    label = f"{subtopic}"
                                    st.markdown(f"**{label}**")
                                    # Add document link input if in Documents section
                                    if "Portfolio" in topic_name:
                                        # Create columns for link input/display and edit button
                                        link_col1, link_col2 = st.columns([4, 1])

                                        # Initialize progress data if not exists
                                        if subtopic_key not in user_data[viewing_user]["progress"]:
                                            user_data[viewing_user]["progress"][subtopic_key] = {
                                                "completion": 0,
                                                "deadlines": [],
                                                "link": "",
                                                "editing": False
                                            }

                                        # Get current link and editing state
                                        progress_data = user_data[viewing_user]["progress"][subtopic_key]
                                        current_link = progress_data.get("link", "")
                                        

                                        # Initialize editing state if not exists
                                        if "editing" not in progress_data:
                                            progress_data["editing"] = False

                                        if current_link and not progress_data["editing"]:
                                            # Display current link as clickable
                                            st.markdown(f"[{subtopic}]({current_link})")
                                        else:
                                            # Initialize session state for this link
                                            link_key = f"link_{viewing_user}_{subtopic_key}"
                                            if link_key not in st.session_state:
                                                st.session_state[link_key] = current_link or ""

                                            # Show input field when editing
                                            new_link = st.text_input(
                                                "Document Link",
                                                value=st.session_state[link_key],
                                                key=link_key,
                                                placeholder="Enter document URL",
                                                disabled=is_viewing_other
                                            )

                                            # Save button to confirm changes
                                            if st.button("Save Link", key=f"save_{subtopic_key}", disabled=is_viewing_other):
                                                progress_data.update({
                                                    "link": new_link,
                                                    "editing": False
                                                })
                                                save_json_data(user_data, USER_DATA_FILE)
                                                st.rerun()

                                        with link_col2:
                                            if not is_viewing_other:
                                                if current_link and not progress_data["editing"]:
                                                    if st.button("📝 Edit", key=f"edit_{subtopic_key}"):
                                                        progress_data["editing"] = True
                                                        save_json_data(user_data, USER_DATA_FILE)
                                                        st.rerun()

                                with col2:
                                    percentage = st.slider("", 0, 100, subtopic_data.get("completion", 0), 
                                                         key=f"{viewing_user}_{subtopic_key}",
                                                         disabled=is_viewing_other)
                                    topic_progress[subtopic] = percentage

                                # Deadline Handling
                                with col3:
                                    prev_dates = subtopic_data.get("deadlines", [])

                                    # Date input (disabled for admin viewing other users)
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
                                        # Only add the date if it's different from the last one
                                        if not prev_dates or prev_dates[-1] != current_date_str:
                                            prev_dates.append(current_date_str)
                                            # Don't sort dates - we want to preserve the history in order of entry

                                        # Update progress data
                                        if "progress" not in user_data[viewing_user]:
                                            user_data[viewing_user]["progress"] = {}

                                        user_data[viewing_user]["progress"][subtopic_key] = {
                                            "completion": percentage,
                                            "deadlines": prev_dates,
                                            "timestamp": datetime.datetime.now().isoformat()
                                        }

                                    # Format and display deadline history
                                    if prev_dates:
                                        st.markdown("##### Deadline History:")
                                        timeline_html = ""

                                        for i, date in enumerate(prev_dates):
                                            # Format: older dates small and strikethrough, latest date bold
                                            if i < len(prev_dates) - 1:
                                                # Older dates (small and strikethrough)
                                                size = max(70 - (len(prev_dates) - i - 1) * 5, 50)  # Size decreases with age
                                                timeline_html += f"<span style='text-decoration:line-through;font-size:{size}%;color:gray;'>{date}</span> → "
                                            else:
                                                # Latest date (bold and larger)
                                                timeline_html += f"<span style='font-weight:bold;font-size:110%;color:#1f77b4;'>{date}</span>"

                                        st.markdown(timeline_html, unsafe_allow_html=True)

                        # Topic progress visualization
                        if topic_progress:
                            st.markdown("#### Topic Progress")

                            # Create DataFrame for better visualization
                            topic_df = pd.DataFrame({
                                'Subtopic': list(topic_progress.keys()),
                                'Completion': list(topic_progress.values())
                            })

                            fig_topic = px.bar(
                                topic_df,
                                x='Subtopic',
                                y='Completion',
                                title=f"{topic_name} Progress",
                                color='Completion',
                                color_continuous_scale='Blues',
                                labels={"Completion": "Completion (%)"}
                            )
                            fig_topic.update_layout(height=300)
                            st.plotly_chart(fig_topic, use_container_width=True)

                            # Add to phase progress
                            phase_progress[topic_name] = sum(topic_progress.values()) / len(topic_progress)

                # Phase progress visualization after all topics are processed
                if phase_progress:
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

                    # Store overall progress for this phase
                    overall_progress[phase_name] = sum(phase_progress.values()) / len(phase_progress)

        # Save all data
        save_json_data(user_data, USER_DATA_FILE)

        # Overall Progress Visualization (after all phases)
        st.markdown("## 📊 Overall Career Progress")

        if overall_progress:
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
                fig_gauge.update_traces(marker=dict(colors=['#1f77b4', '#e0e0e0']))
                st.plotly_chart(fig_gauge, use_container_width=True)

    # Admin View: Monitor Student Progress
    if st.session_state["role"] == "admin":
        st.markdown("## 📈 Students' Progress Overview")

        # Create a tab view for different admin views
        tab1, tab2 = st.tabs(["Class Summary", "Student Comparison"])

        with tab1:
            # Get all students with their career path selected
            students = [user for user in user_data.keys() if user_data[user].get("career_path") is not None]

            if not students:
                st.info("No student data available yet.")
            else:
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

                if student_data:
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

        with tab2:
            # Get all students with their career path selected
            students = [user for user in user_data.keys() if user_data[user].get("career_path") is not None]

            if not students:
                st.info("No student data available yet.")
            else:
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

                if filtered_students:
                    # Get phases for the selected career path(s)
                    all_phases = set()
                    for student in filtered_students:
                        career_path = user_data[student].get("career_path")
                        if career_path:
                            topics_data = manager.get_topics(career_path)
                            all_phases.update(topics_data.keys())

                    # Create comparison data
                    comparison_data = []

                    for student in filtered_students:
                        career_path = user_data[student].get("career_path")
                        if career_path and "progress" in user_data[student]:
                            # Calculate progress for each phase
                            student_phases = {}

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

                    if comparison_data:
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