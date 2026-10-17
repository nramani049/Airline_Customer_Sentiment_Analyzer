"""
app.py - Airline Customer Sentiment Analyzer (Flask Application)

Flask web server providing backend routing, session-isolated in-memory dataset storage,
VADER sentiment processing, dynamic filtering, and CSV/PDF export.
"""

import io
import os
import uuid
from datetime import datetime, timedelta
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file, session

# Custom modules
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

app = Flask(__name__)
# Secret key for secure signed cookies
app.secret_key = os.environ.get("SECRET_KEY", "airline-sentiment-analyzer-secret-key-2026")

SAMPLE_FILE_PATH = os.path.join("data", "sample_feedback.csv")

# ---------------------------------------------------------
# SESSION-ISOLATED IN-MEMORY DATA STORAGE
# ---------------------------------------------------------
# In-memory session store mapping session IDs to DataFrames
# { session_id: { "df": DataFrame, "source_name": str, "last_accessed": datetime } }
USER_SESSIONS = {}
SESSION_TIMEOUT_HOURS = 2


def load_default_sample_dataframe():
    """
    Loads baseline sample dataset and runs initial sentiment analysis.
    """
    if os.path.exists(SAMPLE_FILE_PATH):
        df = pd.read_csv(SAMPLE_FILE_PATH)
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        return analyze_dataframe(df)
    else:
        return pd.DataFrame(columns=["airline", "date", "feedback", "sentiment", "compound_score"])


# Cache the baseline sample dataset in memory so every new session can make a fast copy
BASELINE_SAMPLE_DF = load_default_sample_dataframe()


def cleanup_expired_sessions():
    """
    Removes inactive sessions from memory based on timeout.
    """
    now = datetime.now()
    expired_keys = [
        sid
        for sid, data in USER_SESSIONS.items()
        if now - data.get("last_accessed", now) > timedelta(hours=SESSION_TIMEOUT_HOURS)
    ]
    for sid in expired_keys:
        USER_SESSIONS.pop(sid, None)


def get_or_create_user_session():
    """
    Retrieves current user's session or initializes a new isolated session in memory.
    """
    cleanup_expired_sessions()

    sid = session.get("sid")
    if not sid or sid not in USER_SESSIONS:
        sid = str(uuid.uuid4())
        session["sid"] = sid
        USER_SESSIONS[sid] = {
            "df": BASELINE_SAMPLE_DF.copy(),
            "source_name": "Sample Dataset (50 Reviews, 2020–2026)",
            "last_accessed": datetime.now(),
        }
    else:
        USER_SESSIONS[sid]["last_accessed"] = datetime.now()

    return sid, USER_SESSIONS[sid]


# ---------------------------------------------------------
# FLASK ROUTES: PAGE RENDERING
# ---------------------------------------------------------
@app.route("/")
def index():
    """
    Renders main dashboard HTML page.
    """
    # Ensure session is initialized
    get_or_create_user_session()
    return render_template("index.html")


# ---------------------------------------------------------
# API ROUTE: DASHBOARD DATA (METRICS, CHARTS, FILTERS, TABLE)
# ---------------------------------------------------------
@app.route("/api/dashboard", methods=["GET"])
def get_dashboard_data():
    """
    Returns filtered reviews, KPI metrics, and Chart.js datasets in JSON format.
    """
    sid, user_session = get_or_create_user_session()
    active_df = user_session["df"]

    # Available filter metadata from entire active dataset
    all_airlines = sorted(active_df["airline"].dropna().unique().tolist()) if not active_df.empty else []
    all_sentiments = ["Positive", "Negative", "Neutral"]
    min_date = active_df["date"].min() if not active_df.empty else "2020-01-01"
    max_date = active_df["date"].max() if not active_df.empty else datetime.now().strftime("%Y-%m-%d")

    # Read query parameters
    airlines_param = request.args.get("airlines", "")
    sentiments_param = request.args.get("sentiments", "")
    start_date = request.args.get("start_date", min_date)
    end_date = request.args.get("end_date", max_date)
    trend_freq = request.args.get("freq", "monthly")  # "monthly" or "daily"

    selected_airlines = [a.strip() for a in airlines_param.split(",") if a.strip()] if airlines_param else all_airlines
    selected_sentiments = [s.strip() for s in sentiments_param.split(",") if s.strip()] if sentiments_param else all_sentiments

    # Filter data using existing modules/analytics.py filter_data function
    filtered_df = filter_data(
        active_df,
        selected_airlines=selected_airlines,
        selected_sentiments=selected_sentiments,
        start_date=start_date,
        end_date=end_date,
    )

    # 1. KPIs
    kpis = calculate_kpis(filtered_df)

    # 2. Overall Sentiment Distribution
    dist_df = get_sentiment_distribution(filtered_df)
    dist_chart = {
        "labels": dist_df["sentiment"].tolist() if not dist_df.empty else ["Positive", "Negative", "Neutral"],
        "counts": dist_df["count"].tolist() if not dist_df.empty else [0, 0, 0],
        "percentages": dist_df["percentage"].tolist() if not dist_df.empty else [0, 0, 0],
    }

    # 3. Airline-wise Sentiment Comparison (Grouped Bar Format)
    airline_sum_df = get_airline_sentiment_summary(filtered_df)
    airline_labels = sorted(filtered_df["airline"].dropna().unique().tolist()) if not filtered_df.empty else []
    
    airline_pos_counts = []
    airline_neg_counts = []
    airline_neu_counts = []

    for air in airline_labels:
        sub = airline_sum_df[airline_sum_df["airline"] == air]
        pos_cnt = int(sub[sub["sentiment"] == "Positive"]["count"].sum()) if not sub.empty else 0
        neg_cnt = int(sub[sub["sentiment"] == "Negative"]["count"].sum()) if not sub.empty else 0
        neu_cnt = int(sub[sub["sentiment"] == "Neutral"]["count"].sum()) if not sub.empty else 0
        airline_pos_counts.append(pos_cnt)
        airline_neg_counts.append(neg_cnt)
        airline_neu_counts.append(neu_cnt)

    airline_chart = {
        "labels": airline_labels,
        "positive": airline_pos_counts,
        "negative": airline_neg_counts,
        "neutral": airline_neu_counts,
    }

    # 4. Review Sentiment Timeline - Individual points for chronological scatter visualization
    if not filtered_df.empty:
        timeline_df = filtered_df.copy()
        # plot_date: YYYY-MM for monthly view (x-axis grouping), YYYY-MM-DD for daily view
        # actual_date: full YYYY-MM-DD for tooltip display
        if trend_freq == "monthly":
            timeline_df["plot_date"] = pd.to_datetime(timeline_df["date"]).dt.strftime("%Y-%m")
        else:
            timeline_df["plot_date"] = timeline_df["date"]

        timeline_points = (
            timeline_df[["plot_date", "date", "sentiment"]]
            .rename(columns={"plot_date": "date", "date": "actual_date"})
            .to_dict(orient="records")
        )
    else:
        timeline_points = []

    trend_chart = {
        "frequency": trend_freq,
        "timeline": timeline_points,
    }


    # 5. Reviews Table Data
    reviews_data = []
    if not filtered_df.empty:
        # Sort chronologically by date descending for latest first display
        display_df = filtered_df.sort_values(by="date", ascending=False)
        reviews_data = display_df[
            ["airline", "date", "feedback", "sentiment", "compound_score"]
        ].to_dict(orient="records")

    return jsonify({
        "status": "success",
        "meta": {
            "source_name": user_session.get("source_name", "Active Dataset"),
            "total_records": len(active_df),
            "filtered_records": len(filtered_df),
        },
        "filters": {
            "available_airlines": all_airlines,
            "selected_airlines": selected_airlines,
            "available_sentiments": all_sentiments,
            "selected_sentiments": selected_sentiments,
            "min_date": min_date,
            "max_date": max_date,
            "start_date": start_date,
            "end_date": end_date,
        },
        "kpis": kpis,
        "charts": {
            "distribution": dist_chart,
            "airline_comparison": airline_chart,
            "date_trend": trend_chart,
        },
        "reviews": reviews_data,
    })


# ---------------------------------------------------------
# API ROUTE: MANUAL REVIEW INPUT
# ---------------------------------------------------------
@app.route("/api/reviews", methods=["POST"])
def add_manual_review():
    """
    Analyzes single customer review with VADER and appends it to session dataset.
    """
    sid, user_session = get_or_create_user_session()
    data = request.get_json(silent=True) or {}

    airline = data.get("airline", "").strip()
    date_str = data.get("date", "").strip()
    feedback = data.get("feedback", "").strip()

    if not airline:
        return jsonify({"status": "error", "message": "Airline name is required."}), 400
    if not date_str:
        return jsonify({"status": "error", "message": "Review date is required."}), 400
    if not feedback:
        return jsonify({"status": "error", "message": "Review text cannot be empty."}), 400

    # Validate date format
    try:
        parsed_date = pd.to_datetime(date_str).strftime("%Y-%m-%d")
    except Exception:
        return jsonify({"status": "error", "message": "Invalid date format. Use YYYY-MM-DD."}), 400

    # Calculate sentiment using existing modules/sentiment.py
    sentiment, compound_score = analyze_sentiment(feedback)

    # Append to session DataFrame
    new_row = pd.DataFrame([
        {
            "airline": airline,
            "date": parsed_date,
            "feedback": feedback,
            "sentiment": sentiment,
            "compound_score": compound_score,
        }
    ])

    user_session["df"] = pd.concat([user_session["df"], new_row], ignore_index=True)

    return jsonify({
        "status": "success",
        "message": f"Review added! Predicted: {sentiment} (Score: {compound_score:+.4f})",
        "predicted": {
            "airline": airline,
            "date": parsed_date,
            "sentiment": sentiment,
            "compound_score": compound_score,
        },
    })


# ---------------------------------------------------------
# API ROUTE: CSV UPLOAD AND VALIDATION
# ---------------------------------------------------------
@app.route("/api/upload", methods=["POST"])
def upload_csv():
    """
    Validates uploaded CSV file, analyzes reviews with VADER, and stores them in session dataset.
    """
    sid, user_session = get_or_create_user_session()

    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "No file selected."}), 400

    if not file.filename.lower().endswith(".csv"):
        return jsonify({"status": "error", "message": "Only CSV files are allowed."}), 400

    try:
        content = file.read().decode("utf-8", errors="replace")
        raw_df = pd.read_csv(io.StringIO(content))
        required_cols = {"airline", "date", "feedback"}

        if not required_cols.issubset(set(raw_df.columns)):
            return jsonify({
                "status": "error",
                "message": f"Missing required columns! Found: {list(raw_df.columns)}. Required: airline, date, feedback",
            }), 400

        initial_count = len(raw_df)
        valid_df = raw_df.dropna(subset=["feedback", "airline"]).copy()
        valid_df = valid_df[valid_df["feedback"].astype(str).str.strip() != ""]

        # Parse dates safely
        valid_df["parsed_date"] = pd.to_datetime(valid_df["date"], errors="coerce")
        valid_df = valid_df.dropna(subset=["parsed_date"])
        valid_df["date"] = valid_df["parsed_date"].dt.strftime("%Y-%m-%d")
        valid_df = valid_df.drop(columns=["parsed_date"])

        dropped_count = initial_count - len(valid_df)

        if len(valid_df) == 0:
            return jsonify({"status": "error", "message": "No valid reviews found in the uploaded file."}), 400

        # Analyze uploaded reviews using VADER
        analyzed_df = analyze_dataframe(valid_df)

        user_session["df"] = analyzed_df
        user_session["source_name"] = f"Uploaded File ({file.filename})"

        return jsonify({
            "status": "success",
            "message": f"Loaded and analyzed {len(valid_df)} reviews successfully!"
            + (f" ({dropped_count} blank/invalid rows excluded)" if dropped_count > 0 else ""),
            "records_count": len(valid_df),
            "dropped_count": dropped_count,
            "source_name": user_session["source_name"],
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error parsing CSV: {str(e)}"}), 400


# ---------------------------------------------------------
# API ROUTE: RESET TO SAMPLE DATASET
# ---------------------------------------------------------
@app.route("/api/reset-sample", methods=["POST"])
def reset_sample_dataset():
    """
    Resets the session dataset to the baseline 50 sample reviews.
    """
    sid, user_session = get_or_create_user_session()
    user_session["df"] = BASELINE_SAMPLE_DF.copy()
    user_session["source_name"] = "Sample Dataset (50 Reviews, 2020–2026)"

    return jsonify({
        "status": "success",
        "message": "Sample dataset (50 reviews) reloaded successfully!",
        "source_name": user_session["source_name"],
    })


# ---------------------------------------------------------
# API ROUTE: EXPORT FILTERED CSV
# ---------------------------------------------------------
@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    """
    Exports currently filtered reviews as a downloadable CSV attachment.
    """
    sid, user_session = get_or_create_user_session()
    active_df = user_session["df"]

    airlines_param = request.args.get("airlines", "")
    sentiments_param = request.args.get("sentiments", "")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    selected_airlines = [a.strip() for a in airlines_param.split(",") if a.strip()] if airlines_param else None
    selected_sentiments = [s.strip() for s in sentiments_param.split(",") if s.strip()] if sentiments_param else None

    filtered_df = filter_data(
        active_df,
        selected_airlines=selected_airlines,
        selected_sentiments=selected_sentiments,
        start_date=start_date,
        end_date=end_date,
    )

    if filtered_df.empty:
        export_df = pd.DataFrame(columns=["airline", "date", "feedback", "sentiment", "compound_score"])
    else:
        export_df = filtered_df[["airline", "date", "feedback", "sentiment", "compound_score"]]

    csv_buffer = io.BytesIO()
    export_df.to_csv(csv_buffer, index=False, encoding="utf-8")
    csv_buffer.seek(0)

    return send_file(
        csv_buffer,
        mimetype="text/csv",
        as_attachment=True,
        download_name="airline_sentiment_results.csv",
    )


# ---------------------------------------------------------
# API ROUTE: EXPORT PDF SUMMARY REPORT
# ---------------------------------------------------------
@app.route("/api/export/pdf", methods=["GET"])
def export_pdf():
    """
    Generates and downloads a ReportLab PDF summary report for filtered reviews in-memory.
    """
    sid, user_session = get_or_create_user_session()
    active_df = user_session["df"]

    airlines_param = request.args.get("airlines", "")
    sentiments_param = request.args.get("sentiments", "")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    selected_airlines = [a.strip() for a in airlines_param.split(",") if a.strip()] if airlines_param else None
    selected_sentiments = [s.strip() for s in sentiments_param.split(",") if s.strip()] if sentiments_param else None

    filtered_df = filter_data(
        active_df,
        selected_airlines=selected_airlines,
        selected_sentiments=selected_sentiments,
        start_date=start_date,
        end_date=end_date,
    )

    if filtered_df.empty:
        return jsonify({"status": "error", "message": "Cannot generate PDF report for empty filtered data."}), 400

    pdf_bytes, err = generate_pdf_report(filtered_df)
    if err or not pdf_bytes:
        return jsonify({"status": "error", "message": f"PDF generation failed: {err}"}), 500

    pdf_buffer = io.BytesIO(pdf_bytes)
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="airline_sentiment_report.pdf",
    )


# ---------------------------------------------------------
# APPLICATION ENTRY POINT
# ---------------------------------------------------------
if __name__ == "__main__":
    # Run development server
    port = int(os.environ.get("PORT", 5000))
    print(f">> Airline Customer Sentiment Analyzer starting on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
