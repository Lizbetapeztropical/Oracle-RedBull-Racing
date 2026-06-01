# -*- coding: utf-8 -*-
"""Nube de palabras - F1 Pulse"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import re

def create_wordcloud():
    """Genera nube de palabras global con gama de rojos"""
    
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    file_path = BASE_DIR / "BACKEND" / "EMOTION-AS-A-SERVICE" / "model" / "DATA" / "Tweets" / "tweets_cleaned.csv"
    
    df = pd.read_csv(file_path, low_memory=False)
    print(f"✅ {len(df):,} tweets cargados")
    
    # Unir todo el texto limpio
    all_text = " ".join(df['clean_text'].fillna('').astype(str))
    
    # Limpiar y contar palabras
    words = re.findall(r'\b[a-z]{3,}\b', all_text.lower())
    stopwords = {'the', 'and', 'for', 'are', 'was', 'that', 'this', 'with', 'from', 'have', 'not', 'but', 'get', 'its', 'you', 'all', 'can', 'out', 'one', 'they', 'just', 'like', 'your', 'will', 'has', 'been', 'were', 'their', 'them', 'into', 'when', 'would', 'could', 'should', 'said', 'what', 'there', 'more', 'some', 'than', 'then', 'now', 'did', 'very'}
    
    words_filtered = [w for w in words if w not in stopwords]
    word_counts = Counter(words_filtered).most_common(50)
    
    # Colores rojos personalizados
    def red_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        return f'hsl({0}, 100%, {30 + (font_size / 300) * 40}%)'
    
    # Generar nube con colores rojos
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        colormap='Reds',  # Gama de rojos
        color_func=red_color_func
    ).generate_from_frequencies(dict(word_counts))
    
    # Mostrar
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title("🌍 GLOBAL DE PALABRAS", fontsize=16, fontweight='bold', color='#8B0000')
    plt.tight_layout()
    plt.show()
    
    return wordcloud

if __name__ == "__main__":
    create_wordcloud()
    print("✅ Nube de palabras generada (gama de rojos)")