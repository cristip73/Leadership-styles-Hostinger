import streamlit as st
from utils.visualization import create_style_radar_chart, create_adequacy_gauge
from models.database import Database
from utils.scoring import AssessmentScorer
import uuid

if 'db' not in st.session_state:
    st.session_state.db = Database()

def display_style_interpretation(scorer, primary_style, secondary_style):
    st.write("### Analiza Stilului de Management")
    
    st.write("#### Stil Principal:", primary_style)
    st.write(scorer.get_style_description(primary_style))
    st.write("""
    Acesta este abordarea dominantă de management, reflectând tendințele dumneavoastră naturale în situații de leadership.
    Cel mai probabil veți utiliza acest stil când vă confruntați cu scenarii familiare sau când sunteți sub presiune.
    """)
    
    st.write("#### Stil Secundar:", secondary_style)
    st.write(scorer.get_style_description(secondary_style))
    st.write("""
    Aceasta este abordarea de rezervă în management, pe care o utilizați când stilul principal nu este eficient.
    Având un stil secundar puternic indică flexibilitate în abordarea managementului.
    """)

def display_adequacy_interpretation(scorer, score, level):
    st.write("### Analiza Adecvării")
    
    st.write(f"#### Scor Total: {score}")
    st.write(f"#### Nivel: {level}")
    st.write(scorer.get_adequacy_description(score))
    
    st.write("### Ce Înseamnă Acest Lucru")
    if score >= 20:
        st.write("""
        - Abilitate excelentă de adaptare a stilului de management la diferite situații
        - Înțelegere puternică a momentului potrivit pentru diferite abordări de leadership
        - Eficacitate ridicată în diverse scenarii de management
        """)
    elif score >= 10:
        st.write("""
        - Înțelegere bună a leadershipului situațional
        - Loc de îmbunătățire în identificarea celei mai eficiente abordări
        - Considerați dezvoltarea unei flexibilități mai mari în stilul de management
        """)
    else:
        st.write("""
        - Oportunitate de dezvoltare a abordărilor mai adaptabile de management
        - Concentrare pe recunoașterea diferitelor situații care necesită stiluri diferite
        - Considerați training de dezvoltare leadership sau mentorat
        """)

def display_development_recommendations(score):
    st.write("### Recomandări de Dezvoltare")
    
    if score >= 20:
        st.write("""
        1. Împărtășiți expertiza cu alții prin mentorat
        2. Asumați-vă provocări de leadership mai complexe
        3. Documentați abordările de succes pentru instruirea altora
        """)
    elif score >= 10:
        st.write("""
        1. Exersați identificarea indiciilor situaționale care sugerează abordări diferite de management
        2. Cereți feedback de la membrii echipei despre stilul dumneavoastră de management
        3. Experimentați cu diferite abordări de leadership în situații cu risc scăzut
        """)
    else:
        st.write("""
        1. Concentrați-vă pe dezvoltarea conștientizării diferitelor situații de management
        2. Studiați caracteristicile diferitelor stiluri de leadership
        3. Lucrați cu un mentor pentru a vă îmbunătăți conștientizarea situațională
        4. Practicați adaptarea stilului în situații controlate
        """)

def display_results(results):
    st.title("Rezultatele Evaluării")
    
    scorer = AssessmentScorer()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Profilul Stilului de Management")
        radar_chart = create_style_radar_chart(
            results['primary_style'],
            results['secondary_style']
        )
        st.plotly_chart(radar_chart, use_container_width=True)
    
    with col2:
        st.write("### Scorul de Adecvare")
        gauge_chart = create_adequacy_gauge(results['adequacy_score'])
        st.plotly_chart(gauge_chart, use_container_width=True)
    
    display_style_interpretation(scorer, results['primary_style'], results['secondary_style'])
    display_adequacy_interpretation(scorer, results['adequacy_score'], results['adequacy_level'])
    display_development_recommendations(results['adequacy_score'])
    
    st.download_button(
        label="Descarcă Rezultatele PDF",
        data=f"""Rezultatele Evaluării Stilului de Management

Nume: {results['first_name']} {results['last_name']}
Email: {results['email']}
Data: {results['created_at'].strftime('%Y-%m-%d %H:%M')}

Stil Principal: {results['primary_style']}
Stil Secundar: {results['secondary_style']}
Scor de Adecvare: {results['adequacy_score']}
Nivel de Adecvare: {results['adequacy_level']}

Acest raport a fost generat de instrumentul de Evaluare a Stilului de Management.
        """,
        file_name="rezultate_stil_management.txt",
        mime="text/plain"
    )

def main():
    st.title("Rezultatele Evaluării")
    
    user_id = st.experimental_get_query_params().get('user_id', [None])[0]
    
    if user_id:
        try:
            results = st.session_state.db.get_user_results(uuid.UUID(user_id))
            if results:
                display_results(results)
            else:
                st.error("Rezultate negăsite. Vă rugăm să completați mai întâi evaluarea.")
        except ValueError:
            st.error("URL invalid. Vă rugăm să utilizați link-ul primit după completarea evaluării.")
    else:
        st.warning("Vă rugăm să completați evaluarea pentru a vedea rezultatele")
        if st.button("Începeți Evaluarea", type="primary"):
            st.switch_page("pages/01_take_assessment.py")

if __name__ == "__main__":
    main()
