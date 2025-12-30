from pydantic import BaseModel, Field
from typing import Optional, List

class RestaurantBase(BaseModel):
    name: str
    borough: str
    cuisine: str
    restaurant_id: str

# Modèle pour les statistiques
class StatsBorough(BaseModel):
    borough: str
    count: int