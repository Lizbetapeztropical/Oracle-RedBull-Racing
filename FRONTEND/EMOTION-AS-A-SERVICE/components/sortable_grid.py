import streamlit as st

def show_sortable_grid(driver_abbrs, selected_race_name=None, round_number=None):
    """
    Muestra una parrilla ordenable en dos columnas (TOP 10 y BOTTOM 10)
    con números dinámicos, fuente JetBrains Mono y actualización automática
    """
    
    # ============================================
    # CSS PERSONALIZADO
    # ============================================
    
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;600;700;900&display=swap');
        
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
        
        /* Título de la sección */
        .grid-title {
            color: #FFD700;
            text-align: center;
            margin: 1rem 0;
            font-family: 'Titillium Web', sans-serif;
        }
        
        /* Contenedor de cada columna */
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
        
        /* Fila de cada posición */
        .position-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #1A1A2E;
            padding: 10px 15px;
            margin-bottom: 8px;
            border-radius: 10px;
            border-left: 4px solid #E10600;
            transition: all 0.2s ease;
        }
        
        .position-row:hover {
            transform: translateX(5px);
            border-left-color: #FFD700;
            background: #22223B;
        }
        
        /* Número de posición - JetBrains Mono */
        .position-number {
            background-color: #E10600;
            color: white;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            font-size: 14px;
            padding: 4px 12px;
            border-radius: 20px;
            min-width: 45px;
            text-align: center;
        }
        
        /* Nombre del piloto */
        .driver-name {
            font-family: 'Titillium Web', sans-serif;
            font-weight: 600;
            color: white;
            flex: 1;
            margin-left: 15px;
        }
        
        /* Ocultar etiquetas de los selectbox */
        .stSelectbox label {
            display: none;
        }
        
        /* Ajustar ancho de los selectbox */
        .stSelectbox div[data-baseweb="select"] {
            width: 100px;
        }
        
        /* Botón de reset */
        .reset-button-container {
            display: flex;
            justify-content: center;
            margin: 1rem 0;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .position-row {
                flex-wrap: wrap;
                gap: 8px;
            }
            .stSelectbox div[data-baseweb="select"] {
                width: 100%;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # ============================================
    # HEADER DE CARRERA
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
    
    st.markdown('<h2 class="grid-title">STARTING GRID</h2>', unsafe_allow_html=True)
    
    # ============================================
    # INICIALIZAR ORDEN EN SESSION STATE
    # ============================================
    
    if 'grid_order' not in st.session_state:
        st.session_state.grid_order = driver_abbrs.copy()
    
    # Botón de reset
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("🔄 Resetear orden original", use_container_width=True):
            st.session_state.grid_order = driver_abbrs.copy()
            st.rerun()
    
    # ============================================
    # PARRilla EN DOS COLUMNAS
    # ============================================
    
    mid = len(driver_abbrs) // 2
    
    col_left, col_right = st.columns(2)
    
    # ============================================
    # COLUMNA IZQUIERDA (TOP 10)
    # ============================================
    
    with col_left:
        st.markdown('<div class="grid-col"><h3>TOP 10</h3>', unsafe_allow_html=True)
        
        for i in range(mid):
            pos = i + 1
            current_driver = st.session_state.grid_order[i]
            
            # Usar columnas internas para alinear elementos
            inner_cols = st.columns([1, 3, 2])
            
            with inner_cols[0]:
                st.markdown(f'<div class="position-number">{pos}</div>', unsafe_allow_html=True)
            
            with inner_cols[1]:
                st.markdown(f'<span class="driver-name">{current_driver}</span>', unsafe_allow_html=True)
            
            with inner_cols[2]:
                # Selector para cambiar el piloto
                new_driver = st.selectbox(
                    "",
                    options=st.session_state.grid_order,
                    index=st.session_state.grid_order.index(current_driver),
                    key=f"pos_left_{pos}",
                    label_visibility="collapsed"
                )
            
            # Actualizar orden si cambió
            if new_driver != current_driver:
                old_index = st.session_state.grid_order.index(current_driver)
                new_index = st.session_state.grid_order.index(new_driver)
                st.session_state.grid_order[old_index], st.session_state.grid_order[new_index] = \
                st.session_state.grid_order[new_index], st.session_state.grid_order[old_index]
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================
    # COLUMNA DERECHA (BOTTOM 10)
    # ============================================
    
    with col_right:
        st.markdown('<div class="grid-col"><h3>BOTTOM 10</h3>', unsafe_allow_html=True)
        
        for i in range(mid, len(driver_abbrs)):
            pos = i + 1
            current_driver = st.session_state.grid_order[i]
            
            # Usar columnas internas para alinear elementos
            inner_cols = st.columns([1, 3, 2])
            
            with inner_cols[0]:
                st.markdown(f'<div class="position-number">{pos}</div>', unsafe_allow_html=True)
            
            with inner_cols[1]:
                st.markdown(f'<span class="driver-name">{current_driver}</span>', unsafe_allow_html=True)
            
            with inner_cols[2]:
                # Selector para cambiar el piloto
                new_driver = st.selectbox(
                    "",
                    options=st.session_state.grid_order,
                    index=st.session_state.grid_order.index(current_driver),
                    key=f"pos_right_{pos}",
                    label_visibility="collapsed"
                )
            
            # Actualizar orden si cambió
            if new_driver != current_driver:
                old_index = st.session_state.grid_order.index(current_driver)
                new_index = st.session_state.grid_order.index(new_driver)
                st.session_state.grid_order[old_index], st.session_state.grid_order[new_index] = \
                st.session_state.grid_order[new_index], st.session_state.grid_order[old_index]
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================
    # RESUMEN DEL ORDEN ACTUAL (EXPANDIBLE)
    # ============================================
    
    with st.expander("📋 Ver orden completo de parrilla"):
        for i, driver in enumerate(st.session_state.grid_order, 1):
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; 
                        background: #1A1A2E; padding: 6px 12px; margin-bottom: 4px; border-radius: 6px;">
                <span style="color: white; font-weight: 500; font-family: 'Titillium Web', sans-serif;">
                    {driver}
                </span>
                <span style="background-color: #E10600; font-family: 'JetBrains Mono', monospace; 
                            font-weight: bold; padding: 2px 10px; border-radius: 15px;">
                    {i}
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    return st.session_state.grid_order 
