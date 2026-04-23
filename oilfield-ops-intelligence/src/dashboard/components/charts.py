import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def production_trend_chart(df: pd.DataFrame):
    """Line chart with dual-axis for production and 12m rolling average."""
    fig = go.Figure()
    
    # Primary Area Chart
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['production'],
        name='Monthly Production',
        fill='tozeroy',
        line=dict(color='#E8A100', width=2),
        fillcolor='rgba(232, 161, 0, 0.1)'
    ))
    
    # Rolling Average Line
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['rolling_12m_avg'],
        name='12M Rolling Avg',
        line=dict(color='#00C2A8', width=2, dash='dot')
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#F0F4FF'),
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, color='#8896B3'),
        yaxis=dict(showgrid=True, gridcolor='#1E2D45', color='#8896B3'),
        height=400
    )
    
    return fig

def state_choropleth_map(df: pd.DataFrame):
    """USA Choropleth map colored by production volume."""
    fig = px.choropleth(
        df,
        locations='state_code',
        locationmode="USA-states",
        color='production',
        scope="usa",
        color_continuous_scale=[[0, '#0A0E1A'], [1, '#E8A100']],
        labels={'production': 'BBL/day'}
    )
    
    fig.update_layout(
        geo=dict(
            bgcolor='rgba(0,0,0,0)',
            lakecolor='#0A0E1A',
            showlakes=True,
            landcolor='#141927'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#F0F4FF'),
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_showscale=False
    )
    
    return fig
