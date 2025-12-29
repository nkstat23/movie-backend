#%%
from database import SessionLocal
from query_helpers import *

db = SessionLocal()
#%%
movie = get_movie(db, movie_id=1)
print(f"Movie ID: {movie.movieId}, Title: {movie.title}, Genres: {movie.genres}")
db.close()
# %%
