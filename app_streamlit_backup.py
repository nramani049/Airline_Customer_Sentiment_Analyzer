"""
app.py - Airline Customer Sentiment Analyzer

Streamlit web dashboard jo airline customer reviews ka sentiment analyze karta hai,
KPI metrics aur interactive charts dikhata hai, animated Sun/Moon theme switch provide karta hai,
aur in-memory CSV/PDF export provide karta hai.
"""

import io
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# Custom modules import
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

# Streamlit Page Configuration
st.set_page_config(
    page_title="Airline Customer Sentiment Analyzer",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

SAMPLE_FILE_PATH = os.path.join("data", "sample_feedback.csv")


# ---------------------------------------------------------
# COMPREHENSIVE THEME STYLING INJECTION
# ---------------------------------------------------------
def apply_theme_css(c):
    """
    Application DOM par centralized light/dark theme CSS inject karta hai.
    
    Hinglish explanation:
    Yeh function background, sidebar, KPI cards, inputs, multiselects, dropdowns,
    alerts aur buttons ko 100% theme-aware aur readable banata hai.
    """
    css = f"""
    <style>
    /* CSS Variables for theme consistency */
    :root {{
        --bg: {c['background']};
        --sidebar-bg: {c['sidebar_background']};
        --card-bg: {c['card_background']};
        --border: {c['border']};
        --text: {c['text']};
        --text-secondary: {c['secondary_text']};
        --text-muted: {c['muted_text']};
        --accent: {c['accent']};
        --accent-hover: {c['accent_hover']};
        --pos: {c['positive']};
        --neg: {c['negative']};
        --neu: {c['neutral']};
    }}

    /* Global Transitions (180ms - 250ms smooth transition) */
    html, body, .stApp, [data-testid="stSidebar"], [data-testid="stMetric"], [data-testid="stExpander"], [data-testid="stForm"] {{
        transition: background-color 0.22s ease, border-color 0.22s ease, color 0.22s ease;
    }}

    /* Respect prefers-reduced-motion */
    @media (prefers-reduced-motion: reduce) {{
        *, html, body, .stApp {{
            transition: none !important;
            animation: none !important;
        }}
    }}

    /* Main App Background & Typography */
    .stApp {{
        background-color: {c['background']} !important;
        color: {c['text']} !important;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        color: {c['text']} !important;
        font-weight: 700 !important;
    }}
    p, span, label {{
        color: {c['text']};
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: {c['sidebar_background']} !important;
        border-right: 1px solid {c['border']} !important;
    }}
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label {{
        color: {c['text']} !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: {c['border']} !important;
    }}

    /* Sun/Moon Toggle Button (Pill Switch with Subtle Purple Glow) */
    .st-key-theme_toggle_switch button {{
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
        border-radius: 9999px !important;
        padding: 6px 16px !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        border: 1.5px solid {c['border']} !important;
        background-color: {c['card_background']} !important;
        color: {c['text']} !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06) !important;
        cursor: pointer !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    .st-key-theme_toggle_switch button:hover {{
        border-color: {c['accent']} !important;
        color: {c['accent']} !important;
        box-shadow: 0 0 0 3px rgba(109, 61, 245, 0.16) !important;
        transform: translateY(-1px) !important;
    }}
    .st-key-theme_toggle_switch button:active {{
        transform: translateY(0px) !important;
    }}

    /* Demonstration Notice Banner */
    .demo-notice-banner {{
        background-color: {c['banner_bg']} !important;
        border: 1px solid {c['banner_border']} !important;
        color: {c['banner_text']} !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        font-size: 0.88rem !important;
        margin-bottom: 1rem !important;
    }}
    .demo-notice-banner strong {{
        color: {c['banner_text']} !important;
    }}

    /* KPI Metric Cards */
    [data-testid="stMetric"] {{
        background-color: {c['card_background']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 10px !important;
        padding: 14px 18px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    }}
    [data-testid="stMetricLabel"] p {{
        color: {c['secondary_text']} !important;
        font-weight: 600 !important;
        font-size: 0.84rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }}
    [data-testid="stMetricValue"] div {{
        color: {c['text']} !important;
        font-weight: 700 !important;
        font-size: 1.6rem !important;
    }}
    [data-testid="stMetricDelta"] div {{
        font-size: 0.82rem !important;
        font-weight: 600 !important;
    }}

    /* Multiselect & Selectbox Container */
    [data-baseweb="select"] > div {{
        background-color: {c['card_background']} !important;
        border-color: {c['border']} !important;
        color: {c['text']} !important;
        border-radius: 8px !important;
    }}
    [data-baseweb="select"] span {{
        color: {c['text']} !important;
    }}
    
    /* Multiselect Tag / Pill */
    [data-baseweb="tag"] {{
        background-color: {c['tag_bg']} !important;
        border: 1px solid {c['tag_border']} !important;
        border-radius: 6px !important;
    }}
    [data-baseweb="tag"] span {{
        color: {c['accent']} !important;
        font-weight: 600 !important;
    }}
    [data-baseweb="tag"] svg {{
        fill: {c['accent']} !important;
    }}

    /* Dropdown Menus / Popovers */
    [data-baseweb="popover"], [data-baseweb="menu"] {{
        background-color: {c['card_background']} !important;
        border: 1px solid {c['border']} !important;
    }}
    [data-baseweb="menu"] li {{
        background-color: {c['card_background']} !important;
        color: {c['text']} !important;
    }}
    [data-baseweb="menu"] li:hover {{
        background-color: {c['tag_bg']} !important;
        color: {c['accent']} !important;
    }}

    /* Date Input */
    [data-testid="stDateInput"] input {{
        background-color: {c['card_background']} !important;
        color: {c['text']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 8px !important;
    }}

    /* Inputs & Textareas */
    input[type="text"], textarea {{
        background-color: {c['card_background']} !important;
        color: {c['text']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 8px !important;
    }}
    input::placeholder, textarea::placeholder {{
        color: {c['muted_text']} !important;
    }}

    /* File Uploader Dropzone */
    [data-testid="stFileUploadDropzone"] {{
        background-color: {c['card_background']} !important;
        border: 1.5px dashed {c['border']} !important;
        border-radius: 10px !important;
    }}
    [data-testid="stFileUploadDropzone"] span, 
    [data-testid="stFileUploadDropzone"] small {{
        color: {c['secondary_text']} !important;
    }}
    [data-testid="stFileUploadDropzone"] button {{
        background-color: {c['card_background']} !important;
        border: 1px solid {c['border']} !important;
        color: {c['text']} !important;
    }}

    /* Expanders */
    [data-testid="stExpander"] {{
        background-color: {c['card_background']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 10px !important;
    }}
    [data-testid="stExpander"] summary span {{
        color: {c['text']} !important;
        font-weight: 600 !important;
    }}

    /* Form Containers */
    [data-testid="stForm"] {{
        background-color: {c['card_background']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 10px !important;
        padding: 18px !important;
    }}

    /* Standard Buttons */
    .stButton > button {{
        background-color: {c['card_background']} !important;
        color: {c['text']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{
        border-color: {c['accent']} !important;
        color: {c['accent']} !important;
    }}

    /* Primary Purple Download Buttons */
    .stDownloadButton > button {{
        background-color: {c['accent']} !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12) !important;
        transition: all 0.2s ease !important;
    }}
    .stDownloadButton > button:hover {{
        background-color: {c['accent_hover']} !important;
        color: #FFFFFF !important;
        transform: translateY(-1px) !important;
    }}

    /* Dataframe Table Container */
    [data-testid="stDataFrame"] {{
        background-color: {c['card_background']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 8px !important;
    }}

    /* Dividers */
    hr {{
        border-color: {c['border']} !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ---------------------------------------------------------
# DATA LOADING & CACHING HELPERS
# ---------------------------------------------------------
def load_initial_sample_data():
    """
    Default sample CSV (50 reviews, 2020-2026) ko read karke VADER se analyze karta hai.
    
    Hinglish explanation:
    Yeh function sample_feedback.csv ko read karta hai aur sentiment analysis
    sirf ek baar run karke analyzed DataFrame return karta hai.
    """
    if os.path.exists(SAMPLE_FILE_PATH):
        df = pd.read_csv(SAMPLE_FILE_PATH)
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        return analyze_dataframe(df)
    else:
        st.error(f"Sample data file not found at: {SAMPLE_FILE_PATH}")
        return pd.DataFrame(columns=["airline", "date", "feedback", "sentiment", "compound_score"])


@st.cache_data(show_spinner=False)
def get_cached_pdf_report(df_to_export):
    """
    ReportLab PDF generation ko cache karta hai taaki har filter interaction par
    Matplotlib aur ReportLab unnecessarily repeatedly run na ho.
    
    Hinglish explanation:
    Yeh function PDF report ko memory me cache karta hai jisse chart rendering
    aur filter changes smooth aur fast rehte hain.
    """
    return generate_pdf_report(df_to_export)


# ---------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------
# Theme preference preservation (default: dark)
if "theme" not in st.session_state:
    param_theme = st.query_params.get("theme", "dark")
    st.session_state["theme"] = "light" if param_theme == "light" else "dark"

# Active dataset preservation
if "active_df" not in st.session_state:
    st.session_state["active_df"] = load_initial_sample_data()

if "data_source_name" not in st.session_state:
    st.session_state["data_source_name"] = "Sample Dataset (50 Reviews, 2020–2026)"

# Retrieve and inject current theme colors
theme_colors = get_theme_colors(st.session_state["theme"])
apply_theme_css(theme_colors)


# ---------------------------------------------------------
# HEADER SECTION WITH ANIMATED SUN/MOON TOGGLE
# ---------------------------------------------------------
head_col1, head_col2 = st.columns([3.4, 1.2])

with head_col1:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
            <span style="font-size: 2.2rem;">✈️</span>
            <div>
                <h1 style="margin: 0; font-size: 1.65rem; font-weight: 700; line-height: 1.2;">Airline Customer Sentiment Analyzer</h1>
                <p style="margin: 3px 0 0 0; font-size: 0.88rem; color: {theme_colors['secondary_text']};">
                    Analyze airline customer feedback using Python and VADER sentiment analysis.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with head_col2:
    st.write("")  # Vertical alignment spacing
    is_dark = st.session_state["theme"] == "dark"
    # Modern Sun/Moon icon toggle switch
    # Dark Mode active: shows Moon icon (🌙), tooltip communicates click switches to Light Mode
    # Light Mode active: shows Sun icon (☀️), tooltip communicates click switches to Dark Mode
    toggle_icon = "🌙" if is_dark else "☀️"
    toggle_label = "Dark Mode" if is_dark else "Light Mode"
    toggle_tooltip = "Switch to Light Mode" if is_dark else "Switch to Dark Mode"

    if st.button(
        f"{toggle_icon}  {toggle_label}",
        key="theme_toggle_switch",
        help=toggle_tooltip,
        use_container_width=True,
    ):
        st.session_state["theme"] = "light" if is_dark else "dark"
        st.query_params["theme"] = st.session_state["theme"]
        st.rerun()

# Refined Demonstration Banner (Theme-consistent background & contrast)
st.markdown(
    f"""
    <div class="demo-notice-banner">
        📌 <strong>Demonstration Notice:</strong> Currently analyzing 50 synthetic airline customer reviews spanning 
        <strong>2020 through 2026</strong> across 5 carriers. Predictions and compound polarity scores are computed via rule-based VADER sentiment analysis.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# SIDEBAR: DATA MANAGEMENT & FILTERS
# ---------------------------------------------------------
st.sidebar.markdown(f"<h3 style='margin-top: 0;'>📁 Data Source & Upload</h3>", unsafe_allow_html=True)

# Reset button to restore initial 50 sample reviews
if st.sidebar.button("🔄 Reload Sample Dataset (2020–2026)", use_container_width=True):
    st.session_state["active_df"] = load_initial_sample_data()
    st.session_state["data_source_name"] = "Sample Dataset (50 Reviews, 2020–2026)"
    # Clear filter keys to reset views
    for key in ["airline_filter_key", "sentiment_filter_key", "date_range_filter_key"]:
        if key in st.session_state:
            del st.session_state[key]
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
                f"Missing required columns! Found: {list(raw_uploaded_df.columns)}. "
                "Required: airline, date, feedback"
            )
        else:
            # Handle empty feedback and airlines safely
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
                # Analyze newly uploaded reviews once and store in session state
                analyzed_uploaded_df = analyze_dataframe(valid_df)
                st.session_state["active_df"] = analyzed_uploaded_df
                st.session_state["data_source_name"] = f"Uploaded File ({uploaded_file.name})"
                # Clear filter keys to match new data range
                for key in ["airline_filter_key", "sentiment_filter_key", "date_range_filter_key"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.sidebar.success(f"Loaded and analyzed {len(valid_df)} valid reviews!")

    except Exception as e:
        st.sidebar.error(f"Error reading uploaded file: {str(e)}")

st.sidebar.caption(f"**Active Source:** {st.session_state['data_source_name']}")
st.sidebar.divider()

# Sidebar: Filters
st.sidebar.markdown(f"<h3>🔍 Filter Reviews</h3>", unsafe_allow_html=True)

active_df = st.session_state["active_df"]

if not active_df.empty:
    # 1. Airline filter
    all_airlines = sorted(active_df["airline"].dropna().unique().tolist())
    selected_airlines = st.sidebar.multiselect(
        "Select Airline(s):",
        options=all_airlines,
        default=all_airlines,
        key="airline_filter_key",
    )

    # 2. Sentiment filter
    all_sentiments = ["Positive", "Negative", "Neutral"]
    selected_sentiments = st.sidebar.multiselect(
        "Select Sentiment(s):",
        options=all_sentiments,
        default=all_sentiments,
        key="sentiment_filter_key",
    )

    # 3. Date Range filter (spanning 2020 to 2026)
    date_series = pd.to_datetime(active_df["date"])
    min_date = date_series.min().date()
    max_date = date_series.max().date()

    if min_date == max_date:
        start_date = min_date
        end_date = max_date
        st.sidebar.info(f"Single date available: {min_date}")
    else:
        date_selection = st.sidebar.date_input(
            "Select Date Range (2020 – 2026):",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_range_filter_key",
        )
        if isinstance(date_selection, tuple) and len(date_selection) == 2:
            start_date, end_date = date_selection
        elif isinstance(date_selection, tuple) and len(date_selection) == 1:
            # Prevent intermediate 1-day flash while picking second date
            start_date = date_selection[0]
            end_date = max_date
        else:
            start_date, end_date = min_date, max_date

    # Reset filters button
    if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
        for key in ["airline_filter_key", "sentiment_filter_key", "date_range_filter_key"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # Apply filters to get a single, consistent filtered DataFrame
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
# SECTION: KPI SUMMARY METRICS
# ---------------------------------------------------------
st.markdown(f"<h3 style='margin-bottom: 12px;'>📊 Sentiment Overview Metrics</h3>", unsafe_allow_html=True)

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
        help="Total customer reviews matching active filters",
    )

with col2:
    st.metric(
        label="Positive Reviews",
        value=f"{kpis['positive']} ({kpis['pos_percent']}%)",
        delta="Positive",
        delta_color="normal",
        help="Reviews with VADER compound score >= 0.05",
    )

with col3:
    st.metric(
        label="Negative Reviews",
        value=f"{kpis['negative']} ({kpis['neg_percent']}%)",
        delta="Negative",
        delta_color="inverse",
        help="Reviews with VADER compound score <= -0.05",
    )

with col4:
    st.metric(
        label="Neutral Reviews",
        value=f"{kpis['neutral']} ({kpis['neu_percent']}%)",
        delta="Neutral",
        delta_color="off",
        help="Reviews with VADER compound score between -0.05 and +0.05",
    )

st.divider()


# ---------------------------------------------------------
# SECTION: MANUAL REVIEW SIMULATOR (SESSION ONLY)
# ---------------------------------------------------------
with st.expander("✍️ Add a New Customer Review (Session Only)", expanded=False):
    st.markdown(
        f"<p style='color: {theme_colors['secondary_text']}; margin-top: 0;'>"
        "Enter customer feedback below to test real-time VADER prediction. "
        "<em>This review exists only in your current browser session and will not alter the sample CSV.</em></p>",
        unsafe_allow_html=True,
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
            placeholder="e.g., The cabin crew was polite and the flight landed ahead of schedule!",
        )

        submit_review = st.form_submit_button("Analyze & Add Review")

        if submit_review:
            if not manual_text or not manual_text.strip():
                st.warning("Please enter review text before submitting.")
            else:
                pred_sentiment, pred_score = analyze_sentiment(manual_text)
                
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

                st.session_state["active_df"] = pd.concat([st.session_state["active_df"], new_row], ignore_index=True)
                st.success(
                    f"✅ Review analyzed and added! Predicted Sentiment: **{pred_sentiment}** "
                    f"(VADER Compound Score: {pred_score:+.4f})"
                )
                st.rerun()


# ---------------------------------------------------------
# SECTION: INTERACTIVE PLOTLY VISUALIZATIONS
# ---------------------------------------------------------
st.markdown(f"<h3>📈 Interactive Sentiment Visualizations</h3>", unsafe_allow_html=True)

# Chart builder functions with theme awareness
def build_sentiment_distribution_chart(dist_df, colors):
    """Overall Sentiment Distribution Bar Chart banata hai."""
    sentiment_color_map = {
        "Positive": colors["positive"],
        "Negative": colors["negative"],
        "Neutral": colors["neutral"],
    }
    fig = px.bar(
        dist_df,
        x="sentiment",
        y="count",
        color="sentiment",
        color_discrete_map=sentiment_color_map,
        text="count",
        labels={"sentiment": "Sentiment", "count": "Reviews"},
        title="Chart 1: Overall Sentiment Distribution",
    )
    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        marker=dict(line=dict(width=0)),
    )
    fig.update_layout(
        paper_bgcolor=colors["chart_bg"],
        plot_bgcolor=colors["chart_bg"],
        font=dict(color=colors["text"], family="sans-serif", size=12),
        title=dict(font=dict(color=colors["text"], size=13)),
        showlegend=False,
        height=320,
        margin=dict(t=42, b=25, l=35, r=20),
        xaxis=dict(
            gridcolor=colors["grid"],
            tickfont=dict(color=colors["text"]),
            title=None,
        ),
        yaxis=dict(
            gridcolor=colors["grid"],
            tickfont=dict(color=colors["secondary_text"]),
            title=dict(text="Reviews", font=dict(color=colors["secondary_text"])),
        ),
    )
    return fig


def build_airline_comparison_chart(airline_summary, colors):
    """Airline-wise Grouped Bar Chart banata hai."""
    sentiment_color_map = {
        "Positive": colors["positive"],
        "Negative": colors["negative"],
        "Neutral": colors["neutral"],
    }
    fig = px.bar(
        airline_summary,
        x="airline",
        y="count",
        color="sentiment",
        barmode="group",
        color_discrete_map=sentiment_color_map,
        labels={"airline": "Airline", "count": "Reviews", "sentiment": "Sentiment"},
        title="Chart 2: Airline-wise Sentiment Comparison",
    )
    fig.update_layout(
        paper_bgcolor=colors["chart_bg"],
        plot_bgcolor=colors["chart_bg"],
        font=dict(color=colors["text"], family="sans-serif", size=12),
        title=dict(font=dict(color=colors["text"], size=13)),
        height=320,
        margin=dict(t=42, b=25, l=35, r=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=colors["text"], size=10),
            title=None,
        ),
        xaxis=dict(
            gridcolor=colors["grid"],
            tickfont=dict(color=colors["text"]),
            title=None,
        ),
        yaxis=dict(
            gridcolor=colors["grid"],
            tickfont=dict(color=colors["secondary_text"]),
            title=dict(text="Reviews", font=dict(color=colors["secondary_text"])),
        ),
    )
    return fig


def build_date_trend_chart(date_summary, colors, is_monthly=True):
    """Date-wise Chronological Trend Line Chart banata hai (2020-2026)."""
    sentiment_color_map = {
        "Positive": colors["positive"],
        "Negative": colors["negative"],
        "Neutral": colors["neutral"],
    }
    title_text = (
        "Chart 3: Monthly Sentiment Trend (Actual Review Months, 2020 – 2026)"
        if is_monthly
        else "Chart 3: Daily Sentiment Observations (2020 – 2026)"
    )
    fig = px.line(
        date_summary,
        x="date",
        y="count",
        color="sentiment",
        markers=True,
        color_discrete_map=sentiment_color_map,
        labels={"date": "Timeline", "count": "Reviews", "sentiment": "Sentiment"},
        title=title_text,
    )
    fig.update_traces(
        line=dict(width=2.5),
        marker=dict(size=6),
    )
    fig.update_layout(
        paper_bgcolor=colors["chart_bg"],
        plot_bgcolor=colors["chart_bg"],
        font=dict(color=colors["text"], family="sans-serif", size=12),
        title=dict(font=dict(color=colors["text"], size=13)),
        height=320,
        margin=dict(t=42, b=25, l=35, r=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=colors["text"], size=10),
            title=None,
        ),
        xaxis=dict(
            type="date",
            tickformat="%b %Y",
            gridcolor=colors["grid"],
            tickfont=dict(color=colors["text"]),
            title=None,
        ),
        yaxis=dict(
            gridcolor=colors["grid"],
            tickfont=dict(color=colors["secondary_text"]),
            title=dict(text="Reviews", font=dict(color=colors["secondary_text"])),
        ),
    )
    return fig


if filtered_df.empty:
    st.info("No data available to render charts. Please reset or broaden the sidebar filters.")
else:
    # Row 1: Distribution & Airline Comparison
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        dist_df = get_sentiment_distribution(filtered_df)
        fig_dist = build_sentiment_distribution_chart(dist_df, theme_colors)
        st.plotly_chart(fig_dist, use_container_width=True, key="fig_sentiment_dist")

    with chart_col2:
        airline_summary = get_airline_sentiment_summary(filtered_df)
        fig_airline = build_airline_comparison_chart(airline_summary, theme_colors)
        st.plotly_chart(fig_airline, use_container_width=True, key="fig_airline_comp")

    # Row 2: Date-wise Sentiment Trend spanning full width
    date_summary_monthly = get_date_sentiment_summary(filtered_df, frequency="monthly")
    if not date_summary_monthly.empty:
        fig_trend = build_date_trend_chart(date_summary_monthly, theme_colors, is_monthly=True)
        st.plotly_chart(fig_trend, use_container_width=True, key="fig_date_trend")
    else:
        st.info("Insufficient date observations to render trend line.")

st.divider()


# ---------------------------------------------------------
# SECTION: REVIEW DATA TABLE
# ---------------------------------------------------------
st.markdown(f"<h3>📋 Analyzed Customer Reviews</h3>", unsafe_allow_html=True)

if filtered_df.empty:
    st.info("No reviews available to display in table.")
else:
    display_table = filtered_df[["airline", "date", "feedback", "sentiment", "compound_score"]].copy()
    display_table.columns = ["Airline", "Date", "Customer Feedback", "Predicted Sentiment", "Compound Score"]

    st.dataframe(
        display_table.style.format({"Compound Score": "{:+.4f}"}),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(f"Showing {len(display_table)} review records matching active filters.")


# ---------------------------------------------------------
# SECTION: EXPORT & REPORTS
# ---------------------------------------------------------
st.markdown(f"<h3>📥 Export & Reports</h3>", unsafe_allow_html=True)

col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    st.markdown("##### Download Analyzed Data (CSV)")
    st.caption("Exports currently filtered reviews with predicted sentiments and scores.")

    if not filtered_df.empty:
        csv_buffer = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Filtered Results (CSV)",
            data=csv_buffer,
            file_name="airline_sentiment_results.csv",
            mime="text/csv",
            use_container_width=True,
            key="btn_download_csv",
        )
    else:
        st.button("⬇️ Download Filtered Results (CSV)", disabled=True, use_container_width=True, key="btn_download_csv_disabled")

with col_exp2:
    st.markdown("##### Download PDF Summary Report")
    st.caption("Generates a formal college project report with KPIs, tables, and chart.")

    if not filtered_df.empty:
        # Caching PDF generation avoids repeated Matplotlib rendering on unrelated UI actions
        pdf_bytes, pdf_error = get_cached_pdf_report(filtered_df)
        if pdf_bytes:
            st.download_button(
                label="📄 Download PDF Summary Report",
                data=pdf_bytes,
                file_name="airline_sentiment_report.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="btn_download_pdf",
            )
        else:
            st.error(f"Could not generate PDF: {pdf_error}")
    else:
        st.button("📄 Download PDF Summary Report", disabled=True, use_container_width=True, key="btn_download_pdf_disabled")


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
        - It does not understand domain-specific aviation jargon without manual custom lexicon entries.
        - Sample dataset dates span **2020 through 2026** for chronological trend demonstration purposes.
        """
    )
