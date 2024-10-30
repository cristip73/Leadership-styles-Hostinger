import plotly.graph_objects as go
import pandas as pd

def create_style_radar_chart(style_scores: dict):
    categories = list(style_scores.keys())
    values = list(style_scores.values())
    
    # Calculate maximum score achieved
    max_score = max(values)
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Management Style Profile'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_score],
                dtick=1  # Force integer steps
            )),
        showlegend=False
    )
    
    return fig

def create_adequacy_gauge(score: int):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [-24, 24]},
            'steps': [
                {'range': [-24, 9], 'color': "lightgray"},
                {'range': [10, 19], 'color': "lightblue"},
                {'range': [20, 24], 'color': "blue"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    return fig

def create_statistics_charts(results_df: pd.DataFrame):
    style_counts = results_df['primary_style'].value_counts()
    
    style_pie = go.Figure(data=[go.Pie(
        labels=style_counts.index,
        values=style_counts.values
    )])
    
    adequacy_hist = go.Figure(data=[go.Histogram(
        x=results_df['adequacy_score']
    )])
    
    adequacy_hist.update_layout(
        title_text='Distribution of Adequacy Scores',
        xaxis_title_text='Score',
        yaxis_title_text='Count'
    )
    
    return style_pie, adequacy_hist
