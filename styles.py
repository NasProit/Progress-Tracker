import streamlit as st

def apply_custom_styles():
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            margin-top: 10px;
        }
        .stTextInput>div>div>input {
            width: 100%;
        }
        .reportview-container {
            margin-top: 2rem;
        }
        .css-1d391kg {
            padding: 2rem 1rem;
        }
        .stProgress > div > div > div > div {
            background-color: #1f77b4;
        }
        </style>
    """, unsafe_allow_html=True)
