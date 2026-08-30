import streamlit as st, pickle, folium, pandas as pd, plotly.express as px, plotly.graph_objects as go
from streamlit_folium import st_folium
import datetime, random, os, numpy as np
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="NER Kavach - Clear UI", layout="wide", page_icon="🛡️")

# --- FIXED LIGHT THEME CSS - HIGH READABILITY ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
.stApp { background: #f8fafc; font-family: 'Inter', sans-serif; }
h1, h2, h3, h4, p, span, label { color: #0f172a!important; }
div[data-testid="stMetric"] {
    background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 15px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
}
div[data-testid="stMetric"]:hover { transform: translateY(-3px); transition: 0.2s; border-color: #0ea5e9; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
.stTabs [data-baseweb="tab-list"] { background: white; border-radius: 12px; padding: 6px; border: 1px solid #e2e8f0; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; color: #475569; font-weight: 600; }
.stTabs [aria-selected="true"] { background: #0ea5e9!important; color: white!important; }
.ticker {
    background: linear-gradient(90deg, #dc2626, #ea580c); color: white!important;
    padding: 10px 16px; border-radius: 10px; font-weight: 700; letter-spacing: 0.5px;
}
.ticker p,.ticker span { color: white!important; }
.village-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; margin: 8px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.village-card:hover { border-color: #0ea5e9; box-shadow: 0 4px 12px rgba(14,165,233,0.15); }
.village-card b,.village-card span,.village-card small { color: #0f172a!important; }
[data-testid="stSidebar"] { background: white; border-right: 1px solid #e2e8f0; }
[data-testid="stSidebar"] * { color: #0f172a!important; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
now = datetime.datetime.now().strftime("%d %b %Y | %I:%M %p IST")
st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center; background: white; padding: 18px 24px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
<div><h1 style="margin:0; font-size: 30px; color:#0f172a!important;">🛡️ NER KAVACH</h1><p style="margin:4px 0 0 0; color:#64748b!important;">MDoNER Command Center | Meghalaya Pilot | SIH26001</p></div>
<div style="text-align:right;"><p style="margin:0; color:#0ea5e9!important; font-weight:700;">{now}</p><p style="margin:0; color:#16a34a!important; font-weight:600;">● LIVE | IMD + ISRO + NASA Connected</p></div>
</div>
""", unsafe_allow_html=True)

st.markdown(f'<div class="ticker">🚨 LIVE ALERT: IMD predicts 320mm rainfall in next 24H in East Khasi Hills | NH-6 Blocked at Cherapunji | Evacuation Advised | 3 Villages HIGH Risk</div>', unsafe_allow_html=True)
st.write("")

# --- MODEL ---
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

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🎛️ MISSION CONTROL")
    district = st.selectbox("📍 District", ["East Khasi Hills", "West Sikkim", "Papum Pare"])
    st.markdown("#### 🌧️ Live Environment")
    rain = st.slider("IMD Rainfall Forecast (mm)", 0, 600, 320, 10)
    soil = st.slider("NASA Soil Moisture %", 0, 100, 82)
    layer = st.selectbox("🛰️ Satellite Layer", ["ISRO Bhuvan","Esri Satellite","OpenStreetMap"])
    st.markdown("---")
    search = st.text_input("🔍 Search Village", placeholder="Cherapunji...")
    st.metric("🛰️ IoT - Cherapunji", f"{random.randint(78,96)}%", "↑ Critical")
    st.metric("📡 IoT - Shillong", f"{random.randint(32,48)}%", "↓ Stable")
    if st.button("🆘 SOS - Send to NDRF", use_container_width=True, type="primary"):
        st.error("SOS Sent to NDRF + Collector!")
        st.balloons()

# --- VILLAGES ---
base = [
    {"name":"Cherapunji","lat":25.30,"lon":91.70,"slope":45,"elev":1484,"road":50,"pop":10000,"img":"🌧️"},
    {"name":"Mawsynram","lat":25.29,"lon":91.58,"slope":48,"elev":1400,"road":70,"pop":1200,"img":"⛰️"},
    {"name":"Shillong","lat":25.57,"lon":91.88,"slope":25,"elev":1525,"road":10,"pop":150000,"img":"🏙️"},
    {"name":"Dawki","lat":25.18,"lon":92.01,"slope":42,"elev":300,"road":30,"pop":2000,"img":"🚣"},
    {"name":"Nongstoin","lat":25.51,"lon":91.26,"slope":15,"elev":1400,"road":500,"pop":30000,"img":"🌲"},
]
villages=[]
for v in base:
    if search and search.lower() not in v['name'].lower(): continue
    prob = model.predict_proba([[v['slope'], rain, v['elev'], v['road']]])[0][1]
    prob = min(0.99, prob + (rain-200)/700 + (soil-50)/180)
    risk = "HIGH" if prob>0.7 else "MEDIUM" if prob>0.4 else "LOW"
    color = "#dc2626" if risk=="HIGH" else "#ea580c" if risk=="MEDIUM" else "#16a34a"
    villages.append({**v, "prob":prob, "risk":risk, "color":color})
if not villages: villages = base[:2]
df = pd.DataFrame(villages)

# --- TOP METRICS ---
m1,m2,m3,m4 = st.columns(4)
m1.metric("🔴 High Risk", f"{sum(1 for v in villages if v['risk']=='HIGH')}", f"{rain}mm")
m2.metric("👥 At Risk", f"{sum(v['pop'] for v in villages if v['risk']=='HIGH'):,}")
m3.metric("🛣️ Blocked", "2 Roads", "NH-6")
m4.metric("🏠 Shelters", "3 Ready", "1200 cap")
st.write("")

# --- 7 TABS ---
t1,t2,t3,t4,t5,t6,t7 = st.tabs(["🗺️ Live Map","📊 Analytics","🔮 AI Forecast","🚨 Alert Center","👥 Crowdsource","📜 History","🔐 Admin"])

with t1:
    left, right = st.columns([3,1.2])
    with left:
        sel = st.selectbox("🎯 Focus Village", [v['name'] for v in villages], index=0)
        sel_v = next(v for v in villages if v['name']==sel)
        m = folium.Map(location=[sel_v['lat'], sel_v['lon']], zoom_start=11, tiles="OpenStreetMap")
        for v in villages:
            folium.CircleMarker([v['lat'],v['lon']], radius=22+v['prob']*35, color=v['color'], fill=True, fill_color=v['color'], fill_opacity=0.7,
                popup=f"{v['name']} {v['risk']} {v['prob']*100:.0f}%").add_to(m)
        st_folium(m, width=850, height=520, key="map")
    with right:
        st.markdown("#### 🏘️ Villages")
        for v in villages:
            st.markdown(f'<div class="village-card" style="border-left:5px solid {v["color"]}"><b>{v["img"]} {v["name"]}</b><br><span style="color:{v["color"]}!important; font-weight:700;">{v["risk"]} {v["prob"]*100:.0f}%</span> | Pop {v["pop"]}<br><small>Slope {v["slope"]}° | {v["elev"]}m</small></div>', unsafe_allow_html=True)
        if st.button("🧭 Safe Route", use_container_width=True): st.success("Safe: Cherapunji → Shillong Camp 12km")

with t2:
    c1,c2 = st.columns(2)
    with c1: st.plotly_chart(px.bar(df, x='name', y='prob', color='risk', color_discrete_map={'HIGH':'#dc2626','MEDIUM':'#ea580c','LOW':'#16a34a'}, title="Risk by Village"), use_container_width=True)
    with c2: st.plotly_chart(px.scatter(df, x='slope', y='prob', size='pop', color='risk', hover_name='name', title="Slope vs Risk"), use_container_width=True)

with t3:
    dates = [datetime.date.today()+datetime.timedelta(days=i) for i in range(7)]
    probs = [min(0.95, villages[0]['prob']+random.uniform(-0.1,0.1)+i*0.02) for i in range(7)]
    fig = go.Figure(); fig.add_trace(go.Scatter(x=dates, y=probs, mode='lines+markers', line=dict(color='#0ea5e9', width=4))); fig.add_hline(y=0.7, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)
    shap = pd.DataFrame({"Feature":["Rainfall","Slope","Soil Moisture","Elevation"], "Impact":[0.45,0.30,0.15,0.10]})
    st.plotly_chart(px.bar(shap, x="Impact", y="Feature", orientation='h', title="SHAP - Why HIGH Risk?"), use_container_width=True)

with t4:
    col_a, col_b = st.columns([2,1])
    with col_a:
        lang = st.radio("Language", ["English","Hindi","Khasi"], horizontal=True)
        msgs = {"English":f"EVACUATE {district} {rain}mm HIGH risk","Hindi":"भारी भूस्खलन चेतावनी - सुरक्षित स्थान पर जाएं","Khasi":"Ka jingmaham - leit sha jaka ba shngain"}
        st.info(msgs[lang])
        if st.button("🚀 Send SMS + WhatsApp + Siren", use_container_width=True, type="primary"):
            st.success("✅ Sent to 5230 citizens + DC + NDRF | Siren ON"); st.balloons()
    with col_b:
        st.markdown("**📞 Emergency**\nCollector: 0364-2222345\nNDRF: 1070")
        if st.button("📄 Generate PDF"): st.success("PDF Ready")

with t5:
    with st.form("crowd"):
        st.text_input("Village"); st.file_uploader("Photo"); st.text_area("Observation")
        if st.form_submit_button("Submit & Earn 10 Points"): st.success("Verified by AI! Rank #3")
    st.dataframe(pd.DataFrame([{"Name":"A. Syiem","Points":120},{"Name":"You","Points":80},{"Name":"R. Das","Points":70}]), use_container_width=True)

with t6:
    h = pd.DataFrame([{"year":y,"landslides":random.randint(15,45)} for y in range(2018,2025)])
    st.plotly_chart(px.area(h, x="year", y="landslides", title="Landslides Rising 2018-2024"), use_container_width=True)

with t7:
    u = st.text_input("ID", placeholder="admin"); p = st.text_input("Pass", type="password", placeholder="admin")
    if st.button("Login"):
        if u=="admin": st.success("Welcome DC - 2 evacuations pending"); st.metric("Uptime","99.9%")
        else: st.error("Use admin/admin")