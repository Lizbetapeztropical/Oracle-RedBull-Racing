# =============================================================================
# FUNCIONES PARA KPI DE SENTIMIENTOS (Semáforo Interactivo)
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
    """Retorna figura del semáforo de sentimientos estilizado con Hover effect"""
    
    # Cargar datos
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    file_path = BASE_DIR / "BACKEND" / "EMOTION-AS-A-SERVICE" / "model" / "DATA" / "Tweets" / "tweets_cleaned.csv"
    
    df = pd.read_csv(file_path, low_memory=False)
    
    positivo, negativo, neutral = analizar_sentimientos(df)
    
    # Configuraciones estéticas
    positions = [1, 2, 3]  # Espaciado lineal perfecto
    colors = ["#ef4444", "#f1c40f", "#2ecc71"]  # Colores más vivos y modernos
    labels = ["Negativo", "Neutral", "Positivo"]
    counts = [negativo, neutral, positivo]
    
    # Crear textos personalizados para el Hover flotante
    hover_texts = [f"<b>{label}</b><br>Total: {count:,}" for label, count in zip(labels, counts)]
    
    # Crear figura base
    fig = go.Figure()
    
    # Dibujar las esferas usando un Scatter interactivo
    fig.add_trace(go.Scatter(
        x=positions,
        y=[1, 1, 1],  # Alineación perfecta en el eje Y
        mode="markers+text",
        text=labels,
        textposition="top center",
        textfont=dict(size=14, color="#333333", font="Arial Black"),
        hoverinfo="text",
        hovertext=hover_texts,
        marker=dict(
            size=65,  # Círculos perfectamente simétricos
            color=colors,
            line=dict(color="white", width=3),
            opacity=0.9
        )
    ))
    
    # Título del componente estilizado
    fig.update_layout(
        title=dict(
            text="Índice de Sentimientos",
            x=0.5, y=0.88,
            xanchor="center",
            font=dict(size=20, color="#1e293b", family="Arial")
        ),
        width=380, height=220,
        paper_bgcolor="white", plot_bgcolor="white",
        margin=dict(l=10, r=10, t=50, b=10),
        
        # Ocultar completamente ejes y rejillas de fondo
        xaxis=dict(visible=False, range=[0.4, 3.6]),
        yaxis=dict(visible=False, range=[0.6, 1.4]),
        showlegend=False,
        
        # Diseño premium del cuadro flotante (Hover)
        hoverlabel=dict(
            bgcolor="#1e293b",
            font_size=13,
            font_color="white",
            font_family="Arial",
            bordercolor="white"
        )
    )
    
    return fig


# ============================= EJECUCIÓN DIRECTA =============================
if __name__ == "__main__":
    fig = create_sentiment_semaforo()
    fig.show(config={'displayModeBar': False})
    print("✅ Gráfica de Sentimientos generada correctamente")