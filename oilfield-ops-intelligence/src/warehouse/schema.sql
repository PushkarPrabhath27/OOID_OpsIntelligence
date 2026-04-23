-- OilField Ops Intelligence Dashboard (OOID) - Star Schema DDL

-- 1. Dimension: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year SMALLINT NOT NULL,
    quarter SMALLINT NOT NULL,
    month SMALLINT NOT NULL,
    month_name VARCHAR(10) NOT NULL,
    month_abbrev VARCHAR(3) NOT NULL,
    day_of_year SMALLINT NOT NULL,
    week_of_year SMALLINT NOT NULL,
    is_month_start BOOLEAN NOT NULL,
    is_month_end BOOLEAN NOT NULL,
    fiscal_year SMALLINT NOT NULL,
    fiscal_quarter SMALLINT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_dim_date_full_date ON dim_date(full_date);

-- 2. Dimension: Location
CREATE TABLE IF NOT EXISTS dim_location (
    location_key SERIAL PRIMARY KEY,
    state_code CHAR(2) NOT NULL UNIQUE,
    state_name VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    country CHAR(2) DEFAULT 'US',
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6)
);
CREATE INDEX IF NOT EXISTS idx_dim_location_region ON dim_location(region);

-- 3. Dimension: Well Type
CREATE TABLE IF NOT EXISTS dim_well_type (
    well_type_key SERIAL PRIMARY KEY,
    well_category VARCHAR(30) NOT NULL, -- 'Tight Oil', 'Conventional', etc.
    primary_product VARCHAR(20) NOT NULL, -- 'Crude Oil', 'Natural Gas'
    formation_type VARCHAR(50)
);

-- 4. Fact: Production
CREATE TABLE IF NOT EXISTS fact_production (
    production_id BIGSERIAL PRIMARY KEY,
    date_key INTEGER REFERENCES dim_date(date_key),
    location_key INTEGER REFERENCES dim_location(location_key),
    well_type_key INTEGER REFERENCES dim_well_type(well_type_key),
    
    -- Measures
    crude_production_bbls DECIMAL(15,2),
    gas_production_mcf DECIMAL(15,2),
    active_rig_count SMALLINT,
    
    -- Derived Metrics
    production_per_rig DECIMAL(10,2),
    mom_growth_pct DECIMAL(8,4),
    yoy_growth_pct DECIMAL(8,4),
    rolling_3m_avg DECIMAL(15,2),
    rolling_12m_avg DECIMAL(15,2),
    efficiency_index DECIMAL(8,2),
    
    -- Quality & Anomalies
    data_quality_score DECIMAL(3,2),
    data_quality_flags TEXT[], -- Postgres Array Type
    is_anomaly BOOLEAN DEFAULT FALSE,
    anomaly_severity VARCHAR(10) DEFAULT 'NONE',
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE (date_key, location_key, well_type_key)
);
CREATE INDEX IF NOT EXISTS idx_fact_prod_date_loc ON fact_production(date_key, location_key);
CREATE INDEX IF NOT EXISTS idx_fact_prod_anomaly ON fact_production(is_anomaly) WHERE is_anomaly = TRUE;

-- 5. Operational: Pipeline Log
CREATE TABLE IF NOT EXISTS pipeline_run_log (
    run_id SERIAL PRIMARY KEY,
    pipeline_name VARCHAR(100) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR(20), -- 'SUCCESS', 'FAILED', 'RUNNING'
    records_extracted INTEGER,
    records_transformed INTEGER,
    records_loaded INTEGER,
    records_rejected INTEGER,
    error_message TEXT,
    duration_seconds DECIMAL(10,2)
);
