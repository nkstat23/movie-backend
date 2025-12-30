from fastapi import FastAPI, HTTPException,Query,Path
from sqlalchemy.orm import Session
from typing import List, Optional
from database import SessionLocal
import query_helpers as helpers
import schemas

# -- Initialisation de l'application FastAPI --

api_description = """Bienvenue dans l'API MovieLens!"""

app = FastAPI(
    title = "MovieLens API",
    description = api_description,
    version = "0.1"
)

# -- Dépendance pour obtenir une session de base de données --
def get_db():
    db = SessionLocal()
    try:
        yield db # gerer la session avec yield
    finally:
        db.close()

# Endpoint pour la sante de l'Api
@app.get(
    "/",
    summary="Vérifier la santé de l'API",
    description = "verifier si l'API est opérationnelle",
    response_description="Statut de santé de l'API",
    operation_id="check_health",
    tags=["Monitoring"]
)

async def root():
    return {"message": "API MovieLens est opérationnelle!"}

