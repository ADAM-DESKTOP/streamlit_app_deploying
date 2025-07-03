import streamlit as st
from datetime import date
import geocoder
import calendar
import json
import os
import calendar
from datetime import datetime
from datetime import date
import json
import os
from prayer_times_calculator import PrayerTimesCalculator


import streamlit as st

st.markdown("""
    <style>
    body {
        background-color: #220929;
        color: #ffffff;
    }

    button, .stButton>button {
        background-color: #d19e53;
        color: #000000;
        border: none;
        border-radius: 6px;
    }

    button:hover, .stButton>button:hover {
        background-color: #b8843f;
        color: #ffffff;
    }

    h1, h2, h3, h4 {
        color: #d19e53;
    }

    a {
        color: #d19e53;
    }
    </style>
""", unsafe_allow_html=True)

# --- Persistent storage for prayer status ---
DATA_FILE = "prayer_status.json"

def load_prayer_status():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_prayer_status(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

st.title("🕌 Prayer Tracker")

prayer_status = load_prayer_status()

# --- UI: Menu Bar ---
st.header("Keep Track of your **Prayers** 🗓️")

current_date = f"{datetime.now().year}-{datetime.now().month}-{datetime.now().day}"


Prayer_names = ["alFajr", "alZuhr", "alAsr", "alMaghreb", "alEshaa"]

# Get user's approximate location by IP
g = geocoder.ip('me')
lat, lng = g.latlng
country = g.country

def get():
    # required parameters

    calc_method = 'isna'
    school = "Hanafi"
    midnightMode = "Standard"
    latitudeAdjustmentMethod = "one seventh"
    tune = False
    imsak_tune = 0
    fajr_tune = 0
    sunrise_tune = 0
    dhuhr_tune = 0
    asr_tune = 0
    maghrib_tune = 0
    sunset_tune = 0
    isha_tune = 0
    midnight_tune = 0
    fajr_angle = 19.5
    maghrib_angle = None
    isha_angle = 17.5

    calc = PrayerTimesCalculator(
        latitude=lat,
        longitude=lng,
        calculation_method=calc_method,
        date=current_date,
        school=school,
        midnightMode=midnightMode,
        latitudeAdjustmentMethod=latitudeAdjustmentMethod,
        tune=tune,
        imsak_tune=imsak_tune,
        fajr_tune=fajr_tune,
        sunrise_tune=sunrise_tune,
        dhuhr_tune=dhuhr_tune,
        asr_tune=asr_tune,
        maghrib_tune=maghrib_tune,
        sunset_tune=sunset_tune,
        isha_tune=isha_tune,
        fajr_angle=fajr_angle,
        maghrib_angle=maghrib_angle,
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
month_days = calendar.monthcalendar(selected_day, month_idx)

prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]




# --- Day Details and Prayer Checkboxes ---
selected_day = st.session_state.get("selected_day", today.day if today.month == month_idx and today.day == selected_day else 1)
selected_date = date(selected_day, month_idx, selected_day)
key = selected_date.strftime("%m-%d")
st.write(f"## {current_date}")

if key not in prayer_status:
    prayer_status[key] = {p: False for p in prayers}

for p in prayers:
    checked = st.checkbox(p, value=prayer_status[key][p], key=f"{key}_{p}", value=False)
    prayer_status[key][p] = checked

save_prayer_status(prayer_status)

if all(prayer_status[key][p] for p in prayers):
    st.success("All prayers completed for this day! 🎉")
    st.balloons()
elif any(prayer_status[key][p] for p in prayers):
    st.info("Some prayers completed for this day.")
else:
    st.warning("No prayers completed for this day.")


# Streamlit UI feedback



# Fetch prayer times and display them in a table
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
st.write(f"🗺️ Detected Location: ({country})")

st.markdown(
    "<p style='color:gray; text-align:center; font-size:0.9em;'>© 2025 Adam's Prayer App. All rights reserved.</p>",
    unsafe_allow_html=True
)
