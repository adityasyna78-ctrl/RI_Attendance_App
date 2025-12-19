import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from math import geodesic

# --- CONFIGURATION ---
# Replace these with your business's actual coordinates
BUSINESS_LOCATION = (40.7128, -74.0060)  # Example: New York City
ALLOWED_DISTANCE_METERS = 100

st.title("📍 Business Attendance System")
st.subheader("Ensure you are on-site to check in.")

# --- GEOLOCATION COMPONENT ---
location = streamlit_geolocation()

if location:
    user_lat = location['latitude']
    user_lon = location['longitude']
    user_pos = (user_lat, user_lon)

    st.write(f"Your current coordinates: {user_lat}, {user_lon}")

    # Calculate distance to business
    distance = geodesic(user_pos, BUSINESS_LOCATION).meters

    if st.button("Submit Attendance"):
        if distance <= ALLOWED_DISTANCE_METERS:
            st.success("✅ Check-in Successful! You are within range.")
            # Here you would typically save to a database or Google Sheet
        else:
            st.error(f"❌ Check-in Failed. You are {round(distance)}m away.")
else:
    st.info("Please allow location access and click the 'Get Location' button above.")