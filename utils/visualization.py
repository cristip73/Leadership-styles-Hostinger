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
        name='Management Style Profile',
        line=dict(width=2),  # Thicker line
        fillcolor='rgba(99, 110, 250, 0.5)'  # Semi-transparent fill
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(6, max_score)],  # Minimum range of 6 for better visibility
                dtick=1,  # Force integer steps
                showticklabels=True,
                tickmode='linear',
                ticks='outside',
                ticklen=8,
                gridcolor='rgba(0,0,0,0.1)'  # Lighter grid
            ),
            angularaxis=dict(
                tickmode='array',
                ticktext=categories,
                tickvals=[i * 90 for i in range(4)],  # Position labels at 90-degree intervals
                direction='clockwise',
                gridcolor='rgba(0,0,0,0.1)'  # Lighter grid
            ),
            gridshape='circular'
        ),
        showlegend=False,
        margin=dict(t=20, b=20, l=40, r=40)  # Tighter margins
    )
    
    return fig

def create_adequacy_gauge(score: int):
    colors = ['#FF4136', '#FF851B', '#2ECC40']  # Red, Orange, Green
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'font': {'size': 40}, 'suffix': ' pts'},
        gauge={
            'axis': {
                'range': [-24, 24],
                'tickmode': 'linear',
                'dtick': 4  # Show ticks every 4 points
            },
            'bar': {'color': "royalblue"},
            'steps': [
                {'range': [-24, 9], 'color': colors[0], 'thickness': 0.75},
                {'range': [10, 19], 'color': colors[1], 'thickness': 0.75},
                {'range': [20, 24], 'color': colors[2], 'thickness': 0.75}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(t=40, b=20, l=20, r=20)
    )
    
    return fig

def create_comparative_radar_chart(style_scores_list: list):
    fig = go.Figure()
    
    # Custom colors for better distinction
    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA']
    
    # Find max score across all users for consistent scaling
    max_score = 0
    for user_data in style_scores_list:
        max_score = max(max_score, max(user_data['scores'].values()))
    
    # Add trace for each user
    for idx, user_data in enumerate(style_scores_list):
        categories = list(user_data['scores'].keys())
        values = list(user_data['scores'].values())
        
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            name=user_data['name'],
            fill='toself',
            fillcolor=f'rgba{tuple(list(int(colors[idx % 4].lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}',
            line=dict(
                color=colors[idx % 4],
                width=2
            )
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(6, max_score)],  # Minimum range of 6
                dtick=1,  # Force integer steps
                showticklabels=True,
                tickmode='linear',
                ticks='outside',
                ticklen=8,
                gridcolor='rgba(0,0,0,0.1)'
            ),
            angularaxis=dict(
                tickmode='array',
                ticktext=categories,
                tickvals=[i * 90 for i in range(4)],
                direction='clockwise',
                gridcolor='rgba(0,0,0,0.1)'
            ),
            gridshape='circular'
        ),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=1.2,
            xanchor="left",
            x=0.7
        ),
        margin=dict(t=100, b=20, l=40, r=40)
    )
    
    return fig

def create_statistics_charts(results_df: pd.DataFrame):
    style_counts = results_df['primary_style'].value_counts()
    
    style_pie = go.Figure(data=[go.Pie(
        labels=style_counts.index,
        values=style_counts.values,
        hole=0.4,  # Donut chart
        marker=dict(colors=['#636EFA', '#EF553B', '#00CC96', '#AB63FA'])
    )])
    
    style_pie.update_layout(
        showlegend=True,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    
    adequacy_hist = go.Figure(data=[go.Histogram(
        x=results_df['adequacy_score'],
        nbinsx=12,  # Adjust number of bins
        marker_color='#636EFA'
    )])
    
    adequacy_hist.update_layout(
        title_text='Distribution of Adequacy Scores',
        xaxis_title_text='Score',
        yaxis_title_text='Count',
        bargap=0.1,
        margin=dict(t=40, b=40, l=40, r=40)
    )
    
    return style_pie, adequacy_hist
