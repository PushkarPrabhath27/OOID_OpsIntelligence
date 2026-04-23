from src.ingestion import EIAClient, BakerHughesFetcher
from loguru import logger
import os

def test_initialization():
    try:
        # Mocking environment for init test
        os.environ['EIA_API_KEY'] = 'test_key'
        eia = EIAClient()
        bh = BakerHughesFetcher()
        logger.success("Ingestion classes initialized successfully.")
    except Exception as e:
        logger.error(f"Initialization failed: {e}")

if __name__ == "__main__":
    test_initialization()
