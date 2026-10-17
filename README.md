# Airline Customer Sentiment Analyzer

A web application for analyzing customer feedback across airlines using Python, VADER Sentiment Analysis, Flask, and Chart.js.

## Overview

* **Backend:** Python with Flask REST API
* **Frontend:** HTML5, CSS3, Vanilla JavaScript, Chart.js
* **Sentiment Engine:** VADER (*Valence Aware Dictionary and sEntiment Reasoner*)
* **Architecture:** Session-isolated in-memory storage (no database required)
* **Reporting:** In-memory CSV export and ReportLab PDF report generation
* **Themes:** Light and Dark modes with responsive dashboard layout

## Features

1. **Interactive Analytics Dashboard:** Real-time metrics and dynamic filtering by airline, sentiment, and date range without full-page reloads.
2. **Visualizations:**
   * **Chart 1:** Overall Sentiment Distribution (Doughnut chart)
   * **Chart 2:** Airline-wise Sentiment Comparison (Grouped bar chart)
   * **Chart 3:** Date-wise Sentiment Trend (Multi-year timeline with Monthly and Daily views)
3. **Session-Isolated In-Memory Storage:** Each user session receives an isolated dataset in memory; changes do not alter the baseline sample file.
4. **VADER Sentiment Engine:** Automatic classification into Positive ($\ge +0.05$), Negative ($\le -0.05$), or Neutral.
5. **Data Import & Simulation:** Support for CSV upload and manual review submission.
6. **Report Generation:** Downloadable filtered CSV and in-memory PDF summary reports.

## Project Structure

```text
d:\SMA_Pro\
│
├── app.py                     # Flask application and REST API endpoints
├── app_streamlit_backup.py     # Preserved original Streamlit application
├── requirements.txt           # Project dependencies
├── README.md                  # Documentation
├── test_workflow.py           # Verification test suite
│
├── data/
│   └── sample_feedback.csv   # Baseline sample customer reviews
│
├── modules/
│   ├── __init__.py            # Package initializer
│   ├── sentiment.py           # VADER sentiment analysis
│   ├── analytics.py           # Metrics, aggregations, and filtering
│   └── report_generator.py    # In-memory PDF report generation
│
├── static/
│   ├── css/
│   │   └── style.css          # Application stylesheet and theme variables
│   └── js/
│       └── app.js             # Frontend API interaction, charts, and DOM management
│
└── templates/
    └── index.html             # Dashboard HTML template
```

## Setup and Installation

### Prerequisites

* Python 3.11 or higher
* PowerShell or Command Prompt

### Step 1: Create Virtual Environment

```powershell
python -m venv venv
```

### Step 2: Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

*(On Command Prompt, run: `.\venv\Scripts\activate.bat`)*

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Run Application

```powershell
python app.py
```

Access the application in your browser at:
`http://127.0.0.1:5000`

### Step 5: (Optional) Run Test Suite

```powershell
python test_workflow.py
```

## REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Renders the dashboard template. |
| `GET` | `/api/dashboard` | Returns filtered KPI metrics, chart datasets, and review rows. |
| `POST` | `/api/upload` | Uploads and analyzes a custom CSV file (`airline`, `date`, `feedback`). |
| `POST` | `/api/reviews` | Analyzes and appends a manual customer review to the active session. |
| `POST` | `/api/reset-sample` | Resets the active session back to baseline sample reviews. |
| `GET` | `/api/export/csv` | Streams filtered reviews as a downloadable CSV. |
| `GET` | `/api/export/pdf` | Generates and streams a PDF summary report. |

## Supported Input Formats

For CSV file upload, the file must contain the following headers:
* `airline`: Name of the airline
* `date`: Review date (`YYYY-MM-DD` recommended)
* `feedback`: Customer review text
