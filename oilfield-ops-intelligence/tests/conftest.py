import pytest
import pandas as pd
import numpy as np
from datetime import datetime

@pytest.fixture
def sample_production_df():
    """Returns a realistic 12-month production DataFrame."""
    data = {
        'date': pd.date_range(start='2023-01-01', periods=3, freq='MS').tolist() * 2,
        'state_name': ['Texas', 'Texas', 'Texas', 'New Mexico', 'New Mexico', 'New Mexico'],
        'production_bbls': [1000, 1100, 1200, 500, 550, 600],
        'unit': ['BBL/day'] * 6
    }
    return pd.DataFrame(data)

@pytest.fixture
def dirty_production_df():
    """DataFrame with negatives, nulls, and inconsistent state names."""
    data = {
        'date': ['2023-01-01', '2023-02-01', '2023-03-01'],
        'state_name': ['Texas', 'tx', 'Texas'],
        'production_bbls': [1000, -50, None], # Negative and Null
        'unit': ['BBL/day'] * 3
    }
    return pd.DataFrame(data)
