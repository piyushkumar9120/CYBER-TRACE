import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
import streamlit.components.v1 as components
from sklearn.cluster import DBSCAN
import datetime
import math
import random

# ==============================================================================
# 1. APPLICATION SETUP & RELIABLE STYLING
# ==============================================================================
st.set_page_config(
    page_title="CYBER-TRACE V4.0 | Next-Gen Interceptor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .kpi-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #0284c7;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    .kpi-title { font-size: 11px; color: #64748b; font-weight: 700; text-transform: uppercase; }
    .kpi-val { font-size: 24px; font-weight: 800; color: #0f172a; margin: 4px 0; }
    .kpi-sub { font-size: 11px; color: #0284c7; font-weight: 600; }
    .threat-banner {
        background-color: #fef2f2;
        border: 1px solid #f87171;
        border-radius: 8px;
        padding: 12px 16px;
        color: #991b1b;
        margin-bottom: 15px;
    }
    .cctv-box {
        background-color: #0f172a;
        color: #38bdf8;
        font-family: monospace;
        padding: 14px;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    .evidence-paper {
        background-color: #ffffff;
        color: #1e293b;
        border: 1px solid #cbd5e1;
        padding: 18px;
        font-family: 'Courier New', Courier, monospace;
        border-radius: 6px;
        font-size: 12px;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. MASTER REFERENCE DATA (DELHI NCR ATMS & POLICE UNITS)
# ==============================================================================
ATM_INFRASTRUCTURE = [
    {"atm_id": "ATM-DEL-01", "name": "SBI ATM - CP Outer Circle", "bank": "State Bank of India", "lat": 28.6328, "lon": 77.2195, "rate": 0.88, "guard_phone": "+91 98110-XXXX1", "guard_name": "Ramesh Kumar"},
    {"atm_id": "ATM-DEL-02", "name": "HDFC ATM - Karol Bagh Market", "bank": "HDFC Bank", "lat": 28.6517, "lon": 77.1906, "rate": 0.74, "guard_phone": "+91 98110-XXXX2", "guard_name": "Surender Pal"},
    {"atm_id": "ATM-DEL-03", "name": "ICICI ATM - Laxmi Nagar Commercial", "bank": "ICICI Bank", "lat": 28.6304, "lon": 77.2773, "rate": 0.92, "guard_phone": "+91 98110-XXXX3", "guard_name": "Deepak Singh"},
    {"atm_id": "ATM-DEL-04", "name": "PNB ATM - Chandni Chowk Metro", "bank": "Punjab National Bank", "lat": 28.6560, "lon": 77.2307, "rate": 0.65, "guard_phone": "+91 98110-XXXX4", "guard_name": "Satish Verma"},
    {"atm_id": "ATM-DEL-05", "name": "Axis Bank ATM - Saket District Centre", "bank": "Axis Bank", "lat": 28.5245, "lon": 77.2167, "rate": 0.58, "guard_phone": "+91 98110-XXXX5", "guard_name": "Balbir Yadav"},
    {"atm_id": "ATM-DEL-06", "name": "Bank of Baroda CSP - Rohini Sec 7", "bank": "Bank of Baroda", "lat": 28.7041, "lon": 77.1025, "rate": 0.81, "guard_phone": "+91 98110-XXXX6", "guard_name": "Jagdish Chandra"},
    {"atm_id": "ATM-DEL-07", "name": "SBI CDM & ATM - Nehru Place Hub", "bank": "State Bank of India", "lat": 28.5494, "lon": 77.2526, "rate": 0.85, "guard_phone": "+91 98110-XXXX7", "guard_name": "Vikram Negi"},
    {"atm_id": "ATM-DEL-08", "name": "Canara Bank ATM - Janakpuri West", "bank": "Canara Bank", "lat": 28.6297, "lon": 77.0818, "rate": 0.62, "guard_phone": "+91 98110-XXXX8", "guard_name": "Sunil Tomar"}
]

INITIAL_PATROL_UNITS = [
    {"unit_id": "PCR-ALPHA-01", "name": "Hawk CP Central", "lat": 28.6285, "lon": 77.2120, "status": "Available", "officer": "SI Rakesh Tyagi"},
    {"unit_id": "PCR-BETA-02", "name": "Cheetah Laxmi East", "lat": 28.6270, "lon": 77.2710, "status": "Available", "officer": "ASI Mohan Lal"},
    {"unit_id": "PCR-GAMMA-03", "name": "Falcon South Saket", "lat": 28.5290, "lon": 77.2110, "status": "Available", "officer": "SI Harish Rawat"},
    {"unit_id": "PCR-DELTA-04", "name": "Rhino West Janakpuri", "lat": 28.6340, "lon": 77.0870, "status": "Available", "officer": "ASI Anil Sharma"}
]

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

# ==============================================================================
# 3. SYNTHETIC TELEMETRY GENERATOR
# ==============================================================================
@st.cache_data
def generate_synthetic_complaints(num_records=520):
    np.random.seed(42)
    random.seed(42)
    categories = ["UPI Phishing", "Loan App Extortion", "Part-Time Job Scam", "KYC Spoofing", "Investment Ponzi"]
    statuses = ["Pending", "Withdrawn", "Intercepted"]
    base_time = datetime.datetime.now()
    records = []

    mule_master_rings = {
        "MULE-HDFC-9904": {"layer2": "MASTER-CANARA-4019", "syndicate": "Mewat-Jamtara Link-A"},
        "MULE-HDFC-9908": {"layer2": "MASTER-PNB-1082", "syndicate": "NCR Cyber Core-9"},
        "MULE-ICICI-3301": {"layer2": "MASTER-SBI-8821", "syndicate": "Southeast Phish-Net"}
    }

    for i in range(1, num_records + 1):
        anchor_atm = random.choice(ATM_INFRASTRUCTURE)
        lat = anchor_atm["lat"] + np.random.normal(0, 0.011)
        lon = anchor_atm["lon"] + np.random.normal(0, 0.011)
        amount = int(np.random.choice([18000, 48000, 95000, 160000, 240000]))
        minutes_ago = random.randint(10, 1440)
        timestamp = base_time - datetime.timedelta(minutes=minutes_ago)
        reported_delay = random.randint(4, 45)
        status = np.random.choice(statuses, p=[0.48, 0.37, 0.15])
        assigned_mule = random.choice(list(mule_master_rings.keys()) + [f"MULE-GEN-{random.randint(10, 99)}"])

        records.append({
            "complaint_id": f"CFIR-2026-{10000 + i}",
            "timestamp": timestamp,
            "crime_category": random.choice(categories),
            "amount_stolen": amount,
            "victim_lat": round(lat, 5),
            "victim_long": round(lon, 5),
            "mule_account_id": assigned_mule,
            "reported_delay_mins": reported_delay,
            "withdrawal_status": status,
            "nearest_atm_name": anchor_atm["name"],
            "nearest_atm_id": anchor_atm["atm_id"]
        })
    return pd.DataFrame(records)

# Session State Initialization
if "complaints_df" not in st.session_state:
    st.session_state.complaints_df = generate_synthetic_complaints(520)

if "patrol_units" not in st.session_state:
    st.session_state.patrol_units = [dict(p) for p in INITIAL_PATROL_UNITS]

if "activity_logs" not in st.session_state:
    st.session_state.activity_logs = [
        {"time": "Live", "event": "Real-time Kafka consumer connected to 1930 CFCFRMS Gateway."},
        {"time": "Live", "event": "Spatial mesh calibrated across Delhi NCR banking corridors."}
    ]

if "decoy_active_atm" not in st.session_state:
    st.session_state.decoy_active_atm = None

if "ivr_logs" not in st.session_state:
    st.session_state.ivr_logs = []

# ==============================================================================
# 4. PREDICTIVE CLUSTERING ENGINE (DBSCAN)
# ==============================================================================
def run_predictive_engine(df, risk_cutoff=40):
    unresolved_df = df[df["withdrawal_status"] == "Pending"].copy()
    if len(unresolved_df) < 3:
        return []

    coords = np.radians(unresolved_df[["victim_lat", "victim_long"]].values)
    epsilon = 2.4 / 6371.0
    db = DBSCAN(eps=epsilon, min_samples=3, metric='haversine')
    unresolved_df["cluster_id"] = db.fit_predict(coords)

    hotspots = []
    clustered = unresolved_df[unresolved_df["cluster_id"] != -1]

    for cluster_id, group in clustered.groupby("cluster_id"):
        center_lat = group["victim_lat"].mean()
        center_lon = group["victim_long"].mean()
        total_amount = group["amount_stolen"].sum()
        count = len(group)
        avg_delay = group["reported_delay_mins"].mean()

        atm_distances = [
            (atm, haversine_km(center_lat, center_lon, atm["lat"], atm["lon"]))
            for atm in ATM_INFRASTRUCTURE
        ]
        atm_distances.sort(key=lambda x: x[1])
        closest_atm, dist_km = atm_distances[0]

        vol_score = min(1.0, count / 6.0) * 30.0
        val_score = min(1.0, total_amount / 300000.0) * 30.0
        hist_score = closest_atm["rate"] * 20.0
        rec_score = max(0.0, (1.0 - (avg_delay / 60.0))) * 20.0

        risk = int(vol_score + val_score + hist_score + rec_score)
        risk = min(99, max(25, risk))

        if risk >= risk_cutoff:
            hotspots.append({
                "hotspot_id": f"HOTSPOT-DEL-{cluster_id + 101}",
                "atm_id": closest_atm["atm_id"],
                "atm_name": closest_atm["name"],
                "bank": closest_atm["bank"],
                "lat": closest_atm["lat"],
                "lon": closest_atm["lon"],
                "guard_phone": closest_atm["guard_phone"],
                "guard_name": closest_atm["guard_name"],
                "distance_km": round(dist_km, 2),
                "complaint_count": count,
                "total_value": total_amount,
                "risk_score": risk,
                "top_mule": group["mule_account_id"].mode().iloc[0],
                "avg_delay": round(avg_delay, 1),
                "withdrawal_window": f"{max(8, int(40 - avg_delay))}–{max(18, int(65 - avg_delay))} mins",
                "complaint_ids": group["complaint_id"].tolist(),
                "vol_score": vol_score,
                "val_score": val_score,
                "hist_score": hist_score
            })

    hotspots.sort(key=lambda x: x["risk_score"], reverse=True)
    return hotspots

# ==============================================================================
# 5. SIDEBAR
# ==============================================================================
with st.sidebar:
    st.title("🛡️ CYBER-TRACE V4.0")
    st.caption("Next-Gen Predictive Interception Framework")
    st.markdown("---")

    risk_threshold = st.slider("Minimum Risk Filter (%)", 25, 90, 40, 5)

    st.markdown("### Tactical Simulator")
    if st.button("🚨 Simulate Live Attack Ingestion", use_container_width=True):
        target_atm = random.choice(ATM_INFRASTRUCTURE[:4])
        new_row = {
            "complaint_id": f"CFIR-2026-{random.randint(60000, 99999)}",
            "timestamp": datetime.datetime.now(),
            "crime_category": "UPI Phishing",
            "amount_stolen": random.choice([95000, 160000, 240000]),
            "victim_lat": round(target_atm["lat"] + np.random.normal(0, 0.005), 5),
            "victim_long": round(target_atm["lon"] + np.random.normal(0, 0.005), 5),
            "mule_account_id": "MULE-HDFC-9904",
            "reported_delay_mins": random.randint(4, 9),
            "withdrawal_status": "Pending",
            "nearest_atm_name": target_atm["name"],
            "nearest_atm_id": target_atm["atm_id"]
        }
        st.session_state.complaints_df = pd.concat([pd.DataFrame([new_row]), st.session_state.complaints_df], ignore_index=True)
        st.session_state.activity_logs.insert(0, {
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "event": f"CRITICAL FRAUD: ₹{new_row['amount_stolen']:,} reported near {target_atm['name']} (Mule: MULE-HDFC-9904)."
        })
        st.toast(f"Live Attack Ingested! ₹{new_row['amount_stolen']:,}", icon="🚨")
        st.rerun()

    if st.button("🔄 Reset Telemetry", use_container_width=True):
        st.session_state.complaints_df = generate_synthetic_complaints(520)
        st.session_state.patrol_units = [dict(p) for p in INITIAL_PATROL_UNITS]
        st.session_state.decoy_active_atm = None
        st.rerun()

# Run ML Engine
hotspots = run_predictive_engine(st.session_state.complaints_df, risk_cutoff=risk_threshold)

# ==============================================================================
# 6. HEADER & KPIS
# ==============================================================================
st.title("🛡️ National Cybercrime Cash-Out Interception Radar")
st.markdown("**Predictive Spatial AI & Tactical Interception Platform for ATM / CSP Mule Withdrawals**")

total_pending = len(st.session_state.complaints_df[st.session_state.complaints_df["withdrawal_status"] == "Pending"])
intercepted_cases = st.session_state.complaints_df[st.session_state.complaints_df["withdrawal_status"] == "Intercepted"]
frozen_value = intercepted_cases["amount_stolen"].sum()

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Active Pending Fraud</div>
        <div class="kpi-val">{total_pending:,}</div>
        <div class="kpi-sub">Unresolved complaints in telemetry</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Flagged Hotspots</div>
        <div class="kpi-val" style="color: #dc2626;">{len(hotspots)}</div>
        <div class="kpi-sub">Confidence ≥ {risk_threshold}%</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Proactively Frozen</div>
        <div class="kpi-val" style="color: #16a34a;">₹{frozen_value:,.0f}</div>
        <div class="kpi-sub">{len(intercepted_cases)} mule accounts saved</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Interception Lead Time</div>
        <div class="kpi-val">25 mins</div>
        <div class="kpi-sub">Average window before cash-out</div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 7. MAIN GIS RADAR & COMMAND CENTER
# ==============================================================================
col_map, col_ops = st.columns([1.55, 1.45])

with col_map:
    st.subheader("📍 Geospatial Hotspot Radar (Delhi NCR)")
    
    m = folium.Map(location=[28.6250, 77.2150], zoom_start=11, tiles="OpenStreetMap")

    heat_coords = [
        [r["victim_lat"], r["victim_long"], 0.6] 
        for _, r in st.session_state.complaints_df[st.session_state.complaints_df["withdrawal_status"] == "Pending"].iterrows()
    ]
    if heat_coords:
        HeatMap(heat_coords, radius=14, blur=10).add_to(m)

    for hs in hotspots:
        folium.CircleMarker(
            location=[hs["lat"], hs["lon"]],
            radius=12,
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.6,
            popup=f"<b>{hs['atm_name']}</b><br>Risk: {hs['risk_score']}%<br>Stake: ₹{hs['total_value']:,}"
        ).add_to(m)

    for p in st.session_state.patrol_units:
        icon_color = "blue" if p["status"] == "Available" else "green"
        folium.Marker(
            location=[p["lat"], p["lon"]],
            icon=folium.Icon(color=icon_color, icon="shield"),
            popup=f"<b>{p['name']}</b> ({p['status']})<br>Officer: {p['officer']}"
        ).add_to(m)

    map_html = m._repr_html_()
    components.html(map_html, height=470)

with col_ops:
    st.subheader("⚡ Tactical Interception Operations")

    if hotspots:
        selected_hs_id = st.selectbox(
            "Select Flagged Target Hotspot:",
            options=[h["hotspot_id"] for h in hotspots],
            format_func=lambda x: f"{x} - {next(h['atm_name'] for h in hotspots if h['hotspot_id'] == x)} (Risk: {next(h['risk_score'] for h in hotspots if h['hotspot_id'] == x)}%)"
        )
        curr = next(h for h in hotspots if h["hotspot_id"] == selected_hs_id)

        decoy_status_text = "🟢 ACTIVE TRAP RUNNING" if st.session_state.decoy_active_atm == curr['atm_name'] else "⚪ STANDBY"
        st.markdown(f"""
        <div class="threat-banner">
            <div style="font-weight:bold; font-size:14px;">⚠️ HIGH RISK TARGET: {curr['atm_name']}</div>
            <div style="font-size:12px; margin-top:4px;">
                Stake: <b>₹{curr['total_value']:,}</b> | Primary Mule: <code>{curr['top_mule']}</code> | Window: <b>{curr['withdrawal_window']}</b><br>
                Decoy Dispense Trap Status: <b>{decoy_status_text}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        b1, b2 = st.columns(2)
        with b1:
            if st.button("🚔 Dispatch Nearest Patrol", use_container_width=True):
                p_dists = [(p, haversine_km(curr["lat"], curr["lon"], p["lat"], p["lon"])) for p in st.session_state.patrol_units]
                p_dists.sort(key=lambda x: x[1])
                closest_p, dist = p_dists[0]
                closest_p["status"] = f"En Route ({curr['atm_name']})"
                eta = max(3, int(dist * 2.5))
                st.session_state.activity_logs.insert(0, {
                    "time": datetime.datetime.now().strftime("%H:%M:%S"),
                    "event": f"DISPATCH: {closest_p['name']} ({closest_p['officer']}) deployed to {curr['atm_name']} (ETA: {eta} mins)."
                })
                st.success(f"Dispatched **{closest_p['name']}**! ETA: **{eta} mins**")
                st.rerun()

        with b2:
            if st.button("🛑 Trigger Bank Freeze", use_container_width=True):
                st.session_state.complaints_df.loc[
                    st.session_state.complaints_df["complaint_id"].isin(curr["complaint_ids"]),
                    "withdrawal_status"
                ] = "Intercepted"
                st.session_state.activity_logs.insert(0, {
                    "time": datetime.datetime.now().strftime("%H:%M:%S"),
                    "event": f"BANK HOLD: Frozen ₹{curr['total_value']:,} on Mule {curr['top_mule']} via Bank Webhook."
                })
                st.success(f"Frozen ₹{curr['total_value']:,} on Mule `{curr['top_mule']}`!")
                st.rerun()

        b3, b4 = st.columns(2)
        with b3:
            if st.button("⏱️ Activate Decoy Delay Trap", use_container_width=True):
                st.session_state.decoy_active_atm = curr['atm_name']
                st.session_state.activity_logs.insert(0, {
                    "time": datetime.datetime.now().strftime("%H:%M:%S"),
                    "event": f"DECOY TRAP ARMED: ATM {curr['atm_name']} cash ejection throttled by 90 seconds for on-site sting."
                })
                st.toast(f"Decoy Delay Trap Armed on {curr['atm_name']}!", icon="⏱️")
                st.rerun()

        with b4:
            if st.button("📞 Trigger AI Guard Voice Call", use_container_width=True):
                call_log = {
                    "time": datetime.datetime.now().strftime("%H:%M:%S"),
                    "guard": curr['guard_name'],
                    "phone": curr['guard_phone'],
                    "atm": curr['atm_name'],
                    "msg": f"Alert: Suspected cybercrime cash-out flagged at {curr['atm_name']}. Police PCR en route."
                }
                st.session_state.ivr_logs.insert(0, call_log)
                st.session_state.activity_logs.insert(0, {
                    "time": datetime.datetime.now().strftime("%H:%M:%S"),
                    "event": f"IVR CALL: Automated alert dialed to Guard {curr['guard_name']} ({curr['guard_phone']})."
                })
                st.success(f"AI Call placed to Guard {curr['guard_name']}!")
                st.rerun()

        st.markdown("#### 🧠 Explainable AI (XAI) Decision Breakdown")
        st.progress(int(curr["vol_score"] / 30.0 * 100), text=f"Cluster Density: {curr['complaint_count']} linked victims in zone")
        st.progress(int(curr["val_score"] / 30.0 * 100), text=f"Value at Risk: ₹{curr['total_value']:,}")
        st.progress(int(curr["hist_score"] / 20.0 * 100), text="Historical ATM Cash-Out Vulnerability Index")

    else:
        st.info("No hotspots detected under current risk threshold.")

# ==============================================================================
# 8. ADVANCED MODULES TABS (CCTV, MULE GRAPH, PCR MOBILE, 65B DOSSIER)
# ==============================================================================
st.markdown("---")
tab_cctv, tab_mule, tab_pcr, tab_legal, tab_logs = st.tabs([
    "📹 ATM CCTV & Face Recognition", 
    "🕸️ Mule Syndicate Graph", 
    "📱 Patrol Mobile Terminal", 
    "⚖️ Court-Ready 65B Dossier", 
    "📋 Real-Time Logs"
])

with tab_cctv:
    st.subheader("📹 Real-Time ATM Vestibule CCTV Telemetry & AI Face Match")
    c_col1, c_col2 = st.columns([1.2, 1.8])
    with c_col1:
        st.markdown("""
        <div class="cctv-box">
            [CAM-DEL-03 LIVE FEED] SBI CP VESTIBULE<br>
            FPS: 28.4 | STATUS: STREAMING ENCRYPTED<br>
            -----------------------------------------<br>
            [!] ANOMALY DETECTED: Face Occlusion (Helmet + Mask)<br>
            [!] MULTI-CARD RETRY DETECTED: 3 Attempt(s)<br>
            -----------------------------------------<br>
            MATCH DATABASE: NCR Cyber History-Sheeters<br>
            MATCH SUSPECT: 'Pankaj S. @ Mewat Ring'<br>
            CONFIDENCE SCORE: 88.4% MATCH [CRITICAL]
        </div>
        """, unsafe_allow_html=True)
    with c_col2:
        st.write("#### AI Surveillance Triggers:")
        st.write("• **Facial Occlusion Alert:** Suspicious mask/helmet worn inside ATM vestibule.")
        st.write("• **Card Hopping Anomaly:** Same individual using 3 different debit cards within 120 seconds.")
        st.write("• **Automated Lock Trigger:** ATM vestibule exit door magnetic latch armed for arrival of PCR unit.")

with tab_mule:
    st.subheader("🕸️ Multi-Tier Mule Syndicate Tracing (Layer 1 ➔ Layer 2 Tracing)")
    st.write("Automated correlation identifying how victim funds flow into centralized syndicate accounts:")
    
    mule_data = [
        {"Victim Account": "HDFC-****3201 (₹95,000)", "Layer-1 Mule (Local ATM Card)": "MULE-HDFC-9904", "Layer-2 Master Account": "MASTER-CANARA-4019", "Syndicate Module": "Mewat-NCR Link", "Interception Status": "Card Blocked"},
        {"Victim Account": "SBI-****1192 (₹1,60,000)", "Layer-1 Mule (Local ATM Card)": "MULE-HDFC-9904", "Layer-2 Master Account": "MASTER-CANARA-4019", "Syndicate Module": "Mewat-NCR Link", "Interception Status": "Card Blocked"},
        {"Victim Account": "ICICI-****9982 (₹2,40,000)", "Layer-1 Mule (Local ATM Card)": "MULE-ICICI-3301", "Layer-2 Master Account": "MASTER-SBI-8821", "Syndicate Module": "Southeast Phish-Net", "Interception Status": "Under Watch"}
    ]
    st.dataframe(pd.DataFrame(mule_data), use_container_width=True)

with tab_pcr:
    st.subheader("📱 On-Ground Patrol (PCR) Tactical Interface")
    p_sel = st.selectbox("Select Patrol Vehicle Dashboard:", options=[p["unit_id"] for p in st.session_state.patrol_units])
    p_active = next(p for p in st.session_state.patrol_units if p["unit_id"] == p_sel)

    p_c1, p_c2, p_c3 = st.columns(3)
    p_c1.metric("Unit ID", p_active["unit_id"], p_active["name"])
    p_c2.metric("Commander", p_active["officer"])
    p_c3.metric("Operational Status", p_active["status"])

    if "En Route" in p_active["status"]:
        st.warning(f"🚨 TACTICAL ALERT: Vehicle {p_active['name']} navigating to target node with live priority sirens enabled.")
    else:
        st.info(f"Vehicle {p_active['name']} is patrolling baseline grid. Ready for dispatch.")

with tab_legal:
    st.subheader("⚖️ Section 65B Indian Evidence Act Forensic Dossier Generator")
    st.write("Generate a court-admissible digital evidence certificate and FIR case-diary instantaneously:")
    
    sample_dossier = f"""================================================================================
GOVERNMENT OF NCT OF DELHI / STATE POLICE CYBER CRIME COMMAND
DIGITAL EVIDENCE CHAIN OF CUSTODY CERTIFICATE (U/S 65B INDIAN EVIDENCE ACT)
================================================================================
CASE REFERENCE NUMBER : CFIR-2026-DEL-HOTSPOT-101
GENERATION TIMESTAMP  : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC+05:30")}
TARGET ATM NODE       : {hotspots[0]['atm_name'] if hotspots else 'SBI ATM CP Outer Circle'}
NODAL BANK & SWITCH   : {hotspots[0]['bank'] if hotspots else 'State Bank of India'}
PREDICTED VALUE AT RISK: ₹{hotspots[0]['total_value'] if hotspots else 240000:,}

1. FORENSIC CLUSTERING TELEMETRY:
   - Clustering Algorithm : DBSCAN (Haversine Spherical Epsilon = 2.4 km)
   - Correlated Victims   : {hotspots[0]['complaint_count'] if hotspots else 4} Complaints Linked
   - Primary Mule Account : {hotspots[0]['top_mule'] if hotspots else 'MULE-HDFC-9904'}

2. CHAIN OF CUSTODY & ENFORCEMENT AUDIT:
   - Dispatch Triggered   : Automatic Haversine Closest Patrol Unit Assigned
   - Bank Freeze Webhook  : Automated JSON Payload dispatched to NPCI Gateway
   - Tamper-proof Hash    : SHA256-e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

This document certifies that the automated telemetry logs were extracted directly
from the CYBER-TRACE system without manual alteration.
================================================================================
"""
    st.markdown(f'<div class="evidence-paper"><pre>{sample_dossier}</pre></div>', unsafe_allow_html=True)
    st.download_button(
        label="📥 Download Certified Evidence Dossier (.txt)",
        data=sample_dossier,
        file_name="CYBER_TRACE_Section_65B_Dossier.txt",
        mime="text/plain"
    )

with tab_logs:
    st.subheader("📋 Real-Time Activity & IVR Dispatch Logs")
    if st.session_state.ivr_logs:
        st.write("#### Recent IVR AI Voice Calls to ATM Guards:")
        for ivr in st.session_state.ivr_logs[:3]:
            st.warning(f"📞 `[{ivr['time']}]` Dialed Guard: **{ivr['guard']}** ({ivr['phone']}) @ {ivr['atm']}")
    
    st.write("#### Master Telemetry Event Log:")
    for log in st.session_state.activity_logs[:8]:
        st.write(f"**`[{log['time']}]`** {log['event']}")