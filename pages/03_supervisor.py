import streamlit as st
import pandas as pd
from utils.visualization import create_statistics_charts
import plotly.express as px

if 'db' not in st.session_state:
    st.session_state.db = Database()

def load_results_data():
    results = st.session_state.db.get_all_results()
    return pd.DataFrame(results)

def display_statistics(df):
    st.write("### Statistici Generale")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### Distribuția Stilurilor de Management")
        style_pie, _ = create_statistics_charts(df)
        st.plotly_chart(style_pie)
    
    with col2:
        st.write("#### Distribuția Scorurilor de Adecvare")
        adequacy_box = px.box(df, y="adequacy_score", title="Distribuția Scorurilor")
        st.plotly_chart(adequacy_box)
    
    st.write("### Metrici Sumare")
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    
    with metrics_col1:
        st.metric("Total Evaluări", len(df))
    with metrics_col2:
        st.metric("Scor Mediu de Adecvare", f"{df['adequacy_score'].mean():.1f}")
    with metrics_col3:
        st.metric("Stil Predominant", df['primary_style'].mode()[0])

def display_individual_results(df):
    st.write("### Rezultate Individuale")
    
    selected_user = st.selectbox(
        "Selectați participantul:",
        options=df.apply(lambda x: f"{x['first_name']} {x['last_name']} ({x['email']})", axis=1)
    )
    
    if selected_user:
        user_data = df[df.apply(lambda x: f"{x['first_name']} {x['last_name']} ({x['email']})" == selected_user, axis=1)].iloc[0]
        
        st.write(f"""
        **Nume:** {user_data['first_name']} {user_data['last_name']}  
        **Email:** {user_data['email']}  
        **Stil Principal:** {user_data['primary_style']}  
        **Stil Secundar:** {user_data['secondary_style']}  
        **Scor de Adecvare:** {user_data['adequacy_score']}  
        **Nivel de Adecvare:** {user_data['adequacy_level']}  
        **Data Evaluării:** {user_data['created_at'].strftime('%Y-%m-%d %H:%M')}
        """)

def main():
    st.title("Tablou de Bord Supervizor")
    
    if st.session_state.db:
        results_df = load_results_data()
        
        if len(results_df) > 0:
            tab1, tab2 = st.tabs(["Statistici", "Rezultate Individuale"])
            
            with tab1:
                display_statistics(results_df)
            
            with tab2:
                display_individual_results(results_df)
        else:
            st.info("Nu există încă rezultate ale evaluării")
    else:
        st.error("Eroare de conexiune la baza de date")

if __name__ == "__main__":
    main()
