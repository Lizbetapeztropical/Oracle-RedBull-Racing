# =============================================================================
# MAPA DE EMOCIONES F1 - 25 PAÍSES CON TOOLTIP COMPLETO
# =============================================================================

import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import numpy as np

print("🗺️ Generando mapa de emociones - 25 países con tooltip completo...")

# =============================================================================
# 1. CARGAR DATOS
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Cargar resumen de países (25 países)
countries_path = BASE_DIR / "BACKEND" / "EMOTION-AS-A-SERVICE" / "model" / "DATA" / "Tweets" / "country_emotions_enhanced.csv"

# Cargar tweets con emociones (para porcentajes)
tweets_path = BASE_DIR / "BACKEND" / "EMOTION-AS-A-SERVICE" / "model" / "DATA" / "Tweets" / "tweets_with_emotions.csv"

if not countries_path.exists():
    print(f"❌ No se encuentra: {countries_path}")
    exit()

if not tweets_path.exists():
    print(f"❌ No se encuentra: {tweets_path}")
    exit()

print(f"📥 Cargando países: {countries_path.name}")
df_countries = pd.read_csv(countries_path)
print(f"✅ {len(df_countries)} países en el dataset")

print(f"📥 Cargando tweets con emociones: {tweets_path.name}")
df_tweets = pd.read_csv(tweets_path, low_memory=False)
print(f"✅ {len(df_tweets):,} tweets con emociones cargados")

# =============================================================================
# 2. FILTRAR TWEETS SOLO DE LOS 25 PAÍSES
# =============================================================================

paises_25 = df_countries['country'].unique().tolist()
print(f"\n📊 Filtrando tweets solo para los {len(paises_25)} países...")

df_tweets_filtrado = df_tweets[df_tweets['country'].isin(paises_25)]
print(f"✅ {len(df_tweets_filtrado):,} tweets de los {len(paises_25)} países")

# =============================================================================
# 3. CALCULAR PORCENTAJES DE EMOCIONES POR PAÍS
# =============================================================================

print("\n🧮 Calculando porcentajes de emociones por país...")

# Lista de emociones
emotion_list = ['joy', 'neutral', 'anger', 'trust', 'sadness', 'anticipation', 'surprise', 'fear']

# Diccionario para almacenar resultados
country_emotions_data = {}

for country in paises_25:
    # Filtrar tweets de este país
    country_tweets = df_tweets_filtrado[df_tweets_filtrado['country'] == country]
    
    if len(country_tweets) == 0:
        # Si no hay tweets, usar datos del resumen
        country_row = df_countries[df_countries['country'] == country].iloc[0]
        total_tweets = country_row['tweets']
        dominant_emotion = country_row['emotion']
        
        # Porcentajes aproximados (basados en la emoción dominante)
        percentages = {e: 0 for e in emotion_list}
        percentages[dominant_emotion] = 100
    else:
        total_tweets = len(country_tweets)
        
        # Contar emociones
        emotion_counts = country_tweets['emotion'].value_counts().to_dict()
        
        # Calcular porcentajes
        percentages = {}
        for emotion in emotion_list:
            count = emotion_counts.get(emotion, 0)
            pct = (count / total_tweets * 100) if total_tweets > 0 else 0
            percentages[emotion] = round(pct, 1)
    
    # Ordenar porcentajes de mayor a menor
    sorted_emotions = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
    
    country_emotions_data[country] = {
        'total_tweets': total_tweets,
        'dominant': sorted_emotions[0][0] if sorted_emotions else 'neutral',
        'dominant_pct': sorted_emotions[0][1] if sorted_emotions else 0,
        'percentages': dict(sorted_emotions)
    }
    
    print(f"   {country:20} → {country_emotions_data[country]['dominant']}: {country_emotions_data[country]['dominant_pct']:.0f}% ({total_tweets:,} tweets)")

# =============================================================================
# 4. DICCIONARIO DE COORDENADAS (25+ PAÍSES)
# =============================================================================

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
    'Argentina': {'lat': -38.4161, 'lon': -63.6167},
    'Nigeria': {'lat': 9.0820, 'lon': 8.6753},
    'Kenya': {'lat': -1.2864, 'lon': 36.8172},
    'Egypt': {'lat': 26.8206, 'lon': 30.8025},
    'UAE': {'lat': 23.4241, 'lon': 53.8478},
    'Saudi Arabia': {'lat': 23.8859, 'lon': 45.0792},
    'Singapore': {'lat': 1.3521, 'lon': 103.8198},
    'Malaysia': {'lat': 4.2105, 'lon': 101.9758},
    'Indonesia': {'lat': -0.7893, 'lon': 113.9213},
    'Philippines': {'lat': 12.8797, 'lon': 121.7740},
    'Belgium': {'lat': 50.8503, 'lon': 4.3517},
    'Austria': {'lat': 47.5162, 'lon': 14.5501},
    'Switzerland': {'lat': 46.8182, 'lon': 8.2275},
    'Portugal': {'lat': 39.3999, 'lon': -8.2245},
    'Sweden': {'lat': 60.1282, 'lon': 18.6435},
    'Denmark': {'lat': 56.2639, 'lon': 9.5018},
    'Norway': {'lat': 60.4720, 'lon': 8.4689},
    'Poland': {'lat': 51.9194, 'lon': 19.1451},
    'Greece': {'lat': 39.0742, 'lon': 21.8243},
}

# =============================================================================
# 5. PREPARAR DATOS PARA EL MAPA
# =============================================================================

# Crear lista de países con coordenadas
map_data = []
for country in paises_25:
    if country in country_coords:
        data = country_emotions_data[country]
        map_data.append({
            'country': country,
            'lat': country_coords[country]['lat'],
            'lon': country_coords[country]['lon'],
            'total_tweets': data['total_tweets'],
            'dominant': data['dominant'],
            'dominant_pct': data['dominant_pct'],
            'percentages': data['percentages']
        })
    else:
        print(f"⚠️ {country} no tiene coordenadas")

print(f"\n🗺️ Países en el mapa: {len(map_data)}")

# =============================================================================
# 6. COLORES POR EMOCIÓN
# =============================================================================

emotion_colors = {
    'joy': '#ba1313',
    'trust': '#3498db',
    'anticipation': '#f39c12',
    'surprise': '#e67e22',
    'sadness': '#95a5a6',
    'fear': '#9b59b6',
    'anger': '#e74c3c',
    'neutral': '#031e48'
}

# =============================================================================
# 7. CREAR TOOLTIP COMPLETO Y MAPA
# =============================================================================

fig = go.Figure()

# Crear hover text para cada país
hover_texts = []
lats = []
lons = []
sizes = []
colors = []

for country_data in map_data:
    # Construir texto de emociones en orden descendente
    emotions_lines = []
    for emotion, pct in country_data['percentages'].items():
        if pct > 0:
            emotions_lines.append(f"{emotion}: {pct:.0f}%")
    
    emotions_text = "<br>".join(emotions_lines)
    
    hover_text = f"""
<b>{country_data['country']}</b><br>
📊 Total tweets: {country_data['total_tweets']:,}<br>
🎭 Emoción dominante: {country_data['dominant']} ({country_data['dominant_pct']:.0f}%)<br>
<br>
 Desglose de emociones:<br>
{emotions_text}
"""
    
    hover_texts.append(hover_text)
    lats.append(country_data['lat'])
    lons.append(country_data['lon'])
    sizes.append(np.log1p(country_data['total_tweets']) * 12)
    colors.append(emotion_colors.get(country_data['dominant'], '#bdc3c7'))

fig.add_trace(go.Scattergeo(
    lon=lons,
    lat=lats,
    text=hover_texts,
    mode='markers',
    marker=dict(
        size=sizes,
        color=colors,
        opacity=0.8,
        line=dict(width=1, color='white'),
        sizemode='area',
        sizeref=2.*max(sizes)/(40**2),
        sizemin=6
    ),
    hovertemplate='%{text}<extra></extra>'
))

# Configurar diseño
fig.update_layout(
    title=dict(
        text=f' Mapa de Emociones F1',
        x=0.5,
        font=dict(size=24, color='#333')
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
        showframe=False,
        lataxis_range=[-60, 80],
        lonaxis_range=[-140, 180]
    ),
    height=700,
    margin=dict(l=0, r=0, t=50, b=0)
)

# Agregar leyenda
for emotion, color in emotion_colors.items():
    if emotion in [d['dominant'] for d in map_data]:
        fig.add_trace(go.Scattergeo(
            lon=[None], lat=[None],
            mode='markers',
            marker=dict(size=10, color=color),
            name=emotion.capitalize(),
            showlegend=True
        ))

# =============================================================================
# 8. GUARDAR Y MOSTRAR
# =============================================================================

output_path = Path(__file__).parent / "emotion_map_25_countries.html"
fig.write_html(output_path)
print(f"\n✅ Mapa guardado: {output_path}")

print("\n📊 LISTA COMPLETA DE PAÍSES EN EL MAPA:")
print("-" * 60)
for country_data in sorted(map_data, key=lambda x: x['total_tweets'], reverse=True):
    print(f"   {country_data['country']:20} | {country_data['dominant']:12} | {country_data['dominant_pct']:5.0f}% | {country_data['total_tweets']:5,} tweets")

# Mostrar mapa
fig.show(config={'displayModeBar': True})

print(f"\n🎉 Mapa completado con {len(map_data)} países!")