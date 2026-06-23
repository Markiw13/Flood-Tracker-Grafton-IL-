import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Set page layout
st.set_page_config(page_title="River Monitor", layout="centered")

st.title("River Level Monitor")

# --- DATA FETCH WITH ROBUST ERROR HANDLING ---
try:
    headers = {"User-Agent": "Mozilla/5.0"}
    # Fetch data
    up_res = requests.get("https://api.water.noaa.gov/nwps/v1/gauges/GRFI2/stageflow", headers=headers, timeout=10)
    down_res = requests.get("https://api.water.noaa.gov/nwps/v1/gauges/ALNI2/stageflow", headers=headers, timeout=10)
    
    up_data = up_res.json()['observed']['data']
    down_data = down_res.json()['observed']['data']
    
    df_up = pd.DataFrame(up_data)
    df_down = pd.DataFrame(down_data)
    df_up['validTime'] = pd.to_datetime(df_up['validTime'])
    df_down['validTime'] = pd.to_datetime(df_down['validTime'])
    
    current_up = float(df_up.iloc[-1]['stage'])
    current_down = float(df_down.iloc[-1]['stage'])
    diff = abs(current_up - current_down)
    
    # --- UI RENDERING ---
    if diff <= 0.75:
        st.error(f"🚨 OPEN RIVER (Diff: {diff:.2f} FT)")
    else:
        st.success(f"🔒 CONTROLLED POOL (Diff: {diff:.2f} FT)")

    col1, col2, col3 = st.columns(3)
    col1.metric("Upper", f"{current_up:.2f} FT")
    col2.metric("Tail", f"{current_down:.2f} FT")
    col3.metric("Drop", f"{diff:.2f} FT")

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#0e1117')
    ax.plot(df_up['validTime'], df_up['stage'], color='#51afef', label='Upper Pool')
    ax.plot(df_down['validTime'], df_down['stage'], color='#98c379', label='Tailwater')
    ax.tick_params(colors='white')
    st.pyplot(fig)

except Exception as e:
    st.error(f"Failed to load data. The API might be down or unreachable.")
    st.write(f"Technical error: {e}")
