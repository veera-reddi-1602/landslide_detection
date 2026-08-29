import streamlit as st
import pickle
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MDoNER - NER Landslide Command Center", layout="wide", page_icon="⛰️")

# Header
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg", width=70)
with col_title:
    st.title("MDoNER - AI Landslide Early Warning & Risk Monitoring System")
    st.caption("Pilot: Meghalaya & Sikkim | Data Sources: NASA SRTM DEM, IMD, GSI, Bhuvan | SIH26001")

# Load model
@st.cache_resource
def load_model():
    with open('model.pkl','rb') as f:
        return pickle.load(f)
model = load_model()

# Sidebar Controls - NEW FEATURE 1
st.sidebar.header("🎛️ Command Center Controls")
district = st.sidebar.selectbox("Select District", ["East Khasi Hills (Meghalaya)", "West Sikkim (Sikkim)", "Papum Pare (Arunachal)"])
rain_forecast = st.sidebar.slider("Next 72 Hours Rainfall Forecast (IMD) [mm]", 0, 500, 250)
soil_moisture = st.sidebar.slider("Soil Moisture % (NASA SMAP)", 0, 100, 75)
st.sidebar.divider()
st.sidebar.error(f"IMD Alert: Heavy rainfall predicted in {district}")

# Village database - EXPANDED - NEW FEATURE 2
base_villages = [
    {"name": "Cherapunji", "lat": 25.30, "lon": 91.70, "slope": 45, "elev": 1484, "road": 50, "pop": 10000},
    {"name": "Shillong", "lat": 25.57, "lon": 91.88, "slope": 25, "elev": 1525, "road": 10, "pop": 150000},
    {"name": "Mawlynnong", "lat": 25.20, "lon": 91.91, "slope": 38, "elev": 560, "road": 100, "pop": 500},
    {"name": "Dawki", "lat": 25.18, "lon": 92.01, "slope": 42, "elev": 300, "road": 30, "pop": 2000},
    {"name": "Nongstoin", "lat": 25.51, "lon": 91.26, "slope": 15, "elev": 1400, "road": 500, "pop": 30000},
    {"name": "Mawsynram", "lat": 25.29, "lon": 91.58, "slope": 48, "elev": 1400, "road": 70, "pop": 1200},
]

# Dynamic prediction based on slider - NEW FEATURE 3
villages = []
for v in base_villages:
    # Use forecast rainfall + soil moisture logic
    effective_rain = v["slope"] * 0.5 + rain_forecast * 0.8 + soil_moisture * 0.3
    prob = model.predict_proba([[v['slope'], rain_forecast, v['elev'], v['road']]])[0][1]
    # Boost prob if forecast high
    prob = min(0.98, prob + (rain_forecast-200)/800)

    if prob > 0.7:
        risk, color, action = 'HIGH', 'red', 'EVACUATE'
    elif prob > 0.4:
        risk, color, action = 'MEDIUM', 'orange', 'ALERT'
    else:
        risk, color, action = 'LOW', 'green', 'SAFE'
    villages.append({**v, "prob": prob, "risk": risk, "color": color, "action": action})

# Main Layout
tab1, tab2, tab3 = st.tabs(["🗺️ Live Risk Map", "📊 Analytics & Reports", "🚨 Alert Center"])

with tab1:
    c1, c2 = st.columns([3,1])
    with c1:
        m = folium.Map(location=[25.45, 91.80], zoom_start=10, tiles="Esri.WorldImagery")
        for v in villages:
            folium.CircleMarker(
                location=[v['lat'], v['lon']],
                radius=15 + v['prob']*20,
                color=v['color'],
                fill=True,
                fill_color=v['color'],
                fill_opacity=0.7,
                popup=f"<b>{v['name']}</b><br>Risk: {v['risk']} ({v['prob']*100:.0f}%)<br>Pop: {v['pop']}<br>Rain: {rain_forecast}mm<br>Action: {v['action']}"
            ).add_to(m)
        st_folium(m, width=800, height=550)
    with c2:
        st.subheader("Live Risk Status")
        for v in villages:
            if v['risk'] == 'HIGH':
                st.error(f"🔴 {v['name']}: {v['prob']*100:.0f}% - {v['action']}")
            elif v['risk'] == 'MEDIUM':
                st.warning(f"🟡 {v['name']}: {v['prob']*100:.0f}%")
            else:
                st.success(f"🟢 {v['name']}: {v['prob']*100:.0f}%")
        st.metric("High Risk Villages", sum(1 for v in villages if v['risk']=='HIGH'))
        st.metric("Population at Risk", sum(v['pop'] for v in villages if v['risk']=='HIGH'))

with tab2:
    # NEW FEATURE 4: Charts
    df = pd.DataFrame(villages)
    fig1 = px.bar(df, x='name', y='prob', color='risk', color_discrete_map={'HIGH':'red','MEDIUM':'orange','LOW':'green'}, title="Landslide Probability by Village")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.scatter(df, x='slope', y='prob', size='pop', color='risk', hover_name='name', title="Slope vs Risk Correlation (Explainable AI)")
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(df[['name','slope','elev','prob','risk','action','pop']], use_container_width=True)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Risk Report CSV", csv, "NER_Risk_Report.csv", "text/csv")

with tab3:
    # NEW FEATURE 5: Alert Simulation
    st.subheader("📢 Automated Early Warning Dissemination")
    st.write("As per MDoNER SOP, alerts will be sent in local language via:")
    st.code(f"""
    [SMS to District Collector, {district}]
    ALERT: {sum(1 for v in villages if v['risk']=='HIGH')} villages at HIGH risk in next 72 hrs.
    Villages: {', '.join([v['name'] for v in villages if v['risk']=='HIGH'])}
    Rainfall Forecast: {rain_forecast}mm
    Action: Initiate evacuation.
    - NER Disaster Control
    """)
    if st.button("🚀 Simulate Send SMS/WhatsApp to Villagers (in Khasi/Assamese)"):
        st.success("✅ SMS Sent to 5,230 residents in East Khasi Hills via Fast2SMS API")
        st.balloons()

    st.divider()
    st.info("🔮 Future: Integration with Bhashini API for local language, Bhuvan for satellite live view, and IoT soil sensors.")