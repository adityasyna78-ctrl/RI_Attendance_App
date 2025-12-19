import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz
from geopy.distance import geodesic
import pandas as pd

# --- CONFIGURATION ---
OFFICE_LOCATION = (22.723126709479242, 75.88450302733477)
ALLOWED_DISTANCE_METERS = 50
SHEET_URL = "https://docs.google.com/spreadsheets/d/1eNiLAHx6I8DlUxrVOyuC5DAl6QM77ISDMwRlyUSbjuc/edit?gid=0#gid=0"
EMPLOYEE_LIST = ["Amit Sharma", "Priya Singh", "Rajesh Kumar", "Suman Verma", "Vikram Rathore"]

# Timezone Setup
IST = pytz.timezone('Asia/Kolkata')
today_date = datetime.now(IST).strftime("%Y-%m-%d")

st.set_page_config(page_title="Attendance & Admin", layout="centered")

# 1. Sidebar for Navigation
mode = st.sidebar.selectbox("Choose Mode", ["Employee Check-in", "Daily Summary (Admin)"])

conn = st.connection("gsheets", type=GSheetsConnection)

if mode == "Employee Check-in":
    st.title("📍 Office Attendance")
    name = st.selectbox("Select your Name", ["Select Name"] + EMPLOYEE_LIST)
    action = st.radio("Select Action", ["Check-in", "Check-out"], horizontal=True)
    
    location = streamlit_geolocation()
    
    if location and name != "Select Name":
        user_pos = (location['latitude'], location['longitude'])
        distance = geodesic(user_pos, OFFICE_LOCATION).meters
        
        if st.button(f"Confirm {action}"):
            if distance <= ALLOWED_DISTANCE_METERS:
                # Logic for status
                current_time = datetime.now(IST)
                current_hour = current_time.hour
                status = "Present"
                if action == "Check-in" and current_hour >= 11:
                    status = "Half Day (Late)"
                elif action == "Check-out" and current_hour < 17:
                    status = "Half Day (Early)"

                new_entry = pd.DataFrame([{
                    "Name": name, "Action": action, 
                    "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Date": today_date, "Status": status
                }])
                
                # Update Sheet
                existing_df = conn.read(spreadsheet=SHEET_URL)
                updated_df = pd.concat([existing_df, new_entry], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                st.success("Attendance Recorded!")
            else:
                st.error(f"Too far! ({round(distance)}m)")

# --- STEP 2: THE DAILY SUMMARY SCRIPT ---
elif mode == "Daily Summary (Admin)":
    st.title("📊 Daily Attendance Summary")
    st.write(f"Date: {today_date}")

    # Read current logs
    df = conn.read(spreadsheet=SHEET_URL)
    
    # Filter only for today's entries
    today_df = df[df['Date'] == today_date]
    
    # Get unique names who checked in today
    checked_in_names = today_df[today_df['Action'] == 'Check-in']['Name'].unique()
    
    # Calculate Absentees
    absentees = [emp for emp in EMPLOYEE_LIST if emp not in checked_in_names]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Employees", len(EMPLOYEE_LIST))
        st.success(f"Present: {len(checked_in_names)}")
    with col2:
        st.error(f"Absent: {len(absentees)}")

    if absentees:
        st.subheader("❌ List of Absentees")
        for person in absentees:
            st.write(f"- {person}")
    else:
        st.success("Everyone is present today!")
        
    st.subheader("Today's Detailed Logs")
    st.dataframe(today_df)

