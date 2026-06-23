import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="River Monitor", layout="centered")
st.title("Grafton River Level Monitor")

def get_latest(url):
    try:
        data = requests.get(url, timeout=5).json()
        # Navigate the JSON safely
        obs = data.get('observed', {}).get('data', [])
        if not obs: return None
        # Return the last item
        return obs[-1]
    except:
        return None

# Fetch raw data
upper = get_latest("https://api.water.noaa.gov/nwps/v1/gauges/GRFI2/stageflow")
tail = get_latest("https://api.water.noaa.gov/nwps/v1/gauges/ALNI2/stageflow")

if upper and tail:
    u_val = float(upper.get('stage', 0))
    t_val = float(tail.get('stage', 0))
    diff = abs(u_val - t_val)

    st.metric("Head Differential", f"{diff:.2f} FT")
    col1, col2 = st.columns(2)
    col1.metric("Upper Pool", f"{u_val:.2f} FT")
    col2.metric("Tailwater", f"{t_val:.2f} FT")
else:
    st.error("API is currently returning empty data. Check back in a few minutes.")
