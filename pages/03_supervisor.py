import streamlit as st
import pandas as pd
from utils.visualization import create_statistics_charts
import plotly.express as px
from models.database import Database
from io import BytesIO
import datetime

if 'db' not in st.session_state:
    st.session_state.db = Database()

def load_results_data():
    results = st.session_state.db.get_all_results()
    return pd.DataFrame(results)

def export_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Main results sheet
        df_export = df[[
            'first_name', 'last_name', 'email', 
            'primary_style', 'secondary_style', 
            'adequacy_score', 'adequacy_level',
            'created_at'
        ]].copy()
        df_export.columns = [
            'First Name', 'Last Name', 'Email',
            'Primary Style', 'Secondary Style',
            'Adequacy Score', 'Adequacy Level',
            'Assessment Date'
        ]
        df_export.to_excel(writer, sheet_name='Assessment Results', index=False)
        
        # Style distribution sheet
        style_dist = df['primary_style'].value_counts().reset_index()
        style_dist.columns = ['Management Style', 'Count']
        style_dist.to_excel(writer, sheet_name='Style Distribution', index=False)
        
        # Adequacy statistics sheet
        adequacy_stats = pd.DataFrame({
            'Metric': ['Average Score', 'Median Score', 'Min Score', 'Max Score'],
            'Value': [
                df['adequacy_score'].mean(),
                df['adequacy_score'].median(),
                df['adequacy_score'].min(),
                df['adequacy_score'].max()
            ]
        })
        adequacy_stats.to_excel(writer, sheet_name='Adequacy Statistics', index=False)
    
    return output.getvalue()

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

    # Export section
    st.write("### Export Data")
    col1, col2 = st.columns(2)
    
    with col1:
        # Export to CSV
        csv_data = df[[
            'first_name', 'last_name', 'email',
            'primary_style', 'secondary_style',
            'adequacy_score', 'adequacy_level',
            'created_at'
        ]].to_csv(index=False)
        
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"management_assessment_results_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    
    with col2:
        # Export to Excel
        excel_data = export_to_excel(df)
        st.download_button(
            label="Download Excel Report",
            data=excel_data,
            file_name=f"management_assessment_report_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

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
        
        # Individual export option
        individual_df = pd.DataFrame([user_data])
        csv_data = individual_df[[
            'first_name', 'last_name', 'email',
            'primary_style', 'secondary_style',
            'adequacy_score', 'adequacy_level',
            'created_at'
        ]].to_csv(index=False)
        
        st.download_button(
            label="Export Individual Results",
            data=csv_data,
            file_name=f"individual_assessment_{user_data['first_name']}_{user_data['last_name']}_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

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
