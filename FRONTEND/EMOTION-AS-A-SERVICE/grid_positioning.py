import fastf1
import streamlit as st
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
from pathlib import Path

# Importar el nuevo sortable_grid con números dinámicos
from components.sortable_grid import show_sortable_grid

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
    # PARRILA EN DOS COLUMNAS CON NÚMEROS DINÁMICOS
    # ============================================
    
    # Usar la nueva función con números dinámicos y JetBrains Mono
    sorted_drivers = show_sortable_grid(
        driver_abbrs,
        selected_race_name=selected_race_name,
        round_number=round_number
    )
    
    # Posiciones de parrilla (se actualizan automáticamente)
    grid_positions = {driver: pos + 1 for pos, driver in enumerate(sorted_drivers)}

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
                
                