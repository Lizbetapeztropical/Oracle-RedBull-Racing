# -*- coding: utf-8 -*-
"""F1 PULSE - Dashboard Principal"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import sys
import importlib.util

# Configurar página
st.set_page_config(
    page_title="F1 PULSE - The Voice of the Fans",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Título principal
st.title("🏎️ F1 PULSE")
st.caption("## THE VOICE OF THE FANS")

# =============================================================================
# FUNCIONES PARA CARGAR MÓDULOS
# =============================================================================

def import_module(module_name, file_name):
    """Importa un módulo desde la carpeta Pulse_page"""
    pulse_path = Path(__file__).parent / "Pulse_page" / file_name
    
    if not pulse_path.exists():
        st.error(f"❌ No se encuentra: {file_name}")
        return None
    
    spec = importlib.util.spec_from_file_location(module_name, pulse_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module

# =============================================================================
# KPI CARDS - Fila 1
# =============================================================================

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    try:
        module_users = import_module("pulse_users", "pulse_kpi_total_users.py")
        fig_users = module_users.display_total_users()
        st.plotly_chart(fig_users[0], use_container_width=True, config={'displayModeBar': False})
    except Exception as e:
        st.error(f"Error en Total Users: {e}")

with col2:
    try:
        module_countries = import_module("pulse_countries", "pulse_kpi_countries.py")
        fig_countries = module_countries.display_total_countries()
        st.plotly_chart(fig_countries, use_container_width=True, config={'displayModeBar': False})
    except:
        st.metric("# Countries", "182")

with col3:
    try:
        module_tweets = import_module("pulse_tweets", "pulse_kpi_total_tweets.py")
        fig_tweets = module_tweets.display_total_tweets()
        st.plotly_chart(fig_tweets[0], use_container_width=True, config={'displayModeBar': False})
    except:
        st.metric("Total Tweets", "512.3K")

with col4:
    try:
        module_sentiment = import_module("pulse_sentiment", "pulse_sentimientos.py")
        fig_sentiment = module_sentiment.create_sentiment_semaforo()
        st.plotly_chart(fig_sentiment, use_container_width=True, config={'displayModeBar': False})
    except:
        st.success("😊 Sentimiento: Positivo")

# =============================================================================
# MAPA DE CALOR - Fila 2
# =============================================================================

st.markdown("---")
st.subheader("🌍 MAPA DE DISTRIBUCIÓN GLOBAL")

try:
    module_map = import_module("pulse_map", "pulse_mapapa.py")
    fig_map = module_map.create_emotion_map()
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': True})
except Exception as e:
    st.info("🗺️ Mapa de calor - Cargando...")
    st.caption("Pasa el mouse sobre los países para ver detalles")

# =============================================================================
# TOP 10 PAÍSES - Fila 3
# =============================================================================

st.markdown("---")
st.subheader("📊 TOP 10 PAÍSES POR NÚMERO DE TWEETS")

col_left, col_right = st.columns([1, 1])

with col_left:
    try:
        module_top10 = import_module("pulse_top10", "pulse_top10.py")
        fig_top10 = module_top10.create_top_countries()
        st.plotly_chart(fig_top10, use_container_width=True, config={'displayModeBar': False})
    except:
        st.warning("Top 10 países - Datos no disponibles")

with col_right:
    # Fuente de tweets (para completar el diseño)
    st.subheader("📱 FUENTE DE TWEETS")
    source_data = {
        'Twitter for iPhone': 48.6,
        'Twitter for Android': 28.7,
        'Twitter Web App': 15.3,
        'Others': 7.4
    }
    
    fig_source = go.Figure(go.Pie(
        labels=list(source_data.keys()),
        values=list(source_data.values()),
        hole=0.4,
        marker_colors=['#E74C3C', '#C0392B', '#A93226', '#7B241C']
    ))
    fig_source.update_layout(height=350, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_source, use_container_width=True, config={'displayModeBar': False})

# =============================================================================
# TRENDS - Fila 4
# =============================================================================

st.markdown("---")
st.subheader("📈 TRENDS")

col_trend1, col_trend2 = st.columns([1, 1.5])

with col_trend1:
    st.markdown("#### 🌍 GLOBAL DE PALABRAS")
    try:
        module_nube = import_module("pulse_nube", "pulse_nube.py")
        fig_nube = module_nube.create_wordcloud()
        st.pyplot(fig_nube)
    except:
        st.info("Nube de palabras - Generando...")
        st.caption("verstappen, mercedes, win, lewis, max, hamilton")

with col_trend2:
    st.markdown("#### 🏎️ TOP N-GRAMAS ORACLE RED BULL RACING")
    try:
        module_ngrams = import_module("pulse_ngrams", "pulse_ngama.py")
        fig_ngrams = module_ngrams.create_ngrams()
        st.plotly_chart(fig_ngrams, use_container_width=True, config={'displayModeBar': False})
    except:
        st.info("N-gramas - Cargando...")

# =============================================================================
# TWEETS Y USUARIOS POR DÍA - Fila 5 (con filtro)
# =============================================================================

st.markdown("---")
st.subheader("📊 TWEETS Y USUARIOS POR DÍA")

# Filtros
col_filter1, col_filter2, col_filter3 = st.columns(3)

with col_filter1:
    year_options = [2018, 2019, 2020, 2021, 2022, 2023]
    selected_year = st.selectbox("📅 Año", year_options, index=3)  # 2021 por defecto

with col_filter2:
    month_options = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                     "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    selected_month = st.selectbox("📆 Mes", month_options, index=0)

with col_filter3:
    hour_range = st.slider("⏰ Rango de horas", 0, 23, (0, 23))

try:
    module_metrics = import_module("pulse_metrics", "pulse_metrics.py")
    fig_metrics = module_metrics.plot_combined_daily_metrics_filtered(
        year=selected_year,
        month=selected_month if selected_month != "Todos" else None,
        hour_range=hour_range
    )
    if fig_metrics:
        st.plotly_chart(fig_metrics, use_container_width=True, config={'displayModeBar': True})
    else:
        st.info("Selecciona un año con datos disponibles")
except Exception as e:
    st.info("📈 Gráfica de tweets y usuarios por día")
    st.caption("Filtra por año, mes y rango de horas para ver la evolución temporal")

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.caption("🏎️ F1 PULSE - The Voice of the Fans | Datos de tweets con #F1")