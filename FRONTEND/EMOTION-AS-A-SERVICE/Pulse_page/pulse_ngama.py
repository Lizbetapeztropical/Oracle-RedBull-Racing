# -*- coding: utf-8 -*-
"""N-gramas Oracle Red Bull Racing - F1 Pulse (rojos)"""

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.feature_extraction.text import CountVectorizer

def create_ngrams():
    """Genera unigramas, bigramas y trigramas de Oracle Red Bull Racing (gama de rojos)"""
    
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    file_path = BASE_DIR / "BACKEND" / "EMOTION-AS-A-SERVICE" / "model" / "DATA" / "Tweets" / "tweets_cleaned.csv"
    
    df = pd.read_csv(file_path, low_memory=False)
    print(f"✅ {len(df):,} tweets cargados")
    
    # Filtrar tweets que mencionan Red Bull
    redbull_tweets = df[df['clean_text'].str.contains('red bull|redbull|oracle', na=False, case=False)]
    print(f"📊 Tweets sobre Oracle Red Bull: {len(redbull_tweets):,}")
    
    # Unir textos
    text = " ".join(redbull_tweets['clean_text'].fillna('').astype(str))
    
    stopwords = ['the', 'and', 'for', 'are', 'was', 'that', 'this', 'with', 'from', 'have', 'not', 'but', 'get', 'its', 'you', 'all', 'can', 'out', 'one', 'they', 'just', 'like', 'your', 'will', 'has', 'been', 'were', 'their', 'them', 'into', 'when', 'would', 'could', 'should', 'said', 'what', 'there', 'more', 'some', 'than', 'then', 'now', 'did', 'very']
    
    # Gama de rojos para cada columna
    red_palette = ['#FF6B6B', '#E74C3C', '#C0392B']
    
    # Unigramas
    unigram_vectorizer = CountVectorizer(ngram_range=(1, 1), stop_words=stopwords, max_features=10)
    unigram_matrix = unigram_vectorizer.fit_transform([text])
    unigrams = sorted(zip(unigram_vectorizer.get_feature_names_out(), unigram_matrix.toarray()[0]), key=lambda x: x[1], reverse=True)
    
    # Bigramas
    bigram_vectorizer = CountVectorizer(ngram_range=(2, 2), stop_words=stopwords, max_features=10)
    bigram_matrix = bigram_vectorizer.fit_transform([text])
    bigrams = sorted(zip(bigram_vectorizer.get_feature_names_out(), bigram_matrix.toarray()[0]), key=lambda x: x[1], reverse=True)
    
    # Trigramas
    trigram_vectorizer = CountVectorizer(ngram_range=(3, 3), stop_words=stopwords, max_features=10)
    trigram_matrix = trigram_vectorizer.fit_transform([text])
    trigrams = sorted(zip(trigram_vectorizer.get_feature_names_out(), trigram_matrix.toarray()[0]), key=lambda x: x[1], reverse=True)
    
    # Crear subplots
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("Unigramas", "Bigramas", "Trigramas"),
        horizontal_spacing=0.15
    )
    
    # Unigramas (rojo claro)
    fig.add_trace(go.Bar(
        x=[count for word, count in unigrams[:10]],
        y=[word for word, count in unigrams[:10]],
        orientation='h',
        name='Unigramas',
        marker_color=red_palette[0],
        text=[f"{count/1000:.1f}K" if count >= 1000 else str(count) for word, count in unigrams[:10]],
        textposition='outside'
    ), row=1, col=1)
    
    # Bigramas (rojo medio)
    fig.add_trace(go.Bar(
        x=[count for word, count in bigrams[:10]],
        y=[word for word, count in bigrams[:10]],
        orientation='h',
        name='Bigramas',
        marker_color=red_palette[1],
        text=[f"{count/1000:.1f}K" if count >= 1000 else str(count) for word, count in bigrams[:10]],
        textposition='outside'
    ), row=1, col=2)
    
    # Trigramas (rojo oscuro)
    fig.add_trace(go.Bar(
        x=[count for word, count in trigrams[:10]],
        y=[word for word, count in trigrams[:10]],
        orientation='h',
        name='Trigramas',
        marker_color=red_palette[2],
        text=[f"{count/1000:.1f}K" if count >= 1000 else str(count) for word, count in trigrams[:10]],
        textposition='outside'
    ), row=1, col=3)
    
    fig.update_layout(
        title=dict(
            text="📊 TOP N-GRAMAS - ORACLE RED BULL RACING",
            font=dict(color='#8B0000', size=18)
        ),
        height=550,
        width=1100,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Ajustar ejes - CORREGIDO: update_xaxes y update_yaxes (con 's' al final)
    for i in range(1, 4):
        fig.update_xaxes(title_text="Frecuencia", row=1, col=i, tickfont=dict(color='#C0392B'))
        fig.update_yaxes(title_text="Término", row=1, col=i, tickfont=dict(color='#C0392B'))
    
    return fig

if __name__ == "__main__":
    fig = create_ngrams()
    fig.show(config={'displayModeBar': True})
    print("✅ N-gramas generados (gama de rojos)")