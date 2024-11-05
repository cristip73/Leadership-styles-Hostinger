import streamlit as st
import pandas as pd
import io
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

def safe_convert_to_int(value):
    """Safely convert any value to integer, returning 0 for NaN/None values."""
    try:
        if pd.isna(value):
            return 0
        return int(float(value))
    except (ValueError, TypeError):
        return 0

def load_results_data():
    results = st.session_state.db.get_all_results()
    df = pd.DataFrame(results)
    
    # Convert style scores to integers, handling NaN values
    score_columns = ['directiv_score', 'persuasiv_score', 'participativ_score', 'delegativ_score', 'adequacy_score']
    for col in score_columns:
        if col in df.columns:
            df[col] = df[col].apply(safe_convert_to_int)
    return df

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
                f"{safe_convert_to_int(df['adequacy_score'].mean())}",
                df['primary_style'].mode()[0] if not df['primary_style'].empty else 'N/A'
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Add individual responses sheets
        for _, user in df.iterrows():
            responses = st.session_state.db.get_user_responses(user['id'])
            if responses:
                responses_df = pd.DataFrame(responses)
                sheet_name = f"Responses_{user['first_name']}"[:31]  # Excel limitation
                responses_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
    return output.getvalue()

def display_statistics(df):
    st.write("### Overall Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### Management Style Distribution")
        style_counts = df['primary_style'].value_counts()
        style_pie = go.Figure(data=[go.Pie(
            labels=style_counts.index,
            values=style_counts.values
        )])
        st.plotly_chart(style_pie)
    
    with col2:
        st.write("#### Adequacy Score Distribution")
        adequacy_box = go.Figure(data=[go.Box(
            y=df['adequacy_score'].apply(safe_convert_to_int)
        )])
        adequacy_box.update_layout(yaxis_title='Adequacy Score')
        st.plotly_chart(adequacy_box)
    
    st.write("### Summary Metrics")
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    
    with metrics_col1:
        st.metric("Total Assessments", len(df))
    with metrics_col2:
        st.metric("Average Adequacy Score", safe_convert_to_int(df['adequacy_score'].mean()))
    with metrics_col3:
        st.metric("Most Common Style", df['primary_style'].mode()[0] if not df['primary_style'].empty else 'N/A')

def display_individual_results(df):
    st.write("### Individual Results")
    
    if df.empty:
        st.info("No results available")
        return
        
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
        **Adequacy Score:** {safe_convert_to_int(user_data['adequacy_score'])}  
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
        
        # Add responses section
        st.write("#### Individual Responses")
        responses = st.session_state.db.get_user_responses(user_data['id'])
        if responses:
            responses_df = pd.DataFrame(responses)
            st.dataframe(responses_df[['question_id', 'answer']])
            
            # Export responses
            csv = responses_df.to_csv(index=False)
            st.download_button(
                "Download Individual Responses CSV",
                csv,
                f"responses_{user_data['first_name']}_{user_data['last_name']}.csv",
                "text/csv",
                key='responses-download'
            )

def display_comparative_analysis(df):
    st.write("### Comparative Analysis")
    
    if df.empty:
        st.info("No results available for comparison")
        return
        
    # Select users to compare
    selected_users = st.multiselect(
        "Select participants to compare (2-4 participants):",
        options=df.apply(lambda x: f"{x['first_name']} {x['last_name']} ({x['email']})", axis=1),
        max_selections=4
    )
    
    if len(selected_users) >= 2:
        # Get data for selected users
        selected_data = df[df.apply(lambda x: f"{x['first_name']} {x['last_name']} ({x['email']})" in selected_users, axis=1)]
        
        # Create comparison table
        comparison_data = []
        
        for _, user in selected_data.iterrows():
            comparison_data.append({
                'Name': f"{user['first_name']} {user['last_name']}",
                'Directiv': safe_convert_to_int(user['directiv_score']),
                'Persuasiv': safe_convert_to_int(user['persuasiv_score']),
                'Participativ': safe_convert_to_int(user['participativ_score']),
                'Delegativ': safe_convert_to_int(user['delegativ_score']),
                'Adequacy Score': safe_convert_to_int(user['adequacy_score']),
                'Adequacy Level': user['adequacy_level']
            })
        
        # Display the comparison table with integer formatting
        st.write("#### Management Style Scores")
        comparison_df = pd.DataFrame(comparison_data)
        
        # Format all numeric columns as integers
        numeric_cols = ['Directiv', 'Persuasiv', 'Participativ', 'Delegativ', 'Adequacy Score']
        
        # Display the table with custom formatting
        st.dataframe(
            comparison_df,
            column_config={
                col: st.column_config.NumberColumn(
                    col,
                    format="%d"
                ) for col in numeric_cols
            }
        )
        
        # Display adequacy score comparison
        st.write("#### Adequacy Score Comparison")
        fig = go.Figure()
        
        for _, user in selected_data.iterrows():
            adequacy_score = safe_convert_to_int(user['adequacy_score'])
            fig.add_trace(go.Bar(
                name=f"{user['first_name']} {user['last_name']}",
                x=['Adequacy Score'],
                y=[adequacy_score],
                text=[f"{adequacy_score} - {user['adequacy_level']}"],
                textposition='auto',
            ))
        
        fig.update_layout(
            barmode='group',
            yaxis=dict(
                dtick=1  # Force integer steps
            )
        )
        st.plotly_chart(fig)
        
        # Export comparison
        if st.button("Export Comparison"):
            csv = comparison_df.to_csv(index=False)
            st.download_button(
                "Download Comparison CSV",
                csv,
                "management_style_comparison.csv",
                "text/csv",
                key='comparison-download'
            )
    else:
        st.info("Please select at least 2 participants to compare")

def main():
    st.title("Supervisor Dashboard")
    
    # Add password check at the start
    check_supervisor_password()
    
    if st.session_state.db:
        try:
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
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.error("Database connection error")

if __name__ == "__main__":
    main()
