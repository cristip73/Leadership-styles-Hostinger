import streamlit as st
import pandas as pd
import io
from utils.visualization import create_statistics_charts, create_style_radar_chart, create_adequacy_gauge, create_comparative_radar_chart
import plotly.express as px
import plotly.graph_objects as go
from models.database import Database
from utils.scoring import AssessmentScorer
from utils.auth import require_auth, verify_password, hash_password
import os

if 'db' not in st.session_state:
    st.session_state.db = Database()

# Initialize supervisor password if not set
if 'SUPERVISOR_PASSWORD_HASH' not in st.session_state:
    default_password = "admin123"  # Default password for testing
    st.session_state.SUPERVISOR_PASSWORD_HASH = hash_password(default_password)

def load_results_data():
    results = st.session_state.db.get_all_results()
    return pd.DataFrame(results)

def login_form():
    st.title("Supervisor Login")
    with st.form("login_form"):
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if verify_password(password, st.session_state.SUPERVISOR_PASSWORD_HASH):
                st.session_state.is_authenticated = True
                st.experimental_rerun()
            else:
                st.error("Invalid password")

def logout():
    if st.sidebar.button("Logout"):
        st.session_state.is_authenticated = False
        st.experimental_rerun()

[... rest of the existing functions ...]

def main():
    # Check authentication
    if not st.session_state.get('is_authenticated', False):
        login_form()
        return
    
    # Add logout button
    logout()
    
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
            tab1, tab2, tab3 = st.tabs(["Statistics", "Individual Results", "Comparative Analysis"])
            
            with tab1:
                display_statistics(results_df)
            
            with tab2:
                display_individual_results(results_df)
                
            with tab3:
                display_comparative_analysis(results_df)
        else:
            st.info("No assessment results available yet")
    else:
        st.error("Database connection error")

if __name__ == "__main__":
    main()
