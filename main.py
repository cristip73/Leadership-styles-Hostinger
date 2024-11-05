import streamlit as st
from models.database import Database
import uuid

st.set_page_config(
    page_title="Management Style Assessment | Evaluarea Stilului de Management",
    page_icon="📊",
    layout="wide"
)

# Initialize database connection
if 'db' not in st.session_state:
    st.session_state.db = Database()

def main():
    st.title("Management Style Assessment | Evaluarea Stilului de Management")
    
    # Language selector
    lang = st.selectbox(
        "Select Language | Selectați Limba",
        ["English", "Română"]
    )
    
    if lang == "English":
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

        if st.button("Start Assessment", type="primary", use_container_width=True):
            st.switch_page("pages/01_take_assessment.py")
    else:
        st.write("""
        Bine ați venit la instrumentul de Evaluare a Stilului de Management și Adecvare.
        Această evaluare vă va ajuta să înțelegeți stilul dvs. de management și eficacitatea acestuia.
        """)

        st.markdown("""
        ### Instrucțiuni:
        1. Evaluarea constă în 12 întrebări bazate pe scenarii
        2. Fiecare întrebare are 4 răspunsuri posibile
        3. Alegeți răspunsul care reflectă cel mai bine modul în care ați acționa în fiecare situație
        4. Completați toate întrebările pentru a primi rezultatele
        
        ### Ce veți învăța:
        - Stilurile dvs. primare și secundare de management
        - Scorul dvs. de adecvare în management
        - Interpretarea detaliată a rezultatelor dvs.
        """)

        if st.button("Începeți Evaluarea", type="primary", use_container_width=True):
            st.switch_page("pages/01_take_assessment.py")

if __name__ == "__main__":
    main()
