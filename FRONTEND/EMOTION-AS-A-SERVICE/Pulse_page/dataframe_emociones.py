# =============================================================================
# COUNTRY EMOTION DATASET - VERSIÓN MEJORADA
# =============================================================================

import pandas as pd
import re
from pathlib import Path
from nrclex import NRCLex
from textblob import TextBlob

print("🔍 Buscando tweets_cleaned.csv...")

ROOT_DIR = Path(__file__).resolve()
csv_files = list(ROOT_DIR.parents[5].rglob("tweets_cleaned.csv"))

if not csv_files:
    raise FileNotFoundError("❌ No se encontró tweets_cleaned.csv")

csv_path = csv_files[0]
print(f"✅ Dataset encontrado:\n{csv_path}")

# =============================================================================
# LOAD DATA
# =============================================================================
df = pd.read_csv(csv_path, low_memory=False)
print(f"📥 {len(df):,} tweets cargados")

# =============================================================================
# KEEP NECESSARY COLUMNS
# =============================================================================
df = df[['text', 'user_location_normalized']].dropna()
df.columns = ['tweet', 'country']
print(f"📍 Usando columna: user_location_normalized")

# =============================================================================
# LIMPIEZA AGRESIVA DE TEXTO (elimina emojis, URLs, menciones, etc.)
# =============================================================================
def clean_text_aggressive(text):
    """Limpia el texto eliminando emojis, URLs, menciones y caracteres especiales"""
    text = str(text)
    
    # 1. Eliminar URLs
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    
    # 2. Eliminar menciones (@usuario)
    text = re.sub(r"@\w+", "", text)
    
    # 3. Eliminar hashtags (pero conservar la palabra)
    text = re.sub(r"#", "", text)
    
    # 4. Eliminar emojis y caracteres especiales (rango Unicode de emojis)
    # Esto elimina emojis, símbolos, y caracteres no ASCII
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Elimina caracteres no ASCII (emojis)
    
    # 5. Eliminar números (opcional, a veces útil)
    # text = re.sub(r"\d+", "", text)
    
    # 6. Dejar solo letras, espacios y signos de puntuación básicos
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    
    # 7. Convertir a minúsculas
    text = text.lower()
    
    # 8. Eliminar espacios múltiples
    text = re.sub(r"\s+", " ", text).strip()
    
    # 9. Eliminar palabras muy cortas (menos de 3 letras) que no aportan
    words = text.split()
    words = [w for w in words if len(w) > 2]
    text = " ".join(words)
    
    return text if len(text) > 0 else "empty"

print("🧹 Limpiando tweets (eliminando emojis y caracteres especiales)...")
df['tweet_clean'] = df['tweet'].apply(clean_text_aggressive)
df = df[df['tweet_clean'] != "empty"]
df = df[df['tweet_clean'].str.len() > 5]
print(f"📊 {len(df):,} tweets después de limpiar")

# =============================================================================
# SAMPLE (más rápido)
# =============================================================================
MAX_ROWS = 50000
if len(df) > MAX_ROWS:
    df = df.sample(MAX_ROWS, random_state=42)
print(f"⚡ Analizando {len(df):,} tweets")

# =============================================================================
# FUNCIÓN MEJORADA: TextBlob + NRCLex + Palabras clave
# =============================================================================

# Palabras clave para emociones específicas (para mejorar detección)
emotion_keywords = {
    'joy': ['happy', 'great', 'amazing', 'awesome', 'fantastic', 'brilliant', 'love', 'win', 'winner', 'champion', 'podium', 'celebration'],
    'anger': ['angry', 'mad', 'furious', 'hate', 'terrible', 'awful', 'disaster', 'unfair', 'penalty', 'crash', 'stupid', 'out'],
    'sadness': ['sad', 'unlucky', 'pain', 'hurt', 'disappointed', 'sorry', 'bad luck', 'retire', 'damage'],
    'fear': ['scared', 'fear', 'dangerous', 'risky', 'crash', 'accident', 'safety'],
    'anticipation': ['expect', 'hope', 'finally', 'can wait', 'excited', 'upcoming', 'ready'],
    'trust': ['trust', 'believe', 'sure', 'confident', 'surely', 'best team'],
    'surprise': ['shock', 'unbelievable', 'wow', 'omg', 'surprise', 'incredible', 'unexpected']
}

def get_enhanced_emotion(text):
    """Detecta emoción usando NRCLex + TextBlob + palabras clave"""
    if not text or text == "empty":
        return "neutral"
    
    # 1. TextBlob para sentimiento base
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    
    # 2. NRCLex (si encuentra algo)
    try:
        emotion_nrc = NRCLex(text)
        top_emotions = emotion_nrc.top_emotions
        
        if len(top_emotions) > 0 and top_emotions[0][1] > 0:  # Si tiene score > 0
            detected = top_emotions[0][0]
            return detected
    except:
        pass
    
    # 3. Búsqueda por palabras clave
    text_lower = text.lower()
    for emotion, keywords in emotion_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return emotion
    
    # 4. Si no hay coincidencia, usar TextBlob para positivo/negativo/neutral
    if polarity > 0.2:
        return "joy"  # positivo fuerte
    elif polarity > 0.05:
        return "trust"  # positivo leve
    elif polarity < -0.2:
        return "anger"  # negativo fuerte
    elif polarity < -0.05:
        return "sadness"  # negativo leve
    else:
        return "neutral"

print("🧠 Detectando emociones mejoradas...")
df['emotion'] = df['tweet_clean'].apply(get_enhanced_emotion)
df['polarity'] = df['tweet_clean'].apply(lambda x: TextBlob(x).sentiment.polarity)

# =============================================================================
# DEBUG - Ver distribución
# =============================================================================
print("\n" + "=" * 50)
print("📊 DISTRIBUCIÓN DE EMOCIONES")
print("=" * 50)
emotion_counts = df['emotion'].value_counts()
for emotion, count in emotion_counts.items():
    percentage = (count / len(df)) * 100
    print(f"   {emotion:12} {count:6,} ({percentage:.1f}%)")

# =============================================================================
# GROUP COUNTRY + EMOTION
# =============================================================================
summary = df.groupby(['country', 'emotion']).size().reset_index(name='tweets')

# Emoción dominante por país
idx = summary.groupby('country')['tweets'].idxmax()
country_emotions = summary.loc[idx].sort_values('tweets', ascending=False).reset_index(drop=True)

# =============================================================================
# FILTRAR PAÍSES CON POCOS TWEETS
# =============================================================================
country_emotions = country_emotions[country_emotions['tweets'] >= 10]

# =============================================================================
# VER PAÍSES CON EMOCIONES DIFERENTES A NEUTRAL
# =============================================================================
print("\n" + "=" * 50)
print("🌍 PAÍSES CON EMOCIONES NO-NEUTRALES")
print("=" * 50)
non_neutral = country_emotions[country_emotions['emotion'] != 'neutral']
print(f"Total: {len(non_neutral)} países")
for _, row in non_neutral.head(20).iterrows():
    print(f"   {row['country']:20} → {row['emotion']:12} ({row['tweets']:,} tweets)")

# =============================================================================
# SAVE DATASET
# =============================================================================
output_path = csv_path.parent / "country_emotions_enhanced.csv"
country_emotions.to_csv(output_path, index=False)

# También guardar el DataFrame completo con emociones por tweet
tweets_with_emotions = df[['country', 'tweet_clean', 'emotion', 'polarity']]
tweets_output = csv_path.parent / "tweets_with_emotions.csv"
tweets_with_emotions.to_csv(tweets_output, index=False)

print("\n" + "=" * 50)
print("✅ DATASETS GENERADOS")
print("=" * 50)
print(f"📁 Emociones por país: {output_path}")
print(f"📁 Tweets con emociones: {tweets_output}")

print("\n📊 Preview (top 20 países):")
print(country_emotions.head(20))

# =============================================================================
# TOP 10 EMOCIONES POR PAÍS (opcional)
# =============================================================================
print("\n" + "=" * 50)
print("📊 TOP 10 PAÍSES POR CADA EMOCIÓN")
print("=" * 50)

for emotion in ['joy', 'anger', 'sadness', 'anticipation', 'trust', 'surprise', 'fear']:
    top_countries = summary[summary['emotion'] == emotion].nlargest(5, 'tweets')
    if len(top_countries) > 0:
        print(f"\n{emotion.upper()}:")
        for _, row in top_countries.iterrows():
            print(f"   {row['country']:20} {row['tweets']:5,} tweets")