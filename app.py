"""
CivicTrace
A streamlined tool for municipal staff to document, search, and analyze
council meeting reports and voting outcomes.
"""

import streamlit as st
from pathlib import Path
import sys

# Ensure the local package is importable
sys.path.insert(0, str(Path(_file_).parent))

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

# Custom CSS – navy / blue / gold branding
st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        background-color: #0B1C2D;
    }
    section[data-testid="stSidebar"] * {
        color: #E8EEF5 !important;
    }
    h1, h2, h3 {
        color: #0B1C2D !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #1E88E5;
        border-color: #1E88E5;
    }
    [data-testid="stMetric"] {
        background-color: #F5F7FA;
        padding: 12px 16px;
        border-radius: 8px;
        border-left: 4px solid #1E88E5;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar branding
with st.sidebar:
    st.markdown("### 🛡️ CivicTrace")
    st.caption("Council meeting reports & voting outcomes")
    st.markdown("---")
    st.info("Use the pages in the sidebar to navigate.")

# Home / landing content
st.title("🛡️ CivicTrace")
st.markdown("""
*A streamlined tool for municipal staff to document, search, and analyse council meeting reports and voting outcomes.*

### How to use
1. Go to *Upload Minutes* to upload a set of council minutes (PDF or text).
2. The app will extract motions, votes and conflicts for you to review.
3. Import the ones you want as Reports.
4. Use *Dashboard*, *Search*, *Voting Analysis* and *Manage & Delete* as needed.
""")

st.success("App is running. Select a page from the sidebar to get started.")
