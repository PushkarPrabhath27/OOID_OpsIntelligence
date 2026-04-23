import pandas as pd
from sqlalchemy import text, Engine
from typing import Dict, Optional, List
from loguru import logger

class OilfieldAnalytics:
    """
    High-performance analytics layer for the OOID platform.
    Exposes data for the dashboard via optimized SQL queries.
    """

    def __init__(self, engine: Engine):
        self.engine = engine
        logger.info("OilfieldAnalytics initialized.")

    def get_national_kpis(self) -> Dict:
        """Returns top-level US operational KPIs for the latest month."""
        query = text("""
            WITH latest_month AS (
                SELECT date_key FROM fact_production 
                ORDER BY date_key DESC LIMIT 1
            ),
            metrics AS (
                SELECT 
                    SUM(crude_production_bbls) as total_prod,
                    SUM(active_rig_count) as total_rigs,
                    AVG(efficiency_index) as avg_eff,
                    (SELECT COUNT(*) FROM fact_production WHERE is_anomaly = TRUE AND date_key = (SELECT date_key FROM latest_month)) as anomaly_count
                FROM fact_production
                WHERE date_key = (SELECT date_key FROM latest_month)
            ),
            prior_metrics AS (
                SELECT 
                    SUM(crude_production_bbls) as prior_prod
                FROM fact_production
                WHERE date_key = (SELECT date_key - 100 FROM latest_month) -- Simple month lag for YYYYMMDD
            )
            SELECT * FROM metrics, prior_metrics
        """)
        
        try:
            with self.engine.connect() as conn:
                df = pd.read_sql(query, conn)
                if df.empty:
                    return {}
                
                row = df.iloc[0]
                mom_change = ((row['total_prod'] - row['prior_prod']) / row['prior_prod'] * 100) if row['prior_prod'] else 0
                
                return {
                    "current_production": row['total_prod'],
                    "active_rigs": row['total_rigs'],
                    "efficiency_index": row['avg_eff'],
                    "anomalies_30d": row['anomaly_count'],
                    "mom_change_pct": mom_change
                }
        except Exception as e:
            logger.error(f"Failed to fetch national KPIs: {e}")
            return {}

    def get_production_trend(self, years: int = 5) -> pd.DataFrame:
        """Returns monthly US production trend with rolling averages."""
        query = text("""
            SELECT 
                d.full_date as date,
                SUM(f.crude_production_bbls) as production,
                AVG(SUM(f.crude_production_bbls)) OVER(ORDER BY d.full_date ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) as rolling_12m_avg
            FROM fact_production f
            JOIN dim_date d ON f.date_key = d.date_key
            GROUP BY d.full_date
            ORDER BY d.full_date DESC
            LIMIT :limit
        """)
        
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn, params={"limit": years * 12})

    def get_state_comparison(self) -> pd.DataFrame:
        """Returns all states ranked by production for mapping."""
        query = text("""
            SELECT 
                l.state_code,
                l.state_name,
                l.latitude,
                l.longitude,
                f.crude_production_bbls as production,
                f.efficiency_index,
                RANK() OVER(ORDER BY f.crude_production_bbls DESC) as rank
            FROM fact_production f
            JOIN dim_location l ON f.location_key = l.location_key
            WHERE f.date_key = (SELECT MAX(date_key) FROM fact_production)
        """)
        
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn)

    def get_anomaly_log(self, limit: int = 50) -> pd.DataFrame:
        """Returns recent anomalies across all states."""
        query = text("""
            SELECT 
                d.full_date as date,
                l.state_name,
                f.crude_production_bbls as observed_value,
                f.anomaly_severity,
                f.anomaly_description
            FROM fact_production f
            JOIN dim_date d ON f.date_key = d.date_key
            JOIN dim_location l ON f.location_key = l.location_key
            WHERE f.is_anomaly = TRUE
            ORDER BY d.full_date DESC
            LIMIT :limit
        """)
        
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn, params={"limit": limit})

    def get_pipeline_history(self) -> pd.DataFrame:
        """Returns recent pipeline run logs."""
        query = text("SELECT * FROM pipeline_run_log ORDER BY started_at DESC LIMIT 10")
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn)
