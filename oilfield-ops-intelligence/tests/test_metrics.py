import pytest
import pandas as pd
import numpy as np
from src.transform.metrics import MetricsCalculator

def test_mom_growth_calculation():
    calc = MetricsCalculator()
    df = pd.DataFrame({
        'state_code': ['TX', 'TX', 'TX'],
        'date': pd.to_datetime(['2023-01-01', '2023-02-01', '2023-03-01']),
        'production_bbls': [100, 110, 99]
    })
    
    df = calc.calculate_mom_growth(df, 'production_bbls')
    
    # 100 -> 110 is +10%
    # 110 -> 99 is -10%
    assert df['production_bbls_mom_growth_pct'].iloc[1] == 10.0
    assert df['production_bbls_mom_growth_pct'].iloc[2] == -10.0

def test_production_per_rig_zero_division():
    calc = MetricsCalculator()
    prod_df = pd.DataFrame({
        'state_code': ['TX'],
        'date': pd.to_datetime(['2023-01-01']),
        'production_bbls': [1000]
    })
    rig_df = pd.DataFrame({
        'state_code': ['TX'],
        'date': pd.to_datetime(['2023-01-01']),
        'active_rig_count': [0] # Zero rigs
    })
    
    df = calc.calculate_production_per_rig(prod_df, rig_df)
    
    # Should be NaN, not error or inf
    assert np.isnan(df['production_per_rig'].iloc[0])

def test_efficiency_index_baseline():
    calc = MetricsCalculator()
    df = pd.DataFrame({
        'date': pd.to_datetime(['2023-01-01', '2023-01-01']),
        'state_code': ['TX', 'NM'],
        'production_per_rig': [100, 100] # Both are same as avg
    })
    
    df = calc.calculate_efficiency_index(df)
    assert df['efficiency_index'].iloc[0] == 100.0
