# analytics.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from pymongo import MongoClient

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
        "<h1 style='text-align:center;'>🏁 Oracle Red Bull Racing</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center; color:gray;'>Performance + Predictive Intelligence</p>",
        unsafe_allow_html=True
    )

    # ==================================================
    # LOAD DATA FROM MONGODB (DOCKER)
    # ==================================================

    @st.cache_data
    def load_data():
        try:
            client = MongoClient(
                host="localhost",
                port=27017,
                username="admin",
                password="oracle",
                authSource="admin"
            )
            
            db = client["redbull_racing"] 
            collection = db["merged_races"]

            cursor = collection.find()
            df = pd.DataFrame(list(cursor))

            if df.empty:
                st.error("❌ La colección en MongoDB está vacía.")
                st.stop()

            if '_id' in df.columns:
                df = df.drop(columns=['_id'])

        except Exception as e:
            st.error(f"❌ Error al conectar con MongoDB:\n{e}")
            st.stop()

        # LIMPIEZA DE DATOS
        df['YEAR'] = pd.to_numeric(
            df['NAME_YEAR'].astype(str).str[:4], 
            errors='coerce'
        ).astype('Int64')

        numeric_cols = ['SCORE', 'DRIVER_POINTS_BEFORE_RACE', 'POINTS', 'LAPS',
                       'MILLISECONDS', 'OVERTAKEN_POSITIONS_TOTAL', 'DNF_COUNT',
                       'LAPMEAN', 'FASTESTLAP', 'PS_COUNT', 'WEATHER_rain',
                       'WEATHER_WET', 'WEATHER_cloudy']

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    # ==================================================
    # CARGAR DATOS
    # ==================================================
    merged_dataset = load_data()

    # ==================================================
    # FEATURES
    # ==================================================

    features = [
        'DRIVER_POINTS_BEFORE_RACE',
        'POINTS',
        'LAPS',
        'MILLISECONDS',
        'WEATHER_rain',
        'WEATHER_WET',
        'WEATHER_cloudy',
        'OVERTAKEN_POSITIONS_TOTAL',
        'DNF_COUNT',
        'LAPMEAN',
        'FASTESTLAP',
        'PS_COUNT'
    ]

    model_data = merged_dataset[['SCORE', 'YEAR'] + features].dropna()

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
        options=[
            "XGBoost",
            "SVM",
            "Neural Network",
            "Linear Regression"
        ],
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
        lm = LinearRegression().fit(_X_train, _y_train)
        svm_model = SVR(kernel='rbf', C=1.0).fit(_X_train_scaled, _y_train)
        nn_model = MLPRegressor(hidden_layer_sizes=(5,), max_iter=1000, random_state=123).fit(_X_train_scaled, _y_train)
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
            avg_score = last_dnf = total_stops = predicted_avg_score = "No data"
    else:
        avg_score = last_dnf = total_stops = predicted_avg_score = "No data"

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
        fig.add_trace(go.Scatter(x=filtered_df['NAME_YEAR'], y=filtered_df['SCORE'], mode='lines+markers', name='Real'))
        fig.add_trace(go.Scatter(x=filtered_df['NAME_YEAR'], y=filtered_df['Prediction'], mode='lines+markers', name='Predicted'))
        fig.update_layout(title=f"{driver_choice} - {year_choice}", xaxis_title="Race", yaxis_title="Score", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay suficientes datos para este piloto.")

    # Model Comparison
    st.subheader("📊 Model Comparison")
    st.dataframe(df_rmse.style.format({"RMSE": "{:.4f}"}), use_container_width=True, hide_index=True)