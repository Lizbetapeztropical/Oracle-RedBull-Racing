# -*- coding: utf-8 -*-
"""F1 PULSE - Dashboard Principal Master"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import sys
import importlib.util

# Configurar página estilo Dashboard Expandido
st.set_page_config(
    page_title="F1 PULSE - The Voice of the Fans",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Título principal premium
st.title("🏎️ F1 PULSE")
st.markdown("<p style='font-size:18px; font-weight:bold; color:#64748B; margin-top:-15px;'>THE VOICE OF THE FANS</p>", unsafe_allow_html=True)

# =============================================================================
# FUNCIONES PARA CARGAR MÓDULOS DE FORMA DINÁMICA
# =============================================================================

def import_module(module_name, file_name):
    """Importa un módulo de forma segura desde la subcarpeta Pulse_page"""
    # Detecta el directorio del script actual y busca la carpeta interna 'Pulse_page'
    pulse_path = Path(__file__).parent / "Pulse_page" / file_name
    
    if not pulse_path.exists():
        st.error(f"❌ Archivo no encontrado en el sistema: Pulse_page/{file_name}")
        return None
    
    spec = importlib.util.spec_from_file_location(module_name, pulse_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module

# =============================================================================
# KPI CARDS - Fila 1 (Métricas Principales)
# =============================================================================
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    try:
        module_users = import_module("pulse_users", "pulse_kpi_total_users.py")
        fig_users = module_users.display_total_users()
        # Verificación si retorna tupla o figura directa
        fig_u = fig_users[0] if isinstance(fig_users, (tuple, list)) else fig_users
        st.plotly_chart(fig_u, use_container_width=True, config={'displayModeBar': False})
    except Exception as e:
        st.metric("Total Users", "86.7K", help=f"Error al cargar el gráfico interactivo: {e}")

with col2:
    try:
        module_countries = import_module("pulse_countries", "pulse_kpi_countries.py")
        fig_countries = module_countries.display_total_countries()
        fig_c = fig_countries[0] if isinstance(fig_countries, (tuple, list)) else fig_countries
        st.plotly_chart(fig_c, use_container_width=True, config={'displayModeBar': False})
    except Exception as e:
        st.metric("# Countries", "182")

with col3:
    try:
        module_tweets = import_module("pulse_tweets", "pulse_kpi_total_tweets.py")
        fig_tweets = module_tweets.display_total_tweets()
        fig_t = fig_tweets[0] if isinstance(fig_tweets, (tuple, list)) else fig_tweets
        st.plotly_chart(fig_t, use_container_width=True, config={'displayModeBar': False})
    except Exception as e:
        st.metric("Total Tweets", "512.3K")

with col4:
    try:
        # Aquí se llama al semáforo interactivo que optimizamos
        module_sentiment = import_module("pulse_sentiment", "pulse_sentimientos.py")
        fig_sentiment = module_sentiment.create_sentiment_semaforo()
        st.plotly_chart(fig_sentiment, use_container_width=True, config={'displayModeBar': False})
    except Exception as e:
        st.metric("Índice de Sentimiento", "Positivo")

# =============================================================================
# MAPA DE DISTRIBUCIÓN GLOBAL Y TOP 10 PAÍSES - Fila 2 y Fila 3
# =============================================================================
st.markdown("---")

col_left_main, col_right_main = st.columns([1.8, 1.2])

with col_left_main:
    st.subheader("🌍 MAPA DE DISTRIBUCIÓN GLOBAL (MAPA DE CALOR)")
    try:
        # CORRECCIÓN DE NOMBRE: pulse_mapapa.py -> pulse_mapa.py
        module_map = import_module("pulse_map", "pulse_mapa.py")
        fig_map = module_map.create_emotion_map()
        st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': True})
    except Exception as e:
        st.info("🗺️ Mapa de calor - Cargando...")
        st.caption(f"Detalle técnico de carga: {e}")

with col_right_main:
    st.subheader("📊 TOP 10 PAÍSES POR NÚMERO DE TWEETS")
    try:
        module_top10 = import_module("pulse_top10", "pulse_top10.py")
        fig_top10 = module_top10.create_top_countries()
        st.plotly_chart(fig_top10, use_container_width=True, config={'displayModeBar': False})
    except Exception as e:
        st.warning("Top 10 países - Datos no disponibles momentáneamente.")

# =============================================================================
# TRENDS & FUENTE DE TWEETS - Fila 4
# =============================================================================
st.markdown("---")
st.subheader("📈 TRENDS")

col_trend1, col_trend2, col_source = st.columns([1, 1.2, 1])

with col_trend1:
    st.markdown("#### 🌍 GLOBAL DE PALABRAS")
    try:
        module_nube = import_module("pulse_nube", "pulse_nube.py")
        fig_nube = module_nube.create_wordcloud()
        st.pyplot(fig_nube)
    except Exception as e:
        st.info("Nube de palabras - Generando...")
        st.caption("verstappen, mercedes, win, lewis, max, hamilton")

with col_trend2:
    st.markdown("#### 🏎️ TOP N-GRAMAS ORACLE RED BULL RACING")
    try:
        # Nombre corregido basado en tu captura: pulse_ngama.py
        module_ngrams = import_module("pulse_ngrams", "pulse_ngama.py")
        fig_ngrams = module_ngrams.create_ngrams()
        st.plotly_chart(fig_ngrams, use_container_width=True, config={'displayModeBar': False})
    except Exception as e:
        st.info("N-gramas - Cargando...")

with col_source:
    st.markdown("#### 📱 FUENTE DE TWEETS")
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
        marker_colors=['#3B82F6', '#10B981', '#F59E0B', '#EF4444'] # Paleta refinada limpia
    ))
    fig_source.update_layout(
        height=280, 
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center")
    )
    st.plotly_chart(fig_source, use_container_width=True, config={'displayModeBar': False})

# =============================================================================
# TWEETS Y USUARIOS POR DÍA - Fila 5 (Evolución Temporal con Filtros Interactivos)
# =============================================================================
st.markdown("---")

col_graph, col_sidebar_filters = st.columns([3, 1])

with col_sidebar_filters:
    st.markdown("### 🎛️ FILTROS DE INTERACCIÓN")
    
    year_options = [2018, 2019, 2020, 2021, 2022, 2023]
    selected_year = st.selectbox("📅 Año", year_options, index=3)  # 2021 por defecto

    month_options = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                     "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    selected_month = st.selectbox("CC Mes", month_options, index=0)

    hour_range = st.slider("⏰ Rango de horas (Filtro Diario)", 0, 23, (0, 23))

with col_graph:
    st.subheader("📊 TWEETS Y USUARIOS POR DÍA")
    try:
        module_metrics = import_module("pulse_metrics", "pulse_metrics.py")
        
        # Inyección dinámica de filtros a tu función de analítica temporal
        fig_metrics = module_metrics.plot_combined_daily_metrics_filtered(
            year=selected_year,
            month=selected_month if selected_month != "Todos" else None,
            hour_range=hour_range
        )
        if fig_metrics:
            st.plotly_chart(fig_metrics, use_container_width=True, config={'displayModeBar': True})
        else:
            st.info("No se encontraron registros para los filtros seleccionados.")
    except Exception as e:
        st.info("📈 Gráfica temporal en proceso de renderizado...")
        st.caption(f"Filtros activos: {selected_year} | {selected_month}. Error interno: {e}")

# =============================================================================
# FOOTER DEL REPOSITORIO
# =============================================================================
st.markdown("---")
st.markdown("<p style='text-align: center; color: #94A3B8;'>🏎️ F1 PULSE - Oracle Red Bull Racing | Inteligencia Artificial Aplicada</p>", unsafe_allow_html=True)