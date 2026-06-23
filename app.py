import streamlit as st
import requests

st.set_page_config(page_title="River Level Monitor", layout="centered")
st.title("Grafton River Level Monitor")

def get_nwps_data(gauge_id):
    url = f"https://api.water.noaa.gov/nwps/v1/gauges/{gauge_id}/stageflow"
    headers = {"User-Agent": "RiverMonitor/2.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        # Look at the last entry in the observed data
        entries = data.get('observed', {}).get('data', [])
        if not entries:
            return None
            
        latest = entries[-1]
        
        # KEY FIX: The API is now using 'primary' instead of 'stage'
        value = latest.get('primary')
        
        # If 'primary' is -999, it means the gauge is currently not reporting a valid level
        if value is not None and float(value) > -900:
            return float(value)
        return None
        
    except Exception as e:
        return None

# Fetch data
up_val = get_nwps_data("GRFI2")
down_val = get_nwps_data("ALNI2")

# Display results
if up_val is not None and down_val is not None:
    diff = abs(up_val - down_val)
    st.metric("Head Differential", f"{diff:.2f} FT")
    
    col1, col2 = st.columns(2)
    col1.metric("Upper Pool", f"{up_val:.2f} FT")
    col2.metric("Tailwater", f"{down_val:.2f} FT")
else:
    st.warning("Data is currently reporting as invalid or the gauge is offline.")
