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
    pulse_directory = Path(__file__).parent / "Pulse_page"
    pulse_path = pulse_directory / file_name
    
    if not pulse_path.exists():
        return None

    if str(pulse_directory) not in sys.path:
        sys.path.insert(0, str(pulse_directory))
    
    spec = importlib.util.spec_from_file_location(module_name, pulse_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
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

PULSE_MONTH_OPTIONS = [
    "Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]


def show_pulse():
    """Función principal que muestra el dashboard de Pulse Analytics"""
    
    st.title("🏎️ F1 PULSE")
    st.markdown("<p style='font-size:18px; font-weight:bold; color:#C0C0C0; margin-top:-15px;'>THE VOICE OF THE FANS</p>", unsafe_allow_html=True)
    pulse_data_module = import_pulse_module("pulse_data", "pulse_data.py")
    
    # =============================================================================
    # KPI CARDS
    # =============================================================================
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        _render_kpi_provider("pulse_users", "pulse_kpi_total_users.py", "display_total_users", "Total Users")
    
    with col2:
        _render_kpi_provider("pulse_countries", "pulse_kpi_countries.py", "display_total_countries", "# Countries")
    
    with col3:
        _render_kpi_provider("pulse_tweets", "pulse_kpi_total_tweets.py", "display_total_tweets", "Total Tweets")
    
    with col4:
        _render_kpi_provider("pulse_sentiment", "pulse_sentimientos.py", "create_sentiment_semaforo", "Sentimiento")
    
    # =============================================================================
    # MAPA Y TOP 10
    # =============================================================================
    st.markdown("---")
    
    col_left_main, col_right_main = st.columns([1.8, 1.2])
    
    with col_left_main:
        st.subheader("🌍 MAPA DE EMOCIONES")
        _render_plotly_provider(
            "pulse_map",
            "pulse_mapa.py",
            "create_emotion_map",
            "🗺️ Mapa no disponible",
            chart_config={"displayModeBar": True},
        )
    
    with col_right_main:
        st.subheader("📊 TOP 10 PAÍSES")
        _render_plotly_provider(
            "pulse_top10",
            "pulse_top10p.py",
            "create_top_countries",
            "Top 10 no disponible",
            chart_config={"displayModeBar": False},
            warning=True,
        )
    
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
                wordcloud_figure = module_nube.create_wordcloud()
                st.pyplot(wordcloud_figure)
            else:
                st.info("Nube no disponible")
        except Exception as error:
            st.info("Nube no disponible")
            st.caption(f"Detalle: {error}")
    
    with col_trend2:
        st.markdown("#### 🏎️ N-GRAMAS")
        _render_plotly_provider(
            "pulse_ngrams",
            "pulse_ngama.py",
            "create_ngrams",
            "N-gramas no disponible",
            chart_config={"displayModeBar": False},
        )
    
    with col_source:
        st.markdown("#### 📱 FUENTE DE TWEETS")
        _render_source_chart(pulse_data_module)
    
    # =============================================================================
    # TWEETS POR DÍA
    # =============================================================================
    st.markdown("---")
    
    col_graph, col_sidebar_filters = st.columns([3, 1])
    
    with col_sidebar_filters:
        st.markdown("### 🎛️ FILTROS")
        year_options = _get_pulse_year_options(pulse_data_module)
        selected_year = st.selectbox("📅 Año", year_options, index=_get_default_year_index(year_options))
        selected_month = st.selectbox("Mes", PULSE_MONTH_OPTIONS, index=0)
        full_temporal_metrics_available = _has_full_temporal_metrics(pulse_data_module)
        hour_range = st.slider(
            "⏰ Rango de horas",
            0,
            23,
            (0, 23),
            disabled=not full_temporal_metrics_available,
        )
        if not full_temporal_metrics_available:
            st.caption("Filtro de hora disponible al agregar F1_tweets.csv o tweets_cleaned.csv.")
    
    with col_graph:
        st.subheader("📊 TWEETS Y USUARIOS POR DÍA")
        _render_daily_metrics(selected_year, selected_month, hour_range)
    
    # =============================================================================
    # FOOTER
    # =============================================================================
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #C0C0C0;'>🏎️ F1 PULSE - Oracle Red Bull Racing | Inteligencia Artificial Aplicada</p>", unsafe_allow_html=True)


def _render_kpi_provider(module_name, file_name, function_name, fallback_label):
    try:
        provider_result = _call_pulse_provider(module_name, file_name, function_name)
        figure = _extract_provider_figure(provider_result)
        st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
    except Exception as error:
        st.metric(fallback_label, "N/A")
        st.caption(f"Detalle: {error}")


def _render_plotly_provider(module_name, file_name, function_name, fallback_message, chart_config, warning=False):
    try:
        provider_result = _call_pulse_provider(module_name, file_name, function_name)
        figure = _extract_provider_figure(provider_result)
        st.plotly_chart(figure, use_container_width=True, config=chart_config)
    except Exception as error:
        if warning:
            st.warning(fallback_message)
        else:
            st.info(fallback_message)
        st.caption(f"Detalle: {error}")


def _render_source_chart(pulse_data_module):
    try:
        if pulse_data_module is None or not hasattr(pulse_data_module, "get_source_counts"):
            raise RuntimeError("No se pudo cargar pulse_data.py")

        source_counts = pulse_data_module.get_source_counts(limit=4)
        if source_counts.empty:
            st.info("Fuente de tweets no disponible")
            return

        source_figure = go.Figure(
            go.Pie(
                labels=source_counts.index.tolist(),
                values=source_counts.values.tolist(),
                hole=0.4,
                marker_colors=["#E10600", "#FFD700", "#C0C0C0", "#0A0F1F"],
            )
        )
        source_figure.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"),
            paper_bgcolor="#0A0F1F",
            font=dict(color="white"),
        )
        st.plotly_chart(source_figure, use_container_width=True, config={"displayModeBar": False})
    except Exception as error:
        st.info("Fuente de tweets no disponible")
        st.caption(f"Detalle: {error}")


def _render_daily_metrics(selected_year, selected_month, hour_range):
    try:
        metrics_module = import_pulse_module("pulse_metrics", "pulse_metrics.py")
        if metrics_module is None or not hasattr(metrics_module, "plot_combined_daily_metrics_filtered"):
            raise RuntimeError("No se pudo cargar pulse_metrics.py")

        selected_month_filter = selected_month if selected_month != "Todos" else None
        metrics_figure = metrics_module.plot_combined_daily_metrics_filtered(
            year=selected_year,
            month=selected_month_filter,
            hour_range=hour_range,
        )
        if metrics_figure:
            st.plotly_chart(metrics_figure, use_container_width=True, config={"displayModeBar": True})
        else:
            st.info("No se encontraron registros")
    except Exception as error:
        st.info("Gráfica temporal no disponible")
        st.caption(f"Detalle: {error}")


def _call_pulse_provider(module_name, file_name, function_name):
    pulse_module = import_pulse_module(module_name, file_name)
    if pulse_module is None or not hasattr(pulse_module, function_name):
        raise RuntimeError(f"No se pudo cargar {file_name}.{function_name}")

    provider_function = getattr(pulse_module, function_name)
    return provider_function()


def _extract_provider_figure(provider_result):
    if isinstance(provider_result, (tuple, list)):
        return provider_result[0]
    return provider_result


def _get_pulse_year_options(pulse_data_module):
    try:
        if pulse_data_module is None or not hasattr(pulse_data_module, "get_available_years"):
            raise RuntimeError("No se pudo cargar pulse_data.py")

        available_years = pulse_data_module.get_available_years()
        return available_years if available_years else [2021]
    except Exception as error:
        st.caption(f"Detalle filtros: {error}")
        return [2021]


def _get_default_year_index(year_options):
    if 2021 in year_options:
        return year_options.index(2021)
    return max(len(year_options) - 1, 0)


def _has_full_temporal_metrics(pulse_data_module):
    try:
        if pulse_data_module is None:
            return False
        if not hasattr(pulse_data_module, "load_full_tweet_metrics"):
            return False
        if not hasattr(pulse_data_module, "has_temporal_columns"):
            return False

        full_tweets_dataframe = pulse_data_module.load_full_tweet_metrics()
        return pulse_data_module.has_temporal_columns(full_tweets_dataframe)
    except Exception:
        return False
