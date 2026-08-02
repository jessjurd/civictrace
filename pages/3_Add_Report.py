import streamlit as st
from database import add_report
from datetime import date

st.title("➕ Add Report / Record Vote")
st.caption("Document a motion or report and record how each councillor voted.")

DEFAULT_COUNCILLORS = [
    "Mayor Watton",
    "Cr Dixon",
    "Cr Dunne",
    "Cr Harrington",
    "Cr Hill",
    "Cr Jurd",
    "Cr King",
    "Cr Lea",
    "Cr Franklin",
    "Cr Bangura",
    "Cr Palmowski",
    "Cr Pascoe",
    "Cr Hawkins",
]

VOTE_OPTIONS = ["For", "Against", "Abstain", "Absent", "Not Present"]

with st.form("add_report_form", clear_on_submit=True):
    st.subheader("Meeting details")
    c1, c2 = st.columns(2)
    with c1:
        meeting_date = st.date_input("Meeting date", value=date.today())
    with c2:
        meeting_title = st.text_input(
            "Meeting title *",
            placeholder="Ordinary Council Meeting – 15 July 2026"
        )

    st.subheader("Motion / Report")
    motion_title = st.text_input("Motion / Report title *", placeholder="e.g. Adoption of Nulkaba Structure Plan")
    description = st.text_area(
        "Full wording / description",
        height=120,
        placeholder="Optional – paste the motion wording or key points"
    )

    c3, c4 = st.columns(2)
    with c3:
        mover = st.text_input("Mover", placeholder="Cr Name")
    with c4:
        seconder = st.text_input("Seconder", placeholder="Cr Name")

    outcome = st.selectbox(
        "Outcome *",
        ["Carried", "Lost", "Withdrawn", "Deferred", "Amended then Carried"]
    )

    notes = st.text_area("Internal notes (optional)", height=80)

    st.subheader("Councillor votes")
    st.caption("Record how each councillor voted. Leave blank if not relevant.")

    councillor_text = st.text_area(
        "Councillors (one per line – edit as needed)",
        value="\n".join(DEFAULT_COUNCILLORS),
        height=140
    )
    councillor_list = [c.strip() for c in councillor_text.splitlines() if c.strip()]

    votes = {}
    if councillor_list:
        cols = st.columns(2)
        for i, name in enumerate(councillor_list):
            with cols[i % 2]:
                votes[name] = st.selectbox(
                    name,
                    options=["—"] + VOTE_OPTIONS,
                    key=f"vote_{i}_{name}"
                )

    submitted = st.form_submit_button("Save Report", type="primary", use_container_width=True)

    if submitted:
        if not meeting_title.strip() or not motion_title.strip():
            st.error("Meeting title and Motion title are required.")
        else:
            clean_votes = {k: v for k, v in votes.items() if v != "—"}
            rid = add_report(
                meeting_date=str(meeting_date),
                meeting_title=meeting_title.strip(),
                motion_title=motion_title.strip(),
                description=description.strip(),
                mover=mover.strip(),
                seconder=seconder.strip(),
                outcome=outcome,
                votes=clean_votes,
                notes=notes.strip()
            )
            st.success(f"Report saved successfully (ID #{rid}).")
            st.balloons()
