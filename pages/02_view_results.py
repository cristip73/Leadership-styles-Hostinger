import streamlit as st
from utils.visualization import create_style_radar_chart, create_adequacy_gauge
import uuid

if 'db' not in st.session_state:
    st.session_state.db = Database()

def display_results(results):
    st.title("Your Assessment Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Management Style Profile")
        radar_chart = create_style_radar_chart(
            results['primary_style'],
            results['secondary_style']
        )
        st.plotly_chart(radar_chart)
        
        st.write(f"""
        **Primary Style:** {results['primary_style']}  
        **Secondary Style:** {results['secondary_style']}
        """)
    
    with col2:
        st.write("### Adequacy Score")
        gauge_chart = create_adequacy_gauge(results['adequacy_score'])
        st.plotly_chart(gauge_chart)
        
        st.write(f"""
        **Score:** {results['adequacy_score']}  
        **Level:** {results['adequacy_level']}
        """)
    
    st.write("### Interpretation")
    st.write("""
    Your results indicate your natural management style and how effectively you adapt
    to different situations. The primary style shows your default approach, while the
    secondary style represents your backup strategy.
    
    The adequacy score measures how well you choose appropriate responses based on
    the specific context of each situation.
    """)

def main():
    st.title("Assessment Results")
    
    user_id = st.experimental_get_query_params().get('user_id', [None])[0]
    
    if user_id:
        try:
            results = st.session_state.db.get_user_results(uuid.UUID(user_id))
            if results:
                display_results(results)
            else:
                st.error("Results not found")
        except ValueError:
            st.error("Invalid result URL")
    else:
        st.warning("Please complete the assessment to view your results")
        st.button("Take Assessment", type="primary")

if __name__ == "__main__":
    main()
