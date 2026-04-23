import os
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

class EIAAPIError(Exception):
    """Custom exception for EIA API related errors."""
    pass

class EIAClient:
    """
    Client for interacting with the US Energy Information Administration (EIA) API v2.
    """
    
    BASE_URL = "https://api.eia.gov/v2"
    
    def __init__(self):
        self.api_key = os.getenv("EIA_API_KEY")
        if not self.api_key:
            logger.error("EIA_API_KEY not found in environment variables.")
            raise EIAAPIError("Missing EIA_API_KEY")
            
        self.session = requests.Session()
        
        # Configure retry logic: 3 retries, exponential backoff (1s, 2s, 4s)
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        logger.info("EIAClient initialized with retry logic.")

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handles the actual HTTP call with logging and error checking."""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        params['api_key'] = self.api_key
        
        try:
            logger.debug(f"Requesting EIA API: {url} with params: {params}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if 'error' in data:
                raise EIAAPIError(f"EIA API Error: {data['error']}")
                
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Request failed: {e}")
            raise EIAAPIError(f"Failed to connect to EIA API: {e}")

    def _fetch_paginated_data(self, endpoint: str, params: Dict[str, Any]) -> pd.DataFrame:
        """Helper to handle EIA's 5000-row pagination limit."""
        all_data = []
        offset = 0
        length = 5000
        
        while True:
            params['offset'] = offset
            params['length'] = length
            
            result = self._make_request(endpoint, params)
            data_page = result.get('response', {}).get('data', [])
            
            if not data_page:
                break
                
            all_data.extend(data_page)
            logger.info(f"Fetched {len(data_page)} records. Total: {len(all_data)}")
            
            if len(data_page) < length:
                break
                
            offset += length
            
        return pd.DataFrame(all_data)

    def get_crude_oil_production(self, start_date: str, end_date: str, frequency: str = "monthly") -> pd.DataFrame:
        """
        Fetches US crude oil production by state (barrels per day).
        Endpoint: /petroleum/sum/sndw/
        """
        logger.info(f"Fetching crude oil production from {start_date} to {end_date}")
        
        endpoint = "petroleum/sum/sndw/data/"
        params = {
            "frequency": frequency,
            "data": ["value"],
            "facets": {
                "series": ["MCRFPUS2"] # Standard crude production series
            },
            "start": start_date,
            "end": end_date,
            "sort": [{"column": "period", "direction": "desc"}]
        }
        
        df = self._fetch_paginated_data(endpoint, params)
        
        if not df.empty:
            # Rename columns to match requirements
            rename_map = {
                'period': 'date',
                'area-name': 'state_name',
                'value': 'production_bbls',
                'units': 'unit'
            }
            # Area codes might be useful for state_code normalization later
            df = df.rename(columns=rename_map)
            
        return df

    def get_natural_gas_production(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetches dry natural gas production by state (MCF)."""
        logger.info(f"Fetching natural gas production from {start_date} to {end_date}")
        
        endpoint = "natural-gas/prod/sum/data/"
        params = {
            "frequency": "monthly",
            "data": ["value"],
            "facets": {
                "series": ["N9070US2"] # Dry natural gas production
            },
            "start": start_date,
            "end": end_date
        }
        
        df = self._fetch_paginated_data(endpoint, params)
        if not df.empty:
            df = df.rename(columns={
                'period': 'date',
                'area-name': 'state_name',
                'value': 'gas_production_mcf',
                'units': 'unit'
            })
        return df

    def get_refinery_utilization(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetches weekly refinery utilization rates."""
        logger.info(f"Fetching refinery utilization from {start_date} to {end_date}")
        
        endpoint = "petroleum/refcap/sum/data/"
        params = {
            "frequency": "weekly",
            "data": ["value"],
            "facets": {
                "series": ["W_WPU_YCU_NUS_PCT"] # Weekly refinery utilization
            },
            "start": start_date,
            "end": end_date
        }
        
        df = self._fetch_paginated_data(endpoint, params)
        if not df.empty:
            df = df.rename(columns={
                'period': 'date',
                'value': 'utilization_pct',
                'area-name': 'region'
            })
        return df

    def save_raw_to_bronze(self, df: pd.DataFrame, dataset_name: str) -> str:
        """Saves the raw DataFrame as a timestamped JSON file in data/raw/{dataset_name}/."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_path = f"data/raw/{dataset_name}"
        os.makedirs(dir_path, exist_ok=True)
        
        file_path = f"{dir_path}/{dataset_name}_{timestamp}.json"
        meta_path = f"{dir_path}/{dataset_name}_{timestamp}.metadata.json"
        
        # Save data
        df.to_json(file_path, orient='records', date_format='iso')
        
        # Save metadata
        metadata = {
            "dataset_name": dataset_name,
            "source": "EIA API v2",
            "fetched_at": datetime.now().isoformat(),
            "record_count": len(df),
            "columns": list(df.columns)
        }
        
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=4)
            
        logger.info(f"Saved {len(df)} records to {file_path}")
        return file_path
