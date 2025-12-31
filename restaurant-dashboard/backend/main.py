from fastapi import FastAPI, HTTPException
from backend.database import get_collection
from backend.ml_model import ml_model
from bson import ObjectId
import math

app = FastAPI(title="Resto API By Irch Defluviaire", description="API pour le Dashboard Restaurant")
collection = get_collection()

# Variable pour tracker l'état d'entraînement du modèle
model_trained = False

# Helper pour convertir ObjectId en string
def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

@app.get("/")
def read_root():
    return {"message": "API Resto en ligne"}

# 1. KPI Globaux
@app.get("/api/stats/global")
def get_global_stats():
    total = collection.count_documents({})
    cuisines = len(collection.distinct("cuisine"))
    boroughs = len(collection.distinct("borough"))
    return {"total_restaurants": total, "total_cuisines": cuisines, "total_boroughs": boroughs}

# 2. Agrégation par Borough
@app.get("/api/stats/boroughs")
def get_borough_stats():
    pipeline = [
        {"$group": {"_id": "$borough", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    data = list(collection.aggregate(pipeline))
    # Nettoyage pour le frontend
    return [{"borough": item["_id"], "count": item["count"]} for item in data]

# 3. Agrégation par Cuisine (Top 10)
@app.get("/api/stats/cuisines")
def get_cuisine_stats():
    pipeline = [
        {"$group": {"_id": "$cuisine", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    data = list(collection.aggregate(pipeline))
    return [{"cuisine": item["_id"], "count": item["count"]} for item in data]

# 4. Liste des restaurants (avec recherche et pagination)
@app.get("/api/restaurants")
def get_restaurants(page: int = 1, limit: int = 20, borough: str = None):
    skip = (page - 1) * limit
    query = {}
    if borough and borough != "Tous":
        query["borough"] = borough

    cursor = collection.find(query).skip(skip).limit(limit)
    restaurants = [serialize_doc(doc) for doc in cursor]
    return restaurants

# ============= ENDPOINTS MACHINE LEARNING =============

@app.post("/api/ml/train")
def train_ml_model():
    """
    Entraîne le modèle ML sur toutes les données disponibles
    """
    global model_trained
    try:
        # Récupérer tous les restaurants avec leurs grades
        restaurants_data = list(collection.find({"grades": {"$exists": True, "$ne": []}}))
        
        if len(restaurants_data) < 10:
            raise HTTPException(status_code=400, detail="Pas assez de données pour entraîner le modèle")
        
        # Entraîner le modèle
        metrics = ml_model.train(restaurants_data)
        model_trained = True
        
        # Sauvegarder le modèle
        ml_model.save_model('backend/restaurant_ml_model.pkl')
        
        return {
            "status": "success",
            "message": "Modèle entraîné avec succès",
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'entraînement: {str(e)}")

@app.get("/api/ml/predict/{restaurant_id}")
def predict_restaurant_score(restaurant_id: str):
    """
    Prédit le prochain score d'inspection pour un restaurant spécifique
    """
    global model_trained
    
    # Charger le modèle si non entraîné
    if not model_trained:
        if ml_model.load_model('backend/restaurant_ml_model.pkl'):
            model_trained = True
        else:
            raise HTTPException(status_code=400, detail="Le modèle n'a pas encore été entraîné. Appelez /api/ml/train d'abord")
    
    try:
        # Récupérer les données du restaurant
        restaurant = collection.find_one({"restaurant_id": restaurant_id})
        
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant non trouvé")
        
        if not restaurant.get('grades') or len(restaurant['grades']) == 0:
            raise HTTPException(status_code=400, detail="Ce restaurant n'a pas d'historique d'inspection")
        
        # Faire la prédiction
        prediction = ml_model.predict(restaurant)
        
        if not prediction:
            raise HTTPException(status_code=500, detail="Erreur lors de la prédiction")
        
        # Ajouter les infos du restaurant
        prediction['restaurant_name'] = restaurant['name']
        prediction['cuisine'] = restaurant['cuisine']
        prediction['borough'] = restaurant['borough']
        
        return prediction
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction: {str(e)}")

@app.get("/api/ml/risk-analysis")
def get_risk_analysis():
    """
    Obtient une analyse des niveaux de risque pour tous les restaurants
    """
    global model_trained
    
    if not model_trained:
        if ml_model.load_model('backend/restaurant_ml_model.pkl'):
            model_trained = True
        else:
            raise HTTPException(status_code=400, detail="Le modèle n'a pas encore été entraîné")
    
    try:
        # Récupérer tous les restaurants avec grades
        restaurants_data = list(collection.find({"grades": {"$exists": True, "$ne": []}}))
        
        # Obtenir les statistiques de risque
        risk_stats = ml_model.get_risk_statistics(restaurants_data)
        
        return risk_stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")

@app.get("/api/ml/high-risk-restaurants")
def get_high_risk_restaurants(limit: int = 20):
    """
    Récupère les restaurants à haut risque sanitaire
    """
    global model_trained
    
    if not model_trained:
        if ml_model.load_model('backend/restaurant_ml_model.pkl'):
            model_trained = True
        else:
            raise HTTPException(status_code=400, detail="Le modèle n'a pas encore été entraîné")
    
    try:
        # Récupérer les restaurants avec grades
        restaurants_data = list(collection.find({"grades": {"$exists": True, "$ne": []}}))
        
        high_risk_restaurants = []
        
        for restaurant in restaurants_data[:200]:  # Limiter pour la performance
            try:
                prediction = ml_model.predict(restaurant)
                if prediction and prediction['predicted_risk_level'] == 'High':
                    high_risk_restaurants.append({
                        'restaurant_id': restaurant['restaurant_id'],
                        'name': restaurant['name'],
                        'cuisine': restaurant['cuisine'],
                        'borough': restaurant['borough'],
                        'predicted_score': prediction['predicted_score'],
                        'current_avg_score': prediction['current_avg_score'],
                        'risk_level': prediction['predicted_risk_level']
                    })
            except:
                continue
        
        # Trier par score prédit (descendant)
        high_risk_restaurants.sort(key=lambda x: x['predicted_score'], reverse=True)
        
        return high_risk_restaurants[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")

@app.get("/api/ml/model-status")
def get_model_status():
    """
    Vérifie si le modèle ML est entraîné et prêt
    """
    global model_trained
    
    # Tenter de charger le modèle s'il n'est pas en mémoire
    if not model_trained:
        model_trained = ml_model.load_model('backend/restaurant_ml_model.pkl')
    
    return {
        "is_trained": model_trained,
        "model_ready": ml_model.is_trained
    }