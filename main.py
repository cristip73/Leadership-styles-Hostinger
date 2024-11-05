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
    
    # Introduction text in both languages
    st.write("""
    ### 
    Bine ați venit la instrumentul de Evaluare a Stilului și Adecvării Managementului. Această evaluare vă va ajuta să înțelegeți stilul dvs. de management și eficacitatea acestuia în patru dimensiuni cheie.
    """)

    # Management Styles Description
    st.markdown("""
    ### Stiluri de Management
    
    #### 1. Directive Style (Stil Directiv)
    - **English**: A task-oriented approach focusing on clear instructions, direct supervision, and structured control. Best suited for new team members or crisis situations.
    - **Română**: O abordare orientată spre sarcini, concentrată pe instrucțiuni clare, supraveghere directă și control structurat. Cel mai potrivit pentru membrii noi ai echipei sau situații de criză.
    
    #### 2. Persuasive Style (Stil Persuasiv)
    - **English**: A coaching approach that combines clear direction with explanation and persuasion. Effective for motivated teams that need guidance and support.
    - **Română**: O abordare de tip coaching care combină direcția clară cu explicația și persuasiunea. Eficient pentru echipe motivate care au nevoie de îndrumare și sprijin.
    
    #### 3. Participative Style (Stil Participativ)
    - **English**: A collaborative approach emphasizing shared decision-making and team involvement. Ideal for experienced teams with strong problem-solving skills.
    - **Română**: O abordare colaborativă care pune accent pe luarea deciziilor în comun și implicarea echipei. Ideal pentru echipe experimentate cu abilități puternice de rezolvare a problemelor.
    
    #### 4. Delegative Style (Stil Delegativ)
    - **English**: An autonomy-focused approach that empowers team members to make decisions and take responsibility. Best for highly skilled and self-motivated teams.
    - **Română**: O abordare concentrată pe autonomie care împuternicește membrii echipei să ia decizii și să-și asume responsabilități. Cel mai potrivit pentru echipe înalt calificate și auto-motivate.
    """)

    st.markdown("""
    ### Instructions | Instrucțiuni
    
    #### Assessment Structure | Structura Evaluării:
    1. 12 scenario-based questions | 12 întrebări bazate pe scenarii
    2. 4 possible responses per scenario | 4 răspunsuri posibile per scenariu
    3. Complete assessment time: ~15-20 minutes | Timp de completare: ~15-20 minute
    
    #### You Will Receive | Veți Primi:
    - Your primary and secondary management styles | Stilurile dvs. primare și secundare de management
    - Your management adequacy score | Scorul dvs. de adecvare managerială
    - Detailed interpretation of results | Interpretarea detaliată a rezultatelor
    - Development recommendations | Recomandări de dezvoltare
    """)

    if st.button("Start Assessment | Începeți Evaluarea", type="primary", use_container_width=True):
        st.switch_page("pages/01_take_assessment.py")

if __name__ == "__main__":
    main()
