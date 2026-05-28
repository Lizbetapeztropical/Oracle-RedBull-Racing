import streamlit as st
from streamlit_sortables import sort_items

def show_sortable_grid(driver_abbrs, selected_race_name=None, round_number=None):
    """
    Muestra una lista ordenable (drag & drop) de pilotos
    con números dinámicos en el lado derecho
    """
    
    # CSS con JetBrains Mono y números visibles
    st.markdown("""
    <style>
        /* Importar JetBrains Mono */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');
        
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
        .grid-2cols {
            display: flex;
            gap: 2rem;
            margin-top: 1rem;
        }
        .grid-col {
            flex: 1;
            background: #151520;
            border-radius: 15px;
            padding: 1rem;
            border-left: 4px solid #E10600;
        }
        .grid-col h4 {
            color: #FFD700;
            text-align: center;
            margin-bottom: 1rem;
            font-size: 1.1rem;
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
        
        [data-testid="stVerticalBlock"] div div div li:active {
            cursor: grabbing;
            background: #E10600;
        }
        
        /* Número de posición - JETBRAINS MONO */
        .position-number {
            background-color: #E10600;
            color: #FFFFFF;
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            font-weight: 700;
            font-size: 14px;
            padding: 4px 10px;
            border-radius: 20px;
            min-width: 40px;
            text-align: center;
            margin-left: 12px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        
        .driver-name {
            flex: 1;
            font-weight: 600;
        }
        
        .reset-button {
            background-color: #E10600;
            color: white;
            border: none;
            border-radius: 20px;
            padding: 6px 16px;
            font-size: 12px;
            cursor: pointer;
            margin-bottom: 10px;
        }
        
        @media (max-width: 768px) {
            .grid-2cols {
                flex-direction: column;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # ============================================
    # TÍTULO DE LA CARRERA
    # ============================================
    
    if selected_race_name:
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
            <p><span class="round">ROUND {round_text}</span> · GRAN PREMIO</p>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================
    # PARRILA EN DOS COLUMNAS
    # ============================================
    
    st.markdown('<h3 style="color: #FFD700; margin-bottom: 1rem;">STARTING GRID</h3>', unsafe_allow_html=True)
    
    # Botón de reset
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("🔄 Resetear orden original", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Dividir pilotos
    mid = len(driver_abbrs) // 2
    left_drivers = driver_abbrs[:mid]
    right_drivers = driver_abbrs[mid:]
    
    # Función para crear lista con números visibles EN el elemento sortable
    def create_numbered_list(drivers, start_num=1):
        """Crea una lista de strings con formato '1. VER' para mostrar en sort_items"""
        return [f"{start_num + i}. {driver}" for i, driver in enumerate(drivers)]
    
    # Función para extraer solo el nombre después de ordenar
    def extract_names(numbered_list):
        return [item.split(". ", 1)[1] for item in numbered_list]
    
    # Crear dos columnas
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="grid-col"><h4>TOP 10</h4>', unsafe_allow_html=True)
        
        # Crear lista con números
        left_numbered = create_numbered_list(left_drivers, 1)
        
        # Mostrar lista ordenable con números visibles
        sorted_left_numbered = sort_items(left_numbered, direction="vertical")
        
        # Extraer nombres para usar después
        sorted_left = extract_names(sorted_left_numbered)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        st.markdown('<div class="grid-col"><h4>BOTTOM 10</h4>', unsafe_allow_html=True)
        
        # Crear lista con números (continúa desde 11)
        right_numbered = create_numbered_list(right_drivers, mid + 1)
        
        # Mostrar lista ordenable con números visibles
        sorted_right_numbered = sort_items(right_numbered, direction="vertical")
        
        # Extraer nombres para usar después
        sorted_right = extract_names(sorted_right_numbered)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Combinar resultados
    sorted_drivers = sorted_left + sorted_right
    
    # Mostrar resumen del orden actual
    with st.expander("📋 Ver orden completo de parrilla"):
        for i, driver in enumerate(sorted_drivers, 1):
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; 
                        background: #1A1A2E; padding: 8px 12px; margin-bottom: 5px; border-radius: 8px;">
                <span style="color: white; font-weight: 500;">{driver}</span>
                <span style="background-color: #E10600; font-family: 'JetBrains Mono', monospace; 
                             font-weight: bold; padding: 2px 10px; border-radius: 15px;">
                    {i}
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    return sorted_drivers

