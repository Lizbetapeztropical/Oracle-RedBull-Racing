import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
import joblib


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
    
    # ==================================================
    # FEATURES CORRECTAS (las que usan los modelos entrenados)
    # ==================================================
    
    features = [
        "POINTS", "LAPS", "MILLISECONDS", "WEATHER_cloudy",
        "OVERTAKEN_POSITIONS_TOTAL", "DNF_COUNT", "LAPMEAN",
        "PS_COUNT", "SC_COUNT", "DRIVER_ENCODED", "RACE_ENCODED"
    ]

    # ==================================================
    # CARGAR DATASET
    # ==================================================
    
    csv_path = MODELING_DIR / "processed_dataset.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        st.success(f"✅ Datos cargados ({len(df)} filas)")
    else:
        st.error("❌ No se encontró processed_dataset.csv")
        st.stop()

    # ==================================================
    # VERIFICAR FEATURES DISPONIBLES
    # ==================================================
    
    available_features = [f for f in features if f in df.columns]
    
    if not available_features:
        st.error("❌ No hay features disponibles en el dataset")
        st.stop()
    
    features = available_features

    # ==================================================
    # CARGAR MODELOS .pkl
    # ==================================================
    
    models = {}
    
    st.info("📦 Cargando modelos pre-entrenados...")
    
    model_files = {
        "Regresión Lineal": "linear_score_model.pkl",
        "XGBoost": "xgboost_score_model.pkl",
        "SVM": "svm_score_model.pkl",
        "MLP": "mlp_score_model.pkl"
    }
    
    for name, filename in model_files.items():
        path = MODELING_DIR / filename
        if path.exists():
            models[name] = joblib.load(path)
            st.success(f"✅ {name}")
    
    if not models:
        st.error("❌ No se encontraron modelos .pkl")
        st.stop()

    # ==================================================
    # SIDEBAR
    # ==================================================
    
    st.sidebar.markdown("### 🔎 FILTROS")
    
    # Asegurar YEAR
    if 'YEAR' not in df.columns and 'NAME_YEAR' in df.columns:
        df['YEAR'] = pd.to_numeric(df['NAME_YEAR'].astype(str).str[:4], errors='coerce')
    
    available_years = sorted([y for y in df['YEAR'].unique() if pd.notna(y)])
    year_choice = st.sidebar.selectbox("Año", available_years)
    
    st.sidebar.markdown("### 🤖 MODELO")
    model_choice = st.sidebar.selectbox("Algoritmo", list(models.keys()))

    # ==================================================
    # FILTRAR Y PREDECIR
    # ==================================================
    
    filtered_df = df[df['YEAR'] == year_choice].copy()
    
    if filtered_df.empty:
        st.warning(f"No hay datos para el año {year_choice}")
        st.stop()
    
    input_data = filtered_df[features].copy().dropna()
    
    if input_data.empty:
        st.warning("No hay datos válidos")
        st.stop()
    
    model = models.get(model_choice)
    
    try:
        preds = model.predict(input_data)
        
        filtered_df.loc[input_data.index, 'Prediction'] = preds[:len(filtered_df)]
        
        avg_real = round(filtered_df['SCORE'].mean(), 2)
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
    # GRÁFICO CON LÍNEAS
    # ==================================================
    
    st.subheader(f"Score Real vs Score Predicho - {year_choice}")
    
    if 'NAME_YEAR' in filtered_df.columns:
        labels = filtered_df['NAME_YEAR'].astype(str)
    else:
        labels = list(range(1, len(filtered_df) + 1))
    
    fig = go.Figure()
    
    # Línea REAL (roja, continua)
    fig.add_trace(go.Scatter(
        x=labels,
        y=filtered_df['SCORE'],
        mode='lines+markers',
        name='Real',
        line=dict(color='#E10600', width=2),
        marker=dict(color='#E10600', size=6)
    ))
    
    # Línea PREDICHA (dorada, punteada)
    fig.add_trace(go.Scatter(
        x=labels,
        y=filtered_df['Prediction'],
        mode='lines+markers',
        name='Predicho',
        line=dict(color='#FFD700', width=2, dash='dash'),
        marker=dict(color='#FFD700', size=6, symbol='diamond')
    ))
    
    fig.update_layout(
        xaxis_title="Carrera",
        yaxis_title="Score",
        template="plotly_dark",
        paper_bgcolor="#0A0F1F",
        plot_bgcolor="#151520",
        font=dict(color="white", family="Titillium Web"),
        legend=dict(bgcolor="#151520", bordercolor="#E10600", borderwidth=1),
        xaxis=dict(tickangle=45)
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # ==================================================
    # TABLA DETALLADA
    # ==================================================
    
    with st.expander("Ver datos detallados"):
        if 'NAME_YEAR' in filtered_df.columns:
            display = filtered_df[['NAME_YEAR', 'SCORE', 'Prediction']].dropna()
            display.columns = ['Carrera', 'Score Real', 'Score Predicho']
        else:
            display = filtered_df[['SCORE', 'Prediction']].dropna()
            display.columns = ['Score Real', 'Score Predicho']
        st.dataframe(display, use_container_width=True)

    # ==================================================
    # FOOTER
    # ==================================================
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem; margin-top: 2rem; 
                border-top: 1px solid #C0C0C0; color: #C0C0C0; font-size: 0.7rem;">
        Red Bull Analytics - Powered by Machine Learning
    </div>
    """, unsafe_allow_html=True)
    