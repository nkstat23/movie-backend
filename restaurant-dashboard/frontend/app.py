import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="NYC Resto Dashboard", layout="wide", page_icon="🍔")

API_URL = "http://127.0.0.1:8000/api"

# --- Fonctions utilitaires pour appeler l'API ---
@st.cache_data(ttl=60) # Cache les données pour 60 secondes pour la perf
def fetch_global_stats():
    try:
        response = requests.get(f"{API_URL}/stats/global")
        return response.json()
    except:
        return None

def fetch_borough_stats():
    response = requests.get(f"{API_URL}/stats/boroughs")
    return pd.DataFrame(response.json())

def fetch_cuisine_stats():
    response = requests.get(f"{API_URL}/stats/cuisines")
    return pd.DataFrame(response.json())

def fetch_restaurants(borough_filter):
    response = requests.get(f"{API_URL}/restaurants", params={"borough": borough_filter, "limit": 50})
    return pd.DataFrame(response.json())

# --- Interface Utilisateur ---

st.title("🍔 Dashboard Restaurants New York")
st.markdown("Analyse des données via **FastAPI** et **MongoDB**")

# Sidebar
st.sidebar.header("Filtres")
borough_options = ["Tous", "Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
selected_borough = st.sidebar.selectbox("Choisir un Arrondissement", borough_options)

# 1. Section KPI (Indicateurs clés)
stats = fetch_global_stats()
if stats:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Restaurants", stats['total_restaurants'])
    col2.metric("Types de Cuisine", stats['total_cuisines'])
    col3.metric("Arrondissements", stats['total_boroughs'])
else:
    st.error("Impossible de connecter à l'API Backend. Vérifiez que FastAPI tourne.")

st.divider()

# 2. Section Graphiques
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Répartition par Arrondissement")
    df_borough = fetch_borough_stats()
    if not df_borough.empty:
        fig = px.pie(df_borough, values='count', names='borough', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

with col_chart2:
    st.subheader("Top 10 Cuisines Populaires")
    df_cuisine = fetch_cuisine_stats()
    if not df_cuisine.empty:
        fig = px.bar(df_cuisine, x='count', y='cuisine', orientation='h', color='count')
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

# 3. Section Données Détaillées
st.subheader(f"Liste des Restaurants ({selected_borough})")
df_resto = fetch_restaurants(selected_borough)

if not df_resto.empty:
    # Nettoyage pour l'affichage : on garde les colonnes utiles
    display_cols = ["name", "cuisine", "borough", "restaurant_id"]
    # Gestion si adresse est un objet complexe, on simplifie pour l'exemple
    st.dataframe(df_resto[display_cols], use_container_width=True)
else:
    st.info("Aucun restaurant trouvé.")