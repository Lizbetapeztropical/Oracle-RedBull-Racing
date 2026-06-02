# -*- coding: utf-8 -*-
"""Word cloud provider for Fan Pulse."""

from collections import Counter
import re

import matplotlib.pyplot as plt

from pulse_data import get_text_series, load_clean_tweets


STOPWORDS = {
    "the",
    "and",
    "for",
    "are",
    "was",
    "that",
    "this",
    "with",
    "from",
    "have",
    "not",
    "but",
    "get",
    "its",
    "you",
    "all",
    "can",
    "out",
    "one",
    "they",
    "just",
    "like",
    "your",
    "will",
    "has",
    "been",
    "were",
    "their",
    "them",
    "into",
    "when",
    "would",
    "could",
    "should",
    "said",
    "what",
    "there",
    "more",
    "some",
    "than",
    "then",
    "now",
    "did",
    "very",
}


def create_wordcloud():
    """Return a Matplotlib figure with the global Fan Pulse word cloud."""
    tweets_dataframe = load_clean_tweets()
    all_text = " ".join(get_text_series(tweets_dataframe))
    word_counts = _count_words(all_text)

    if not word_counts:
        return _create_empty_wordcloud_figure()

    try:
        from wordcloud import WordCloud
    except ImportError:
        return _create_word_frequency_figure(word_counts)

    figure, axes = plt.subplots(figsize=(12, 6))
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color="white",
        colormap="Reds",
        color_func=_red_color_func,
    ).generate_from_frequencies(dict(word_counts))
    axes.imshow(wordcloud, interpolation="bilinear")
    axes.axis("off")
    axes.set_title("GLOBAL DE PALABRAS", fontsize=16, fontweight="bold", color="#8B0000")
    figure.tight_layout()

    return figure


def _count_words(text):
    words = re.findall(r"\b[a-z]{3,}\b", text.lower())
    filtered_words = [word for word in words if word not in STOPWORDS]
    return Counter(filtered_words).most_common(50)


def _red_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    lightness = 30 + (font_size / 300) * 40
    return f"hsl(0, 100%, {lightness}%)"


def _create_empty_wordcloud_figure():
    figure, axes = plt.subplots(figsize=(12, 6))
    axes.axis("off")
    axes.text(0.5, 0.5, "No hay palabras para mostrar.", ha="center", va="center", fontsize=16)
    figure.tight_layout()
    return figure


def _create_word_frequency_figure(word_counts):
    top_words = list(reversed(word_counts[:20]))
    words = [word for word, count in top_words]
    counts = [count for word, count in top_words]

    figure, axes = plt.subplots(figsize=(12, 6))
    axes.barh(words, counts, color="#C0392B")
    axes.set_title("GLOBAL DE PALABRAS", fontsize=16, fontweight="bold", color="#8B0000")
    axes.set_xlabel("Frecuencia")
    axes.tick_params(axis="y", labelsize=9)
    figure.tight_layout()

    return figure


if __name__ == "__main__":
    wordcloud_figure = create_wordcloud()
    wordcloud_figure.show()
