import streamlit as st
from database import add_minutes, get_all_minutes, add_report
from parser import extract_motions, extract_conflicts
from datetime import date

st.title("📄 Upload Minutes")
st.caption(
    "Upload council meeting minutes (PDF or text). "
    "The app extracts motions, FOR/AGAINST votes, and conflict-of-interest disclosures."
)

with st.form("upload_minutes_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        meeting_date = st.date_input("Meeting date", value=date.today())
    with col2:
        meeting_title = st.text_input(
            "Meeting title *",
            placeholder="e.g. Ordinary Council Meeting – 15 July 2026",
            value=st.session_state.get("last_meeting_title", ""),
        )

    uploaded_file = st.file_uploader(
        "Upload minutes file (PDF or TXT)",
        type=["pdf", "txt"],
    )

    pasted_text = st.text_area(
        "Or paste minutes text here",
        height=150,
        placeholder="Paste the full text of the minutes if preferred...",
    )

    submitted = st.form_submit_button(
        "Upload, Save & Extract", type="primary", use_container_width=True
    )

if submitted:
    if not meeting_title.strip():
        st.error("Please enter a meeting title.")
    else:
        content = ""
        filename = None

        if uploaded_file is not None:
            filename = uploaded_file.name
            if uploaded_file.type == "application/pdf" or (
                filename and filename.lower().endswith(".pdf")
            ):
                try:
                    import pypdf
                    reader = pypdf.PdfReader(uploaded_file)
                    content = "\n".join(page.extract_text() or "" for page in reader.pages)
                except Exception as e:
                    st.warning(f"Could not extract text from PDF ({e}). Saving filename only.")
                    content = f"[PDF uploaded: {filename} – text extraction failed]"
            else:
                content = uploaded_file.read().decode("utf-8", errors="ignore")

        if pasted_text.strip():
            content = (
                (content + "\n\n" + pasted_text).strip() if content else pasted_text.strip()
            )

        if not content and not filename:
            st.error("Please upload a file or paste some text.")
        else:
            mid = add_minutes(
                meeting_date=str(meeting_date),
                meeting_title=meeting_title.strip(),
                filename=filename or "pasted-text",
                content_text=content or "",
            )
            st.success(f"Minutes saved (ID #{mid}).")

            motions = extract_motions(content or "")
            conflicts = extract_conflicts(content or "")

            st.session_state["extracted_motions"] = motions
            st.session_state["extracted_conflicts"] = conflicts
            st.session_state["extract_meeting_date"] = str(meeting_date)
            st.session_state["extract_meeting_title"] = meeting_title.strip()
            st.session_state["last_meeting_title"] = meeting_title.strip()

            if motions:
                st.info(f"Found *{len(motions)}* motion(s). Review and import below.")
            else:
                st.warning(
                    "No clear MOTION / RESOLVED blocks detected. "
                    "You can still search the minutes or add reports manually."
                )
            if conflicts:
                st.info(f"Found *{len(conflicts)}* conflict-of-interest disclosure(s).")

conflicts = st.session_state.get("extracted_conflicts", [])
if conflicts:
    st.markdown("---")
    st.subheader("⚖️ Conflict of interest disclosures")
    st.caption("These were detected in the minutes.")

    for c in conflicts:
        with st.container(border=True):
            line = f"*{c['councillor']}* — {c['interest_type']}"
            if c.get("item_ref"):
                line += f"  ·  {c['item_ref']}"
            st.markdown(line)
            if c.get("reason"):
                st.write(c["reason"])
            if c.get("action"):
                st.caption(f"Action: {c['action']}")

motions = st.session_state.get("extracted_motions", [])
if motions:
    st.markdown("---")
    st.subheader("Review extracted motions")
    st.caption("Tick the ones you want to import as Reports.")

    select_all = st.checkbox("Select all", value=True, key="select_all_motions")

    selected_indices = []
    for i, m in enumerate(motions):
        with st.container(border=True):
            checked = st.checkbox(
                f"*{m['motion_title']}*",
                value=select_all,
                key=f"sel_motion_{i}",
            )
            if checked:
                selected_indices.append(i)

            c1, c2 = st.columns(2)
            with c1:
                st.caption(
                    f"Mover: {m['mover'] or '—'}  ·  Seconder: {m['seconder'] or '—'}  ·  "
                    f"Outcome: *{m['outcome']}*"
                )
            with c2:
                if m.get("votes"):
                    vote_summary = ", ".join(f"{k}: {v}" for k, v in list(m["votes"].items())[:8])
                    st.caption(f"Votes: {vote_summary}")
                else:
                    st.caption("No individual votes detected")

            new_title = st.text_input("Title", value=m["motion_title"], key=f"title_{i}")
            new_desc = st.text_area(
                "Description / resolution wording",
                value=m["description"],
                height=70,
                key=f"desc_{i}",
            )
            m["motion_title"] = new_title
            m["description"] = new_desc

            with st.expander("Show detected text"):
