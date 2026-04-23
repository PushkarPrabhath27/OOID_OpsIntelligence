import streamlit as st
import plotly.graph_objects as go
import pydeck as pdk
from src.dashboard.components.kpi_card import render_kpi_card

def render_overview(analytics):
    # 1. Page Header (Ultra Bold)
    st.markdown("""
        <div style="margin-bottom: 3rem;">
            <h1>Operational Intelligence</h1>
            <p style="color: #67C090; font-size: 1.1rem; font-weight: 600;">System Telemetry & Basin Production Mesh</p>
        </div>
    """, unsafe_allow_html=True)

    # 2. Key Metrics
    kpis = analytics.get_national_kpis()
    if kpis:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_kpi_card("System Production", f"{kpis['current_production']/1e6:.2f}M", f"{kpis['mom_change_pct']:+.1f}%", "Δ MoM", "🛢️")
        with c2:
            render_kpi_card("Basin Efficiency", f"{kpis['efficiency_index']:.1f}", "+0.4", "INDEX_UP", "⚡")
        with c3:
            render_kpi_card("Active Rigs", str(int(kpis['active_rigs'])), "±0", "STABLE", "🏗️")
        with c4:
            render_kpi_card("Anomaly Health", "NOMINAL", "0", "CLEAN", "🛡️")

    # 3. Geospatial Mesh (Fixed & Redesigned)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h3 style="margin-bottom: 20px;">Geospatial Production Mesh</h3>', unsafe_allow_html=True)
    
    comp_df = analytics.get_state_comparison()
    
    if not comp_df.empty:
        # Fixed Map using Scatterplot with radius based on production
        # Palette: #AAFFC7, #67C090, #215B63, #124170
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=comp_df,
            get_position=["longitude", "latitude"],
            get_radius="production",
            radius_scale=0.08,
            radius_min_pixels=5,
            radius_max_pixels=100,
            get_fill_color="[33, 91, 99, 180]", # #215B63 Teal
            get_line_color="[170, 255, 199]",   # #AAFFC7 Mint
            line_width_min_pixels=2,
            pickable=True,
            auto_highlight=True,
        )
        
        view_state = pdk.ViewState(latitude=37, longitude=-96, zoom=3.8, pitch=0)
        
        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/dark-v10",
            tooltip={"text": "{state_name}\nProduction: {production} BBL/day"}
        ))

    # 4. Momentum Analytics
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3>Production Momentum</h3>', unsafe_allow_html=True)
        trend_df = analytics.get_production_trend()
        if not trend_df.empty:
            fig = go.Figure()
            # Gradient Area with Mint/Emerald
            fig.add_trace(go.Scatter(
                x=trend_df['date'], y=trend_df['production'],
                fill='tozeroy',
                fillcolor='rgba(103, 192, 144, 0.1)', # #67C090 Emerald
                line=dict(color='#AAFFC7', width=3), # #AAFFC7 Mint
                name="System Vol"
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(showgrid=False, color='#67C090'),
                yaxis=dict(showgrid=True, gridcolor='#215B63', color='#67C090'),
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        st.markdown('<h3>Market Dominance</h3>', unsafe_allow_html=True)
        if not comp_df.empty:
            fig_bar = go.Figure(go.Bar(
                x=comp_df['state_code'], 
                y=comp_df['production'],
                marker=dict(
                    color='#67C090',
                    line=dict(color='#AAFFC7', width=1)
                )
            ))
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(showgrid=False, color='#67C090'),
                yaxis=dict(showgrid=True, gridcolor='#215B63', color='#67C090'),
                height=350
            )
            st.plotly_chart(fig_bar, use_container_width=True)
