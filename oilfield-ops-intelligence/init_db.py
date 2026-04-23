import os
from sqlalchemy import create_engine
from src.warehouse.loader import DataWarehouseLoader

def init_native():
    """Initializes the warehouse schema for native environment."""
    print("Initializing Native Warehouse (SQLite)...")
    loader = DataWarehouseLoader()
    loader.initialize_schema()
    print("Warehouse ready.")

if __name__ == "__main__":
    init_native()
