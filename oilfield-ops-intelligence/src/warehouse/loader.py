import os
import pandas as pd
from sqlalchemy import create_all, create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
from loguru import logger
from .models import Base, DimDate, DimLocation, FactProduction, PipelineRunLog

class DataWarehouseLoader:
    """
    Handles loading transformed DataFrames into the Star Schema warehouse.
    Supports high-performance bulk inserts and upserts.
    """

    def __init__(self, connection_string: str = None):
        if not connection_string:
            connection_string = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
        logger.info("DataWarehouseLoader initialized.")

    def initialize_schema(self, schema_file: str = "src/warehouse/schema.sql"):
        """Executes the DDL script to create tables and pre-populate dimensions."""
        with open(schema_file, 'r') as f:
            sql = f.read()
            
        with self.engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
        logger.info("Database schema initialized successfully.")

    def seed_dimensions(self):
        """Pre-populates dim_date and dim_location if empty."""
        session = self.Session()
        try:
            # Simple check for location seeding
            if session.query(DimLocation).count() == 0:
                logger.info("Seeding dim_location...")
                # Add sample seeding logic here or via SQL file
                pass
            session.commit()
        finally:
            session.close()

    def upsert_facts(self, df: pd.DataFrame):
        """
        Performs a PostgreSQL UPSERT for fact_production.
        Matches on (date_key, location_key, well_type_key).
        """
        if df.empty:
            return
            
        session = self.Session()
        try:
            records = df.to_dict(orient='records')
            
            for record in records:
                stmt = insert(FactProduction).values(**record)
                # Define update mapping for conflict
                update_dict = {c.name: stmt.excluded[c.name] for c in FactProduction.__table__.columns if not c.primary_key}
                
                upsert_stmt = stmt.on_conflict_do_update(
                    index_elements=['date_key', 'location_key', 'well_type_key'],
                    set_=update_dict
                )
                session.execute(upsert_stmt)
            
            session.commit()
            logger.info(f"Upserted {len(records)} records into fact_production.")
        except Exception as e:
            session.rollback()
            logger.error(f"Fact load failed: {e}")
            raise
        finally:
            session.close()

    def log_run(self, log_entry: dict):
        """Logs a pipeline execution run."""
        session = self.Session()
        try:
            run = PipelineRunLog(**log_entry)
            session.add(run)
            session.commit()
            return run.run_id
        finally:
            session.close()
