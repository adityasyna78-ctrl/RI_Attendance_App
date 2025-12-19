import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz  # Handles IST timezone
from geopy.distance import geodesic
import pandas as pd

# --- CONFIGURATION ---
OFFICE_LOCATION = (22.723126709479242, 75.88450302733477)
ALLOWED_DISTANCE_METERS = 50
SHEET_URL = "https://docs.google.com/spreadsheets/d/1eNiLAHx6I8DlUxrVOyuC5DAl6QM77ISDMwRlyUSbjuc/edit?usp=sharing"
EMPLOYEES = ["Select Name", "Amit Sharma", "Priya Singh", "Rajesh Kumar", "Suman Verma"]

st.set_page_config(page_title="Office Attendance", page_icon="📍")
st.title("📍 Office Attendance System")

# 1. Timezone Setup (IST)
IST = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(IST)
current_hour = current_time.hour

# 2. Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

name = st.selectbox("Select your Name", EMPLOYEES)
action = st.radio("Select Action", ["Check-in", "Check-out"], horizontal=True)

st.info("Capture your location to proceed:")
location = streamlit_geolocation()

if location and name != "Select Name":
    user_pos = (location['latitude'], location['longitude'])
    distance = geodesic(user_pos, OFFICE_LOCATION).meters
    
    if st.button(f"Confirm {action}"):
        if distance <= ALLOWED_DISTANCE_METERS:
            # --- LOGIC FOR HALF DAY ---
            status = "Present"
            
            if action == "Check-in":
                # If Check-in is 11:00 AM or later
                if current_hour >= 11:
                    status = "Half Day (Late In)"
            
            elif action == "Check-out":
                # If Check-out is before 5:00 PM (17:00)
                if current_hour < 17:
                    status = "Half Day (Early Out)"

            # Prepare Data
            new_data = pd.DataFrame([{
                "Name": name,
                "Action": action,
                "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Distance_Meters": round(distance, 2),
                "Status": status
            }])
            
            try:
                existing_data = conn.read(spreadsheet=SHEET_URL)
                updated_df = pd.concat([existing_data, new_data], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                
                st.success(f"✅ {action} recorded as {status}!")
                st.balloons()
            except Exception as e:
                st.error("Error saving to Sheet. Check permissions.")
        else:
            st.error(f"❌ You are {round(distance)}m away. Move within 50m.")

