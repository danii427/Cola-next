# 🥤 Cola Next SMO KPI Analyzer (Easy Guide & Flowchart)

An easy-to-use tool to analyze sales targets, shop visits, delivery success, and generate 1-page PDF report cards for your sales team.

---

## 🧭 Super Simple 6-Step Flowchart (How It Works)

```mermaid
flowchart TD
    Step1["📂 STEP 1: Upload Excel File<br><i>(Put your monthly sales report into the app)</i>"]
    --> Step2["⚙️ STEP 2: Set Targets<br><i>(Choose Green = Good, Yellow = Average, Red = Needs Help)</i>"]
    --> Step3["🧹 STEP 3: Automatic Calculation<br><i>(App checks all 43 sales officers, sales vs target, and visits)</i>"]
    --> Step4["📊 STEP 4: View Simple Bar Charts<br><i>(See top performers and team health at a glance)</i>"]
    --> Step5["👤 STEP 5: Check Any Sales Officer<br><i>(Read their 6-paragraph summary, where they are low, and action plan)</i>"]
    --> Step6["📄 STEP 6: Download 1-Page PDF<br><i>(Click download for a clean printable PDF report card)</i>"]

    style Step1 fill:#eff6ff,stroke:#1d4ed8,stroke-width:2px;
    style Step2 fill:#fefce8,stroke:#ca8a04,stroke-width:2px;
    style Step3 fill:#f0fdf4,stroke:#15803d,stroke-width:2px;
    style Step4 fill:#faf5ff,stroke:#7e22ce,stroke-width:2px;
    style Step5 fill:#fff1f2,stroke:#be123c,stroke-width:2px;
    style Step6 fill:#ecfdf5,stroke:#047857,stroke-width:3px;
```

---

### 📋 What Happens in Each Step (In Plain Words):

1. **Step 1 (Upload):** You upload your monthly sales Excel file (`.xlsx`).
2. **Step 2 (Targets):** You set your standards (e.g., Green = 100% target met, Yellow = 85% acceptable, Red = below 85%).
3. **Step 3 (Calculation):** The app automatically reads each salesperson's numbers, calculates their percentages, and checks if they passed.
4. **Step 4 (Overview):** You see simple, color-coded bar charts showing who made target and who is lagging behind.
5. **Step 5 (Individual Profile):** You pick any salesperson (like *SAAD SADDIQUE*) and get a clear 6-paragraph explanation telling you:
   - How many days they worked.
   - Their sales percentage.
   - Their shop visit completion.
   - Their delivery percentage and GPS accuracy.
   - **Where they are low** and **what specific actions they must take to improve**.
6. **Step 6 (Download):** Click one button to download a clean, printable 1-page PDF report card for that salesperson or download a ZIP file with all report cards.

---

## 📊 Detailed System Architecture Flowchart

```mermaid
flowchart TD
    subgraph INGESTION ["1. Ingestion & Auto-Detection"]
        A["📂 User Uploads Excel File (.xlsx / .xls)"] --> B["🔍 find_excel_header()"]
        B -->|Scans top 30 rows across sheets| C["Identifies Sheet Name & Header Row"]
        C --> D["Standardizes Column Names using ALIAS_LOOKUP (49 Columns)"]
    end

    subgraph CLEANING ["2. Data Cleaning & Calculations"]
        D --> E["🧹 clean_and_transform_dataset()"]
        E --> F["Separate Grand Total Row from Individual SMO Records"]
        F --> G["Normalize Percentages (0.0-1.0 to 0-100%) & Parse Clean Numbers"]
        G --> H["Calculate Performance Tier (Elite / On-Track / Watchlist / Critical)"]
        H --> I["Evaluate KPI Status Zones (Green / Yellow / Red based on Sidebar Thresholds)"]
    end

    subgraph ENGINE ["3. Analytics & Narrative Engine"]
        I --> J["📈 calculate_team_metrics() (Rollups, Averages, Health Counts)"]
        I --> K["📝 generate_smo_narrative() (6 Paragraphs, Low Deficits & Action Plan)"]
    end

    subgraph DASHBOARD ["4. Interactive 5-Tab Dashboard UI"]
        J --> T1["🌟 Tab 1: Team Overview (Health Bar, Target vs Sales Bar, Top/Bottom Performers)"]
        K --> T2["👤 Tab 2: Single SMO Profile (Scorecard Bar, Calls/Delivery Bar, Diagnostic Narrative)"]
        I --> T3["🏆 Tab 3: Full Leaderboard & Table Rankings"]
        I --> T4["🗺️ Tab 4: Distributor Sales Breakdown"]
        K --> T5["📦 Tab 5: Download Reports"]
    end

    subgraph EXPORT ["5. High-Resolution Document Exports"]
        T2 --> P1["📄 create_smo_pdf() -> 1-Page Printable PDF Dossier"]
        T5 --> P2["🗜️ generate_batch_pdf_zip() -> Bulk ZIP Package for All SMOs"]
        T5 --> P3["📊 create_executive_excel_workbook() -> Multi-Tab Styled Excel (.xlsx)"]
    end

    style INGESTION fill:#f8fafc,stroke:#0b1e36,stroke-width:2px;
    style CLEANING fill:#f0fdf4,stroke:#10b981,stroke-width:2px;
    style ENGINE fill:#eff6ff,stroke:#3b82f6,stroke-width:2px;
    style DASHBOARD fill:#fefce8,stroke:#f59e0b,stroke-width:2px;
    style EXPORT fill:#fdf2f8,stroke:#ec4899,stroke-width:2px;
```

---

## 🔄 Detailed Data Pipeline Explained (Step-by-Step)

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant App as Streamlit App (app.py)
    participant Processor as Data Engine (data_processor.py)
    participant Visuals as Chart Engine (visualizations.py)
    participant PDF as PDF Engine (pdf_generator.py)
    participant Excel as Excel Engine (excel_exporter.py)

    User->>App: Uploads SMO July Report.xlsx
    App->>Processor: Calls find_excel_header() & clean_and_transform_dataset()
    Processor-->>App: Returns Cleaned DataFrame (43 SMOs) + Team Metrics
    
    App->>Visuals: Request simple bar charts (Team Health, Target vs Sales, Single SMO Scorecard)
    Visuals-->>App: Returns interactive Plotly horizontal bar charts
    
    User->>App: Selects a specific Sales Officer (e.g., SAAD SADDIQUE)
    App->>Processor: Calls generate_smo_narrative(smo_row, thresholds)
    Processor-->>App: Returns 6-paragraph narrative, Where We Are Low, and Action Plan
    
    User->>App: Clicks "Download 1-Page PDF"
    App->>PDF: Calls create_smo_pdf()
    PDF-->>User: Downloads crisp branded A4 PDF report card
    
    User->>App: Clicks "Download All PDFs (ZIP Archive)"
    App->>PDF: Calls generate_batch_pdf_zip()
    PDF-->>User: Downloads ZIP file with individual PDFs for all SMOs
```

---

## 📁 Repository Structure & Module Breakdown

| File | Purpose & Responsibilities |
| :--- | :--- |
| [`app.py`](file:///c:/Users/dayan/Desktop/kpi%20report%20analyzer/app.py) | **Main Application Entry Point:** Manages Streamlit state, sidebar KPI thresholds, initial upload screen, global filters, and the 5-tab user interface. |
| [`data_processor.py`](file:///c:/Users/dayan/Desktop/kpi%20report%20analyzer/data_processor.py) | **Core Processing Engine:** Auto-detects Excel headers, maps all 49 potential columns via canonical aliases, cleans nulls/floats, computes performance zones (Green/Yellow/Red), and generates the standardized 6-paragraph narrative and deficit diagnostics. |
| [`visualizations.py`](file:///c:/Users/dayan/Desktop/kpi%20report%20analyzer/visualizations.py) | **Layman-Friendly Charting Engine:** Generates simple, clean horizontal and grouped bar charts with color coding and clear plain-English explanation callouts. Zero complicated scatter plots. |
| [`pdf_generator.py`](file:///c:/Users/dayan/Desktop/kpi%20report%20analyzer/pdf_generator.py) | **Executive PDF Engine:** Uses ReportLab to generate print-ready, high-resolution A4 single-page report cards and bulk ZIP archives. |
| [`excel_exporter.py`](file:///c:/Users/dayan/Desktop/kpi%20report%20analyzer/excel_exporter.py) | **Excel Workbook Exporter:** Uses OpenPyXL to build corporate-styled multi-sheet `.xlsx` files with Executive Summary, Scorecards, and Full Clean Dataset. |
| [`theme.py`](file:///c:/Users/dayan/Desktop/kpi%20report%20analyzer/theme.py) | **Design System & CSS:** Manages Cola Next brand colors (Navy `#0B1E36`, Crimson `#D8232A`, Emerald `#10B981`, Amber `#F59E0B`), high-contrast text styles, and full Light/Dark mode compatibility. |
| [`requirements.txt`](file:///c:/Users/dayan/Desktop/kpi%20report%20analyzer/requirements.txt) | **Dependencies:** Lists required packages (`streamlit`, `pandas`, `openpyxl`, `reportlab`, `plotly`). |

---

## 📖 Layman's KPI Dictionary (What Each Metric Means)

| KPI Metric | Plain English Meaning | Standard Green Goal | Yellow Zone | Red Zone |
| :--- | :--- | :---: | :---: | :---: |
| **Sales Achievement %** | How much of the monthly sales target was actually sold. | **≥ 100%** | 85% to 99% | < 85% |
| **Shop Visit Completion %** | What percentage of scheduled store visits were actually made. | **≥ 95%** | 85% to 94% | < 85% |
| **Order Strike Rate %** | Out of the shops visited, how many actually placed an order. | **≥ 80%** | 65% to 79% | < 65% |
| **GPS Location Accuracy %** | Percentage of shop check-ins that occurred directly inside the store. | **≥ 90%** | 75% to 89% | < 75% |
| **Delivered Cases %** | Percentage of booked orders that were successfully delivered to retailers. | **≥ 90%** | 80% to 89% | < 80% |
| **Field Working Days** | Number of active field days the sales officer worked in the month. | **≥ 18 Days** | 15 to 17 Days | < 15 Days |

---

## 🚀 How to Run the Application

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Streamlit App
```bash
python -m streamlit run app.py
```

### 3. Open in Browser
Visit **`http://localhost:8501`** in any web browser.

---

## 💡 Using the App
1. **Upload Report:** On the home screen, drag and drop your Excel report (or click *▶️ Load Sample July Report* for a quick test).
2. **Set Thresholds:** Adjust minimum target levels in the sidebar if needed.
3. **Analyze:**
   - **Tab 1 (Team Overview):** High-level summary, health distribution bar chart, and top/bottom performers.
   - **Tab 2 (Single SMO):** Individual performance scorecard bar chart, 6-paragraph narrative, "Where We Are Low" deficits, "What to Enhance" action plan, and 1-click PDF download.
   - **Tab 3 (Ranking):** Sortable team leaderboard.
   - **Tab 4 (Distributor Sales):** Target vs sales comparison by distribution center.
   - **Tab 5 (Download Reports):** Download all individual PDFs in a ZIP file or download the executive Excel workbook.
