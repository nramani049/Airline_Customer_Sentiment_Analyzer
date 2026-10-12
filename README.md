# ✈️ Airline Customer Sentiment Analyzer (Flask + HTML/CSS/JS)

A polished, full-stack web application for college-level **Social Media Analytics / Data Analytics** project demonstrations. The application analyzes customer reviews using **Python & VADER Sentiment Analysis**, serves responsive data via a lightweight **Flask REST API**, and renders an interactive, minimal analytics dashboard with **HTML5, CSS3, Vanilla JavaScript, and Chart.js**.

---

## 📌 Project Overview

* **Domain:** Social Media Analytics / Customer Experience Analytics
* **Frontend:** HTML5, CSS3, Vanilla JavaScript, Chart.js (via CDN)
* **Backend:** Python 3.11+ with Flask REST API
* **Architecture:** Session-isolated in-memory store (Zero database, zero permanent disk writes)
* **Sentiment Engine:** VADER (*Valence Aware Dictionary and sEntiment Reasoner*)
* **Reporting:** In-memory ReportLab PDF generator & CSV export
* **Themes:** ☀️ Light Mode (Default clean grey/purple) & 🌙 Dark Mode (Charcoal/violet) with an animated Sun/Moon toggle
* **Sample Dataset:** Exactly 50 synthetic airline customer reviews spanning **2020 through 2026**

---

## ✨ Key Features & Enhancements

1. **Native HTML5 & CSS3 Dashboard:** Complete UI control with responsive CSS Grid and Flexbox layouts—replacing rigid Streamlit component constraints.
2. **Vanilla JavaScript & Asynchronous Requests:** Dynamic filtering via `fetch('/api/dashboard?...')`. Changing filters updates KPIs, Chart.js canvases, and data tables **without full-page reloads**.
3. **Animated Sun/Moon Theme Toggle:** A compact pill toggle that smoothly transitions between an elegant light theme and a modern dark analytics theme. Theme state is saved in `localStorage`.
4. **Chart.js Visualizations (Zero DOM Recreation):**
   * **Chart 1:** Overall Sentiment Distribution (Doughnut chart with hover percentages).
   * **Chart 2:** Airline-wise Sentiment Comparison (Grouped bar chart).
   * **Chart 3:** Date-wise Sentiment Trend (Multi-year timeline with Monthly and Daily toggles).
   * Charts dynamically update datasets and color palettes without redrawing the DOM or recalculating VADER scores.
5. **Session-Isolated In-Memory Storage:** Each browser session gets an isolated dataset in server RAM via signed session cookies (`USER_SESSIONS[sid]`). User A cannot see User B's manual entries or uploaded CSVs.
6. **VADER Sentiment Engine:** Automatic polarity scoring and compound threshold assignment:
   * $\ge +0.05 \rightarrow$ **Positive**
   * $\le -0.05 \rightarrow$ **Negative**
   * Otherwise $\rightarrow$ **Neutral**
7. **CSV Upload & Manual Review Simulator:** Upload custom CSV files or submit single customer reviews directly from the web interface.
8. **In-Memory CSV & PDF Exports:** Download filtered analyzed results as CSV or as an academic ReportLab PDF report generated in RAM (`io.BytesIO`).
9. **Preserved Streamlit Backup:** The original working Streamlit code is preserved in `app_streamlit_backup.py`.

---

## 🛠️ Technology Stack & Hinglish Explanations

| Technology | Purpose | One-Line Hinglish Explanation |
| :--- | :--- | :--- |
| **Python** | Backend Programming | Python backend mein business logic, sentiment analysis aur PDF generation handle karta hai. |
| **Flask** | Web Framework & Routing | Flask HTTP requests ko route karta hai aur dynamic JSON REST API endpoints provide karta hai. |
| **HTML5 & CSS3** | Frontend UI & Styling | HTML5 semantic structure banata hai aur CSS3 custom properties se responsive light/dark themes deta hai. |
| **Vanilla JavaScript** | Asynchronous Interactions | JavaScript bina page reload kiye `fetch()` API se backend se data laakar DOM aur charts update karta hai. |
| **Chart.js** | Interactive Visualizations | Chart.js kam code mein smooth, theme-aware bar, doughnut aur line charts render karta hai. |
| **Pandas** | Tabular Data Handling | Pandas CSV data ko DataFrame mein convert karke filtering aur calculations fast perform karta hai. |
| **VADER Sentiment** | Lexicon Rule-Based Scoring | VADER customer reviews ke words aur emojis ko analyze karke compound score aur sentiment label deta hai. |
| **ReportLab** | PDF Report Generation | ReportLab in-memory summary report banata hai jise user direct download kar sakta hai. |

---

## 📂 Project Structure

```text
d:\SMA_Pro\
│
├── app.py                     # Flask web server, REST API endpoints, session store
├── app_streamlit_backup.py     # Preserved original Streamlit application
├── requirements.txt           # Project dependencies
├── README.md                  # Complete documentation and viva guide
├── test_workflow.py           # Automated 21-point verification test suite
│
├── data/
│   └── sample_feedback.csv   # Exactly 50 synthetic airline customer reviews (2020–2026)
│
├── modules/
│   ├── __init__.py            # Package initializer
│   ├── sentiment.py           # VADER analyzer initialization and classification logic
│   ├── analytics.py           # KPIs, theme colors, aggregations, and multi-criteria filters
│   └── report_generator.py    # In-memory ReportLab PDF generator with static chart
│
├── static/
│   ├── css/
│   │   └── style.css          # Theme custom properties, layout, components, toggle animation
│   └── js/
│       └── app.js             # Theme toggle, fetch API, Chart.js managers, table renderer
│
└── templates/
    └── index.html             # Clean semantic HTML5 dashboard
```

---

## 💻 Windows Setup & Startup Instructions

Follow these exact steps from the project root folder (`d:\SMA_Pro`):

### Step 1: Open PowerShell
```powershell
cd d:\SMA_Pro
```

### Step 2: Activate the Virtual Environment
```powershell
.venv\Scripts\Activate.ps1
```
*(Or in Command Prompt: `.venv\Scripts\activate.bat`)*

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Flask Application
```powershell
python app.py
```

The application will start on:
👉 **`http://127.0.0.1:5000`**

Open `http://127.0.0.1:5000` in any web browser to access the dashboard.

### Step 5: (Optional) Run Automated Verification Tests
```powershell
python test_workflow.py
```

*(Note: To run the legacy Streamlit backup version instead, execute: `streamlit run app_streamlit_backup.py`)*

---

## 🌐 Flask REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Renders the HTML5 dashboard (`index.html`). |
| `GET` | `/api/dashboard` | Returns JSON containing filtered KPIs, Chart.js datasets, reviews, and filter bounds. |
| `POST` | `/api/upload` | Accepts multipart CSV upload, validates columns, analyzes reviews with VADER, updates session. |
| `POST` | `/api/reviews` | Accepts JSON review (`airline`, `date`, `feedback`), predicts sentiment, appends to session. |
| `POST` | `/api/reset-sample` | Restores the session dataset back to the baseline 50 sample reviews. |
| `GET` | `/api/export/csv` | Streams filtered reviews as a downloadable CSV attachment. |
| `GET` | `/api/export/pdf` | Generates and streams the ReportLab PDF summary report in memory. |

---

## 🎨 Theme Architecture (CSS Custom Properties)

* **☀️ Light Theme (Default):**
  * Page background: `#F7F8FC`
  * Sidebar & Card surfaces: `#FFFFFF`
  * Text: `#172033` (Secondary: `#5F6B7A`, Muted: `#778196`)
  * Border: `#E3E7EF`
  * Primary Accent: `#6D3DF5` (Hover: `#5B2FE0`)
* **🌙 Dark Theme:**
  * Page background: `#0F1117`
  * Sidebar surface: `#171A23`
  * Card surfaces: `#191D28`
  * Text: `#F4F5FA` (Secondary: `#B7BDCB`, Muted: `#929AAC`)
  * Border: `#2B3040`
  * Primary Accent: `#9270FF` (Hover: `#A48AFF`)
* **Sentiment Accents:**
  * Positive: `#159A63` (Light) / `#35C98A` (Dark)
  * Negative: `#DC4545` (Light) / `#FF6666` (Dark)
  * Neutral: `#778196` (Light) / `#A0A7B5` (Dark)

---

## 💾 Session-Only In-Memory Storage

* **No Database:** No SQLite, MySQL, or MongoDB is used.
* **Isolation:** Each user's dataset is stored in `USER_SESSIONS[sid]` in server RAM, keyed by a signed HTTP-only cookie `session['sid']`.
* **Zero Disk Modification:** Uploaded files and manual reviews are held only in memory. The committed `data/sample_feedback.csv` is read-only and never modified.
* **Restart Behavior:** When the Flask server restarts, all in-memory sessions reset to the baseline 50 sample reviews.

---

## 🔄 Code Flow in Simple Hinglish

1. **User Website Kholta Hai:**
   * Browser `http://127.0.0.1:5000` par `GET /` bhejta hai. Flask `index.html` render karta hai aur session initialize karta hai.
2. **Initial Dashboard Load:**
   * `app.js` initialize hota hai, `localStorage` se theme apply karta hai, aur turant `fetch('/api/dashboard')` call karta hai.
3. **Backend Processing:**
   * Flask endpoint session dataset ko analyze karke KPIs, Chart.js friendly JSON, aur review rows return karta hai.
4. **Asynchronous DOM & Chart Update:**
   * `app.js` bina page reload ke KPI cards, Chart.js instances (doughnut, grouped bar, line), aur table rows ko inject karta hai.
5. **Filter Change Interaction:**
   * Jab user sidebar me airline checkbox, sentiment checkbox ya date change karta hai, `app.js` debounced `fetch()` bhejta hai. Flask sirf filtered data return karta hai aur Chart.js `chart.update()` call karta hai.
6. **Sun/Moon Toggle Click:**
   * User header me toggle button click karta hai. JavaScript `data-theme` attribute change karti hai, `localStorage` update karti hai, aur charts ke colors live change ho jaate hain bina kisi page reload ke.
7. **CSV / PDF Export:**
   * Download button click karne par Flask RAM buffer se CSV ya PDF attachment generate karke bhejta hai.

---

## 🔍 Important Functions Explained (One-Line Hinglish)

1. `get_or_create_user_session()`:
   * **Hinglish:** "User ke cookie se session ID check karta hai aur RAM me uska isolated 50-review DataFrame provide karta hai."
2. `get_dashboard_data()`:
   * **Hinglish:** "Filtered reviews ke आधार par KPIs, Chart.js data aur table records JSON format me frontend ko bhejta hai."
3. `add_manual_review()`:
   * **Hinglish:** "Form se review lekar VADER se score karta hai aur user ke session dataset me add karta hai."
4. `upload_csv()`:
   * **Hinglish:** "Uploaded CSV ke columns validate karke VADER run karta hai aur session dataset replace karta hai."
5. `export_pdf()`:
   * **Hinglish:** "ReportLab aur Matplotlib ka use karke filtered summary report PDF in-memory banata hai aur browser ko download bhejta hai."
6. `initTheme()` & `updateAllChartThemes()`:
   * **Hinglish:** "Frontend me Sun/Moon toggle ko handle karta hai aur Chart.js ke text aur gridline colors ko instantly switch karta hai."
7. `fetchDashboardData()`:
   * **Hinglish:** "Sidebar ke active filters ko query string me convert karke Flask se asynchronous data fetch karta hai."

---

## 🎓 Viva Preparation — Questions & Answers

### Q1: Streamlit se Flask + HTML/CSS/JS par kyu migrate kiya?
* **Answer:** Streamlit har user interaction par pure Python script ko rerun karta hai, jisse layout customization, smooth transitions, aur client-side chart responsiveness limited ho jaate the. HTML5/CSS3/JS aur Flask architecture se hume exact pixel-level visual control mila, `fetch()` ke through asynchronous DOM updates mile, aur Chart.js ke through smooth canvas animations mili bina page reload ke.

### Q2: Multi-user session isolation bina database ke kaise kaam karta hai?
* **Answer:** Flask signed cookies ke through har user ko ek unique `session_id` assign karta hai. Server ki RAM me `USER_SESSIONS` dictionary har `session_id` ke liye isolated DataFrame hold karti hai. Isliye User A ka uploaded dataset ya manual review User B ko nahi dikhta.

### Q3: VADER sentiment analysis filter badalne par baar-baar run kyu nahi hota?
* **Answer:** Sentiment calculation computationally expensive ho sakti hai. Isliye VADER sirf tab execute hota hai jab pehli baar sample load hota hai, naya CSV upload hota hai, ya manual review submit hota hai. Filter badalne par Pandas sirf already-analyzed columns (`sentiment`, `compound_score`) par boolean filtering perform karta hai.

### Q4: Chart.js me theme switch karte waqt charts blink ya duplicate kyu nahi hote?
* **Answer:** Hum canvas elements ko delete nahi karte. Hum existing `Chart` instance ke `options.scales`, `grid.color`, aur `legend.labels.color` ko modify karke `chart.update()` call karte hain. Isse chart seamlessly naye colors adapt kar leta hai bina reload ke.

---

## ⏱️ 60-Second Presentation Script (Hinglish)

> *"Good morning respected teachers. Humara project hai **Airline Customer Sentiment Analyzer** jo Social Media Analytics subject ke liye banaya gaya hai.*
>
> *Is project ko humne **Streamlit se genuine Full-Stack Python architecture** par migrate kiya hai jisme backend **Flask REST API** hai aur frontend **HTML5, CSS3, Vanilla JavaScript aur Chart.js** se bana hai.*
>
> *Humne 50 customer reviews ka 2020 se 2026 tak ka synthetic dataset incorporate kiya hai. Application VADER rule-based sentiment engine se har review ka compound score predict karti hai aur Positive, Negative ya Neutral label deti hai.*
>
> *Features me animated Sun/Moon light/dark mode switch, dynamic KPI cards, Chart.js se interactive doughnut, grouped bar aur monthly trend charts, manual review simulator, custom CSV upload, aur in-memory CSV/PDF export shamil hain bina kisi external database ke. Thank you!"*
