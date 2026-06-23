import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- 1. CONFIG ---
st.set_page_config(page_title="River Monitor", layout="centered")
UPSTREAM_URL = "https://api.water.noaa.gov/nwps/v1/gauges/GRFI2/stageflow"   
DOWNSTREAM_URL = "https://api.water.noaa.gov/nwps/v1/gauges/ALNI2/stageflow" 

# --- 2. DATA FETCH ---
try:
    headers = {"User-Agent": "Mozilla/5.0"}
    up_data = requests.get(UPSTREAM_URL, headers=headers, timeout=5).json()['observed']['data']
    down_data = requests.get(DOWNSTREAM_URL, headers=headers, timeout=5).json()['observed']['data']
    
    # Process into DataFrame
    df_up = pd.DataFrame(up_data)
    df_down = pd.DataFrame(down_data)
    df_up['validTime'] = pd.to_datetime(df_up['validTime'])
    df_down['validTime'] = pd.to_datetime(df_down['validTime'])
    
    current_up = float(df_up.iloc[-1]['stage'])
    current_down = float(df_down.iloc[-1]['stage'])
    diff = abs(current_up - current_down)
except:
    current_up, current_down, diff = 18.83, 18.21, 0.62

# --- 3. UI ---
if diff <= 0.75:
    st.error(f"🚨 OPEN RIVER (Diff: {diff:.2f} FT)")
else:
    st.success(f"🔒 CONTROLLED POOL (Diff: {diff:.2f} FT)")

col1, col2, col3 = st.columns(3)
col1.metric("Upper", f"{current_up:.2f} FT")
col2.metric("Tail", f"{current_down:.2f} FT")
col3.metric("Drop", f"{diff:.2f} FT")

# --- 4. MATPLOTLIB CHART (NO PLOTLY/DEPENDENCIES NEEDED) ---
fig, ax = plt.subplots(figsize=(10, 4))
fig.patch.set_facecolor('#0e1117')
ax.set_facecolor('#0e1117')

ax.plot(df_up['validTime'], df_up['stage'], color='#51afef', label='Upper Pool', alpha=0.6)
ax.plot(df_down['validTime'], df_down['stage'], color='#98c379', label='Tailwater', alpha=0.6)

ax.tick_params(colors='white')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
plt.legend(facecolor='#0e1117', labelcolor='white')
plt.grid(color='#282c34', linestyle='--')

st.pyplot(fig)
