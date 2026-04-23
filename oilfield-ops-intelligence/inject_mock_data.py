import pandas as pd
import numpy as np
import os
from datetime import datetime
from sqlalchemy import text
from src.warehouse.loader import DataWarehouseLoader

def inject_mock():
    # Hardcoded Absolute Path for DB
    db_path = r"c:\Users\pushk\OneDrive\Documents\OOID SBL1\oilfield-ops-intelligence\ooid_warehouse.db"
    conn_str = f"sqlite:///{db_path}"
    
    loader = DataWarehouseLoader(connection_string=conn_str)
    
    # 1. Professional Locations with Coordinates
    # These are necessary for the Map and joins
    states = [
        ('TX', 'Texas', 'Permian Basin', 31.9686, -99.9018),
        ('NM', 'New Mexico', 'Permian Basin', 34.5199, -105.8701),
        ('ND', 'North Dakota', 'Bakken', 47.5515, -101.0020),
        ('AK', 'Alaska', 'North Slope', 64.2008, -149.4937),
        ('OK', 'Oklahoma', 'Anadarko', 35.4676, -97.5164)
    ]
    
    with loader.engine.connect() as conn:
        for idx, (code, name, reg, lat, lon) in enumerate(states):
            l_key = idx + 1
            conn.execute(text(f"""
                INSERT OR REPLACE INTO dim_location (location_key, state_code, state_name, region, country, latitude, longitude) 
                VALUES ({l_key}, '{code}', '{name}', '{reg}', 'US', {lat}, {lon})
            """))
        conn.commit()

    # 2. Mock Dates
    dates = pd.date_range(start='2023-01-01', end='2024-03-01', freq='MS')
    with loader.engine.connect() as conn:
        for d in dates:
            d_key = int(d.strftime('%Y%m%d'))
            conn.execute(text(f"""
                INSERT OR REPLACE INTO dim_date 
                (date_key, full_date, year, quarter, month, month_name, month_abbrev, 
                 day_of_year, week_of_year, is_month_start, is_month_end, fiscal_year, fiscal_quarter) 
                VALUES ({d_key}, '{d.date()}', {d.year}, {(d.month-1)//3+1}, {d.month}, 
                        '{d.strftime('%B')}', '{d.strftime('%b')}', 1, 1, 1, 1, {d.year}, 1)
            """))
        conn.commit()

    # 3. Mock Well Types
    with loader.engine.connect() as conn:
        conn.execute(text("INSERT OR REPLACE INTO dim_well_type (well_type_key, well_category, primary_product) VALUES (1, 'Shale/Tight Oil', 'Crude Oil')"))
        conn.commit()

    # 4. Mock Facts (Aligning keys)
    facts = []
    for d in dates:
        d_key = int(d.strftime('%Y%m%d'))
        for idx, (code, _, _, _, _) in enumerate(states):
            l_key = idx + 1 # SQLite autoincrement starts at 1
            base_prod = 5000000 if code == 'TX' else 1000000
            prod = base_prod + np.random.randint(-50000, 50000)
            rigs = np.random.randint(50, 500)
            facts.append({
                'date_key': d_key,
                'location_key': l_key,
                'well_type_key': 1,
                'crude_production_bbls': prod,
                'active_rig_count': rigs,
                'production_per_rig': prod / rigs,
                'efficiency_index': 100 + np.random.randint(-10, 10),
                'data_quality_score': 0.98,
                'is_anomaly': False
            })
    loader.upsert_facts(pd.DataFrame(facts))
    print(f"Injection complete. {len(facts)} facts loaded.")

if __name__ == "__main__":
    inject_mock()
