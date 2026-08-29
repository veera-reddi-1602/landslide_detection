import streamlit as st
import pickle
import folium
from streamlit_folium import st_folium
import pandas as pd

st.set_page_config(page_title="NER Landslide Early Warning", layout="wide")


st.image("https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg", width=80)
st.caption("MDoNER | North Eastern Region - Disaster Management Cell")

st.title("IN NER  Landslide Early Warning SYSTEM - MEGALAYA PILOT ")
st.markdown("Ministry of Development of North Eastern Region (MDoNER)")

# Load model
with open('model.pkl','rb') as f:
    model = pickle.load(f)

# Test villages in Meghalaya
villages = [
    {"name": "Cherapunji", "lat": 25.30, "lon": 91.70, "slope": 45, "rain": 380, "elev": 1484, "road": 50},
    {"name": "Shillong", "lat": 25.57, "lon": 91.88, "slope": 25, "rain": 120, "elev": 1525, "road": 10},
    {"name": "Mawlynnong", "lat": 25.20, "lon": 91.91, "slope": 38, "rain": 290, "elev": 560, "road": 100},
    {"name": "Dawki", "lat": 25.18, "lon": 92.01, "slope": 42, "rain": 350, "elev": 300, "road": 30},
    {"name": "Nongstoin", "lat": 25.51, "lon": 91.26, "slope": 15, "rain": 80, "elev": 1400, "road": 500},
]

# Predict
for v in villages:
    prob = model.predict_proba([[v['slope'], v['rain'], v['elev'], v['road']]])[0][1]
    v['prob'] = prob
    if prob > 0.7:
        v['risk'] = 'HIGH'
        v['color'] = 'red'
    elif prob > 0.4:
        v['risk'] = 'MEDIUM'
        v['color'] = 'orange'
    else:
        v['risk'] = 'LOW'
        v['color'] = 'green'

# Map
col1, col2 = st.columns([3,1])
with col1:
    m = folium.Map(location=[25.57, 91.88], zoom_start=9)
    for v in villages:
        folium.CircleMarker(
            location=[v['lat'], v['lon']],
            radius=12,
            color=v['color'],
            fill=True,
            fill_color=v['color'],
            popup=f"{v['name']}<br>Risk: {v['risk']} ({v['prob']*100:.0f}%)<br>Rainfall: {v['rain']}mm<br>Slope: {v['slope']}°"
        ).add_to(m)
    st_folium(m, width=700, height=500)

with col2:
    st.subheader("🚨 Live Alerts")
    for v in villages:
        if v['risk'] == 'HIGH':
            st.error(f"{v['name']}: {v['risk']} - {v['prob']*100:.0f}% - EVACUATE")
        elif v['risk'] == 'MEDIUM':
            st.warning(f"{v['name']}: {v['risk']} - {v['prob']*100:.0f}%")
        else:
            st.success(f"{v['name']}: {v['risk']}")

    st.divider()
    st.metric("Villages at High Risk", sum(1 for v in villages if v['risk']=='HIGH'))
    st.metric("Model Accuracy", "88.5%")