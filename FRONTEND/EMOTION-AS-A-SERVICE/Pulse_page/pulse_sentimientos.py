# -*- coding: utf-8 -*-
"""Sentiment KPI chart for Fan Pulse."""

import plotly.graph_objects as go

from pulse_data import load_clean_tweets

CHART_BACKGROUND = "#1A1A2E"
CHART_TEXT = "#F5F5F5"
MUTED_TEXT = "#C7CAD8"


POSITIVE_WORDS = {
    "win",
    "victory",
    "great",
    "amazing",
    "love",
    "best",
    "good",
    "happy",
    "excellent",
    "fantastic",
    "champion",
    "podium",
    "proud",
}
NEGATIVE_WORDS = {
    "crash",
    "bad",
    "terrible",
    "hate",
    "worst",
    "sad",
    "angry",
    "disaster",
    "lose",
    "failure",
    "broken",
    "disappoint",
}


def analizar_sentimientos(tweets_dataframe):
    """Return positive, negative, and neutral tweet counts."""
    if "emotion" in tweets_dataframe.columns:
        return _count_emotion_labels(tweets_dataframe)

    text_values = tweets_dataframe["clean_text"].fillna("").astype(str).str.lower()

    positive_count = 0
    negative_count = 0
    neutral_count = 0
    for text_value in text_values:
        positive_matches = sum(1 for word in POSITIVE_WORDS if word in text_value)
        negative_matches = sum(1 for word in NEGATIVE_WORDS if word in text_value)

        if positive_matches > negative_matches:
            positive_count += 1
        elif negative_matches > positive_matches:
            negative_count += 1
        else:
            neutral_count += 1

    return positive_count, negative_count, neutral_count


def _count_emotion_labels(tweets_dataframe):
    emotion_values = tweets_dataframe["emotion"].fillna("neutral").astype(str).str.lower()
    positive_emotions = {"joy", "trust", "anticipation", "surprise"}
    negative_emotions = {"anger", "sadness", "fear"}

    positive_count = emotion_values.isin(positive_emotions).sum()
    negative_count = emotion_values.isin(negative_emotions).sum()
    neutral_count = len(emotion_values) - positive_count - negative_count

    return int(positive_count), int(negative_count), int(neutral_count)


def create_sentiment_semaforo():
    """Return the interactive sentiment traffic-light KPI figure."""
    tweets_dataframe = load_clean_tweets()
    positive_count, negative_count, neutral_count = analizar_sentimientos(tweets_dataframe)

    positions = [1, 2, 3]
    colors = ["#EF4444", "#F59E0B", "#10B981"]
    labels = ["Negativo", "Neutral", "Positivo"]
    counts = [negative_count, neutral_count, positive_count]
    hover_templates = [
        f"<b>{label.upper()}</b><br>"
        f"<span style='font-size:15px; font-weight:bold;'>{count:,} tweets</span>"
        "<extra></extra>"
        for label, count in zip(labels, counts)
    ]

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=positions,
            y=[1.1, 1.1, 1.1],
            mode="markers",
            hovertemplate=hover_templates,
            marker=dict(
                size=75,
                color=colors,
                line=dict(color="#FFFFFF", width=4),
                opacity=1.0,
            ),
        )
    )

    for position, label in zip(positions, labels):
        figure.add_annotation(
            x=position,
            y=0.65,
            text=f"<b>{label}</b>",
            showarrow=False,
            font=dict(size=14, color=MUTED_TEXT, family="Arial Black"),
            align="center",
        )

    figure.update_layout(
        title=dict(
            text="Indice de Sentimientos en Twitter",
            x=0.5,
            y=0.92,
            xanchor="center",
            font=dict(size=18, color=CHART_TEXT, family="Arial"),
        ),
        width=400,
        height=220,
        paper_bgcolor=CHART_BACKGROUND,
        plot_bgcolor=CHART_BACKGROUND,
        margin=dict(l=20, r=20, t=45, b=25),
        xaxis=dict(visible=False, range=[0.3, 3.7]),
        yaxis=dict(visible=False, range=[0.3, 1.7]),
        showlegend=False,
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=13,
            font_color="#FFFFFF",
            font_family="Arial",
            bordercolor="#475569",
        ),
    )

    return figure


if __name__ == "__main__":
    sentiment_figure = create_sentiment_semaforo()
    sentiment_figure.show(config={"displayModeBar": False})
