import streamlit as st

def show_sortable_grid(driver_abbrs, selected_race_name=None, round_number=None):
    """
    Muestra una parrilla ordenable usando selectbox para cada posición
    con números visibles y JetBrains Mono
    """
    
    # CSS con JetBrains Mono
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');
        
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
        
        .position-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #1A1A2E;
            padding: 10px 15px;
            margin-bottom: 8px;
            border-radius: 10px;
            border-left: 4px solid #E10600;
        }
        
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
        
        .driver-name {
            font-family: 'Titillium Web', sans-serif;
            font-weight: 600;
            color: white;
            flex: 1;
            margin-left: 15px;
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
            if last_digit == 1: return "ST"
            elif last_digit == 2: return "ND"
            elif last_digit == 3: return "RD"
            else: return "TH"
        
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
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Resetear orden original", use_container_width=True):
            st.session_state.grid_order = driver_abbrs.copy()
            st.rerun()
    
    # ============================================
    # MOSTRAR PARRILLA ORDENABLE
    # ============================================
    
    # Crear dos columnas para TOP 10 y BOTTOM 10
    col_left, col_right = st.columns(2)
    
    mid = len(driver_abbrs) // 2
    
    with col_left:
        st.markdown("### TOP 10")
        for i in range(mid):
            pos = i + 1
            current_driver = st.session_state.grid_order[i]
            
            # Selector para cada posición
            new_driver = st.selectbox(
                f"Posición {pos}",
                options=st.session_state.grid_order,
                index=st.session_state.grid_order.index(current_driver),
                key=f"pos_{pos}",
                label_visibility="collapsed"
            )
            
            # Mostrar fila con número y piloto
            st.markdown(f"""
            <div class="position-row">
                <span class="position-number">{pos}</span>
                <span class="driver-name">{new_driver}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Actualizar orden si cambió
            if new_driver != current_driver:
                # Mover el piloto a la nueva posición
                old_index = st.session_state.grid_order.index(current_driver)
                new_index = st.session_state.grid_order.index(new_driver)
                st.session_state.grid_order[old_index], st.session_state.grid_order[new_index] = \
                st.session_state.grid_order[new_index], st.session_state.grid_order[old_index]
                st.rerun()
    
    with col_right:
        st.markdown("### BOTTOM 10")
        for i in range(mid, len(driver_abbrs)):
            pos = i + 1
            current_driver = st.session_state.grid_order[i]
            
            # Selector para cada posición
            new_driver = st.selectbox(
                f"Posición {pos}",
                options=st.session_state.grid_order,
                index=st.session_state.grid_order.index(current_driver),
                key=f"pos_{pos}",
                label_visibility="collapsed"
            )
            
            # Mostrar fila con número y piloto
            st.markdown(f"""
            <div class="position-row">
                <span class="position-number">{pos}</span>
                <span class="driver-name">{new_driver}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Actualizar orden si cambió
            if new_driver != current_driver:
                old_index = st.session_state.grid_order.index(current_driver)
                new_index = st.session_state.grid_order.index(new_driver)
                st.session_state.grid_order[old_index], st.session_state.grid_order[new_index] = \
                st.session_state.grid_order[new_index], st.session_state.grid_order[old_index]
                st.rerun()
    
    # ============================================
    # RESUMEN DEL ORDEN ACTUAL
    # ============================================
    
    with st.expander("📋 Ver orden completo de parrilla"):
        for i, driver in enumerate(st.session_state.grid_order, 1):
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; 
                        background: #1A1A2E; padding: 6px 12px; margin-bottom: 4px; border-radius: 6px;">
                <span style="color: white;">{driver}</span>
                <span style="background-color: #E10600; font-family: 'JetBrains Mono', monospace; 
                             padding: 2px 10px; border-radius: 15px;">{i}</span>
            </div>
            """, unsafe_allow_html=True)
    
    return st.session_state.grid_order

