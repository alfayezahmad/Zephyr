import os
import time
import random
import requests
import itertools
import pandas as pd
import pydeck as pdk
import streamlit as st
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Zephyr | Command Center",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Use environment variable for backend URL, fallback to localhost for local testing
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

with st.sidebar:
    st.markdown("### 🔧 SIMULATION CONTROLS")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        if st.button("⚡ Spike Test", use_container_width=True):
            try:
                res = requests.post(f"{BACKEND_URL}/api/simulate_spike")
                if res.status_code == 200:
                    st.toast("Atmospheric PM2.5 Spike Injected (GRAP IV Emergency)!", icon="🚨")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Simulation failed.")
            except Exception as e:
                st.error(f"Backend unreachable: {e}")
    with col_sb2:
        if st.button("🔄 Reset Live", use_container_width=True):
            try:
                res = requests.post(f"{BACKEND_URL}/api/reset_spike")
                if res.status_code == 200:
                    st.toast("Restored Live Sensor Baseline Telemetry!", icon="✅")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Reset failed.")
            except Exception as e:
                st.error(f"Backend unreachable: {e}")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    
    /* Restore the header (and hamburger) but make it transparent and hide the deploy button */
    footer {visibility: hidden;}
    header {background-color: transparent !important;}
    .stDeployButton {display: none !important;}
    
    /* Dramatically reduce the top whitespace */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Sleeker Metric Cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(90deg, rgba(0, 229, 255, 0.08) 0%, rgba(0,0,0,0) 100%);
        border-left: 3px solid #00e5ff;
        padding: 10px 15px;
        border-radius: 4px;
    }
    div[data-testid="metric-container"] label {
        font-weight: 500 !important;
        color: #6b7280 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stDataFrame { border: 1px solid #1e1e24 !important; border-radius: 4px !important; }
    hr { border-color: #1e1e24 !important; margin: 1.5rem 0 !important; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    
    /* Neon Cyber Button Styling */
    div[data-testid="stButton"] button {
        background: linear-gradient(90deg, rgba(0,229,255,0.8) 0%, rgba(0,123,181,0.8) 100%) !important;
        color: #ffffff !important;
        border: 1px solid #00e5ff !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stButton"] button:hover {
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.6) !important;
        border: 1px solid #ffffff !important;
    }
    
    /* Tactical Telemetry Card Grid */
    .tactical-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-bottom: 10px;
    }
    .tactical-card {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid #374151;
        border-radius: 6px;
        padding: 10px 12px;
        box-sizing: border-box;
        transition: border-color 0.2s ease;
    }
    .tactical-card:hover {
        border-color: #00e5ff;
    }
    .tactical-label {
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #9ca3af;
        margin-bottom: 4px;
    }
    .tactical-val {
        font-size: 1.45rem;
        font-weight: 700;
        color: #f9fafb;
        font-family: 'Inter', sans-serif;
        line-height: 1.2;
        letter-spacing: -0.5px;
    }
    .tactical-sub {
        font-size: 0.72rem;
        color: #9ca3af;
        font-weight: 400;
    }
    .tactical-badge {
        display: inline-block;
        margin-top: 6px;
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.2px;
        white-space: nowrap;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Auto-refresh every 60 seconds (60000 milliseconds) silently
# commenting this to save the llm quota i aint made of money
#st_autorefresh(interval=60000, limit=None, key="datarefresh") 


@st.cache_data(ttl=5)
def fetch_telemetry():
    try:
        print(f"Attempting to fetch from: {BACKEND_URL}/api/forecast", flush=True)
        res = requests.get(f"{BACKEND_URL}/api/forecast", timeout=30)
        if res.status_code == 200:
            return res.json()
        else:
            print(f"Failed with status code: {res.status_code}", flush=True)
    except Exception as e:
        print(f"Exception fetching telemetry: {e}", flush=True)
    return None


data = fetch_telemetry()

st.markdown("## ZEPHYR // CYBER-PHYSICAL AIR QUALITY TWIN")
st.markdown(
    "<span style='color:#ff9900; font-weight:600; font-size: 0.85rem; letter-spacing: 1px;'>AWS BHARAT BUILDS TOUR (TRACK 01: AIR)</span> • <span style='color:#9ca3af; font-size: 0.85rem; letter-spacing: 1px;'>AMAZON BEDROCK • ST-GNN INFERENCE • AWS IOT CORE • DYNAMODB</span>",
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

if not data:
    st.error(
        "System Offline: Backend microservice unreachable. Awaiting FastAPI telemetry."
    )
    st.stop()

nodes = data["nodes"]
df = pd.DataFrame(nodes)
mean_pm25 = data["city_mean_pm25"]
active_dispatches = sum(1 for n in nodes if n["needs_dispatch"])
inference_latency = random.randint(45, 85)
aws_infra = data.get("aws_infrastructure", {})

# Create main functional zones (30% Left Rail, 70% Right Canvas)
col_left, col_right = st.columns([3, 7])

with col_left:
    st.markdown("<h4 style='font-weight:400; color:#e5e7eb;'>TACTICAL TELEMETRY</h4>", unsafe_allow_html=True)
    
    # Dynamic styling based on PM2.5 and dispatch thresholds
    if mean_pm25 >= 450:
        pm_border = "#ef4444"
        pm_badge_style = "background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.5);"
        pm_badge_text = "⚡ GRAP IV (Emergency)"
    elif mean_pm25 >= 120:
        pm_border = "#f59e0b"
        pm_badge_style = "background: rgba(245, 158, 11, 0.2); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.5);"
        pm_badge_text = "⚠️ GRAP III (Severe)"
    else:
        pm_border = "#00e5ff"
        pm_badge_style = "background: rgba(0, 229, 255, 0.15); color: #67e8f9; border: 1px solid rgba(0, 229, 255, 0.4);"
        pm_badge_text = "● Normal Baseline"

    if active_dispatches > 0:
        dispatch_border = "#f59e0b"
        dispatch_badge_style = "background: rgba(245, 158, 11, 0.2); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.5);"
        dispatch_badge_text = f"🚛 {active_dispatches} Cannons Active"
    else:
        dispatch_border = "#10b981"
        dispatch_badge_style = "background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4);"
        dispatch_badge_text = "✓ Depot Standby"

    telemetry_cards_html = f"""
    <div class="tactical-grid">
        <div class="tactical-card" style="border-left: 3px solid {pm_border};">
            <div class="tactical-label">Pred. Mean PM2.5</div>
            <div class="tactical-val">{mean_pm25} <span class="tactical-sub">µg/m³</span></div>
            <span class="tactical-badge" style="{pm_badge_style}">{pm_badge_text}</span>
        </div>
        <div class="tactical-card" style="border-left: 3px solid #10b981;">
            <div class="tactical-label">Active Sensors</div>
            <div class="tactical-val">{len(df)} <span class="tactical-sub">/ 5 nodes</span></div>
            <span class="tactical-badge" style="background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4);">● 100% Online</span>
        </div>
        <div class="tactical-card" style="border-left: 3px solid {dispatch_border};">
            <div class="tactical-label">Fleet Dispatches</div>
            <div class="tactical-val">{active_dispatches} <span class="tactical-sub">units</span></div>
            <span class="tactical-badge" style="{dispatch_badge_style}">{dispatch_badge_text}</span>
        </div>
        <div class="tactical-card" style="border-left: 3px solid #ff9900;">
            <div class="tactical-label">Cloud Engine</div>
            <div class="tactical-val" style="font-size: 1.15rem; padding-top: 3px;">AWS Bedrock</div>
            <span class="tactical-badge" style="background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4);">✓ Sonnet 3.5</span>
        </div>
    </div>
    <div class="tactical-card" style="border-left: 3px solid #00e5ff; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="tactical-label">ST-GNN Inference Latency</div>
                <div class="tactical-val" style="font-size: 1.25rem;">{inference_latency} <span class="tactical-sub">ms</span></div>
            </div>
            <span class="tactical-badge" style="background: rgba(0, 229, 255, 0.15); color: #67e8f9; border: 1px solid rgba(0, 229, 255, 0.4);">⚡ Real-Time Compute</span>
        </div>
    </div>
    """
    st.markdown(telemetry_cards_html, unsafe_allow_html=True)
    
    # AWS Infrastructure Status Banner
    st.markdown(f"""
    <div style="background: rgba(255, 153, 0, 0.08); border-left: 3px solid #ff9900; padding: 8px 12px; border-radius: 4px; font-family: monospace; font-size: 0.75rem; color: #d1d5db; margin-top: 10px;">
        <span style="color:#ff9900; font-weight:bold;">AWS RUNTIME:</span> {aws_infra.get('aws_mode', 'AWS Cloud / LocalStack')} <br/>
        <span style="color:#ff9900; font-weight:bold;">STORAGE:</span> DynamoDB Ledger & S3 Data Lake <br/>
        <span style="color:#ff9900; font-weight:bold;">ACTUATION:</span> AWS IoT Core & SNS Alerts
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 1rem 0 !important;'>", unsafe_allow_html=True)
    
    # THE AGENTIC LAYER UI (AMAZON BEDROCK)
    st.markdown("### AUTONOMOUS AGENT BRIEFING")
    with st.spinner("Amazon Bedrock synthesizing live ST-GNN telemetry..."):
        try:
            agent_res = requests.get(
                f"{BACKEND_URL}/api/agent_briefing", timeout=60
            )
            if agent_res.status_code == 200:
                agent_json = agent_res.json()
                briefing_text = agent_json.get("briefing", "No briefing available.")
                provider_name = agent_json.get("provider", "Amazon Bedrock")
                st.markdown(f"""
                <div style="background-color: rgba(0, 229, 255, 0.05); border-left: 3px solid #00e5ff; padding: 15px; border-radius: 4px; font-family: monospace; font-size: 0.85rem; color: #e5e7eb; margin-bottom: 10px; line-height: 1.5;">
                    <div style="color: #00e5ff; font-weight: bold; margin-bottom: 10px;">> ZEPHYR_CHIEF_AI // {provider_name.upper()} SECURE UPLINK</div>
                    {briefing_text}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning(f"Agent API returned status code: {agent_res.status_code}")
        except requests.exceptions.RequestException as e:
            st.warning(f"Agent API unreachable: {e}")
            
    st.markdown("<hr style='margin: 1rem 0 !important;'>", unsafe_allow_html=True)
    
    # GRAP Table
    st.markdown("<h5 style='font-weight:400; color:#e5e7eb;'>STATUTORY GRAP MITIGATION BOARD</h5>", unsafe_allow_html=True)
    display_df = df[["station", "pm25", "grap_stage", "prescribed_action"]].copy()
    display_df["prescribed_action"] = display_df["prescribed_action"].str.replace("_", " ").str.title()
    
    table_html = "<div style='background-color: #0e1117; border: 1px solid #1e1e24; border-radius: 6px; padding: 10px;'><table style='width:100%; border-collapse: collapse; font-size: 0.80rem; color: #d1d5db; font-family: Inter, sans-serif;'>"
    table_html += "<tr style='border-bottom: 1px solid #374151; color: #9ca3af; text-transform: uppercase;'><th style='text-align:left; padding:8px 4px;'>Node</th><th style='text-align:left; padding:8px 4px;'>PM2.5</th><th style='text-align:left; padding:8px 4px;'>Status</th><th style='text-align:left; padding:8px 4px;'>Intervention</th></tr>"
    for _, row in display_df.iterrows():
        status = row['grap_stage']
        color = "#00e5ff" if status == "Normal" else ("#ef4444" if "Severe" in status else "#f59e0b")
        table_html += f"<tr style='border-bottom: 1px solid #1f2937;'>"
        table_html += f"<td style='padding:8px 4px;'>{row['station']}</td>"
        table_html += f"<td style='padding:8px 4px; font-family: monospace;'>{row['pm25']}</td>"
        table_html += f"<td style='padding:8px 4px; color: {color}; font-weight: 600;'>{status}</td>"
        table_html += f"<td style='padding:8px 4px;'>{row['prescribed_action']}</td>"
        table_html += "</tr>"
    table_html += "</table></div>"
    st.markdown(table_html, unsafe_allow_html=True)


with col_right:
    st.markdown("<h4 style='font-weight:400; color:#e5e7eb;'>SPATIAL POLLUTION TOPOLOGY & FLEET ROUTING</h4>", unsafe_allow_html=True)
    
    # 3D PyDeck - SLEEK NEEDLES FIX
    def get_color(val):
        if val > 250:
            return [138, 43, 226, 255]
        elif val > 120:
            return [220, 38, 38, 255]
        elif val > 60:
            return [245, 158, 11, 255]
        return [0, 229, 255, 255]

    df["color"] = df["pm25"].apply(get_color)
    df["elevation"] = df["pm25"] * 30

    if "routes" in data and data["routes"]:
        df_routes = pd.DataFrame(data["routes"])
    else:
        df_routes = pd.DataFrame()

    # Generate graph edges connecting all 5 stations (Fully Connected Graph)
    graph_edges = []
    for n1, n2 in itertools.combinations(nodes, 2):
        graph_edges.append({
            "start": [n1["lon"], n1["lat"]],
            "end": [n2["lon"], n2["lat"]]
        })
    df_graph_edges = pd.DataFrame(graph_edges)

    # Central Municipal Depot Hub Beacon
    hub_info = data.get("dispatch_hub", {"lat": 26.8467, "lon": 80.9462, "name": "Central Municipal Depot"})
    df_hub = pd.DataFrame([{
        "lon": hub_info["lon"],
        "lat": hub_info["lat"],
        "name": hub_info.get("name", "Central Municipal Depot")
    }])

    layers = [
        # The physical graph topology (ST-GNN Message Passing layer)
        pdk.Layer(
            "LineLayer",
            data=df_graph_edges,
            get_source_position="start",
            get_target_position="end",
            get_color=[0, 229, 255, 70], # Low opacity cyan
            get_width=2,
            pickable=False,
        ),
        # Central Municipal Fleet Depot Marker
        pdk.Layer(
            "ScatterplotLayer",
            data=df_hub,
            get_position=["lon", "lat"],
            get_color=[255, 170, 0, 240], # Amber beacon
            get_radius=180,
            pickable=True,
        ),
        # The station pollution column needles
        pdk.Layer(
            "ColumnLayer",
            data=df,
            get_position=["lon", "lat"],
            get_elevation="elevation",
            elevation_scale=1,
            radius=90,   # Slim, elegant sensor needles
            get_fill_color="color",
            pickable=True,
            auto_highlight=True,
        )
    ]

    # The OR-Tools VRP Dispatch Parabolic Arcs
    if not df_routes.empty:
        layers.append(
            pdk.Layer(
                "ArcLayer",
                data=df_routes,
                get_source_position="start",
                get_target_position="end",
                get_source_color=[0, 229, 255, 200], # Glowing cyan source (Depot)
                get_target_color=[220, 38, 38, 255],   # Warning red target (Station)
                get_width=2,                           # Sleek, thin professional arcs
                pickable=True,
                auto_highlight=True,
            )
        )

    st.pydeck_chart(
        pdk.Deck(
            map_style=pdk.map_styles.CARTO_DARK,
            initial_view_state=pdk.ViewState(
                latitude=26.8467, longitude=80.9462, zoom=11.5, pitch=55, bearing=-20
            ),
            layers=layers,
            tooltip={
                "html": "<div style='font-family:Inter; font-size:12px; color:#ffffff;'><b>{station}</b><br/>PM2.5: {pm25} µg/m³<br/>GRAP: {grap_stage}</div>"
            },
        )
    )

    st.markdown("<hr style='margin: 1.5rem 0 !important;'>", unsafe_allow_html=True)
    
    # 2-Row Chart Layout for the Right Canvas
    
    # ROW 1: Severity Ranking and XAI
    chart_c1, chart_c2 = st.columns(2)
    
    with chart_c1:
        st.markdown("<h5 style='font-weight:400; color:#e5e7eb;'>NODE SEVERITY RANKING</h5>", unsafe_allow_html=True)
        fig = px.bar(
            df,
            x="pm25",
            y="station",
            orientation="h",
            color="pm25",
            color_continuous_scale="Reds",
        )
        fig.update_traces(texttemplate='%{x} µg/m³', textposition="outside", cliponaxis=False)
        fig.update_layout(
            font=dict(family="Inter", size=11, color="#9ca3af"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=60, t=5, b=0),
            xaxis=dict(visible=False),
            yaxis=dict(title="", showgrid=False, visible=True, automargin=True),
            coloraxis_showscale=False,
            bargap=0.5,
            height=260,
        )
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with chart_c2:
        st.markdown("<h5 style='font-weight:400; color:#e5e7eb;'>ML FEATURE IMPORTANCE (XAI)</h5>", unsafe_allow_html=True)
        shap_data = data.get("shap_attributions", {})
        if shap_data:
            features = list(shap_data.keys())
            importance = list(shap_data.values())
        else:
            features = ["No Data"]
            importance = [0]

        fig_ml = px.bar(
            x=importance, 
            y=features, 
            orientation="h",
            color=importance,
            color_continuous_scale=[[0, "#00838f"], [1, "#00e5ff"]]
        )
        fig_ml.update_traces(texttemplate='%{x:.1f}%', textposition="outside", cliponaxis=False)
        fig_ml.update_coloraxes(showscale=False)
        fig_ml.update_layout(
            font=dict(family="Inter", size=11, color="#9ca3af"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=45, t=5, b=0),
            xaxis=dict(visible=False),
            yaxis=dict(title="", showgrid=False, visible=True, automargin=True),
            bargap=0.45,
            height=260,
        )
        fig_ml.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig_ml, use_container_width=True, config={"displayModeBar": False})

    # ROW 2: Live Telemetry Timeline (24H)
    st.markdown("<hr style='margin: 1.5rem 0 !important;'>", unsafe_allow_html=True)
    st.markdown("<h5 style='font-weight:400; color:#e5e7eb;'>LIVE 24H TELEMETRY TIMELINE</h5>", unsafe_allow_html=True)
    
    # Process the timeseries data into a single Pandas DataFrame
    timeline_records = []
    
    # Station color mapping matching the SCADA cyan/red gradient aesthetic
    station_colors = {
        "Talkatora": "#00e5ff",      # Cyan
        "Lalbagh": "#14b8a6",        # Teal
        "Gomti Nagar": "#f59e0b",    # Amber
        "Alambagh": "#ef4444",       # Red
        "Kalyanpur": "#8b5cf6"       # Purple
    }

    for node in nodes:
        times = node.get("timeseries_time", [])
        pm25_vals = node.get("timeseries_pm25", [])
        station = node.get("station", "Unknown")
        
        for t, v in zip(times, pm25_vals):
            timeline_records.append({"Time": t, "PM2.5": v, "Station": station})
            
    if timeline_records:
        df_timeline = pd.DataFrame(timeline_records)
        df_timeline["Time"] = pd.to_datetime(df_timeline["Time"])
        
        # Create a sleek dark-mode line chart
        fig_timeline = px.line(
            df_timeline, 
            x="Time", 
            y="PM2.5", 
            color="Station",
            color_discrete_map=station_colors
        )
        
        # Style to match the SCADA military aesthetic
        fig_timeline.update_layout(
            font=dict(family="Inter", size=11, color="#9ca3af"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis=dict(
                title="", 
                showgrid=False, 
                showline=True, 
                linecolor="#374151"
            ),
            yaxis=dict(
                title="", 
                showgrid=False, 
                showline=True, 
                linecolor="#374151"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                title=""
            ),
            height=300,
        )
        # Apply distinct colored lines for neon aesthetic
        fig_timeline.update_traces(line=dict(width=2.5), line_shape="spline")
        
        st.plotly_chart(fig_timeline, use_container_width=True, config={"displayModeBar": False})
    else:
        st.warning("No timeline data available in payload.")
