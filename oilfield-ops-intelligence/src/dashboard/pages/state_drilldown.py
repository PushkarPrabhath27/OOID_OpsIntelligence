import streamlit as st
import plotly.express as px
from src.dashboard.components.kpi_card import render_kpi_card

def render_drilldown(analytics):
    st.title("State Drilldown Analysis")
    st.caption("Deep-dive into regional operational performance and anomaly detection")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 1. State Selector
    comp_df = analytics.get_state_comparison()
    state_list = sorted(comp_df['state_code'].tolist())
    
    selected_state = st.selectbox(
        "Select State for Analysis", 
        state_list, 
        index=state_list.index('TX') if 'TX' in state_list else 0
    )
    
    data = analytics.get_state_drilldown(selected_state)
    
    if not data:
        st.warning(f"No detailed data available for {selected_state}.")
        return

    # 2. State KPIs
    st.markdown(f'<div class="chart-header">Real-Time Metrics: {selected_state}</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Current Production", f"{data['current_production']/1e3:.1f}k BBL", "+0.8%", "vs last period", "🛢️")
    with c2:
        render_kpi_card("Active Rigs", str(int(data['current_rigs'] or 0)), "0", "Operational", "🏗️")
    with c3:
        render_kpi_card("State Efficiency", f"{data['current_efficiency']:.1f}", "+0.2", "Basin Index", "⚡")
    with c4:
        rank_series = comp_df[comp_df['state_code'] == selected_state]['rank']
        rank = rank_series.iloc[0] if not rank_series.empty else 0
        render_kpi_card("National Rank", f"#{int(rank)}", "-1", "Sector Rank", "🏆")

    # 3. Charts
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-header">Historical Production Volume</div>', unsafe_allow_html=True)
        fig_prod = px.line(data['history'], x='date', y='crude_production_bbls', 
                          template="plotly_dark", color_discrete_sequence=['#3B82F6'])
        fig_prod.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_prod, use_container_width=True)
        
    with col2:
        st.markdown('<div class="chart-header">Rig Count Stability Trend</div>', unsafe_allow_html=True)
        fig_rigs = px.area(data['history'], x='date', y='active_rig_count', 
                          template="plotly_dark", color_discrete_sequence=['#10B981'])
        fig_rigs.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_rigs, use_container_width=True)

    # 4. Recent Anomalies
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="chart-header">Intelligence Alert Log (Anomalies)</div>', unsafe_allow_html=True)
    if not data['anomalies'].empty:
        st.dataframe(
            data['anomalies'][['date', 'anomaly_severity', 'crude_production_bbls']].rename(
                columns={'date': 'Date', 'anomaly_severity': 'Severity', 'crude_production_bbls': 'Value (BBL)'}
            ),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("Operational integrity verified. No anomalies detected in the last 12 months.")
