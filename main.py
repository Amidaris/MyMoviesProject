from flask import Flask, render_template
from flask import request, url_for, redirect, flash
import requests
import tmdb_client
from tmdb_client import get_single_movie, get_movie_cast, get_movies_list
import datetime

app = Flask(__name__)
app.secret_key = 'my-secret'

FAVORITES = set()

@app.route('/')
def homepage():
    # Lista dozwolonych typów list
    valid_list_types = ['now_playing', 'popular', 'top_rated', 'upcoming']

    # Pobierz typ listy z parametrów URL
    selected_list = request.args.get('list_type', 'popular')

    # Walidacja: jeśli typ nie jest poprawny, ustaw na 'popular'
    if selected_list not in valid_list_types:
        selected_list = 'popular'

    # Pobierz filmy z TMDB
    movies = tmdb_client.get_movies_list(list_type=selected_list)["results"][:8]

    # Przekaż dane do szablonu
    return render_template(
        "homepage.html",
        movies=movies,
        current_list=selected_list,
        list_types=valid_list_types
    )

@app.context_processor
def utility_processor():
    def tmdb_image_url(path, size):
        return tmdb_client.get_poster_url(path, size)
    return {"tmdb_image_url": tmdb_image_url}

@app.route("/movie/<movie_id>")
def movie_details(movie_id):
    movie = get_single_movie(movie_id)
    cast = get_movie_cast(movie_id)[:8]
    return render_template("movie_details.html", movie=movie, cast=cast)

@app.route('/search')
def search():
    search_query = request.args.get("q", "")
    if search_query:
        movies = tmdb_client.search(search_query=search_query)
    else:
        movies = []
    return render_template("search.html", movies=movies, search_query=search_query)

@app.route('/today')
def today():
    movies = tmdb_client.get_airing_today()
    today = datetime.date.today()
    return render_template("today.html", movies=movies, today=today)

@app.route("/favorites")
def show_favorites():
    if FAVORITES:
        movies = []
        for movie_id in FAVORITES:
            movie_details = tmdb_client.get_single_movie(movie_id)
            movies.append(movie_details)
    else:
        movies = []
    return render_template("homepage.html", movies=movies)

@app.route("/favorites/add", methods=['POST'])
def add_to_favorites():
    data = request.form
    movie_id = data.get('movie_id')
    movie_title = data.get('movie_title')
    if movie_id and movie_title:
        FAVORITES.add(movie_id)
        flash(f'Dodano film {movie_title} do ulubionych!')
    return redirect(url_for('homepage'))

if __name__ == '__main__':
    app.run(debug=True)