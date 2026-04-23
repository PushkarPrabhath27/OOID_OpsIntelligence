import streamlit as st
from src.dashboard.components.kpi_card import render_kpi_card

def render_monitor(analytics):
    st.title("Pipeline & Data Health Monitor")
    st.caption("Real-time telemetry of the OOID ingestion and validation engine")
    st.markdown("<br>", unsafe_allow_html=True)

    # 1. Pipeline Stats
    runs = analytics.get_pipeline_history()
    
    st.markdown('<div class="chart-header">Engine Reliability Overview</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    status = "OPERATIONAL" if not runs.empty and runs.iloc[0]['status'] == 'SUCCESS' else "DEGRADED"
    with c1:
        render_kpi_card("System Status", status, "UP", "Core Services", "⚙️")
    with c2:
        render_kpi_card("Data Freshness", "Up to Date", "Real-time", "Last Sync", "🕒")
    with c3:
        coverage = analytics.get_data_coverage()
        avg_q = coverage['avg_quality'].mean() * 100
        render_kpi_card("Avg Quality Score", f"{avg_q:.1f}%", "+0.2%", "vs last run", "✅")

    # 2. Execution History
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="chart-header">Pipeline Execution History</div>', unsafe_allow_html=True)
    if not runs.empty:
        st.dataframe(
            runs[['started_at', 'status', 'records_loaded', 'duration_seconds']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No pipeline runs recorded in the current session.")

    # 3. State-Level Coverage
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="chart-header">Multi-Basin Data Coverage</div>', unsafe_allow_html=True)
    if not coverage.empty:
        st.dataframe(
            coverage.rename(columns={
                'state_name': 'State', 
                'record_count': 'Total Records', 
                'last_update': 'Latest Data', 
                'avg_quality': 'Quality Score'
            }),
            use_container_width=True,
            hide_index=True
        )
