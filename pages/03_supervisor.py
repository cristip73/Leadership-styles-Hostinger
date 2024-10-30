import streamlit as st
import pandas as pd
from utils.visualization import create_statistics_charts
import plotly.express as px

if 'db' not in st.session_state:
    st.session_state.db = Database()

def load_results_data():
    results = st.session_state.db.get_all_results()
    return pd.DataFrame(results)

def display_statistics(df):
    st.write("### Overall Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### Management Style Distribution")
        style_pie, _ = create_statistics_charts(df)
        st.plotly_chart(style_pie)
    
    with col2:
        st.write("#### Adequacy Score Distribution")
        adequacy_box = px.box(df, y="adequacy_score")
        st.plotly_chart(adequacy_box)
    
    st.write("### Summary Metrics")
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    
    with metrics_col1:
        st.metric("Total Assessments", len(df))
    with metrics_col2:
        st.metric("Average Adequacy Score", f"{df['adequacy_score'].mean():.1f}")
    with metrics_col3:
        st.metric("Most Common Style", df['primary_style'].mode()[0])

def display_individual_results(df):
    st.write("### Individual Results")
    
    selected_user = st.selectbox(
        "Select participant:",
        options=df.apply(lambda x: f"{x['first_name']} {x['last_name']} ({x['email']})", axis=1)
    )
    
    if selected_user:
        user_data = df[df.apply(lambda x: f"{x['first_name']} {x['last_name']} ({x['email']})" == selected_user, axis=1)].iloc[0]
        
        st.write(f"""
        **Name:** {user_data['first_name']} {user_data['last_name']}  
        **Email:** {user_data['email']}  
        **Primary Style:** {user_data['primary_style']}  
        **Secondary Style:** {user_data['secondary_style']}  
        **Adequacy Score:** {user_data['adequacy_score']}  
        **Adequacy Level:** {user_data['adequacy_level']}  
        **Assessment Date:** {user_data['created_at'].strftime('%Y-%m-%d %H:%M')}
        """)

def main():
    st.title("Supervisor Dashboard")
    
    if st.session_state.db:
        results_df = load_results_data()
        
        if len(results_df) > 0:
            tab1, tab2 = st.tabs(["Statistics", "Individual Results"])
            
            with tab1:
                display_statistics(results_df)
            
            with tab2:
                display_individual_results(results_df)
        else:
            st.info("No assessment results available yet")
    else:
        st.error("Database connection error")

if __name__ == "__main__":
    main()
