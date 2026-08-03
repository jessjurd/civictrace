import streamlit as st
from database import add_minutes, get_all_minutes, add_report
from parser import extract_motions, extract_conflicts
from datetime import date

st.title("📄 Upload Minutes")
st.caption("Upload council meeting minutes (PDF or text).")

meeting_date = st.date_input("Meeting date", value=date.today())
meeting_title = st.text_input("Meeting title *", placeholder="e.g. Ordinary Council Meeting – Nov 2025")

uploaded_file = st.file_uploader("Upload minutes file (PDF or TXT)", type=["pdf", "txt"])
pasted_text = st.text_area("Or paste minutes text here", height=150)

if st.button("Upload, Save & Extract", type="primary"):
    if not meeting_title.strip():
        st.error("Please enter a meeting title.")
    else:
        content = ""
        filename = None

        if uploaded_file is not None:
            filename = uploaded_file.name
            if filename.lower().endswith(".pdf"):
                try:
                    import pypdf
                    reader = pypdf.PdfReader(uploaded_file)
                    content = "\n".join([page.extract_text() or "" for page in reader.pages])
                    st.write(f"Extracted {len(content)} characters from PDF.")
                except Exception as e:
                    st.error(f"PDF error: {e}")
                    content = ""
            else:
                content = uploaded_file.read().decode("utf
