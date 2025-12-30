from fastapi import FastAPI
from backend.database import get_collection
from bson import ObjectId
import math

app = FastAPI(title="Resto API", description="API pour le Dashboard Restaurant")
collection = get_collection()

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