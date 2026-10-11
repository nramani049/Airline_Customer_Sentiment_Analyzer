"""
modules/analytics.py

Yeh module analyzed reviews ke data par calculations karta hai jaise KPIs,
airline-wise sentiment counts, date-wise trends aur filter operations.
"""

import pandas as pd


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
        df.groupby(["airline", "sentiment"])
        .size()
        .reset_index(name="count")
    )
    return summary


def get_date_sentiment_summary(df):
    """
    Date-wise sentiment trend nikalta hai aur dates ko chronologically sort karta hai.
    
    Hinglish explanation:
    Yeh function dates ke according reviews ko group karta hai aur unhe chronological
    order me sort karta hai taaki line chart me sentiment trend dikhe.
    """
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=["date", "sentiment", "count"])

    # Date column ko date type me convert karke sort karte hain
    temp_df = df.copy()
    temp_df["date"] = pd.to_datetime(temp_df["date"]).dt.strftime("%Y-%m-%d")

    summary = (
        temp_df.groupby(["date", "sentiment"])
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
    Pandas conditions lagakar matching reviews ka filtered DataFrame return karta hai.
    """
    if df is None or len(df) == 0:
        return df

    filtered_df = df.copy()

    # 1. Filter by Airlines
    if selected_airlines:
        filtered_df = filtered_df[filtered_df["airline"].isin(selected_airlines)]

    # 2. Filter by Sentiments
    if selected_sentiments:
        filtered_df = filtered_df[filtered_df["sentiment"].isin(selected_sentiments)]

    # 3. Filter by Date range
    if start_date is not None and end_date is not None:
        # Convert date column to datetime for accurate comparison
        date_series = pd.to_datetime(filtered_df["date"])
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        filtered_df = filtered_df[(date_series >= start) & (date_series <= end)]

    return filtered_df
