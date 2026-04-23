import streamlit as st
from ..components.kpi_card import render_kpi_card
from ..components.charts import production_trend_chart, state_choropleth_map
import pandas as pd

def render_overview(analytics):
    st.header("Executive Operations Overview")
    
    # 1. KPI Cards Row
    kpis = analytics.get_national_kpis()
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        render_kpi_card("US Production", f"{kpis.get('current_production', 0)/1e6:.1f}M BBL", f"{kpis.get('mom_change_pct', 0):+.1f}%", "vs last month", "🛢️")
    with c2:
        render_kpi_card("Active Rigs", str(int(kpis.get('active_rigs', 0))), "+2", "vs last week", "🏗️")
    with c3:
        render_kpi_card("Efficiency Index", f"{kpis.get('efficiency_index', 0):.1f}", "+0.4", "national avg", "⚡")
    with c4:
        render_kpi_card("Anomalies (30d)", str(int(kpis.get('anomalies_30d', 0))), "-1", "critical issues", "⚠️")

    # 2. Production Trend
    st.subheader("US Production Trend (5-Year)")
    trend_df = analytics.get_production_trend()
    st.plotly_chart(production_trend_chart(trend_df), use_container_width=True)

    # 3. Geo Analysis
    col_map, col_table = st.columns([2, 1])
    
    with col_map:
        st.subheader("Regional Production Distribution")
        comp_df = analytics.get_state_comparison()
        st.plotly_chart(state_choropleth_map(comp_df), use_container_width=True)
        
    with col_table:
        st.subheader("Top Producing States")
        st.dataframe(
            comp_df[['rank', 'state_name', 'production']].head(10),
            column_config={
                "rank": st.column_config.NumberColumn("Rank"),
                "state_name": "State",
                "production": st.column_config.NumberColumn("BBL/day", format="%.2f")
            },
            hide_index=True,
            use_container_width=True
        )
