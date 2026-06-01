# =============================================================================
# FUNCIONES PARA KPI DE SENTIMIENTOS (Semáforo Premium Interactivo)
# =============================================================================

import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

def analizar_sentimientos(df):
    """Analiza sentimientos y retorna conteos"""
    text_column = 'clean_text' if 'clean_text' in df.columns else 'text'
    textos = df[text_column].astype(str).str.lower()
    
    positive_words = ['win','victory','great','amazing','love','best','good','happy','excellent','fantastic','champion','podium','proud']
    negative_words = ['crash','bad','terrible','hate','worst','sad','angry','disaster','lose','failure','broken','disappoint']
    
    pos = neg = neu = 0
    for texto in textos:
        p = sum(1 for word in positive_words if word in texto)
        n = sum(1 for word in negative_words if word in texto)
        if p > n:
            pos += 1
        elif n > p:
            neg += 1
        else:
            neu += 1
    return pos, neg, neu


def create_sentiment_semaforo():
    """Retorna figura del semáforo de sentimientos ultra-estético con Hover interactivo"""
    
    # Cargar datos
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    file_path = BASE_DIR / "BACKEND" / "EMOTION-AS-A-SERVICE" / "model" / "DATA" / "Tweets" / "tweets_cleaned.csv"
    
    df = pd.read_csv(file_path, low_memory=False)
    
    positivo, negativo, neutral = analizar_sentimientos(df)
    
    # Configuraciones estéticas de alta fidelidad
    positions = [1, 2, 3]  
    colors = ["#EF4444", "#F59E0B", "#10B981"]  # Paleta moderna (Tailwind: Red, Amber, Emerald)
    labels = ["Negativo", "Neutral", "Positivo"]
    counts = [negativo, neutral, positivo]
    
    # Diseño HTML estilizado exclusivo para el Tooltip flotante (Hover)
    hover_templates = [
        f"<b>{label.upper()}</b><br>"
        f"<span style='font-size:15px; font-weight:bold;'>{count:,} tweets</span>"
        f"<extra></extra>"  # Oculta la etiqueta secundaria fea de Plotly
        for label, count in zip(labels, counts)
    ]
    
    fig = go.Figure()
    
    # 1. Dibujar las esferas del semáforo (ÚNICAMENTE interactivas)
    fig.add_trace(go.Scatter(
        x=positions,
        y=[1.1, 1.1, 1.1],  # Subimos un poco el centro para equilibrar el espacio
        mode="markers",
        hovertemplate=hover_templates,
        marker=dict(
            size=75,  # Esferas más grandes e imponentes
            color=colors,
            line=dict(color="#FFFFFF", width=4),  # Borde grueso que da efecto de relieve
            opacity=1.0
        )
    ))
    
    # 2. Agregar los textos fijos de clasificación de forma elegante
    for x, label in zip(positions, labels):
        fig.add_annotation(
            x=x, y=0.65,  # Posición fija debajo de cada círculo
            text=f"<b>{label}</b>",
            showarrow=False,
            font=dict(size=14, color="#64748B", family="Arial Black"),  # Gris pizarra elegante
            align="center"
        )
    
    # Configuración de Layout Estilo Dashboard Premium
    fig.update_layout(
        title=dict(
            text="Índice de Sentimientos en Twitter",
            x=0.5, y=0.92,
            xanchor="center",
            font=dict(size=18, color="#0F172A", family="Arial", weight="bold")
        ),
        width=400, height=220,
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=45, b=25),
        
        # Limpieza absoluta de rejillas de fondo
        xaxis=dict(visible=False, range=[0.3, 3.7]),
        yaxis=dict(visible=False, range=[0.3, 1.7]),
        showlegend=False,
        
        # Efecto Card de Cristal para el cuadro flotante
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="#1E293B",  # Fondo oscuro elegante
            font_size=13,
            font_color="#FFFFFF",
            font_family="Arial",
            bordercolor="#475569"
        )
    )
    
    return fig


# ============================= EJECUCIÓN DIRECTA =============================
if __name__ == "__main__":
    fig = create_sentiment_semaforo()
    fig.show(config={'displayModeBar': False})
    print("✅ Gráfica de Sentimientos generada correctamente")