# =============================================================================
# MAPA DE CALOR POR SENTIMIENTO - F1 Pulse
# =============================================================================

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from textblob import TextBlob
import numpy as np

print("🗺️ Generando mapa de sentimiento por país...")

# =============================================================================
# 1. CARGAR DATOS
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
file_path = BASE_DIR / "BACKEND" / "EMOTION-AS-A-SERVICE" / "model" / "DATA" / "Tweets" / "tweets_cleaned.csv"

print(f"📥 Cargando: {file_path.name}")

df = pd.read_csv(file_path, low_memory=False)
print(f"✅ {len(df):,} tweets cargados")

# =============================================================================
# 2. FILTRAR Y PREPARAR DATOS
# =============================================================================

# Usar columna normalizada de países
if 'user_location_normalized' not in df.columns:
    print("❌ No se encuentra 'user_location_normalized'")
    print("Ejecuta primero dataprep2.py con normalización")
    exit()

# Filtrar países válidos (excluir Unknown, Other)
df_countries = df[~df['user_location_normalized'].isin(['Unknown', 'Other', 'unknown'])]
df_countries = df_countries.dropna(subset=['user_location_normalized'])

print(f"📍 Países válidos: {df_countries['user_location_normalized'].nunique()}")

# =============================================================================
# 3. FUNCIÓN DE SENTIMIENTO (usando TextBlob)
# =============================================================================

def get_sentiment(text):
    """Retorna sentimiento: positivo, neutral, negativo"""
    if not isinstance(text, str) or len(text.strip()) == 0:
        return "neutral"
    
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return "positive"
        elif polarity < -0.1:
            return "negative"
        else:
            return "neutral"
    except:
        return "neutral"

print("🧠 Analizando sentimientos...")

# Aplicar sentimiento (solo a una muestra si es muy grande)
if len(df_countries) > 100000:
    df_sample = df_countries.sample(100000, random_state=42)
    print(f"⚡ Usando muestra de {len(df_sample):,} tweets")
else:
    df_sample = df_countries

df_sample['sentiment'] = df_sample['clean_text'].apply(get_sentiment)

# =============================================================================
# 4. AGREGAR POR PAÍS Y SENTIMIENTO
# =============================================================================

# Conteo por país
country_counts = df_sample.groupby('user_location_normalized').size().reset_index(name='total_tweets')

# Conteo por sentimiento
sentiment_by_country = df_sample.groupby(['user_location_normalized', 'sentiment']).size().unstack(fill_value=0)

# Calcular sentimiento dominante
sentiment_by_country['dominant'] = sentiment_by_country.idxmax(axis=1)
sentiment_by_country['dominant_count'] = sentiment_by_country.max(axis=1)
sentiment_by_country['total'] = sentiment_by_country.sum(axis=1)

# Unir con total de tweets
sentiment_by_country = sentiment_by_country.reset_index()
sentiment_by_country = sentiment_by_country.merge(country_counts, on='user_location_normalized')

# Calcular porcentajes
for sentiment in ['positive', 'neutral', 'negative']:
    if sentiment in sentiment_by_country.columns:
        sentiment_by_country[f'{sentiment}_pct'] = (
            sentiment_by_country[sentiment] / sentiment_by_country['total'] * 100
        ).round(1)

# =============================================================================
# 5. COORDENADAS DE PAÍSES (para el mapa)
# =============================================================================

# Diccionario de coordenadas aproximadas de países
country_coords = {
    'United Kingdom': {'lat': 51.5074, 'lon': -0.1278},
    'United States': {'lat': 37.0902, 'lon': -95.7129},
    'Italy': {'lat': 41.8719, 'lon': 12.5674},
    'France': {'lat': 46.2276, 'lon': 2.2137},
    'Spain': {'lat': 40.4637, 'lon': -3.7492},
    'Germany': {'lat': 51.1657, 'lon': 10.4515},
    'India': {'lat': 20.5937, 'lon': 78.9629},
    'Australia': {'lat': -25.2744, 'lon': 133.7751},
    'Canada': {'lat': 56.1304, 'lon': -106.3468},
    'Brazil': {'lat': -14.2350, 'lon': -51.9253},
    'Netherlands': {'lat': 52.1326, 'lon': 5.2913},
    'Mexico': {'lat': 23.6345, 'lon': -102.5528},
    'Japan': {'lat': 36.2048, 'lon': 138.2529},
    'South Africa': {'lat': -30.5595, 'lon': 22.9375},
    'Ireland': {'lat': 53.1424, 'lon': -7.6921},
    'Monaco': {'lat': 43.7384, 'lon': 7.4246},
    'Belgium': {'lat': 50.8503, 'lon': 4.3517},
    'Portugal': {'lat': 39.3999, 'lon': -8.2245},
    'Switzerland': {'lat': 46.8182, 'lon': 8.2275},
    'Austria': {'lat': 47.5162, 'lon': 14.5501},
    'Sweden': {'lat': 60.1282, 'lon': 18.6435},
    'Denmark': {'lat': 56.2639, 'lon': 9.5018},
    'Norway': {'lat': 60.4720, 'lon': 8.4689},
    'Finland': {'lat': 61.9241, 'lon': 25.7482},
    'Poland': {'lat': 51.9194, 'lon': 19.1451},
    'Greece': {'lat': 39.0742, 'lon': 21.8243},
    'Turkey': {'lat': 38.9637, 'lon': 35.2433},
    'Russia': {'lat': 61.5240, 'lon': 105.3188},
    'China': {'lat': 35.8617, 'lon': 104.1954},
    'South Korea': {'lat': 35.9078, 'lon': 127.7669},
    'Singapore': {'lat': 1.3521, 'lon': 103.8198},
    'Malaysia': {'lat': 4.2105, 'lon': 101.9758},
    'Indonesia': {'lat': -0.7893, 'lon': 113.9213},
    'Philippines': {'lat': 12.8797, 'lon': 121.7740},
    'Thailand': {'lat': 15.8700, 'lon': 100.9925},
    'Vietnam': {'lat': 14.0583, 'lon': 108.2772},
    'Egypt': {'lat': 26.8206, 'lon': 30.8025},
    'Nigeria': {'lat': 9.0820, 'lon': 8.6753},
    'Kenya': {'lat': -1.2864, 'lon': 36.8172},
    'Argentina': {'lat': -38.4161, 'lon': -63.6167},
    'Chile': {'lat': -35.6751, 'lon': -71.5430},
    'Colombia': {'lat': 4.5709, 'lon': -74.2973},
    'Peru': {'lat': -9.1900, 'lon': -75.0152},
    'UAE': {'lat': 23.4241, 'lon': 53.8478},
    'Qatar': {'lat': 25.3548, 'lon': 51.1839},
    'Bahrain': {'lat': 26.0667, 'lon': 50.5577},
}

# Agregar coordenadas al dataframe
sentiment_by_country['lat'] = sentiment_by_country['user_location_normalized'].map(
    lambda x: country_coords.get(x, {}).get('lat', 0)
)
sentiment_by_country['lon'] = sentiment_by_country['user_location_normalized'].map(
    lambda x: country_coords.get(x, {}).get('lon', 0)
)

# Filtrar países con coordenadas
df_map = sentiment_by_country[sentiment_by_country['lat'] != 0].copy()

# =============================================================================
# 6. COLOR SEGÚN SENTIMIENTO DOMINANTE
# =============================================================================

sentiment_colors = {
    'positive': '#2ecc71',  # Verde
    'neutral': '#f39c12',   # Naranja
    'negative': '#e74c3c'   # Rojo
}

df_map['color'] = df_map['dominant'].map(sentiment_colors)
df_map['size'] = np.log1p(df_map['total_tweets']) * 15  # Tamaño proporcional al log de tweets

# =============================================================================
# 7. CREAR MAPA INTERACTIVO
# =============================================================================

fig = go.Figure()

# Capa de mapa base
fig.add_trace(go.Scattergeo(
    lon=df_map['lon'],
    lat=df_map['lat'],
    text=df_map['user_location_normalized'],
    mode='markers',
    marker=dict(
        size=df_map['size'],
        color=df_map['color'],
        opacity=0.7,
        line=dict(width=1, color='white'),
        sizemode='area',
        sizeref=2.*max(df_map['size'])/(40**2),
        sizemin=4
    ),
    hovertemplate='<b>%{text}</b><br>' +
                  'Total tweets: %{customdata[0]:,}<br>' +
                  'Sentimiento dominante: %{customdata[1]}<br>' +
                  '😊 Positivo: %{customdata[2]}%<br>' +
                  '😐 Neutral: %{customdata[3]}%<br>' +
                  '😞 Negativo: %{customdata[4]}%<br>' +
                  '<extra></extra>',
    customdata=df_map[['total_tweets', 'dominant', 'positive_pct', 'neutral_pct', 'negative_pct']].values
))

# Configurar diseño del mapa
fig.update_layout(
    title=dict(
        text='🌍 Distribución de Sentimiento por País',
        x=0.5,
        font=dict(size=24, family='Arial', color='#333')
    ),
    geo=dict(
        projection_type='natural earth',
        showland=True,
        landcolor='rgb(243, 243, 243)',
        coastlinecolor='rgb(204, 204, 204)',
        showocean=True,
        oceancolor='rgb(230, 245, 255)',
        showcountries=True,
        countrycolor='rgb(204, 204, 204)',
        showframe=False
    ),
    height=600,
    margin=dict(l=0, r=0, t=50, b=0),
    legend=dict(
        title='Sentimiento',
        x=0.02, y=0.98,
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor='#ddd',
        borderwidth=1
    )
)

# Agregar leyenda manual de colores
for sentiment, color in sentiment_colors.items():
    fig.add_trace(go.Scattergeo(
        lon=[None], lat=[None],
        mode='markers',
        marker=dict(size=10, color=color),
        name=sentiment.capitalize(),
        showlegend=True
    ))

# =============================================================================
# 8. TOP PAÍSES POR SENTIMIENTO (tabla adicional)
# =============================================================================

print("\n📊 TOP PAÍSES POR SENTIMIENTO:")
print("-" * 50)

for sentiment in ['positive', 'neutral', 'negative']:
    top = df_map.nlargest(5, f'{sentiment}_pct')[['user_location_normalized', f'{sentiment}_pct', 'total_tweets']]
    print(f"\n{sentiment.upper()}:")
    for _, row in top.iterrows():
        print(f"   {row['user_location_normalized']:20} {row[f'{sentiment}_pct']:.1f}% ({row['total_tweets']:,} tweets)")

# =============================================================================
# 9. GUARDAR Y MOSTRAR
# =============================================================================

output_path = BASE_DIR / "FRONTEND" / "EMOTION-AS-A-SERVICE" / "Pulse_page" / "sentiment_map.html"
fig.write_html(output_path)
print(f"\n✅ Mapa guardado: {output_path}")

# También guardar los datos procesados
data_path = Path(__file__).parent / "country_sentiment_data.csv"
df_map.to_csv(data_path, index=False)
print(f"✅ Datos guardados: {data_path}")

# Mostrar mapa
fig.show(config={'displayModeBar': True})

print("\n🎉 Mapa de sentimiento generado correctamente!")