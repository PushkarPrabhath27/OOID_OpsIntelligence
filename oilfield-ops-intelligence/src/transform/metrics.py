import pandas as pd
import numpy as np
from loguru import logger

class MetricsCalculator:
    """
    Calculates derived metrics for oil and gas production analytics.
    """

    def __init__(self):
        logger.info("MetricsCalculator initialized.")

    def calculate_production_per_rig(self, production_df: pd.DataFrame, rig_df: pd.DataFrame) -> pd.DataFrame:
        """
        Joins production and rig data to calculate efficiency.
        Formula: crude_production_bbls / active_rig_count
        """
        if production_df.empty or rig_df.empty:
            logger.warning("Empty DataFrame(s) provided to calculate_production_per_rig.")
            return production_df
            
        # Ensure dates are monthly for joining
        production_df['join_date'] = production_df['date'].dt.to_period('M')
        rig_df['join_date'] = rig_df['date'].dt.to_period('M')
        
        # Merge on date and state
        merged = pd.merge(
            production_df, 
            rig_df[['join_date', 'state_code', 'active_rig_count']], 
            on=['join_date', 'state_code'], 
            how='left'
        )
        
        # Calculate metric
        merged['production_per_rig'] = merged['production_bbls'] / merged['active_rig_count']
        
        # Handle division by zero or NaN
        merged['production_per_rig'] = merged['production_per_rig'].replace([np.inf, -np.inf], np.nan)
        
        return merged.drop(columns=['join_date'])

    def calculate_mom_growth(self, df: pd.DataFrame, value_col: str, group_col: str = 'state_code') -> pd.DataFrame:
        """Calculates month-over-month percentage change."""
        df = df.sort_values([group_col, 'date'])
        df[f'{value_col}_mom_growth_pct'] = df.groupby(group_col)[value_col].pct_change() * 100
        return df

    def calculate_yoy_growth(self, df: pd.DataFrame, value_col: str, group_col: str = 'state_code') -> pd.DataFrame:
        """Calculates year-over-year percentage change (12-month lag)."""
        df = df.sort_values([group_col, 'date'])
        df[f'{value_col}_yoy_growth_pct'] = df.groupby(group_col)[value_col].pct_change(periods=12) * 100
        return df

    def calculate_efficiency_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Efficiency Index = (state_prod_per_rig / national_avg_prod_per_rig) * 100
        """
        if 'production_per_rig' not in df.columns:
            return df
            
        # Calculate national average per month
        national_avg = df.groupby('date')['production_per_rig'].transform('mean')
        
        df['efficiency_index'] = (df['production_per_rig'] / national_avg) * 100
        return df
