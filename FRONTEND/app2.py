# analytics.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from xgboost import XGBRegressor
from sklearn.metrics import root_mean_squared_error

def show_analytics():
    st.markdown("<h1 style='text-align:center;'>🏁 Oracle Red Bull Racing</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>Performance + Predictive Intelligence</p>", unsafe_allow_html=True)
    
    # =========================
    # LOAD DATA
    # =========================
    @st.cache_data
    def load_data():
        path = '/Users/ingridetb/Documents/clean and merged/merged_dataset.csv'
        df = pd.read_csv(path)
        df['YEAR'] = df['NAME_YEAR'].astype(str).str[0:4].astype(int)
        return df

    try:
        merged_dataset = load_data()
    except FileNotFoundError:
        st.error("⚠️ No se encontró el archivo de datos. Revisa la ruta de 'merged_dataset.csv'.")
        st.stop()

    # =========================
    # PREP DATA
    # =========================
    features = [
        'DRIVER_POINTS_BEFORE_RACE', 'POINTS', 'LAPS', 'MILLISECONDS',
        'WEATHER_rain', 'WEATHER_WET', 'WEATHER_cloudy',
        'OVERTAKEN_POSITIONS_TOTAL', 'DNF_COUNT', 'LAPMEAN',
        'FASTESTLAP', 'PS_COUNT'
    ]

    model_data = merged_dataset[['SCORE', 'YEAR'] + features].dropna()

    # =========================
    # SIDEBAR FILTERS (Añadidos a la barra lateral existente)
    # =========================
    st.sidebar.markdown("### 🔎 Filters")
    driver_choice = st.sidebar.selectbox("Driver", options=sorted(merged_dataset['DRIVERID'].unique()))
    year_choice = st.sidebar.selectbox("Prediction Year", options=sorted(model_data['YEAR'].unique()))

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 Model")
    model_choice = st.sidebar.selectbox(
        "Choose Algorithm",
        options=["XGBoost", "SVM", "Neural Network", "Linear Regression"],
        index=0
    )

    # =========================
    # SPLIT DINÁMICO
    # =========================
    train_data = model_data[model_data['YEAR'] < year_choice]
    test_data = model_data[model_data['YEAR'] == year_choice]

    if train_data.empty or test_data.empty:
        st.warning(f"⚠️ No hay suficientes datos históricos para entrenar o evaluar el año {year_choice}.")
        st.stop()

    X_train = train_data[features]
    y_train = train_data['SCORE']
    X_test = test_data[features]
    y_test = test_data['SCORE']

    # =========================
    # NORMALIZATION
    # =========================
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # =========================
    # MODELS
    # =========================
    @st.cache_resource
    def train_models(_X_tr, _y_tr, _X_tr_sc):
        lm = LinearRegression().fit(_X_tr, _y_tr)
        svm_mod = SVR(kernel='rbf', C=1.0).fit(_X_tr_sc, _y_tr)
        nn = MLPRegressor(hidden_layer_sizes=(5,), max_iter=1000, random_state=123).fit(_X_tr_sc, _y_tr)
        xgb = XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=123).fit(_X_tr, _y_tr)
        return {"Linear Regression": lm, "SVM": svm_mod, "Neural Network": nn, "XGBoost": xgb}

    trained_models = train_models(X_train, y_train, X_train_scaled)

    # =========================
    # MODEL COMPARISON (Métricas de Test)
    # =========================
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

    # =========================
    # FILTERED DRIVER DATA
    # =========================
    filtered_df = merged_dataset[(merged_dataset['DRIVERID'] == driver_choice) & (merged_dataset['YEAR'] == year_choice)].sort_values(by='NAME_YEAR')

    # =========================
    # KPIs Y PREDICCIONES
    # =========================
    if not filtered_df.empty:
        input_data_driver = filtered_df[features].dropna()
        
        avg_score = round(filtered_df['SCORE'].mean(), 2)
        last_dnf = filtered_df['DNF_COUNT'].iloc[-1] if 'DNF_COUNT' in filtered_df.columns else 0
        total_stops = int(filtered_df['PS_COUNT'].sum())
        
        if model_choice == "Linear Regression":
            driver_preds = trained_models["Linear Regression"].predict(input_data_driver)
        elif model_choice == "SVM":
            input_scaled = scaler.transform(input_data_driver)
            driver_preds = trained_models["SVM"].predict(input_scaled)
        elif model_choice == "Neural Network":
            input_scaled = scaler.transform(input_data_driver)
            driver_preds = trained_models["Neural Network"].predict(input_scaled)
        else:
            driver_preds = trained_models["XGBoost"].predict(input_data_driver)
            
        predicted_avg_score = round(driver_preds.mean(), 2)
        filtered_df['Prediction'] = driver_preds
    else:
        avg_score, last_dnf, total_stops, predicted_avg_score = "No data", "No data", "No data", "No data"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div style='padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); background-color: #f8f9fa; margin-bottom: 10px;'><h6>Score</h6><h2 style='color:#D00000;'>{avg_score}</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); background-color: #f8f9fa; margin-bottom: 10px;'><h6>DNFs</h6><h2>{last_dnf}</h2></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div style='padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); background-color: #f8f9fa; margin-bottom: 10px;'><h6>Pit Stops</h6><h2>{total_stops}</h2></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div style='padding: 20px; border-radius: 10px; background-color: #D00000; color: white; margin-bottom: 10px;'><h6>Predicted Score - {model_choice}</h6><h2>{predicted_avg_score}</h2></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # PLOT (PLOTLY INTERACTIVO)
    # =========================
    st.markdown("### 📈 Real vs Predicted Score")
    if not filtered_df.empty and 'Prediction' in filtered_df.columns:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=filtered_df['NAME_YEAR'], y=filtered_df['SCORE'],
            mode='lines+markers', name='Real',
            line=dict(color='#D00000', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=filtered_df['NAME_YEAR'], y=filtered_df['Prediction'],
            mode='lines+markers', name='Predicted',
            line=dict(color='orange', width=3, dash='dash')
        ))
        
        fig.update_layout(
            title=f"Real vs Predicted - {year_choice} ({driver_choice})",
            xaxis_title="Race", yaxis_title="Score",
            template="minimal",
            xaxis=dict(tickangle=45),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay suficientes datos de carreras para este piloto en el año seleccionado.")

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # MODEL COMPARISON TABLE
    # =========================
    st.markdown("### 📊 Model Comparison")
    st.dataframe(df_rmse.style.format({"RMSE": "{:.4f}"}), use_container_width=True, hide_index=True)