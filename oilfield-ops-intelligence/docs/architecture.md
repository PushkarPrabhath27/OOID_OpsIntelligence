# OOID System Architecture

## 1. Architectural Overview
The OilField Ops Intelligence Dashboard (OOID) follows a modern **Data Lakehouse** architecture, separating storage into tiered layers to ensure data lineage and reliability.

### Data Layers
- **Bronze (Raw):** Immutable JSON/CSV files stored in `data/raw/`. These represent the "Source of Truth" as received from EIA/Baker Hughes.
- **Gold (Analytics):** A highly structured **Star Schema** relational model optimized for BI workloads, hosted in PostgreSQL.

## 2. The Star Schema (Kimball Methodology)
We implemented a dimensional model to ensure high-speed analytical queries:
- **Fact Table (`fact_production`):** Stores granular monthly measures.
- **Dimension Tables:** `dim_date`, `dim_location`, and `dim_well_type` provide the context for slicing and dicing.

**Why Star Schema?**
1. **Query Performance:** Reduces complex joins to simple FK lookups.
2. **Standardization:** Matches industry standards used by SLB's HANA and BI teams.

## 3. ETL Pipeline Flow
1. **Extraction:** Python `requests` session with exponential backoff.
2. **Transformation:** Vectorized Pandas operations for growth metrics (MoM/YoY).
3. **Validation:** Statistical anomaly detection using rolling Z-scores.
4. **Loading:** PostgreSQL UPSERT pattern ensuring idempotency.

## 4. Technology Stack Justification
- **Python/Pandas:** Chosen over Spark because the dataset (~20k rows initially) fits easily into memory. This provides significantly lower latency and infrastructure cost.
- **Streamlit:** Allows for rapid iteration of data-dense UIs using pure Python, keeping the "Logic" and "Presentation" close together.
- **SQLAlchemy:** Provides a database-agnostic ORM layer, making the eventual migration to BigQuery (Cloud) seamless.

## 5. Security & Governance
- API Keys and DB credentials are restricted to `.env` files.
- Every ETL run is audited in `pipeline_run_log`.
- Every data point is tagged with a `data_quality_score`.
