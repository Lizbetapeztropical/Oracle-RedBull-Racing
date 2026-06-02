# -*- coding: utf-8 -*-
"""Interactive emotion map for Fan Pulse."""

import numpy as np
import plotly.graph_objects as go

from pulse_data import load_country_emotions, load_tweets_with_emotions


EMOTION_LIST = ["joy", "neutral", "anger", "trust", "sadness", "anticipation", "surprise", "fear"]
EMOTION_COLORS = {
    "joy": "#ba1313",
    "trust": "#3498db",
    "anticipation": "#f39c12",
    "surprise": "#e67e22",
    "sadness": "#95a5a6",
    "fear": "#9b59b6",
    "anger": "#e74c3c",
    "neutral": "#031e48",
}
COUNTRY_COORDS = {
    "United Kingdom": {"lat": 51.5074, "lon": -0.1278},
    "United States": {"lat": 37.0902, "lon": -95.7129},
    "Italy": {"lat": 41.8719, "lon": 12.5674},
    "France": {"lat": 46.2276, "lon": 2.2137},
    "Spain": {"lat": 40.4637, "lon": -3.7492},
    "Germany": {"lat": 51.1657, "lon": 10.4515},
    "India": {"lat": 20.5937, "lon": 78.9629},
    "Australia": {"lat": -25.2744, "lon": 133.7751},
    "Canada": {"lat": 56.1304, "lon": -106.3468},
    "Brazil": {"lat": -14.2350, "lon": -51.9253},
    "Netherlands": {"lat": 52.1326, "lon": 5.2913},
    "Mexico": {"lat": 23.6345, "lon": -102.5528},
    "Japan": {"lat": 36.2048, "lon": 138.2529},
    "South Africa": {"lat": -30.5595, "lon": 22.9375},
    "Ireland": {"lat": 53.1424, "lon": -7.6921},
    "Argentina": {"lat": -38.4161, "lon": -63.6167},
    "Nigeria": {"lat": 9.0820, "lon": 8.6753},
    "Kenya": {"lat": -1.2864, "lon": 36.8172},
    "Egypt": {"lat": 26.8206, "lon": 30.8025},
    "UAE": {"lat": 23.4241, "lon": 53.8478},
    "Saudi Arabia": {"lat": 23.8859, "lon": 45.0792},
    "Singapore": {"lat": 1.3521, "lon": 103.8198},
    "Malaysia": {"lat": 4.2105, "lon": 101.9758},
    "Indonesia": {"lat": -0.7893, "lon": 113.9213},
    "Philippines": {"lat": 12.8797, "lon": 121.7740},
    "Belgium": {"lat": 50.8503, "lon": 4.3517},
    "Austria": {"lat": 47.5162, "lon": 14.5501},
    "Switzerland": {"lat": 46.8182, "lon": 8.2275},
    "Portugal": {"lat": 39.3999, "lon": -8.2245},
    "Sweden": {"lat": 60.1282, "lon": 18.6435},
    "Denmark": {"lat": 56.2639, "lon": 9.5018},
    "Norway": {"lat": 60.4720, "lon": 8.4689},
    "Poland": {"lat": 51.9194, "lon": 19.1451},
    "Greece": {"lat": 39.0742, "lon": 21.8243},
}


def create_emotion_map():
    """Return an inline Plotly map of dominant emotion by country."""
    country_emotions = load_country_emotions()
    tweets_with_emotions = load_tweets_with_emotions()
    map_rows = _build_map_rows(country_emotions, tweets_with_emotions)

    figure = go.Figure()
    if not map_rows:
        return _create_empty_map(figure)

    marker_sizes = [np.log1p(country_data["total_tweets"]) * 12 for country_data in map_rows]
    dominant_emotions = [country_data["dominant"] for country_data in map_rows]

    figure.add_trace(
        go.Scattergeo(
            lon=[country_data["lon"] for country_data in map_rows],
            lat=[country_data["lat"] for country_data in map_rows],
            text=[_build_hover_text(country_data) for country_data in map_rows],
            mode="markers",
            marker=dict(
                size=marker_sizes,
                color=[EMOTION_COLORS.get(emotion, "#bdc3c7") for emotion in dominant_emotions],
                opacity=0.8,
                line=dict(width=1, color="white"),
                sizemode="area",
                sizeref=2 * max(marker_sizes) / (40**2),
                sizemin=6,
            ),
            hovertemplate="%{text}<extra></extra>",
            showlegend=False,
        )
    )

    _apply_map_layout(figure)
    _add_emotion_legend(figure, dominant_emotions)
    return figure


def _build_map_rows(country_emotions, tweets_with_emotions):
    map_rows = []
    countries = country_emotions["country"].dropna().astype(str).unique().tolist()

    for country in countries:
        if country not in COUNTRY_COORDS:
            continue

        country_tweets = tweets_with_emotions[tweets_with_emotions["country"] == country]
        emotion_summary = _summarize_country_emotions(country, country_emotions, country_tweets)
        coordinates = COUNTRY_COORDS[country]
        map_rows.append(
            {
                "country": country,
                "lat": coordinates["lat"],
                "lon": coordinates["lon"],
                "total_tweets": emotion_summary["total_tweets"],
                "dominant": emotion_summary["dominant"],
                "dominant_pct": emotion_summary["dominant_pct"],
                "percentages": emotion_summary["percentages"],
            }
        )

    return map_rows


def _summarize_country_emotions(country, country_emotions, country_tweets):
    if country_tweets.empty:
        country_row = country_emotions[country_emotions["country"] == country].iloc[0]
        percentages = {emotion: 0 for emotion in EMOTION_LIST}
        percentages[country_row["emotion"]] = 100
        return {
            "total_tweets": int(country_row["tweets"]),
            "dominant": country_row["emotion"],
            "dominant_pct": 100,
            "percentages": percentages,
        }

    total_tweets = len(country_tweets)
    emotion_counts = country_tweets["emotion"].value_counts().to_dict()
    percentages = {
        emotion: round((emotion_counts.get(emotion, 0) / total_tweets) * 100, 1)
        for emotion in EMOTION_LIST
    }
    sorted_percentages = dict(sorted(percentages.items(), key=lambda item: item[1], reverse=True))
    dominant_emotion = next(iter(sorted_percentages), "neutral")

    return {
        "total_tweets": total_tweets,
        "dominant": dominant_emotion,
        "dominant_pct": sorted_percentages.get(dominant_emotion, 0),
        "percentages": sorted_percentages,
    }


def _build_hover_text(country_data):
    emotion_lines = [
        f"{emotion}: {percentage:.0f}%"
        for emotion, percentage in country_data["percentages"].items()
        if percentage > 0
    ]
    emotions_text = "<br>".join(emotion_lines)

    return (
        f"<b>{country_data['country']}</b><br>"
        f"Total tweets: {country_data['total_tweets']:,}<br>"
        f"Emocion dominante: {country_data['dominant']} "
        f"({country_data['dominant_pct']:.0f}%)<br><br>"
        f"Desglose de emociones:<br>{emotions_text}"
    )


def _apply_map_layout(figure):
    figure.update_layout(
        title=dict(text="Mapa de Emociones F1", x=0.5, font=dict(size=24, color="#333333")),
        geo=dict(
            projection_type="natural earth",
            showland=True,
            landcolor="rgb(243, 243, 243)",
            coastlinecolor="rgb(204, 204, 204)",
            showocean=True,
            oceancolor="rgb(230, 245, 255)",
            showcountries=True,
            countrycolor="rgb(204, 204, 204)",
            showframe=False,
            lataxis_range=[-60, 80],
            lonaxis_range=[-140, 180],
        ),
        height=700,
        margin=dict(l=0, r=0, t=50, b=0),
    )


def _add_emotion_legend(figure, dominant_emotions):
    for emotion, color in EMOTION_COLORS.items():
        if emotion not in dominant_emotions:
            continue

        figure.add_trace(
            go.Scattergeo(
                lon=[None],
                lat=[None],
                mode="markers",
                marker=dict(size=10, color=color),
                name=emotion.capitalize(),
                showlegend=True,
            )
        )


def _create_empty_map(figure):
    _apply_map_layout(figure)
    figure.add_annotation(
        text="No hay paises con coordenadas para mostrar.",
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=16, color="#333333"),
    )
    return figure


if __name__ == "__main__":
    emotion_map = create_emotion_map()
    emotion_map.show(config={"displayModeBar": True})
