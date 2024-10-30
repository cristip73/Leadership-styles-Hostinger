import streamlit as st
from models.database import Database
from utils.scoring import AssessmentScorer
from assets.test_data import QUESTIONS
import uuid

if 'db' not in st.session_state:
    st.session_state.db = Database()

def init_session_state():
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

def registration_form():
    st.write("### Please enter your information to begin")
    with st.form("registration"):
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        
        if st.form_submit_button("Start Assessment"):
            if all([first_name, last_name, email]):
                try:
                    user_id = st.session_state.db.create_user(first_name, last_name, email)
                    st.session_state.user_id = user_id
                    return True
                except Exception as e:
                    if "duplicate key" in str(e):
                        st.error("This email is already registered. Please use a different email.")
                    else:
                        st.error("An error occurred during registration. Please try again.")
                    return False
            else:
                st.error("Please fill in all fields")
    return False

def display_question(question_data):
    st.write(f"### Question {question_data['id']}")
    st.write(question_data['scenario'])
    
    # Use session state for the radio button to persist selection
    if f"q_{question_data['id']}" not in st.session_state:
        st.session_state[f"q_{question_data['id']}"] = None
    
    answer = st.radio(
        "Choose your response:",
        options=["A", "B", "C", "D"],
        format_func=lambda x: question_data['options'][x],
        key=f"q_{question_data['id']}"
    )
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("Next Question" if st.session_state.current_question < 11 else "Submit"):
            # Save the response
            st.session_state.responses[question_data['id']] = answer
            st.session_state.db.save_response(
                st.session_state.user_id,
                question_data['id'],
                answer
            )
            
            if st.session_state.current_question < 11:
                st.session_state.current_question += 1
                st.rerun()  # Force rerun to show next question
            else:
                calculate_and_save_results()

def calculate_and_save_results():
    scorer = AssessmentScorer()
    primary_style, secondary_style = scorer.calculate_style_scores(st.session_state.responses)
    adequacy_score, adequacy_level = scorer.calculate_adequacy_score(st.session_state.responses)
    
    st.session_state.db.save_results(
        st.session_state.user_id,
        primary_style,
        secondary_style,
        adequacy_score,
        adequacy_level
    )
    
    # Set the completion state before redirecting
    st.session_state.assessment_complete = True
    
    # Use the newer query_params API for redirection
    st.query_params["user_id"] = str(st.session_state.user_id)
    st.switch_page("pages/02_view_results.py")

def main():
    st.title("Management Style Assessment")
    
    init_session_state()
    
    if not st.session_state.user_id:
        if registration_form():
            st.rerun()
    else:
        if 'assessment_complete' in st.session_state and st.session_state.assessment_complete:
            st.success("Assessment completed! View your results in the Results page.")
            if st.button("View Results"):
                st.query_params["user_id"] = str(st.session_state.user_id)
                st.switch_page("pages/02_view_results.py")
        else:
            display_question(QUESTIONS[st.session_state.current_question])
            
            progress = st.session_state.current_question / 11
            st.progress(progress)
            st.write(f"Question {st.session_state.current_question + 1} of 12")

if __name__ == "__main__":
    main()
