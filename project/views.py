from flask import Blueprint, render_template, request, flash, redirect
from flask_login import login_required, current_user
from sqlalchemy import func

from . import get_genres, db, genres_list
from .models import Movie, MovieGenre
from .forms import GenreFilter, YearFilter, DirectorFilter, SearchForm, FilmForm

views = Blueprint('views', __name__)

genres: dict = get_genres()


@views.route('/', methods=['GET', 'POST'])
def home():
    movies = Movie.query.paginate(per_page=2, error_out=False)

    form = FilmForm()

    form_genre = GenreFilter()
    form_year = YearFilter()
    form_dir = DirectorFilter()
    form_search = SearchForm()

    # adding new film to a database
    if request.method == 'POST':
        title = form.title.data
        director = form.director.data
        year_release = form.year_release.data
        description = form.description.data
        rating = form.rating.data
        poster = form.poster.data
        genre = request.form.getlist('genre')

        if not current_user.is_authenticated:
            flash('Please log in to add new films to the database', category='error')
        else:
            db.session.add(
                Movie(title, director, year_release, description,
                      rating, poster, current_user.get_username())
            )

            new_film_id = db.session.query(func.max(Movie.id)).scalar()

            for g in genre:
                db.session.add(
                    MovieGenre(genres_list.index(g) + 1, new_film_id)
                )

            db.session.commit()

            flash('New film was added to a database')

    return render_template('home.html', user=current_user, movies=movies,
                           genres=genres, form=form, form_genre=form_genre,
                           form_year=form_year, form_dir=form_dir, form_search=form_search)


@views.route('/search', methods=['POST'])
def search_redirect():
    form_search = SearchForm()
    query = form_search.search_query.data

    return redirect(f'search/{query}')


@views.route('/search/<search_query>', methods=['GET'])
def search(search_query):
    movies = Movie.query.filter(Movie.title.ilike(f'%{search_query}%')).paginate(per_page=1, error_out=False)

    return render_template('search.html', user=current_user, movies=movies,
                           genres=genres, search_query=search_query)


@views.route('/filter', methods=['POST'])
def filter_f():
    form_genre, form_year, form_dir = GenreFilter(), YearFilter(), DirectorFilter()

    if form_genre.validate_on_submit():
        genres_filter = form_genre.genre.data
        movie_ids = []
        for _, e in enumerate(genres):
            if genres_filter.lower() in genres[e]:
                movie_ids.append(e)
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


@views.route('/sort', methods=['POST'])
def sort():
    form = request.form

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


@views.route('/sorted_films/<sort_algo>', methods=['GET'])
def sorted_films(sort_algo):
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
    try:
        username = current_user.username
    except AttributeError:
        flash('Please log in to be able to delete films', category='error')
        return redirect('/')

    if username == Movie.query.with_entities(Movie.added_by).filter_by(id=movie_id).all()[0][0]:
        MovieGenre.query.filter_by(movie_id=movie_id).delete()
        Movie.query.filter_by(id=movie_id).delete()
        db.session.commit()

    else:
        flash('You can only delete/edit a record if you were the user that added it.', category='error')

    return home()


@views.route('/edit/<movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.filter_by(id=movie_id).first()
    m_genres: list = genres[movie.id].split(', ')
    form = FilmForm()

    if request.method == 'GET':

        if current_user.username == movie.added_by:
            return render_template('edit.html', user=current_user, movie=movie,
                                   m_genres=m_genres, form=form)

        flash('Only user that added a film in the database can edit a film record.', category='error')
        return redirect('/')

    title = form.title.data
    director = form.director.data
    year_release = form.year_release.data
    description = form.description.data
    rating = form.rating.data
    poster = form.poster.data
    genre = request.form.getlist('genre')

    Movie.query.filter_by(id=movie_id).update({'title': f'{title}',
                                               'director': f'{director}',
                                               'year_release': f'{year_release}',
                                               'description': f'{description}',
                                               'rating': f'{rating}',
                                               'poster': f'{poster}'})
    MovieGenre.query.filter_by(movie_id=movie_id).delete()

    for g in genre:
        add_g = MovieGenre(genres_list.index(g)+1, movie_id)
        db.session.add(add_g)

    db.session.commit()
    flash('Film was edited successfully', category='success')

    return redirect('/')
