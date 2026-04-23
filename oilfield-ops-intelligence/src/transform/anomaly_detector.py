import pandas as pd
import numpy as np
from loguru import logger

class AnomalyDetector:
    """
    Detects statistical anomalies in oilfield production data.
    """

    def __init__(self):
        logger.info("AnomalyDetector initialized.")

    def detect_statistical_anomalies(self, df: pd.DataFrame, value_col: str, window: int = 3) -> pd.DataFrame:
        """
        Detects anomalies using a rolling z-score method.
        Note: For monthly data, window is in months.
        """
        if df.empty or value_col not in df.columns:
            return df

        df = df.sort_values(['state_code', 'date'])
        
        # Calculate rolling mean and std
        grouped = df.groupby('state_code')[value_col]
        rolling_mean = grouped.transform(lambda x: x.rolling(window=window, min_periods=1).mean())
        rolling_std = grouped.transform(lambda x: x.rolling(window=window, min_periods=1).std())
        
        # Z-score: (x - mean) / std
        df['z_score'] = (df[value_col] - rolling_mean) / rolling_std
        df['z_score'] = df['z_score'].replace([np.inf, -np.inf], 0).fillna(0)
        
        # Flag anomalies (|z| > 2.5)
        df['is_anomaly'] = df['z_score'].abs() > 2.5
        
        # Severity
        df['anomaly_severity'] = 'NONE'
        df.loc[df['z_score'].abs() > 2.5, 'anomaly_severity'] = 'LOW'
        df.loc[df['z_score'].abs() > 3.0, 'anomaly_severity'] = 'MEDIUM'
        df.loc[df['z_score'].abs() > 4.0, 'anomaly_severity'] = 'HIGH'
        
        # Description
        df['anomaly_description'] = ""
        anom_mask = df['is_anomaly']
        df.loc[anom_mask, 'anomaly_description'] = df.apply(
            lambda x: f"Value of {x[value_col]:.2f} is {x['z_score']:.2f} standard deviations from {window}-month mean" 
            if x['is_anomaly'] else "", axis=1
        )
        
        logger.info(f"Anomaly detection complete. Found {df['is_anomaly'].sum()} statistical anomalies.")
        return df

    def detect_sudden_drops(self, df: pd.DataFrame, value_col: str, threshold_pct: float = -30.0) -> pd.DataFrame:
        """Flags month-over-month drops greater than threshold_pct (e.g., -30%)."""
        mom_col = f'{value_col}_mom_growth_pct'
        if mom_col not in df.columns:
            return df
            
        drop_mask = df[mom_col] < threshold_pct
        df.loc[drop_mask, 'is_anomaly'] = True
        df.loc[drop_mask, 'anomaly_severity'] = 'HIGH'
        df.loc[drop_mask, 'anomaly_description'] = df.loc[drop_mask, 'anomaly_description'] + " | SUDDEN_DROP detected."
        
        return df
