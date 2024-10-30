import streamlit as st
import pandas as pd
from utils.visualization import create_statistics_charts
import plotly.express as px
from models.database import Database
from io import BytesIO
from datetime import datetime

if 'db' not in st.session_state:
    st.session_state.db = Database()

def load_results_data():
    results = st.session_state.db.get_all_results()
    return pd.DataFrame(results)

def export_to_excel(df):
    output = BytesIO()
    
    # Create Excel writer
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Summary sheet
        summary_data = {
            'Metric': [
                'Total Evaluări',
                'Scor Mediu de Adecvare',
                'Stil Predominant',
                'Data Raport'
            ],
            'Valoare': [
                len(df),
                f"{df['adequacy_score'].mean():.1f}",
                df['primary_style'].mode()[0],
                datetime.now().strftime('%Y-%m-%d %H:%M')
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Sumar', index=False)
        
        # Individual results sheet
        results_df = df[[
            'first_name', 'last_name', 'email', 
            'primary_style', 'secondary_style',
            'adequacy_score', 'adequacy_level',
            'created_at'
        ]].copy()
        
        # Rename columns for better readability
        results_df.columns = [
            'Prenume', 'Nume', 'Email',
            'Stil Principal', 'Stil Secundar',
            'Scor Adecvare', 'Nivel Adecvare',
            'Data Evaluării'
        ]
        
        results_df.to_excel(writer, sheet_name='Rezultate Individuale', index=False)
        
        # Style distribution sheet
        style_dist = pd.DataFrame(df['primary_style'].value_counts()).reset_index()
        style_dist.columns = ['Stil de Management', 'Număr de Persoane']
        style_dist.to_excel(writer, sheet_name='Distribuție Stiluri', index=False)
        
        # Adequacy scores distribution
        adequacy_dist = df['adequacy_level'].value_counts().reset_index()
        adequacy_dist.columns = ['Nivel Adecvare', 'Număr de Persoane']
        adequacy_dist.to_excel(writer, sheet_name='Distribuție Adecvare', index=False)
    
    return output.getvalue()

def display_statistics(df):
    st.write("### Statistici Generale")
    
    # Export button at the top
    if st.download_button(
        label="📊 Exportă Raport Excel",
        data=export_to_excel(df),
        file_name=f"raport_management_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ):
        st.success("Raportul a fost descărcat cu succes!")
    
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
        
        # Individual export button
        user_df = pd.DataFrame([user_data]).copy()
        if st.download_button(
            label="📄 Exportă Rezultat Individual",
            data=export_to_excel(user_df),
            file_name=f"rezultat_{user_data['first_name']}_{user_data['last_name']}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            st.success("Rezultatul individual a fost descărcat cu succes!")

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
