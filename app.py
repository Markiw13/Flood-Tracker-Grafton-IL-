import streamlit as st
import requests

st.set_page_config(page_title="Grafton River Monitor", layout="centered")
st.title("Grafton River Level Monitor")

# OFFICIAL NWPS GAUGE ENDPOINTS
# NWPS uses these paths for observation data
GAUGES = {
    "Upper": "GRFI2",
    "Tail": "ALNI2"
}

def get_nwps_data(gauge_id):
    # The official NWPS endpoint for gauge observations
    url = f"https://api.water.noaa.gov/nwps/v1/gauges/{gauge_id}/stageflow"
    try:
        # User-Agent is required by NOAA for their new API
        headers = {"User-Agent": "RiverMonitor/2.0"}
        response = requests.get(url, headers=headers, timeout=10).json()
        
        # Modern NWPS schema: 'observed' -> 'data' -> latest entry
        # We look for the most recent record
        data = response.get('observed', {}).get('data', [])
        if data:
            # The modern API returns the latest entry at the end of the list
            latest = data[-1]
            return float(latest.get('stage', 0))
    except Exception as e:
        st.error(f"API Error: {e}")
    return None

up_val = get_nwps_data(GAUGES["Upper"])
down_val = get_nwps_data(GAUGES["Tail"])

if up_val is not None and down_val is not None:
    diff = abs(up_val - down_val)
    st.metric("Head Differential", f"{diff:.2f} FT")
    col1, col2 = st.columns(2)
    col1.metric("Upper Pool", f"{up_val:.2f} FT")
    col2.metric("Tailwater", f"{down_val:.2f} FT")
else:
    st.error("Unable to retrieve data from the NWPS service. The gauge may be offline.")
