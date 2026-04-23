import streamlit as st
import plotly.graph_objects as go
from src.dashboard.components.kpi_card import render_kpi_card

def render_drilldown(analytics):
    st.markdown("""
        <div style="margin-bottom: 2rem;">
            <h1>State Analytics</h1>
            <p style="color: #67C090; font-size: 1.1rem; font-weight: 600;">Granular Telemetry & Basin Specific Integrity</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 1. State Selector
    comp_df = analytics.get_state_comparison()
    state_list = sorted(comp_df['state_code'].tolist())
    
    selected_state = st.selectbox(
        "BASIN_TARGET_SELECT", 
        state_list, 
        index=state_list.index('TX') if 'TX' in state_list else 0
    )
    
    data = analytics.get_state_drilldown(selected_state)
    
    if not data:
        st.warning(f"No detailed data available for {selected_state}.")
        return

    # 2. State KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Basin Volume", f"{data['current_production']/1e3:.1f}k", "+0.8%", "LOC_NOMINAL", "🛢️")
    with c2:
        render_kpi_card("Active Rigs", str(int(data['current_rigs'] or 0)), "0", "STABLE", "🏗️")
    with c3:
        render_kpi_card("Efficiency", f"{data['current_efficiency']:.1f}", "+0.2", "INDEX_UP", "⚡")
    with c4:
        rank_series = comp_df[comp_df['state_code'] == selected_state]['rank']
        rank = rank_series.iloc[0] if not rank_series.empty else 0
        render_kpi_card("Sector Rank", f"#{int(rank)}", "-1", "TOP_QUARTILE", "🏆")

    # 3. Telemetry Trends
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3>Production Telemetry</h3>', unsafe_allow_html=True)
        fig_prod = go.Figure()
        fig_prod.add_trace(go.Scatter(
            x=data['history']['date'], y=data['history']['crude_production_bbls'],
            line=dict(color='#AAFFC7', width=3),
            fill='tozeroy', fillcolor='rgba(103, 192, 144, 0.1)'
        ))
        fig_prod.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=10, b=0), height=350,
            xaxis=dict(showgrid=False, color='#67C090'),
            yaxis=dict(showgrid=True, gridcolor='#215B63', color='#67C090')
        )
        st.plotly_chart(fig_prod, use_container_width=True)
        
    with col2:
        st.markdown('<h3>Deployment Stability</h3>', unsafe_allow_html=True)
        fig_rigs = go.Figure()
        fig_rigs.add_trace(go.Scatter(
            x=data['history']['date'], y=data['history']['active_rig_count'],
            line=dict(color='#67C090', width=2),
            fill='tozeroy', fillcolor='rgba(33, 91, 99, 0.2)'
        ))
        fig_rigs.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=10, b=0), height=350,
            xaxis=dict(showgrid=False, color='#67C090'),
            yaxis=dict(showgrid=True, gridcolor='#215B63', color='#67C090')
        )
        st.plotly_chart(fig_rigs, use_container_width=True)

    # 4. Integrity Log
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<h3>Integrity Alert Log</h3>', unsafe_allow_html=True)
    if not data['anomalies'].empty:
        st.dataframe(
            data['anomalies'][['date', 'anomaly_severity', 'crude_production_bbls']],
            use_container_width=True, hide_index=True
        )
    else:
        st.success("System scan complete. No basin-level anomalies detected.")
