import streamlit as st
from database import init_db

st.set_page_config(
    page_title="CivicTrace",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

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
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🛡️ CivicTrace")
    st.caption("Council meeting reports & voting outcomes")
    st.markdown("---")

st.title("🛡️ CivicTrace")
st.markdown("""
*A streamlined tool for municipal staff to document, search, and analyse council meeting reports and voting outcomes.*

### How to use
1. Use the sidebar to open *Upload Minutes*, *Add Report*, *Dashboard*, etc.
2. Upload minutes to extract motions, votes and conflicts.
3. Review and import the ones you want.
""")

st.success("App is running. Select a page from the sidebar to get started.")
