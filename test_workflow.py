"""
test_workflow.py - Automated Verification Test Suite

Tests all components, data integrity, sentiment predictions, analytics calculations,
filtering logic, PDF generation, and CSV compatibility.
"""

import os
import io
import pandas as pd
from modules.sentiment import analyze_sentiment, analyze_dataframe
from modules.analytics import (
    calculate_kpis,
    get_sentiment_distribution,
    get_airline_sentiment_summary,
    get_date_sentiment_summary,
    filter_data,
)
from modules.report_generator import generate_pdf_report


def run_all_tests():
    print("=" * 60)
    print("RUNNING AIRLINE SENTIMENT ANALYZER VERIFICATION SUITE")
    print("=" * 60)

    # 1. Dataset Verification
    csv_path = os.path.join("data", "sample_feedback.csv")
    assert os.path.exists(csv_path), "sample_feedback.csv does not exist"
    df = pd.read_csv(csv_path)
    
    assert len(df) == 50, f"Expected exactly 50 data rows, found {len(df)}"
    print(f"[PASS] 1. Row count check: Exactly {len(df)} rows found.")

    expected_cols = ["airline", "date", "feedback"]
    assert list(df.columns) == expected_cols, f"Columns mismatch: {list(df.columns)}"
    print(f"[PASS] 2. Columns check: {expected_cols} verified.")

    assert df["airline"].nunique() >= 4, "Expected 4-5 airlines"
    print(f"[PASS] 3. Airlines count check: {df['airline'].nunique()} unique airlines ({df['airline'].unique().tolist()}).")

    assert df.isnull().sum().sum() == 0, "Null values found in sample dataset"
    print("[PASS] 4. Null value check: 0 nulls in sample dataset.")

    # 2. Sentiment Engine Tests
    pos_sent, pos_score = analyze_sentiment("Flight was excellent and crew was extraordinarily helpful!")
    assert pos_sent == "Positive" and pos_score >= 0.05
    print(f"[PASS] 5. Positive review test: '{pos_sent}', compound: {pos_score}")

    neg_sent, neg_score = analyze_sentiment("Horrible experience. Flight delayed by 5 hours and baggage lost.")
    assert neg_sent == "Negative" and neg_score <= -0.05
    print(f"[PASS] 6. Negative review test: '{neg_sent}', compound: {neg_score}")

    neu_sent, neu_score = analyze_sentiment("The flight departed at 10 AM.")
    assert neu_sent == "Neutral" and -0.05 < neu_score < 0.05
    print(f"[PASS] 7. Neutral review test: '{neu_sent}', compound: {neu_score}")

    empty_sent, empty_score = analyze_sentiment("   ")
    assert empty_sent == "Neutral" and empty_score == 0.0
    print(f"[PASS] 8. Empty string safety test: '{empty_sent}', compound: {empty_score}")

    # 3. DataFrame Analysis
    analyzed_df = analyze_dataframe(df)
    assert "sentiment" in analyzed_df.columns and "compound_score" in analyzed_df.columns
    assert len(analyzed_df) == 50
    print(f"[PASS] 9. DataFrame batch analysis test: {len(analyzed_df)} rows analyzed.")

    # 4. KPI Calculations
    kpis = calculate_kpis(analyzed_df)
    assert kpis["total"] == 50
    assert kpis["total"] == kpis["positive"] + kpis["negative"] + kpis["neutral"]
    print(f"[PASS] 10. KPI identity check: Total ({kpis['total']}) == Pos ({kpis['positive']}) + Neg ({kpis['negative']}) + Neu ({kpis['neutral']})")

    # 5. Sentiment Distribution
    dist_df = get_sentiment_distribution(analyzed_df)
    assert len(dist_df) == 3
    assert set(dist_df["sentiment"]) == {"Positive", "Negative", "Neutral"}
    print(f"[PASS] 11. Sentiment distribution check: 3 labels present.")

    # 6. Airline Breakdown
    airline_sum = get_airline_sentiment_summary(analyzed_df)
    assert not airline_sum.empty
    assert airline_sum["count"].sum() == 50
    print(f"[PASS] 12. Airline summary check: Total sum {airline_sum['count'].sum()} matches 50.")

    # 7. Date Breakdown (Chronological Sort)
    date_sum = get_date_sentiment_summary(analyzed_df)
    dates_list = date_sum["date"].unique().tolist()
    assert dates_list == sorted(dates_list), "Dates are not sorted chronologically"
    print(f"[PASS] 13. Date chronological sort check: {len(dates_list)} distinct dates verified.")

    # 8. Filter Logic
    filtered = filter_data(analyzed_df, selected_airlines=["IndiGo"], selected_sentiments=["Positive"])
    assert all(filtered["airline"] == "IndiGo")
    assert all(filtered["sentiment"] == "Positive")
    print(f"[PASS] 14. Filter logic check: Filtered {len(filtered)} IndiGo Positive rows correctly.")

    # 9. PDF Generation
    pdf_bytes, err = generate_pdf_report(analyzed_df)
    assert err is None, f"PDF generation produced error: {err}"
    assert pdf_bytes is not None and len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF"), "Generated output is not a valid PDF header"
    print(f"[PASS] 15. PDF generation check: Valid PDF generated in-memory ({len(pdf_bytes)} bytes).")

    # 10. CSV Export Simulation
    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    re_read_df = pd.read_csv(io.BytesIO(csv_bytes))
    assert list(re_read_df.columns) == ["airline", "date", "feedback", "sentiment", "compound_score"]
    print(f"[PASS] 16. CSV export check: Analyzed columns preserved, index=False verified.")

    # 11. Original File Integrity
    original_after = pd.read_csv(csv_path)
    assert len(original_after) == 50
    assert list(original_after.columns) == expected_cols
    print("[PASS] 17. Original sample_feedback.csv file integrity check: Unmodified.")

    print("=" * 60)
    print("ALL 17 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
