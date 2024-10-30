import streamlit as st
from models.database import Database
import uuid

st.set_page_config(
    page_title="Management Style Assessment",
    page_icon="📊",
    layout="wide"
)

# Initialize database connection
if 'db' not in st.session_state:
    st.session_state.db = Database()

def main():
    st.title("Management Style Assessment")
    st.write("""
    Welcome to the Management Style and Adequacy Assessment tool. 
    This assessment will help you understand your management style and its effectiveness.
    """)

    st.markdown("""
    ### Instructions:
    1. The assessment consists of 12 scenario-based questions
    2. Each question has 4 possible responses
    3. Choose the response that best reflects how you would act in each situation
    4. Complete all questions to receive your results
    
    ### What you'll learn:
    - Your primary and secondary management styles
    - Your management adequacy score
    - Detailed interpretation of your results
    """)

    st.button("Start Assessment", type="primary", use_container_width=True)

if __name__ == "__main__":
    main()
