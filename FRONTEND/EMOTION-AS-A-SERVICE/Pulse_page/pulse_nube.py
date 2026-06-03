# -*- coding: utf-8 -*-
"""Word cloud provider for Fan Pulse."""

from collections import Counter
import re

import matplotlib.pyplot as plt

from pulse_data import get_text_series, load_clean_tweets

CHART_BACKGROUND = "#1A1A2E"
CHART_GRID = "#2F3048"
CHART_TEXT = "#F5F5F5"
RED_TEXT = "#FF6B6B"


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

    figure, axes = plt.subplots(figsize=(12, 6), facecolor=CHART_BACKGROUND)
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color=CHART_BACKGROUND,
        colormap="Reds",
        color_func=_red_color_func,
    ).generate_from_frequencies(dict(word_counts))
    axes.set_facecolor(CHART_BACKGROUND)
    axes.imshow(wordcloud, interpolation="bilinear")
    axes.axis("off")
    axes.set_title("GLOBAL DE PALABRAS", fontsize=16, fontweight="bold", color=RED_TEXT)
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
    figure, axes = plt.subplots(figsize=(12, 6), facecolor=CHART_BACKGROUND)
    axes.set_facecolor(CHART_BACKGROUND)
    axes.axis("off")
    axes.text(
        0.5,
        0.5,
        "No hay palabras para mostrar.",
        ha="center",
        va="center",
        fontsize=16,
        color=CHART_TEXT,
    )
    figure.tight_layout()
    return figure


def _create_word_frequency_figure(word_counts):
    top_words = list(reversed(word_counts[:20]))
    words = [word for word, count in top_words]
    counts = [count for word, count in top_words]

    figure, axes = plt.subplots(figsize=(12, 6), facecolor=CHART_BACKGROUND)
    axes.set_facecolor(CHART_BACKGROUND)
    axes.barh(words, counts, color="#C0392B")
    axes.set_title("GLOBAL DE PALABRAS", fontsize=16, fontweight="bold", color=RED_TEXT)
    axes.set_xlabel("Frecuencia", color=CHART_TEXT)
    axes.tick_params(axis="x", colors=CHART_TEXT)
    axes.tick_params(axis="y", labelsize=9, colors=CHART_TEXT)
    axes.grid(axis="x", color=CHART_GRID, linewidth=0.8)
    for spine in axes.spines.values():
        spine.set_color(CHART_GRID)
    figure.tight_layout()

    return figure


if __name__ == "__main__":
    wordcloud_figure = create_wordcloud()
    wordcloud_figure.show()
