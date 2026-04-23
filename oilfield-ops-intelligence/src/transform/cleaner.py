import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Dict
from loguru import logger

class DataCleaner:
    """
    Handles cleaning and standardization of raw oil and gas data.
    """
    
    # Mapping of common full state names to 2-letter codes
    STATE_MAP = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
        'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
        'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
        'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
        'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
        'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN',
        'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
        'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC'
    }

    def __init__(self):
        logger.info("DataCleaner initialized.")

    def standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Converts column names to snake_case and removes special characters."""
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(' ', '_', regex=False)
            .str.replace('-', '_', regex=False)
            .str.replace(r'[^a-z0-9_]', '', regex=True)
        )
        return df

    def clean_production_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans EIA crude oil/gas production data.
        """
        if df.empty:
            return df
            
        logger.info(f"Cleaning {len(df)} production records...")
        
        # 1. Standardize columns
        df = self.standardize_column_names(df)
        
        # 2. Parse dates
        # EIA periods are often YYYY-MM or YYYY-MM-DD
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # 3. Normalize state codes
        if 'state_name' in df.columns:
            df['state_code'] = df['state_name'].map(self.STATE_MAP).fillna(df.get('state_code', 'UNKNOWN'))
        
        if 'state_code' in df.columns:
            df['state_code'] = df['state_code'].str.upper().str.strip()
            
        # 4. Cast production to float64
        prod_col = 'production_bbls' if 'production_bbls' in df.columns else 'gas_production_mcf'
        df[prod_col] = pd.to_numeric(df[prod_col], errors='coerce')
        
        # 5. Initialize quality flags and scores
        df['data_quality_flags'] = [[] for _ in range(len(df))]
        df['data_quality_score'] = 1.0
        
        # 6. Check for negative values
        neg_mask = df[prod_col] < 0
        df.loc[neg_mask, 'data_quality_score'] = 0.0
        df.loc[neg_mask, 'data_quality_flags'] = df.loc[neg_mask, 'data_quality_flags'].apply(lambda x: x + ['NEGATIVE_VALUE'])
        
        # 7. Forward-fill missing values within each state group (max 2 consecutive)
        if 'state_code' in df.columns:
            # Sort to ensure forward fill makes sense chronologically
            df = df.sort_values(['state_code', 'date'])
            
            # Identify nulls before filling for scoring
            null_mask = df[prod_col].isna()
            
            df[prod_col] = df.groupby('state_code')[prod_col].ffill(limit=2)
            
            # Score filled rows
            filled_mask = null_mask & df[prod_col].notna()
            df.loc[filled_mask, 'data_quality_score'] = 0.7
            df.loc[filled_mask, 'data_quality_flags'] = df.loc[filled_mask, 'data_quality_flags'].apply(lambda x: x + ['FORWARD_FILLED'])

        # 8. Add inserted_at
        df['inserted_at'] = datetime.now()
        
        logger.info(f"Cleaning complete. Quality flags raised: {df['data_quality_flags'].apply(len).sum()}")
        return df

    def validate_date_range(self, df: pd.DataFrame, min_date: str, max_date: str) -> pd.DataFrame:
        """Filters rows outside the valid date range."""
        start = pd.to_datetime(min_date)
        end = pd.to_datetime(max_date)
        initial_count = len(df)
        df = df[(df['date'] >= start) & (df['date'] <= end)]
        logger.info(f"Dropped {initial_count - len(df)} rows outside range {min_date} to {max_date}")
        return df
