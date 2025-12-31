import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

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
@st.cache_data(ttl=60)
def fetch_borough_stats():
    response = requests.get(f"{API_URL}/stats/boroughs")
    return pd.DataFrame(response.json())

@st.cache_data(ttl=60)
def fetch_cuisine_stats():
    response = requests.get(f"{API_URL}/stats/cuisines")
    return pd.DataFrame(response.json())

@st.cache_data(ttl=60)
def fetch_restaurants(borough_filter):
    response = requests.get(f"{API_URL}/restaurants", params={"borough": borough_filter, "limit": 50})
    return pd.DataFrame(response.json())

# --- Fonctions ML ---
@st.cache_data(ttl=300)
def fetch_model_status():
    try:
        response = requests.get(f"{API_URL}/ml/model-status")
        return response.json()
    except:
        return {"is_trained": False}

@st.cache_data(ttl=300)
def fetch_risk_analysis():
    try:
        response = requests.get(f"{API_URL}/ml/risk-analysis")
        return response.json()
    except:
        return None

@st.cache_data(ttl=300)
def fetch_high_risk_restaurants():
    try:
        response = requests.get(f"{API_URL}/ml/high-risk-restaurants")
        return response.json()
    except:
        return []

def train_model():
    """Déclenche l'entraînement du modèle ML"""
    try:
        response = requests.post(f"{API_URL}/ml/train")
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def predict_for_restaurant(restaurant_id):
    """Prédit le score pour un restaurant spécifique"""
    try:
        response = requests.get(f"{API_URL}/ml/predict/{restaurant_id}")
        return response.json()
    except:
        return None

# --- Interface Utilisateur ---

st.title("🍔 Dashboard Restaurants New York")
st.markdown("Analyse des données via **FastAPI** et **MongoDB**")

# Sidebar
st.sidebar.header("Filtres")
borough_options = ["Tous", "Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
selected_borough = st.sidebar.selectbox("Choisir un Arrondissement", borough_options)

# === SECTION MACHINE LEARNING ===
st.sidebar.divider()
st.sidebar.header("🤖 Machine Learning")

# Vérifier le statut du modèle
model_status = fetch_model_status()

if model_status.get("is_trained"):
    st.sidebar.success("✅ Modèle ML entraîné")
else:
    st.sidebar.warning("⚠️ Modèle non entraîné")
    if st.sidebar.button("🎯 Entraîner le modèle ML"):
        with st.spinner("Entraînement en cours..."):
            result = train_model()
            if result.get("status") == "success":
                st.sidebar.success("Modèle entraîné avec succès!")
                st.rerun()
            else:
                st.sidebar.error(f"Erreur: {result.get('message')}")

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

# === SECTION MACHINE LEARNING - ANALYSE DES RISQUES ===
if model_status.get("is_trained"):
    st.divider()
    st.header("🤖 Analyse Prédictive - Machine Learning")
    
    # Onglets pour différentes analyses ML
    tab1, tab2, tab3 = st.tabs(["📊 Analyse des Risques", "⚠️ Restaurants à Risque", "🔮 Prédiction Individuelle"])
    
    with tab1:
        st.subheader("Distribution des Niveaux de Risque Sanitaire")
        
        risk_analysis = fetch_risk_analysis()
        
        if risk_analysis:
            col1, col2, col3 = st.columns(3)
            
            risk_dist = risk_analysis['risk_distribution']
            risk_pct = risk_analysis['risk_percentages']
            
            col1.metric(
                "🟢 Faible Risque", 
                risk_dist['Low'],
                f"{risk_pct['Low']}%"
            )
            col2.metric(
                "🟡 Risque Moyen", 
                risk_dist['Medium'],
                f"{risk_pct['Medium']}%"
            )
            col3.metric(
                "🔴 Risque Élevé", 
                risk_dist['High'],
                f"{risk_pct['High']}%"
            )
            
            # Graphique de distribution
            st.markdown("---")
            col_graph1, col_graph2 = st.columns(2)
            
            with col_graph1:
                # Pie chart
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['Faible', 'Moyen', 'Élevé'],
                    values=[risk_dist['Low'], risk_dist['Medium'], risk_dist['High']],
                    marker=dict(colors=['#2ecc71', '#f39c12', '#e74c3c']),
                    hole=0.4
                )])
                fig_pie.update_layout(title="Répartition des Risques")
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_graph2:
                # Bar chart
                fig_bar = go.Figure(data=[go.Bar(
                    x=['Faible', 'Moyen', 'Élevé'],
                    y=[risk_dist['Low'], risk_dist['Medium'], risk_dist['High']],
                    marker=dict(color=['#2ecc71', '#f39c12', '#e74c3c'])
                )])
                fig_bar.update_layout(title="Nombre de Restaurants par Niveau de Risque")
                st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab2:
        st.subheader("🚨 Restaurants à Haut Risque Sanitaire")
        st.markdown("Ces restaurants sont prédits comme ayant un risque élevé lors de leur prochaine inspection.")
        
        high_risk = fetch_high_risk_restaurants()
        
        if high_risk:
            df_high_risk = pd.DataFrame(high_risk)
            
            # Afficher les statistiques
            st.info(f"**{len(high_risk)} restaurants** identifiés comme à haut risque")
            
            # Tableau avec code couleur
            st.dataframe(
                df_high_risk[['name', 'cuisine', 'borough', 'predicted_score', 'current_avg_score']].style.background_gradient(
                    subset=['predicted_score', 'current_avg_score'],
                    cmap='Reds'
                ),
                use_container_width=True
            )
            
            # Top 5 graphique
            st.markdown("### Top 5 Restaurants à Plus Haut Risque")
            top_5 = df_high_risk.head(5)
            fig = px.bar(
                top_5,
                x='predicted_score',
                y='name',
                orientation='h',
                color='predicted_score',
                color_continuous_scale='Reds',
                labels={'predicted_score': 'Score Prédit', 'name': 'Restaurant'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("Aucun restaurant à haut risque détecté!")
    
    with tab3:
        st.subheader("🔮 Prédiction pour un Restaurant Spécifique")
        st.markdown("Entrez l'ID d'un restaurant pour obtenir une prédiction de son prochain score d'inspection.")
        
        # Input pour l'ID du restaurant
        restaurant_id_input = st.text_input(
            "ID du Restaurant",
            placeholder="Ex: 30075445",
            help="Trouvez l'ID dans le tableau des restaurants ci-dessus"
        )
        
        if st.button("🎯 Prédire le Score"):
            if restaurant_id_input:
                with st.spinner("Analyse en cours..."):
                    prediction = predict_for_restaurant(restaurant_id_input)
                    
                    if prediction:
                        st.success("✅ Prédiction réussie!")
                        
                        # Afficher les informations
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"### 🏪 {prediction['restaurant_name']}")
                            st.markdown(f"**Cuisine:** {prediction['cuisine']}")
                            st.markdown(f"**Arrondissement:** {prediction['borough']}")
                            st.markdown(f"**Nombre d'inspections:** {prediction['num_inspections']}")
                        
                        with col2:
                            # Indicateur de risque
                            risk_level = prediction['predicted_risk_level']
                            risk_color = {
                                'Low': '🟢',
                                'Medium': '🟡',
                                'High': '🔴'
                            }.get(risk_level, '⚪')
                            
                            st.markdown(f"### {risk_color} Niveau de Risque: **{risk_level}**")
                            st.metric(
                                "Score Actuel Moyen",
                                f"{prediction['current_avg_score']}"
                            )
                            st.metric(
                                "Score Prédit",
                                f"{prediction['predicted_score']}",
                                delta=f"{prediction['predicted_score'] - prediction['current_avg_score']:.1f}"
                            )
                        
                        # Probabilités de risque
                        st.markdown("### Probabilités de Risque")
                        risk_probs = prediction['risk_probabilities']
                        
                        prob_df = pd.DataFrame({
                            'Niveau': list(risk_probs.keys()),
                            'Probabilité': [f"{v*100:.1f}%" for v in risk_probs.values()]
                        })
                        
                        fig_prob = px.bar(
                            prob_df,
                            x='Niveau',
                            y=[v*100 for v in risk_probs.values()],
                            color='Niveau',
                            color_discrete_map={'Low': '#2ecc71', 'Medium': '#f39c12', 'High': '#e74c3c'},
                            labels={'y': 'Probabilité (%)'}
                        )
                        st.plotly_chart(fig_prob, use_container_width=True)
                        
                    else:
                        st.error("❌ Impossible de faire une prédiction pour ce restaurant. Vérifiez l'ID.")
            else:
                st.warning("Veuillez entrer un ID de restaurant.")
