import streamlit as st
from database import get_all_reports
from collections import Counter, defaultdict
import pandas as pd

st.title("📈 Voting Analysis")
st.caption("Simple breakdowns of recorded votes and outcomes.")

reports = get_all_reports()

if not reports:
    st.info("No reports yet. Add some reports first to see analysis.")
    st.stop()

# --- Outcomes ---
st.subheader("Outcomes")
outcome_counts = Counter(r["outcome"] for r in reports)
df_outcomes = pd.DataFrame(
    {"Outcome": list(outcome_counts.keys()), "Count": list(outcome_counts.values())}
)
st.bar_chart(df_outcomes.set_index("Outcome"))

# --- Councillor voting patterns ---
st.subheader("Councillor voting patterns")

vote_totals = defaultdict(lambda: Counter())
for r in reports:
    for name, vote in r.get("votes", {}).items():
        vote_totals[name][vote] += 1

if vote_totals:
    # Build a summary table
    rows = []
    for name, counts in sorted(vote_totals.items()):
        rows.append({
            "Councillor": name,
            "For": counts.get("For", 0),
            "Against": counts.get("Against", 0),
            "Abstain": counts.get("Abstain", 0),
            "Absent / Not Present": counts.get("Absent", 0) + counts.get("Not Present", 0),
            "Total recorded": sum(counts.values())
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Simple percentage For
    st.subheader("% For (of votes cast)")
    for_pct = []
    for name, counts in sorted(vote_totals.items()):
        for_count = counts.get("For", 0)
        against = counts.get("Against", 0)
        total_cast = for_count + against
        pct = round(100 * for_count / total_cast, 1) if total_cast > 0 else None
        if pct is not None:
            for_pct.append({"Councillor": name, "% For": pct})
    if for_pct:
        st.bar_chart(pd.DataFrame(for_pct).set_index("Councillor"))
else:
    st.info("No individual votes have been recorded yet.")

# --- Recent activity ---
st.subheader("All recorded reports")
for r in reports:
    with st.expander(f"{r['meeting_date']}  ·  {r['motion_title']}  ({r['outcome']})"):
        st.write(f"**Meeting:** {r['meeting_title']}")
        st.write(f"**Mover:** {r['mover'] or '—'}   |   **Seconder:** {r['seconder'] or '—'}")
        if r.get("description"):
            st.write(r["description"])
        if r.get("votes"):
            st.write("**Votes:**")
            for name, vote in r["votes"].items():
                st.write(f"- {name}: {vote}")
        if r.get("notes"):
            st.caption(f"Notes: {r['notes']}")
