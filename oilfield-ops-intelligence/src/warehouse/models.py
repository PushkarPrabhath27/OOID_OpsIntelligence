from sqlalchemy import Column, Integer, String, Date, Numeric, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class DimDate(Base):
    __tablename__ = 'dim_date'
    date_key = Column(Integer, primary_key=True)
    full_date = Column(Date, nullable=False, unique=True)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    month_name = Column(String(10), nullable=False)
    month_abbrev = Column(String(3), nullable=False)
    day_of_year = Column(Integer, nullable=False)
    week_of_year = Column(Integer, nullable=False)
    is_month_start = Column(Boolean, nullable=False)
    is_month_end = Column(Boolean, nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    fiscal_quarter = Column(Integer, nullable=False)

class DimLocation(Base):
    __tablename__ = 'dim_location'
    location_key = Column(Integer, primary_key=True, autoincrement=True)
    state_code = Column(String(2), nullable=False, unique=True)
    state_name = Column(String(50), nullable=False)
    region = Column(String(50), nullable=False)
    country = Column(String(2), default='US')
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))

class DimWellType(Base):
    __tablename__ = 'dim_well_type'
    well_type_key = Column(Integer, primary_key=True, autoincrement=True)
    well_category = Column(String(30), nullable=False)
    primary_product = Column(String(20), nullable=False)
    formation_type = Column(String(50))

class FactProduction(Base):
    __tablename__ = 'fact_production'
    production_id = Column(Integer, primary_key=True, autoincrement=True)
    date_key = Column(Integer, ForeignKey('dim_date.date_key'))
    location_key = Column(Integer, ForeignKey('dim_location.location_key'))
    well_type_key = Column(Integer, ForeignKey('dim_well_type.well_type_key'))
    
    crude_production_bbls = Column(Numeric(15, 2))
    gas_production_mcf = Column(Numeric(15, 2))
    active_rig_count = Column(Integer)
    
    production_per_rig = Column(Numeric(10, 2))
    mom_growth_pct = Column(Numeric(8, 4))
    yoy_growth_pct = Column(Numeric(8, 4))
    rolling_3m_avg = Column(Numeric(15, 2))
    rolling_12m_avg = Column(Numeric(15, 2))
    efficiency_index = Column(Numeric(8, 2))
    
    data_quality_score = Column(Numeric(3, 2))
    data_quality_flags = Column(ARRAY(Text))
    is_anomaly = Column(Boolean, default=False)
    anomaly_severity = Column(String(10), default='NONE')
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class PipelineRunLog(Base):
    __tablename__ = 'pipeline_run_log'
    run_id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_name = Column(String(100), nullable=False)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    status = Column(String(20))
    records_extracted = Column(Integer)
    records_transformed = Column(Integer)
    records_loaded = Column(Integer)
    records_rejected = Column(Integer)
    error_message = Column(Text)
    duration_seconds = Column(Numeric(10, 2))
