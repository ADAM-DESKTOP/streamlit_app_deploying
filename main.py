import streamlit as st
import hashlib
import os
from database import PrayerDB
from datetime import date, datetime
import geocoder
import calendar
from prayer_times_calculator import PrayerTimesCalculator
import uuid


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_user(username, password):
    # Save user credentials to a simple file (for demo; use a real DB in production)
    with open("users.txt", "a") as f:
        f.write(f"{username}:{hash_password(password)}\n")

def user_exists(username):
    if not os.path.exists("users.txt"):
        return False
    with open("users.txt", "r") as f:
        for line in f:
            if line.split(":")[0] == username:
                return True
    return False

def check_user(username, password):
    if not os.path.exists("users.txt"):
        return False
    with open("users.txt", "r") as f:
        for line in f:
            u, p = line.strip().split(":")
            if u == username and p == hash_password(password):
                return True
    return False

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

if not st.session_state["logged_in"]:
    st.title("Login or Register")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if check_user(login_user, login_pass):
                st.session_state["logged_in"] = True
                st.session_state["username"] = login_user
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with tab2:
        reg_user = st.text_input("Choose a username", key="reg_user")
        reg_pass = st.text_input("Choose a password", type="password", key="reg_pass")
        if st.button("Register"):
            if user_exists(reg_user):
                st.error("Username already exists.")
            elif reg_user.strip() == "" or reg_pass.strip() == "":
                st.error("Username and password cannot be empty.")
            else:
                save_user(reg_user, reg_pass)
                st.success("Registration successful! Please log in.")
else:
    name = st.session_state["username"]
    user_id = str(uuid.uuid4())  # Generate a unique user ID
    prayer_db = PrayerDB(f"{name}_{user_id}")

    st.title("🕌 Prayer Tracker")
    st.header("Keep Track of your **Prayers** 🗓️")

    current_date = f"{datetime.now().year}-{datetime.now().month}-{datetime.now().day}"

    Prayer_names = ["alFajr", "alZuhr", "alAsr", "alMaghreb", "alEshaa"]


    def get():
        calc_method = 'egypt'
        school = "Hanafi"
        midnightMode = "Standard"
        latitudeAdjustmentMethod = "one seventh"
        fajr_angle = 19.5
        isha_angle = 17.5

        calc = PrayerTimesCalculator(
            latitude=30.0626,
            longitude=31.2497,
            calculation_method=calc_method,
            date=current_date,
            school=school,
            midnightMode=midnightMode,
            latitudeAdjustmentMethod=latitudeAdjustmentMethod,
            fajr_angle=fajr_angle,
            # maghrib_angle=maghrib_angle,
            isha_angle=isha_angle,
            iso8601=False
        )

        
        times = calc.fetch_prayer_times()
        return times

    # --- Calendar View ---
    today = date.today()
    selected_month = st.selectbox("Month", list(calendar.month_name)[1:], index=today.month-1)
    selected_day = st.number_input("Day", min_value=1, max_value=31, value=today.day, step=1)
    month_idx = list(calendar.month_name).index(selected_month)
    selected_date = date(today.year, month_idx, selected_day)
    key = selected_date.strftime("%Y-%m-%d")
    prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

    # Load prayer status from DB
    prayer_status = prayer_db.get_status_for_date(key)
    if not prayer_status:
        prayer_status = {p: False for p in prayers}

    st.write(f"## {selected_date.strftime('%A, %B %d, %Y')}")

    updated_status = {}
    for p in prayers:
        checked = st.checkbox(p, value=prayer_status.get(p, False), key=f"{key}_{p}")
        updated_status[p] = checked

    # Save to DB if changed
    if updated_status != prayer_status:
        prayer_db.set_status_for_date(key, updated_status)

    if all(updated_status[p] for p in prayers):
        st.success(f"All prayers completed for this day! 🎉")
        st.balloons()
    elif any(updated_status[p] for p in prayers):
        st.info("Some prayers completed for this day.")
    else:
        st.warning("No prayers completed for this day.")

    st.divider()
    st.header("Prayer Times")

    prayer_times = get()

    prayer_times_list = [
        prayer_times['Fajr'],
        prayer_times['Dhuhr'],
        prayer_times['Asr'],
        prayer_times['Maghrib'],
        prayer_times['Isha']
    ]

    prayers_dict = {
        "Prayer": Prayer_names,
        "Time" : prayer_times_list
    }

    with st.container(border=True):
        st.markdown(f"**{prayers_dict['Prayer'][0]}**  :   {prayers_dict['Time'][0]}")
        st.markdown(f"**{prayers_dict['Prayer'][1]}**  :   {prayers_dict['Time'][1]}")
        st.markdown(f"**{prayers_dict['Prayer'][2]}**  :   {prayers_dict['Time'][2]}")
        st.markdown(f"**{prayers_dict['Prayer'][3]}**  :   {prayers_dict['Time'][3]}")
        st.markdown(f"**{prayers_dict['Prayer'][4]}**  :   {prayers_dict['Time'][4]}")

    st.markdown(
        "<p style='color:gray;  font-size:0.9em;'>note That the prayer times aren't specific and we're Working to improve it</p>",
        unsafe_allow_html=True
    )

    st.divider()
    st.header("Info")
    st.markdown("**Developer**: ***Adam*** ")
    st.write(f"")

    st.markdown(
        "<p style='color:gray; text-align:center; font-size:0.9em;'>© 2025 Adam's Prayer App. All rights reserved.</p>",
        unsafe_allow_html=True
    )

    # At the end of the script, close DB connection
    prayer_db.close()

