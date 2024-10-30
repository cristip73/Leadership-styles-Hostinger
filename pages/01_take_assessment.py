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
                user_id = st.session_state.db.create_user(first_name, last_name, email)
                st.session_state.user_id = user_id
                return True
            else:
                st.error("Please fill in all fields")
    return False

def display_question(question_data):
    st.write(f"### Question {question_data['id']}")
    st.write(question_data['scenario'])
    
    def on_answer_change():
        if 'last_answer' in st.session_state:
            answer = st.session_state.last_answer
            st.session_state.responses[question_data['id']] = answer
            st.session_state.db.save_response(
                st.session_state.user_id,
                question_data['id'],
                answer
            )
            
            if st.session_state.current_question < 11:
                st.session_state.current_question += 1
                st.rerun()
            else:
                calculate_and_save_results()
                st.rerun()
    
    st.radio(
        "Choose your response:",
        options=["A", "B", "C", "D"],
        format_func=lambda x: question_data['options'][x],
        key="last_answer",
        on_change=on_answer_change
    )
    
    st.progress(st.session_state.current_question / 11)
    st.write(f"Question {st.session_state.current_question + 1} of 12")

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
    
    st.session_state.assessment_complete = True

def main():
    st.title("Management Style Assessment")
    
    init_session_state()
    
    if not st.session_state.user_id:
        if registration_form():
            st.rerun()
    else:
        if 'assessment_complete' in st.session_state and st.session_state.assessment_complete:
            st.success("Assessment completed! View your results in the Results page.")
        else:
            display_question(QUESTIONS[st.session_state.current_question])
            
            progress = st.session_state.current_question / 11
            st.progress(progress)
            st.write(f"Question {st.session_state.current_question + 1} of 12")

if __name__ == "__main__":
    main()
