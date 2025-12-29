"""SQLAlchemy Query Functions for MovieLens API """
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from typing import Optional

import models

# --- Films ---
def get_movie(db: Session, movie_id: int) :
    # recuperer un film par son ID
    return db.query(models.Movie).filter(models.Movie.movieId == movie_id).first()

def get_movies(db: Session, skip: int = 0, limit: int = 100, title: str = None, genre: str=None):
    #recuperer une liste de films avec filtres optionnels
    query = db.query(models.Movie)
    if title:
        query = query.filter(models.Movie.title.ilike(f"%{title}%"))
    if genre:
        query = query.filter(models.Movie.genres.ilike(f"%{genre}%"))
    return query.offset(skip).limit(limit).all()


# --- Evaluations (Ratings) ---
def get_rating(db: Session, user_id: int, movie_id: int):
    # recuperer une evaluation par user_id et movie_id
    return db.query(models.Rating).filter(models.Rating.userId == user_id, models.Rating.movieId == movie_id).first()

def get_ratings(db: Session, skip: int = 0, limit: int = 100, min_rating: Optional[float] = None):
    # recuperer une liste d'evaluations avec un filtre optionnel sur la note minimale
    query = db.query(models.Rating)
    if min_rating is not None:
        query = query.filter(models.Rating.rating >= min_rating)
    return query.offset(skip).limit(limit).all()


# --- Tags ---
def get_tag(db: Session, user_id: int, movie_id: int, tag_text: str):
    # recuperer un tag par user_id, movie_id et le texte du tag
    return db.query(models.Tag).filter(models.Tag.userId == user_id, models.Tag.movieId == movie_id, models.Tag.tag == tag_text).first()


def get_tags(db: Session, skip: int = 0, limit: int = 100, movie_id: Optional[int] = None):
    # recuperer une liste de tags avec un filtre optionnel sur movie_id
    query = db.query(models.Tag)
    if movie_id is not None:
        query = query.filter(models.Tag.movieId == movie_id)
    return query.offset(skip).limit(limit).all()



# --- Links ---
def get_link(db: Session, movie_id: int):
    # recuperer un lien par movie_id
    return db.query(models.Link).filter(models.Link.movieId == movie_id).first()


def get_links(db: Session, skip: int = 0, limit: int = 100):
    # recuperer une liste de liens
    return db.query(models.Link).offset(skip).limit(limit).all()


# ---Requetes analytiques ---
def get_movie_count(db:Session):
    # recuperer le nombre total de films
    return db.query(models.Movie).count()

def get_rating_count(db:Session):
    # recuperer le nombre total d'evaluations
    return db.query(models.Rating).count()

def get_tag_count(db:Session):
    # recuperer le nombre total de tags
    return db.query(models.Tag).count()


def get_link_count(db:Session):
    # recuperer le nombre total de liens
    return db.query(models.Link).count()

# c'est optionnele mais on peut passer directemment a l'api c'est une bonne pratique
