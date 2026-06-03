#!/usr/bin/env python
# coding: utf-8
"""
Script para preprocesar tweets_cleaned.csv y generar un archivo liviano
con solo los datos necesarios para análisis de sentimiento.
Ubicación: BACKEND/EMOTION-AS-A-SERVICE/model/DATA/Tweets/
"""

import pandas as pd
import numpy as np
from pathlib import Path
from textblob import TextBlob
import sys

# ==================================================
# CONFIGURACIÓN
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
TWEETS_INPUT = BASE_DIR / "tweets_cleaned.csv"
TWEETS_OUTPUT = BASE_DIR / "sentiment_data.csv"

print("=" * 60)
print(" PREPROCESAMIENTO DE TWEETS PARA ANÁLISIS DE SENTIMIENTO")
print("=" * 60)

# ==================================================
# VERIFICAR ARCHIVO DE ENTRADA
# ==================================================

if not TWEETS_INPUT.exists():
    print(f"❌ Error: No se encuentra {TWEETS_INPUT}")
    print("Asegúrate de que el archivo tweets_cleaned.csv existe en esta carpeta.")
    sys.exit(1)

print(f"📂 Archivo de entrada: {TWEETS_INPUT}")
print(f"📂 Archivo de salida: {TWEETS_OUTPUT}")

# ==================================================
# CARGAR DATOS
# ==================================================

print("\n📥 Cargando tweets...")
try:
    df = pd.read_csv(TWEETS_INPUT, low_memory=False)
    print(f"✅ {len(df):,} tweets cargados")
except Exception as e:
    print(f"❌ Error cargando archivo: {e}")
    sys.exit(1)

# ==================================================
# IDENTIFICAR COLUMNAS NECESARIAS
# ==================================================

print("\n🔍 Identificando columnas...")

# Columna de texto
text_col = None
for col in ['clean_text', 'text', 'tweet', 'content']:
    if col in df.columns:
        text_col = col
        break

if text_col is None:
    print("❌ No se encontró columna de texto")
    sys.exit(1)
print(f"   ✅ Columna de texto: '{text_col}'")

# Columna de año
year_col = None
for col in ['year', 'YEAR', 'Year', 'date_year']:
    if col in df.columns:
        year_col = col
        break

if year_col is None:
    print("❌ No se encontró columna de año")
    sys.exit(1)
print(f"   ✅ Columna de año: '{year_col}'")

# ==================================================
# LIMPIEZA Y PREPARACIÓN
# ==================================================

print("\n🧹 Limpiando datos...")

# Crear DataFrame con solo las columnas necesarias
df_clean = df[[year_col, text_col]].copy()
df_clean = df_clean.dropna(subset=[year_col, text_col])

# Limitar a una muestra para pruebas (opcional, quitar si quieres todos los datos)
# Si el archivo es demasiado grande, puedes limitar a 500,000 registros
if len(df_clean) > 500000:
    df_clean = df_clean.sample(500000, random_state=42)
    print(f"   ⚠️ Muestra reducida a 500,000 tweets para rendimiento")

print(f"   ✅ {len(df_clean):,} tweets después de limpieza")

# ==================================================
# CALCULAR SENTIMIENTO
# ==================================================

print("\n🧠 Calculando sentimiento (esto puede tomar unos minutos)...")

def get_sentiment_score(text):
    if not isinstance(text, str) or len(text.strip()) == 0:
        return 0
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity
    except:
        return 0

def get_sentiment_label(score):
    if score > 0.1:
        return 'Positive'
    elif score < -0.1:
        return 'Negative'
    else:
        return 'Neutral'

# Aplicar análisis de sentimiento
df_clean['polarity'] = df_clean[text_col].fillna('').apply(get_sentiment_score)
df_clean['sentiment'] = df_clean['polarity'].apply(get_sentiment_label)

print("   ✅ Sentimiento calculado")

# ==================================================
# AGREGAR POR AÑO
# ==================================================

print("\n📊 Agregando datos por año...")

# Resultado por año
sentiment_by_year = df_clean.groupby([year_col, 'sentiment']).size().unstack(fill_value=0).reset_index()
sentiment_by_year = sentiment_by_year.rename(columns={year_col: 'year'})

# Asegurar que todas las columnas existen
for col in ['Positive', 'Negative', 'Neutral']:
    if col not in sentiment_by_year.columns:
        sentiment_by_year[col] = 0

# Calcular totales y porcentajes
sentiment_by_year['total'] = sentiment_by_year['Positive'] + sentiment_by_year['Negative'] + sentiment_by_year['Neutral']
sentiment_by_year['positive_pct'] = (sentiment_by_year['Positive'] / sentiment_by_year['total'] * 100).round(1)
sentiment_by_year['negative_pct'] = (sentiment_by_year['Negative'] / sentiment_by_year['total'] * 100).round(1)
sentiment_by_year['neutral_pct'] = (sentiment_by_year['Neutral'] / sentiment_by_year['total'] * 100).round(1)

# Determinar sentimiento dominante
def get_dominant(row):
    if row['Positive'] >= row['Negative'] and row['Positive'] >= row['Neutral']:
        return 'Positive'
    elif row['Negative'] >= row['Positive'] and row['Negative'] >= row['Neutral']:
        return 'Negative'
    else:
        return 'Neutral'

sentiment_by_year['dominant'] = sentiment_by_year.apply(get_dominant, axis=1)

# ==================================================
# GUARDAR RESULTADOS
# ==================================================

print(f"\n💾 Guardando archivo en: {TWEETS_OUTPUT}")

# Guardar solo los datos necesarios para la app
output_columns = ['year', 'Positive', 'Negative', 'Neutral', 'total', 'positive_pct', 'negative_pct', 'neutral_pct', 'dominant']
sentiment_by_year[output_columns].to_csv(TWEETS_OUTPUT, index=False)

print(f"✅ Archivo guardado correctamente")
print(f"   → {len(sentiment_by_year)} años procesados")
print(f"   → Tamaño del archivo: {TWEETS_OUTPUT.stat().st_size / 1024:.1f} KB")

# ==================================================
# MOSTRAR RESULTADOS
# ==================================================

print("\n" + "=" * 60)
print("📊 RESULTADOS DEL PREPROCESAMIENTO")
print("=" * 60)
print("\nSentimiento por año:")
print(sentiment_by_year[['year', 'Positive', 'Negative', 'Neutral', 'total', 'dominant']].to_string(index=False))

print("\n" + "=" * 60)
print("✅ PROCESO COMPLETADO EXITOSAMENTE")
print("=" * 60)
print(f"\nAhora puedes usar '{TWEETS_OUTPUT}' en analytics.py para cargar datos de sentimiento de forma rápida.")


