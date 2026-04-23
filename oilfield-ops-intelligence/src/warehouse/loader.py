import os
import pandas as pd
from sqlalchemy import create_engine, text
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
            user = os.getenv('POSTGRES_USER')
            if user:
                connection_string = f"postgresql://{user}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
            else:
                connection_string = "sqlite:///ooid_warehouse.db"
                logger.warning("No Postgres credentials found. Falling back to local SQLite: ooid_warehouse.db")
        
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"DataWarehouseLoader initialized with: {connection_string}")

    def initialize_schema(self, schema_file: str = "src/warehouse/schema.sql"):
        """Executes the DDL script to create tables. Handles SQLite multi-statement limitation."""
        with open(schema_file, 'r') as f:
            sql = f.read()
            
        with self.engine.connect() as conn:
            if 'sqlite' in str(self.engine.url):
                # SQLite needs individual statements or executescript
                statements = sql.split(';')
                for statement in statements:
                    if statement.strip():
                        conn.execute(text(statement))
            else:
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
        Performs an UPSERT for fact_production.
        Handles both PostgreSQL and SQLite logic.
        """
        if df.empty:
            return
            
        session = self.Session()
        try:
            records = df.to_dict(orient='records')
            
            # Convert list of flags to comma-separated string for SQLite/Storage
            for r in records:
                if isinstance(r.get('data_quality_flags'), list):
                    r['data_quality_flags'] = ",".join(r['data_quality_flags'])

            if 'postgresql' in str(self.engine.url):
                for record in records:
                    stmt = insert(FactProduction).values(**record)
                    update_dict = {c.name: stmt.excluded[c.name] for c in FactProduction.__table__.columns if not c.primary_key}
                    upsert_stmt = stmt.on_conflict_do_update(
                        index_elements=['date_key', 'location_key', 'well_type_key'],
                        set_=update_dict
                    )
                    session.execute(upsert_stmt)
            else:
                # Basic SQLite Logic (Delete then Insert for idempotency)
                for record in records:
                    session.query(FactProduction).filter_by(
                        date_key=record['date_key'], 
                        location_key=record['location_key'], 
                        well_type_key=record['well_type_key']
                    ).delete()
                    session.add(FactProduction(**record))
            
            session.commit()
            logger.info(f"Loaded {len(records)} records into fact_production.")
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
