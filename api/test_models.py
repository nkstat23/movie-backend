#%%
from database import SessionLocal
from models import Movie, Rating, Tag, Link


db = SessionLocal()

#%%
#recuperation de quelaues films
movies = db.query(Movie).limit(10).all() # Recuperer les 10 premiers films de la table movies
for movie in movies:
    print(f"Movie ID: {movie.movieId}, Title: {movie.title}, Genres: {movie.genres}")
else:
    print("---- End of Movies ----")
# %%
# Recuperer touts les films dont le genre est "Action"
action_movies = db.query(Movie).filter(Movie.genres.like("%Action%")).limit(5).all()
for movie in action_movies:
    print(f"Movie ID: {movie.movieId}, Title: {movie.title}, Genres: {movie.genres}")

# %%
# tester la recuperation des evaluations (ratings) pour un film specifique
Ratings = db.query(Rating).filter(Rating.movieId == 1).limit(5).all() # Recuperer toutes les evaluations pour le film avec movieId = 1
for rating in Ratings:
    print(f"User ID: {rating.userId}, Movie ID: {rating.movieId}, Rating: {rating.rating}, Timestamp: {rating.timestamp}")
# %%
# film note >=4
high_rated_movies = db.query(Rating).filter(Rating.rating >= 4).limit(5).all()
for rating in high_rated_movies:
    print(f"User ID: {rating.userId}, Movie ID: {rating.movieId}, Rating: {rating.rating}, Timestamp: {rating.timestamp}")
# %%
# utiliser les jointure les films note >=4
high_rated_movies_with_details = db.query(Movie, Rating).join(Rating, Movie.movieId == Rating.movieId).filter(Rating.rating >= 4).limit(5).all()
for movie, rating in high_rated_movies_with_details:
    print(f"Movie ID: {movie.movieId}, Title: {movie.title}, Rating: {rating.rating}")


# %%
# recuperation des tags associes aux films
tags = db.query(Tag).filter(Tag.movieId == 1).limit(5).all() # Recuperer les tags pour le film avec movieId = 1
for tag in tags:
    print(f"User ID: {tag.userId}, Movie ID: {tag.movieId}, Tag: {tag.tag}, Timestamp: {tag.timestamp}")
# %%
# tester la classe Link
links = db.query(Link).filter(Link.movieId == 1).all() # Recuperer le lien pour le film avec movieId = 1
for link in links:
    print(f"Movie ID: {link.movieId}, IMDB ID: {link.imdbId}, TMDB ID: {link.tmdbId}")
# %%
# fermer la session de base de donnees
db.close()
# %%
