import streamlit as st

def render_kpi_card(label: str, value: str, delta: str, context: str, icon: str):
    """
    Minimalist, high-density HUD card.
    """
    is_positive = "+" in delta
    delta_color = "#00F2FF" if is_positive else "#FF3B30"
    
    st.markdown(f"""
        <div class="stealth-card">
            <div class="hud-label">{label}</div>
            <div class="hud-value">{value}</div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div class="hud-delta" style="color: {delta_color}">{delta} <span style="color: #48484A; font-size: 0.65rem;">{context}</span></div>
                <div style="font-size: 0.8rem; opacity: 0.5;">{icon}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
