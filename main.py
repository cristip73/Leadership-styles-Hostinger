import streamlit as st
from models.database import Database
import uuid

st.set_page_config(
    page_title="Evaluare Stil de Management",
    page_icon="📊",
    layout="wide"
)

# Initialize database connection
if 'db' not in st.session_state:
    st.session_state.db = Database()

def main():
    st.title("Evaluare Stil de Management")
    st.write("""
    Bine ați venit la instrumentul de evaluare a stilului de management și adecvării. 
    Această evaluare vă va ajuta să înțelegeți stilul dumneavoastră de management și eficacitatea acestuia.
    """)

    st.markdown("""
    ### Instrucțiuni:
    1. Evaluarea constă în 12 întrebări bazate pe scenarii
    2. Fiecare întrebare are 4 răspunsuri posibile
    3. Alegeți răspunsul care reflectă cel mai bine modul în care ați acționa în fiecare situație
    4. Completați toate întrebările pentru a primi rezultatele
    
    ### Ce veți afla:
    - Stilurile dumneavoastră primare și secundare de management
    - Scorul de adecvare al managementului
    - Interpretarea detaliată a rezultatelor
    """)

    if st.button("Începeți Evaluarea", type="primary", use_container_width=True):
        st.switch_page("pages/01_take_assessment.py")

if __name__ == "__main__":
    main()
