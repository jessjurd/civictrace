"""
CivicTrace
A streamlined tool for municipal staff to document, search, and analyze
council meeting reports and voting outcomes.
"""

import streamlit as st
from pathlib import Path
import sys

# Ensure the local package is importable
sys.path.insert(0, str(Path(__file__).parent))

from database import init_db

# Page config – must be first Streamlit command
st.set_page_config(
    page_title="CivicTrace",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialise database
init_db()

# Custom CSS – navy / blue / gold branding matching the Base44 logo
st.markdown("""
<style>
    /* Main theme colours */
    :root {
        --navy: #0B1C2D;
        --blue: #1E88E5;
        --gold: #C9A227;
        --light: #F5F7FA;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0B1C2D;
    }
    section[data-testid="stSidebar"] * {
        color: #E8EEF5 !important;
    }
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] span {
        color: #E8EEF5 !important;
    }

    /* Headers */
    h1, h2, h3 {
        color: #0B1C2D !important;
    }

    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background-color: #1E88E5;
        border-color: #1E88E5;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #1565C0;
        border-color: #1565C0;
    }

    /* Danger / delete buttons */
    .stButton > button[kind="secondary"] {
        border-color: #c62828;
        color: #c62828;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #F5F7FA;
        padding: 12px 16px;
        border-radius: 8px;
        border-left: 4px solid #1E88E5;
    }

    /* Success / info boxes */
    .stSuccess, .stInfo {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar branding
with st.sidebar:
    st.markdown("### 🛡️ CivicTrace")
    st.caption("Council meeting reports & voting outcomes")
    st.markdown("---")

# Define pages
dashboard = st.Page("pages/1_Dashboard.py", title="Dashboard", icon="📊", default=True)
upload = st.Page("pages/2_Upload_Minutes.py", title="Upload Minutes", icon="📄")
add_report = st.Page("pages/3_Add_Report.py", title="Add Report", icon="➕")
search = st.Page("pages/4_Search.py", title="Search", icon="🔍")
analysis = st.Page("pages/5_Analysis.py", title="Voting Analysis", icon="📈")
manage = st.Page("pages/6_Manage_Data.py", title="Manage & Delete", icon="🗑️")

pg = st.navigation([dashboard, upload, add_report, search, analysis, manage])
pg.run()
