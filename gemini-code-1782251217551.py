import streamlit as st
import requests

st.title("Melvin Price Dam Gate Status Monitor")
st.subheader("Grafton Gauge Tracking (GRFI2)")

# Embed the live NOAA hydrograph directly into your app interface
st.image("https://water.noaa.gov/resources/hydrographs/grfi2_hg.png", 
         caption="Live Dynamic NOAA Hydrograph Feed")

# Fetch live number
API_URL = "https://api.water.noaa.gov/v1/gauges/GRFI2/stage/observed"
try:
    res = requests.get(API_URL, timeout=5).json()
    current_ft = float(res['data'][0]['value'])
    
    st.metric(label="Current Stage at Grafton", value=f"{current_ft} ft")
    
    if current_ft >= 18.5:
        st.error("🚨 FLOOD GATES DETECTED AS OPEN (Open River Flow)")
    else:
        st.success("🔒 FLOOD GATES CLOSED (Controlled Pool)")
except Exception:
    st.warning("Could not read digital data stream; check the hydrograph visual above.")