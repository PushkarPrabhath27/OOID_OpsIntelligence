# AI Implementation Prompt — OilField Ops Intelligence Dashboard (OOID)
### Phased Prompt Guide for AI-Assisted Development

---

> **How to Use This Document**
> Each phase below is a standalone prompt you feed to an AI coding assistant (Claude, Cursor, GitHub Copilot, etc.). Run them in order. Never skip a phase. Each phase builds on the previous one. Before starting each phase, paste the exact prompt under "PROMPT TO USE" into your AI assistant.

---

## PHASE 0 — Project Scaffolding & Environment Setup

### What This Phase Does
Creates the entire project folder structure, initializes Git, sets up the Python virtual environment, installs all dependencies, and creates configuration files.

### PROMPT TO USE:

```
You are a senior data engineer setting up a professional Python project. Create the complete folder structure and configuration for a project called "oilfield-ops-intelligence".

Create the following exact directory structure:
oilfield-ops-intelligence/
├── src/
│   ├── __init__.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── eia_api_client.py
│   │   └── baker_hughes_fetcher.py
│   ├── transform/
│   │   ├── __init__.py
│   │   ├── cleaner.py
│   │   ├── metrics.py
│   │   └── anomaly_detector.py
│   ├── warehouse/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schema.sql
│   │   └── loader.py
│   ├── analytics/
│   │   ├── __init__.py
│   │   └── queries.py
│   └── dashboard/
│       ├── __init__.py
│       ├── app.py
│       ├── pages/
│       │   ├── executive_overview.py
│       │   ├── state_drilldown.py
│       │   ├── rig_efficiency.py
│       │   ├── pipeline_monitor.py
│       │   └── anomaly_log.py
│       └── components/
│           ├── kpi_card.py
│           ├── charts.py
│           └── maps.py
├── airflow/
│   └── dags/
│       └── production_pipeline_dag.py
├── gcp/
│   └── cloud_functions/
│       └── scheduled_ingestion/
│           ├── main.py
│           └── requirements.txt
├── tests/
│   ├── __init__.py
│   ├── test_cleaner.py
│   ├── test_metrics.py
│   └── test_loader.py
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   └── architecture.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md

Now create these specific files with real content:

1. requirements.txt — include: streamlit, pandas, numpy, plotly, folium, sqlalchemy, psycopg2-binary, requests, python-dotenv, apache-airflow, pytest, pydantic, loguru, streamlit-folium, great-expectations

2. .env.example with variables: EIA_API_KEY, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, GCP_PROJECT_ID, GCP_BUCKET_NAME

3. docker-compose.yml that spins up PostgreSQL 15 with persistent volume, pgAdmin for database management, and the Streamlit app container — all networked together

4. .gitignore appropriate for a Python data project — include .env, __pycache__, *.pyc, data/raw/, venv/, .pytest_cache/

5. A professional README.md with: project banner placeholder, badges (Python version, License, Status), one-paragraph description, architecture diagram placeholder, quick start instructions, features list, tech stack table, and contributing guide

Make all files production-quality. Use real configurations, not placeholders. The docker-compose should actually work when run.
```

---

## PHASE 1 — Data Ingestion Layer

### What This Phase Does
Builds the complete data ingestion system that connects to the EIA API and Baker Hughes data sources, handles authentication, pagination, errors, and saves raw data to the Bronze layer.

### PROMPT TO USE:

```
You are building the data ingestion layer for an oil and gas analytics platform. 

Create src/ingestion/eia_api_client.py with the following complete implementation:

The EIA API base URL is https://api.eia.gov/v2/
The API key is loaded from environment variable EIA_API_KEY.

Build a class EIAClient with these methods:

1. __init__(self) — loads API key from .env, sets up a requests Session with retry logic (3 retries, exponential backoff: 1s, 2s, 4s), sets default headers, initializes loguru logger

2. get_crude_oil_production(self, start_date: str, end_date: str, frequency: str = "monthly") -> pd.DataFrame
   - Endpoint: /petroleum/sum/sndw/
   - Fetches US crude oil production by state (barrels per day)
   - Parameters: facets[duoarea][] for state filtering, start, end, frequency
   - Returns DataFrame with columns: date, state_code, production_bbls, unit
   - Handle pagination: EIA returns max 5000 rows; loop with offset if more

3. get_natural_gas_production(self, start_date: str, end_date: str) -> pd.DataFrame
   - Fetches dry natural gas production by state (MCF)
   - Returns DataFrame with columns: date, state_code, gas_production_mcf, unit

4. get_refinery_utilization(self, start_date: str, end_date: str) -> pd.DataFrame
   - Fetches weekly refinery utilization rates
   - Returns DataFrame with columns: date, utilization_pct, region

5. save_raw_to_bronze(self, df: pd.DataFrame, dataset_name: str) -> str
   - Saves the raw DataFrame as a timestamped JSON file in data/raw/{dataset_name}/
   - Filename format: {dataset_name}_{YYYYMMDD_HHMMSS}.json
   - Returns the file path
   - Also saves a metadata file with: source, fetched_at, record_count, date_range

6. A private method _make_request(self, endpoint, params) that handles the actual HTTP call, logs the request, checks for HTTP errors, parses JSON, and raises a custom EIAAPIError if anything fails

Also create src/ingestion/baker_hughes_fetcher.py:

Build a class BakerHughesFetcher with:

1. fetch_rig_count_csv(self, year: int) -> pd.DataFrame
   - Downloads Baker Hughes North America rig count CSV from their public URL
   - Parses it into a DataFrame with columns: week_ending_date, us_total_rigs, canada_total_rigs, by_state (dict), oil_rigs, gas_rigs, misc_rigs
   - Cleans the CSV (Baker Hughes format has merged headers, skip rows logic needed)
   - Returns clean DataFrame

2. fetch_historical_rig_counts(self, start_year: int = 2015) -> pd.DataFrame
   - Loops from start_year to current year
   - Calls fetch_rig_count_csv for each year
   - Concatenates results
   - Drops duplicates
   - Returns combined DataFrame sorted by date

3. save_raw_to_bronze(self, df, dataset_name) — same signature as EIAClient's version, reuse the same logic

Also create src/ingestion/__init__.py that exports EIAClient, BakerHughesFetcher, and EIAAPIError.

Add comprehensive docstrings to every method. Add type hints everywhere. Use loguru for all logging — log at INFO for successful fetches (include record count and time taken), WARNING for retried requests, and ERROR for failures. Never use print statements.
```

---

## PHASE 2 — Transform Layer (ETL Logic)

### What This Phase Does
Builds the complete data transformation pipeline including cleaning, standardization, derived metrics calculation, and anomaly detection logic.

### PROMPT TO USE:

```
You are building the ETL transform layer for an oil and gas data engineering pipeline. The raw data comes from the ingestion layer as pandas DataFrames. Now build the transformation logic.

Create src/transform/cleaner.py with a class DataCleaner:

1. clean_production_data(self, df: pd.DataFrame) -> pd.DataFrame
   - Input: raw EIA crude oil production DataFrame
   - Operations:
     a. Parse date column to datetime, handle multiple formats (YYYY-MM, YYYY-MM-DD)
     b. Strip whitespace from all string columns
     c. Normalize state codes to uppercase 2-letter abbreviations (map full names to codes if present)
     d. Cast production values to float64, coerce errors to NaN
     e. Flag rows where production is negative (set data_quality_flag = 'NEGATIVE_VALUE')
     f. Flag rows where production is more than 3 standard deviations above the column mean (flag = 'STATISTICAL_OUTLIER') — but do NOT drop them, just flag
     g. Forward-fill missing production values within each state group (max 2 consecutive fills) 
     h. Add a data_quality_score column: 1.0 (clean), 0.7 (forward-filled), 0.3 (outlier flagged), 0.0 (negative)
     i. Add inserted_at timestamp column
   - Return cleaned DataFrame

2. clean_rig_count_data(self, df: pd.DataFrame) -> pd.DataFrame
   - Parse dates properly
   - Handle the Baker Hughes format where some weeks have duplicate entries
   - Aggregate to monthly average rigs if frequency is weekly
   - Add data_quality_flag column

3. standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame
   - Convert all column names to snake_case
   - Remove special characters
   - Return DataFrame with clean column names

4. validate_date_range(self, df: pd.DataFrame, date_col: str, min_date: str, max_date: str) -> pd.DataFrame
   - Removes rows outside the valid date range
   - Logs how many rows were dropped and why

Create src/transform/metrics.py with a class MetricsCalculator:

1. calculate_production_per_rig(self, production_df: pd.DataFrame, rig_df: pd.DataFrame) -> pd.DataFrame
   - Joins production and rig count data on date + state
   - Calculates: production_per_rig = crude_production_bbls / active_rig_count
   - Handles division by zero (when rig_count = 0, set result to NaN, flag it)
   - Returns merged DataFrame with new metric column

2. calculate_mom_growth(self, df: pd.DataFrame, value_col: str, group_col: str = 'state_code') -> pd.DataFrame
   - Calculates month-over-month percentage change within each group
   - Formula: (current - previous) / previous * 100
   - Handles first month of each group (NaN, cannot calculate)
   - Returns DataFrame with new column: {value_col}_mom_growth_pct

3. calculate_yoy_growth(self, df: pd.DataFrame, value_col: str, group_col: str = 'state_code') -> pd.DataFrame
   - Same as MoM but 12-month lag
   - Returns DataFrame with {value_col}_yoy_growth_pct

4. calculate_rolling_average(self, df: pd.DataFrame, value_col: str, windows: list = [3, 6, 12]) -> pd.DataFrame
   - For each window size, adds a {value_col}_rolling_{window}m column
   - Groups by state before calculating rolling avg

5. calculate_efficiency_index(self, df: pd.DataFrame) -> pd.DataFrame
   - Efficiency Index = (production_per_rig / national_avg_production_per_rig) * 100
   - Where national_avg_production_per_rig is the national average for that month
   - Score > 100 means the state is more efficient than national average
   - Returns DataFrame with efficiency_index column

Create src/transform/anomaly_detector.py with a class AnomalyDetector:

1. detect_statistical_anomalies(self, df: pd.DataFrame, value_col: str, window: int = 90) -> pd.DataFrame
   - Uses rolling z-score method
   - For each row: z = (value - rolling_mean) / rolling_std where rolling window = 90 days
   - Flag rows where abs(z) > 2.5 as anomalies
   - Add columns: z_score, is_anomaly (boolean), anomaly_severity ('LOW', 'MEDIUM', 'HIGH' based on z > 2.5, 3.0, 4.0)
   - Add anomaly_description: human-readable string like "Production spiked 340% above 3-month average"

2. detect_sudden_drops(self, df: pd.DataFrame, value_col: str, threshold_pct: float = 30.0) -> pd.DataFrame
   - Flags month-over-month drops greater than threshold_pct
   - Tags these as 'SUDDEN_DROP' anomalies separately from statistical anomalies

3. get_anomaly_summary(self, df: pd.DataFrame) -> pd.DataFrame
   - Returns a summary DataFrame: one row per anomaly, sorted by severity
   - Columns: date, state, metric, observed_value, expected_value, deviation_pct, severity, description

Use loguru for all logging. Add type hints everywhere. Write Numpy-style docstrings for every method.
```

---

## PHASE 3 — Data Warehouse & Star Schema

### What This Phase Does
Creates the Star Schema database design, SQLAlchemy ORM models, schema creation scripts, and the data loader that populates the warehouse from transformed DataFrames.

### PROMPT TO USE:

```
You are a data warehouse engineer implementing a Star Schema for an oil and gas analytics platform using PostgreSQL and SQLAlchemy.

Create src/warehouse/schema.sql — the complete SQL DDL for this Star Schema:

1. dim_date table:
   - date_key (SERIAL PRIMARY KEY)
   - full_date DATE NOT NULL UNIQUE
   - year SMALLINT, quarter SMALLINT, month SMALLINT
   - month_name VARCHAR(10), month_abbrev VARCHAR(3)
   - day_of_year SMALLINT, week_of_year SMALLINT
   - is_month_start BOOLEAN, is_month_end BOOLEAN
   - fiscal_year SMALLINT, fiscal_quarter SMALLINT (SLB fiscal year starts Jan 1)
   - Add index on full_date

2. dim_location table:
   - location_key (SERIAL PRIMARY KEY)
   - state_code CHAR(2) NOT NULL UNIQUE
   - state_name VARCHAR(50) NOT NULL
   - region VARCHAR(50) NOT NULL — valid values: 'Permian Basin', 'Gulf Coast', 'Appalachian', 'Mid-Continent', 'Rocky Mountain', 'West Coast', 'Other'
   - country CHAR(2) DEFAULT 'US'
   - latitude DECIMAL(9,6), longitude DECIMAL(9,6) — for mapping
   - Add index on state_code and region

3. dim_well_type table:
   - well_type_key (SERIAL PRIMARY KEY)
   - well_category VARCHAR(30) — 'Tight Oil / Shale', 'Conventional', 'Offshore', 'Other'
   - primary_product VARCHAR(20) — 'Crude Oil', 'Natural Gas', 'Both'
   - formation_type VARCHAR(50)

4. fact_production table:
   - production_id BIGSERIAL PRIMARY KEY
   - date_key INTEGER FK → dim_date(date_key)
   - location_key INTEGER FK → dim_location(location_key)
   - well_type_key INTEGER FK → dim_well_type(well_type_key)
   - crude_production_bbls DECIMAL(15,2)
   - gas_production_mcf DECIMAL(15,2)
   - active_rig_count SMALLINT
   - production_per_rig DECIMAL(10,2)
   - mom_growth_pct DECIMAL(8,4)
   - yoy_growth_pct DECIMAL(8,4)
   - rolling_3m_avg DECIMAL(15,2)
   - rolling_12m_avg DECIMAL(15,2)
   - efficiency_index DECIMAL(8,2)
   - data_quality_score DECIMAL(3,2)
   - data_quality_flags TEXT[]
   - is_anomaly BOOLEAN DEFAULT FALSE
   - anomaly_severity VARCHAR(10)
   - created_at TIMESTAMP DEFAULT NOW()
   - updated_at TIMESTAMP DEFAULT NOW()
   - Add composite index on (date_key, location_key)
   - Add partial index on (is_anomaly) WHERE is_anomaly = TRUE

5. pipeline_run_log table (operational table, not a dimension):
   - run_id SERIAL PRIMARY KEY
   - pipeline_name VARCHAR(100)
   - started_at TIMESTAMP, completed_at TIMESTAMP
   - status VARCHAR(20) — 'RUNNING', 'SUCCESS', 'FAILED'
   - records_extracted INTEGER, records_transformed INTEGER, records_loaded INTEGER
   - records_rejected INTEGER
   - error_message TEXT
   - duration_seconds DECIMAL(10,2)

6. Pre-populate dim_date with all dates from 2010-01-01 to 2030-12-31 using a SQL function/loop

7. Pre-populate dim_location with all 50 US states + DC with their correct region classifications and approximate coordinates. Include CORRECT region for key states: TX=Permian Basin/Gulf Coast, PA=Appalachian, ND=Rocky Mountain, CA=West Coast, LA=Gulf Coast, WY=Rocky Mountain, CO=Rocky Mountain

Now create src/warehouse/models.py — SQLAlchemy ORM models matching exactly the SQL schema above. Use declarative_base(). Add __repr__ methods to each model.

Now create src/warehouse/loader.py with class DataWarehouseLoader:

1. __init__(self, connection_string: str) — creates SQLAlchemy engine, session factory, logs connection success

2. initialize_schema(self) — runs schema.sql to create all tables if they don't exist. Also seeds dim_date and dim_location.

3. load_production_facts(self, df: pd.DataFrame, pipeline_run_id: int) -> dict
   - Receives a fully transformed DataFrame from the metrics layer
   - Maps DataFrame columns to fact_production columns
   - Looks up date_key from dim_date using the date
   - Looks up location_key from dim_location using state_code
   - Uses bulk insert (SQLAlchemy's bulk_insert_mappings for performance)
   - On conflict (same date + location): UPDATE the record (upsert pattern)
   - Returns dict: {'inserted': N, 'updated': N, 'rejected': N, 'duration_ms': N}

4. log_pipeline_run(self, pipeline_name, status, records_extracted, records_transformed, records_loaded, records_rejected, started_at, error_message=None) -> int
   - Inserts a row into pipeline_run_log
   - Returns the run_id

5. get_data_freshness(self) -> dict
   - Returns dict with: latest_date_in_warehouse, days_since_last_update, total_records, states_covered

Include proper transaction management: each load_production_facts call is one transaction — if any row fails, rollback and log the error, don't crash the entire load.
```

---

## PHASE 4 — Analytics Query Layer

### What This Phase Does
Builds the analytics query module that the dashboard calls to retrieve data. All business logic for queries lives here, not in the dashboard pages.

### PROMPT TO USE:

```
Create src/analytics/queries.py with a class OilfieldAnalytics.

This class takes a SQLAlchemy session or connection string and exposes all the data the dashboard needs. Every method returns a pandas DataFrame. Cache results using functools.lru_cache where appropriate (for expensive queries).

Implement these methods:

1. get_national_kpis(self, as_of_date: str = None) -> dict
   - Returns the top-level dashboard numbers:
     - current_month_production_bbls: sum of crude production for the latest month
     - previous_month_production_bbls: same for prior month
     - mom_change_pct: calculated change
     - yoy_change_pct: vs same month last year
     - active_rig_count: latest week's total US rig count
     - rig_count_change_wow: week over week change
     - avg_efficiency_index: national average for current month
     - anomaly_count_30d: number of anomalies flagged in last 30 days
     - data_freshness_days: days since last pipeline run
   - SQL behind this: joins fact_production + dim_date + dim_location, uses window functions for YoY/MoM

2. get_production_trend(self, years: int = 5, state_code: str = None) -> pd.DataFrame
   - Returns monthly production trend for either all US or a specific state
   - Columns: date, crude_production_bbls, rolling_12m_avg, mom_growth_pct, yoy_growth_pct
   - Sorted ascending by date

3. get_state_comparison(self, metric: str = 'crude_production_bbls', period: str = 'latest_month') -> pd.DataFrame
   - Returns all states ranked by the given metric for the given period
   - Columns: state_code, state_name, region, {metric}, rank, mom_change_pct, efficiency_index
   - Include latitude/longitude for map plotting

4. get_state_drilldown(self, state_code: str) -> dict
   - Returns a complete data package for a single state:
     - kpis: dict (same shape as national kpis but state-scoped)
     - production_trend: DataFrame (last 5 years monthly)
     - rig_trend: DataFrame (last 2 years monthly)
     - recent_anomalies: DataFrame (last 6 months anomalies)
     - efficiency_trend: DataFrame (efficiency_index over last 3 years)
     - rank_history: DataFrame (state's national rank by month for last 12 months)

5. get_rig_efficiency_data(self) -> pd.DataFrame
   - Returns correlation data for scatter plot: rig count vs production, colored by state
   - Also includes efficiency_index for each state for current month
   - Top 5 and bottom 5 states by efficiency_index flagged

6. get_pipeline_run_history(self, limit: int = 30) -> pd.DataFrame
   - Returns last N pipeline run records from pipeline_run_log
   - Include calculated: success_rate (last 30 runs), avg_duration_seconds

7. get_anomaly_log(self, days: int = 90, severity: str = None) -> pd.DataFrame
   - Returns all anomaly records from last N days
   - Filter by severity if provided
   - Join with dim_location for state name
   - Order by anomaly_severity DESC, date DESC

8. get_top_producers(self, n: int = 10, metric: str = 'crude_production_bbls') -> pd.DataFrame
   - Returns top N states for the latest month

Use raw SQL via SQLAlchemy text() for complex queries (do not use ORM for analytics — it's too slow). Add proper indexing hints where appropriate. Every method must have a complete docstring explaining: what it returns, what SQL it runs conceptually, and any caching behavior.
```

---

## PHASE 5 — Dashboard Frontend

### What This Phase Does
Builds the complete Streamlit dashboard with professional UI/UX, dark industrial theme, interactive charts, and all five pages. This is the most important phase — it's what interviewers will see first.

### PROMPT TO USE:

```
You are a senior UI/UX engineer building a professional executive analytics dashboard in Streamlit for an oil and gas company. The aesthetic must be: dark industrial, data-dense, premium — like a Bloomberg terminal crossed with a modern SaaS tool. NOT generic. NOT blue-gradient-on-white.

Color palette:
- Background: #0A0E1A (near-black navy)
- Surface: #141927 (dark navy card)
- Border: #1E2D45 (subtle dark blue border)
- Accent primary: #E8A100 (warm amber — petroleum reference)
- Accent secondary: #00C2A8 (teal — contrast)
- Danger: #FF4B4B
- Success: #00E676
- Text primary: #F0F4FF
- Text muted: #8896B3

Typography: use Syne for headers, Space Mono for data values, Inter for body text (import from Google Fonts in custom CSS)

Create src/dashboard/app.py — the main Streamlit entry point:
- Configure page: wide layout, dark theme, custom tab icon (use 🛢️)
- Inject custom CSS that applies the color palette to ALL Streamlit elements: background, sidebar, cards, metric labels, dataframes, buttons
- The CSS must override Streamlit defaults completely — no white backgrounds anywhere
- Set up sidebar navigation with styled buttons for each page
- Show a header bar with: project logo area ("⚡ OOID"), last data refresh timestamp, data freshness indicator (green if < 1 day old, yellow if 1-3 days, red if > 3 days)
- Import and route to page modules based on selection

Create src/dashboard/components/kpi_card.py:
- Function render_kpi_card(title, value, delta, delta_label, icon, color_override=None)
- Renders a styled card using st.markdown with custom HTML/CSS
- Card style: dark surface background, amber top border accent, rounded corners, inner shadow
- Shows: icon + title row, large bold value, colored delta (green if positive, red if negative)
- Example: render_kpi_card("US Production", "12.4M BBL/day", "+3.2%", "vs last month", "🛢️")

Create src/dashboard/components/charts.py — all Plotly chart functions:

1. production_trend_chart(df) — Line chart with:
   - Dual y-axis: production volume + rolling 12m average as a softer line
   - Filled area under the production line with amber color at 20% opacity
   - Hover tooltips showing date, production, MoM change, YoY change
   - Dark background matching app theme (paper_bgcolor, plot_bgcolor set to transparent)
   - Custom tick formatting (e.g., "12.4M" not "12400000")

2. state_choropleth_map(df, metric_col, title) — Plotly choropleth:
   - USA map, state-level, colored by metric_col
   - Color scale: dark navy (low) to amber (high)
   - On hover: show state name, value, rank, MoM change
   - Clean styling: no borders visible, dark ocean color

3. rig_vs_production_scatter(df) — Scatter plot:
   - X axis: active_rig_count, Y axis: crude_production_bbls
   - Points sized by efficiency_index, colored by region
   - Annotate top 3 and bottom 3 states by name
   - Trendline added

4. efficiency_bar_chart(df) — Horizontal bar chart:
   - States ranked by efficiency_index
   - Bars colored: green if > 110, amber if 90-110, red if < 90
   - Reference line at 100 (national average)

5. pipeline_timeline_chart(df) — Timeline/Gantt-style chart showing each pipeline run as a bar
   - Green for SUCCESS, red for FAILED, yellow for RUNNING
   - Hover shows: duration, records processed, error if any

Create src/dashboard/pages/executive_overview.py:
- Title: "US Oilfield Operations — Executive Overview"
- Row 1: 4 KPI cards using render_kpi_card: Production, Rig Count, Efficiency Index, Anomalies (30d)
- Row 2: Full-width production trend chart (last 5 years)
- Row 3 left (60%): State choropleth map colored by production volume
- Row 3 right (40%): Top 10 producing states table, styled with colored rank column
- Row 4: 3 sparkline mini-charts (MoM growth by region: Gulf Coast, Permian, Appalachian)
- Add a subtle animated "live data" indicator in top right

Create src/dashboard/pages/state_drilldown.py:
- State selector dropdown at top (all 50 states)
- On state select: loads state data from analytics layer
- Shows: state name as large header + state flag emoji
- Row 1: 4 state-level KPIs (production, rig count, rank, efficiency)
- Row 2: Production history line chart (10 years if available)
- Row 3 left: Rig count trend. Row 3 right: Efficiency index trend with national avg reference line
- Row 4: Recent anomalies table for this state (last 6 months)

Create src/dashboard/pages/pipeline_monitor.py:
- Title: "Data Pipeline Operations"
- Status badge at top: "HEALTHY" / "DEGRADED" / "DOWN" with color coding
- Pipeline run history chart (last 30 runs as timeline)
- Metrics: success rate %, avg duration, records/run average
- Data coverage table: each state, last update date, record count, coverage %
- Data quality breakdown: pie chart of quality scores distribution

All Plotly charts must use this config: config={'displayModeBar': False} — hide the toolbar for cleaner look.

Every page must have smooth loading states using st.spinner with contextual messages like "Fetching production data from warehouse..." not generic "Loading...".

The complete app must work when run with: streamlit run src/dashboard/app.py
```

---

## PHASE 6 — Testing & Quality

### What This Phase Does
Builds the complete test suite and data quality validation layer.

### PROMPT TO USE:

```
Create a complete test suite for the oilfield-ops-intelligence project.

Create tests/test_cleaner.py:

Test class TestDataCleaner with these test methods (use pytest, use fixtures):

1. test_clean_production_data_handles_negative_values
   - Create a DataFrame with a row where production = -500
   - Assert that after cleaning, data_quality_flag = 'NEGATIVE_VALUE' for that row

2. test_clean_production_data_handles_nulls
   - DataFrame with 2 consecutive nulls for one state
   - Assert forward fill was applied (max 2 fills)
   - Assert data_quality_score is 0.7 for filled rows

3. test_state_code_normalization
   - Input: state_code column with mix of full names ("Texas"), abbreviations ("TX"), lowercase ("tx")
   - Assert all normalized to uppercase abbreviations

4. test_date_parsing_multiple_formats
   - Input: dates as "2023-01", "2023-01-01", "Jan 2023"
   - Assert all parse to same datetime

Create tests/test_metrics.py:

1. test_mom_growth_calculation_correct
   - Known input: Jan=1000, Feb=1100, Mar=990
   - Assert Feb MoM = 10.0%, Mar MoM = -10.0% (approx, handle floating point)

2. test_production_per_rig_zero_division
   - Row with rig_count = 0
   - Assert production_per_rig = NaN, not infinity, not error

3. test_efficiency_index_baseline
   - When a state matches the national average exactly, assert efficiency_index = 100.0

Create tests/test_loader.py:

1. test_load_production_facts_upsert
   - Mock the database
   - Load same record twice with different values
   - Assert the second load updates, not inserts duplicate

2. test_pipeline_run_logging
   - Assert log_pipeline_run returns an integer run_id
   - Assert all fields are correctly stored

Create a conftest.py with shared fixtures:
- sample_production_df() — returns a realistic 12-month production DataFrame for 5 states
- db_session() — creates a test database (SQLite in-memory for speed), initializes schema, yields session, teardown
- eia_client_mock() — mocks requests.Session to return test JSON without hitting the real API

Run all tests with: pytest tests/ -v --tb=short

All tests must pass. Target: 100% coverage on cleaner.py and metrics.py.
```

---

## PHASE 7 — GCP Deployment

### What This Phase Does
Deploys the pipeline to GCP using Cloud Functions for scheduling and BigQuery as the cloud warehouse.

### PROMPT TO USE:

```
Create the GCP deployment configuration for the oilfield-ops-intelligence project.

Create gcp/cloud_functions/scheduled_ingestion/main.py:

This is a Google Cloud Function (Python 3.11, gen2) triggered by Cloud Scheduler on a monthly cron.

The function entry point is: def run_monthly_pipeline(request):

Inside the function:
1. Initialize the EIAClient and BakerHughesFetcher
2. Set start_date = first day of last month, end_date = last day of last month
3. Run: production_df = eia_client.get_crude_oil_production(start_date, end_date)
4. Run: rig_df = baker_fetcher.fetch_rig_count_csv(current_year)
5. Pass through DataCleaner → MetricsCalculator → AnomalyDetector
6. Connect to BigQuery (using google-cloud-bigquery library, credentials from environment)
7. Load to BigQuery tables (same Star Schema, mapped to BQ column types)
8. Log the run result to pipeline_run_log
9. Return JSON response: {"status": "success", "records_loaded": N, "run_id": X}

Handle all exceptions: any unhandled exception → log to Cloud Logging → return {"status": "error", "message": str(e)} with HTTP 500

Create gcp/cloud_functions/scheduled_ingestion/requirements.txt:
List: functions-framework, google-cloud-bigquery, google-cloud-storage, pandas, numpy, requests, python-dotenv, loguru

Create a deployment shell script gcp/deploy.sh that:
1. Creates the GCP bucket for raw data storage (gsutil mb)
2. Deploys the Cloud Function (gcloud functions deploy)
3. Creates a Cloud Scheduler job that triggers it on the 3rd of every month at 6:00 AM UTC
4. Sets all required environment variables as Cloud Function secrets (--set-env-vars)
5. Prints the Cloud Function URL and Scheduler job name on success

Create gcp/bigquery_schema.json — the BigQuery table schema JSON for fact_production, with correct BQ types:
- DATE for dates (not TIMESTAMP)
- FLOAT64 for production values
- INT64 for rig counts and keys
- BOOL for boolean flags
- STRING for varchar fields

Add a section to README.md explaining GCP setup in 5 steps: create project, enable APIs, set service account, run deploy.sh, verify in Cloud Console.
```

---

## PHASE 8 — Final Polish & Documentation

### What This Phase Does
Adds the professional finishing touches: a beautiful README with screenshots section, architecture diagram, and project documentation.

### PROMPT TO USE:

```
Create the final professional documentation for oilfield-ops-intelligence.

Rewrite README.md as a world-class open source project README:

Structure:
1. Header: ASCII art or text logo "OOID", subtitle "OilField Ops Intelligence Dashboard"
2. Badges row: Python 3.11+, PostgreSQL, Streamlit, GCP, License MIT, Status: Active
3. One-line description: "End-to-end oil & gas production analytics platform with automated ETL pipeline, Star Schema data warehouse, and executive-grade dashboard."
4. Demo GIF placeholder: ![Dashboard Preview](docs/assets/demo.gif)
5. Features section with emoji bullets — be specific: ✅ Automated monthly data ingestion from EIA API, ✅ Star Schema data warehouse (Kimball methodology), etc.
6. Architecture section with ASCII diagram of the full pipeline
7. Tech Stack table
8. Quick Start (5 steps: clone, cp .env.example .env, add EIA API key, docker-compose up, open localhost:8501)
9. Project Structure tree
10. Data Sources section
11. Configuration reference: all .env variables explained
12. Contributing guide
13. License

Create docs/architecture.md with:
- Full system architecture narrative (2-3 paragraphs)
- Data flow description step by step
- Data model documentation (describe each table, each column, why it was designed that way)
- Design decisions section: Why Star Schema? Why Airflow? Why Streamlit over Power BI for open source?
- Known limitations and future improvements

Make it sound like it was written by a thoughtful engineer who made deliberate architectural choices, not someone who built the first thing that came to mind.
```