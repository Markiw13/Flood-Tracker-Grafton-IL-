import streamlit as st
import requests

# Set page config
st.set_page_config(page_title="River Level Monitor", layout="centered")
st.title("Grafton River Level Monitor")

# Function to fetch data safely
def get_nwps_data(gauge_id):
    # Official NWPS API endpoint
    url = f"https://api.water.noaa.gov/nwps/v1/gauges/{gauge_id}/stageflow"
    headers = {"User-Agent": "RiverMonitor/2.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Check if request was successful
        if response.status_code != 200:
            st.error(f"API returned status {response.status_code}")
            return None
            
        data = response.json()
        
        # Defensive navigation of JSON:
        # Looking for 'observed' -> 'data' list
        observed = data.get('observed', {})
        entries = observed.get('data', [])
        
        if not entries:
            st.warning(f"No observed data found for gauge {gauge_id}")
            return None
            
        # Get the latest entry
        latest = entries[-1]
        
        # Check for 'stage' key, if not found return None but show raw entry for debug
        stage = latest.get('stage')
        if stage is None:
            st.error(f"Gauge {gauge_id} data entry missing 'stage' key: {latest}")
            return None
            
        return float(stage)
        
    except Exception as e:
        st.error(f"Fetch error for {gauge_id}: {str(e)}")
        return None

# Fetch data for both gauges
up_val = get_nwps_data("GRFI2")
down_val = get_nwps_data("ALNI2")

# Display results if available
if up_val is not None and down_val is not None:
    diff = abs(up_val - down_val)
    st.metric("Head Differential", f"{diff:.2f} FT")
    
    col1, col2 = st.columns(2)
    col1.metric("Upper Pool", f"{up_val:.2f} FT")
    col2.metric("Tailwater", f"{down_val:.2f} FT")
else:
    st.info("Waiting for valid data from NOAA API...")
