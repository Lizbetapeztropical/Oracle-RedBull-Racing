# -*- coding: utf-8 -*-
"""Top 10 Países - F1 Pulse"""

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

def create_top_countries():
    """Genera gráfica de Top 10 países con más tweets (gama de rojos)"""
    
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    file_path = BASE_DIR / "BACKEND" / "EMOTION-AS-A-SERVICE" / "model" / "DATA" / "Tweets" / "tweets_cleaned.csv"
    
    df = pd.read_csv(file_path, low_memory=False)
    print(f"✅ {len(df):,} tweets cargados")
    
    # Usar columna normalizada, excluir Unknown
    if 'user_location_normalized' in df.columns:
        country_col = 'user_location_normalized'
    else:
        country_col = 'user_location'
    
    top_countries = df[df[country_col] != 'Unknown'][country_col].value_counts().head(10).reset_index()
    top_countries.columns = ['País', 'Tweets']
    
    # Formatear números (ej: 68.7K)
    top_countries['Tweets_fmt'] = top_countries['Tweets'].apply(lambda x: f"{x/1000:.1f}K" if x >= 1000 else str(x))
    
    # Gama de rojos (del más claro al más oscuro)
    reds = ['#FF6B6B', '#E74C3C', '#C0392B', '#A93226', '#922B21', '#7B241C', '#641E16', '#4A0E0A']
    
    # Gráfica con colores rojos
    fig = go.Figure(go.Bar(
        x=top_countries['Tweets'],
        y=top_countries['País'],
        orientation='h',
        marker_color=reds[:len(top_countries)],
        text=top_countries['Tweets_fmt'],
        textposition='outside',
        textfont=dict(color='#8B0000', size=12)
    ))
    
    fig.update_layout(
        title=dict(
            text="📊 TOP 10 PAÍSES POR NÚMERO DE TWEETS",
            font=dict(color='#8B0000', size=18)
        ),
        xaxis_title=dict(text="Número de Tweets", font=dict(color='#C0392B')),
        yaxis_title=dict(text="País", font=dict(color='#C0392B')),
        height=500,
        width=700,
        yaxis=dict(categoryorder='total ascending'),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Cambiar color de las barras al pasar el mouse
    fig.update_traces(marker=dict(line=dict(width=0)))
    
    return fig

if __name__ == "__main__":
    fig = create_top_countries()
    fig.show(config={'displayModeBar': True})
    print("✅ Top 10 países generado (gama de rojos)")