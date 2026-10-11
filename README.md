# ✈️ Airline Customer Sentiment Analyzer

A beginner-friendly Python web application built for college-level **Social Media Analytics / Data Analytics** project demonstrations. The application analyzes customer reviews for major airlines using **VADER Sentiment Analysis**, visualizes actionable insights through an interactive **Streamlit** dashboard, and allows exporting results as **CSV** and **PDF** summary reports.

---

## 📌 Project Overview

* **Domain:** Social Media Analytics / Customer Experience Analytics
* **Target Audience:** College project demonstration (Viva, Lab evaluation)
* **Team Size:** 3 Members
* **Sample Dataset Size:** Exactly 50 synthetic airline customer reviews
* **Sentiment Engine:** VADER (*Valence Aware Dictionary and sEntiment Reasoner*)
* **Architecture:** Session-based in-memory application (No database, no permanent storage, no cloud servers)

---

## ✨ Key Features

1. **Preloaded 50-Review Dataset:** Comes with exactly 50 realistic customer reviews across 5 major Indian carriers (`IndiGo`, `Air India`, `SpiceJet`, `Vistara`, `Akasa Air`).
2. **Automated VADER Sentiment Scoring:** Calculates normalized compound polarity scores (`-1.0` to `+1.0`) and assigns labels (`Positive`, `Negative`, `Neutral`).
3. **Custom CSV Upload & Validation:** Supports uploading custom review files with automatic validation of required columns, date formats, and empty row exclusion.
4. **Interactive Dashboard & KPI Cards:** Real-time metrics for Total Reviews, Positive Reviews, Negative Reviews, and Neutral Reviews (where `Total = Positive + Negative + Neutral`).
5. **Interactive Plotly Visualizations:**
   * **Chart 1:** Overall Sentiment Distribution (Bar chart with standard green/red/gray color coding).
   * **Chart 2:** Airline-wise Sentiment Comparison (Grouped bar chart).
   * **Chart 3:** Date-wise Sentiment Trend (Chronological line chart).
6. **Dynamic Sidebar Filters:** Filter records simultaneously by Airline, Sentiment label, and Date range.
7. **Manual Review Simulator:** Test real-time VADER scoring on any custom sentence directly in the web UI.
8. **Filtered Data CSV Export:** Download currently filtered review rows with scores as Excel-compatible CSV.
9. **PDF Summary Report Generation:** Automatically generate and download a formal academic PDF report using ReportLab with embedded KPI table, airline breakdown, static chart, and methodology notes.
10. **Zero Database Footprint:** Runs entirely in RAM via `st.session_state` without altering source CSVs.

---

## 🛠️ Technology Stack & Hinglish Explanations

| Technology | Purpose | One-Line Hinglish Explanation |
| :--- | :--- | :--- |
| **Python 3.11+** | Core Programming Language | Python mein humne application ka core logic aur saari processing clean functions ke roop mein likhi hai. |
| **Streamlit** | Web Interface & Dashboard | Streamlit Python code se bina complex HTML/CSS ke interactive web app aur dynamic dashboard banata hai. |
| **Pandas** | Tabular Data & CSV Processing | Pandas CSV ko DataFrame mein convert karke reviews ko read, filter aur analyze karne mein help karta hai. |
| **VADER Sentiment** | Lexicon-based Sentiment Scoring | VADER review ke words aur expressions ko analyze karke Positive, Negative ya Neutral sentiment predict karta hai. |
| **Plotly Express** | Interactive Data Visualizations | Plotly Express kam code mein interactive bar charts aur line charts render karta hai. |
| **ReportLab** | PDF Report Generation | ReportLab Python se sentiment summary aur review statistics ki downloadable PDF report banata hai. |
| **Matplotlib** | Static Chart for PDF | Matplotlib PDF report ke andar static bar chart image embed karne ke liye use hota hai. |

---

## 📂 Project Structure

```text
airline-sentiment-analyzer/
│
├── app.py                     # Streamlit frontend dashboard, session state, UI widgets
├── requirements.txt           # Project dependencies
├── README.md                  # Complete documentation and viva guide
│
├── data/
│   └── sample_feedback.csv   # Exactly 50 synthetic airline customer reviews
│
└── modules/
    ├── __init__.py            # Package initializer
    ├── sentiment.py           # VADER analyzer initialization and classification logic
    ├── analytics.py           # KPI calculations, aggregations, and multi-criteria filters
    └── report_generator.py    # In-memory ReportLab PDF generator with static chart
```

---

## 💻 Windows Setup & Installation Instructions

Follow these exact steps from the project root folder (`d:\SMA_Pro`):

### Step 1: Open Terminal (PowerShell or Command Prompt)
Navigate to the root folder:
```bash
cd d:\SMA_Pro
```

### Step 2: Create a Virtual Environment
```bash
python -m venv .venv
```

### Step 3: Activate the Virtual Environment
On Windows PowerShell:
```bash
.venv\Scripts\Activate.ps1
```
*(Or in Command Prompt: `.venv\Scripts\activate.bat`)*

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run the Streamlit Application
```bash
streamlit run app.py
```
The application will launch automatically in your browser at `http://localhost:8501`.

---

## 📄 CSV Dataset Format Requirements

Any uploaded CSV file must contain the following three columns:

| Column Name | Data Type | Example | Description |
| :--- | :--- | :--- | :--- |
| `airline` | Text | `IndiGo` | Name of the airline carrier |
| `date` | Date (`YYYY-MM-DD`) | `2024-03-01` | Date on which feedback was submitted |
| `feedback` | Text | `The flight landed 15 minutes ahead of schedule. Great crew!` | Customer review or opinion |

*Note: Do not include pre-calculated sentiment labels in the CSV. The app automatically computes sentiment using VADER.*

---

## 🧠 Sentiment Analysis Methodology & Thresholds

We use the official **VADER** (*Valence Aware Dictionary and sEntiment Reasoner*) compound score thresholds:

$$\text{Compound Score Range: } [-1.0, +1.0]$$

* **Positive ($\ge +0.05$):** Review indicates predominantly positive tone (e.g., *"Outstanding hospitality and delicious food!"* $\rightarrow$ `+0.8398`).
* **Negative ($\le -0.05$):** Review expresses dissatisfaction or negative experience (e.g., *"Terrible delay and rude staff."* $\rightarrow$ `-0.8126`).
* **Neutral ($-0.05 < \text{Score} < +0.05$):** Factual, non-emotional or balanced statements (e.g., *"The flight departed at 10 AM."* $\rightarrow$ `0.0000`).

---

## 💾 Session-Only Data Handling

* **What is preserved:** Active reviews, manual additions, and filter selections exist temporarily in `st.session_state` while the browser tab is open.
* **What is NOT stored:** No database (no MySQL, SQLite, MongoDB), no permanent files, and no backend API server.
* **Integrity:** `data/sample_feedback.csv` is read-only and is never modified when users submit manual reviews or upload other files.
* **Exports:** All CSV downloads and PDF reports are constructed in RAM using `io.BytesIO`.

---

## ⚠️ Known Limitations

1. **Sarcasm Misclassification:** Sarcastic feedback like *"Great, another 3-hour delay with no water!"* may receive a positive score due to the word *"Great"*.
2. **Domain-Specific Jargon:** Aviation acronyms (e.g., *"ATC congestion"*, *"DGCA guidelines"*, *"deplaned"*) are not scored with specialized weights unless added to custom dictionaries.
3. **Lexicon-Based Rules:** VADER operates on predefined word lists and grammatical heuristics rather than contextual transformer embeddings (BERT/GPT).
4. **Demonstration Dataset:** The sample reviews are synthetically generated for academic demonstration and do not reflect real passenger names or private data.

---

## 👥 Three-Member Team Responsibilities

| Team Member | Module / Role | Primary Responsibilities |
| :--- | :--- | :--- |
| **Member 1** | **Data & Sentiment Analysis** | • Designed and validated `data/sample_feedback.csv` (exactly 50 rows).<br>• Implemented `modules/sentiment.py` (`analyze_sentiment`, `analyze_dataframe`).<br>• Tested Positive, Negative, and Neutral corner cases. |
| **Member 2** | **Analytics & PDF Report** | • Implemented `modules/analytics.py` (KPIs, airline/date grouping, filters).<br>• Implemented `modules/report_generator.py` (ReportLab document, Matplotlib chart buffer).<br>• Tested CSV and PDF in-memory export generation. |
| **Member 3** | **UI & Dashboard Integration** | • Implemented `app.py` using Streamlit layout and session state.<br>• Built Plotly Express visualizations (Distribution, Comparison, Trend).<br>• Integrated manual review simulator, file uploader, and download buttons.<br>• Conducted full end-to-end integration testing. |

---

## 🔄 Code Flow in Simple Hinglish

1. **User Application Start Karta Hai:**
   * Jab user terminal me `streamlit run app.py` chalata hai, Streamlit server start hota hai aur browser open hota hai.
2. **Session State Initialization:**
   * `app.py` check karta hai ki kya `active_df` session state me maujood hai. Agar nahi, toh woh `load_initial_sample_data()` call karta hai.
3. **Dataset Loading & Sentiment Scoring:**
   * `data/sample_feedback.csv` ko read kiya jata hai (50 reviews). `modules/sentiment.py` ka `analyze_dataframe()` function har review ko VADER se score karta hai aur `sentiment` (`Positive`/`Negative`/`Neutral`) aur `compound_score` columns add karta hai.
4. **Sidebar Controls & Filters:**
   * User sidebar se airlines, sentiment labels ya date range choose karta hai.
   * `modules/analytics.py` ka `filter_data()` function matching rows filter karta hai.
5. **Dashboard Rendering:**
   * `calculate_kpis()` se Total, Positive, Negative, Neutral metrics display hote hain.
   * Plotly Express se teen dynamic charts render hote hain.
   * Filtered reviews ek clean table me format hokar display hote hain.
6. **Manual Review Ya Upload Processing:**
   * Agar user form me naya review add karta hai, toh VADER turant predict karta hai aur `st.session_state["active_df"]` me concatenate ho jata hai bina original CSV ko touch kiye.
   * Agar naya CSV upload hota hai, toh column check aur clean validation ke baad dataset replace hota hai.
7. **Report & CSV Download:**
   * User button click karta hai toh filtered results memory me CSV ya ReportLab ke through PDF me convert hokar direct browser se download ho jaate hain.

---

## 🔍 Important Functions Explained (One-Line Hinglish)

1. `analyze_sentiment(review)`:
   * **Hinglish:** "Single review text ko VADER polarity scores se compound score nikal kar Positive, Negative ya Neutral label assign karta hai."
2. `analyze_dataframe(df)`:
   * **Hinglish:** "DataFrame ke feedback column par loop karke har row ke liye sentiment aur compound score columns create karta hai."
3. `calculate_kpis(df)`:
   * **Hinglish:** "Dataset me se Positive, Negative aur Neutral reviews ki ginti aur unka percentage calculate karke KPI dictionary banata hai."
4. `get_sentiment_distribution(df)`:
   * **Hinglish:** "Bar chart ke liye sentiment labels, counts aur percentages ka structured DataFrame prepare karta hai."
5. `get_airline_sentiment_summary(df)`:
   * **Hinglish:** "Airlines aur sentiments ke hisaab se data ko group karta hai taaki airline-wise comparison chart ban sake."
6. `get_date_sentiment_summary(df)`:
   * **Hinglish:** "Reviews ko date ke according chronologically sort aur aggregate karta hai taaki trend line chart render ho sake."
7. `filter_data(df, selected_airlines, selected_sentiments, start_date, end_date)`:
   * **Hinglish:** "Sidebar filters ke selections ke according Pandas boolean conditions se matching reviews filter karta hai."
8. `generate_pdf_report(df)`:
   * **Hinglish:** "ReportLab aur Matplotlib ka use karke table, static chart aur VADER methodology notes ko ek clean PDF file me compile karta hai."
9. `create_sentiment_chart_image(kpis)`:
   * **Hinglish:** "Matplotlib se sentiment counts ka static bar chart memory buffer (BytesIO) me banata hai taaki PDF document me embed ho sake."
10. `load_initial_sample_data()`:
    * **Hinglish:** "Initial 50 synthetic reviews ko sample CSV se load aur analyze karke session state me store karta hai."

---

## 🎓 Viva Preparation — Questions & Answers

### Q1: VADER kya hai aur yeh traditional machine learning models se alag kaise hai?
* **Answer:** VADER (*Valence Aware Dictionary and sEntiment Reasoner*) ek rule-based, lexicon-driven sentiment analysis library hai. Isme pre-trained neural networks ya heavy training data ki zaroorat nahi hoti. Yeh predefined words ki sentiment intensity (valence), punctuation (jaise `!`), capitalization, aur negations (jaise *"not good"*) ko rules ke through calculate karta hai.

### Q2: Compound score kya hota hai aur labels kaise decide hote hain?
* **Answer:** Compound score ek normalized unidimensional metric hai jo `-1.0` (most negative) se `+1.0` (most positive) ke beech rehta hai. VADER ke standard thresholds ke mutabiq:
  * Score $\ge 0.05 \rightarrow$ **Positive**
  * Score $\le -0.05 \rightarrow$ **Negative**
  * Score between $-0.05$ and $+0.05 \rightarrow$ **Neutral**

### Q3: Is project mein database (jaise SQLite ya MySQL) kyu use nahi kiya gaya?
* **Answer:** Yeh project ek specific academic demonstration ke liye hai jisme 50 reviews ka analysis showcase karna tha. Streamlit ka `st.session_state` RAM me active working data ko hold karta hai. Database na lagane se application lightweight rehti hai, configuration overhead zero ho jata hai, aur code beginner-friendly bana rehta hai.

### Q4: Streamlit me session state ka role kya hai?
* **Answer:** Streamlit har user action (jaise button click, slider change) par pure Python script ko top to bottom rerun karta hai. Normal variables re-initialize ho jaate hain. `st.session_state` user ke interaction ke dauran dataset aur variables ko memory me persist rakhta hai.

### Q5: PDF generation server par disk file kyu create nahi karta?
* **Answer:** Humne `io.BytesIO()` use kiya hai jo PDF bytes ko seedhe RAM (memory buffer) me generate karta hai. Isse server par unnecessary files store nahi hoti, disk cleanup ki zaroorat nahi padti, aur multi-user environments me race conditions ya permission errors nahi aate.

### Q6: Agar user invalid CSV upload kare toh application crash kyu nahi hoti?
* **Answer:** Humne Pandas se pehle check kiya hai ki mandatory columns (`airline`, `date`, `feedback`) maujood hain ya nahi. Sath hi `pd.to_datetime(errors='coerce')` invalid dates ko handle karta hai aur empty rows ko filter karke user ko friendly warning message dikhata hai.

---

## ⏱️ How to Explain This Project in 60 Seconds (Viva Script in Hinglish)

> *"Good morning respected teachers. Humara project hai **Airline Customer Sentiment Analyzer** jo Social Media Analytics subject ke liye banaya gaya hai.*
>
> *Is project ka main goal hai airline customer reviews ko VADER sentiment analysis ke through analyze karna aur ek clean Streamlit dashboard me actionable insights dikhana.*
>
> *Humne exactly 50 synthetic reviews ka sample dataset prepare kiya hai jo 5 major airlines—IndiGo, Air India, SpiceJet, Vistara aur Akasa Air—ko cover karta hai.*
>
> *Application automatically har review ka compound score nikaal kar use Positive, Negative ya Neutral label deti hai. Humne chaar key metrics, airline-wise grouped comparisons, aur chronological sentiment trend line chart add kiye hain.*
>
> *Saath hi, user real-time me naya review test kar sakta hai, custom CSV upload kar sakta hai, aur pure analysis ka formal PDF report aur filtered CSV download kar sakta hai bina kisi external database ke. Thank you!"*

---

## 🛠️ Common Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'streamlit'` | Virtual environment activate nahi hai ya packages install nahi hue | Run `.venv\Scripts\activate` and then `pip install -r requirements.txt` |
| `Missing required columns` error on upload | Uploaded CSV headers match nahi kar rahe | Ensure headers are exactly: `airline`, `date`, `feedback` (lowercase) |
| Port 8501 already in use | Puraana Streamlit instance background me chal raha hai | Run `streamlit run app.py --server.port 8502` |
