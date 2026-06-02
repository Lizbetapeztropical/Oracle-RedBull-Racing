# -*- coding: utf-8 -*-
"""Shared data access helpers for the Fan Pulse dashboard."""

import json
import re
from functools import lru_cache
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[3]
TWEETS_DIR = REPO_ROOT / "BACKEND" / "EMOTION-AS-A-SERVICE" / "model" / "DATA" / "Tweets"

CLEAN_TWEETS_PATH = TWEETS_DIR / "tweets_cleaned.csv"
RAW_TWEETS_PATH = TWEETS_DIR / "F1_tweets.csv"
TWEETS_WITH_EMOTIONS_PATH = TWEETS_DIR / "tweets_with_emotions.csv"
COUNTRY_EMOTIONS_PATH = TWEETS_DIR / "country_emotions_enhanced.csv"
TWEETS_NOTEBOOK_PATH = TWEETS_DIR / "tweets_graphs.ipynb"

TEXT_COLUMN_CANDIDATES = ("clean_text", "tweet_clean", "text", "tweet")
COUNTRY_COLUMN_CANDIDATES = ("user_location_normalized", "country", "user_location")
USER_COLUMN_CANDIDATES = ("user_name", "username", "user_id", "author_id")
SOURCE_COLUMN_CANDIDATES = ("source", "tweet_source")
TEMPORAL_COLUMNS = {"date", "year", "month", "hour"}
REQUIRED_CLEAN_TWEET_COLUMNS = {"clean_text", "user_location_normalized"}
REQUIRED_RAW_TWEET_COLUMNS = {"user_name", "date", "text", "source"}
REQUIRED_TWEETS_WITH_EMOTIONS_COLUMNS = {"country", "tweet_clean", "emotion", "polarity"}
REQUIRED_COUNTRY_EMOTION_COLUMNS = {"country", "emotion", "tweets"}

# The full F1 tweet file is not committed in this workspace. These values come
# from the preserved notebook output for F1_tweets.csv and the expected Fan Pulse
# source metrics, and are used only while the full CSV is absent.
FULL_TWEET_COUNT_FROM_NOTEBOOK = 580_909
FULL_USER_COUNT_FROM_SOURCE = 119_000

INVALID_COUNTRY_VALUES = {"", "unknown", "other", "others", "nan", "none"}
MONTH_NAME_TO_NUMBER = {
    "Enero": 1,
    "Febrero": 2,
    "Marzo": 3,
    "Abril": 4,
    "Mayo": 5,
    "Junio": 6,
    "Julio": 7,
    "Agosto": 8,
    "Septiembre": 9,
    "Octubre": 10,
    "Noviembre": 11,
    "Diciembre": 12,
}


def format_compact_number(value):
    """Format large integer-like values for KPI cards."""
    numeric_value = int(value)

    if numeric_value >= 1_000_000:
        return f"{numeric_value / 1_000_000:.1f}M"
    if numeric_value >= 1_000:
        return f"{numeric_value / 1_000:.1f}K"
    return str(numeric_value)


def get_valid_countries(tweets_dataframe, country_column="user_location_normalized"):
    """Return non-empty, known countries from the normalized country column."""
    resolved_country_column = resolve_country_column(tweets_dataframe, preferred_column=country_column)
    countries = tweets_dataframe[resolved_country_column].dropna().astype(str).str.strip()
    return countries[~countries.str.lower().isin(INVALID_COUNTRY_VALUES)]


def get_available_years():
    """Return sorted years available in the cleaned tweet dataset."""
    full_tweets_dataframe = load_full_tweet_metrics()
    if full_tweets_dataframe is not None and "year" in full_tweets_dataframe.columns:
        years = pd.to_numeric(full_tweets_dataframe["year"], errors="coerce").dropna().astype(int)
        return sorted(years.unique().tolist())

    daily_counts = load_notebook_daily_tweet_counts()
    if not daily_counts.empty:
        return sorted(daily_counts["date"].dt.year.unique().tolist())

    tweets_dataframe = load_clean_tweets()
    if "year" in tweets_dataframe.columns:
        years = pd.to_numeric(tweets_dataframe["year"], errors="coerce").dropna().astype(int)
        return sorted(years.unique().tolist())

    return []


def get_source_counts(limit=4):
    """Return the most common tweet sources as a Series."""
    tweets_dataframe = load_clean_tweets()
    source_column = resolve_first_existing_column(tweets_dataframe, SOURCE_COLUMN_CANDIDATES)
    if source_column is None:
        return pd.Series({"Fuente no registrada": len(tweets_dataframe)})

    sources = tweets_dataframe[source_column].fillna("Unknown").astype(str).str.strip()
    source_counts = sources.replace("", "Unknown").value_counts()
    return source_counts.head(limit)


def get_text_series(tweets_dataframe):
    """Return the best available tweet text column."""
    text_column = resolve_first_existing_column(tweets_dataframe, TEXT_COLUMN_CANDIDATES)
    if text_column is None:
        return pd.Series(dtype=str)
    return tweets_dataframe[text_column].fillna("").astype(str)


def get_user_count(tweets_dataframe):
    """Return user count when available, otherwise fall back to tweet records."""
    user_column = resolve_first_existing_column(tweets_dataframe, USER_COLUMN_CANDIDATES)
    if user_column is None:
        return len(tweets_dataframe)
    return tweets_dataframe[user_column].nunique()


def get_total_tweet_count():
    """Return total tweets from the full tweet source, not the emotions sample."""
    full_tweets_dataframe = load_full_tweet_metrics()
    if full_tweets_dataframe is not None:
        return len(full_tweets_dataframe)

    return FULL_TWEET_COUNT_FROM_NOTEBOOK


def get_total_user_count():
    """Return unique users from the full tweet source when available."""
    full_tweets_dataframe = load_full_tweet_metrics()
    if full_tweets_dataframe is not None:
        return get_user_count(full_tweets_dataframe)

    return FULL_USER_COUNT_FROM_SOURCE


def has_temporal_columns(tweets_dataframe):
    """Return True when the dataset can support year/month/hour filtering."""
    if tweets_dataframe is None:
        return False
    return TEMPORAL_COLUMNS.issubset(set(tweets_dataframe.columns))


def resolve_country_column(tweets_dataframe, preferred_column=None):
    """Return the best available country column name."""
    candidates = []
    if preferred_column:
        candidates.append(preferred_column)
    candidates.extend(COUNTRY_COLUMN_CANDIDATES)
    country_column = resolve_first_existing_column(tweets_dataframe, candidates)
    if country_column is None:
        raise ValueError("No hay columna de pais disponible en el dataset de Pulse.")
    return country_column


def resolve_first_existing_column(tweets_dataframe, candidates):
    """Return the first column from candidates present in a dataframe."""
    for candidate in candidates:
        if candidate in tweets_dataframe.columns:
            return candidate
    return None


def normalize_month_filter(month):
    """Convert UI month labels to numbers while accepting numeric month input."""
    if month is None:
        return None
    if isinstance(month, str):
        if month in MONTH_NAME_TO_NUMBER:
            return MONTH_NAME_TO_NUMBER[month]
        if month.isdigit():
            return int(month)
        return None
    return int(month)


def load_clean_tweets():
    """Load cleaned tweets, falling back to the available emotion-tagged tweets."""
    return _read_clean_tweets().copy()


def load_full_tweet_metrics():
    """Load the full tweet dataset for KPI metrics when it exists locally."""
    full_tweets_dataframe = _read_full_tweet_metrics()
    if full_tweets_dataframe is None:
        return None
    return full_tweets_dataframe.copy()


def load_notebook_daily_tweet_counts():
    """Load preserved daily tweet counts from the exploratory notebook."""
    return _read_notebook_daily_tweet_counts().copy()


def load_tweets_with_emotions():
    """Load a copy of tweets enriched with emotion labels."""
    return _read_tweets_with_emotions().copy()


def load_country_emotions():
    """Load a copy of country-level dominant emotion data."""
    return _read_country_emotions().copy()


@lru_cache(maxsize=1)
def _read_clean_tweets():
    if CLEAN_TWEETS_PATH.exists():
        return _normalize_clean_tweets(
            _read_required_csv(CLEAN_TWEETS_PATH, REQUIRED_CLEAN_TWEET_COLUMNS)
        )

    if RAW_TWEETS_PATH.exists():
        return _normalize_clean_tweets(
            _read_required_csv(RAW_TWEETS_PATH, REQUIRED_RAW_TWEET_COLUMNS)
        )

    emotion_tweets = _read_tweets_with_emotions()
    return _normalize_emotion_tweets(emotion_tweets)


@lru_cache(maxsize=1)
def _read_full_tweet_metrics():
    if CLEAN_TWEETS_PATH.exists():
        return _normalize_clean_tweets(
            _read_required_csv(CLEAN_TWEETS_PATH, REQUIRED_CLEAN_TWEET_COLUMNS)
        )

    if RAW_TWEETS_PATH.exists():
        return _normalize_clean_tweets(
            _read_required_csv(RAW_TWEETS_PATH, REQUIRED_RAW_TWEET_COLUMNS)
        )

    return None


@lru_cache(maxsize=1)
def _read_tweets_with_emotions():
    return _read_required_csv(TWEETS_WITH_EMOTIONS_PATH, REQUIRED_TWEETS_WITH_EMOTIONS_COLUMNS)


@lru_cache(maxsize=1)
def _read_country_emotions():
    return _read_required_csv(COUNTRY_EMOTIONS_PATH, REQUIRED_COUNTRY_EMOTION_COLUMNS)


@lru_cache(maxsize=1)
def _read_notebook_daily_tweet_counts():
    if not TWEETS_NOTEBOOK_PATH.exists():
        return pd.DataFrame(columns=["date", "tweet_count"])

    notebook = json.loads(TWEETS_NOTEBOOK_PATH.read_text(encoding="utf-8"))
    for cell in notebook.get("cells", []):
        for output in cell.get("outputs", []):
            html_output = output.get("data", {}).get("text/html")
            html_text = _join_notebook_output(html_output)
            if "Tweets per Day" not in html_text:
                continue

            dates = _extract_plotly_array(html_text, "x")
            tweet_counts = _extract_plotly_array(html_text, "y")
            if not dates or not tweet_counts:
                continue

            daily_counts = pd.DataFrame({"date": dates, "tweet_count": tweet_counts})
            daily_counts["date"] = pd.to_datetime(daily_counts["date"], errors="coerce")
            daily_counts["tweet_count"] = pd.to_numeric(
                daily_counts["tweet_count"], errors="coerce"
            )
            daily_counts = daily_counts.dropna(subset=["date", "tweet_count"])
            daily_counts["tweet_count"] = daily_counts["tweet_count"].astype(int)
            return daily_counts.sort_values("date").reset_index(drop=True)

    return pd.DataFrame(columns=["date", "tweet_count"])


def _read_required_csv(file_path, required_columns):
    if not file_path.exists():
        raise FileNotFoundError(f"No se encontro el archivo requerido: {file_path}")

    dataframe = pd.read_csv(file_path, low_memory=False)
    missing_columns = sorted(required_columns - set(dataframe.columns))
    if missing_columns:
        missing_columns_text = ", ".join(missing_columns)
        raise ValueError(f"{file_path.name} no contiene columnas requeridas: {missing_columns_text}")

    return dataframe


def _normalize_clean_tweets(dataframe):
    normalized_dataframe = dataframe.copy()

    if "clean_text" not in normalized_dataframe.columns:
        text_column = resolve_first_existing_column(normalized_dataframe, TEXT_COLUMN_CANDIDATES)
        if text_column:
            normalized_dataframe["clean_text"] = normalized_dataframe[text_column]

    if "user_location_normalized" not in normalized_dataframe.columns:
        country_column = resolve_first_existing_column(normalized_dataframe, COUNTRY_COLUMN_CANDIDATES)
        if country_column:
            normalized_dataframe["user_location_normalized"] = normalized_dataframe[country_column]

    _derive_temporal_columns(normalized_dataframe)
    return normalized_dataframe


def _normalize_emotion_tweets(dataframe):
    normalized_dataframe = dataframe.copy()
    normalized_dataframe["clean_text"] = normalized_dataframe["tweet_clean"]
    normalized_dataframe["user_location_normalized"] = normalized_dataframe["country"]
    return normalized_dataframe


def _derive_temporal_columns(dataframe):
    if "date" not in dataframe.columns:
        return

    dates = pd.to_datetime(dataframe["date"], errors="coerce")
    if "year" not in dataframe.columns:
        dataframe["year"] = dates.dt.year
    if "month" not in dataframe.columns:
        dataframe["month"] = dates.dt.month
    if "hour" not in dataframe.columns:
        dataframe["hour"] = dates.dt.hour


def _join_notebook_output(output_value):
    if isinstance(output_value, list):
        return "".join(output_value)
    if isinstance(output_value, str):
        return output_value
    return ""


def _extract_plotly_array(html_text, field_name):
    match = re.search(rf'"{field_name}":(\[[^\]]*\])', html_text)
    if not match:
        return []
    return json.loads(match.group(1))
