import os
import pandas as pd
import plotly.express as px

# =========================================================================
# CARGAR DATOS ISO
# =========================================================================

iso_slug = "kimkijun7/iso-csv-file"
archivo_iso = "iso.csv"

if not os.path.exists(archivo_iso):
    print("🗺️ Conectando con Kaggle...")
    import kaggle
    kaggle.api.dataset_download_files(iso_slug, path='.', unzip=True)

df_iso = pd.read_csv(archivo_iso)

# =========================================================================
# TOP 10 PAÍSES CON MÁS TWEETS (SEGÚN TU TABLA)
# =========================================================================

# Datos exactos de tu tabla
top_paises_data = {
    'Ubicación': [
        'United Kingdom',
        'London, England',
        'Italy',
        'London',
        'Paris',
        'UK',
        'England, United Kingdom',
        'United States',
        'India',
        'Manchester'
    ],
    'Tweets': [
        14514,
        12027,
        11240,
        7507,
        7279,
        6247,
        6247,
        4348,
        4019,
        3889
    ]
}

top_paises = pd.DataFrame(top_paises_data)

print("\n📊 TOP 10 PAÍSES CON MÁS TWEETS:")
print("-" * 50)
for i, row in top_paises.iterrows():
    print(f"{i+1}. {row['Ubicación']:<25} {row['Tweets']:>6,} tweets")

# =========================================================================
# MAPEO DE UBICACIONES A CÓDIGOS ISO (AGRUPANDO POR PAÍS REAL)
# =========================================================================

# Mapeo específico para cada ubicación
# Nota: Múltiples ubicaciones del mismo país se sumarán
mapeo_paises = {
    'United Kingdom': 'GBR',
    'London, England': 'GBR',
    'London': 'GBR',
    'UK': 'GBR',
    'England, United Kingdom': 'GBR',
    'Manchester': 'GBR',
    'Italy': 'ITA',
    'Paris': 'FRA',
    'United States': 'USA',
    'India': 'IND'
}

# Agregar código ISO
top_paises['codigo_iso'] = top_paises['Ubicación'].map(mapeo_paises)

# Agrupar por código ISO (sumando tweets del mismo país)
top_paises_agrupado = top_paises.groupby('codigo_iso').agg({
    'Tweets': 'sum',
    'Ubicación': lambda x: ', '.join(x)  # Guardar las ubicaciones originales
}).reset_index()

# Ordenar por tweets descendente
top_paises_agrupado = top_paises_agrupado.sort_values('Tweets', ascending=False)

print("\n📍 PAÍSES AGRUPADOS POR CÓDIGO ISO:")
print("-" * 50)
for _, row in top_paises_agrupado.iterrows():
    # Obtener nombre del país
    nombre_pais = df_iso[df_iso['Alpha-3 code'] == row['codigo_iso']]['English short name lower case'].values
    nombre = nombre_pais[0] if len(nombre_pais) > 0 else row['codigo_iso']
    print(f"{nombre:<20} ({row['codigo_iso']}): {row['Tweets']:>6,} tweets")

# =========================================================================
# PREPARAR DATAFRAME PARA EL MAPA
# =========================================================================

# Crear dataframe con todos los países del mundo
df_mapa = df_iso[['Alpha-3 code', 'English short name lower case']].copy()

# Inicializar todos los tweets en 0
df_mapa['Tweets'] = 0

# Asignar los tweets agrupados a cada país
for _, row in top_paises_agrupado.iterrows():
    df_mapa.loc[df_mapa['Alpha-3 code'] == row['codigo_iso'], 'Tweets'] = row['Tweets']

# Verificar qué países del top se colorearán
print("\n🎨 PAÍSES QUE APARECERÁN COLOREADOS EN EL MAPA:")
print("-" * 50)
paises_coloreados = df_mapa[df_mapa['Tweets'] > 0][['Alpha-3 code', 'English short name lower case', 'Tweets']]
for _, row in paises_coloreados.iterrows():
    print(f"• {row['English short name lower case']:<20} ({row['Alpha-3 code']}): {row['Tweets']:>6,} tweets")

# =========================================================================
# GRÁFICO DE BARRAS DEL TOP 10 (VERSIÓN CORREGIDA)
# =========================================================================

# Preparar datos para el gráfico de barras (versión agrupada)
top_barras = top_paises_agrupado.copy()
top_barras['nombre_pais'] = top_barras['codigo_iso'].apply(
    lambda x: df_iso[df_iso['Alpha-3 code'] == x]['English short name lower case'].values[0]
)
top_barras = top_barras.sort_values('Tweets', ascending=True)

fig_barras = px.bar(
    top_barras,
    x='Tweets',
    y='nombre_pais',
    orientation='h',
    title="🏎️ TOP 10 PAÍSES CON MÁS TWEETS DE F1 (AGRUPADO POR PAÍS REAL)",
    text='Tweets',
    color='Tweets',
    color_continuous_scale='Reds'
)

fig_barras.update_traces(
    texttemplate='%{text:,.0f}',
    textposition='outside'
)

fig_barras.update_layout(
    template='plotly_white',
    height=500,
    width=900,
    xaxis_title="Número de Tweets",
    yaxis_title="País"
)

print("\n🎨 Mostrando gráfico de barras...")
fig_barras.show()

# =========================================================================
# MAPA DE CALOR INTERACTIVO
# =========================================================================

# Crear mapa de calor
fig_mapa = px.choropleth(
    df_mapa,
    locations="Alpha-3 code",
    color="Tweets",
    hover_name="English short name lower case",
    title="🌍 MAPA DE CALOR - DISTRIBUCIÓN DE TWEETS DE F1",
    color_continuous_scale=[
        '#f5f5f5',  # 0 - gris muy claro
        '#ffe5e5',  # muy bajo
        '#ffb3b3',  # bajo
        '#ff8080',  # medio bajo
        '#ff4d4d',  # medio
        '#cc0000',  # alto
        '#8b0000'   # máximo
    ],
    labels={'Tweets': 'Número de Tweets'},
    range_color=[0, top_paises_agrupado['Tweets'].max()]
)

# Crear texto personalizado para el hover con los tweets exactos
df_mapa['texto_hover'] = df_mapa.apply(
    lambda row: f"<b>{row['English short name lower case']}</b><br>"
                f"📊 <b>{row['Tweets']:,.0f} tweets</b><br>"
                f"🔥 Top 10 países" 
                if row['Tweets'] > 0 
                else f"<b>{row['English short name lower case']}</b><br>"
                     f"📊 No está en el Top 10",
    axis=1
)

fig_mapa.update_traces(
    hovertemplate="%{customdata[0]}<extra></extra>",
    custom_data=df_mapa[['texto_hover']].values
)

# Estilizar el mapa
fig_mapa.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="lightgray",
        showland=True,
        landcolor="#fafafa",
        projection_type='equirectangular',
        showcountries=True,
        countrycolor="#d3d3d3",
        countrywidth=0.5
    ),
    title={
        'text': "<b>🔥 DISTRIBUCIÓN DE TWEETS DE FÓRMULA 1 (TOP PAÍSES)</b>",
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 20, 'family': 'Arial Black', 'color': '#333333'}
    },
    margin=dict(l=0, r=0, t=60, b=0),
    coloraxis_colorbar=dict(
        title="📊 NÚMERO DE TWEETS",
        thickness=20,
        len=0.7,
        tickformat=",.0f",
        title_font=dict(size=12, family="Arial Black"),
        tickfont=dict(size=10)
    ),
    height=600,
    width=1200,
    hoverlabel=dict(
        bgcolor="white",
        font_size=13,
        font_family="Arial",
        font_color="#333333"
    ),
    paper_bgcolor='white',
    plot_bgcolor='white'
)

# Mostrar el mapa
print("\n🗺️ Mostrando mapa de calor interactivo...")
fig_mapa.show()

# =========================================================================
# RESUMEN FINAL
# =========================================================================

print("\n" + "="*60)
print("RESUMEN FINAL DEL MAPA DE CALOR")
print("="*60)
print(f"📊 Total de tweets en Top 10 (original): {top_paises['Tweets'].sum():,}")
print(f"📊 Total de tweets agrupados por país: {top_paises_agrupado['Tweets'].sum():,}")
print(f"🌍 Países coloreados en el mapa: {len(paises_coloreados)}")
print("\n📍 PAÍSES COLOREADOS CON SUS TWEETS:")
for _, row in paises_coloreados.iterrows():
    print(f"   • {row['English short name lower case']:<20} {row['Tweets']:>8,} tweets")