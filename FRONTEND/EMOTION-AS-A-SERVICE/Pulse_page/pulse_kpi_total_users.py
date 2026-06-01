# -*- coding: utf-8 -*-
"""usuarios_totales"""

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

# ============================= CONFIGURACIÓN =============================

def get_total_users():
    """Retorna el número total de usuarios únicos"""
    
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    file_path = BASE_DIR / "BACKEND" / "EMOTION-AS-A-SERVICE" / "model" / "DATA" / "Tweets" / "tweets_cleaned.csv"
    
    print(f"📥 Cargando: {file_path.name}")
    
    df = pd.read_csv(file_path, low_memory=False)
    total_unique_users = df['user_name'].nunique()
    
    print(f"✅ {total_unique_users:,} usuarios únicos cargados")
    return total_unique_users

def display_total_users():
    """Muestra el total de usuarios únicos en formato KPI card"""
    
    total = get_total_users()
    
    # Formato abreviado (ej: 86.7K, 512.3K, etc.)
    if total >= 1_000_000:
        total_fmt = f"{total/1_000_000:.1f}M"
    elif total >= 1_000:
        total_fmt = f"{total/1_000:.1f}K"
    else:
        total_fmt = str(total)
    
    # Crear figura KPI card
    fig = go.Figure()
    
    # Texto pequeño arriba
    fig.add_annotation(
        text="Total Users",
        x=0.05,
        y=0.78,
        xref="paper",
        yref="paper",
        showarrow=False,
        align="left",
        font=dict(size=20, color="black")
    )
    
    # Número grande
    fig.add_annotation(
        text=f"<b>{total_fmt}</b>",
        x=0.05,
        y=0.35,
        xref="paper",
        yref="paper",
        showarrow=False,
        align="left",
        font=dict(size=42, color="black")
    )
    
    fig.update_layout(
        width=320,
        height=170,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        shapes=[
            dict(
                type="rect",
                x0=0, y0=0, x1=1, y1=1,
                xref="paper", yref="paper",
                line=dict(color="#DDDDDD", width=1),
                fillcolor="white"
            )
        ]
    )
    
    return fig, total

# ============================= EJECUCIÓN DIRECTA =============================
if __name__ == "__main__":
    fig, total = display_total_users()
    fig.show(config={'displayModeBar': False})
    print(f"✅ Total unique users: {total:,}")
    print("✅ Gráfica generada correctamente")