import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_progress_chart(progress_data):
    df = pd.DataFrame([
        {
            'Student': student,
            'Course': course,
            'Progress': data['progress']
        }
        for student, courses in progress_data.items()
        for course, data in courses.items()
    ])
    
    fig = px.bar(
        df,
        x='Student',
        y='Progress',
        color='Course',
        title='Student Progress by Course',
        labels={'Progress': 'Completion %'},
        barmode='group'
    )
    return fig

def create_average_progress_chart(progress_data):
    df = pd.DataFrame([
        {
            'Student': student,
            'Average': sum(d['progress'] for d in courses.values()) / len(courses)
        }
        for student, courses in progress_data.items()
        if courses
    ])
    
    fig = px.line(
        df,
        x='Student',
        y='Average',
        title='Average Student Progress',
        labels={'Average': 'Average Completion %'}
    )
    return fig
