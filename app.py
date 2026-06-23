import streamlit as st
import requests
import time
import pandas as pd
import plotly.graph_objects as go

# --- 1. CORE APPLICATION CONFIG ---
st.set_page_config(page_title="River Level Monitor", layout="centered")

UPSTREAM_URL = "https://api.water.noaa.gov/nwps/v1/gauges/GRFI2/stageflow"   
DOWNSTREAM_URL = "https://api.water.noaa.gov/nwps/v1/gauges/ALNI2/stageflow" 

# --- 2. TELEMETRY FETCH & HISTORICAL TIMELINE PARSING ---
upper_pool_ft = 18.83  
tailwater_ft = 18.21  
is_open_river = True
df_history = pd.DataFrame()

try:
    headers = {"User-Agent": "Mozilla/5.0 TerminalMonitor/16.0"}
    
    # Fetch 7-day raw data streams from the server
    up_res = requests.get(UPSTREAM_URL, headers=headers, timeout=5).json()
    up_data = up_res.get('observed', {}).get('data', [])
    
    down_res = requests.get(DOWNSTREAM_URL, headers=headers, timeout=5).json()
    down_data = down_res.get('observed', {}).get('data', [])

    if up_data and down_data:
        up_valid = [e for e in up_data if e.get('stage') is not None]
        down_valid = [e for e in down_data if e.get('stage') is not None]
        
        if up_valid and down_valid:
            upper_pool_ft = float(up_valid[-1]['stage'])
            tailwater_ft = float(down_valid[-1]['stage'])

        # Align timelines together
        up_hist = {e['validTime']: float(e['stage']) for e in up_data if e.get('stage') is not None}
        down_hist = {e['validTime']: float(e['stage']) for e in down_data if e.get('stage') is not None}
        
        common_times = sorted(list(set(up_hist.keys()) & set(down_hist.keys())))
        
        timeline_records = []
        for t in common_times:
            timeline_records.append({
                "DateTime": pd.to_datetime(t),
                "Upper Pool": up_hist[t],
                "Tailwater": down_hist[t]
            })
            
        if timeline_records:
            df_history = pd.DataFrame(timeline_records).sort_values("DateTime")

    head_differential = abs(upper_pool_ft - tailwater_ft)
    is_open_river = True if head_differential <= 0.75 else False

except Exception:
    head_differential = abs(upper_pool_ft - tailwater_ft)
    is_open_river = True if head_differential <= 0.75 else False

# --- 3. SYSTEM STATUS BANNER ---
if is_open_river:
    st.error(f"🚨 **SYSTEM STATUS: OPEN RIVER FLOW** (Differential: {head_differential:.2f} FT)\n\nPools have equalized. Submersible dam gates are pulled completely clear of the river channel.")
else:
    st.success(f"🔒 **SYSTEM STATUS: CONTROLLED POOL** (Differential: {head_differential:.2f} FT)\n\nControlled operation active. Submerged gates are holding back pool depth.")

# --- 4. TELEMETRY METRICS MATRIX ---
col1, col2, col3 = st.columns(3)
col1.metric(label="Upper Pool (Grafton)", value=f"{upper_pool_ft:.2f} FT")
col2.metric(label="Tailwater (Dam Site)", value=f"{tailwater_ft:.2f} FT")
col3.metric(label="Head Drop", value=f"{head_differential:.2f} FT")

st.markdown("---")

# --- 5. HIGH-CONTRAST HISTORICAL GHOST CHART ---
if not df_history.empty:
    fig = go.Figure()

    # A. Shadowed Historical Lines (Faded, thin gray-toned profiles over 7 days)
    fig.add_trace(go.Scatter(
        x=df_history["DateTime"], y=df_history["Upper Pool"],
        mode='lines', name='Upper Pool History',
        line=dict(color='rgba(81, 175, 239, 0.20)', width=1.5)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_history["DateTime"], y=df_history["Tailwater"],
        mode='lines', name='Tailwater History',
        line=dict(color='rgba(152, 195, 121, 0.20)', width=1.5)
    ))

    # B. Live Current Data Points (Bold, solid lines with high-contrast final markers)
    fig.add_trace(go.Scatter(
        x=[df_history["DateTime"].iloc[-1]], y=[upper_pool_ft],
        mode='markers+text', name='Current Upper Pool',
        marker=dict(color='#51afef', size=10, line=dict(color='#ffffff', width=1.5)),
        text=[f"<b>{upper_pool_ft:.2f} FT</b>"], textposition="top center"
    ))
    
    fig.add_trace(go.Scatter(
        x=[df_history["DateTime"].iloc[-1]], y=[tailwater_ft],
        mode='markers+text', name='Current Tailwater',
        marker=dict(color='#98c379', size=10, line=dict(color='#ffffff', width=1.5)),
        text=[f"<b>{tailwater_ft:.2f} FT</b>"], textposition="bottom center"
    ))

    # Clean Dark Industrial Slate Theme Configurations
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=20, b=10),
        height=400,
        showlegend=False,
        hovermode="x unified",
        xaxis=dict(showgrid=True, gridcolor='#22252a', zeroline=False, title=None),
        yaxis=dict(showgrid=True, gridcolor='#22252a', zeroline=False, title="Stage Depth (FT)")
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown("---")

# Automatic update execution interval routine (15 minutes)
time.sleep(900)
st.rerun()
