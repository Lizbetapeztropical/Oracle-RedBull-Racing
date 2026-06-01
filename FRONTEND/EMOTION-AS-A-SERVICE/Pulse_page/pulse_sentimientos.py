# =============================================================================
# FUNCIONES PARA KPI DE SENTIMIENTOS (Semáforo)
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
    """Retorna figura del semáforo de sentimientos"""
    
    # Cargar datos
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    file_path = BASE_DIR / "BACKEND" / "EMOTION-AS-A-SERVICE" / "model" / "DATA" / "Tweets" / "tweets_cleaned.csv"
    
    df = pd.read_csv(file_path, low_memory=False)
    
    positivo, negativo, neutral = analizar_sentimientos(df)
    
    # Crear figura
    fig = go.Figure()
    
    fig.add_annotation(
        text="Índice de Sentimientos",
        x=0.5, y=0.92, xref="paper", yref="paper",
        showarrow=False, font=dict(size=18, color="black"), align="center"
    )
    
    positions = [0.25, 0.5, 0.75]
    colors = ["#ef4444", "#eab308", "#22c55e"]
    labels = ["Negativo", "Neutral", "Positivo"]
    counts = [negativo, neutral, positivo]
    
    for x, color, label, count in zip(positions, colors, labels, counts):
        fig.add_shape(
            type="circle",
            xref="paper", yref="paper",
            x0=x-0.09, y0=0.42, x1=x+0.09, y1=0.68,
            fillcolor=color,
            line=dict(color="white", width=4)
        )
        fig.add_annotation(
            text=label,
            x=x, y=0.78,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=12, color="black"),
            align="center"
        )
        fig.add_annotation(
            text=f"{count:,}",
            x=x, y=0.32,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=13, color=color),
            align="center"
        )
    
    fig.update_layout(
        width=380, height=220,
        paper_bgcolor="white", plot_bgcolor="white",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False
    )
    
    return fig


# ============================= EJECUCIÓN DIRECTA =============================
if __name__ == "__main__":
    fig = create_sentiment_semaforo()
    fig.show(config={'displayModeBar': False})
    print("✅ Gráfica de Sentimientos generada correctamente")