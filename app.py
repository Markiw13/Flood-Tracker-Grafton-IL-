import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIG ---
st.set_page_config(page_title="River Monitor", layout="centered")
st.title("River Level Monitor")

@st.cache_data(ttl=600)
def fetch_data():
    headers = {"User-Agent": "Mozilla/5.0"}
    urls = {
        "upper": "https://api.water.noaa.gov/nwps/v1/gauges/GRFI2/stageflow",
        "lower": "https://api.water.noaa.gov/nwps/v1/gauges/ALNI2/stageflow"
    }
    data_frames = {}
    for name, url in urls.items():
        res = requests.get(url, headers=headers, timeout=10).json()
        raw = res.get('observed', {}).get('data', [])
        df = pd.DataFrame(raw)
        
        # DYNAMIC FINDER: Look for time and stage columns regardless of specific name
        time_col = next((c for c in df.columns if 'time' in c.lower()), None)
        stage_col = next((c for c in df.columns if 'stage' in c.lower()), None)
        
        if time_col and stage_col:
            df = df[[time_col, stage_col]].rename(columns={time_col: 'time', stage_col: 'stage'})
            df['time'] = pd.to_datetime(df['time'])
            df['stage'] = pd.to_numeric(df['stage'], errors='coerce')
            data_frames[name] = df.dropna()
        else:
            raise ValueError(f"Could not find time/stage data in {name} feed")
            
    return data_frames['upper'], data_frames['lower']

# --- MAIN ---
try:
    df_up, df_down = fetch_data()
    up_val = df_up['stage'].iloc[-1]
    down_val = df_down['stage'].iloc[-1]
    diff = abs(up_val - down_val)

    # Status
    if diff <= 0.75:
        st.error(f"🚨 OPEN RIVER (Diff: {diff:.2f} FT)")
    else:
        st.success(f"🔒 CONTROLLED POOL (Diff: {diff:.2f} FT)")

    col1, col2, col3 = st.columns(3)
    col1.metric("Upper", f"{up_val:.2f} FT")
    col2.metric("Tail", f"{down_val:.2f} FT")
    col3.metric("Drop", f"{diff:.2f} FT")

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#0e1117')
    ax.plot(df_up['time'], df_up['stage'], label='Upper', color='#51afef')
    ax.plot(df_down['time'], df_down['stage'], label='Tail', color='#98c379')
    ax.tick_params(colors='white')
    ax.legend(facecolor='#0e1117', labelcolor='white')
    st.pyplot(fig)

except Exception as e:
    st.error("Data structure changed. Attempting recovery...")
    st.write(f"Log: {e}")
