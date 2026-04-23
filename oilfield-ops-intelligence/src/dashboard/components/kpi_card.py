import streamlit as st

def render_kpi_card(title: str, value: str, delta: str, delta_label: str, icon: str):
    """
    Renders a premium, dark-themed KPI card using custom HTML/CSS.
    """
    delta_color = "#00E676" if "+" in delta else "#FF4B4B"
    
    st.markdown(f"""
        <div style="
            background-color: #141927;
            padding: 20px;
            border-radius: 10px;
            border-top: 3px solid #E8A100;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 24px; margin-right: 10px;">{icon}</span>
                <span style="color: #8896B3; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">{title}</span>
            </div>
            <div style="color: #F0F4FF; font-size: 28px; font-weight: 700; margin-bottom: 5px; font-family: 'Space Mono', monospace;">
                {value}
            </div>
            <div style="display: flex; align-items: center;">
                <span style="color: {delta_color}; font-weight: 700; font-size: 14px; margin-right: 8px;">{delta}</span>
                <span style="color: #8896B3; font-size: 12px;">{delta_label}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
