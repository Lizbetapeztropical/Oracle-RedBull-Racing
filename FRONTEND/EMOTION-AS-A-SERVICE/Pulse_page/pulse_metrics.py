# -*- coding: utf-8 -*-
"""Daily tweets and users charts for Fan Pulse."""

import pandas as pd
import plotly.graph_objects as go

from pulse_data import (
    has_temporal_columns,
    load_clean_tweets,
    load_full_tweet_metrics,
    load_notebook_daily_tweet_counts,
    normalize_month_filter,
)


def get_data():
    """Return the cleaned tweets dataset used by the temporal charts."""
    return load_clean_tweets()


def plot_combined_daily_metrics(df_to_plot, year=2021):
    """Return daily tweet and unique-user counts for a specific year."""
    if not has_temporal_columns(df_to_plot):
        return _create_temporal_unavailable_figure()

    filtered_dataframe = _filter_tweets(df_to_plot, year=year)
    return _build_combined_daily_figure(filtered_dataframe, year=year)


def plot_combined_daily_metrics_filtered(year, month=None, hour_range=(0, 23)):
    """Return daily tweets/users after year, month, and hour filters."""
    tweets_dataframe = load_full_tweet_metrics()
    if not has_temporal_columns(tweets_dataframe):
        return _build_notebook_daily_tweet_figure(year=year, month=month)

    filtered_dataframe = _filter_tweets(
        tweets_dataframe,
        year=year,
        month=month,
        hour_range=hour_range,
    )
    return _build_combined_daily_figure(filtered_dataframe, year=year)


def plot_tweets_per_day(df_to_plot, year=2021):
    """Return a daily tweet-count chart for a specific year."""
    if not has_temporal_columns(df_to_plot):
        return _create_temporal_unavailable_figure()

    filtered_dataframe = _filter_tweets(df_to_plot, year=year)
    if filtered_dataframe.empty:
        return None

    tweet_counts = _count_tweets_by_day(filtered_dataframe)
    if tweet_counts.empty:
        return None

    figure = go.Figure(
        go.Scatter(
            x=tweet_counts["date"],
            y=tweet_counts["tweet_count"],
            mode="lines+markers",
            name="Tweets",
            marker_color="dodgerblue",
            line=dict(width=2),
        )
    )
    _apply_temporal_layout(figure, filtered_dataframe, title=f"Tweets por Dia ({year})")
    figure.update_layout(yaxis_title="Numero de Tweets")
    return figure


def plot_users_per_day(df_to_plot, year=2021):
    """Return a daily unique-user chart for a specific year."""
    if not has_temporal_columns(df_to_plot):
        return _create_temporal_unavailable_figure()

    filtered_dataframe = _filter_tweets(df_to_plot, year=year)
    if filtered_dataframe.empty:
        return None

    user_counts = _count_users_by_day(filtered_dataframe)
    if user_counts.empty:
        return None

    figure = go.Figure(
        go.Scatter(
            x=user_counts["date"],
            y=user_counts["unique_users"],
            mode="lines+markers",
            name="Usuarios Unicos",
            marker_color="#2ecc71",
            line=dict(width=2, color="#2ecc71"),
        )
    )
    _apply_temporal_layout(figure, filtered_dataframe, title=f"Usuarios Unicos por Dia ({year})")
    figure.update_layout(yaxis_title="Numero de Usuarios Unicos")
    return figure


def _filter_tweets(tweets_dataframe, year, month=None, hour_range=None):
    filtered_dataframe = tweets_dataframe.copy()
    filtered_dataframe["year"] = pd.to_numeric(filtered_dataframe["year"], errors="coerce")
    filtered_dataframe["month"] = pd.to_numeric(filtered_dataframe["month"], errors="coerce")
    filtered_dataframe["hour"] = pd.to_numeric(filtered_dataframe["hour"], errors="coerce")

    filtered_dataframe = filtered_dataframe[filtered_dataframe["year"] == int(year)]

    month_number = normalize_month_filter(month)
    if month_number is not None:
        filtered_dataframe = filtered_dataframe[filtered_dataframe["month"] == month_number]

    if hour_range is not None:
        start_hour, end_hour = hour_range
        filtered_dataframe = filtered_dataframe[
            filtered_dataframe["hour"].between(int(start_hour), int(end_hour), inclusive="both")
        ]

    return filtered_dataframe


def _build_combined_daily_figure(filtered_dataframe, year):
    if filtered_dataframe.empty:
        return None

    tweet_counts = _count_tweets_by_day(filtered_dataframe)
    user_counts = _count_users_by_day(filtered_dataframe)
    if tweet_counts.empty or user_counts.empty:
        return None

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=tweet_counts["date"],
            y=tweet_counts["tweet_count"],
            mode="lines+markers",
            name="Tweets por dia",
            marker_color="dodgerblue",
            line=dict(width=2),
        )
    )
    figure.add_trace(
        go.Scatter(
            x=user_counts["date"],
            y=user_counts["unique_users"],
            mode="lines+markers",
            name="Usuarios unicos por dia",
            marker_color="#e74c3c",
            line=dict(width=2, color="#e74c3c"),
        )
    )
    _apply_temporal_layout(figure, filtered_dataframe, title=f"Tweets y Usuarios Unicos por Dia ({year})")
    return figure


def _build_notebook_daily_tweet_figure(year, month=None):
    daily_counts = load_notebook_daily_tweet_counts()
    if daily_counts.empty:
        return _create_temporal_unavailable_figure()

    filtered_daily_counts = daily_counts[daily_counts["date"].dt.year == int(year)].copy()
    month_number = normalize_month_filter(month)
    if month_number is not None:
        filtered_daily_counts = filtered_daily_counts[
            filtered_daily_counts["date"].dt.month == month_number
        ]

    if filtered_daily_counts.empty:
        return None

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=filtered_daily_counts["date"],
            y=filtered_daily_counts["tweet_count"],
            mode="lines+markers",
            name="Tweets por dia",
            marker_color="dodgerblue",
            line=dict(width=2),
        )
    )
    _apply_notebook_temporal_layout(
        figure,
        filtered_daily_counts,
        title=f"Tweets por Dia ({year})",
    )
    return figure


def _count_tweets_by_day(filtered_dataframe):
    prepared_dataframe = _prepare_dates(filtered_dataframe)
    tweet_counts = prepared_dataframe["tweet_date"].value_counts().reset_index()
    tweet_counts.columns = ["date", "tweet_count"]
    tweet_counts["date"] = pd.to_datetime(tweet_counts["date"], errors="coerce")
    return tweet_counts.sort_values("date", ascending=True)


def _count_users_by_day(filtered_dataframe):
    prepared_dataframe = _prepare_dates(filtered_dataframe)
    if "user_name" in prepared_dataframe.columns:
        user_counts = prepared_dataframe.groupby("tweet_date")["user_name"].nunique().reset_index()
    else:
        user_counts = prepared_dataframe.groupby("tweet_date").size().reset_index(name="user_name")

    user_counts.columns = ["date", "unique_users"]
    user_counts["date"] = pd.to_datetime(user_counts["date"], errors="coerce")
    return user_counts.sort_values("date", ascending=True)


def _prepare_dates(filtered_dataframe):
    prepared_dataframe = filtered_dataframe.copy()
    prepared_dataframe["date"] = pd.to_datetime(prepared_dataframe["date"], errors="coerce")
    prepared_dataframe = prepared_dataframe.dropna(subset=["date"])
    prepared_dataframe["tweet_date"] = prepared_dataframe["date"].dt.date
    return prepared_dataframe


def _apply_temporal_layout(figure, filtered_dataframe, title):
    prepared_dataframe = _prepare_dates(filtered_dataframe)
    if prepared_dataframe.empty:
        return

    min_date = prepared_dataframe["tweet_date"].min().strftime("%d/%m/%Y")
    max_date = prepared_dataframe["tweet_date"].max().strftime("%d/%m/%Y")

    figure.update_layout(
        title=dict(text=f"{title}<br><sub>{min_date} - {max_date}</sub>", x=0.5, font=dict(size=18)),
        template="plotly_white",
        xaxis_title="Fecha",
        yaxis_title="Cantidad",
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#dddddd",
            borderwidth=1,
        ),
        hovermode="x unified",
        width=900,
        height=500,
        margin=dict(l=50, r=50, t=80, b=50),
    )


def _apply_notebook_temporal_layout(figure, filtered_daily_counts, title):
    min_date = filtered_daily_counts["date"].min().strftime("%d/%m/%Y")
    max_date = filtered_daily_counts["date"].max().strftime("%d/%m/%Y")

    figure.update_layout(
        title=dict(
            text=(
                f"{title}<br><sub>{min_date} - {max_date} | "
                "usuarios/hora requieren F1_tweets.csv</sub>"
            ),
            x=0.5,
            font=dict(size=18),
        ),
        template="plotly_white",
        xaxis_title="Fecha",
        yaxis_title="Numero de Tweets",
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#dddddd",
            borderwidth=1,
        ),
        hovermode="x unified",
        width=900,
        height=500,
        margin=dict(l=50, r=50, t=80, b=50),
    )


def _create_temporal_unavailable_figure():
    figure = go.Figure()
    figure.add_annotation(
        text="El dataset disponible no incluye fecha, hora ni usuario para graficar esta sección.",
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=16, color="#333333"),
    )
    figure.update_layout(
        template="plotly_white",
        height=500,
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return figure


if __name__ == "__main__":
    combined_figure = plot_combined_daily_metrics_filtered(year=2021)
    if combined_figure:
        combined_figure.show(config={"displayModeBar": True})
