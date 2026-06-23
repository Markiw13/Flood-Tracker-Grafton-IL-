import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="River Monitor", layout="centered")
st.title("River Level Monitor")

# --- 2. DATA FETCH & CLEANING ---
@st.cache_data(ttl=900) # Caches the data for 15 minutes to improve speed
def get_river_data():
    headers = {"User-Agent": "Mozilla/5.0"}
    urls = {
        "upper": "https://api.water.noaa.gov/nwps/v1/gauges/GRFI2/stageflow",
        "lower": "https://api.water.noaa.gov/nwps/v1/gauges/ALNI2/stageflow"
    }
    
    results = {}
    for name, url in urls.items():
        res = requests.get(url, headers=headers, timeout=10).json()
        # Extract only data with 'stage' key
        data = [e for e in res['observed']['data'] if 'stage' in e]
        df = pd.DataFrame(data)
        df['validTime'] = pd.to_datetime(df['validTime'])
        df['stage'] = df['stage'].astype(float)
        results[name] = df
    return results['upper'], results['lower']

# --- 3. MAIN APP LOGIC ---
try:
    df_up, df_down = get_river_data()
    
    current_up = df_up.iloc[-1]['stage']
    current_down = df_down.iloc[-1]['stage']
    diff = abs(current_up - current_down)

    # Status Banner
    if diff <= 0.75:
        st.error(f"🚨 OPEN RIVER (Diff: {diff:.2f} FT)")
    else:
        st.success(f"🔒 CONTROLLED POOL (Diff: {diff:.2f} FT)")

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Upper", f"{current_up:.2f} FT")
    col2.metric("Tail", f"{current_down:.2f} FT")
    col3.metric("Drop", f"{diff:.2f} FT")

    # Charting
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#0e1117')
    
    ax.plot(df_up['validTime'], df_up['stage'], color='#51afef', label='Upper Pool', linewidth=2)
    ax.plot(df_down['validTime'], df_down['stage'], color='#98c379', label='Tailwater', linewidth=2)
    
    ax.tick_params(colors='white')
    ax.grid(color='#282c34', linestyle='--')
    ax.legend(facecolor='#0e1117', labelcolor='white')
    
    st.pyplot(fig)

except Exception as e:
    st.error("Error retrieving river data. Please try again in a moment.")
    st.caption(f"Details: {e}")
