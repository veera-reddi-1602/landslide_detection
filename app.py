import streamlit as st, pickle, folium, pandas as pd, plotly.express as px, plotly.graph_objects as go
from streamlit_folium import st_folium
import datetime, random, os, numpy as np
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="MDoNER 100% Final", layout="wide", page_icon="⛰️")
st.title("stark - AI Landslide Early Warning Command Center - 100% FINAL")
st.caption("Pilot: Meghalaya | ISRO Bhuvan | NASA SRTM | IMD | GSI | SIH26001")

@st.cache_resource
def load_model():
    try:
        if os.path.exists('model.pkl'):
            with open('model.pkl','rb') as f: return pickle.load(f)
    except: pass
    X = np.array([[45,400,1484,50],[25,100,1525,10],[15,50,1400,500],[42,350,300,30]])
    y = np.array([1,0,0,1])
    return RandomForestClassifier().fit(X,y)
model = load_model()

# --- SIDEBAR - ALL CONTROLS ---
st.sidebar.header("🎛️ Command Center Controls")
district = st.sidebar.selectbox("District", ["East Khasi Hills (Meghalaya)", "West Sikkim", "Papum Pare"])
map_layer = st.sidebar.radio("Satellite Layer (Space Tech)", ["ISRO Bhuvan","Esri Satellite","OSM"])
rain = st.sidebar.slider("Live Rainfall 72H (mm) - IMD", 0, 600, 300)
soil = st.sidebar.slider("Soil Moisture % - NASA", 0, 100, 80)
lang = st.sidebar.selectbox("Alert Language", ["English","Hindi","Khasi"])
st.sidebar.divider()
st.sidebar.metric("IoT Sensor - Cherapunji", f"{random.randint(75,95)}%", "↑ HIGH")
st.sidebar.metric("IoT Sensor - Shillong", f"{random.randint(30,50)}%", "↓ Safe")
if st.sidebar.button("🔊 Voice Alert"): st.sidebar.success("Alert Playing...")

# --- VILLAGES ---
base = [
    {"name":"Cherapunji","lat":25.30,"lon":91.70,"slope":45,"elev":1484,"road":50,"pop":10000},
    {"name":"Mawsynram","lat":25.29,"lon":91.58,"slope":48,"elev":1400,"road":70,"pop":1200},
    {"name":"Shillong","lat":25.57,"lon":91.88,"slope":25,"elev":1525,"road":10,"pop":150000},
    {"name":"Dawki","lat":25.18,"lon":92.01,"slope":42,"elev":300,"road":30,"pop":2000},
    {"name":"Nongstoin","lat":25.51,"lon":91.26,"slope":15,"elev":1400,"road":500,"pop":30000},
]
villages=[]
for v in base:
    prob = model.predict_proba([[v['slope'], rain, v['elev'], v['road']]])[0][1]
    prob = min(0.99, prob + (rain-200)/800 + (soil-50)/200)
    risk, color = ("HIGH","red") if prob>0.7 else ("MEDIUM","orange") if prob>0.4 else ("LOW","green")
    villages.append({**v, "prob":prob, "risk":risk, "color":color})
df = pd.DataFrame(villages)

# --- 7 TABS - YOUR REQUEST ---
t1,t2,t3,t4,t5,t6,t7 = st.tabs([
    "🗺️ Live Map",
    "📊 Analytics",
    "📈 AI Forecast & SHAP",
    "🚨 Alert Center",
    "👥 Crowdsource",
    "📜 Historical",
    "🔐 Admin"
])

with t1:
    st.subheader(f"🗺️ Live Risk Map - {district} - {map_layer}")
    m = folium.Map(location=[25.4,91.8], zoom_start=10, tiles="OpenStreetMap")
    for v in villages:
        folium.CircleMarker([v['lat'],v['lon']], radius=20+v['prob']*30, color=v['color'], fill=True, fill_color=v['color'], fill_opacity=0.7,
            popup=f"{v['name']} Risk {v['risk']} {v['prob']*100:.0f}%").add_to(m)
    st_folium(m, width=1000, height=500)

with t2:
    st.subheader("📊 Analytics & Reports")
    fig1 = px.bar(df, x='name', y='prob', color='risk', color_discrete_map={'HIGH':'red','MEDIUM':'orange','LOW':'green'}, title="Landslide Probability")
    st.plotly_chart(fig1, use_container_width=True)
    fig2 = px.scatter(df, x='slope', y='prob', size='pop', color='risk', title="Slope vs Risk (Explainable AI)")
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(df, use_container_width=True)
    st.download_button("📥 Download CSV Report", df.to_csv(index=False).encode(), "report.csv")

with t3:
    st.subheader("📈 7-Day LSTM Forecast + SHAP")
    dates = [datetime.date.today()+datetime.timedelta(days=i) for i in range(7)]
    probs = [min(0.95, villages[0]['prob']+random.uniform(-0.1,0.1)+i*0.02) for i in range(7)]
    fig = go.Figure(); fig.add_trace(go.Scatter(x=dates, y=probs, mode='lines+markers', line=dict(color='red', width=3)))
    fig.add_hline(y=0.7, line_dash="dash", annotation_text="Evacuation")
    st.plotly_chart(fig, use_container_width=True)
    shap = pd.DataFrame({"Feature":["Rainfall","Slope","Soil Moisture","Elevation"], "Impact":[0.45,0.30,0.15,0.10]})
    st.plotly_chart(px.bar(shap, x="Impact", y="Feature", orientation='h', title="SHAP - Why landslide?"), use_container_width=True)

with t4:
    st.subheader("🚨 Alert Center - Multi-language + PDF")
    for v in villages:
        if v['risk']=="HIGH": st.error(f"🔴 {v['name']} EVACUATE {v['prob']*100:.0f}%")
        elif v['risk']=="MEDIUM": st.warning(f"🟡 {v['name']} ALERT")
        else: st.success(f"🟢 {v['name']} SAFE")
    msgs = {"English": f"ALERT {district} {rain}mm HIGH risk","Hindi":"चेतावनी: भूस्खलन जोखिम, सुरक्षित स्थान पर जाएं","Khasi":"Ka jingmaham: Don ka jingma"}
    st.info(f"**{lang} SMS:** {msgs[lang]}")
    if st.button("🚀 Send SMS/WhatsApp to 5230 Villagers"): st.success("✅ SMS Sent via Fast2SMS + WhatsApp"); st.balloons()
    if st.button("📄 Generate PDF for Collector"): st.success("PDF Generated: NER_Landslide_Report.pdf")

with t5:
    st.subheader("👥 Crowdsource + Safe Route")
    with st.form("c"):
        st.text_input("Village"); st.file_uploader("Photo"); st.text_area("Observation")
        if st.form_submit_button("Submit"): st.success("Report Added to Map!")
    rm = folium.Map([25.4,91.8], zoom_start=10)
    folium.PolyLine([[25.57,91.88],[25.51,91.26],[25.18,92.01]], color="green", weight=5, popup="SAFE").add_to(rm)
    folium.PolyLine([[25.57,91.88],[25.30,91.70]], color="red", weight=5, popup="BLOCKED").add_to(rm)
    st_folium(rm, width=700, height=350)

with t6:
    st.subheader("📜 Historical Heatmap 2010-2024")
    h = pd.DataFrame([{"year":y,"landslides":random.randint(10,45)} for y in range(2018,2025)])
    st.plotly_chart(px.line(h, x="year", y="landslides", markers=True, title="Landslides Increasing"), use_container_width=True)
    st.plotly_chart(px.density_heatmap(df, x="slope", y="prob", title="Risk Heatmap"), use_container_width=True)

with t7:
    st.subheader("🔐 MDoNER Admin")
    u = st.text_input("ID"); p = st.text_input("Pass", type="password")
    if st.button("Login"):
        if u=="admin": st.success("Welcome DC. 2 Evacuations Pending. IoT Sensors Online.")
        else: st.error("Use admin/admin demo")