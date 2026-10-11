"""
app.py - Airline Customer Sentiment Analyzer

Streamlit web dashboard jo airline customer reviews ka sentiment analyze karta hai,
KPI metrics aur interactive charts dikhata hai, aur CSV/PDF export provide karta hai.
"""

import io
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# Custom modules import karte hain
# modules/sentiment.py: VADER analysis logic
# modules/analytics.py: KPIs, aggregations, aur filters
# modules/report_generator.py: PDF summary report generator
from modules.sentiment import analyze_sentiment, analyze_dataframe
from modules.analytics import (
    calculate_kpis,
    get_sentiment_distribution,
    get_airline_sentiment_summary,
    get_date_sentiment_summary,
    filter_data,
)
from modules.report_generator import generate_pdf_report

# Streamlit Page Configuration
st.set_page_config(
    page_title="Airline Customer Sentiment Analyzer",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom color palette for sentiment consistency
SENTIMENT_COLORS = {
    "Positive": "#2ecc71",
    "Negative": "#e74c3c",
    "Neutral": "#95a5a6",
}

SAMPLE_FILE_PATH = os.path.join("data", "sample_feedback.csv")


def load_initial_sample_data():
    """
    Default sample CSV (50 reviews) ko load karke VADER se analyze karta hai.
    
    Hinglish explanation:
    Yeh function sample_feedback.csv ko Pandas se read karke VADER ke through
    sentiment calculate karta hai aur analyzed DataFrame return karta hai.
    """
    if os.path.exists(SAMPLE_FILE_PATH):
        df = pd.read_csv(SAMPLE_FILE_PATH)
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        return analyze_dataframe(df)
    else:
        st.error(f"Sample data file not found at: {SAMPLE_FILE_PATH}")
        return pd.DataFrame(columns=["airline", "date", "feedback", "sentiment", "compound_score"])


# ---------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------
# Streamlit har interaction par script ko rerun karta hai,
# isliye session_state me active dataset ko store karte hain taaki data gayab na ho.
if "active_df" not in st.session_state:
    st.session_state["active_df"] = load_initial_sample_data()

if "data_source_name" not in st.session_state:
    st.session_state["data_source_name"] = "Dataset (50 Reviews)"


# ---------------------------------------------------------
# HEADER & INTRODUCTION
# ---------------------------------------------------------
st.title("✈️ Airline Customer Sentiment Analyzer")
st.markdown(
    "**Analyze airline customer feedback using Python and VADER sentiment analysis.** "
    "*(College Social Media Analytics / Data Analytics Project)*"
)

# Synthetic data banner
st.info(
    "📌 **Demonstration Notice:** Currently using synthetic customer reviews prepared for academic demonstration. "
    "Predictions are generated automatically by rule-based VADER sentiment analysis."
)


# ---------------------------------------------------------
# SIDEBAR: DATA MANAGEMENT & FILTERS
# ---------------------------------------------------------
st.sidebar.header("📁 Data Source & Upload")

# Reset button to restore initial 50 sample reviews
if st.sidebar.button("🔄 Reload Sample Dataset (50 Reviews)", use_container_width=True):
    st.session_state["active_df"] = load_initial_sample_data()
    st.session_state["data_source_name"] = "Sample Dataset (50 Reviews)"
    st.sidebar.success("Default 50 sample reviews reloaded!")
    st.rerun()

# CSV File Uploader
uploaded_file = st.sidebar.file_uploader(
    "Upload Reviews CSV",
    type=["csv"],
    help="CSV must contain columns: 'airline', 'date', 'feedback'",
)

if uploaded_file is not None:
    try:
        raw_uploaded_df = pd.read_csv(uploaded_file)
        required_cols = {"airline", "date", "feedback"}

        # Validate required columns
        if not required_cols.issubset(set(raw_uploaded_df.columns)):
            st.sidebar.error(
                f"Missing required columns! Uploaded file has: {list(raw_uploaded_df.columns)}. "
                "Required: airline, date, feedback"
            )
        else:
            # Handle empty feedback and airlines
            initial_count = len(raw_uploaded_df)
            valid_df = raw_uploaded_df.dropna(subset=["feedback", "airline"]).copy()
            valid_df = valid_df[valid_df["feedback"].astype(str).str.strip() != ""]
            
            # Parse dates safely
            valid_df["parsed_date"] = pd.to_datetime(valid_df["date"], errors="coerce")
            valid_df = valid_df.dropna(subset=["parsed_date"])
            valid_df["date"] = valid_df["parsed_date"].dt.strftime("%Y-%m-%d")
            valid_df = valid_df.drop(columns=["parsed_date"])

            dropped_count = initial_count - len(valid_df)
            if dropped_count > 0:
                st.sidebar.warning(f"Excluded {dropped_count} row(s) with blank text or invalid dates.")

            if len(valid_df) == 0:
                st.sidebar.error("No valid reviews found in the uploaded file.")
            else:
                # Analyze uploaded reviews
                analyzed_uploaded_df = analyze_dataframe(valid_df)
                st.session_state["active_df"] = analyzed_uploaded_df
                st.session_state["data_source_name"] = f"Uploaded File ({uploaded_file.name})"
                st.sidebar.success(f"Loaded and analyzed {len(valid_df)} valid reviews!")

    except Exception as e:
        st.sidebar.error(f"Error reading uploaded file: {str(e)}")

st.sidebar.caption(f"**Active Source:** {st.session_state['data_source_name']}")
st.sidebar.divider()

# ---------------------------------------------------------
# SIDEBAR: FILTERS
# ---------------------------------------------------------
st.sidebar.header("🔍 Filter Reviews")

active_df = st.session_state["active_df"]

if not active_df.empty:
    # 1. Airline filter
    all_airlines = sorted(active_df["airline"].dropna().unique().tolist())
    selected_airlines = st.sidebar.multiselect(
        "Select Airline(s):",
        options=all_airlines,
        default=all_airlines,
    )

    # 2. Sentiment filter
    all_sentiments = ["Positive", "Negative", "Neutral"]
    selected_sentiments = st.sidebar.multiselect(
        "Select Sentiment(s):",
        options=all_sentiments,
        default=all_sentiments,
    )

    # 3. Date Range filter
    min_date = pd.to_datetime(active_df["date"]).min().date()
    max_date = pd.to_datetime(active_df["date"]).max().date()

    if min_date == max_date:
        start_date = min_date
        end_date = max_date
        st.sidebar.info(f"Single date available: {min_date}")
    else:
        date_range = st.sidebar.date_input(
            "Select Date Range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        elif isinstance(date_range, tuple) and len(date_range) == 1:
            start_date = date_range[0]
            end_date = date_range[0]
        else:
            start_date, end_date = min_date, max_date

    # Reset filters button
    if st.sidebar.button("Reset Filters", use_container_width=True):
        st.rerun()

    # Apply filters using modules/analytics.py filter_data function
    filtered_df = filter_data(
        active_df,
        selected_airlines=selected_airlines,
        selected_sentiments=selected_sentiments,
        start_date=start_date,
        end_date=end_date,
    )
else:
    filtered_df = active_df.copy()


# ---------------------------------------------------------
# MAIN DASHBOARD CONTENT
# ---------------------------------------------------------

# 1. KPI Cards
st.subheader("📊 Sentiment Overview Metrics")

if filtered_df.empty:
    st.warning("⚠️ No reviews match the currently selected filters. Please adjust the filters in the sidebar.")
    kpis = calculate_kpis(filtered_df)
else:
    kpis = calculate_kpis(filtered_df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Reviews",
        value=kpis["total"],
        help="Total number of reviews matching the selected filters",
    )

with col2:
    st.metric(
        label="Positive Reviews",
        value=f"{kpis['positive']} ({kpis['pos_percent']}%)",
        delta=f"{kpis['pos_percent']}%",
        delta_color="normal",
        help="Reviews with VADER compound score >= 0.05",
    )

with col3:
    st.metric(
        label="Negative Reviews",
        value=f"{kpis['negative']} ({kpis['neg_percent']}%)",
        delta=f"-{kpis['neg_percent']}%" if kpis["negative"] > 0 else "0%",
        delta_color="inverse",
        help="Reviews with VADER compound score <= -0.05",
    )

with col4:
    st.metric(
        label="Neutral Reviews",
        value=f"{kpis['neutral']} ({kpis['neu_percent']}%)",
        help="Reviews with VADER compound score between -0.05 and +0.05",
    )

st.divider()

# ---------------------------------------------------------
# SECTION: MANUAL REVIEW INPUT (OPTIONAL FORM)
# ---------------------------------------------------------
with st.expander("✍️ Add a New Customer Review (Session Only)", expanded=False):
    st.markdown(
        "Enter customer feedback below to test real-time VADER prediction. "
        "*Note: This review is saved only in your current browser session and is not stored permanently.*"
    )

    with st.form(key="manual_review_form", clear_on_submit=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            existing_airlines = sorted(active_df["airline"].dropna().unique().tolist()) if not active_df.empty else ["IndiGo"]
            manual_airline = st.selectbox("Airline Name", options=existing_airlines)
        with f_col2:
            manual_date = st.date_input("Review Date", value=datetime.now().date())

        manual_text = st.text_area(
            "Customer Feedback Text",
            placeholder="e.g., The cabin crew was very helpful and the landing was on time!",
        )

        submit_review = st.form_submit_button("Analyze & Add Review")

        if submit_review:
            if not manual_text or not manual_text.strip():
                st.warning("Please enter review text before submitting.")
            else:
                # Predict sentiment for manual review
                pred_sentiment, pred_score = analyze_sentiment(manual_text)
                
                # Create a new review record
                new_row = pd.DataFrame(
                    [
                        {
                            "airline": manual_airline,
                            "date": manual_date.strftime("%Y-%m-%d"),
                            "feedback": manual_text.strip(),
                            "sentiment": pred_sentiment,
                            "compound_score": pred_score,
                        }
                    ]
                )

                # Append to session state
                st.session_state["active_df"] = pd.concat([st.session_state["active_df"], new_row], ignore_index=True)
                st.success(
                    f"✅ Review analyzed and added! Predicted Sentiment: **{pred_sentiment}** "
                    f"(VADER Compound Score: {pred_score:+.4f})"
                )
                st.rerun()

# ---------------------------------------------------------
# SECTION: VISUALIZATIONS & CHARTS
# ---------------------------------------------------------
st.subheader("📈 Interactive Sentiment Visualizations")

if filtered_df.empty:
    st.info("No data to visualize. Reset filters in the sidebar to see charts.")
else:
    chart_col1, chart_col2 = st.columns(2)

    # Chart 1: Overall Sentiment Distribution
    with chart_col1:
        st.markdown("##### Chart 1: Overall Sentiment Distribution")
        dist_df = get_sentiment_distribution(filtered_df)
        fig_dist = px.bar(
            dist_df,
            x="sentiment",
            y="count",
            color="sentiment",
            color_discrete_map=SENTIMENT_COLORS,
            text="count",
            labels={"sentiment": "Sentiment", "count": "Review Count"},
            title="Sentiment Breakdown (Filtered)",
        )
        fig_dist.update_traces(textposition="outside")
        fig_dist.update_layout(showlegend=False, height=350, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_dist, use_container_width=True)

    # Chart 2: Airline-wise Sentiment Comparison
    with chart_col2:
        st.markdown("##### Chart 2: Airline-wise Sentiment Comparison")
        airline_summary = get_airline_sentiment_summary(filtered_df)
        fig_airline = px.bar(
            airline_summary,
            x="airline",
            y="count",
            color="sentiment",
            barmode="group",
            color_discrete_map=SENTIMENT_COLORS,
            labels={"airline": "Airline", "count": "Review Count", "sentiment": "Sentiment"},
            title="Sentiment by Airline (Grouped)",
        )
        fig_airline.update_layout(height=350, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_airline, use_container_width=True)

    # Chart 3: Date-wise Sentiment Trend
    st.markdown("##### Chart 3: Date-wise Sentiment Trend Across Time")
    date_summary = get_date_sentiment_summary(filtered_df)
    if not date_summary.empty:
        fig_trend = px.line(
            date_summary,
            x="date",
            y="count",
            color="sentiment",
            markers=True,
            color_discrete_map=SENTIMENT_COLORS,
            labels={"date": "Date", "count": "Daily Reviews", "sentiment": "Sentiment"},
            title="Chronological Sentiment Trend",
        )
        fig_trend.update_layout(height=350, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Insufficient date points to render trend line.")

st.divider()

# ---------------------------------------------------------
# SECTION: REVIEW DATA TABLE
# ---------------------------------------------------------
st.subheader("📋 Analyzed Customer Reviews")

if filtered_df.empty:
    st.info("No reviews available to display in table.")
else:
    # Display table with nicely rounded compound scores
    display_table = filtered_df[["airline", "date", "feedback", "sentiment", "compound_score"]].copy()
    display_table.columns = ["Airline", "Date", "Customer Feedback", "Predicted Sentiment", "Compound Score"]

    st.dataframe(
        display_table.style.format({"Compound Score": "{:+.2f}"}),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(f"Showing {len(display_table)} review records matching active filters.")

# ---------------------------------------------------------
# SECTION: DOWNLOAD & EXPORT OPTIONS
# ---------------------------------------------------------
st.subheader("📥 Export & Reports")

col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    st.markdown("##### Download Analyzed Data (CSV)")
    st.caption("Exports currently filtered reviews with predicted sentiments and scores.")

    if not filtered_df.empty:
        # Convert filtered DataFrame to CSV in memory
        csv_buffer = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Filtered Results (CSV)",
            data=csv_buffer,
            file_name="airline_sentiment_results.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.button("⬇️ Download Filtered Results (CSV)", disabled=True, use_container_width=True)

with col_exp2:
    st.markdown("##### Download PDF Summary Report")
    st.caption("Generates a formal college project report with KPIs, tables, and chart.")

    if not filtered_df.empty:
        # Generate PDF report in memory using ReportLab
        pdf_bytes, pdf_error = generate_pdf_report(filtered_df)
        if pdf_bytes:
            st.download_button(
                label="📄 Download PDF Summary Report",
                data=pdf_bytes,
                file_name="airline_sentiment_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.error(f"Could not generate PDF: {pdf_error}")
    else:
        st.button("📄 Download PDF Summary Report", disabled=True, use_container_width=True)

# ---------------------------------------------------------
# METHODOLOGY & COLLEGE PROJECT FOOTER
# ---------------------------------------------------------
st.divider()
with st.expander("ℹ️ Methodology, VADER Thresholds & Limitations"):
    st.markdown(
        r"""
        ### VADER Sentiment Classification Methodology
        - **Engine:** VADER (*Valence Aware Dictionary and sEntiment Reasoner*)
        - **Compound Score Range:** -1.0 (Extremely Negative) to +1.0 (Extremely Positive)
        - **Classification Rules:**
            - **Positive:** Compound Score $\ge$ `+0.05`
            - **Negative:** Compound Score $\le$ `-0.05`
            - **Neutral:** `-0.05` $<$ Compound Score $<$ `+0.05`
        
        ### Practical Limitations for Viva Discussion
        - VADER is a **lexical, rule-based model**, not an LLM or deep neural network.
        - It may misclassify subtle sarcasm (e.g., *"Great, another 4-hour delay!"* may get marked positive due to the word *"Great"*).
        - It does not understand airline-specific jargon without manual custom lexicon entries.
        """
    )
