# analytics.py - Versión con datos de ejemplo (no requiere MongoDB)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import root_mean_squared_error
from xgboost import XGBRegressor


def show_analytics():

    # ==================================================
    # TITLE
    # ==================================================

    st.markdown(
        "<h1 style='text-align:center; color:#E10600;'>🏁 Oracle Red Bull Racing</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center; color:gray;'>Performance + Predictive Intelligence</p>",
        unsafe_allow_html=True
    )

    # ==================================================
    # GENERAR DATOS DE EJEMPLO
    # ==================================================

    @st.cache_data
    def load_data():
        """Genera datos de ejemplo para demostración"""
        
        np.random.seed(42)
        
        # Pilotos de ejemplo
        drivers = [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120]
        years = [2021, 2022, 2023, 2024]
        
        data = []
        for driver in drivers:
            for year in years:
                # Base de 20 carreras por año
                for race in range(1, 21):
                    base_score = np.random.uniform(3, 9)
                    noise = np.random.normal(0, 1)
                    score = max(0, min(10, base_score + noise))
                    
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
                        'DNF_COUNT': np.random.choice([0, 0, 0, 1]),  # 25% DNF
                        'LAPMEAN': round(np.random.uniform(75, 95), 2),
                        'SC_COUNT': np.random.randint(0, 4),
                        'PS_COUNT': np.random.randint(0, 4)
                    })
        
        df = pd.DataFrame(data)
        st.info("📊 Usando datos de demostración")
        return df

    # ==================================================
    # CARGAR DATOS
    # ==================================================
    merged_dataset = load_data()

    # ==================================================
    # FEATURES
    # ==================================================

    features = [
        'POINTS', 'LAPS', 'MILLISECONDS', 'WEATHER_cloudy',
        'OVERTAKEN_POSITIONS_TOTAL', 'DNF_COUNT', 'LAPMEAN',
        'SC_COUNT', 'PS_COUNT'
    ]

    model_data = merged_dataset[['SCORE', 'YEAR'] + features].dropna()

    if model_data.empty:
        st.error("❌ No hay datos suficientes")
        st.stop()

    # ==================================================
    # SIDEBAR
    # ==================================================

    st.sidebar.markdown("### 🔎 Filters")

    driver_choice = st.sidebar.selectbox(
        "Driver",
        options=sorted(merged_dataset['DRIVERID'].unique())
    )

    year_choice = st.sidebar.selectbox(
        "Prediction Year",
        options=sorted(model_data['YEAR'].unique())
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 Model")

    model_choice = st.sidebar.selectbox(
        "Choose Algorithm",
        options=["XGBoost", "SVM", "Neural Network", "Linear Regression"],
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
    # NORMALIZATION + MODELS
    # ==================================================

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    @st.cache_resource
    def train_models(_X_train, _y_train, _X_train_scaled):
        with st.spinner("Entrenando modelos..."):
            lm = LinearRegression().fit(_X_train, _y_train)
            svm_model = SVR(kernel='rbf', C=1.0).fit(_X_train_scaled, _y_train)
            nn_model = MLPRegressor(hidden_layer_sizes=(10,5), max_iter=1000, random_state=123).fit(_X_train_scaled, _y_train)
            xgb_model = XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=123).fit(_X_train, _y_train)

            return {
                "Linear Regression": lm,
                "SVM": svm_model,
                "Neural Network": nn_model,
                "XGBoost": xgb_model
            }

    trained_models = train_models(X_train, y_train, X_train_scaled)

    # ==================================================
    # MODEL COMPARISON
    # ==================================================

    pred_lm = trained_models["Linear Regression"].predict(X_test)
    pred_svm = trained_models["SVM"].predict(X_test_scaled)
    pred_nn = trained_models["Neural Network"].predict(X_test_scaled)
    pred_xgb = trained_models["XGBoost"].predict(X_test)

    rmse_dict = {
        "Model": ["Linear", "SVM", "NN", "XGB"],
        "RMSE": [
            root_mean_squared_error(y_test, pred_lm),
            root_mean_squared_error(y_test, pred_svm),
            root_mean_squared_error(y_test, pred_nn),
            root_mean_squared_error(y_test, pred_xgb)
        ]
    }

    df_rmse = pd.DataFrame(rmse_dict)
    best_model_name = df_rmse.loc[df_rmse['RMSE'].idxmin(), 'Model']

    st.sidebar.markdown(f"**🏆 Best Model:** `{best_model_name}`")

    # ==================================================
    # FILTER + PREDICTION
    # ==================================================

    filtered_df = merged_dataset[
        (merged_dataset['DRIVERID'] == driver_choice) &
        (merged_dataset['YEAR'] == year_choice)
    ].sort_values(by='NAME_YEAR')

    if not filtered_df.empty:
        input_data_driver = filtered_df[features].copy().dropna()

        if not input_data_driver.empty:
            if model_choice == "Linear Regression":
                driver_preds = trained_models["Linear Regression"].predict(input_data_driver)
            elif model_choice == "SVM":
                driver_preds = trained_models["SVM"].predict(scaler.transform(input_data_driver))
            elif model_choice == "Neural Network":
                driver_preds = trained_models["Neural Network"].predict(scaler.transform(input_data_driver))
            else:
                driver_preds = trained_models["XGBoost"].predict(input_data_driver)

            filtered_df = filtered_df.copy()
            filtered_df.loc[input_data_driver.index, 'Prediction'] = driver_preds

            avg_score = round(filtered_df['SCORE'].mean(), 2)
            last_dnf = filtered_df['DNF_COUNT'].iloc[-1] if len(filtered_df) > 0 else 0
            total_stops = int(filtered_df['PS_COUNT'].sum())
            predicted_avg_score = round(float(driver_preds.mean()), 2)
        else:
            avg_score = last_dnf = total_stops = predicted_avg_score = 0
    else:
        avg_score = last_dnf = total_stops = predicted_avg_score = 0

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Score", avg_score)
    with col2: st.metric("DNFs", last_dnf)
    with col3: st.metric("Pit Stops", total_stops)
    with col4: st.metric(f"Predicted Score ({model_choice})", predicted_avg_score)

    st.markdown("---")

    # Plot
    st.subheader("📈 Real vs Predicted Score")
    if not filtered_df.empty and 'Prediction' in filtered_df.columns:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=filtered_df['NAME_YEAR'], 
            y=filtered_df['SCORE'], 
            mode='lines+markers', 
            name='Real',
            line=dict(color='#E10600', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=filtered_df['NAME_YEAR'], 
            y=filtered_df['Prediction'], 
            mode='lines+markers', 
            name='Predicted',
            line=dict(color='#FFD700', width=2, dash='dash')
        ))
        fig.update_layout(
            title=f"{driver_choice} - {year_choice}",
            xaxis_title="Race",
            yaxis_title="Score",
            template="plotly_dark",
            paper_bgcolor="#0A0F1F",
            plot_bgcolor="#151520",
            font=dict(color="white")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay suficientes datos para este piloto.")

    # Model Comparison
    st.subheader("📊 Model Comparison")
    st.dataframe(df_rmse.style.format({"RMSE": "{:.4f}"}), use_container_width=True, hide_index=True)
    