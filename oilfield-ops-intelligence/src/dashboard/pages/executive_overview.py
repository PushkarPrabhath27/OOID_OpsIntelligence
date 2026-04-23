import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
from src.dashboard.components.kpi_card import render_kpi_card

def render_overview(analytics):
    # 1. Page Header
    st.title("Executive Operations Overview")
    st.caption("Strategic Intelligence for Multi-Basin Production & Efficiency")
    st.markdown("<br>", unsafe_allow_html=True)

    # 2. National KPIs
    kpis = analytics.get_national_kpis()
    if kpis:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_kpi_card("Daily Production", f"{kpis['current_production']/1e6:.2f}M BBL", f"{kpis['mom_change_pct']:+.1f}%", "MoM Growth", "🛢️")
        with c2:
            render_kpi_card("Active Rig Count", str(int(kpis['active_rigs'])), "0", "Basin Neutral", "🏗️")
        with c3:
            render_kpi_card("Efficiency Index", f"{kpis['efficiency_index']:.1f}", "+0.4", "Operational Gain", "⚡")
        with c4:
            render_kpi_card("Detected Anomalies", str(kpis['anomalies_30d']), "-2", "vs prior cycle", "⚠️")

    # 3. Geo-Spatial 3D Analysis & Trend
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.5, 1])
    
    comp_df = analytics.get_state_comparison()
    
    with col1:
        st.markdown('<div class="chart-header">3D Regional Production Volume</div>', unsafe_allow_html=True)
        if not comp_df.empty:
            # Pydeck 3D Column Map
            view_state = pdk.ViewState(latitude=38, longitude=-98, zoom=3.5, pitch=45)
            
            layer = pdk.Layer(
                "ColumnLayer",
                data=comp_df,
                get_position=["longitude", "latitude"],
                get_elevation="production",
                elevation_scale=0.05,
                radius=100000,
                get_fill_color=["255 * (production / 5000000)", "150 * (1 - production / 5000000)", 255, 180],
                pickable=True,
                auto_highlight=True,
            )
            
            st.pydeck_chart(pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip={"text": "{state_name}: {production} BBL/day"},
                map_style="mapbox://styles/mapbox/dark-v10"
            ))
    
    with col2:
        st.markdown('<div class="chart-header">Market Share by Region</div>', unsafe_allow_html=True)
        if not comp_df.empty:
            fig_pie = px.pie(comp_df, values='production', names='state_code', hole=.6,
                            color_discrete_sequence=px.colors.sequential.Blues_r)
            fig_pie.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                legend=dict(font=dict(color="#94A3B8"))
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # 4. Deep Analytical Row
    st.markdown("<br>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="chart-header">Efficiency-Production Correlation</div>', unsafe_allow_html=True)
        if not comp_df.empty:
            fig_scatter = px.scatter(comp_df, x="production", y="efficiency_index", 
                                    size="production", color="state_code",
                                    hover_name="state_name", log_x=True, size_max=60,
                                    template="plotly_dark")
            fig_scatter.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
    with col4:
        st.markdown('<div class="chart-header">Production Trends (Rolling 12M Avg)</div>', unsafe_allow_html=True)
        trend_df = analytics.get_production_trend()
        if not trend_df.empty:
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=trend_df['date'], y=trend_df['production'], 
                                        name='Production', line=dict(color='#3B82F6', width=3)))
            fig_trend.add_trace(go.Scatter(x=trend_df['date'], y=trend_df['rolling_12m_avg'], 
                                        name='12M Rolling Avg', line=dict(color='#F59E0B', width=2, dash='dot')))
            fig_trend.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig_trend, use_container_width=True)
