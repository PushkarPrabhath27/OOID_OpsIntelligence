import streamlit as st
import os
import sys
from sqlalchemy import create_engine, text
from datetime import datetime
from loguru import logger

# --- PATH FIX FOR NATIVE EXECUTION ---
# Hardcoded to your verified workspace to ensure zero mismatch
DB_PATH = r"c:\Users\pushk\OneDrive\Documents\OOID SBL1\oilfield-ops-intelligence\ooid_warehouse.db"
PROJECT_ROOT = r"c:\Users\pushk\OneDrive\Documents\OOID SBL1\oilfield-ops-intelligence"

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.analytics.queries import OilfieldAnalytics
from src.dashboard.pages.executive_overview import render_overview
from src.dashboard.pages.state_drilldown import render_drilldown
from src.dashboard.pages.pipeline_monitor import render_monitor

# --- 1. PREMIUM UI CONFIGURATION & CSS ---
st.set_page_config(
    page_title="OOID | Intelligence Dashboard", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load External CSS
css_path = os.path.join(PROJECT_ROOT, "src/dashboard/styles/main.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');
    </style>
""", unsafe_allow_html=True)

# --- 2. INTELLIGENT DB CONNECTION (Postgres/SQLite Fallback) ---
def get_analytics_engine():
    user = os.getenv('POSTGRES_USER')
    if user:
        pw = os.getenv('POSTGRES_PASSWORD', 'postgres_password')
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        db = os.getenv('POSTGRES_DB', 'ooid_db')
        conn_str = f"postgresql://{user}:{pw}@{host}:{port}/{db}"
    else:
        conn_str = f"sqlite:///{DB_PATH}"
        logger.info(f"Connecting to absolute SQLite path: {DB_PATH}")
    
    engine = create_engine(conn_str)
    return OilfieldAnalytics(engine), DB_PATH

# Force re-connection on every script run (Zero Cache)
analytics, active_db_path = get_analytics_engine()

# --- 3. CONSOLIDATED SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
        <div style="padding: 1.5rem 0; border-bottom: 2px solid #215B63; margin-bottom: 2.5rem;">
            <h2 style="margin: 0; font-family: 'Outfit', sans-serif; font-weight: 900; font-size: 1.8rem; color: #AAFFC7 !important;">OOID</h2>
            <p style="margin: 0; font-size: 0.75rem; color: #67C090; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;">Enterprise Intel Layer</p>
        </div>
    """, unsafe_allow_html=True)
    
    page = st.selectbox(
        "NAVIGATION_INDEX", 
        ["Executive Overview", "State Drilldown", "Pipeline Monitor"],
        label_visibility="collapsed"
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # --- LIVE DATA DIAGNOSTICS (FAANG DEBUG MODE) ---
    with st.expander("SYSTEM_INTEGRITY", expanded=False):
        st.write(f"**Target DB:** `{os.path.basename(active_db_path)}`")
        try:
            with analytics.engine.connect() as conn:
                f_count = conn.execute(text("SELECT COUNT(*) FROM fact_production")).scalar()
                l_count = conn.execute(text("SELECT COUNT(*) FROM dim_location")).scalar()
                d_count = conn.execute(text("SELECT COUNT(*) FROM dim_date")).scalar()
                
                # Check Join Intersection
                join_count = conn.execute(text("""
                    SELECT COUNT(*) FROM fact_production f 
                    JOIN dim_location l ON CAST(f.location_key AS INTEGER) = CAST(l.location_key AS INTEGER)
                """)).scalar()
                
                st.write(f"Facts: `{f_count}` | Locs: `{l_count}` | Dates: `{d_count}`")
                st.write(f"**Valid Joins:** `{join_count}`")
                
                if join_count > 0:
                    st.success("Relational Integrity: OK")
                else:
                    st.error("Relational Integrity: BROKEN (Keys Mismatch)")
        except Exception as e:
            st.error(f"DB Error: {e}")
            
        if st.button("🛠️ Emergency Data Rebuild"):
            try:
                from inject_mock_data import inject_mock
                inject_mock()
                st.rerun()
            except Exception as e:
                st.error(f"Rebuild Failed: {e}")
    
    st.info(f"📍 Region: North America\n📅 Cycle: {datetime.now().strftime('%B %Y')}")

# 4. Page Routing
if page == "Executive Overview":
    render_overview(analytics)
elif page == "State Drilldown":
    render_drilldown(analytics)
else:
    render_monitor(analytics)
