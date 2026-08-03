import streamlit as st
from database import add_minutes, get_all_minutes, add_report
from parser import extract_motions, extract_conflicts
from datetime import date

st.title("📄 Upload Minutes")
st.caption("Upload council meeting minutes (PDF or text). The app extracts motions, FOR/AGAINST votes, and conflict-of-interest disclosures.")

with st.form("upload_minutes_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        meeting_date = st.date_input("Meeting date", value=date.today())
    with col2:
        meeting_title = st.text_input("Meeting title *", placeholder="e.g. Ordinary Council Meeting – 15 July 2026", value=st.session_state.get("last_meeting_title", ""))

    uploaded_file = st.file_uploader("Upload minutes file (PDF or TXT)", type=["pdf", "txt"])
    pasted_text = st.text_area("Or paste minutes text here", height=150, placeholder="Paste the full text of the minutes if preferred...")
    submitted = st.form_submit_button("Upload, Save & Extract", type="primary", use_container_width=True)

if submitted:
    if not meeting_title.strip():
        st.error("Please enter a meeting title.")
    else:
        content = ""
        filename = None
