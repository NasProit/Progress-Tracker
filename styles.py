import streamlit as st

def apply_custom_styles():
    st.markdown("""
        <style>
        /* Main container styling */
        .main {
            padding: 2rem;
        }

        /* Button styling */
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            background-color: #1f77b4;
            color: white;
            font-weight: bold;
            border: none;
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            background-color: #135c8d;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        /* Input field styling */
        .stTextInput>div>div>input {
            border-radius: 5px;
            border: 1px solid #e0e0e0;
            padding: 1em;
        }

        /* Progress bar styling */
        .stProgress>div>div>div>div {
            background-color: #1f77b4;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f0f2f6;
            border-radius: 5px 5px 0 0;
            gap: 2px;
            padding: 10px;
        }

        .stTabs [aria-selected="true"] {
            background-color: #1f77b4;
            color: white;
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #f0f2f6;
            border-radius: 5px;
        }

        /* Sidebar styling */
        .css-1d391kg {
            padding: 2rem 1rem;
        }

        /* Card-like containers */
        div[data-testid="stExpander"] {
            background-color: white;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        </style>
    """, unsafe_allow_html=True)