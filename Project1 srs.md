# Software Requirements Specification (SRS)
## OilField Ops Intelligence Dashboard (OOID)
### Version 1.0 | April 2026

---

**Document Control**

| Field | Detail |
|---|---|
| Document Title | Software Requirements Specification — OOID |
| Version | 1.0 |
| Status | Draft |
| Author | [Your Name] |
| Reviewer | — |
| Approved By | — |
| Created | April 2026 |
| Last Modified | April 2026 |

---

## Table of Contents

1. Introduction
2. Overall Description
3. Functional Requirements
4. Non-Functional Requirements
5. Data Requirements
6. Interface Requirements
7. System Architecture Requirements
8. Constraints & Assumptions
9. Acceptance Criteria

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification defines the complete functional and non-functional requirements for the OilField Ops Intelligence Dashboard (OOID) — an end-to-end data engineering and business intelligence platform built around US oilfield production data.

This document serves as the authoritative reference for development, testing, and stakeholder communication. Any feature or behavior not described here is considered out of scope for Version 1.0.

### 1.2 Scope

OOID is a standalone data platform consisting of:

- An automated data ingestion system connecting to public US energy data sources
- A multi-stage ETL (Extract, Transform, Load) pipeline with data quality controls
- A Star Schema relational data warehouse hosted on PostgreSQL (local) and BigQuery (cloud)
- An interactive, multi-page business intelligence dashboard built in Streamlit
- A cloud deployment layer on Google Cloud Platform for production operation

The system covers US oil and gas production data from 2015 to present and refreshes monthly.

### 1.3 Definitions

| Term | Definition |
|---|---|
| ETL | Extract, Transform, Load — the process of moving data from source to warehouse |
| Star Schema | A dimensional data modeling pattern with a central fact table surrounded by dimension tables |
| Bronze Layer | Raw, unprocessed data stored exactly as received from source |
| Gold Layer | Cleaned, transformed, warehouse-ready data |
| EIA | US Energy Information Administration — primary data source |
| BBL | Barrel — unit of crude oil volume |
| MCF | Thousand Cubic Feet — unit of natural gas volume |
| KPI | Key Performance Indicator |
| MoM | Month-over-Month |
| YoY | Year-over-Year |
| DAG | Directed Acyclic Graph — Airflow pipeline definition |
| GCP | Google Cloud Platform |

### 1.4 References

- US EIA Open Data API Documentation: https://www.eia.gov/opendata/
- Baker Hughes Rig Count Archive: https://rigcount.bakerhughes.com/
- Kimball Group Dimensional Modeling: The Data Warehouse Toolkit, 3rd Ed.
- Streamlit Documentation: https://docs.streamlit.io/
- Google BigQuery Documentation: https://cloud.google.com/bigquery/docs
- SLB BI Engineer Internship JD (attached)
- SLB Associate Data Engineer Internship JD (attached)

---

## 2. Overall Description

### 2.1 Product Perspective

OOID is built as a standalone project that mirrors the real-world data engineering and BI workflows at energy technology companies such as SLB. It demonstrates the complete data lifecycle from raw API ingestion through to executive-facing visualization, deployed on production-grade infrastructure.

The system is designed to be:
- **Reproducible:** Any developer can set it up locally in under 10 minutes via Docker
- **Observable:** Every pipeline run is logged, every data quality issue is flagged
- **Extensible:** New data sources or dashboard pages can be added without rewriting existing components

### 2.2 User Classes

| User Type | Description | Primary Interaction |
|---|---|---|
| Executive / Business User | Non-technical stakeholder interested in production trends and KPIs | Executive Overview and State Drilldown pages |
| Operations Analyst | Intermediate user who needs state-level drill-downs and anomaly investigation | All dashboard pages |
| Data Engineer (Developer) | Technical user who monitors pipeline health and data quality | Pipeline Monitor page, direct database access |

### 2.3 Product Functions (Summary)

- Automated ingestion of US crude oil production, natural gas production, and rig count data
- Data cleaning, validation, and quality scoring
- Derived metric calculation: MoM growth, YoY growth, production-per-rig, efficiency index
- Anomaly detection using rolling z-score methodology
- Star Schema data warehousing in PostgreSQL and BigQuery
- Five-page interactive Streamlit dashboard
- Monthly scheduled pipeline runs via GCP Cloud Functions

### 2.4 Constraints

- All data sources must be publicly available at zero cost
- The system must run locally via Docker without cloud credentials for development
- The dashboard must be usable on a 1920×1080 screen without horizontal scrolling
- The pipeline must complete a full monthly refresh in under 15 minutes

---

## 3. Functional Requirements

### 3.1 Data Ingestion

#### FR-ING-001: EIA API Integration
**Priority:** Critical
**Description:** The system shall connect to the US Energy Information Administration Open Data API v2 to retrieve oil and gas production data.
**Details:**
- Shall authenticate using an API key stored in environment variables
- Shall retrieve crude oil production data by US state at monthly frequency
- Shall retrieve natural gas production data by US state at monthly frequency
- Shall retrieve refinery utilization rates at weekly frequency
- Shall handle paginated responses (EIA returns max 5,000 rows per request)

**Acceptance Test:** Given a valid EIA API key, the system retrieves at least 12 months of crude oil production data for all 50 US states without error.

#### FR-ING-002: Baker Hughes Rig Count Integration
**Priority:** High
**Description:** The system shall ingest Baker Hughes North America rig count data.
**Details:**
- Shall download weekly rig count CSV from Baker Hughes public archive
- Shall parse the multi-header CSV format correctly
- Shall extract: total US rig count, oil rigs, gas rigs, state-level breakdown
- Shall aggregate weekly data to monthly averages for warehouse loading

**Acceptance Test:** The system downloads and parses the current year's rig count data, producing a clean DataFrame with correct column names and numeric types.

#### FR-ING-003: Bronze Layer Storage
**Priority:** High
**Description:** All raw data fetched from sources shall be saved to a Bronze layer before transformation.
**Details:**
- Raw data stored as timestamped JSON files in data/raw/{source_name}/
- Each raw file accompanied by a metadata sidecar with: source name, fetch timestamp, record count, date range covered
- Bronze files are never modified after creation

#### FR-ING-004: Retry and Error Handling
**Priority:** High
**Description:** The ingestion layer shall handle transient failures gracefully.
**Details:**
- Shall retry failed API requests up to 3 times with exponential backoff (1s, 2s, 4s)
- Shall log every retry attempt with timestamp and error details
- Shall raise a typed exception (EIAAPIError) if all retries are exhausted
- Shall NOT silently swallow errors

---

### 3.2 Data Transformation

#### FR-ETL-001: Date Standardization
**Priority:** Critical
**Description:** All date fields in ingested data shall be standardized to Python datetime objects before loading.
**Details:**
- Shall handle formats: YYYY-MM, YYYY-MM-DD, Mon YYYY (e.g., "Jan 2023")
- Failed date parses shall be logged and the row flagged, not silently dropped

#### FR-ETL-002: State Code Normalization
**Priority:** Critical
**Description:** State identifiers shall be normalized to 2-letter uppercase USPS abbreviations.
**Details:**
- Shall map full state names ("Texas") to codes ("TX")
- Shall uppercase any lowercase codes
- Unrecognized state identifiers shall be flagged and logged

#### FR-ETL-003: Data Quality Scoring
**Priority:** High
**Description:** Every row in the warehouse shall have an associated data quality score.
**Details:**
- Score 1.0: Clean, no issues
- Score 0.7: Forward-filled to handle a null (max 2 consecutive fills allowed)
- Score 0.3: Statistical outlier flagged (value > 3 standard deviations from column mean)
- Score 0.0: Invalid value (negative production, unparseable date)
- The data_quality_flags column shall list all flags applied to a row as an array

#### FR-ETL-004: Derived Metrics Calculation
**Priority:** High
**Description:** The transform layer shall calculate the following derived metrics before warehouse loading.

| Metric | Formula | Notes |
|---|---|---|
| production_per_rig | crude_production_bbls / active_rig_count | NaN when rig_count = 0 |
| mom_growth_pct | (current - prior_month) / prior_month × 100 | NaN for first month of each state |
| yoy_growth_pct | (current - same_month_prior_year) / same_month_prior_year × 100 | NaN for first 12 months |
| rolling_3m_avg | 3-month rolling mean of crude_production_bbls, grouped by state | |
| rolling_12m_avg | 12-month rolling mean, grouped by state | |
| efficiency_index | (state production_per_rig / national_avg_production_per_rig) × 100 | 100 = national average |

#### FR-ETL-005: Anomaly Detection
**Priority:** High
**Description:** The system shall automatically detect and flag anomalous production values.
**Details:**
- Method: Rolling z-score over 90-day window
- Threshold: Flag rows where |z-score| > 2.5
- Severity levels: LOW (2.5–3.0), MEDIUM (3.0–4.0), HIGH (>4.0)
- Additionally flag: month-over-month drops > 30% as SUDDEN_DROP
- Anomaly description must be human-readable (e.g., "Production 340% above 3-month average")

---

### 3.3 Data Warehouse

#### FR-DW-001: Star Schema Implementation
**Priority:** Critical
**Description:** The data warehouse shall implement a Star Schema with one fact table and three dimension tables.

**Fact Table:** fact_production — one row per state per month
**Dimension Tables:** dim_date, dim_location, dim_well_type
**Operational Table:** pipeline_run_log

See Section 5 (Data Requirements) for complete schema definitions.

#### FR-DW-002: Upsert on Conflict
**Priority:** High
**Description:** Loading the same state-month combination twice shall UPDATE the existing record, not create a duplicate.
**Details:**
- Conflict key: (date_key, location_key) combination
- On conflict: update all measure columns and set updated_at = NOW()

#### FR-DW-003: Referential Integrity
**Priority:** High
**Description:** All foreign key relationships shall be enforced at the database level.
- fact_production.date_key must exist in dim_date
- fact_production.location_key must exist in dim_location
- fact_production.well_type_key must exist in dim_well_type

#### FR-DW-004: Date Dimension Pre-Population
**Priority:** High
**Description:** dim_date shall be pre-populated with every date from 2010-01-01 through 2030-12-31 during schema initialization.

#### FR-DW-005: Pipeline Run Logging
**Priority:** High
**Description:** Every pipeline execution shall write a record to pipeline_run_log with: start time, end time, status, records processed, records rejected, error message (if any).

---

### 3.4 Dashboard

#### FR-DASH-001: Executive Overview Page
**Priority:** Critical
**Description:** The first page of the dashboard shall display top-level US oilfield operational KPIs and trends.

**Required Elements:**
- 4 KPI cards: US crude production (BBL/day), active rig count, national efficiency index, anomaly count (30d)
- Each KPI card shows: current value, delta vs prior period, delta percentage, colored up/down indicator
- Full-width monthly production trend chart (5-year history) with 12-month rolling average overlay
- US choropleth map colored by crude production volume, all states
- Top 10 producing states table with rank, production, MoM change

#### FR-DASH-002: State Drilldown Page
**Priority:** Critical
**Description:** Users shall be able to select any US state and view its complete operational profile.

**Required Elements:**
- State selector dropdown
- 4 state-level KPI cards (same metrics as national, scoped to state)
- 10-year production history line chart
- Rig count trend chart (2-year)
- Efficiency index trend vs national average (3-year)
- Anomaly table for selected state (last 6 months)

#### FR-DASH-003: Rig Efficiency Analysis Page
**Priority:** High
**Description:** A dedicated page for analyzing rig count vs production efficiency.

**Required Elements:**
- Scatter plot: X = rig count, Y = production, sized by efficiency index, colored by region
- Horizontal bar chart of all states ranked by efficiency index, color-coded vs national average
- Top 5 / Bottom 5 states by efficiency index highlighted

#### FR-DASH-004: Pipeline Monitor Page
**Priority:** High
**Description:** A technical page showing data pipeline health and data quality metrics.

**Required Elements:**
- System status badge (HEALTHY / DEGRADED / DOWN)
- Pipeline run timeline chart (last 30 runs)
- Success rate metric (last 30 runs)
- Data coverage table (one row per state: last update date, record count, freshness)
- Data quality breakdown chart (distribution of quality scores)

#### FR-DASH-005: Anomaly Log Page
**Priority:** High
**Description:** A searchable, filterable table of all detected anomalies.

**Required Elements:**
- Filter controls: date range, state, severity level
- Anomaly table with: date, state, metric, observed value, expected value, deviation %, severity, description
- Summary counts by severity type

#### FR-DASH-006: Data Freshness Indicator
**Priority:** Medium
**Description:** Every page shall show a data freshness indicator in the header.
- Green: data updated within last 24 hours
- Yellow: data 1–3 days old
- Red: data > 3 days old

---

### 3.5 Pipeline Orchestration

#### FR-ORCH-001: Monthly Automated Pipeline
**Priority:** High
**Description:** The complete ingestion-transform-load cycle shall run automatically on the 3rd of each month.

#### FR-ORCH-002: Manual Trigger
**Priority:** Medium
**Description:** The pipeline shall be triggerable manually via a command-line script for development and backfill purposes.
```
python -m src.pipeline.run --start-date 2023-01 --end-date 2023-12
```

---

## 4. Non-Functional Requirements

### 4.1 Performance

| Requirement | Target |
|---|---|
| FR-PERF-001: Pipeline completion time | Full monthly refresh completes in < 15 minutes |
| FR-PERF-002: Dashboard page load time | Each dashboard page loads in < 3 seconds on first load |
| FR-PERF-003: State drilldown query time | State drilldown data loads in < 2 seconds |
| FR-PERF-004: Warehouse query performance | All analytics queries complete in < 5 seconds with proper indexing |

### 4.2 Reliability

| Requirement | Target |
|---|---|
| FR-REL-001: Pipeline retry | Transient API failures retried automatically; no human intervention needed |
| FR-REL-002: Data completeness | If ingestion fails for one state, other states still process successfully |
| FR-REL-003: Graceful degradation | Dashboard loads even when pipeline_run_log has no entries |

### 4.3 Maintainability

| Requirement | Standard |
|---|---|
| FR-MAIN-001: Code documentation | All public methods have complete docstrings |
| FR-MAIN-002: Type hints | All function signatures have type annotations |
| FR-MAIN-003: Logging | All significant events logged at appropriate level (INFO/WARNING/ERROR) via loguru |
| FR-MAIN-004: Test coverage | Unit test coverage ≥ 80% for transform and warehouse layers |
| FR-MAIN-005: Configuration | No hardcoded credentials or environment-specific values in source code |

### 4.4 Security

| Requirement | Standard |
|---|---|
| FR-SEC-001: API Keys | Stored in environment variables only; never committed to Git |
| FR-SEC-002: Database credentials | Stored in .env file, which is gitignored |
| FR-SEC-003: .env template | .env.example committed with placeholder values and comments |

### 4.5 Usability

| Requirement | Standard |
|---|---|
| FR-USE-001: Setup time | Developer can run `docker-compose up` and access dashboard in < 10 minutes |
| FR-USE-002: Responsive layout | Dashboard usable at 1280px wide and above |
| FR-USE-003: Error messages | User-facing errors show helpful context, not raw Python tracebacks |
| FR-USE-004: Loading states | All data-loading operations show a spinner with a descriptive message |

---

## 5. Data Requirements

### 5.1 Data Sources

| Source | Data | Frequency | Format | License |
|---|---|---|---|---|
| EIA Open Data API | Crude oil production, natural gas production, refinery utilization | Monthly | JSON REST API | Public domain |
| Baker Hughes | North America rig count by state | Weekly | CSV download | Publicly available |

### 5.2 Data Volume Estimates

| Dataset | Estimated Records (Initial Load) | Growth Rate |
|---|---|---|
| fact_production | ~18,000 rows (50 states × ~360 months × 1) | ~50 rows/month |
| dim_date | ~7,305 rows (2010–2030) | Static after init |
| dim_location | 51 rows (50 states + DC) | Effectively static |
| dim_well_type | ~5 rows | Static |
| pipeline_run_log | Grows by 1 row/month | ~12 rows/year |

### 5.3 Data Retention

- Bronze layer raw files: retain for 12 months, then archive or delete
- Warehouse data: retained indefinitely (historical analysis is core value)
- Pipeline run logs: retained indefinitely

### 5.4 Complete Schema Definition

#### dim_date

| Column | Type | Nullable | Description |
|---|---|---|---|
| date_key | SERIAL | No | Surrogate primary key |
| full_date | DATE | No | Actual calendar date |
| year | SMALLINT | No | Calendar year (e.g., 2024) |
| quarter | SMALLINT | No | Quarter (1–4) |
| month | SMALLINT | No | Month number (1–12) |
| month_name | VARCHAR(10) | No | Full month name (e.g., "January") |
| month_abbrev | VARCHAR(3) | No | Abbreviated month (e.g., "Jan") |
| week_of_year | SMALLINT | No | ISO week number |
| is_month_start | BOOLEAN | No | True if first day of month |
| is_month_end | BOOLEAN | No | True if last day of month |
| fiscal_year | SMALLINT | No | SLB fiscal year |
| fiscal_quarter | SMALLINT | No | SLB fiscal quarter |

#### dim_location

| Column | Type | Nullable | Description |
|---|---|---|---|
| location_key | SERIAL | No | Surrogate primary key |
| state_code | CHAR(2) | No | USPS state abbreviation |
| state_name | VARCHAR(50) | No | Full state name |
| region | VARCHAR(50) | No | Oil production region |
| country | CHAR(2) | No | Country code (US) |
| latitude | DECIMAL(9,6) | Yes | State centroid latitude |
| longitude | DECIMAL(9,6) | Yes | State centroid longitude |

#### dim_well_type

| Column | Type | Nullable | Description |
|---|---|---|---|
| well_type_key | SERIAL | No | Surrogate primary key |
| well_category | VARCHAR(30) | No | Tight Oil/Shale, Conventional, Offshore, Other |
| primary_product | VARCHAR(20) | No | Crude Oil, Natural Gas, Both |
| formation_type | VARCHAR(50) | Yes | Geological formation description |

#### fact_production

| Column | Type | Nullable | Description |
|---|---|---|---|
| production_id | BIGSERIAL | No | Surrogate primary key |
| date_key | INTEGER | No | FK → dim_date |
| location_key | INTEGER | No | FK → dim_location |
| well_type_key | INTEGER | No | FK → dim_well_type |
| crude_production_bbls | DECIMAL(15,2) | Yes | Monthly crude production in BBL |
| gas_production_mcf | DECIMAL(15,2) | Yes | Monthly gas production in MCF |
| active_rig_count | SMALLINT | Yes | Average active rigs for the month |
| production_per_rig | DECIMAL(10,2) | Yes | BBL per active rig |
| mom_growth_pct | DECIMAL(8,4) | Yes | Month-over-month % change |
| yoy_growth_pct | DECIMAL(8,4) | Yes | Year-over-year % change |
| rolling_3m_avg | DECIMAL(15,2) | Yes | 3-month rolling average production |
| rolling_12m_avg | DECIMAL(15,2) | Yes | 12-month rolling average production |
| efficiency_index | DECIMAL(8,2) | Yes | Relative efficiency (100 = national avg) |
| data_quality_score | DECIMAL(3,2) | No | 0.0–1.0 quality score |
| data_quality_flags | TEXT[] | Yes | Array of flag strings |
| is_anomaly | BOOLEAN | No | True if any anomaly detected |
| anomaly_severity | VARCHAR(10) | Yes | LOW, MEDIUM, HIGH |
| created_at | TIMESTAMP | No | Row creation timestamp |
| updated_at | TIMESTAMP | No | Row last update timestamp |

---

## 6. Interface Requirements

### 6.1 External Interfaces

#### EIA API
- **Endpoint:** https://api.eia.gov/v2/
- **Auth:** API key as query parameter `api_key`
- **Response:** JSON with nested `response.data` array
- **Rate Limit:** Not officially published; implement 0.5s delay between requests

#### Baker Hughes CSV
- **Access:** HTTP GET on publicly accessible URL
- **Format:** CSV with multi-row headers (first 2 rows are merged headers)
- **Columns of interest:** Week Ending, United States (total), state-level breakdown

### 6.2 Internal Interfaces

All internal modules communicate via pandas DataFrames with defined column contracts. Any module that produces a DataFrame must output columns exactly matching the contract expected by the next module in the pipeline. Deviations fail loudly (assertion errors or Pydantic validation errors), not silently.

### 6.3 Dashboard Interface

- **Access:** Web browser at http://localhost:8501 (local) or Cloud Run URL (GCP)
- **Supported browsers:** Chrome 110+, Firefox 110+, Edge 110+, Safari 16+
- **Minimum resolution:** 1280 × 800

---

## 7. System Architecture Requirements

### 7.1 Local Development Architecture

```
Developer Machine
├── Docker Compose
│   ├── PostgreSQL 15 container (port 5432)
│   ├── pgAdmin container (port 5050)
│   └── Streamlit container (port 8501)
└── Python venv (for running pipeline scripts directly)
```

### 7.2 Production Architecture (GCP)

```
Google Cloud Platform
├── Cloud Scheduler (cron: 0 6 3 * *)
│   └── triggers →
├── Cloud Function (run_monthly_pipeline)
│   ├── reads/writes → Cloud Storage (Bronze layer)
│   └── loads → BigQuery (Gold layer)
└── Cloud Run (Streamlit dashboard)
    └── queries → BigQuery
```

### 7.3 Module Dependencies

```
ingestion/ ──────────────────────────────────────┐
                                                  ▼
transform/cleaner.py ──► transform/metrics.py ──► transform/anomaly_detector.py
                                                  │
                                                  ▼
                                         warehouse/loader.py
                                                  │
                                                  ▼
                                         analytics/queries.py
                                                  │
                                                  ▼
                                         dashboard/pages/*.py
```

---

## 8. Constraints & Assumptions

### 8.1 Constraints

- **C-001:** Only publicly available, zero-cost data sources may be used
- **C-002:** The project must be fully reproducible from a clean checkout using `docker-compose up`
- **C-003:** No cloud credits required for local development mode
- **C-004:** Python 3.11+ required; no compatibility with Python 3.9 or earlier guaranteed
- **C-005:** Dashboard must use Streamlit; no other frontend framework for this version

### 8.2 Assumptions

- **A-001:** The EIA API will remain free and publicly accessible throughout the project
- **A-002:** Baker Hughes will continue making historical rig count CSVs publicly available
- **A-003:** The developer has a Google account for GCP deployment (free tier is sufficient)
- **A-004:** Monthly production data from EIA is complete within 45 days of month end (EIA's stated publication schedule)
- **A-005:** PostgreSQL 15+ is the target database; no support for MySQL or other RDBMS required

---

## 9. Acceptance Criteria

The project is considered complete and shippable when ALL of the following are true:

| ID | Criterion | Verification Method |
|---|---|---|
| AC-001 | `docker-compose up` starts all services without error on a clean machine | Manual test on fresh clone |
| AC-002 | Running the pipeline script fetches at least 12 months of EIA data for 48+ US states | Automated test + log inspection |
| AC-003 | Transformed data passes all data quality assertions (no nulls in required fields, no invalid dates) | Pytest test suite passing |
| AC-004 | Star Schema is correctly populated with referential integrity enforced | SQL queries verifying FK counts |
| AC-005 | Dashboard renders all 5 pages without Python errors | Manual test in browser |
| AC-006 | Executive Overview loads in < 3 seconds on localhost with full dataset | Browser dev tools timing |
| AC-007 | Anomaly detection flags known test anomalies in test dataset | Pytest test for anomaly_detector.py |
| AC-008 | All unit tests pass: `pytest tests/ -v` exits 0 | CI run |
| AC-009 | GCP Cloud Function deploys and runs successfully via `gcp/deploy.sh` | Cloud Console verification |
| AC-010 | README.md accurately describes setup in 5 steps that actually work | Independent reviewer test |
| AC-011 | No hardcoded credentials appear anywhere in the Git history | `git log -S "api_key"` returns nothing |
| AC-012 | Dashboard renders correctly at 1280px wide without horizontal scroll | Browser test at 1280px |