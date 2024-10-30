import streamlit as st
import pandas as pd
import io
from utils.visualization import create_statistics_charts
import plotly.express as px
from models.database import Database

if 'db' not in st.session_state:
    st.session_state.db = Database()

def load_results_data():
    results = st.session_state.db.get_all_results()
    return pd.DataFrame(results)

def export_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Export main results
        df.to_excel(writer, sheet_name='All Results', index=False)
        
        # Export style statistics
        style_stats = pd.DataFrame(df['primary_style'].value_counts()).reset_index()
        style_stats.columns = ['Style', 'Count']
        style_stats.to_excel(writer, sheet_name='Style Statistics', index=False)
        
        # Export adequacy statistics
        adequacy_stats = df['adequacy_level'].value_counts().reset_index()
        adequacy_stats.columns = ['Level', 'Count']
        adequacy_stats.to_excel(writer, sheet_name='Adequacy Statistics', index=False)
        
        # Add summary statistics
        summary_data = {
            'Metric': ['Total Assessments', 'Average Adequacy Score', 'Most Common Style'],
            'Value': [
                len(df),
                f"{df['adequacy_score'].mean():.1f}",
                df['primary_style'].mode()[0]
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
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
        
        # Export individual result
        if st.button("Export Individual Result"):
            individual_df = pd.DataFrame([user_data])
            csv = individual_df.to_csv(index=False)
            st.download_button(
                "Download Individual Result CSV",
                csv,
                f"result_{user_data['first_name']}_{user_data['last_name']}.csv",
                "text/csv",
                key='individual-download'
            )

def main():
    st.title("Supervisor Dashboard")
    
    if st.session_state.db:
        results_df = load_results_data()
        
        if len(results_df) > 0:
            # Export options
            st.sidebar.write("### Export Options")
            
            # Export all data
            excel_data = export_to_excel(results_df)
            st.sidebar.download_button(
                label="Download Full Report (Excel)",
                data=excel_data,
                file_name="management_assessment_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Export CSV
            csv_data = results_df.to_csv(index=False)
            st.sidebar.download_button(
                label="Download Raw Data (CSV)",
                data=csv_data,
                file_name="management_assessment_data.csv",
                mime="text/csv"
            )
            
            # Main content tabs
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
