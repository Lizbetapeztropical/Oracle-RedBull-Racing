import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from pathlib import Path
import base64

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import root_mean_squared_error
from xgboost import XGBRegressor


def show_analytics():

    # ==================================================
    # TÍTULO (sin logo duplicado)
    # ==================================================
    
    st.markdown("""
    <h1 style='text-align:center; color:#E10600; font-family: "Titillium Web", sans-serif;'>
        RED BULL ANALYTICS
    </h1>
    <p style='text-align:center; color:#C0C0C0;'>Performance + Predictive Intelligence</p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # ==================================================
    # GENERAR DATOS DE EJEMPLO (no requiere MongoDB)
    # ==================================================

    @st.cache_data(ttl=60)
    def generate_sample_data():
        """Genera datos de ejemplo para demostración"""
        np.random.seed(42)
        
        # Pilotos de ejemplo (20 pilotos)
        drivers = list(range(101, 121))
        years = [2021, 2022, 2023, 2024]
        
        data = []
        for driver in drivers:
            for year in years:
                # 20 carreras por año
                for race in range(1, 21):
                    # Score base entre 3 y 9
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
                        'PS_COUNT': np.random.randint(0, 4)
                    })
        
        df = pd.DataFrame(data)
        return df

    # ==================================================
    # CARGAR DATOS
    # ==================================================
    
    st.info("📊 Usando datos de demostración (MongoDB no disponible)")
    merged_dataset = generate_sample_data()

    # ==================================================
    # LIMPIEZA DE DATOS
    # ==================================================
    
    try:
        numeric_cols = ['SCORE', 'POINTS', 'LAPS', 'MILLISECONDS',
                       'OVERTAKEN_POSITIONS_TOTAL', 'DNF_COUNT',
                       'LAPMEAN', 'PS_COUNT', 'WEATHER_cloudy', 'SC_COUNT']
        
        for col in numeric_cols:
            if col in merged_dataset.columns:
                merged_dataset[col] = pd.to_numeric(merged_dataset[col], errors='coerce')
        
    except Exception as e:
        st.error(f"❌ Error en limpieza de datos: {e}")
        st.stop()

    # ==================================================
    # FEATURES
    # ==================================================

    features = [
        'POINTS', 'LAPS', 'MILLISECONDS', 'WEATHER_cloudy',
        'OVERTAKEN_POSITIONS_TOTAL', 'DNF_COUNT', 'LAPMEAN',
        'SC_COUNT', 'PS_COUNT'
    ]
    
    # Verificar features disponibles
    available_features = [f for f in features if f in merged_dataset.columns]
    if len(available_features) < len(features):
        features = available_features

    model_data = merged_dataset[['SCORE', 'YEAR'] + features].dropna()

    if model_data.empty:
        st.error("❌ No hay datos suficientes después de la limpieza")
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
        options=["XGBoost", "SVM", "Red Neuronal", "Regresión Lineal"],
        index=0
    )

    # ==================================================
    # TRAIN / TEST SPLIT
    # ==================================================

    train_data = model_data[model_data['YEAR'] < year_choice]
    test_data = model_data[model_data['YEAR'] == year_choice]

    if train_data.empty or test_data.empty:
        st.warning(f"⚠️ No hay suficientes datos para el año {year_choice}")
        st.stop()

    X_train = train_data[features]
    y_train = train_data['SCORE']
    X_test = test_data[features]
    y_test = test_data['SCORE']

    # ==================================================
    # NORMALIZACIÓN Y MODELOS
    # ==================================================

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    @st.cache_resource
    def train_models(_X_train, _y_train, _X_train_scaled):
        with st.spinner("Entrenando modelos..."):
            lm = LinearRegression().fit(_X_train, _y_train)
            svm_model = SVR(kernel='rbf', C=1.0).fit(_X_train_scaled, _y_train)
            nn_model = MLPRegressor(hidden_layer_sizes=(10, 5), max_iter=1000, random_state=123).fit(_X_train_scaled, _y_train)
            xgb_model = XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=123).fit(_X_train, _y_train)
            
            return {
                "Regresión Lineal": lm,
                "SVM": svm_model,
                "Red Neuronal": nn_model,
                "XGBoost": xgb_model
            }

    trained_models = train_models(X_train, y_train, X_train_scaled)

    # ==================================================
    # EVALUACIÓN DE MODELOS
    # ==================================================

    pred_lm = trained_models["Regresión Lineal"].predict(X_test)
    pred_svm = trained_models["SVM"].predict(X_test_scaled)
    pred_nn = trained_models["Red Neuronal"].predict(X_test_scaled)
    pred_xgb = trained_models["XGBoost"].predict(X_test)

    rmse_dict = {
        "Modelo": ["Linear", "SVM", "NN", "XGB"],
        "RMSE": [
            root_mean_squared_error(y_test, pred_lm),
            root_mean_squared_error(y_test, pred_svm),
            root_mean_squared_error(y_test, pred_nn),
            root_mean_squared_error(y_test, pred_xgb)
        ]
    }

    df_rmse = pd.DataFrame(rmse_dict)
    best_model_idx = df_rmse['RMSE'].idxmin()
    best_model_name = df_rmse.loc[best_model_idx, 'Modelo']
    
    st.sidebar.markdown(f"**🏆 Mejor Modelo:** `{best_model_name}`")

    # ==================================================
    # PREDICCIÓN POR PILOTO
    # ==================================================

    filtered_df = merged_dataset[
        (merged_dataset['DRIVERID'] == driver_choice) &
        (merged_dataset['YEAR'] == year_choice)
    ].sort_values(by='NAME_YEAR')

    if not filtered_df.empty:
        input_data_driver = filtered_df[features].copy().dropna()

        if not input_data_driver.empty:
            if model_choice == "Regresión Lineal":
                driver_preds = trained_models["Regresión Lineal"].predict(input_data_driver)
            elif model_choice == "SVM":
                driver_preds = trained_models["SVM"].predict(scaler.transform(input_data_driver))
            elif model_choice == "Red Neuronal":
                driver_preds = trained_models["Red Neuronal"].predict(scaler.transform(input_data_driver))
            else:
                driver_preds = trained_models["XGBoost"].predict(input_data_driver)

            filtered_df = filtered_df.copy()
            filtered_df.loc[input_data_driver.index, 'Prediction'] = driver_preds

            avg_score = round(filtered_df['SCORE'].mean(), 2) if not filtered_df['SCORE'].isna().all() else 0
            last_dnf = filtered_df['DNF_COUNT'].iloc[-1] if len(filtered_df) > 0 and 'DNF_COUNT' in filtered_df.columns else 0
            total_stops = int(filtered_df['PS_COUNT'].sum()) if 'PS_COUNT' in filtered_df.columns else 0
            predicted_avg_score = round(float(driver_preds.mean()), 2) if len(driver_preds) > 0 else 0
        else:
            avg_score = last_dnf = total_stops = predicted_avg_score = 0
    else:
        avg_score = last_dnf = total_stops = predicted_avg_score = 0

    # ==================================================
    # KPI CARDS
    # ==================================================
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        st.metric("📊 Score Promedio", avg_score)
    with col2: 
        st.metric("⚠️ DNFs", last_dnf)
    with col3: 
        st.metric("🛞 Paradas en Boxes", total_stops)
    with col4: 
        st.metric(f"🎯 Score Predicho ({model_choice})", predicted_avg_score)

    st.markdown("---")

    # ==================================================
    # GRÁFICO
    # ==================================================
    
    st.subheader("📈 Score Real vs Score Predicho")
    
    if not filtered_df.empty and 'Prediction' in filtered_df.columns:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=filtered_df['NAME_YEAR'], 
            y=filtered_df['SCORE'], 
            mode='lines+markers', 
            name='Real',
            line=dict(color='#E10600', width=2),
            marker=dict(color='#E10600', size=8)
        ))
        fig.add_trace(go.Scatter(
            x=filtered_df['NAME_YEAR'], 
            y=filtered_df['Prediction'], 
            mode='lines+markers', 
            name='Predicho',
            line=dict(color='#FFD700', width=2, dash='dash'),
            marker=dict(color='#FFD700', size=8, symbol='diamond')
        ))
        fig.update_layout(
            title=f"{driver_choice} - Temporada {year_choice}",
            xaxis_title="Carrera",
            yaxis_title="Score",
            template="plotly_dark",
            paper_bgcolor="#0A0F1F",
            plot_bgcolor="#151520",
            font=dict(color="white", family="Titillium Web"),
            legend=dict(
                bgcolor="#151520",
                bordercolor="#E10600",
                borderwidth=1
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay suficientes datos para este piloto.")

    # ==================================================
    # COMPARACIÓN DE MODELOS
    # ==================================================
    
    st.subheader("📊 Comparación de Modelos")
    st.dataframe(df_rmse.style.format({"RMSE": "{:.4f}"}), use_container_width=True, hide_index=True)
    
    # ==================================================
    # PIE DE PÁGINA
    # ==================================================
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem; margin-top: 2rem; 
                border-top: 1px solid #C0C0C0; color: #C0C0C0; font-size: 0.7rem;">
        Red Bull Analytics - Powered by Machine Learning
    </div>
    """, unsafe_allow_html=True)
    
    