import streamlit as st
import requests

st.set_page_config(page_title="River Level", layout="centered")
st.title("Grafton River Level Monitor")

def fetch_safe(url):
    try:
        response = requests.get(url, timeout=10).json()
        # Navigate to the data list regardless of key names
        # Look for the last item in the first available list in the JSON
        data = response.get('observed', {}).get('data', [])
        if data:
            return data[-1].get('stage', 'N/A')
    except:
        pass
    return "N/A"

upper = fetch_safe("https://api.water.noaa.gov/nwps/v1/gauges/GRFI2/stageflow")
tail = fetch_safe("https://api.water.noaa.gov/nwps/v1/gauges/ALNI2/stageflow")

st.metric("Upper Pool", f"{upper} FT")
st.metric("Tailwater", f"{tail} FT")

if str(upper).replace('.','',1).isdigit() and str(tail).replace('.','',1).isdigit():
    diff = abs(float(upper) - float(tail))
    st.metric("Head Differential", f"{diff:.2f} FT")
else:
    st.warning("Data currently unavailable from NOAA.")
