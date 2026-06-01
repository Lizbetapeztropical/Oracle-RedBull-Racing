import fastf1
import streamlit as st
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
from pathlib import Path
from streamlit_sortables import sort_items



<<<<<<< Updated upstream
=======
from components.sortable_grid import show_sortable_grid
>>>>>>> Stashed changes


def show_grid_positioning():


<<<<<<< Updated upstream
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

=======
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
    # PARRILA ORDENABLE
    # ============================================
    
    sorted_drivers = show_sortable_grid(
        driver_abbrs,
        selected_race_name=selected_race_name,
        round_number=round_number
    )
    
    # Posiciones de parrilla
    grid_positions = {driver: pos + 1 for pos, driver in enumerate(sorted_drivers)}
>>>>>>> Stashed changes

   schedule = fastf1.get_event_schedule(2024)
   schedule = schedule.drop(0)


   event_names = schedule["EventName"].tolist()
   event_rounds = schedule["RoundNumber"].tolist()
   race_name_to_round = dict(zip(event_names, event_rounds))


   # ============================================
   # CSS PARA DOS COLUMNAS Y NÚMEROS
   # ============================================
  
   st.markdown("""
   <style>
       @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');
       @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;600;700;900&display=swap');
      
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
      
       .grid-title {
           color: #FFD700;
           text-align: center;
           margin: 1rem 0;
           font-family: 'Titillium Web', sans-serif;
       }
      
       .grid-col {
           background: #151520;
           border-radius: 15px;
           padding: 1rem;
           border-left: 4px solid #E10600;
           height: 100%;
       }
      
       .grid-col h3 {
           color: #FFD700;
           text-align: center;
           margin-bottom: 1rem;
           font-family: 'Titillium Web', sans-serif;
       }
      
       /* Estilo de cada elemento de la lista sortable */
       [data-testid="stVerticalBlock"] div div div ul {
           padding: 0;
           margin: 0;
           list-style: none;
       }
      
       [data-testid="stVerticalBlock"] div div div li {
           list-style-type: none;
           background: linear-gradient(90deg, #1A1A2E 0%, #22223B 100%);
           color: #FFFFFF;
           padding: 12px 16px;
           margin-bottom: 8px;
           border-radius: 12px;
           display: flex;
           align-items: center;
           justify-content: space-between;
           border-left: 4px solid #E10600;
           transition: all 0.2s ease;
           cursor: grab;
           font-family: 'Titillium Web', sans-serif;
           font-size: 16px;
           font-weight: 500;
       }
      
       [data-testid="stVerticalBlock"] div div div li:hover {
           transform: translateX(5px);
           background: linear-gradient(90deg, #22223B 0%, #2A2A45 100%);
           border-left-color: #FFD700;
       }
      
       /* Número de posición - JetBrains Mono */
       .pos-number {
           background-color: #E10600;
           color: white;
           font-family: 'JetBrains Mono', monospace;
           font-weight: 700;
           font-size: 14px;
           padding: 4px 10px;
           border-radius: 20px;
           min-width: 40px;
           text-align: center;
       }
      
       .driver-text {
           flex: 1;
           margin-left: 15px;
           font-weight: 600;
       }
      
       @media (max-width: 768px) {
           .two-columns {
               flex-direction: column;
           }
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
       <p><span class="round">ROUND {round_number}{suffix}</span> · GRAN PREMIO</p>
   </div>
   """, unsafe_allow_html=True)


   # ============================================
   # PARRILA EN DOS COLUMNAS
   # ============================================
  
   st.markdown('<h2 class="grid-title">STARTING GRID</h2>', unsafe_allow_html=True)
  
   # Inicializar orden en session_state
   if 'grid_order' not in st.session_state:
       st.session_state.grid_order = driver_abbrs.copy()
  
   # Botón de reset
   col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
   with col_btn2:
       if st.button("🔄 Resetear orden original", use_container_width=True):
           st.session_state.grid_order = driver_abbrs.copy()
           st.rerun()
  
   # Dividir en dos mitades
   mid = len(driver_abbrs) // 2
  
   # Función para mostrar lista ordenable con números
   def show_sortable_column(drivers, start_pos, column_key):
       # Crear lista con formato "POS. DRIVER" para mostrar números
       formatted_drivers = [f"{start_pos + i}. {driver}" for i, driver in enumerate(drivers)]
      
       # Mostrar lista ordenable
       sorted_formatted = sort_items(formatted_drivers, direction="vertical", key=column_key)
      
       # Extraer solo los nombres sin el número
       sorted_drivers = [item.split(". ", 1)[1] for item in sorted_formatted]
      
       return sorted_drivers
  
   # Crear dos columnas
   col_left, col_right = st.columns(2)
  
   with col_left:
       st.markdown('<div class="grid-col"><h3>TOP 10</h3>', unsafe_allow_html=True)
       sorted_left = show_sortable_column(st.session_state.grid_order[:mid], 1, "left_column")
       st.markdown('</div>', unsafe_allow_html=True)
  
   with col_right:
       st.markdown('<div class="grid-col"><h3>BOTTOM 10</h3>', unsafe_allow_html=True)
       sorted_right = show_sortable_column(st.session_state.grid_order[mid:], mid + 1, "right_column")
       st.markdown('</div>', unsafe_allow_html=True)
  
   # Combinar resultados
   sorted_drivers = sorted_left + sorted_right
  
   # Actualizar session_state si cambió
   if sorted_drivers != st.session_state.grid_order:
       st.session_state.grid_order = sorted_drivers
       st.rerun()
  
   # Posiciones de parrilla
   grid_positions = {driver: pos + 1 for pos, driver in enumerate(sorted_drivers)}


   # ============================================
   # ORDEN ACTUAL (EXPANDIBLE)
   # ============================================
  
   with st.expander("📋 Ver orden completo de parrilla"):
       for i, driver in enumerate(sorted_drivers, 1):
           st.markdown(f"""
           <div style="display: flex; justify-content: space-between; align-items: center;
                       background: #1A1A2E; padding: 6px 12px; margin-bottom: 4px; border-radius: 6px;">
               <span style="color: white; font-weight: 500;">{driver}</span>
               <span style="background-color: #E10600; font-family: 'JetBrains Mono', monospace;
                           font-weight: bold; padding: 2px 10px; border-radius: 15px;">
                   {i}
               </span>
           </div>
           """, unsafe_allow_html=True)


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
               

<<<<<<< Updated upstream
=======
            except Exception as e:
                st.error(f"Error en la predicción: {e}")
                
>>>>>>> Stashed changes
