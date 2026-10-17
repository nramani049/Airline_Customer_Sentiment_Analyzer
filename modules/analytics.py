"""
modules/analytics.py

Analytics module for computing KPI metrics, sentiment distributions,
airline breakdowns, chronological summaries, and multi-criteria filters.
"""

import pandas as pd


def get_theme_colors(theme_name="dark"):
    """
    Returns color palette configuration dictionary for the specified theme.
    """
    if theme_name == "light":
        return {
            "name": "light",
            "background": "#F7F8FC",
            "sidebar_background": "#FFFFFF",
            "card_background": "#FFFFFF",
            "card_border": "#E3E7EF",
            "border": "#E3E7EF",
            "text": "#172033",
            "secondary_text": "#5F6B7A",
            "muted_text": "#778196",
            "accent": "#6D3DF5",          # Primary purple
            "accent_hover": "#5B2FE0",    # Purple hover
            "positive": "#159A63",        # Green
            "negative": "#DC4545",        # Red
            "neutral": "#778196",         # Grey
            "grid": "#E3E7EF",
            "chart_bg": "#FFFFFF",
            "input_bg": "#FFFFFF",
            "banner_bg": "#F0EEFC",
            "banner_border": "#D8D0F8",
            "banner_text": "#43288C",
            "tag_bg": "rgba(109, 61, 245, 0.10)",
            "tag_border": "#D8D0F8",
        }
    else:  # dark mode (default)
        return {
            "name": "dark",
            "background": "#0F1117",          # Deep charcoal / dark
            "sidebar_background": "#171A23",  # Sidebar dark
            "card_background": "#191D28",     # Card dark
            "card_border": "#2B3040",
            "border": "#2B3040",
            "text": "#F4F5FA",
            "secondary_text": "#B7BDCB",
            "muted_text": "#929AAC",
            "accent": "#9270FF",              # Bright purple / violet
            "accent_hover": "#A48AFF",
            "positive": "#35C98A",            # Bright green
            "negative": "#FF6666",            # Bright red
            "neutral": "#A0A7B5",             # Muted grey
            "grid": "#2B3040",
            "chart_bg": "#191D28",
            "input_bg": "#171A23",
            "banner_bg": "#1F1A3A",
            "banner_border": "#3E326B",
            "banner_text": "#D4C8FC",
            "tag_bg": "rgba(146, 112, 255, 0.18)",
            "tag_border": "#3E326B",
        }


def calculate_kpis(df):
    """
    Calculates total, positive, negative, and neutral review counts and percentages.
    """
    if df is None or len(df) == 0:
        return {
            "total": 0,
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "pos_percent": 0.0,
            "neg_percent": 0.0,
            "neu_percent": 0.0,
        }

    total = len(df)
    positive = int((df["sentiment"] == "Positive").sum())
    negative = int((df["sentiment"] == "Negative").sum())
    neutral = int((df["sentiment"] == "Neutral").sum())

    # Guarantee relationship: total = positive + negative + neutral
    pos_percent = round((positive / total) * 100, 1) if total > 0 else 0.0
    neg_percent = round((negative / total) * 100, 1) if total > 0 else 0.0
    neu_percent = round((neutral / total) * 100, 1) if total > 0 else 0.0

    return {
        "total": total,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "pos_percent": pos_percent,
        "neg_percent": neg_percent,
        "neu_percent": neu_percent,
    }


def get_sentiment_distribution(df):
    """
    Generates DataFrame containing overall sentiment counts and percentages.
    """
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=["sentiment", "count", "percentage"])

    kpis = calculate_kpis(df)
    data = [
        {"sentiment": "Positive", "count": kpis["positive"], "percentage": kpis["pos_percent"]},
        {"sentiment": "Negative", "count": kpis["negative"], "percentage": kpis["neg_percent"]},
        {"sentiment": "Neutral", "count": kpis["neutral"], "percentage": kpis["neu_percent"]},
    ]
    return pd.DataFrame(data)


def get_airline_sentiment_summary(df):
    """
    Aggregates review counts grouped by airline and sentiment.
    """
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=["airline", "sentiment", "count"])

    summary = (
        df.groupby(["airline", "sentiment"], observed=False)
        .size()
        .reset_index(name="count")
    )
    return summary


def get_date_sentiment_summary(df, frequency="monthly"):
    """
    Aggregates sentiment counts chronologically by month or day.
    """
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=["date", "sentiment", "count"])

    temp_df = df.copy()

    if frequency == "monthly":
        temp_df["date"] = pd.to_datetime(temp_df["date"]).dt.strftime("%Y-%m")
    else:
        temp_df["date"] = pd.to_datetime(temp_df["date"]).dt.strftime("%Y-%m-%d")

    summary = (
        temp_df.groupby(["date", "sentiment"], observed=False)
        .size()
        .reset_index(name="count")
        .sort_values(by="date")
    )
    return summary


def filter_data(df, selected_airlines=None, selected_sentiments=None, start_date=None, end_date=None):
    """
    Filters DataFrame based on airline, sentiment, and date range criteria.
    """
    if df is None or len(df) == 0:
        return df

    filtered_df = df

    # 1. Filter by Airlines
    if selected_airlines is not None and len(selected_airlines) > 0:
        filtered_df = filtered_df[filtered_df["airline"].isin(selected_airlines)]

    # 2. Filter by Sentiments
    if selected_sentiments is not None and len(selected_sentiments) > 0:
        filtered_df = filtered_df[filtered_df["sentiment"].isin(selected_sentiments)]

    # 3. Filter by Date range (Fast ISO string comparison for 'YYYY-MM-DD')
    if start_date is not None and end_date is not None:
        start_str = start_date.strftime("%Y-%m-%d") if hasattr(start_date, "strftime") else str(start_date)
        end_str = end_date.strftime("%Y-%m-%d") if hasattr(end_date, "strftime") else str(end_date)
        filtered_df = filtered_df[(filtered_df["date"] >= start_str) & (filtered_df["date"] <= end_str)]

    return filtered_df
