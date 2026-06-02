# -*- coding: utf-8 -*-
"""Top 10 countries chart for Fan Pulse."""

import plotly.graph_objects as go

from pulse_data import format_compact_number, get_valid_countries, load_clean_tweets


def create_top_countries():
    """Return a bar chart with the ten countries that have the most tweets."""
    tweets_dataframe = load_clean_tweets()
    countries = get_valid_countries(tweets_dataframe)
    top_countries = countries.value_counts().head(10).reset_index()
    top_countries.columns = ["Pais", "Tweets"]
    top_countries["Tweets_fmt"] = top_countries["Tweets"].apply(format_compact_number)

    red_palette = ["#FF6B6B", "#E74C3C", "#C0392B", "#A93226", "#922B21", "#7B241C", "#641E16", "#4A0E0A"]
    marker_colors = [red_palette[index % len(red_palette)] for index in range(len(top_countries))]

    figure = go.Figure(
        go.Bar(
            x=top_countries["Tweets"],
            y=top_countries["Pais"],
            orientation="h",
            marker_color=marker_colors,
            text=top_countries["Tweets_fmt"],
            textposition="outside",
            textfont=dict(color="#8B0000", size=12),
        )
    )
    figure.update_layout(
        title=dict(
            text="TOP 10 PAISES POR NUMERO DE TWEETS",
            font=dict(color="#8B0000", size=18),
        ),
        xaxis_title=dict(text="Numero de Tweets", font=dict(color="#C0392B")),
        yaxis_title=dict(text="Pais", font=dict(color="#C0392B")),
        height=500,
        width=700,
        yaxis=dict(categoryorder="total ascending"),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    figure.update_traces(marker=dict(line=dict(width=0)))

    return figure


if __name__ == "__main__":
    countries_figure = create_top_countries()
    countries_figure.show(config={"displayModeBar": True})
