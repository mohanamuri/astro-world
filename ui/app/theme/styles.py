"""Dark cosmic CSS theme."""
import streamlit as st

CSS = """
<style>
/* ── Global ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0D0D1A !important;
    color: #E8E8F0 !important;
}
[data-testid="stSidebar"] {
    background-color: #12122A !important;
    border-right: 1px solid #2A2A4A !important;
}

/* ── Headers ── */
h1, h2, h3 { color: #C9A96E !important; font-weight: 700 !important; }
h4, h5, h6 { color: #B0B8D0 !important; }

/* ── Cards / containers ── */
[data-testid="stExpander"] {
    background-color: #1A1A2E !important;
    border: 1px solid #2A2A4A !important;
    border-radius: 10px !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background-color: #1A1A2E !important;
    border: 1px solid #2A2A4A !important;
    border-radius: 10px !important;
    padding: 12px !important;
}
[data-testid="metric-container"] label { color: #C9A96E !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #E8E8F0 !important; font-size: 1.4rem !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #C9A96E, #a07a45) !important;
    color: #0D0D1A !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.2rem !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #e0c080, #C9A96E) !important;
}

/* ── Tabs ── */
[data-testid="stTab"] { color: #B0B8D0 !important; }
[aria-selected="true"] { color: #C9A96E !important; border-bottom: 2px solid #C9A96E !important; }

/* ── Info/success boxes ── */
.stAlert { border-radius: 8px !important; }

/* ── Divider ── */
hr { border-color: #2A2A4A !important; }

/* ── Input fields ── */
input, textarea, select {
    background-color: #1A1A2E !important;
    color: #E8E8F0 !important;
    border: 1px solid #2A2A4A !important;
    border-radius: 6px !important;
}

/* ── Sidebar nav ── */
.nav-item {
    display: block;
    padding: 10px 16px;
    border-radius: 8px;
    cursor: pointer;
    color: #B0B8D0;
    text-decoration: none;
    margin-bottom: 4px;
    transition: all 0.2s;
}
.nav-item:hover, .nav-item.active {
    background-color: #2A2A4A;
    color: #C9A96E;
}

/* ── Planet badge ── */
.planet-badge {
    display: inline-block;
    background: #1A1A2E;
    border: 1px solid #C9A96E;
    border-radius: 20px;
    padding: 3px 10px;
    margin: 3px;
    font-size: 0.82rem;
    color: #E8E8F0;
}

/* ── Score bar ── */
.score-bar-bg {
    background: #1A1A2E;
    border-radius: 10px;
    height: 14px;
    width: 100%;
    margin: 6px 0;
}
.score-bar-fill {
    border-radius: 10px;
    height: 14px;
    background: linear-gradient(90deg, #C9A96E, #7B6CF6);
}
</style>
"""

def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)
