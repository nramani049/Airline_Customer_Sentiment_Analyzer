"""
modules/analytics.py

Yeh module analyzed reviews ke data par calculations karta hai jaise KPIs,
airline-wise sentiment counts, date-wise trends, theme colors aur filter operations.
"""

import pandas as pd


def get_theme_colors(theme_name="dark"):
    """
    Selected theme (dark ya light) ke hisaab se centralized colors dictionary return karta hai.
    
    Hinglish explanation:
    Yeh function dark mode aur light mode ke liye consistent, high-contrast color palette
    provide karta hai jo dashboard, cards, sidebar, table aur Plotly charts me use hoti hai.
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
    Total, Positive, Negative aur Neutral reviews count calculate karta hai.
    
    Hinglish explanation:
    Yeh function filtered ya full dataset me se Positive, Negative aur Neutral
    reviews ki ginti karke total summary KPI dictionary return karta hai.
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
    Overall sentiment distribution ka DataFrame banata hai chart ke liye.
    
    Hinglish explanation:
    Yeh function bar chart ya pie chart ke liye Positive, Negative aur Neutral
    ke counts aur percentages ka clean DataFrame banata hai.
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
    Har airline ke Positive, Negative aur Neutral reviews count nikalta hai.
    
    Hinglish explanation:
    Yeh function airline aur sentiment ke according data ko group karta hai
    taaki hum grouped bar chart me airlines ka comparison dikha sakein.
    """
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=["airline", "sentiment", "count"])

    # Group by airline and sentiment, counting occurrences
    summary = (
        df.groupby(["airline", "sentiment"], observed=False)
        .size()
        .reset_index(name="count")
    )
    return summary


def get_date_sentiment_summary(df, frequency="monthly"):
    """
    Date-wise ya Monthly sentiment summary nikalta hai aur chronologically sort karta hai.
    
    Hinglish explanation:
    Yeh function reviews ko actual dates ya months ke hisaab se group karke
    chronological trend line chart ke liye structured DataFrame return karta hai.
    """
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=["date", "sentiment", "count"])

    temp_df = df.copy()

    if frequency == "monthly":
        # Group by YYYY-MM formatted string
        temp_df["date"] = pd.to_datetime(temp_df["date"]).dt.strftime("%Y-%m")
    else:
        # Group by exact date YYYY-MM-DD
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
    Airlines, sentiments aur date range ke basis par DataFrame ko filter karta hai.
    
    Hinglish explanation:
    Yeh function user ke sidebar selections (airline, sentiment, dates) ke according
    fast conditions lagakar matching reviews ka filtered DataFrame return karta hai.
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
