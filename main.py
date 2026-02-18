"""
Streamlit UI for Prayer Tracker + Tasks
- Uses DBManager from database.py
- Dark brown theme is injected via CSS for a consistent "brown ecosystem" dark mode
- Professional layout with sidebar user selection, date picker, task form, prayer checklist, and task list
"""

import streamlit as st
from datetime import date
from database import DBManager
from pathlib import Path

st.set_page_config(page_title="Prayer & Tasks — Tracker", layout="wide", initial_sidebar_state="expanded")

# --- Dark brown theme (injected CSS) ---
BROWN_PRIMARY = "#a66b2a"
BROWN_ACCENT = "#8a5b1f"
BROWN_BG = "#1b120b"  # very dark brown / near black
BROWN_PANEL = "#23160f"
TEXT = "#EDE3DA"

st.markdown(
    f"""
    <style>
    /* page background */
    .stApp {{
        background: linear-gradient(0deg, {BROWN_BG}, {BROWN_BG});
        color: {TEXT};
    }}
    /* main container and sidebar */
    .css-1d391kg .css-1v3fvcr {{
        background-color: {BROWN_PANEL};
    }}
    .stSidebar .css-1d391kg {{
        background-color: {BROWN_PANEL};
    }}
    /* headers and text */
    .css-ffhzg2, .css-1v3fvcr, .st-bk {{
        color: {TEXT} !important;
    }}
    /* buttons */
    .stButton>button {{
        background: linear-gradient(180deg, {BROWN_PRIMARY}, {BROWN_ACCENT});
        color: #fff;
        border-radius: 6px;
        padding: 8px 12px;
    }}
    /* inputs */
    .stTextInput>div>div>input, .stDateInput>div>div>input, textarea {{
        background-color: #2b2018;
        color: {TEXT};
        border: 1px solid #3b2a1f;
    }}
    /* cards / tables */
    .stDataFrame table {{
        color: {TEXT};
        background-color: transparent;
    }}
    /* checkbox labels color */
    .stCheckbox label {{
        color: {TEXT};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Database ---
DB = DBManager()  # uses data/app_data.db by default

# --- Sidebar: user and date selection ---
st.sidebar.header("User & Date")
username = st.sidebar.text_input("Your name", value=st.session_state.get("username", "Guest"))
st.sidebar.write("Date for prayers / tasks")
selected_date = st.sidebar.date_input("Select date", value=st.session_state.get("selected_date", date.today()))
# normalize and store in session
st.session_state["username"] = username
st.session_state["selected_date"] = selected_date

# Convert date to ISO string for DB usage
date_iso = selected_date.isoformat()

# --- Main layout ---
st.title("Prayer Tracker & Tasks")
st.caption("Organize your daily prayers and tasks — professional, private, and backed by SQLite.")

col1, col2 = st.columns([2, 1])

# Left column: Tasks
with col1:
    st.subheader("Tasks")
    with st.form(key="add_task_form", clear_on_submit=True):
        task_text = st.text_input("Add a task", placeholder="e.g. Prepare sermon notes", key="task_input")
        due_date = st.date_input("Due date (optional)", value=selected_date, key="task_due")
        submitted = st.form_submit_button("Add task")
        if submitted and task_text.strip():
            try:
                created = DB.add_task(username, task_text.strip(), due_date.isoformat() if due_date else None)
                st.success("Task added")
            except Exception as e:
                st.error(f"Could not add task: {e}")

    # Show lists
    tasks = DB.get_tasks(username)
    st.markdown("### Incomplete")
    for t in tasks["incomplete"]:
        row_col1, row_col2 = st.columns([8, 2])
        with row_col1:
            st.markdown(f"**{t['task']}**  \n*Due:* {t.get('due_date') or '—'}  \n*Added:* {t.get('created_at')}")
        with row_col2:
            # Buttons to mark complete or delete
            if st.button("Mark done", key=f"done_{t['id']}"):
                DB.set_task_completed(username, t["id"], True)
                st.experimental_rerun()
            if st.button("Delete", key=f"del_{t['id']}"):
                DB.delete_task(username, t["id"])
                st.experimental_rerun()

    st.markdown("### Completed")
    for t in tasks["completed"]:
        st.markdown(f"- ~~{t['task']}~~  (added {t.get('created_at')})")
        if st.button("Mark not done", key=f"undo_{t['id']}"):
            DB.set_task_completed(username, t["id"], False)
            st.experimental_rerun()

# Right column: Prayers
with col2:
    st.subheader("Prayer checklist")
    # default prayer set (you can modify this list)
    default_prayers = [
        "AlFajr",
        "alZuhr",
        "Alaasr",
        "Almaghreb",
        "alEshaa"
    ]
    # Ensure these prayers exist for the user and date (won't overwrite completed state)
    DB.ensure_prayers_exist_for_date(username, date_iso, default_prayers)

    prayer_status = DB.get_prayers_for_date(username, date_iso)
    # Display as checkboxes in a form so we can batch update
    with st.form(key="prayer_form"):
        updated_status = {}
        for p_text in sorted(prayer_status.keys()):
            checked = prayer_status.get(p_text, False)
            # Use unique keys to avoid collisions in Streamlit
            updated = st.checkbox(p_text, value=checked, key=f"pr_{p_text}_{date_iso}")
            updated_status[p_text] = updated
        saved = st.form_submit_button("Save prayers")
        if saved:
            DB.set_prayer_status_for_date(username, date_iso, updated_status)
            st.success("Prayers updated")

st.sidebar.markdown("---")
st.sidebar.caption("Made with care — brown dark theme enabled.")

# optionally show debug / DB path
if st.sidebar.checkbox("Show storage info"):
    st.sidebar.write(f"DB file: {DB.db_path}")
    st.sidebar.write(f"User: {username}  Date: {date_iso}")
