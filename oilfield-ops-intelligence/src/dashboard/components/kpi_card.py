import streamlit as st

def render_kpi_card(label: str, value: str, delta: str, context: str, icon: str):
    """
    Bold Enterprise KPI Card.
    """
    is_positive = "+" in delta
    delta_color = "#AAFFC7" if is_positive else "#FF6B6B"
    
    st.markdown(f"""
        <div class="enterprise-card">
            <div class="m-label">{label}</div>
            <div class="m-value">{value}</div>
            <div style="display: flex; align-items: center; gap: 10px; margin-top: 10px;">
                <span style="color: {delta_color}; font-weight: 800; font-size: 0.9rem;">{delta}</span>
                <span style="color: #67C090; font-size: 0.75rem; opacity: 0.8;">{context}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
