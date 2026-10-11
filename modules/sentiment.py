"""
modules/sentiment.py

Yeh module VADER sentiment analyzer ka use karke customer reviews ka
sentiment (Positive, Negative, Neutral) aur compound score nikalta hai.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# VADER analyzer ko ek baar initialize karte hain taaki baar-baar naya object na banana pade
# VADER: Rule-based sentiment analysis tool jo words ke intensity ke hisaab se score calculate karta hai.
analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(review):
    """
    Ek single review text ko analyze karke uska sentiment label aur compound score return karta hai.
    
    Hinglish explanation:
    Yeh function single review text ko score karta hai aur compound score ke hisaab se
    Positive, Negative ya Neutral label deta hai.
    """
    # Agar review empty, None ya sirf spaces ho, toh usse safely Neutral declare karte hain
    if not isinstance(review, str) or not review.strip():
        return "Neutral", 0.0

    # VADER polarity scores calculate karta hai (pos, neg, neu, compound)
    scores = analyzer.polarity_scores(review)
    compound_score = scores["compound"]

    # VADER standard thresholds:
    # compound >= 0.05  -> Positive
    # compound <= -0.05 -> Negative
    # between -0.05 and 0.05 -> Neutral
    if compound_score >= 0.05:
        sentiment = "Positive"
    elif compound_score <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return sentiment, round(compound_score, 4)


def analyze_dataframe(df):
    """
    Pure DataFrame ke feedback column par sentiment analysis run karta hai aur
    'sentiment' aur 'compound_score' columns add karta hai.
    
    Hinglish explanation:
    Yeh function pure table ke saare reviews par loop karke har review ka sentiment
    aur score calculate karta hai aur nayi columns add karta hai.
    """
    # Original data ko modify karne se bachne ke liye copy banate hain
    analyzed_df = df.copy()

    # Empty lists jisme har review ka result store hoga
    sentiments = []
    compound_scores = []

    # Simple beginner-friendly loop across all feedback rows
    for text in analyzed_df["feedback"]:
        sentiment, score = analyze_sentiment(text)
        sentiments.append(sentiment)
        compound_scores.append(score)

    # DataFrame mein results ko nayi columns ke roop mein save karte hain
    analyzed_df["sentiment"] = sentiments
    analyzed_df["compound_score"] = compound_scores

    return analyzed_df
