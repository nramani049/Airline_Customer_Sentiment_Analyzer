"""
modules/sentiment.py

VADER sentiment analyzer module for customer reviews polarity scoring.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(review):
    """
    Analyzes single review text and returns sentiment classification and compound score.
    """
    if not isinstance(review, str) or not review.strip():
        return "Neutral", 0.0

    scores = analyzer.polarity_scores(review)
    compound_score = scores["compound"]

    # VADER standard thresholds
    if compound_score >= 0.05:
        sentiment = "Positive"
    elif compound_score <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return sentiment, round(compound_score, 4)


def analyze_dataframe(df):
    """
    Analyzes feedback column in DataFrame and appends 'sentiment' and 'compound_score' columns.
    """
    analyzed_df = df.copy()

    sentiments = []
    compound_scores = []

    for text in analyzed_df["feedback"]:
        sentiment, score = analyze_sentiment(text)
        sentiments.append(sentiment)
        compound_scores.append(score)

    analyzed_df["sentiment"] = sentiments
    analyzed_df["compound_score"] = compound_scores

    return analyzed_df
