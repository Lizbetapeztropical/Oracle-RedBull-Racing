# -*- coding: utf-8 -*-
"""tweets_por_dia"""

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

# ============================= CONFIGURACIÓN =============================

def get_data():
    """Carga los datos de tweets_cleaned.csv"""
    
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    file_path = BASE_DIR / "BACKEND" / "EMOTION-AS-A-SERVICE" / "model" / "DATA" / "Tweets" / "tweets_cleaned.csv"
    
    print(f"📥 Cargando: {file_path.name}")
    
    df = pd.read_csv(file_path, low_memory=False)
    print(f"✅ {len(df):,} tweets cargados")
    
    return df

def plot_combined_daily_metrics(df_to_plot, year=2021):
    """
    Genera gráfica combinada de Tweets y Usuarios Únicos por día
    
    Args:
        df_to_plot (pd.DataFrame): DataFrame con los datos
        year (int): Año a filtrar (default: 2021)
    
    Returns:
        plotly.graph_objects.Figure: Figura con la gráfica
    """
    
    # Filtrar por año
    df_filtered = df_to_plot[df_to_plot['year'] == float(year)].copy()
    
    if df_filtered.empty:
        print(f"⚠️ No hay datos para el año {year}")
        return None
    
    # Asegurar que la columna 'date' está en formato datetime
    df_filtered['date'] = pd.to_datetime(df_filtered['date'])
    
    # Extraer solo la parte de la fecha
    df_filtered['tweet_date'] = df_filtered['date'].dt.date
    
    # --- Calcular Tweets por día ---
    tweet_counts = df_filtered['tweet_date'].value_counts().reset_index()
    tweet_counts.columns = ['date', 'tweet_count']
    tweet_counts['date'] = pd.to_datetime(tweet_counts['date'], errors='coerce')
    tweet_counts = tweet_counts.sort_values('date', ascending=True)
    
    # --- Calcular Usuarios Únicos por día ---
    user_counts = df_filtered.groupby('tweet_date')['user_name'].nunique().reset_index()
    user_counts.columns = ['date', 'unique_users']
    user_counts['date'] = pd.to_datetime(user_counts['date'], errors='coerce')
    user_counts = user_counts.sort_values('date', ascending=True)
    
    # --- Crear la figura ---
    fig = go.Figure()
    
    # Añadir Tweets por día
    fig.add_trace(go.Scatter(
        x=tweet_counts['date'],
        y=tweet_counts['tweet_count'],
        mode='lines+markers',
        name='Tweets por día',
        marker_color='dodgerblue',
        line=dict(width=2)
    ))
    
    # Añadir Usuarios Únicos por día
    fig.add_trace(go.Scatter(
        x=user_counts['date'],
        y=user_counts['unique_users'],
        mode='lines+markers',
        name='Usuarios únicos por día',
        marker_color='#e74c3c',
        line=dict(width=2, color='#e74c3c')
    ))
    
    # Rango de fechas para el título
    min_date = df_filtered['tweet_date'].min().strftime("%d/%m/%Y")
    max_date = df_filtered['tweet_date'].max().strftime("%d/%m/%Y")
    
    # Configurar diseño
    fig.update_layout(
        title=dict(
            text=f'📊 Tweets y Usuarios Únicos por Día ({year})<br><sub>{min_date} - {max_date}</sub>',
            x=0.5,
            font=dict(size=18)
        ),
        template="plotly_white",
        xaxis_title="Fecha",
        yaxis_title="Cantidad",
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#ddd',
            borderwidth=1
        ),
        hovermode='x unified',
        width=900,
        height=500,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def plot_tweets_per_day(df_to_plot, year=2021):
    """Genera gráfica solo de tweets por día"""
    
    df_filtered = df_to_plot[df_to_plot['year'] == float(year)].copy()
    
    if df_filtered.empty:
        print(f"⚠️ No hay datos para el año {year}")
        return None
    
    df_filtered['date'] = pd.to_datetime(df_filtered['date'])
    df_filtered['tweet_date'] = df_filtered['date'].dt.date
    
    tweet_counts = df_filtered['tweet_date'].value_counts().reset_index()
    tweet_counts.columns = ['date', 'count']
    tweet_counts['date'] = pd.to_datetime(tweet_counts['date'], errors='coerce')
    tweet_counts = tweet_counts.sort_values('date', ascending=True)
    
    min_date = df_filtered['tweet_date'].min().strftime("%d/%m/%Y")
    max_date = df_filtered['tweet_date'].max().strftime("%d/%m/%Y")
    
    fig = go.Figure(go.Scatter(
        x=tweet_counts['date'],
        y=tweet_counts['count'],
        mode='lines+markers',
        name='Tweets',
        marker_color='dodgerblue',
        line=dict(width=2)
    ))
    
    fig.update_layout(
        title=dict(
            text=f'📊 Tweets por Día ({year})<br><sub>{min_date} - {max_date}</sub>',
            x=0.5,
            font=dict(size=18)
        ),
        template="plotly_white",
        xaxis_title="Fecha",
        yaxis_title="Número de Tweets",
        hovermode='x unified',
        width=900,
        height=500,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def plot_users_per_day(df_to_plot, year=2021):
    """Genera gráfica solo de usuarios únicos por día"""
    
    df_filtered = df_to_plot[df_to_plot['year'] == float(year)].copy()
    
    if df_filtered.empty:
        print(f"⚠️ No hay datos para el año {year}")
        return None
    
    df_filtered['date'] = pd.to_datetime(df_filtered['date'])
    df_filtered['tweet_date'] = df_filtered['date'].dt.date
    
    user_counts = df_filtered.groupby('tweet_date')['user_name'].nunique().reset_index()
    user_counts.columns = ['date', 'unique_users']
    user_counts['date'] = pd.to_datetime(user_counts['date'], errors='coerce')
    user_counts = user_counts.sort_values('date', ascending=True)
    
    min_date = df_filtered['tweet_date'].min().strftime("%d/%m/%Y")
    max_date = df_filtered['tweet_date'].max().strftime("%d/%m/%Y")
    
    fig = go.Figure(go.Scatter(
        x=user_counts['date'],
        y=user_counts['unique_users'],
        mode='lines+markers',
        name='Usuarios Únicos',
        marker_color='#2ecc71',
        line=dict(width=2, color='#2ecc71')
    ))
    
    fig.update_layout(
        title=dict(
            text=f'📊 Usuarios Únicos por Día ({year})<br><sub>{min_date} - {max_date}</sub>',
            x=0.5,
            font=dict(size=18)
        ),
        template="plotly_white",
        xaxis_title="Fecha",
        yaxis_title="Número de Usuarios Únicos",
        hovermode='x unified',
        width=900,
        height=500,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

# ============================= EJECUCIÓN DIRECTA =============================
if __name__ == "__main__":
    # Cargar datos
    df = get_data()
    
    # Generar gráfica combinada
    fig_combinada = plot_combined_daily_metrics(df, year=2021)
    if fig_combinada:
        fig_combinada.show(config={'displayModeBar': True})
        print("✅ Gráfica combinada generada correctamente")
    
    # También puedes generar gráficas individuales:
    # fig_tweets = plot_tweets_per_day(df, year=2021)
    # fig_tweets.show()
    
    # fig_users = plot_users_per_day(df, year=2021)
    # fig_users.show()