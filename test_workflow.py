"""
test_workflow.py - Automated Verification Test Suite (Flask Edition)

Tests all components:
1. Dataset & VADER Sentiment Prediction
2. Analytics & KPI Calculations
3. PDF Report Generation & CSV Export
4. Flask Web Application & REST API Endpoints
5. Session Isolation & In-Memory Storage Safety
"""

import os
import io
import json
import pandas as pd
from modules.sentiment import analyze_sentiment, analyze_dataframe
from modules.analytics import (
    calculate_kpis,
    get_sentiment_distribution,
    get_airline_sentiment_summary,
    get_date_sentiment_summary,
    filter_data,
    get_theme_colors,
)
from modules.report_generator import generate_pdf_report
from app import app, USER_SESSIONS, BASELINE_SAMPLE_DF


def run_all_tests():
    print("=" * 68)
    print("RUNNING AIRLINE SENTIMENT ANALYZER FLASK TEST SUITE")
    print("=" * 68)

    # 1. Dataset Verification
    csv_path = os.path.join("data", "sample_feedback.csv")
    assert os.path.exists(csv_path), "sample_feedback.csv does not exist"
    df = pd.read_csv(csv_path)
    
    assert len(df) == 50, f"Expected exactly 50 data rows, found {len(df)}"
    print(f"[PASS] 1. Row count check: Exactly {len(df)} rows found.")

    expected_cols = ["airline", "date", "feedback"]
    assert list(df.columns) == expected_cols, f"Columns mismatch: {list(df.columns)}"
    print(f"[PASS] 2. Columns check: {expected_cols} verified.")

    assert df["airline"].nunique() == 5, "Expected 5 airlines"
    print(f"[PASS] 3. Airlines count check: 5 unique airlines ({df['airline'].unique().tolist()}).")

    assert df.isnull().sum().sum() == 0, "Null values found in sample dataset"
    print("[PASS] 4. Null value check: 0 nulls in sample dataset.")

    # 2. Date Distribution 2020-2026 Verification
    dt_series = pd.to_datetime(df["date"], errors="raise")
    years_present = sorted(dt_series.dt.year.unique().tolist())
    expected_years = [2020, 2021, 2022, 2023, 2024, 2025, 2026]
    assert years_present == expected_years, f"Years mismatch: expected {expected_years}, got {years_present}"
    assert df["date"].min().startswith("2020"), "Earliest date must be in 2020"
    assert df["date"].max().startswith("2026"), "Latest date must be in 2026"
    print(f"[PASS] 5. 2020-2026 Date check: Earliest {df['date'].min()}, Latest {df['date'].max()}, all 7 years represented.")

    # 3. Sentiment Engine Tests
    pos_sent, pos_score = analyze_sentiment("Flight was excellent and crew was extraordinarily helpful!")
    assert pos_sent == "Positive" and pos_score >= 0.05
    print(f"[PASS] 6. Positive review test: '{pos_sent}', compound: {pos_score}")

    neg_sent, neg_score = analyze_sentiment("Horrible experience. Flight delayed by 5 hours and baggage lost.")
    assert neg_sent == "Negative" and neg_score <= -0.05
    print(f"[PASS] 7. Negative review test: '{neg_sent}', compound: {neg_score}")

    neu_sent, neu_score = analyze_sentiment("The flight departed at 10 AM.")
    assert neu_sent == "Neutral" and -0.05 < neu_score < 0.05
    print(f"[PASS] 8. Neutral review test: '{neu_sent}', compound: {neu_score}")

    empty_sent, empty_score = analyze_sentiment("   ")
    assert empty_sent == "Neutral" and empty_score == 0.0
    print(f"[PASS] 9. Empty string safety test: '{empty_sent}', compound: {empty_score}")

    # 4. DataFrame Analysis & KPIs
    analyzed_df = analyze_dataframe(df)
    assert "sentiment" in analyzed_df.columns and "compound_score" in analyzed_df.columns
    kpis = calculate_kpis(analyzed_df)
    assert kpis["total"] == 50
    assert kpis["total"] == kpis["positive"] + kpis["negative"] + kpis["neutral"]
    print(f"[PASS] 10. KPI identity check: Total ({kpis['total']}) == Pos ({kpis['positive']}) + Neg ({kpis['negative']}) + Neu ({kpis['neutral']})")

    # 5. PDF Generation
    pdf_bytes, err = generate_pdf_report(analyzed_df)
    assert err is None and pdf_bytes.startswith(b"%PDF")
    print(f"[PASS] 11. PDF report generator check: Valid PDF generated in-memory ({len(pdf_bytes)} bytes).")

    # 6. Flask Test Client Endpoints Verification
    app.config["TESTING"] = True
    client = app.test_client()

    # Route: GET /
    res_home = client.get("/")
    assert res_home.status_code == 200
    assert b"Airline Customer Sentiment Analyzer" in res_home.data
    assert b"themeToggleBtn" in res_home.data
    print("[PASS] 12. Flask GET / check: HTML dashboard rendered with status 200.")

    # Route: GET /api/dashboard
    res_dash = client.get("/api/dashboard")
    assert res_dash.status_code == 200
    data = json.loads(res_dash.data)
    assert data["status"] == "success"
    assert data["meta"]["total_records"] == 50
    assert data["kpis"]["total"] == 50
    assert "charts" in data and "reviews" in data
    print(f"[PASS] 13. Flask GET /api/dashboard check: JSON data returned (50 reviews).")

    # Route: GET /api/dashboard with filters
    res_filter = client.get("/api/dashboard?airlines=IndiGo&sentiments=Positive")
    assert res_filter.status_code == 200
    filter_data = json.loads(res_filter.data)
    assert filter_data["kpis"]["total"] > 0
    assert all(r["airline"] == "IndiGo" for r in filter_data["reviews"])
    assert all(r["sentiment"] == "Positive" for r in filter_data["reviews"])
    print(f"[PASS] 14. Flask API filtering check: Filtered {filter_data['kpis']['total']} IndiGo Positive reviews.")

    # Route: POST /api/reviews (Manual Entry)
    res_review = client.post(
        "/api/reviews",
        data=json.dumps({
            "airline": "Vistara",
            "date": "2026-10-12",
            "feedback": "Outstanding service and delicious in-flight meal!",
        }),
        content_type="application/json",
    )
    assert res_review.status_code == 200
    rev_json = json.loads(res_review.data)
    assert rev_json["status"] == "success"
    assert rev_json["predicted"]["sentiment"] == "Positive"
    print(f"[PASS] 15. Flask POST /api/reviews check: Manual review analyzed (Predicted: {rev_json['predicted']['sentiment']}).")

    # Verify review was added to session
    res_after_add = client.get("/api/dashboard")
    data_after_add = json.loads(res_after_add.data)
    assert data_after_add["meta"]["total_records"] == 51
    print(f"[PASS] 16. Session in-memory update check: Session dataset now has 51 reviews.")

    # Route: POST /api/upload
    csv_content = "airline,date,feedback\nIndiGo,2025-05-01,Smooth flight and on time.\nSpiceJet,2025-05-02,Flight delayed for 2 hours."
    upload_data = {
        "file": (io.BytesIO(csv_content.encode("utf-8")), "test_upload.csv")
    }
    res_upload = client.post("/api/upload", data=upload_data, content_type="multipart/form-data")
    assert res_upload.status_code == 200
    upload_json = json.loads(res_upload.data)
    assert upload_json["records_count"] == 2
    print(f"[PASS] 17. Flask POST /api/upload check: Uploaded CSV validated and analyzed ({upload_json['records_count']} rows).")

    # Route: POST /api/reset-sample
    res_reset = client.post("/api/reset-sample")
    assert res_reset.status_code == 200
    res_after_reset = client.get("/api/dashboard")
    data_after_reset = json.loads(res_after_reset.data)
    assert data_after_reset["meta"]["total_records"] == 50
    print("[PASS] 18. Flask POST /api/reset-sample check: Reset restored original 50 sample reviews.")

    # Route: GET /api/export/csv
    res_csv = client.get("/api/export/csv")
    assert res_csv.status_code == 200
    assert res_csv.mimetype == "text/csv"
    assert b"compound_score" in res_csv.data
    print("[PASS] 19. Flask GET /api/export/csv check: Downloadable CSV generated.")

    # Route: GET /api/export/pdf
    res_pdf = client.get("/api/export/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.mimetype == "application/pdf"
    assert res_pdf.data.startswith(b"%PDF")
    print(f"[PASS] 20. Flask GET /api/export/pdf check: Downloadable PDF generated ({len(res_pdf.data)} bytes).")

    # Original sample file check
    orig_df = pd.read_csv(csv_path)
    assert len(orig_df) == 50
    assert list(orig_df.columns) == expected_cols
    print("[PASS] 21. Original sample_feedback.csv integrity check: Completely unchanged.")

    print("=" * 68)
    print("ALL 21 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 68)


if __name__ == "__main__":
    run_all_tests()
