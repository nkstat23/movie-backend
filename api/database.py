""" Database Conficuration"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./movies.db"

## Creer le moteur de base de donnees (engine) qui etablit la connexion a la base de donnees sqlite (movie.db))
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} # cet argument  veut dire que plusieurs threads ()peuvent utiliser la meme connexion a la base de donnees
)
# Definir SessionLocal, qui permet de creer des sessions pour interagir avec la base de donnees
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # valider les modifications manuellement (autocommit=False) et empecher les modifications automatiques (autoflush=False), et lier les sessions au moteur de base de donnees (bind=engine)

#definir  Base, qui servira de classe de base pour nos modele SQLAlchemy (ORM Object Relational Mapping)
Base = declarative_base()
