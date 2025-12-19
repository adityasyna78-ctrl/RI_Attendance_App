import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from geopy.distance import geodesic
import pandas as pd

# --- CONFIGURATION ---
OFFICE_LOCATION = (22.723126709479242, 75.88450302733477)
ALLOWED_DISTANCE_METERS = 50  # Updated to 50 meters
SHEET_URL = "https://docs.google.com/spreadsheets/d/1eNiLAHx6I8DlUxrVOyuC5DAl6QM77ISDMwRlyUSbjuc/edit?usp=sharing"

# List of employees
EMPLOYEES = ["Select Name", "Amit Sharma", "Priya Singh", "Rajesh Kumar", "Suman Verma"]

st.set_page_config(page_title="Recovered India Attendance", page_icon="📍")
st.title("📍 RI Attendance System")

# 1. Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Employee Selection
name = st.selectbox("Select your Name", EMPLOYEES)

# 3. Action Selection
action = st.radio("Select Action", ["Check-in", "Check-out"], horizontal=True)

# 4. Geolocation Component
st.info("Click the button below to verify your location:")
location = streamlit_geolocation()

if location and name != "Select Name":
    user_pos = (location['latitude'], location['longitude'])
    
    # Calculate distance
    distance = geodesic(user_pos, OFFICE_LOCATION).meters
    
    # Visual feedback for the user
    if distance <= ALLOWED_DISTANCE_METERS:
        st.success(f"You are on-site! (Distance: {round(distance, 1)} meters)")
    else:
        st.warning(f"You are currently {round(distance, 1)} meters away. Please move closer to the office (within 50m).")
    
    if st.button(f"Confirm {action}"):
        if distance <= ALLOWED_DISTANCE_METERS:
            # Prepare the log entry
            new_data = pd.DataFrame([{
                "Name": name,
                "Action": action,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Distance_Meters": round(distance, 2),
                "Status": "Success"
            }])
            
            # Read and Update Google Sheet
            try:
                existing_data = conn.read(spreadsheet=SHEET_URL)
                updated_df = pd.concat([existing_data, new_data], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                
                st.success(f"✅ {action} recorded for {name}!")
                st.balloons()
            except Exception as e:
                st.error("Error saving to Google Sheets. Check your secrets/permissions.")
        else:
            st.error(f"❌ Outside Range: {round(distance)}m is beyond the 50m limit.")

elif name == "Select Name":
    st.warning("Please select your name from the dropdown list.")

