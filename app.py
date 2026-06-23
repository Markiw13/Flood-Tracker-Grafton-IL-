import streamlit as st
import requests
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Grafton River Level Monitor", layout="wide")
st.title("Grafton River Level Monitor")

@st.cache_data(ttl=600)
def get_river_data(gauge_id):
    url = f"https://api.water.noaa.gov/nwps/v1/gauges/{gauge_id}/stageflow"
    headers = {"User-Agent": "RiverMonitor/2.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10).json()
        data = response.get('observed', {}).get('data', [])
        # Create a clean DataFrame
        df = pd.DataFrame(data)
        # Ensure we have the data we need (primary is the new stage)
        if 'primary' in df.columns:
            df['primary'] = pd.to_numeric(df['primary'], errors='coerce')
            df['validTime'] = pd.to_datetime(df['validTime'])
            return df.dropna(subset=['primary'])
        return None
    except:
        return None

# Fetch data
df_up = get_river_data("GRFI2")
df_down = get_river_data("ALNI2")

if df_up is not None and df_down is not None:
    u_val = df_up['primary'].iloc[-1]
    d_val = df_down['primary'].iloc[-1]
    diff = abs(u_val - d_val)

    # Metrics Row
    c1, c2, c3 = st.columns(3)
    c1.metric("Head Differential", f"{diff:.2f} FT")
    c2.metric("Upper Pool", f"{u_val:.2f} FT")
    c3.metric("Tailwater", f"{d_val:.2f} FT")

    # Chart
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(df_up['validTime'], df_up['primary'], label='Upper', color='#2196F3')
    ax.plot(df_down['validTime'], df_down['primary'], label='Tail', color='#4CAF50')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig)
else:
    st.error("Data currently missing from NOAA source.")
