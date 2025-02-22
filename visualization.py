import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_progress_chart(progress_data):
    # Create a list to store the flattened data
    data_list = []

    for student, topics in progress_data.items():
        for topic, subtopics in topics.items():
            for subtopic, data in subtopics.items():
                data_list.append({
                    'Student': student,
                    'Topic': topic,
                    'Subtopic': subtopic,
                    'Progress': data['progress']
                })

    if not data_list:
        return go.Figure()

    df = pd.DataFrame(data_list)

    fig = px.bar(
        df,
        x='Student',
        y='Progress',
        color='Topic',
        pattern_shape='Subtopic',
        title='Student Progress by Topic',
        labels={'Progress': 'Completion %'},
        barmode='group'
    )

    fig.update_layout(
        showlegend=True,
        xaxis_title="Students",
        yaxis_title="Progress (%)",
        legend_title="Topics",
        font=dict(size=12)
    )

    return fig

def create_average_progress_chart(progress_data):
    # Create a list to store the flattened data
    data_list = []

    for student, topics in progress_data.items():
        student_total = 0
        subtopic_count = 0
        for topic, subtopics in topics.items():
            for subtopic, data in subtopics.items():
                student_total += data['progress']
                subtopic_count += 1
        if subtopic_count > 0:
            data_list.append({
                'Student': student,
                'Average': student_total / subtopic_count
            })

    if not data_list:
        return go.Figure()

    df = pd.DataFrame(data_list)

    fig = px.line(
        df,
        x='Student',
        y='Average',
        title='Average Student Progress',
        labels={'Average': 'Average Completion %'},
        markers=True
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=10)
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title="Students",
        yaxis_title="Average Progress (%)",
        font=dict(size=12)
    )

    return fig