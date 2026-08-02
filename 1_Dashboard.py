import streamlit as st
from database import get_all_reports, get_all_minutes
from collections import Counter
from datetime import datetime

st.title("📊 Dashboard")
st.caption("Overview of documented reports and uploaded minutes")

reports = get_all_reports()
minutes = get_all_minutes()

# --- Key metrics ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Reports", len(reports))
col2.metric("Minutes Uploaded", len(minutes))

carried = sum(1 for r in reports if r["outcome"] == "Carried")
lost = sum(1 for r in reports if r["outcome"] == "Lost")
col3.metric("Carried", carried)
col4.metric("Lost", lost)

st.markdown("---")

# --- Recent reports ---
st.subheader("Recent Reports")
if not reports:
    st.info("No reports recorded yet. Go to **Add Report** to create one.")
else:
    for r in reports[:8]:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"**{r['motion_title']}**")
                st.caption(f"{r['meeting_date']}  ·  {r['meeting_title']}")
                outcome_colour = {
                    "Carried": "🟢",
                    "Lost": "🔴",
                    "Withdrawn": "⚪",
                    "Deferred": "🟡"
                }.get(r["outcome"], "⚪")
                st.write(f"{outcome_colour} **{r['outcome']}**  ·  Mover: {r['mover'] or '—'}  ·  Seconder: {r['seconder'] or '—'}")
            with c2:
                st.caption(f"ID #{r['id']}")

# --- Recent minutes ---
st.markdown("---")
st.subheader("Recently Uploaded Minutes")
if not minutes:
    st.info("No minutes uploaded yet.")
else:
    for m in minutes[:5]:
        with st.container(border=True):
            st.markdown(f"**{m['meeting_title']}**")
            st.caption(f"{m['meeting_date']}  ·  File: {m['filename'] or '—'}  ·  Uploaded {m['uploaded_at'][:10]}")
