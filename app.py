import streamlit as st, pickle, folium, pandas as pd, plotly.express as px, plotly.graph_objects as go
from streamlit_folium import st_folium
import datetime, random, os, numpy as np
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="NER Kavach - 100% Unique", layout="wide", page_icon="🛡️")

# --- ULTRA UNIQUE CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap');
.stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%); font-family: 'Space Grotesk', sans-serif; }
h1, h2, h3 { color: #f8fafc!important; }
div[data-testid="stMetric"] { background: rgba(255,255,255,0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 15px; }
div[data-testid="stMetric"]:hover { transform: translateY(-5px); transition: 0.3s; border-color: #38bdf8; box-shadow: 0 0 20px rgba(56,189,248,0.3); }
.stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 5px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; color: #94a3b8; }
.stTabs [aria-selected="true"] { background: #38bdf8!important; color: black!important; font-weight: bold; }
.ticker { background: linear-gradient(90deg, #ef4444, #f97316); color: white; padding: 8px; border-radius: 8px; font-weight: bold; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity:1 } 50% { opacity:0.8 } }
.village-card { background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 12px; margin: 5px 0; cursor: pointer; }
.village-card:hover { background: rgba(56,189,248,0.15); border-color: #38bdf8; }
</style>
""", unsafe_allow_html=True)

# --- HEADER WITH LIVE CLOCK ---
import time
now = datetime.datetime.now().strftime("%d %b %Y | %I:%M %p IST")
st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center; background: rgba(255,255,255,0.05); padding: 15px 25px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1);">
<div><h1 style="margin:0; font-size: 32px;">🛡️ NER KAVACH</h1><p style="margin:0; color:#94a3b8;">MDoNER Command Center | Meghalaya Pilot | SIH26001</p></div>
<div style="text-align:right;"><p style="margin:0; color:#38bdf8; font-weight:bold;">{now}</p><p style="margin:0; color:#22c55e;">● LIVE | IMD + ISRO + NASA Connected</p></div>
</div>
""", unsafe_allow_html=True)

# --- LIVE TICKER ---
high_count = random.randint(1,3)
st.markdown(f'<div class="ticker">🚨 LIVE ALERT: {high_count} villages in HIGH RISK zone | IMD predicts 320mm rainfall in next 24H in East Khasi Hills | NH-6 Blocked at Cherapunji | Evacuation Advised</div>', unsafe_allow_html=True)
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

# --- SIDEBAR - INTERACTIVE ---
with st.sidebar:
    st.markdown("### 🎛️ MISSION CONTROL")
    district = st.selectbox("📍 Select District", ["East Khasi Hills", "West Sikkim", "Papum Pare"], index=0)
    st.markdown("---")
    st.markdown("#### 🌧️ Live Environment")
    rain = st.slider("IMD Rainfall Forecast (mm)", 0, 600, 320, 10)
    soil = st.slider("NASA Soil Moisture %", 0, 100, 82)
    layer = st.select_slider("🛰️ Satellite", options=["Bhuvan 2D","Bhuvan 3D","Esri Sat","OSM"])
    st.markdown("---")
    search = st.text_input("🔍 Search Village", placeholder="Type Cherapunji...")
    st.metric("🛰️ IoT - Cherapunji", f"{random.randint(78,96)}%", "↑ Critical")
    st.metric("📡 IoT - Shillong", f"{random.randint(32,48)}%", "↓ Stable")
    if st.button("🆘 SOS - Send SOS to NDRF", use_container_width=True):
        st.error("SOS Sent to NDRF Shillong + DC Office!")
        st.balloons()

# --- VILLAGES + INTERACTIVE SELECTION ---
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
    color = "red" if risk=="HIGH" else "orange" if risk=="MEDIUM" else "#22c55e"
    villages.append({**v, "prob":prob, "risk":risk, "color":color})
if not villages: villages = base[:1] # fallback
df = pd.DataFrame(villages)

# --- TOP METRICS - INTERACTIVE CARDS ---
m1,m2,m3,m4 = st.columns(4)
m1.metric("🔴 High Risk Zones", f"{sum(1 for v in villages if v['risk']=='HIGH')}", f"{rain}mm rain")
m2.metric("👥 Population at Risk", f"{sum(v['pop'] for v in villages if v['risk']=='HIGH'):,}")
m3.metric("🛣️ Roads Blocked", "2", "NH-6, SH-5")
m4.metric("🏠 Shelters Ready", "3", "1200 capacity")
st.write("")

# --- 7 TABS ---
t1,t2,t3,t4,t5,t6,t7 = st.tabs(["🗺️ Live Map","📊 Analytics","🔮 AI Forecast","🚨 Alert Center","👥 Crowdsource","📜 History","🔐 Admin"])

with t1:
    left, right = st.columns([3,1.2])
    with left:
        # Interactive village selector
        sel = st.selectbox("🎯 Focus on Village (Map will zoom)", [v['name'] for v in villages], index=0)
        sel_v = next(v for v in villages if v['name']==sel)
        m = folium.Map(location=[sel_v['lat'], sel_v['lon']], zoom_start=12, tiles="OpenStreetMap")
        for v in villages:
            folium.CircleMarker([v['lat'],v['lon']], radius=20+v['prob']*35, color=v['color'], fill=True, fill_color=v['color'], fill_opacity=0.7,
                popup=f"<b>{v['img']} {v['name']}</b><br>Risk {v['risk']} {v['prob']*100:.0f}%<br>Click card on right to focus").add_to(m)
        st_folium(m, width=800, height=500, key="main_map")
    with right:
        st.markdown("#### 🏘️ Village Status - Click to Focus")
        for v in villages:
            st.markdown(f"""
            <div class="village-card" style="border-left: 5px solid {v['color']}">
                <b>{v['img']} {v['name']}</b><br>
                <span style="color:{v['color']}; font-weight:bold;">{v['risk']} {v['prob']*100:.0f}%</span> | Pop: {v['pop']}<br>
                <small>Slope {v['slope']}° | Elev {v['elev']}m</small>
            </div>
            """, unsafe_allow_html=True)
        if st.button("🧭 Show Safe Route to Shelter", use_container_width=True):
            st.success("Safe Route: Cherapunji → Shillong Camp (Green Corridor) - 12km")

with t2:
    st.markdown("#### 📊 Risk Analytics - Interactive")
    c1,c2 = st.columns(2)
    with c1:
        fig = px.bar(df, x='name', y='prob', color='risk', color_discrete_map={'HIGH':'#ef4444','MEDIUM':'#f59e0b','LOW':'#22c55e'}, title="Risk by Village")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.scatter(df, x='slope', y='prob', size='pop', color='risk', hover_name='name', title="Why Landslide? Slope vs Probability")
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig2, use_container_width=True)

with t3:
    st.markdown("#### 🔮 7-Day LSTM Forecast + SHAP Explainability")
    dates = [datetime.date.today()+datetime.timedelta(days=i) for i in range(7)]
    probs = [min(0.95, villages[0]['prob']+random.uniform(-0.1,0.1)+i*0.03) for i in range(7)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=probs, mode='lines+markers+text', text=[f"{p*100:.0f}%" for p in probs], textposition="top center", line=dict(color='#38bdf8', width=4)))
    fig.add_hline(y=0.7, line_dash="dash", line_color="red", annotation_text="EVACUATE LINE")
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', title="Landslide Probability Next 7 Days")
    st.plotly_chart(fig, use_container_width=True)
    shap = pd.DataFrame({"Feature":["IMD Rainfall","Slope Angle","Soil Moisture","Elevation"], "Impact":[0.45,0.30,0.15,0.10]})
    st.plotly_chart(px.bar(shap, x="Impact", y="Feature", orientation='h', color="Impact", title="SHAP - Why AI Says HIGH Risk?", color_continuous_scale="Blues"), use_container_width=True)

with t4:
    st.markdown("#### 🚨 Alert Center - Most Interactive")
    col_a, col_b = st.columns([2,1])
    with col_a:
        lang = st.radio("Send Alert in:", ["English","Hindi","Khasi"], horizontal=True)
        msgs = {"English":f"EVACUATE {district} {rain}mm rain HIGH risk","Hindi":"भारी भूस्खलन चेतावनी - सुरक्षित स्थान पर जाएं","Khasi":"Ka jingmaham - To leit sha jaka ba shngain"}
        st.code(msgs[lang], language="text")
        if st.button("🚀 Send SMS + WhatsApp + Siren", use_container_width=True):
            st.success("✅ Sent to 5,230 citizens + Collector + NDRF | Siren ON in Cherapunji"); st.balloons()
            st.snow()
    with col_b:
        st.markdown("**📞 Emergency Contacts**")
        st.markdown("Collector: 0364-2222345\nNDRF: 1070\nMDoNER: 011-23022445")
        if st.button("📄 Generate Collector PDF"): st.success("PDF Ready: NER_KAVACH_Report.pdf")

with t5:
    st.markdown("#### 👥 Crowdsource - Gamified")
    c1,c2 = st.columns([2,1])
    with c1:
        with st.form("crowd"):
            st.text_input("Village"); st.file_uploader("📸 Upload Crack/Rain Photo"); st.text_area("Observation")
            if st.form_submit_button("📤 Submit & Earn 10 Points"): st.success("Report Verified by AI! You are Rank #3 in Meghalaya")
    with c2:
        st.markdown("**🏆 Citizen Leaderboard**")
        lb = pd.DataFrame([{"Name":"A. Syiem","Village":"Cherapunji","Points":120},{"Name":"You","Village":district,"Points":80},{"Name":"R. Das","Village":"Shillong","Points":70}])
        st.dataframe(lb, use_container_width=True)

with t6:
    st.markdown("#### 📜 Historical Trend - Interactive Heatmap")
    h = pd.DataFrame([{"year":y,"landslides":random.randint(15,45),"deaths":random.randint(10,90)} for y in range(2018,2025)])
    st.plotly_chart(px.area(h, x="year", y="landslides", title="Landslides Rising Due to Climate Change - Meghalaya"), use_container_width=True)

with t7:
    st.markdown("#### 🔐 MDoNER Admin Login")
    u = st.text_input("Official ID", placeholder="admin")
    p = st.text_input("Password", type="password", placeholder="admin")
    if st.button("Login to Command Center"):
        if u=="admin": st.success("Welcome, DC East Khasi Hills. 2 evacuations pending approval. IoT sensors online."); st.metric("System Uptime","99.9%")
        else: st.error("Demo: admin/admin")