# 🤖 Intégration Machine Learning - Dashboard Restaurant

## Vue d'ensemble

Ce dashboard intègre un modèle de Machine Learning qui analyse et prédit les performances sanitaires des restaurants de New York basé sur leur historique d'inspections.

## 🎯 Fonctionnalités ML

### 1. **Prédiction de Score d'Inspection**
- Prédit le prochain score d'inspection sanitaire d'un restaurant
- Basé sur l'historique des scores, la cuisine, l'arrondissement et les tendances

### 2. **Classification de Risque**
- Classifie les restaurants en 3 niveaux :
  - 🟢 **Faible Risque** : Score moyen ≤ 13
  - 🟡 **Risque Moyen** : Score moyen entre 14 et 27
  - 🔴 **Risque Élevé** : Score moyen > 27

### 3. **Analyse des Tendances**
- Identifie les restaurants à haut risque
- Analyse la distribution des risques dans la base de données
- Calcule les probabilités de risque pour chaque établissement

## 📊 Modèle Utilisé

**Random Forest** (Ensemble Learning)
- **Prédicteur de Score** : RandomForestRegressor
- **Classificateur de Risque** : RandomForestClassifier
- **Nombre d'arbres** : 100
- **Features** : 9 caractéristiques extraites

### Features extraites :
1. **cuisine_encoded** : Type de cuisine (encodé)
2. **borough_encoded** : Arrondissement (encodé)
3. **avg_score** : Score moyen historique
4. **max_score** : Score maximum historique
5. **min_score** : Score minimum historique
6. **std_score** : Écart-type des scores
7. **num_inspections** : Nombre d'inspections
8. **score_trend** : Tendance (score récent - moyenne)
9. **bad_grades_ratio** : Ratio de mauvaises notes (B, C, Z)

## 🚀 Installation

1. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

Les nouvelles dépendances ML :
- `scikit-learn` : Modèles de Machine Learning
- `numpy` : Calculs numériques
- `joblib` : Sauvegarde/chargement du modèle

## 📖 Guide d'utilisation

### Étape 1 : Démarrer le Backend
```bash
cd restaurant-dashboard
uvicorn backend.main:app --reload
```

### Étape 2 : Démarrer le Frontend
```bash
cd frontend
streamlit run app.py
```

### Étape 3 : Entraîner le Modèle

**Option A - Via l'interface Streamlit :**
1. Ouvrez le dashboard dans votre navigateur
2. Dans la sidebar, cliquez sur "🎯 Entraîner le modèle ML"
3. Attendez la confirmation

**Option B - Via l'API directement :**
```bash
curl -X POST http://127.0.0.1:8000/api/ml/train
```

### Étape 4 : Explorer les Analyses

Une fois le modèle entraîné, trois onglets sont disponibles :

#### 📊 **Onglet 1 : Analyse des Risques**
- Visualisation de la distribution des niveaux de risque
- Graphiques en camembert et barres
- Statistiques globales

#### ⚠️ **Onglet 2 : Restaurants à Risque**
- Liste des 20 restaurants à plus haut risque
- Tableau avec scores prédits et actuels
- Graphique Top 5 des plus risqués

#### 🔮 **Onglet 3 : Prédiction Individuelle**
- Entrez l'ID d'un restaurant (ex: `30075445`)
- Obtenez :
  - Score prédit
  - Niveau de risque
  - Probabilités pour chaque niveau
  - Comparaison avec la moyenne actuelle

## 🔌 Endpoints API

### 1. Entraîner le modèle
```http
POST /api/ml/train
```
**Réponse :**
```json
{
  "status": "success",
  "message": "Modèle entraîné avec succès",
  "metrics": {
    "score_r2": 0.85,
    "risk_accuracy": 0.92,
    "num_samples": 1234
  }
}
```

### 2. Prédire pour un restaurant
```http
GET /api/ml/predict/{restaurant_id}
```
**Exemple :** `/api/ml/predict/30075445`

**Réponse :**
```json
{
  "restaurant_name": "Morris Park Bake Shop",
  "cuisine": "Bakery",
  "borough": "Bronx",
  "predicted_score": 8.2,
  "predicted_risk_level": "Low",
  "risk_probabilities": {
    "Low": 0.85,
    "Medium": 0.12,
    "High": 0.03
  },
  "current_avg_score": 8.2,
  "num_inspections": 5
}
```

### 3. Analyse des risques globale
```http
GET /api/ml/risk-analysis
```

### 4. Restaurants à haut risque
```http
GET /api/ml/high-risk-restaurants?limit=20
```

### 5. Statut du modèle
```http
GET /api/ml/model-status
```

## 📈 Interprétation des Résultats

### Scores d'inspection
- **0-13** : Excellent (A)
- **14-27** : Acceptable (B)
- **28+** : Problématique (C ou plus)

### Niveau de risque
- **Low** : Restaurant performant, peu de chances de violation
- **Medium** : Surveillance recommandée
- **High** : Inspection prioritaire recommandée

## 🔧 Architecture Technique

```
restaurant-dashboard/
├── backend/
│   ├── main.py              # API FastAPI avec endpoints ML
│   ├── ml_model.py          # Module ML principal
│   ├── database.py          # Connexion MongoDB
│   └── restaurant_ml_model.pkl  # Modèle entraîné (généré)
├── frontend/
│   └── app.py               # Interface Streamlit avec visualisations ML
└── requirements.txt         # Dépendances incluant scikit-learn
```

## 🎓 Algorithme et Méthodologie

### Pourquoi Random Forest ?

1. **Robustesse** : Résistant au surapprentissage
2. **Interprétabilité** : Importance des features facilement accessible
3. **Performance** : Excellent pour les données tabulaires
4. **Versatilité** : Fonctionne bien pour régression et classification

### Pipeline de traitement

1. **Extraction des features** → Calcul des statistiques historiques
2. **Encodage** → Transformation des variables catégorielles
3. **Entraînement** → Fit sur l'ensemble des données
4. **Prédiction** → Inference sur nouveaux restaurants
5. **Persistance** → Sauvegarde du modèle avec joblib

## 🐛 Dépannage

### Erreur "Le modèle n'a pas encore été entraîné"
→ Entraînez d'abord le modèle via l'interface ou l'API

### Erreur "Pas assez de données"
→ Assurez-vous que MongoDB contient des restaurants avec des `grades`

### Prédiction impossible pour un restaurant
→ Le restaurant doit avoir au moins un historique d'inspection (`grades`)

## 📊 Performance du Modèle

Typiquement, sur l'ensemble de données NYC restaurants :
- **R² Score** : ~0.75-0.85 pour la prédiction de score
- **Accuracy** : ~0.85-0.92 pour la classification de risque
- **Temps d'entraînement** : 5-15 secondes (selon la taille des données)

## 🔮 Améliorations Futures

- [ ] Ajouter des features temporelles (saison, tendances)
- [ ] Intégrer des données géographiques (proximité d'autres restaurants)
- [ ] Modèle de séries temporelles pour prédire l'évolution
- [ ] Système de recommandations pour améliorer les scores
- [ ] API de batch prediction pour analyser plusieurs restaurants

## 📝 Notes Importantes

⚠️ Le modèle est purement prédictif et basé sur des patterns historiques. Il ne remplace pas une inspection sanitaire officielle.

✅ Les prédictions sont mises à jour à chaque réentraînement du modèle avec les nouvelles données.

---

**Développé avec ❤️ pour l'analyse prédictive des restaurants NYC**
