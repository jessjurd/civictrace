import streamlit as st
from database import search_content

st.title("🔍 Search")
st.caption("Search across all reports and uploaded minutes.")

query = st.text_input(
    "Search term",
    placeholder="e.g. rates, BESS, drainage, Nulkaba, Cr Jurd..."
)

if query.strip():
    results = search_content(query.strip())
    reports = results["reports"]
    minutes = results["minutes"]

    st.markdown(f"*Found {len(reports)} report(s) and {len(minutes)} minutes document(s)*")

    if reports:
        st.subheader("Reports")
        for r in reports:
            with st.container(border=True):
                st.markdown(f"*{r['motion_title']}*  ·  {r['outcome']}")
                st.caption(f"{r['meeting_date']}  ·  {r['meeting_title']}  ·  ID #{r['id']}")
                if r.get("description"):
                    st.write(r["description"][:300] + ("..." if len(r["description"]) > 300 else ""))
                if r.get("votes"):
                    vote_str = ", ".join(f"{k}: {v}" for k, v in r["votes"].items())
                    st.caption(f"Votes: {vote_str}")

    if minutes:
        st.subheader("Minutes")
        for m in minutes:
            with st.expander(f"{m['meeting_date']}  ·  {m['meeting_title']}"):
                st.caption(f"File: {m['filename']}")
                text = m.get("content_text") or ""
                idx = text.lower().find(query.lower())
                if idx >= 0:
                    start = max(0, idx - 80)
                    end = min(len(text), idx + 200)
                    snippet = text[start:end]
                    st.text("..." + snippet + "...")
                else:
                    st.text(text[:400] + ("..." if len(text) > 400 else ""))

    if not reports and not minutes:
        st.info("No matches found.")
else:
    st.info("Enter a search term above.")
