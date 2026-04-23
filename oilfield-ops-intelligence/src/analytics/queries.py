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
                    1 as join_key,
                    SUM(f.crude_production_bbls) as total_prod,
                    SUM(f.active_rig_count) as total_rigs,
                    AVG(f.efficiency_index) as avg_eff,
                    (SELECT COUNT(*) FROM fact_production WHERE is_anomaly = TRUE AND date_key = (SELECT date_key FROM latest_month)) as anomaly_count
                FROM fact_production f
                WHERE f.date_key = (SELECT date_key FROM latest_month)
            ),
            prior_metrics AS (
                SELECT 
                    1 as join_key,
                    SUM(f.crude_production_bbls) as prior_prod
                FROM fact_production f
                JOIN dim_date d_curr ON d_curr.date_key = (SELECT date_key FROM latest_month)
                JOIN dim_date d_prev ON d_prev.year = CASE WHEN d_curr.month = 1 THEN d_curr.year - 1 ELSE d_curr.year END
                                    AND d_prev.month = CASE WHEN d_curr.month = 1 THEN 12 ELSE d_curr.month - 1 END
                WHERE f.date_key = d_prev.date_key
            )
            SELECT m.*, p.prior_prod 
            FROM metrics m
            LEFT JOIN prior_metrics p ON m.join_key = p.join_key
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

    def get_state_drilldown(self, state_code: str) -> Dict:
        """Returns a complete data package for a single state."""
        query = text("""
            SELECT 
                d.full_date as date,
                f.crude_production_bbls,
                f.active_rig_count,
                f.efficiency_index,
                f.is_anomaly,
                f.anomaly_severity
            FROM fact_production f
            JOIN dim_date d ON f.date_key = d.date_key
            JOIN dim_location l ON f.location_key = l.location_key
            WHERE l.state_code = :state_code
            ORDER BY d.full_date ASC
        """)
        
        with self.engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"state_code": state_code})
            if df.empty:
                return {}
            
            latest = df.iloc[-1]
            return {
                "history": df,
                "current_production": latest['crude_production_bbls'],
                "current_rigs": latest['active_rig_count'],
                "current_efficiency": latest['efficiency_index'],
                "anomalies": df[df['is_anomaly'] == True].tail(5)
            }

    def get_data_coverage(self) -> pd.DataFrame:
        """Returns records count and last update per state."""
        query = text("""
            SELECT 
                l.state_name,
                COUNT(f.production_id) as record_count,
                MAX(d.full_date) as last_update,
                AVG(f.data_quality_score) as avg_quality
            FROM dim_location l
            LEFT JOIN fact_production f ON l.location_key = f.location_key
            LEFT JOIN dim_date d ON f.date_key = d.date_key
            GROUP BY l.state_name
            ORDER BY last_update DESC
        """)
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn)
