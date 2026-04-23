import streamlit as st
import os
from sqlalchemy import create_engine
from src.analytics.queries import OilfieldAnalytics
from src.dashboard.pages.executive_overview import render_overview

# 1. App Configuration & CSS
st.set_page_config(page_title="⚡ OOID | OilField Intelligence", page_icon="🛢️", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Space+Mono:wght@700&display=swap');
        
        .stApp {
            background-color: #0A0E1A;
            color: #F0F4FF;
        }
        
        [data-testid="stSidebar"] {
            background-color: #141927;
            border-right: 1px solid #1E2D45;
        }
        
        h1, h2, h3 {
            color: #F0F4FF;
            font-family: 'Inter', sans-serif;
            font-weight: 700;
        }
        
        .stMetric {
            background-color: #141927;
            padding: 15px;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# 2. Database Connection
@st.cache_resource
def get_analytics_engine():
    user = os.getenv('POSTGRES_USER', 'postgres')
    pw = os.getenv('POSTGRES_PASSWORD', 'postgres_password')
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5432')
    db = os.getenv('POSTGRES_DB', 'ooid_db')
    
    conn_str = f"postgresql://{user}:{pw}@{host}:{port}/{db}"
    engine = create_engine(conn_str)
    return OilfieldAnalytics(engine)

analytics = get_analytics_engine()

# 3. Sidebar Navigation
with st.sidebar:
    st.title("⚡ OOID")
    st.markdown("---")
    page = st.radio("Navigation", ["Executive Overview", "State Drilldown", "Pipeline Monitor"])
    
    st.markdown("---")
    st.info("Data Refresh: Monthly\nLast Update: 2026-04-23")

# 4. Page Routing
if page == "Executive Overview":
    render_overview(analytics)
elif page == "State Drilldown":
    st.title("State Drilldown")
    st.info("Drilldown module implementation in progress...")
else:
    st.title("Pipeline Monitor")
    st.info("Monitor module implementation in progress...")
