import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIG ---
st.set_page_config(page_title="Flood Tracker", layout="wide")
st.title("Grafton River Level Monitor")

# --- PROFESSIONAL DATA PARSER ---
@st.cache_data(ttl=600)
def get_river_data():
    # Using a broader API request to catch current telemetry
    session = requests.Session()
    session.headers.update({"User-Agent": "FloodTracker/1.0"})
    
    urls = {
        "Upper": "https://api.water.noaa.gov/nwps/v1/gauges/GRFI2/stageflow",
        "Tail": "https://api.water.noaa.gov/nwps/v1/gauges/ALNI2/stageflow"
    }
    
    dfs = {}
    for name, url in urls.items():
        response = session.get(url, timeout=10).json()
        # Direct pathing to observed data
        obs = response.get('observed', {}).get('data', [])
        df = pd.DataFrame(obs)
        
        # Ensure correct column selection
        if 'validTime' in df.columns and 'stage' in df.columns:
            df = df[['validTime', 'stage']].copy()
            df['validTime'] = pd.to_datetime(df['validTime'])
            df['stage'] = pd.to_numeric(df['stage'])
            dfs[name] = df.sort_values('validTime')
        else:
            # Fallback if structure is missing
            raise KeyError(f"Data feed {name} structure unexpected.")
            
    return dfs['Upper'], dfs['Tail']

# --- APP EXECUTION ---
try:
    df_upper, df_tail = get_river_data()
    
    # Latest readings
    u_val = df_upper['stage'].iloc[-1]
    t_val = df_tail['stage'].iloc[-1]
    diff = abs(u_val - t_val)

    # Status Dashboard
    st.metric("System Head Differential", f"{diff:.2f} FT")
    
    col1, col2 = st.columns(2)
    col1.metric("Upper Pool", f"{u_val:.2f} FT")
    col2.metric("Tailwater", f"{t_val:.2f} FT")

    # Charting
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(df_upper['validTime'], df_upper['stage'], label='Upper', color='#2196F3')
    ax.plot(df_tail['validTime'], df_tail['stage'], label='Tail', color='#4CAF50')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig)

except Exception as e:
    st.error("System synchronization issue.")
    st.write(f"Diagnostic: {e}")
