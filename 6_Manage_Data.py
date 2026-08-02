import streamlit as st
from database import get_all_reports, delete_report, get_all_minutes, delete_minutes

st.title("🗑️ Manage & Delete")
st.caption("Review and permanently delete reports or minutes that were entered incorrectly.")

tab1, tab2 = st.tabs(["Reports", "Minutes"])

# ---------- REPORTS ----------
with tab1:
    reports = get_all_reports()
    if not reports:
        st.info("No reports to manage.")
    else:
        st.write(f"**{len(reports)} report(s)**")
        for r in reports:
            with st.container(border=True):
                col_main, col_del = st.columns([5, 1])
                with col_main:
                    st.markdown(f"**#{r['id']}  ·  {r['motion_title']}**")
                    st.caption(
                        f"{r['meeting_date']}  ·  {r['meeting_title']}  ·  "
                        f"Outcome: **{r['outcome']}**  ·  Mover: {r['mover'] or '—'}"
                    )
                    if r.get("description"):
                        st.write(r["description"][:250] + ("..." if len(r["description"]) > 250 else ""))
                with col_del:
                    # Confirmation pattern
                    if st.button("Delete", key=f"del_report_{r['id']}", type="secondary"):
                        st.session_state[f"confirm_del_report_{r['id']}"] = True

                # Show confirmation if requested
                if st.session_state.get(f"confirm_del_report_{r['id']}", False):
                    st.warning(f"Are you sure you want to permanently delete report **#{r['id']}**?")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Yes, delete it", key=f"yes_del_report_{r['id']}", type="primary"):
                            if delete_report(r["id"]):
                                st.success(f"Report #{r['id']} deleted.")
                                # Clear confirmation flag
                                del st.session_state[f"confirm_del_report_{r['id']}"]
                                st.rerun()
                            else:
                                st.error("Could not delete.")
                    with c2:
                        if st.button("Cancel", key=f"cancel_del_report_{r['id']}"):
                            del st.session_state[f"confirm_del_report_{r['id']}"]
                            st.rerun()

# ---------- MINUTES ----------
with tab2:
    minutes = get_all_minutes()
    if not minutes:
        st.info("No minutes to manage.")
    else:
        st.write(f"**{len(minutes)} minutes document(s)**")
        for m in minutes:
            with st.container(border=True):
                col_main, col_del = st.columns([5, 1])
                with col_main:
                    st.markdown(f"**#{m['id']}  ·  {m['meeting_title']}**")
                    st.caption(
                        f"{m['meeting_date']}  ·  File: {m['filename']}  ·  "
                        f"Uploaded: {m['uploaded_at'][:16]}"
                    )
                    preview = (m.get("content_text") or "")[:200]
                    if preview:
                        st.text(preview + ("..." if len(m.get("content_text") or "") > 200 else ""))
                with col_del:
                    if st.button("Delete", key=f"del_min_{m['id']}", type="secondary"):
                        st.session_state[f"confirm_del_min_{m['id']}"] = True

                if st.session_state.get(f"confirm_del_min_{m['id']}", False):
                    st.warning(f"Are you sure you want to permanently delete minutes **#{m['id']}**?")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Yes, delete it", key=f"yes_del_min_{m['id']}", type="primary"):
                            if delete_minutes(m["id"]):
                                st.success(f"Minutes #{m['id']} deleted.")
                                del st.session_state[f"confirm_del_min_{m['id']}"]
                                st.rerun()
                            else:
                                st.error("Could not delete.")
                    with c2:
                        if st.button("Cancel", key=f"cancel_del_min_{m['id']}"):
                            del st.session_state[f"confirm_del_min_{m['id']}"]
                            st.rerun()
