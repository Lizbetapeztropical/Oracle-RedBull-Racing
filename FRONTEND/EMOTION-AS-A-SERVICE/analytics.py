import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from pathlib import Path
import base64
import joblib
import torch
import torch.nn as nn

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import root_mean_squared_error


# ==================================================
# DEFINIR ARQUITECTURA DE LA RED NEURONAL (TORCH)
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
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
    
    def forward(self, x):
        return self.network(x)


def show_analytics():

    # ==================================================
    # TÍTULO
    # ==================================================
    
    st.markdown("""
    <h1 style='text-align:center; color:#E10600; font-family: "Titillium Web", sans-serif;'>
        RED BULL ANALYTICS
    </h1>
    <p style='text-align:center; color:#C0C0C0;'>Performance + Predictive Intelligence</p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # ==================================================
    # RUTAS DE LOS MODELOS
    # ==================================================
    
    BASE_DIR = Path(__file__).resolve().parent
    MODELING_DIR = BASE_DIR.parent.parent / "BACKEND" / "MODELING"
    
    features = [
        "POINTS", "LAPS", "MILLISECONDS", "WEATHER_cloudy",
        "OVERTAKEN_POSITIONS_TOTAL", "DNF_COUNT", "LAPMEAN",
        "PS_COUNT", "SC_COUNT", "DRIVER_ENCODED", "RACE_ENCODED"
    ]
    
    target = "SCORE"

    # ==================================================
    # GENERAR DATOS DE EJEMPLO (NO usa MongoDB)
    # ==================================================

    @st.cache_data(ttl=60)
    def generate_sample_data():
        """Genera datos de ejemplo para demostración"""
        np.random.seed(42)
        
        drivers = list(range(101, 121))
        years = [2021, 2022, 2023, 2024]
        
        data = []
        for driver in drivers:
            for year in years:
                for race in range(1, 21):
                    base_score = 3 + (driver % 10) * 0.3 + np.random.normal(0, 0.8)
                    score = max(0, min(10, base_score))
                    
                    data.append({
                        'DRIVERID': driver,
                        'YEAR': year,
                        'NAME_YEAR': f"Race_{race}_{year}",
                        'SCORE': round(score, 2),
                        'POINTS': np.random.randint(0, 26),
                        'LAPS': np.random.randint(50, 71),
                        'MILLISECONDS': np.random.randint(3000000, 4500000),
                        'WEATHER_cloudy': np.random.choice([0, 1]),
                        'OVERTAKEN_POSITIONS_TOTAL': np.random.randint(0, 15),
                        'DNF_COUNT': np.random.choice([0, 0, 0, 1]),
                        'LAPMEAN': round(np.random.uniform(75, 95), 2),
                        'SC_COUNT': np.random.randint(0, 3),
                        'PS_COUNT': np.random.randint(0, 4),
                        'DRIVER_ENCODED': driver % 20,
                        'RACE_ENCODED': race % 10
                    })
        
        return pd.DataFrame(data)

    # ==================================================
    # CARGAR MODELOS PRE-ENTRENADOS
    # ==================================================

    @st.cache_resource
    def load_models():
        """Carga los modelos pre-entrenados desde BACKEND/MODELING"""
        models = {}
        scaler = None
        
        if not MODELING_DIR.exists():
            st.warning(f"⚠️ Carpeta de modelos no encontrada: {MODELING_DIR}")
            return models, None
        
        st.info("📦 Cargando modelos pre-entrenados...")
        
        try:
            xgb_path = MODELING_DIR / "xgboost_score_model.pkl"
            if xgb_path.exists():
                models["XGBoost"] = joblib.load(xgb_path)
                st.success("✅ XGBoost cargado")
            
            svm_path = MODELING_DIR / "svm_score_model.pkl"
            if svm_path.exists():
                models["SVM"] = joblib.load(svm_path)
                st.success("✅ SVM cargado")
            
            linear_path = MODELING_DIR / "linear_score_model.pkl"
            if linear_path.exists():
                models["Regresión Lineal"] = joblib.load(linear_path)
                st.success("✅ Regresión Lineal cargada")
            
            mlp_path = MODELING_DIR / "mlp_score_model.pkl"
            if mlp_path.exists():
                models["MLP (sklearn)"] = joblib.load(mlp_path)
                st.success("✅ MLP (sklearn) cargado")
            
            torch_path = MODELING_DIR / "f1_pytorch_model.pth"
            if torch_path.exists():
                input_size = len(features)
                torch_model = F1NeuralNetwork(input_size)
                torch_model.load_state_dict(torch.load(torch_path, map_location=torch.device('cpu')))
                torch_model.eval()
                models["PyTorch NN"] = torch_model
                st.success("✅ PyTorch NN cargado")
            
            scaler_path = MODELING_DIR / "scaler.pkl"
            if scaler_path.exists():
                scaler = joblib.load(scaler_path)
                
        except Exception as e:
            st.error(f"❌ Error cargando modelos: {e}")
            
        return models, scaler

    # ==================================================
    # CARGAR DATOS (NO MongoDB)
    # ==================================================
    
    csv_path = MODELING_DIR / "processed_dataset.csv"
    if csv_path.exists():
        try:
            merged_dataset = pd.read_csv(csv_path)
            st.success(f"✅ Datos cargados desde processed_dataset.csv ({len(merged_dataset)} filas)")
        except Exception as e:
            merged_dataset = generate_sample_data()
            st.info("📊 Usando datos de demostración")
    else:
        merged_dataset = generate_sample_data()
        st.info("📊 Usando datos de demostración")

    # ==================================================
    # LIMPIEZA DE DATOS
    # ==================================================
    
    try:
        for col in features + [target]:
            if col in merged_dataset.columns:
                merged_dataset[col] = pd.to_numeric(merged_dataset[col], errors='coerce')
        
        if 'YEAR' not in merged_dataset.columns and 'NAME_YEAR' in merged_dataset.columns:
            merged_dataset['YEAR'] = pd.to_numeric(
                merged_dataset['NAME_YEAR'].astype(str).str[:4], 
                errors='coerce'
            ).astype('Int64')
        
    except Exception as e:
        st.error(f"❌ Error en limpieza de datos: {e}")
        st.stop()

    # ==================================================
    # VERIFICAR FEATURES
    # ==================================================

    available_features = [f for f in features if f in merged_dataset.columns]
    if len(available_features) < len(features):
        features = available_features

    model_data = merged_dataset[['SCORE', 'YEAR'] + features].dropna()

    if model_data.empty:
        st.error("❌ No hay datos suficientes")
        st.stop()

    # ==================================================
    # CARGAR MODELOS
    # ==================================================
    
    models, scaler = load_models()
    
    available_models = []
    for name in ["XGBoost", "SVM", "Regresión Lineal", "MLP (sklearn)", "PyTorch NN"]:
        if models.get(name) is not None:
            available_models.append(name)
    
    if not available_models:
        st.error("❌ No se encontraron modelos pre-entrenados")
        st.stop()

    # ==================================================
    # SIDEBAR
    # ==================================================

    st.sidebar.markdown("### 🔎 FILTROS")
    st.sidebar.markdown("---")

    driver_choice = st.sidebar.selectbox(
        "Piloto",
        options=sorted(merged_dataset['DRIVERID'].unique())
    )

    available_years = sorted([y for y in model_data['YEAR'].unique() if pd.notna(y)])
    year_choice = st.sidebar.selectbox(
        "Año de Predicción",
        options=available_years
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 MODELO")

    model_choice = st.sidebar.selectbox(
        "Selecciona Algoritmo",
        options=available_models,
        index=0
    )

    # ==================================================
    # PREPARAR DATOS
    # ==================================================

    filtered_df = merged_dataset[
        (merged_dataset['DRIVERID'] == driver_choice) &
        (merged_dataset['YEAR'] == year_choice)
    ].sort_values(by='NAME_YEAR' if 'NAME_YEAR' in merged_dataset.columns else 'YEAR')

    if filtered_df.empty:
        st.warning(f"⚠️ No hay datos para el piloto {driver_choice} en {year_choice}")
        st.stop()

    input_data = filtered_df[features].copy().dropna()
    
    if input_data.empty:
        st.warning("⚠️ No hay datos válidos para este piloto")
        st.stop()

    # ==================================================
    # PREDICCIÓN
    # ==================================================
    
    model = models.get(model_choice)
    
    if model is None:
        st.error(f"❌ Modelo {model_choice} no disponible")
        st.stop()
    
    try:
        if model_choice in ["SVM", "MLP (sklearn)", "Regresión Lineal"]:
            predictions = model.predict(input_data)
        elif model_choice == "PyTorch NN":
            if scaler is not None:
                input_scaled = scaler.transform(input_data)
            else:
                temp_scaler = StandardScaler()
                input_scaled = temp_scaler.fit_transform(input_data)
            input_tensor = torch.tensor(input_scaled, dtype=torch.float32)
            with torch.no_grad():
                predictions = model(input_tensor).numpy().flatten()
        else:
            predictions = model.predict(input_data)
        
        filtered_df = filtered_df.copy()
        filtered_df.loc[input_data.index, 'Prediction'] = predictions
        
        avg_score = round(filtered_df['SCORE'].mean(), 2)
        last_dnf = filtered_df['DNF_COUNT'].iloc[-1] if len(filtered_df) > 0 else 0
        total_stops = int(filtered_df['PS_COUNT'].sum()) if 'PS_COUNT' in filtered_df.columns else 0
        predicted_avg_score = round(float(predictions.mean()), 2)
        
    except Exception as e:
        st.error(f"❌ Error en predicción: {e}")
        st.stop()

    # ==================================================
    # KPI CARDS
    # ==================================================
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("📊 Score Promedio", avg_score)
    with col2: st.metric("⚠️ DNFs", last_dnf)
    with col3: st.metric("🛞 Paradas en Boxes", total_stops)
    with col4: st.metric(f"🎯 Score Predicho ({model_choice})", predicted_avg_score)

    st.markdown("---")

    # ==================================================
    # GRÁFICO
    # ==================================================
    
    st.subheader("📈 Score Real vs Score Predicho")
    
    x_values = filtered_df['NAME_YEAR'] if 'NAME_YEAR' in filtered_df.columns else list(range(1, len(filtered_df) + 1))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_values, y=filtered_df['SCORE'], mode='lines+markers', name='Real',
        line=dict(color='#E10600', width=2), marker=dict(color='#E10600', size=8)
    ))
    fig.add_trace(go.Scatter(
        x=x_values, y=filtered_df['Prediction'], mode='lines+markers', name='Predicho',
        line=dict(color='#FFD700', width=2, dash='dash'), marker=dict(color='#FFD700', size=8, symbol='diamond')
    ))
    fig.update_layout(
        title=f"{driver_choice} - Temporada {year_choice}",
        xaxis_title="Carrera", yaxis_title="Score", template="plotly_dark",
        paper_bgcolor="#0A0F1F", plot_bgcolor="#151520",
        font=dict(color="white", family="Titillium Web"),
        legend=dict(bgcolor="#151520", bordercolor="#E10600", borderwidth=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # ==================================================
    # PIE DE PÁGINA
    # ==================================================
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem; margin-top: 2rem; 
                border-top: 1px solid #C0C0C0; color: #C0C0C0; font-size: 0.7rem;">
        Red Bull Analytics - Powered by Machine Learning
    </div>
    """, unsafe_allow_html=True)
