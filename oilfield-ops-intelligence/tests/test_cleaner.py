import pytest
import pandas as pd
import numpy as np
from src.transform.cleaner import DataCleaner

def test_clean_production_data_handles_negatives(dirty_production_df):
    cleaner = DataCleaner()
    df = cleaner.clean_production_data(dirty_production_df)
    
    # Check that negative value was flagged
    neg_row = df[df['production_bbls'] == -50]
    assert 'NEGATIVE_VALUE' in neg_row['data_quality_flags'].iloc[0]
    assert neg_row['data_quality_score'].iloc[0] == 0.0

def test_clean_production_data_handles_forward_fill(dirty_production_df):
    cleaner = DataCleaner()
    df = cleaner.clean_production_data(dirty_production_df)
    
    # Row 3 (index 2) was None, should be filled with Row 2's value (-50)
    # Note: Sorts by state_code, date during clean
    df = df.sort_values(['state_code', 'date'])
    assert df['production_bbls'].isna().sum() == 0
    assert 'FORWARD_FILLED' in df.iloc[2]['data_quality_flags']
    assert df.iloc[2]['data_quality_score'] == 0.7

def test_state_code_normalization():
    cleaner = DataCleaner()
    df = pd.DataFrame({'state_name': ['Texas', 'New Mexico', 'California'], 'production_bbls': [1, 2, 3], 'date': ['2023-01-01']*3})
    df = cleaner.clean_production_data(df)
    
    assert set(df['state_code']) == {'TX', 'NM', 'CA'}
