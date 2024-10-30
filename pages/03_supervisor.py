import streamlit as st
import pandas as pd
import io
from utils.visualization import create_statistics_charts, create_comparative_radar_chart
import plotly.graph_objects as go
from models.database import Database
from utils.scoring import AssessmentScorer

if 'db' not in st.session_state:
    st.session_state.db = Database()

def check_supervisor_password():
    if 'supervisor_authenticated' not in st.session_state:
        st.session_state.supervisor_authenticated = False
        
    if not st.session_state.supervisor_authenticated:
        with st.expander("Supervisor Authentication", expanded=True):
            password = st.text_input("Enter supervisor password:", type="password")
            if st.button("Login"):
                if password == "Potsolik11":
                    st.session_state.supervisor_authenticated = True
                    st.rerun()
                else:
                    st.error("Incorrect password")
            st.stop()

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
        st.plotly_chart(style_pie, use_container_width=True)
    
    with col2:
        st.write("#### Adequacy Score Distribution")
        adequacy_box = go.Figure(data=[go.Box(
            y=df['adequacy_score'],
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8,
            marker=dict(color='#636EFA'),
            line=dict(color='#636EFA')
        )])
        adequacy_box.update_layout(
            yaxis=dict(
                title='Adequacy Score',
                tickmode='linear',
                dtick=2  # Show even numbers
            )
        )
        st.plotly_chart(adequacy_box, use_container_width=True)
    
    # Summary metrics with improved styling
    st.write("### Summary Metrics")
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    
    with metrics_col1:
        st.metric(
            "Total Assessments",
            len(df),
            help="Total number of completed assessments"
        )
    with metrics_col2:
        st.metric(
            "Average Adequacy Score",
            f"{df['adequacy_score'].mean():.1f}",
            help="Mean adequacy score across all assessments"
        )
    with metrics_col3:
        st.metric(
            "Most Common Style",
            df['primary_style'].mode()[0],
            help="Most frequently occurring primary management style"
        )

def display_comparative_analysis(df):
    st.write("### Comparative Analysis")
    
    # Select users to compare
    selected_users = st.multiselect(
        "Select participants to compare (2-4 participants):",
        options=df.apply(lambda x: f"{x['first_name']} {x['last_name']} ({x['email']})", axis=1),
        max_selections=4,
        help="Choose between 2 and 4 participants to compare their management styles and adequacy scores"
    )
    
    if len(selected_users) >= 2:
        # Get data for selected users
        selected_data = df[df.apply(lambda x: f"{x['first_name']} {x['last_name']} ({x['email']})" in selected_users, axis=1)]
        
        # Create comparison visualizations
        st.write("#### Style Profile Comparison")
        
        # Get style scores for each user
        scorer = AssessmentScorer()
        style_scores_list = []
        for _, user in selected_data.iterrows():
            responses = st.session_state.db.get_user_responses(user['id'])
            user_scores = scorer.get_all_style_scores(responses)
            style_scores_list.append({
                'name': f"{user['first_name']} {user['last_name']}",
                'scores': user_scores
            })
        
        # Create and display comparative radar chart
        comp_radar = create_comparative_radar_chart(style_scores_list)
        st.plotly_chart(comp_radar, use_container_width=True)
        
        # Adequacy Score Comparison
        st.write("#### Adequacy Score Comparison")
        adequacy_fig = go.Figure()
        
        for _, user in selected_data.iterrows():
            adequacy_fig.add_trace(go.Bar(
                name=f"{user['first_name']} {user['last_name']}",
                x=['Adequacy Score'],
                y=[user['adequacy_score']],
                text=[f"{int(user['adequacy_score'])} pts<br>{user['adequacy_level']}"],
                textposition='auto',
                hovertemplate="Score: %{y}<br>Level: %{text}<extra></extra>"
            ))
        
        adequacy_fig.update_layout(
            barmode='group',
            yaxis=dict(
                title='Score',
                tickmode='linear',
                dtick=2,  # Show even numbers
                gridcolor='rgba(0,0,0,0.1)'
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        st.plotly_chart(adequacy_fig, use_container_width=True)
        
        # Detailed comparison table
        st.write("#### Detailed Comparison")
        
        # Create comparison DataFrame with style scores
        comparison_data = []
        for idx, user in selected_data.iterrows():
            user_data = {
                'Name': f"{user['first_name']} {user['last_name']}",
                'Primary Style': user['primary_style'],
                'Secondary Style': user['secondary_style'],
                'Adequacy Score': int(user['adequacy_score']),
                'Adequacy Level': user['adequacy_level']
            }
            # Add individual style scores
            responses = st.session_state.db.get_user_responses(user['id'])
            style_scores = scorer.get_all_style_scores(responses)
            for style, score in style_scores.items():
                user_data[f'{style} Score'] = score
            
            comparison_data.append(user_data)
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Style the dataframe
        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Name': st.column_config.TextColumn('Participant Name'),
                'Primary Style': st.column_config.TextColumn('Primary Style'),
                'Secondary Style': st.column_config.TextColumn('Secondary Style'),
                'Adequacy Score': st.column_config.NumberColumn('Adequacy Score', format='%d pts'),
                'Adequacy Level': st.column_config.TextColumn('Adequacy Level'),
                'Directiv Score': st.column_config.NumberColumn('Directiv Score', format='%d'),
                'Persuasiv Score': st.column_config.NumberColumn('Persuasiv Score', format='%d'),
                'Participativ Score': st.column_config.NumberColumn('Participativ Score', format='%d'),
                'Delegativ Score': st.column_config.NumberColumn('Delegativ Score', format='%d')
            }
        )
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            # Export comparison to Excel
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer) as writer:
                comparison_df.to_excel(writer, sheet_name='Comparison', index=False)
                
                # Add individual responses
                for _, user in selected_data.iterrows():
                    responses = st.session_state.db.get_user_responses(user['id'])
                    if responses:
                        responses_df = pd.DataFrame(responses)
                        sheet_name = f"Responses_{user['first_name']}"[:31]
                        responses_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            st.download_button(
                "Download Detailed Excel Report",
                excel_buffer.getvalue(),
                "management_style_comparison.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col2:
            # Export comparison to CSV
            csv = comparison_df.to_csv(index=False)
            st.download_button(
                "Download CSV Summary",
                csv,
                "management_style_comparison.csv",
                "text/csv"
            )
    else:
        st.info("Please select at least 2 participants to compare")

def main():
    st.title("Supervisor Dashboard")
    
    check_supervisor_password()
    
    if st.session_state.db:
        results_df = load_results_data()
        
        if len(results_df) > 0:
            # Export options in sidebar
            st.sidebar.write("### Export Options")
            
            excel_data = export_to_excel(results_df)
            st.sidebar.download_button(
                label="Download Full Report (Excel)",
                data=excel_data,
                file_name="management_assessment_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            csv_data = results_df.to_csv(index=False)
            st.sidebar.download_button(
                label="Download Raw Data (CSV)",
                data=csv_data,
                file_name="management_assessment_data.csv",
                mime="text/csv"
            )
            
            # Main content tabs
            tab1, tab2 = st.tabs(["Statistics", "Comparative Analysis"])
            
            with tab1:
                display_statistics(results_df)
            
            with tab2:
                display_comparative_analysis(results_df)
        else:
            st.info("No assessment results available yet")
    else:
        st.error("Database connection error")

if __name__ == "__main__":
    main()
