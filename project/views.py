from flask import Blueprint, render_template, request, flash, redirect
from flask_login import login_required, current_user
from . import get_db_connection, get_genres, db, genres_list
import validators

from flask_sqlalchemy import SQLAlchemy

from .models import Movie, MovieGenre, Genre
from .forms import GenreFilter, YearFilter, DirectorFilter, SearchForm

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    genres = get_genres()
    movies = Movie.query.paginate(per_page=2, error_out=False)

    form_genre = GenreFilter()
    form_year = YearFilter()
    form_dir = DirectorFilter()
    form_search = SearchForm()

    # adding new film to a database
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
            cur.execute('INSERT INTO movie (title, director, year_release, description,'
                        'rating, poster, added_by)'
                        'VALUES (%s, %s, %s, %s, %s, %s, %s);',
                        (title, director, release_year, description,
                         rating, poster, current_user.get_username()
                         ))
            cur.execute('select MAX(id) FROM movie;')
            movie_id = cur.fetchall()[0]
            for g in genre:
                cur.execute("SELECT id FROM genre WHERE genre = (%s);", (g,))
                genre_id = cur.fetchall()[0]
                cur.execute('INSERT INTO movie_genre (genre_id, movie_id)'
                            'VALUES (%s, %s);',
                            (genre_id, movie_id))

            conn.commit()
            cur.close()
            conn.close()

            flash('New film was added to a database')

    return render_template('home.html', user=current_user, movies=movies,
                           genres=genres, form_genre=form_genre,
                           form_year=form_year, form_dir=form_dir, form_search=form_search)


@views.route('/search', methods=['GET', 'POST'])
def search_redirect():
    if request.method == 'POST':
        form = SearchForm()
        query = form.search_query.data

        return redirect(f'search/{query}')


@views.route('/search/<search_query>', methods=['GET', 'POST'])
def search(search_query):
    form_search = SearchForm()
    movies = Movie.query.filter(Movie.title.ilike(f'%{search_query}%')).paginate(per_page=1, error_out=False)

    genres = get_genres()

    return render_template('search.html', user=current_user, movies=movies,
                           genres=genres, search_query=search_query)


@views.route('/filter', methods=['GET', 'POST'])
def filtered():
    genres = get_genres()
    form_genre, form_year, form_dir = GenreFilter(), YearFilter(), DirectorFilter()

    if form_genre.validate_on_submit():
        genres_filter = form_genre.genre.data
        movie_ids = []
        for i, e in enumerate(genres):
            if genres_filter.lower() in e[0]:
                movie_ids.append(i + 1)
        movies = db.session.query(Movie).filter(Movie.id.in_(movie_ids)).all()

    elif form_dir.validate_on_submit():
        movies = db.session.query(Movie).filter(Movie.director.ilike(f'%{form_dir.director.data}%')).all()

    elif form_year.validate_on_submit():
        movies = db.session.query(Movie).filter(Movie.year_release >= form_year.start_year.data,
                                                Movie.year_release <= form_year.end_year.data).all()

    if 'movies' not in locals():
        flash('Please choose how to filter films', category='error')
        return home()

    return render_template('filtered.html', user=current_user, movies=movies,
                           genres=genres, form_genre=form_genre, form_year=form_year, form_dir=form_dir)


@views.route('/sort', methods=['GET', 'POST'])
def sort():
    form = request.form
    genres = get_genres()

    if form.get('sort') == 'rating':
        if form.get('asc'):
            sort_algo = 'rating_asc'
        else:
            sort_algo = 'rating'

    else:
        if form.get('asc'):
            sort_algo = 'year_asc'
        else:
            sort_algo = 'year'

    return redirect(f'/sorted_films/{sort_algo}')


@views.route('/sorted_films/<sort_algo>', methods=['GET', 'POST'])
def sorted_films(sort_algo):
    genres = get_genres()
    if sort_algo == 'rating':
        movies = Movie.query.order_by(Movie.rating.desc()).paginate(per_page=2)

    elif sort_algo == 'year':
        movies = Movie.query.order_by(Movie.year_release.desc()).paginate(per_page=2)

    elif sort_algo == 'rating_asc':
        movies = Movie.query.order_by(Movie.rating).paginate(per_page=2)

    else:
        movies = Movie.query.order_by(Movie.year_release).paginate(per_page=2)

    return render_template(f'sorting/{sort_algo}.html', user=current_user, movies=movies, genres=genres)


@views.route('/delete/<movie_id>', methods=['GET'])
def delete(movie_id):
    username = current_user.username

    if username == Movie.query.with_entities(Movie.added_by).filter_by(id=movie_id).all()[0][0]:
        MovieGenre.query.filter_by(movie_id=movie_id).delete()
        Movie.query.filter_by(id=movie_id).delete()
        db.session.commit()

    else:
        flash('You can only delete/edit a record if you were the user that added it.', category='error')

    return home()


@views.route('/edit/<movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    movie = Movie.query.filter_by(id=movie_id).first()
    m_genres = get_genres()[movie.id]

    if request.method == 'GET':

        if current_user.username == movie.added_by:
            return render_template('edit.html', user=current_user, movie=movie, m_genres=m_genres)
        else:
            flash('Only user that added a film in the database can edit a film record.', category='error')
            return redirect('/')

    else:
        form = request.form

        title, director, year_release, description, rating, poster, genre = \
            request.form.get('title'), request.form.get('director'), \
            request.form.get('year_release'), request.form.get('description'), \
            request.form.get('rating'), request.form['poster'], request.form.getlist('genre')
        print('YEAR OF RELEASE :::::::::::', year_release)
        print('&&&&&&&&&&&&&&&', not description)
        print('&&&&&&&&&&&&&&&', not description, len(form))
        try:
            year_release = int(year_release)
        except ValueError:
            flash('Year of release should be a number, please fill it accordingly.', category='error')
        if not validators.url(poster):
            flash('Invalid link to a poster, please check it', category='error')
        elif description and len(request.form) < 6 \
                or not description and len(request.form) < 7:
            flash('Please make sure to fill in all fields.', category='error')
        else:
            Movie.query.filter_by(id=movie_id).update({'title': f'{title}',
                                                       'director': f'{director}',
                                                       'year_release': f'{year_release}',
                                                       'description': f'{description}',
                                                       'rating': f'{rating}',
                                                       'poster': f'{poster}'})
            MovieGenre.query.filter_by(movie_id=movie_id).delete()

            for g in genre:
                add = MovieGenre()
                add.movie_id, add.genre_id = movie_id, genres_list.index(g)+1
                db.session.add(add)

            db.session.commit()

            flash('Film was edited successfully', category='success')

            return redirect('/')

        return redirect(f'/edit/{movie_id}')


