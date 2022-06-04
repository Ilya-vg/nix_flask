from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from . import get_db_connection
import validators

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM movie')
    list_movies = cur.fetchall()

    cur.execute('SELECT genre.genre, movie_genre.movie_id FROM genre '
                'JOIN movie_genre ON genre.id = movie_genre.genre_id; '
                )
    list_genres = cur.fetchall()

    for genre in list_genres:
        print(genre[0], genre[1])
        list_movies[genre[1] - 1] += (genre[0],)

    conn.commit()
    cur.close()
    conn.close()

    if request.method == 'POST':
        title = request.form.get('title')
        director = request.form.get('director')
        release_year = request.form.get('release_year')
        description = request.form.get('description')
        rating = request.form.get('rating')
        poster = request.form['poster']
        genre = request.form.getlist('genre')
        try:
            release_year = int(release_year)
        except ValueError:
            flash('Year of release should be a number, please fill it accordingly.', category='error')
        if not validators.url(poster):
            flash('Invalid link to a poster, please check it', category='error')
        if not description and len(request.form) < 6 \
                or description and len(request.form) < 7:
            flash('Please make sure to fill in all fields.', category='error')
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('INSERT INTO movie (title, director, release_year, description,'
                        'rating, poster, user_added)'
                        'VALUES (%s, %s, %s, %s, %s, %s, %s);',
                        (title, director, release_year, description,
                         rating, poster, current_user.get_username()
                         ))
            cur.execute('select MAX(id) FROM movie;')
            movie_id = cur.fetchall()[0]
            for i in genre:
                cur.execute("SELECT id FROM genre WHERE genre = (%s);", (i,))
                genre_id = cur.fetchall()[0]
                cur.execute('INSERT INTO movie_genre (genre_id, movie_id)'
                            'VALUES (%s, %s);',
                            (genre_id, movie_id))

            conn.commit()

            cur.close()
            conn.close()

            flash('New film was added to a database')

    return render_template('home.html', list_movies=list_movies, user=current_user)


@views.route('/add_movie', methods=['POST'])
def add_movie():
    return 'Add movie'
