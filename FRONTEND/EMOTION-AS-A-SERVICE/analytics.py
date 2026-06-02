import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
import joblib
import torch
import torch.nn as nn
import sys
import importlib.util


# ==================================================
# ARQUITECTURA DEL MODELO PYTORCH
# ==================================================

class F1NeuralNetwork(nn.Module):
    def __init__(self, input_size):
        super(F1NeuralNetwork, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.40),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.35),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.30),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
    
    def forward(self, x):
        return self.network(x)


# ==================================================
# FUNCIÓN PARA IMPORTAR MÓDULOS DE PULSE PAGE
# ==================================================

def import_pulse_module(module_name, file_name):
    """Importa un módulo de forma segura desde la subcarpeta Pulse_page"""
    pulse_path = Path(__file__).parent / "Pulse_page" / file_name
    
    if not pulse_path.exists():
        return None
    
    spec = importlib.util.spec_from_file_location(module_name, pulse_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module


# ==================================================
# SECCIÓN 1: RED BULL ANALYTICS (Modelos sklearn)
# ==================================================

def show_analytics():

    st.markdown("""
    <h1 style='text-align:center; color:#E10600; font-family: "Titillium Web", sans-serif;'>
        RED BULL ANALYTICS
    </h1>
    <p style='text-align:center; color:#C0C0C0;'>Performance + Predictive Intelligence</p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # ==================================================
    # RUTAS
    # ==================================================
    
    BASE_DIR = Path(__file__).resolve().parent
    MODELING_DIR = BASE_DIR.parent.parent / "BACKEND" / "MODELING"
    RAWDATA_DIR = BASE_DIR.parent.parent / "BACKEND" / "RAWDATA" / "DATA" / "Merged"
    
    # ==================================================
    # CARGAR DATASET (merged_dataset.csv)
    # ==================================================
    
    csv_path = RAWDATA_DIR / "merged_dataset.csv"
    
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        st.success(f"✅ Datos cargados desde merged_dataset.csv ({len(df)} filas)")
    else:
        st.error(f"❌ No se encontró merged_dataset.csv")
        st.stop()

    # ==================================================
    # FEATURES - COLUMNAS NUMÉRICAS DISPONIBLES
    # ==================================================
    
    candidate_features = [
        "POINTS", "LAPS", "MILLISECONDS", "WEATHER_cloudy",
        "OVERTAKEN_POSITIONS_TOTAL", "DNF_COUNT", "LAPMEAN",
        "PS_COUNT", "SC_COUNT"
    ]
    
    features = [f for f in candidate_features if f in df.columns]
    
    if not features:
        st.error("❌ No hay features numéricas disponibles")
        st.stop()
    
    st.info(f"📊 Features utilizadas: {len(features)} columnas")

    # ==================================================
    # CARGAR MODELOS (sin PyTorch)
    # ==================================================
    
    models = {}
    
    st.info("📦 Cargando modelos pre-entrenados...")
    
    # Regresión Lineal
    linear_path = MODELING_DIR / "linear_regression_model.pkl"
    if linear_path.exists():
        models["Regresión Lineal"] = joblib.load(linear_path)
        st.success("✅ Regresión Lineal")
    
    # MLP
    mlp_path = MODELING_DIR / "mlp_score_model.pkl"
    if mlp_path.exists():
        models["MLP"] = joblib.load(mlp_path)
        st.success("✅ MLP")
    
    # SVM
    svm_path = MODELING_DIR / "svm_regression_model.pkl"
    if svm_path.exists():
        models["SVM"] = joblib.load(svm_path)
        st.success("✅ SVM")
    
    # XGBoost
    xgb_path = MODELING_DIR / "xgboost_regression_model.pkl"
    if xgb_path.exists():
        models["XGBoost"] = joblib.load(xgb_path)
        st.success("✅ XGBoost")
    
    if not models:
        st.error("❌ No se encontraron modelos")
        st.stop()
    
    st.info(f"📊 Modelos disponibles: {', '.join(models.keys())}")

    # ==================================================
    # SIDEBAR FILTROS
    # ==================================================
    
    st.sidebar.markdown("### 🔎 FILTROS")
    
    if 'YEAR' not in df.columns and 'NAME_YEAR' in df.columns:
        df['YEAR'] = pd.to_numeric(df['NAME_YEAR'].astype(str).str[:4], errors='coerce')
    elif 'YEAR' not in df.columns:
        df['YEAR'] = 2023
    
    available_years = sorted([y for y in df['YEAR'].unique() if pd.notna(y)])
    if not available_years:
        available_years = [2023]
    year_choice = st.sidebar.selectbox("Año", available_years)
    
    st.sidebar.markdown("### 🤖 MODELO")
    model_choice = st.sidebar.selectbox("Algoritmo", list(models.keys()))

    # ==================================================
    # FILTRAR Y PREDECIR
    # ==================================================
    
    filtered_df = df[df['YEAR'] == year_choice].copy()
    
    if filtered_df.empty:
        st.warning(f"No hay datos para {year_choice}")
        st.stop()
    
    input_data = filtered_df[features].copy().dropna()
    
    if input_data.empty:
        st.warning("No hay datos válidos")
        st.stop()
    
    model = models.get(model_choice)
    
    try:
        preds = model.predict(input_data)
        
        filtered_df.loc[input_data.index, 'Prediction'] = preds[:len(filtered_df)]
        
        avg_real = round(filtered_df['SCORE'].mean(), 2) if 'SCORE' in filtered_df.columns else 0
        avg_pred = round(float(preds[:len(filtered_df)].mean()), 2)
        total = len(filtered_df)
        
    except Exception as e:
        st.error(f"Error en predicción: {str(e)[:200]}")
        st.stop()

    # ==================================================
    # KPIS
    # ==================================================
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total Registros", total)
    with col2: st.metric("Score Real Promedio", avg_real)
    with col3: st.metric("Score Predicho Promedio", avg_pred)
    
    st.markdown("---")

    # ==================================================
    # GRÁFICO
    # ==================================================
    
    st.subheader(f"Score Real vs Score Predicho - {year_choice}")
    
    if 'NAME_YEAR' in filtered_df.columns:
        labels = filtered_df['NAME_YEAR'].astype(str)
    else:
        labels = list(range(1, len(filtered_df) + 1))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=filtered_df['SCORE'] if 'SCORE' in filtered_df.columns else [0]*len(filtered_df),
        mode='lines+markers', name='Real',
        line=dict(color='#E10600', width=2),
        marker=dict(color='#E10600', size=6)
    ))
    fig.add_trace(go.Scatter(
        x=labels, y=filtered_df['Prediction'],
        mode='lines+markers', name='Predicho',
        line=dict(color='#FFD700', width=2, dash='dash'),
        marker=dict(color='#FFD700', size=6, symbol='diamond')
    ))
    fig.update_layout(
        xaxis_title="Carrera",
        yaxis_title="Score",
        template="plotly_dark",
        paper_bgcolor="#0A0F1F",
        plot_bgcolor="#151520",
        font=dict(color="white"),
        xaxis=dict(tickangle=45)
    )
    st.plotly_chart(fig, use_container_width=True)

    # ==================================================
    # TABLA
    # ==================================================
    
    with st.expander("Ver datos detallados"):
        if 'NAME_YEAR' in filtered_df.columns and 'SCORE' in filtered_df.columns:
            display = filtered_df[['NAME_YEAR', 'SCORE', 'Prediction']].dropna()
            display.columns = ['Carrera', 'Score Real', 'Score Predicho']
        else:
            display = filtered_df[['Prediction']].dropna()
            display.columns = ['Score Predicho']
        st.dataframe(display, use_container_width=True)

    st.markdown("""
    <div style="text-align: center; padding: 1rem; margin-top: 2rem; border-top: 1px solid #C0C0C0;">
        Red Bull Analytics - Powered by Machine Learning
    </div>
    """, unsafe_allow_html=True)


# ==================================================
# SECCIÓN 2: PYTORCH FOR PREDICTION
# ==================================================

def show_pytorch_page():
    """Página dedicada al modelo PyTorch Neural Network"""

    st.markdown("""
    <h1 style='text-align:center; color:#E10600; font-family: "Titillium Web", sans-serif;'>
        PYTORCH NEURAL NETWORK
    </h1>
    <p style='text-align:center; color:#C0C0C0;'>Deep Learning Model for Score Prediction</p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # ==================================================
    # RUTAS
    # ==================================================
    
    BASE_DIR = Path(__file__).resolve().parent
    MODELING_DIR = BASE_DIR.parent.parent / "BACKEND" / "MODELING"
    PYTORCH_DIR = MODELING_DIR / "pytorch"
    RAWDATA_DIR = BASE_DIR.parent.parent / "BACKEND" / "RAWDATA" / "DATA" / "Merged"
    
    # ==================================================
    # CARGAR DATASET
    # ==================================================
    
    csv_path = RAWDATA_DIR / "merged_dataset.csv"
    
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        st.success(f"✅ Datos cargados ({len(df)} filas)")
    else:
        st.error(f"❌ No se encontró merged_dataset.csv")
        st.stop()

    # ==================================================
    # CARGAR MODELO PYTORCH
    # ==================================================
    
    st.info("📦 Cargando modelo PyTorch...")
    
    # Cargar scaler
    scaler_path = PYTORCH_DIR / "f1_scaler.pkl"
    if scaler_path.exists():
        scaler = joblib.load(scaler_path)
        st.success("✅ Scaler cargado")
    else:
        st.error("❌ No se encontró f1_scaler.pkl")
        st.stop()
    
    # Cargar features
    features_path = PYTORCH_DIR / "f1_features.pkl"
    if features_path.exists():
        features = joblib.load(features_path)
        st.success(f"✅ Features cargadas ({len(features)} columnas)")
    else:
        st.error("❌ No se encontró f1_features.pkl")
        st.stop()
    
    # Cargar modelo
    model_path = PYTORCH_DIR / "f1_neural_network.pth"
    if model_path.exists():
        try:
            input_size = len(features)
            torch_model = F1NeuralNetwork(input_size)
            torch_model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
            torch_model.eval()
            st.success("✅ Modelo PyTorch cargado")
        except Exception as e:
            st.error(f"❌ Error cargando modelo: {e}")
            st.stop()
    else:
        st.error("❌ No se encontró f1_neural_network.pth")
        st.stop()

    # ==================================================
    # VERIFICAR FEATURES
    # ==================================================
    
    available_features = [f for f in features if f in df.columns]
    missing_features = [f for f in features if f not in df.columns]
    
    if missing_features:
        st.warning(f"⚠️ Features faltantes: {missing_features[:5]}...")
        for f in missing_features:
            df[f] = 0
    
    st.info(f"📊 Features utilizadas: {len(available_features)} de {len(features)}")

    # ==================================================
    # SIDEBAR FILTROS
    # ==================================================
    
    if 'YEAR' not in df.columns and 'NAME_YEAR' in df.columns:
        df['YEAR'] = pd.to_numeric(df['NAME_YEAR'].astype(str).str[:4], errors='coerce')
    
    available_years = sorted([y for y in df['YEAR'].unique() if pd.notna(y)])
    year_choice = st.sidebar.selectbox("Año", available_years)

    # ==================================================
    # PREDECIR
    # ==================================================
    
    filtered_df = df[df['YEAR'] == year_choice].copy()
    
    if filtered_df.empty:
        st.warning(f"No hay datos para {year_choice}")
        st.stop()
    
    input_data = filtered_df[features].copy()
    for f in features:
        if f not in input_data.columns:
            input_data[f] = 0
    input_data = input_data[features].dropna()
    
    if input_data.empty:
        st.warning("No hay datos válidos")
        st.stop()
    
    try:
        input_scaled = scaler.transform(input_data)
        input_tensor = torch.tensor(input_scaled, dtype=torch.float32)
        
        with torch.no_grad():
            predictions = torch_model(input_tensor).numpy().flatten()
        
        filtered_df.loc[input_data.index, 'Prediction'] = predictions[:len(filtered_df)]
        
        avg_real = round(filtered_df['SCORE'].mean(), 2) if 'SCORE' in filtered_df.columns else 0
        avg_pred = round(float(predictions.mean()), 2)
        total = len(filtered_df)
        
    except Exception as e:
        st.error(f"Error en predicción: {str(e)[:200]}")
        st.stop()

    # ==================================================
    # KPIS
    # ==================================================
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total Registros", total)
    with col2: st.metric("Score Real Promedio", avg_real)
    with col3: st.metric("Score Predicho Promedio", avg_pred)
    
    st.markdown("---")

    # ==================================================
    # GRÁFICO
    # ==================================================
    
    st.subheader(f"Score Real vs Score Predicho - {year_choice}")
    
    if 'NAME_YEAR' in filtered_df.columns:
        labels = filtered_df['NAME_YEAR'].astype(str)
    else:
        labels = list(range(1, len(filtered_df) + 1))
    
    fig = go.Figure()
    
    if 'SCORE' in filtered_df.columns:
        fig.add_trace(go.Scatter(
            x=labels, y=filtered_df['SCORE'],
            mode='lines+markers', name='Real',
            line=dict(color='#E10600', width=2),
            marker=dict(color='#E10600', size=6)
        ))
    
    fig.add_trace(go.Scatter(
        x=labels, y=filtered_df['Prediction'],
        mode='lines+markers', name='Predicho (PyTorch)',
        line=dict(color='#FFD700', width=2, dash='dash'),
        marker=dict(color='#FFD700', size=6, symbol='diamond')
    ))
    
    fig.update_layout(
        xaxis_title="Carrera",
        yaxis_title="Score",
        template="plotly_dark",
        paper_bgcolor="#0A0F1F",
        plot_bgcolor="#151520",
        font=dict(color="white"),
        xaxis=dict(tickangle=45)
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # ==================================================
    # TABLA
    # ==================================================
    
    with st.expander("Ver datos detallados"):
        if 'NAME_YEAR' in filtered_df.columns and 'SCORE' in filtered_df.columns:
            display = filtered_df[['NAME_YEAR', 'SCORE', 'Prediction']].dropna()
            display.columns = ['Carrera', 'Score Real', 'Score Predicho']
        else:
            display = filtered_df[['Prediction']].dropna()
            display.columns = ['Score Predicho']
        st.dataframe(display, use_container_width=True)

    st.markdown("""
    <div style="text-align: center; padding: 1rem; margin-top: 2rem; border-top: 1px solid #C0C0C0;">
        PyTorch Neural Network - Deep Learning Model
    </div>
    """, unsafe_allow_html=True)


# ==================================================
# SECCIÓN 3: FAN PULSE
# ==================================================

def show_pulse():
    """Función principal que muestra el dashboard de Pulse Analytics"""
    
    st.title("🏎️ F1 PULSE")
    st.markdown("<p style='font-size:18px; font-weight:bold; color:#C0C0C0; margin-top:-15px;'>THE VOICE OF THE FANS</p>", unsafe_allow_html=True)
    
    # =============================================================================
    # KPI CARDS
    # =============================================================================
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        try:
            module_users = import_pulse_module("pulse_users", "pulse_kpi_total_users.py")
            if module_users and hasattr(module_users, 'display_total_users'):
                fig_users = module_users.display_total_users()
                st.plotly_chart(fig_users, use_container_width=True, config={'displayModeBar': False})
            else:
                st.metric("Total Users", "N/A")
        except Exception:
            st.metric("Total Users", "N/A")
    
    with col2:
        try:
            module_countries = import_pulse_module("pulse_countries", "pulse_kpi_countries.py")
            if module_countries and hasattr(module_countries, 'display_total_countries'):
                fig_countries = module_countries.display_total_countries()
                st.plotly_chart(fig_countries, use_container_width=True, config={'displayModeBar': False})
            else:
                st.metric("# Countries", "N/A")
        except Exception:
            st.metric("# Countries", "N/A")
    
    with col3:
        try:
            module_tweets = import_pulse_module("pulse_tweets", "pulse_kpi_total_tweets.py")
            if module_tweets and hasattr(module_tweets, 'display_total_tweets'):
                fig_tweets = module_tweets.display_total_tweets()
                st.plotly_chart(fig_tweets, use_container_width=True, config={'displayModeBar': False})
            else:
                st.metric("Total Tweets", "N/A")
        except Exception:
            st.metric("Total Tweets", "N/A")
    
    with col4:
        try:
            module_sentiment = import_pulse_module("pulse_sentiment", "pulse_sentimientos.py")
            if module_sentiment and hasattr(module_sentiment, 'create_sentiment_semaforo'):
                fig_sentiment = module_sentiment.create_sentiment_semaforo()
                st.plotly_chart(fig_sentiment, use_container_width=True, config={'displayModeBar': False})
            else:
                st.metric("Sentimiento", "N/A")
        except Exception:
            st.metric("Sentimiento", "N/A")
    
    # =============================================================================
    # MAPA Y TOP 10
    # =============================================================================
    st.markdown("---")
    
    col_left_main, col_right_main = st.columns([1.8, 1.2])
    
    with col_left_main:
        st.subheader("🌍 MAPA DE EMOCIONES")
        try:
            module_map = import_pulse_module("pulse_map", "pulse_mapa.py")
            if module_map and hasattr(module_map, 'create_emotion_map'):
                fig_map = module_map.create_emotion_map()
                st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': True})
            else:
                st.info("🗺️ Mapa no disponible")
        except Exception:
            st.info("🗺️ Mapa no disponible")
    
    with col_right_main:
        st.subheader("📊 TOP 10 PAÍSES")
        try:
            module_top10 = import_pulse_module("pulse_top10", "pulse_top10.py")
            if module_top10 and hasattr(module_top10, 'create_top_countries'):
                fig_top10 = module_top10.create_top_countries()
                st.plotly_chart(fig_top10, use_container_width=True, config={'displayModeBar': False})
            else:
                st.warning("Top 10 no disponible")
        except Exception:
            st.warning("Top 10 no disponible")
    
    # =============================================================================
    # TRENDS
    # =============================================================================
    st.markdown("---")
    st.subheader("📈 TRENDS")
    
    col_trend1, col_trend2, col_source = st.columns([1, 1.2, 1])
    
    with col_trend1:
        st.markdown("#### 🌍 NUBE DE PALABRAS")
        try:
            module_nube = import_pulse_module("pulse_nube", "pulse_nube.py")
            if module_nube and hasattr(module_nube, 'create_wordcloud'):
                fig_nube = module_nube.create_wordcloud()
                st.pyplot(fig_nube)
            else:
                st.info("Nube no disponible")
        except Exception:
            st.info("Nube no disponible")
    
    with col_trend2:
        st.markdown("#### 🏎️ N-GRAMAS")
        try:
            module_ngrams = import_pulse_module("pulse_ngrams", "pulse_ngama.py")
            if module_ngrams and hasattr(module_ngrams, 'create_ngrams'):
                fig_ngrams = module_ngrams.create_ngrams()
                st.plotly_chart(fig_ngrams, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("N-gramas no disponible")
        except Exception:
            st.info("N-gramas no disponible")
    
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
            marker_colors=['#E10600', '#FFD700', '#C0C0C0', '#0A0F1F']
        ))
        fig_source.update_layout(
            height=280, 
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"),
            paper_bgcolor="#0A0F1F",
            font=dict(color="white")
        )
        st.plotly_chart(fig_source, use_container_width=True, config={'displayModeBar': False})
    
    # =============================================================================
    # TWEETS POR DÍA
    # =============================================================================
    st.markdown("---")
    
    col_graph, col_sidebar_filters = st.columns([3, 1])
    
    with col_sidebar_filters:
        st.markdown("### 🎛️ FILTROS")
        year_options = [2018, 2019, 2020, 2021, 2022, 2023]
        selected_year = st.selectbox("📅 Año", year_options, index=3)
        month_options = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        selected_month = st.selectbox("Mes", month_options, index=0)
        hour_range = st.slider("⏰ Rango de horas", 0, 23, (0, 23))
    
    with col_graph:
        st.subheader("📊 TWEETS Y USUARIOS POR DÍA")
        try:
            module_metrics = import_pulse_module("pulse_metrics", "pulse_metrics.py")
            if module_metrics and hasattr(module_metrics, 'plot_combined_daily_metrics_filtered'):
                fig_metrics = module_metrics.plot_combined_daily_metrics_filtered(
                    year=selected_year,
                    month=selected_month if selected_month != "Todos" else None,
                    hour_range=hour_range
                )
                if fig_metrics:
                    st.plotly_chart(fig_metrics, use_container_width=True, config={'displayModeBar': True})
                else:
                    st.info("No se encontraron registros")
            else:
                st.info("Métrica no disponible")
        except Exception:
            st.info("Gráfica temporal no disponible")
    
    # =============================================================================
    # FOOTER
    # =============================================================================
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #C0C0C0;'>🏎️ F1 PULSE - Oracle Red Bull Racing | Inteligencia Artificial Aplicada</p>", unsafe_allow_html=True)
    