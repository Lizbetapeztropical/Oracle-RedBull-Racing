import fastf1
import streamlit as st
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
from streamlit_sortables import sort_items
from pathlib import Path
from datetime import datetime

from analytics import show_analytics 

# ============================================
# CONFIGURACION DE PAGINA
# ============================================

st.set_page_config(
    page_title="Oracle Red Bull Racing | F1 Predictor",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CSS PERSONALIZADO - TEMA ORACLE RED BULL RACING
# ============================================

custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;600;700;900&display=swap');
    
    :root {
        --rb-dark-blue: #0A0F1F;
        --rb-red: #E10600;
        --rb-white: #FFFFFF;
        --rb-silver: #C0C0C0;
        --rb-gold: #FFD700;
        --rb-dark-bg: #0D0D1A;
        --rb-card-bg: #151520;
        --rb-hover: #1A1A2E;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--rb-dark-blue) 0%, var(--rb-dark-bg) 100%);
    }
    
    /* Header principal */
    .main-header {
        background: linear-gradient(90deg, var(--rb-dark-blue) 0%, var(--rb-red) 100%);
        padding: 1.5rem 2rem;
        border-radius: 0 0 15px 15px;
        margin-bottom: 2rem;
        border-bottom: 3px solid var(--rb-gold);
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    .main-header h1 {
        font-family: 'Titillium Web', sans-serif;
        font-size: 2rem;
        font-weight: 900;
        letter-spacing: 2px;
        margin: 0;
        color: var(--rb-white);
    }
    
    .main-header h1 span {
        color: var(--rb-gold);
    }
    
    .main-header p {
        font-family: 'Titillium Web', sans-serif;
        font-size: 0.85rem;
        color: var(--rb-silver);
        margin: 0.5rem 0 0 0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--rb-dark-blue) 0%, var(--rb-card-bg) 100%);
        border-right: 1px solid var(--rb-red);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--rb-gold);
    }
    
    [data-testid="stSidebar"] .stRadio label {
        color: var(--rb-white);
        font-weight: 600;
    }
    
    /* Tarjetas */
    .custom-card {
        background: var(--rb-card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid var(--rb-red);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.2s;
    }
    
    .custom-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(225,6,0,0.15);
    }
    
    /* Botones */
    .stButton button {
        background: linear-gradient(90deg, var(--rb-red) 0%, #B80500 100%);
        color: var(--rb-white);
        font-family: 'Titillium Web', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        padding: 0.6rem 2rem;
        border: none;
        border-radius: 30px;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton button:hover {
        background: linear-gradient(90deg, #B80500 0%, var(--rb-red) 100%);
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(225,6,0,0.4);
    }
    
    /* Tablas */
    .dataframe {
        background: var(--rb-card-bg);
        border-radius: 12px;
        overflow: hidden;
    }
    
    .dataframe th {
        background: var(--rb-red);
        color: var(--rb-white);
        font-weight: 700;
        padding: 12px;
    }
    
    .dataframe td {
        background: var(--rb-card-bg);
        color: var(--rb-white);
        padding: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    .dataframe tr:hover td {
        background: var(--rb-hover);
    }
    
    /* Selectbox */
    .stSelectbox label {
        color: var(--rb-white);
        font-weight: 600;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        background-color: var(--rb-card-bg);
        border: 1px solid var(--rb-red);
        border-radius: 8px;
    }
    
    /* Lista sortable (drag & drop) */
    [data-testid="stVerticalBlock"] div div div ul {
        padding: 0;
    }
    
    [data-testid="stVerticalBlock"] div div div li {
        list-style-type: none;
        background: linear-gradient(90deg, var(--rb-card-bg) 0%, var(--rb-hover) 100%);
        color: var(--rb-white);
        padding: 20px;
        margin-bottom: 12px;
        border-radius: 18px;
        font-size: 24px;
        font-weight: 700;
        text-align: center;
        border-left: 8px solid var(--rb-red);
        box-shadow: 0 4px 15px rgba(0,0,0,0.35);
        transition: 0.2s ease;
        cursor: grab;
        font-family: 'Titillium Web', sans-serif;
    }
    
    [data-testid="stVerticalBlock"] div div div li:hover {
        transform: scale(1.01);
        border-left-width: 12px;
    }
    
    /* Success message */
    .stAlert {
        background: linear-gradient(90deg, var(--rb-gold), #FFA500);
        color: var(--rb-dark-blue);
        font-weight: 700;
        border-radius: 10px;
        border: none;
    }
    
    /* Metricas */
    .metric-box {
        text-align: center;
        background: var(--rb-card-bg);
        padding: 0.75rem;
        border-radius: 10px;
        border-left: 3px solid var(--rb-gold);
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 900;
        color: var(--rb-gold);
    }
    
    .metric-label {
        font-size: 0.7rem;
        color: var(--rb-silver);
        text-transform: uppercase;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 1.5rem;
        margin-top: 2rem;
        border-top: 1px solid rgba(192,192,192,0.2);
        font-size: 0.7rem;
        color: var(--rb-silver);
    }
    
    /* Subheader */
    .stSubheader {
        color: var(--rb-gold);
        font-family: 'Titillium Web', sans-serif;
        font-weight: 700;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# ============================================
# HEADER PERSONALIZADO
# ============================================

st.markdown(f"""
<div class="main-header">
    <h1>ORACLE <span>RED BULL RACING</span></h1>
    <p>F1 Race Predictor - Predictive Analytics Dashboard</p>
    <p style="font-size:0.7rem; margin-top:5px;">{datetime.now().strftime("%d %B %Y")}</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR DE NAVEGACION
# ============================================

with st.sidebar:
    st.markdown("## NAVEGACION")
    page = st.radio("Ir a:", ["Podium Simulator", "Red Bull Analytics"])
    st.markdown("---")
    st.markdown("### Oracle Red Bull Racing")
    st.markdown("Predictive Analytics System")
    st.markdown("---")
    st.markdown(f"*Version 2.0*")

# ============================================
# RED BULL ANALYTICS
# ============================================

if page == "Red Bull Analytics":
    show_analytics()
    
# ============================================
# PODIUM SIMULATOR
# ============================================

else:
    BASE_DIR = Path(__file__).resolve().parent
    MODEL_DIR = BASE_DIR.parent.parent / "BACKEND" / "EMOTION-AS-A-SERVICE" / "model"

    with st.spinner("Cargando modelos y datos..."):
        try:
            stack_model = joblib.load(MODEL_DIR / "f1_race_predictor_model.pkl")
            scaler = joblib.load(MODEL_DIR / "scaler.pkl")
            feature_columns = joblib.load(MODEL_DIR / "feature_columns.pkl")
            filtered_drivers_info = pd.read_csv(
                MODEL_DIR / "DATA" / "filtered_drivers_info.csv"
            )
            
            driver_abbrs = filtered_drivers_info["Abbreviation"].tolist()
            
            schedule = fastf1.get_event_schedule(2024)
            schedule = schedule.drop(0)
            
            event_names = schedule['EventName'].tolist()
            event_rounds = schedule['RoundNumber'].tolist()
            race_name_to_round = dict(zip(event_names, event_rounds))
            
            st.success("Modelos cargados correctamente")
        except Exception as e:
            st.error(f"Error cargando modelos: {e}")
            st.stop()

    # ============================================
    # METRICAS RAPIDAS
    # ============================================
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-box"><div class="metric-value">20</div><div class="metric-label">Pilotos</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-box"><div class="metric-value">{len(event_names)}</div><div class="metric-label">Carreras 2024</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-box"><div class="metric-value">XGBoost</div><div class="metric-label">Modelo Principal</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-box"><div class="metric-value">R²:0.71</div><div class="metric-label">Precision</div></div>', unsafe_allow_html=True)

    # ============================================
    # SELECCION DE CARRERA
    # ============================================
    
    st.markdown('<div class="custom-card"><h3>1. SELECCIONA LA CARRERA</h3>', unsafe_allow_html=True)
    selected_race_name = st.selectbox("Gran Premio", event_names, label_visibility="collapsed")
    round_number = race_name_to_round[selected_race_name]
    st.markdown(f'<p style="color: #C0C0C0; margin-top: 0.5rem;">Ronda {round_number} - {selected_race_name}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================
    # POSICIONES DE PARRILLA (SORTABLE)
    # ============================================
    
    st.markdown('<div class="custom-card"><h3>2. POSICIONES DE PARRILLA</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color: #C0C0C0;">Arrastra los pilotos para cambiar el orden de salida</p>', unsafe_allow_html=True)

    default_order = driver_abbrs.copy()
    sorted_drivers = sort_items(default_order, direction="vertical")

    grid_positions = {
        driver: position + 1
        for position, driver in enumerate(sorted_drivers)
    }

    grid_df = pd.DataFrame({
        "Posicion de Salida": range(1, len(sorted_drivers)+1),
        "Piloto": sorted_drivers
    })

    st.dataframe(
        grid_df,
        use_container_width=True,
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================
    # PREDICCION
    # ============================================
    
    st.markdown('<div class="custom-card"><h3>3. PREDICCION</h3>', unsafe_allow_html=True)

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
                results.rename_axis("PredictedRank", inplace=True)
                results = results.reset_index()
                results["Driver_Abbreviation"] = label_enc_driver.inverse_transform(results["Abbreviation"])


                # Resultados con diseño
                st.markdown(f'<div style="background:rgba(225,6,0,0.15); padding:1rem; border-radius:10px; margin:1rem 0;">', unsafe_allow_html=True)
                st.markdown(f'<p style="color:#FFD700; font-weight:700; font-size:1.2rem;">RESULTADOS PREDICHOS</p>', unsafe_allow_html=True)
                st.markdown(f'<p>{selected_race_name} - Ronda {round_number}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                display_results = results[["PredictedRank", "Driver_Abbreviation"]]
                display_results.columns = ["Posicion Final", "Piloto"]
                st.dataframe(display_results, use_container_width=True)

            except Exception as e:
                st.error(f"Error en la prediccion: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# FOOTER
# ============================================

st.markdown("""
<div class="footer">
    Oracle Red Bull Racing - Predictive Analytics<br>
    Datos procesados via MongoDB | Modelo XGBoost | Dashboard v2.0<br>
    Sistema de Prediccion de Resultados F1
</div>
""", unsafe_allow_html=True)