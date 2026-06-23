import streamlit as st
import requests

# Page setup
st.set_page_config(page_title="Grafton River Monitor")
st.title("Grafton River Level Monitor")

# Function to get stage
def get_level(url):
    try:
        response = requests.get(url, timeout=5).json()
        # Direct access to the observation list
        return response['observed']['data'][-1]['stage']
    except Exception as e:
        return None

# Get readings
up = get_level("https://api.water.noaa.gov/nwps/v1/gauges/GRFI2/stageflow")
down = get_level("https://api.water.noaa.gov/nwps/v1/gauges/ALNI2/stageflow")

# Display
if up is not None and down is not None:
    st.metric("Upper Pool", f"{up} FT")
    st.metric("Tailwater", f"{down} FT")
    st.metric("Drop", f"{abs(float(up) - float(down)):.2f} FT")
else:
    st.error("NOAA API connection failed. The endpoints may have changed.")
