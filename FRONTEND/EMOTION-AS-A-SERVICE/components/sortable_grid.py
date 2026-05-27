import streamlit as st
import pandas as pd
from streamlit_sortables import sort_items

def show_sortable_grid(driver_abbrs, selected_race_name=None, round_number=None):
    """
    Muestra una lista ordenable (drag & drop) de pilotos
    con diseño de dos columnas y título de carrera
    """
    
    # CSS personalizado con los colores de Oracle Red Bull Racing
    st.markdown("""
    <style>
        /* Contenedor principal de la carrera */
        .race-header {
            background: linear-gradient(90deg, #0A0F1F 0%, #E10600 100%);
            padding: 1rem 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
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
            font-family: 'Titillium Web', sans-serif;
            margin: 0.5rem 0 0 0;
            font-size: 1rem;
        }
        
        .race-header .round {
            color: #FFD700;
            font-weight: 600;
        }
        
        /* Contenedor de la parrilla en dos columnas */
        .grid-container {
            display: flex;
            gap: 2rem;
            margin-top: 1rem;
        }
        
        .grid-column {
            flex: 1;
            background: #151520;
            border-radius: 15px;
            padding: 1rem;
            border-left: 4px solid #E10600;
        }
        
        .grid-column h4 {
            color: #FFD700;
            font-family: 'Titillium Web', sans-serif;
            text-align: center;
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }
        
        /* Estilo de cada elemento de la lista */
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
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-left: 4px solid #E10600;
            transition: all 0.2s ease;
            cursor: grab;
            font-family: 'Titillium Web', sans-serif;
        }
        
        [data-testid="stVerticalBlock"] div div div li:hover {
            transform: translateX(5px);
            border-left-color: #FFD700;
            background: linear-gradient(90deg, #22223B 0%, #2A2A45 100%);
        }
        
        [data-testid="stVerticalBlock"] div div div li:active {
            cursor: grabbing;
            background: #E10600;
        }
        
        /* Posición del piloto */
        .position-number {
            background-color: #E10600;
            color: #FFFFFF;
            font-weight: bold;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 14px;
            min-width: 45px;
            text-align: center;
        }
        
        .driver-name {
            flex: 1;
            margin-left: 15px;
            font-weight: 600;
        }
        
        /* Sufijo (ST, ND, RD, TH) */
        .position-suffix {
            color: #FFD700;
            font-size: 12px;
            margin-left: 5px;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .grid-container {
                flex-direction: column;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # ============================================
    # TÍTULO DE LA CARRERA SELECCIONADA
    # ============================================
    
    if selected_race_name:
        # Obtener el sufijo de la ronda
        def get_round_suffix(n):
            if 11 <= n <= 13:
                return "TH"
            last_digit = n % 10
            if last_digit == 1:
                return "ST"
            elif last_digit == 2:
                return "ND"
            elif last_digit == 3:
                return "RD"
            else:
                return "TH"
        
        round_suffix = get_round_suffix(round_number) if round_number else ""
        round_text = f"{round_number}{round_suffix}" if round_number else ""
        
        st.markdown(f"""
        <div class="race-header">
            <h2>{selected_race_name}</h2>
            <p><span class="round">ROUND {round_text}</span> · MIAMI INTERNATIONAL AUTODROME</p>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================
    # PARRILA EN DOS COLUMNAS
    # ============================================
    
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h3 style="color: #FFD700; font-family: 'Titillium Web', sans-serif;">STARTING GRID</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Dividir los pilotos en dos mitades
    mid_point = len(driver_abbrs) // 2
    left_drivers = driver_abbrs[:mid_point]
    right_drivers = driver_abbrs[mid_point:]
    
    # Crear dos columnas
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="grid-column"><h4>TOP 10</h4>', unsafe_allow_html=True)
        
        # Crear una lista ordenable para la columna izquierda
        sorted_left = sort_items(left_drivers, direction="vertical")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        st.markdown('<div class="grid-column"><h4>BOTTOM 10</h4>', unsafe_allow_html=True)
        
        # Crear una lista ordenable para la columna derecha
        sorted_right = sort_items(right_drivers, direction="vertical")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Combinar resultados de ambas columnas
    sorted_drivers = sorted_left + sorted_right
    
    # ============================================
    # MOSTRAR ORDEN ACTUAL (opcional)
    # ============================================
    
    with st.expander("Ver orden actual de parrilla"):
        order_df = pd.DataFrame({
            "Posición": range(1, len(sorted_drivers) + 1),
            "Piloto": sorted_drivers
        })
        st.dataframe(order_df, use_container_width=True, hide_index=True)
    
    return sorted_drivers
