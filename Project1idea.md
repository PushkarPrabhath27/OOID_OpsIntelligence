# OilField Ops Intelligence Dashboard
### Project Idea & Concept Document — Version 1.0

---

## 1. The Big Picture

**Project Name:** OilField Ops Intelligence Dashboard (OOID)
**Tagline:** *From raw well data to boardroom-ready insights — automated, reliable, real-time.*

This project is a **production-grade, end-to-end data engineering + business intelligence system** built specifically around the oil & gas domain. It ingests publicly available US oilfield production data, processes it through a clean ETL pipeline, stores it in a well-designed relational data warehouse using Star Schema modeling, and surfaces insights through a professional, interactive Power BI-style dashboard built in Streamlit.

The entire system is designed to mirror exactly what a junior Data/BI engineer at a company like SLB would build on their first real project — not a toy, not a demo, but something that could be shown to a non-technical stakeholder and immediately communicate value.

---

## 2. Why This Project Exists

### The Problem It Solves
Oil & gas companies collect enormous volumes of operational data — daily production volumes, rig activity, well counts, efficiency ratios — but this data lives in raw government databases, CSVs, and reporting systems that are hard to query, impossible to visualize quickly, and require engineering effort to turn into decisions.

The OOID project solves this by:
- **Automating data ingestion** from the US Energy Information Administration (EIA) public API
- **Standardizing and cleaning** the data through a well-structured ETL pipeline
- **Storing it** in a Star Schema warehouse optimized for BI queries
- **Visualizing it** through an executive-grade dashboard with KPIs, trend lines, drill-downs, and anomaly indicators

### Why This Matters For SLB Specifically
SLB operates across 85+ countries and generates operational data at an enormous scale. Their internal BI, Data Engineering, and HANA teams do exactly what this project demonstrates:
- Design data models that reflect business logic (Star Schema)
- Build ETL pipelines that move data from source systems into warehouses
- Deploy visualizations that help business stakeholders make decisions
- Maintain data quality and pipeline reliability

Building this project in the oil & gas domain is not an accident — it's deliberate. It signals that you understand the industry, not just the technology.

---

## 3. What Exactly Gets Built

### Component 1 — Data Ingestion Layer
- Connects to the **EIA Open Data API** (free, no cost, publicly available)
- Pulls data on: US crude oil production by state, natural gas production, drilling rig counts (Baker Hughes rig count data), refinery utilization rates
- Handles pagination, rate limiting, and API failures gracefully
- Stores raw responses in a **Bronze layer** (raw, unprocessed) as JSON files / staging tables

### Component 2 — ETL Pipeline
- **Extract:** Pull from API + optionally from static CSV datasets (EIA bulk download)
- **Transform:** 
  - Data type standardization (dates, numeric fields)
  - Null handling and outlier flagging
  - Derived metrics calculation: month-over-month growth %, rig efficiency index, production-per-rig ratio
  - State/region code normalization
- **Load:** Insert cleaned, transformed data into PostgreSQL structured as a Star Schema
- Pipeline is orchestrated with **Apache Airflow** DAGs (or simple Python scheduler for lightweight version)
- Full logging of every pipeline run: start time, records processed, errors, duration

### Component 3 — Data Warehouse (Star Schema)
Designed following **Kimball's dimensional modeling** methodology:

```
FACT TABLE: fact_production
- production_id (PK)
- date_key (FK → dim_date)
- location_key (FK → dim_location)
- well_type_key (FK → dim_well_type)
- crude_production_bbls (measure)
- gas_production_mcf (measure)
- active_rig_count (measure)
- production_per_rig (derived measure)
- data_quality_flag (boolean)

DIMENSION: dim_date
- date_key (PK)
- full_date, year, quarter, month, month_name, week_of_year

DIMENSION: dim_location
- location_key (PK)
- state_code, state_name, region (Permian, Gulf Coast, Appalachian, etc.), country

DIMENSION: dim_well_type
- well_type_key (PK)
- well_category (conventional, shale/tight oil, offshore)
- formation_type, primary_product
```

### Component 4 — Dashboard (OOID Frontend)
Built in **Streamlit** with a dark, industrial, data-dense aesthetic appropriate for an oilfield operations context.

**Dashboard Pages:**
1. **Executive Overview** — Top-level KPIs: Total US production this month, YoY growth, active rig count, refinery utilization. Trend sparklines for each.
2. **State-Level Drill-Down** — Choropleth map of US production by state. Click a state → see its full production history, rig count trend, and efficiency metrics.
3. **Rig Activity & Efficiency** — Rig count vs production correlation chart. Efficiency index over time. Top 5 / Bottom 5 producing states by efficiency.
4. **Data Pipeline Monitor** — Shows pipeline run history, data freshness, records ingested, quality flags raised. This page is for the "data team" persona.
5. **Anomaly Log** — Any production values that deviated more than 2 standard deviations from the rolling 3-month average are flagged here with explanation.

### Component 5 — GCP Deployment (Bonus Layer)
- Pipeline runs scheduled via **Google Cloud Scheduler + Cloud Functions**
- Data warehouse hosted on **BigQuery** (replaces local PostgreSQL)
- Dashboard deployed via **Cloud Run**
- Everything connected, running on a free-tier GCP account

---

## 4. Technical Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                          │
│  EIA Open API  ──  Baker Hughes CSV  ──  EIA Bulk Download   │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────┐
│                     INGESTION LAYER                          │
│            Python Scripts / Cloud Functions                  │
│         Rate limiting · Error handling · Retry logic         │
└──────────────────┬───────────────────────────────────────────┘
                   │ Raw JSON / CSV
                   ▼
┌──────────────────────────────────────────────────────────────┐
│                   BRONZE LAYER (Raw Store)                   │
│              GCS Bucket / Local File System                  │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────┐
│                   TRANSFORM LAYER (ETL)                      │
│  Pandas / PySpark · Data cleaning · Metrics calculation      │
│  Null handling · Type standardization · Quality scoring      │
└──────────────────┬───────────────────────────────────────────┘
                   │ Clean, typed data
                   ▼
┌──────────────────────────────────────────────────────────────┐
│              GOLD LAYER — STAR SCHEMA WAREHOUSE              │
│          PostgreSQL (local) / BigQuery (cloud)               │
│     fact_production + dim_date + dim_location + dim_well     │
└──────────────────┬───────────────────────────────────────────┘
                   │ SQL Queries
                   ▼
┌──────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│           Streamlit Dashboard · Interactive Charts           │
│      Executive View · State Drilldown · Pipeline Monitor     │
└──────────────────────────────────────────────────────────────┘
```

---

## 5. Technology Stack

| Layer | Technology | Why |
|---|---|---|
| Language | Python 3.11+ | Industry standard for data engineering |
| Data Processing | Pandas, NumPy | Fast, well-supported ETL processing |
| Database (Local) | PostgreSQL 15 | Professional RDBMS, strong SQL support |
| Database (Cloud) | Google BigQuery | Matches BI Engineer JD requirement exactly |
| Orchestration | Apache Airflow | Industry standard pipeline orchestration |
| Visualization | Streamlit | Python-native, fast to build, looks professional |
| Charts | Plotly | Interactive, publication-quality charts |
| Maps | Folium / Plotly Geo | Choropleth maps for state-level data |
| Cloud | Google Cloud Platform | Matches SLB BI Engineer JD explicitly |
| Cloud Functions | GCP Cloud Functions | Scheduled pipeline runs |
| Version Control | Git + GitHub | Professional workflow, visible to recruiters |
| Testing | Pytest | Unit tests for pipeline components |
| Documentation | Mkdocs | Professional project documentation site |

---

## 6. Data Sources (All Free, All Public)

1. **EIA Open Data API** — `https://api.eia.gov/v2/` — Crude oil production, natural gas production, refinery data. Free API key, no cost.
2. **Baker Hughes Rig Count** — Weekly CSV downloads from their public website. Historical data going back to 1940.
3. **EIA State Energy Data System** — Bulk CSV download of state-level energy production going back decades.

No paid data sources. No licensing issues. Everything reproducible.

---

## 7. What Makes This Stand Out From Other Campus Projects

| Typical Campus Project | OOID Project |
|---|---|
| Random dataset from Kaggle | Domain-specific oil & gas data relevant to SLB |
| Basic bar charts in Matplotlib | Interactive multi-page Streamlit dashboard |
| Single Python script | Multi-component ETL pipeline with error handling |
| No data modeling | Proper Star Schema following Kimball methodology |
| No deployment | Deployed on GCP with scheduled pipeline runs |
| No tests | Unit tests for pipeline components |
| Generic README | Full SRS document + architecture diagrams |

---

## 8. What You Can Say In The Interview

When an SLB interviewer asks "tell me about a project you've built":

> "I built an end-to-end data engineering and BI system around US oilfield production data from the EIA. The system ingests data automatically through a scheduled ETL pipeline, models it using Star Schema dimensional modeling in a PostgreSQL data warehouse, and surfaces insights through a multi-page dashboard with KPIs, state-level drilldowns, rig efficiency analysis, and a pipeline monitoring view. I also deployed the pipeline on GCP using Cloud Functions and BigQuery, which gave me hands-on experience with the exact cloud stack mentioned in your BI Engineer role. The domain — oil and gas production analytics — was a deliberate choice because I wanted to understand the kind of data problems SLB works with."

That answer, backed by a live GitHub repo they can click, wins interviews.

---

## 9. Project Timeline

| Week | Milestone |
|---|---|
| Week 1, Days 1–2 | Set up project structure, EIA API integration, raw data ingestion |
| Week 1, Days 3–4 | Build ETL transform layer, data cleaning, metrics derivation |
| Week 1, Day 5 | Design and populate Star Schema in PostgreSQL |
| Week 2, Days 1–2 | Build Streamlit dashboard — Executive Overview + State Drilldown |
| Week 2, Days 3–4 | Add Anomaly Detection, Pipeline Monitor pages |
| Week 2, Day 5 | GCP deployment, Cloud Functions, BigQuery migration |
| Week 3 | Testing, documentation, GitHub README, demo video |

---

## 10. Deliverables (What Goes on GitHub)

```
oilfield-ops-intelligence/
├── README.md                    ← Professional README with screenshots
├── docs/                        ← Architecture diagrams, SRS
├── data/
│   ├── raw/                     ← Bronze layer raw files
│   └── processed/               ← Cleaned staging files
├── src/
│   ├── ingestion/               ← API connectors, data fetchers
│   ├── transform/               ← ETL logic, cleaning functions
│   ├── warehouse/               ← DB models, schema creation SQL
│   ├── analytics/               ← Metric calculations, anomaly detection
│   └── dashboard/               ← Streamlit app pages
├── airflow/
│   └── dags/                    ← Pipeline DAG definitions
├── gcp/
│   └── cloud_functions/         ← GCP deployment code
├── tests/                       ← Pytest unit tests
├── requirements.txt
└── docker-compose.yml           ← One-command local setup
```