import streamlit as st

# header
def render_header():
    st.markdown("""
    <h1 style='text-align:center; color:#00C2FF;'>🚦 TrafficAI System</h1>
    <p style='text-align:center; color:gray;'>Real-time Vehicle Detection & Counting System</p>
    """, unsafe_allow_html=True)

# UI style
def render_ui_style():
    st.markdown("""
    <style>
    .block-container {
        padding-top: 3rem;
        padding-bottom: 1rem;
    }
    /* Plotly */
    div[data-testid="stPlotlyChart"] {
        background: #111827;
        border-radius: 14px;
        padding: 10px;
        box-shadow: 0px 6px 25px rgba(0,0,0,0.5);
    }
    /* Image */
    div[data-testid="stImage"] {
        border-radius: 16px;
        border: 1px solid #38BDF8;
        box-shadow: 0 0 20px rgba(56,189,248,0.4);
        background: rgba(17,24,39,0.8);
        padding: 6px;
    }
    /* Table */
    div[data-testid="stDataFrame"] {
        border-radius: 18px;
        overflow: hidden;
        background: #0B1220;
        border: 1px solid #38BDF8;
        box-shadow: 0 10px 30px rgba(56,189,248,0.25);
        padding: 8px;
    }
    div[data-testid="stDataFrame"] table tbody tr:hover {
        background-color: rgba(56,189,248,0.08);
        transition: 0.2s;
    }
    </style>
    """, unsafe_allow_html=True)