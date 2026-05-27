import fastf1
import streamlit as st
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
from pathlib import Path
from streamlit_sortables import sort_items


def show_grid_positioning():

    BASE_DIR = Path(__file__).resolve().parent
    MODEL_DIR = (
        BASE_DIR.parent.parent
        / "BACKEND"
        / "EMOTION-AS-A-SERVICE"
        / "model"
    )

    stack_model = joblib.load(MODEL_DIR / "f1_race_predictor_model.pkl")
    scaler = joblib.load(MODEL_DIR / "scaler.pkl")
    feature_columns = joblib.load(MODEL_DIR / "feature_columns.pkl")
    filtered_drivers_info = pd.read_csv(MODEL_DIR / "DATA" / "filtered_drivers_info.csv")

    driver_abbrs = filtered_drivers_info["Abbreviation"].tolist()

    schedule = fastf1.get_event_schedule(2024)
    schedule = schedule.drop(0)

    event_names = schedule["EventName"].tolist()
    event_rounds = schedule["RoundNumber"].tolist()
    race_name_to_round = dict(zip(event_names, event_rounds))

    # ============================================
    # CSS PARA DOS COLUMNAS
    # ============================================
    
    st.markdown("""
    <style>
        /* Header de carrera */
        .race-header {
            background: linear-gradient(90deg, #0A0F1F 0%, #E10600 100%);
            padding: 1rem 2rem;
            border-radius: 15px;
            margin: 1rem 0 2rem 0;
            border-bottom: 3px solid #FFD700;
            text-align: center;
        }
        .race-header h2 {
            color: #FFFFFF;
            font-family: 'Titillium Web', sans-serif;
            font-weight: 700;
            margin: 0;
            font-size: 1.8rem;
        }
        .race-header p {
            color: #C0C0C0;
            margin: 0.5rem 0 0 0;
        }
        .race-header .round {
            color: #FFD700;
            font-weight: 600;
        }
        
        /* Contenedor de dos columnas */
        .two-columns {
            display: flex;
            gap: 2rem;
            margin: 1rem 0;
        }
        .column {
            flex: 1;
            background: #151520;
            border-radius: 15px;
            padding: 1rem;
            border-left: 4px solid #E10600;
        }
        .column h3 {
            color: #FFD700;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        /* Estilo de cada piloto */
        .driver-item {
            background: linear-gradient(90deg, #1A1A2E 0%, #22223B 100%);
            color: white;
            padding: 12px 16px;
            margin-bottom: 8px;
            border-radius: 10px;
            border-left: 4px solid #E10600;
            font-family: 'Titillium Web', sans-serif;
            cursor: pointer;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .two-columns { flex-direction: column; }
        }
    </style>
    """, unsafe_allow_html=True)

    # ============================================
    # TÍTULO PRINCIPAL
    # ============================================
    
    st.markdown("""
    <h1 style="color: #E10600; text-align: center; font-family: 'Titillium Web', sans-serif;">
        LIGHTS OUT SIMULATOR
    </h1>
    <p style="color: #C0C0C0; text-align: center; margin-bottom: 2rem;">
        Selecciona la carrera y ordena la parrilla para predecir los resultados finales
    </p>
    """, unsafe_allow_html=True)

    # ============================================
    # SELECCIÓN DE CARRERA
    # ============================================
    
    selected_race_name = st.selectbox("Selecciona el Gran Premio", event_names)
    round_number = race_name_to_round[selected_race_name]

    # ============================================
    # HEADER DE CARRERA
    # ============================================
    
    def get_suffix(n):
        if 11 <= n <= 13:
            return "TH"
        last = n % 10
        if last == 1: return "ST"
        if last == 2: return "ND"
        if last == 3: return "RD"
        return "TH"
    
    suffix = get_suffix(round_number)
    
    st.markdown(f"""
    <div class="race-header">
        <h2>{selected_race_name}</h2>
        <p><span class="round">ROUND {round_number}{suffix}</span> · CIRCUITO INTERNACIONAL</p>
    </div>
    """, unsafe_allow_html=True)

    # ============================================
    # PARRILA EN DOS COLUMNAS CON SORTABLE
    # ============================================
    
    st.markdown('<h3 style="color: #FFD700;">STARTING GRID</h3>', unsafe_allow_html=True)
    
    # Dividir pilotos en dos mitades
    mid = len(driver_abbrs) // 2
    left_drivers = driver_abbrs[:mid]
    right_drivers = driver_abbrs[mid:]
    
    # Crear dos columnas con st.columns (funciona con sort_items)
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="column"><h3>TOP 10</h3>', unsafe_allow_html=True)
        sorted_left = sort_items(left_drivers, direction="vertical")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        st.markdown('<div class="column"><h3>BOTTOM 10</h3>', unsafe_allow_html=True)
        sorted_right = sort_items(right_drivers, direction="vertical")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Combinar resultados
    sorted_drivers = sorted_left + sorted_right
    
    # Posiciones de parrilla
    grid_positions = {driver: pos + 1 for pos, driver in enumerate(sorted_drivers)}

    # ============================================
    # ORDEN ACTUAL (EXPANDIBLE)
    # ============================================
    
    with st.expander("Ver orden actual de parrilla"):
        order_df = pd.DataFrame({
            "Posición de Salida": range(1, len(sorted_drivers) + 1),
            "Piloto": sorted_drivers
        })
        st.dataframe(order_df, use_container_width=True, hide_index=True)

    # ============================================
    # PREDICCIÓN
    # ============================================
    
    if st.button("PREDECIR RESULTADOS", use_container_width=True):
        with st.spinner("Procesando predicciones..."):
            try:
                GridPosition = [grid_positions[driver] for driver in driver_abbrs]

                pred_gp_data = pd.DataFrame({
                    "Round": [round_number] * 20,
                    "Abbreviation": driver_abbrs,
                    "GridPosition": GridPosition,
                    "Points": filtered_drivers_info["Points"],
                    "AvgQualiPosition": filtered_drivers_info["AvgQualiPosition"],
                    "AvgRacePosition": filtered_drivers_info["AvgRacePosition"],
                    "QualifyingScore": (filtered_drivers_info["AvgQualiPosition"] + GridPosition) / 2
                })

                label_enc_driver = LabelEncoder()
                label_enc_driver.fit(driver_abbrs)
                pred_gp_data["Abbreviation"] = label_enc_driver.transform(pred_gp_data["Abbreviation"])

                pred_gp_data = pred_gp_data[feature_columns]
                X_scaled = scaler.transform(pred_gp_data)
                predicted_positions = stack_model.predict(X_scaled)
                pred_gp_data["PredictedPosition"] = predicted_positions

                results = pred_gp_data.sort_values("PredictedPosition").reset_index(drop=True)
                results.index += 1
                results = results.reset_index()
                results["Driver_Abbreviation"] = label_enc_driver.inverse_transform(results["Abbreviation"])

                st.markdown(f"""
                <div style="background:rgba(225,6,0,0.15); padding:1rem; border-radius:10px; margin:1rem 0;">
                    <p style="color:#FFD700; font-weight:700; font-size:1.2rem;">RESULTADOS PREDICHOS</p>
                    <p style="color:white;">{selected_race_name} - Ronda {round_number}</p>
                </div>
                """, unsafe_allow_html=True)

                display_results = results[["index", "Driver_Abbreviation"]]
                display_results.columns = ["Posición Final", "Piloto"]
                st.dataframe(display_results, use_container_width=True)

            except Exception as e:
                st.error(f"Error en la predicción: {e}")