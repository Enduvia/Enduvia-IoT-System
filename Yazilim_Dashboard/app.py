import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import firebase_admin
from firebase_admin import credentials, db
from streamlit_autorefresh import st_autorefresh
import time

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="Canlı IoT Paneli", layout="wide", page_icon="🌐")

st.markdown("""
<style>
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- 2. FIREBASE BAĞLANTISI ---
if not firebase_admin._apps:
    cred = credentials.Certificate('firebase-admin-key.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://iot-freelance-yolculugu-default-rtdb.europe-west1.firebasedatabase.app/' 
    })

# --- 3. CANLI YENİLEME VE HAFIZA ---
st_autorefresh(interval=5000, key="iot_live_refresh")

if 'canli_tablo' not in st.session_state:
    st.session_state.canli_tablo = pd.DataFrame(columns=['Tarih', 'Zaman', 'DHT11 (Sıcaklık)', 'DHT11 (Nem)', 'LDR (Işık)'])

def verileri_cek():
    ref = db.reference('/enduvia_verileri')
    gelen = ref.get()
    
    if gelen:
        yeni_satir = {
            'Tarih': time.strftime('%d.%m.%Y'),
            'Zaman': time.strftime('%H:%M:%S'),
            'DHT11 (Sıcaklık)': float(gelen.get('sicaklik', 0)),
            'DHT11 (Nem)': float(gelen.get('nem', 0)),
            'LDR (Işık)': float(gelen.get('isik', 0))
        }
        
        if not st.session_state.canli_tablo.empty and st.session_state.canli_tablo.iloc[-1]['Zaman'] == yeni_satir['Zaman']:
            pass
        else:
            st.session_state.canli_tablo = pd.concat([st.session_state.canli_tablo, pd.DataFrame([yeni_satir])], ignore_index=True)
        
        # Son 100 kaydı tutalım
        if len(st.session_state.canli_tablo) > 100:
            st.session_state.canli_tablo = st.session_state.canli_tablo.tail(100)

verileri_cek()

# --- 4. YAN MENÜ (SIDEBAR) ---
st.sidebar.title("🎛️ Kontrol Paneli")
sensor_opsiyon = ["DHT11 (Sıcaklık)", "DHT11 (Nem)", "LDR (Işık)"]
secilenler = st.sidebar.multiselect("İzlenecek Sensörler:", options=sensor_opsiyon, default=sensor_opsiyon)

st.sidebar.markdown("---")
st.sidebar.markdown("*📈 Görselleştirme Stili*")
cizgi_stili = st.sidebar.selectbox("Grafik Türü:", ["Akıcı Çizgi", "Keskin Çizgi"], label_visibility="collapsed")

df = st.session_state.canli_tablo

# --- 5. ANA EKRAN DÜZENİ ---
st.markdown("<h2 style='text-align: center; color: #0F172A;'>🌐 SYNAPSE - Gerçek Zamanlı Donanım Akış Paneli</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if not df.empty and secilenler:
    # ÜST SATIR: Sol tarafta Göstergeler (Ortalamalar), Sağ tarafta Bar Chart
    ust_sol, ust_sag = st.columns([6, 4])
    
    with ust_sol:
        g_cols = st.columns(len(secilenler))
        
        for idx, s_ad in enumerate(secilenler):
            # BURASI DÜZELTİLDİ: Anlık değer yerine tablodaki o sütunun ortalaması alındı
            ortalama_deger = df[s_ad].mean() 
            
            if "Sıcaklık" in s_ad: limit, renk, birim = 50, "#E11D48", "°C"
            elif "Nem" in s_ad: limit, renk, birim = 100, "#2563EB", "%"
            else: limit, renk, birim = 1500, "#D97706", "lux"
            
            with g_cols[idx]:
                fig_g = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=ortalama_deger, # Ortalama değer buraya eklendi
                    title={'text': f"Ort. {s_ad.split(' ')[0]}", 'font': {'size': 14, 'color': '#64748B'}},
                    number={'valueformat': '.1f', 'suffix': f" {birim}", 'font': {'size': 22, 'color': '#0F172A'}}, # Kusursuz yuvarlama eklendi
                    gauge={'axis': {'range': [None, limit]}, 'bar': {'color': renk}, 'bgcolor': "white", 'borderwidth': 1, 'bordercolor': "#E2E8F0"}
                ))
                fig_g.update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_g, use_container_width=True)

    with ust_sag:
        st.markdown("<p style='font-weight: 600; color: #334155; text-align: center;'>Sensör Min-Max Değerleri</p>", unsafe_allow_html=True)
        # Bar chart için veriyi hazırlama
        df_melted = df.melt(id_vars=['Zaman'], value_vars=secilenler, var_name='Sensör', value_name='Değer')
        df_agg = df_melted.groupby("Sensör")["Değer"].agg(['min', 'max']).reset_index()
        df_bar_data = df_agg.melt(id_vars="Sensör", var_name="Limit", value_name="Değer")
        
        fig_bar = px.bar(df_bar_data, x="Sensör", y="Değer", color="Limit", barmode="group", color_discrete_sequence=["#1E3A8A", "#D97706"])
        fig_bar.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0), legend=dict(orientation="h", y=-0.3, title=""))
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # ALT SATIR: Sol tarafta Çizgi Grafiği, Sağ tarafta Tablo
    alt_sol, alt_sag = st.columns([6, 4])
    
    with alt_sol:
        st.markdown("<p style='font-weight: 600; color: #334155;'>Canlı Sensör Dalgalanmaları (Son 100 Kayıt)</p>", unsafe_allow_html=True)
        fig_dual = go.Figure()
        grafik_sekli = 'spline' if "Akıcı" in cizgi_stili else 'linear'

        if "DHT11 (Nem)" in secilenler:
            fig_dual.add_trace(go.Scatter(x=df["Zaman"], y=df["DHT11 (Nem)"], name="Nem (%)", line=dict(color="#2563EB", width=2, shape=grafik_sekli)))

        if "DHT11 (Sıcaklık)" in secilenler:
            fig_dual.add_trace(go.Scatter(x=df["Zaman"], y=df["DHT11 (Sıcaklık)"], name="Sıcaklık (°C)", line=dict(color="#E11D48", width=3, dash='dot', shape=grafik_sekli)))

        if "LDR (Işık)" in secilenler:
            fig_dual.add_trace(go.Scatter(x=df["Zaman"], y=df["LDR (Işık)"], name="Işık (Lux)", line=dict(color="#D97706", width=2, shape=grafik_sekli), yaxis="y2"))

        fig_dual.update_layout(
            height=300, margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
            plot_bgcolor="white",
            yaxis=dict(title="Sıcaklık & Nem", side="left", showgrid=True, gridcolor='#F1F5F9'),
            yaxis2=dict(title="Işık Şiddeti", side="right", overlaying="y", showgrid=False, anchor="x")
        )
        st.plotly_chart(fig_dual, use_container_width=True)

    with alt_sag:
        st.markdown("<p style='font-weight: 600; color: #334155;'>Veritabanı Logları (Ham Veri)</p>", unsafe_allow_html=True)
        display_columns = ['Tarih', 'Zaman'] + secilenler
        display_df = df[display_columns].sort_index(ascending=False)
        st.dataframe(display_df, use_container_width=True, height=300)

# Veritabanında veri yoksa görünecek kısım
if df.empty:
    st.info("🔌 Firebase bağlantısı bekleniyor... Lütfen donanımı aktif edin.")
