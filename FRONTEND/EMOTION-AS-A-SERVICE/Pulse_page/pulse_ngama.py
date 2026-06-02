# -*- coding: utf-8 -*-
"""N-gram provider for Fan Pulse."""

from collections import Counter
import re

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from pulse_data import get_text_series, load_clean_tweets


STOPWORDS = [
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
]


def create_ngrams():
    """Return unigrams, bigrams, and trigrams for Oracle Red Bull mentions."""
    tweets_dataframe = load_clean_tweets()
    text_values = get_text_series(tweets_dataframe)
    redbull_text_values = text_values[text_values.str.contains("red bull|redbull|oracle", case=False, na=False)]
    combined_text = " ".join(redbull_text_values)

    if not combined_text.strip():
        return _create_empty_ngrams_figure()

    ngram_groups = [
        _extract_ngrams(combined_text, ngram_range=(1, 1)),
        _extract_ngrams(combined_text, ngram_range=(2, 2)),
        _extract_ngrams(combined_text, ngram_range=(3, 3)),
    ]
    if not any(ngram_groups):
        return _create_empty_ngrams_figure()

    figure = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=("Unigramas", "Bigramas", "Trigramas"),
        horizontal_spacing=0.15,
    )
    red_palette = ["#FF6B6B", "#E74C3C", "#C0392B"]

    for column_index, ngrams in enumerate(ngram_groups, start=1):
        figure.add_trace(
            go.Bar(
                x=[count for term, count in ngrams],
                y=[term for term, count in ngrams],
                orientation="h",
                marker_color=red_palette[column_index - 1],
                text=[_format_ngram_count(count) for term, count in ngrams],
                textposition="outside",
            ),
            row=1,
            col=column_index,
        )

    figure.update_layout(
        title=dict(text="TOP N-GRAMAS - ORACLE RED BULL RACING", font=dict(color="#8B0000", size=18)),
        height=550,
        width=1100,
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    for column_index in range(1, 4):
        figure.update_xaxes(title_text="Frecuencia", row=1, col=column_index, tickfont=dict(color="#C0392B"))
        figure.update_yaxes(title_text="Termino", row=1, col=column_index, tickfont=dict(color="#C0392B"))

    return figure


def _extract_ngrams(text, ngram_range):
    min_ngram_length, max_ngram_length = ngram_range
    if min_ngram_length != max_ngram_length:
        raise ValueError("Este proveedor solo acepta rangos de n-gramas exactos.")

    words = [
        word
        for word in re.findall(r"\b[a-z]{3,}\b", text.lower())
        if word not in STOPWORDS
    ]
    ngram_length = min_ngram_length
    ngrams = zip(*(words[offset:] for offset in range(ngram_length)))
    ngram_counts = Counter(" ".join(ngram) for ngram in ngrams)

    return ngram_counts.most_common(10)


def _format_ngram_count(count):
    if count >= 1000:
        return f"{count / 1000:.1f}K"
    return str(count)


def _create_empty_ngrams_figure():
    figure = go.Figure()
    figure.add_annotation(
        text="No hay n-gramas para mostrar.",
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=16, color="#333333"),
    )
    figure.update_layout(height=550, plot_bgcolor="white", paper_bgcolor="white")
    return figure


if __name__ == "__main__":
    ngrams_figure = create_ngrams()
    ngrams_figure.show(config={"displayModeBar": True})
