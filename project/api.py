from datetime import timedelta

from flask_jwt_extended import create_access_token, jwt_required, current_user
from flask_restx import Resource, Api, abort, fields
from flask import Blueprint, request
from werkzeug.security import check_password_hash, generate_password_hash

from project import jwt, db, genres_list
from project.models import Movie, User, MovieGenre, Genre

blueprint = Blueprint('api', __name__)
api = Api(blueprint, version='1.0', title='Home Films Database',
          description='An API for a home films platform.')

ns_auth = api.namespace('auth', 'User authentication-related.')
ns_films = api.namespace('films', 'Everything about your films.')

auth_param = {'jwt_key': {'description': 'JWT auth key of user',
                          'in': 'header'}}

pgnate_param = {'page': {'description': 'A page that you want to get,'
                                        ' 1st by default',
                         'in': 'query'},
                'per_page': {'description': 'Number of films on a page,'
                                            ' 10 by default',
                             'in': 'query'}}

users = api.model('User', {
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

movies = api.model('Movie', {
    'title': fields.String(required=True),
    'director': fields.String(required=True),
    'year_release': fields.Integer(required=True),
    'description': fields.String,
    'rating': fields.Integer(required=True),
    'poster': fields.String(required=True),
    'added_by': fields.String(required=True),
})

login_info = api.model('Login Info', {
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


@ns_auth.route("/whoami")
class WhoAmI(Resource):
    @jwt_required()
    def get(self):
        return {'id': current_user.id, 'username': current_user.username, 'email': current_user.email}


@ns_auth.route('/signup')
class SignUp(Resource):
    @ns_auth.expect(users)
    def post(self):
        username = request.json['username']
        email = request.json['email']
        password = request.json['password']

        by_email = User.query.filter_by(email=email).all()
        by_name = User.query.filter_by(username=username).all()

        if by_email:
            return {'data': 'User with this email already exists.'}
        if by_name:
            return {'data': 'User with this name already exists.'}

        user = User(username, email, generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        ns_auth.logger.info('A new user %s has signed up.', user.username)

        return {'data': f'New user {user.username} was added successfully.'}


@ns_auth.route("/login")
class Login(Resource):
    @ns_auth.expect(login_info)
    def post(self):
        username = request.json['username']
        password = request.json['password']

        user = User.query.filter_by(username=username).one_or_none()
        if not user or not check_password_hash(user.password, password):
            return {'data': 'Wrong username or password'}

        access_token = create_access_token(identity=user, expires_delta=timedelta(days=7))
        ns_auth.logger.info('A user %s has logged in.', user.username)

        return access_token


@ns_films.route('/<int:film_id>')
@ns_films.doc(responses={404: 'Wrong ID provided', 200: 'Success'})
class Film(Resource):
    nf_message = 'No film with provided id exists in the database.'

    @ns_films.doc(description='Gets the record by id.')
    def get(self, film_id):
        film = Movie.query.filter_by(id=film_id).first()
        if not film:
            abort(404, Film.nf_message)
        return film.as_dict()

    @ns_films.doc(params=auth_param, description='Updates the record by id.')
    @jwt_required()
    def put(self, film_id):
        film = Movie.query.filter_by(id=film_id).first()
        if not film:
            abort(404, Film.nf_message)
        if current_user.username in (film.added_by, 'admin'):
            json = request.json
            if 'title' in json:
                film.title = json['title']
            if 'director' in json:
                film.director = json['director']
            if 'year_release' in json:
                film.year_release = int(json['year_release'])
            if 'description' in json:
                film.description = json['description']
            if 'rating' in json:
                film.rating = int(json['rating'])
            if 'poster' in json:
                film.poster = json['poster']
            if 'genres' in json:
                MovieGenre.query.filter_by(movie_id=film_id).delete()
                for g in json['genres']:
                    add_g = MovieGenre(genres_list.index(g) + 1, film_id)
                    db.session.add(add_g)

            db.session.commit()
            ns_films.logger.info('A film %s was edited successfully.', film.title)

            return {'data': 'Film edited successfully'}

        return {'data': 'Only a user that added film in the database can edit it.'}

    @ns_films.doc(params=auth_param, description='Deletes the record by id.')
    @jwt_required()
    def delete(self, film_id):
        film = Movie.query.filter_by(id=film_id).first()
        if not film:
            abort(404, Film.nf_message)

        if current_user.username in (film.added_by, 'admin'):
            title = film.title
            db.session.delete(film)
            db.session.commit()
            ns_films.logger.info('A film %s was deleted from a database.', title)
            return {'data': f'Film with id {film_id} was deleted successfully.'}

        return {'data': 'You can only delete/edit a record'
                        ' if you were the user that added it'
                        'or if you\'re an admin.'}, 400


@ns_films.route('/')
@ns_films.doc(description='Gets paginated list of all films in a database.', params=pgnate_param)
class FilmList(Resource):
    @ns_films.expect(movies)
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        film_list = Movie.query.paginate(page=page, per_page=per_page)

        films_on_page = []
        for film in film_list.items:
            films_on_page.append(film.as_dict())

        meta = {
            "page": film_list.page,
            'pages': film_list.pages,
            'total_count': film_list.total,
            'prev_page': film_list.prev_num,
            'next_page': film_list.next_num,
            'has_next': film_list.has_next,
            'has_prev': film_list.has_prev,

        }

        return films_on_page, meta


@ns_films.route('/search')
@ns_films.doc(description='Search film by title (supports partial match).')
class Search(Resource):
    @ns_films.expect(api.model('search_query', {'query': fields.String(required=True)}))
    def get(self):
        query = request.json['query']

        films = Movie.query.filter(Movie.title.ilike(f'%{query}%'))
        films = films.paginate(per_page=10, error_out=False)

        films_on_page = []
        for film in films.items:
            films_on_page.append(film.as_dict())

        ns_films.logger.info('Search request for: %s', query)

        return films_on_page


@ns_films.route('/add')
class Add(Resource):
    @ns_films.doc(params=auth_param, description='Adds a new film in a database.')
    @jwt_required()
    def post(self):
        json = request.json
        try:
            add_film = Movie(title=json['title'],
                             director=json['director'],
                             year_release=json['year_release'],
                             description='',
                             rating=json['rating'],
                             poster=json['poster'],
                             added_by=current_user.username)

        except KeyError:
            return {'data': 'Please provide the following fields to create a new film record:'
                            '- title'
                            '- director'
                            '- description (this field is optional)'
                            '- year_release'
                            '- rating'
                            '- poster'}, 400
        if 'description' in json:
            add_film.description = json['description']

        db.session.add(add_film)

        if json['genre']:
            for g in json['genre']:
                db.session.add(
                    MovieGenre(genres_list.index(g) + 1, add_film.id)
                )
        else:
            return {'data': 'Please provide at least one genre in "genres" list.'}, 400

        db.session.commit()
        ns_films.logger.info('A film %s was added to a database.', add_film.title)

        return {'data': f'New film {add_film.title} with id {add_film.id} was added successfully.'}


@ns_films.route('/filter')
@ns_films.doc(params=pgnate_param, description='Filters films by either year of release or genre')
class Filter(Resource):
    @ns_films.expect(api.model('filter_algo', {'algo': fields.String(required=True)}))
    def get(self):
        algo = request.json['algo']
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        if algo == 'year':

            films = Movie.query.filter(Movie.year_release >= request.json['start_year'],
                                       Movie.year_release <= request.json['end_year'])

        elif algo == 'genre':
            genre_id = Genre.query.filter_by(genre=request.json['genre']) \
                .with_entities(Genre.id).first()[0]
            ids = MovieGenre.query.filter_by(genre_id=genre_id).with_entities(MovieGenre.movie_id).all()

            ids = [m_id[0] for m_id in ids]
            films = db.session.query(Movie).filter(Movie.id.in_(ids))

        elif algo == 'director':
            films = db.session.query(Movie).filter(
                Movie.director.ilike(f'%{request.json["director"]}%'))

        else:
            return {'data': 'Unknown filtering condition.'
                            ' Valid ones are year of release, genre or director.'}, 400

        films = films.paginate(page=page, per_page=per_page)
        data = []
        for film in films.items:
            data.append(film.as_dict())

        return data


@ns_films.route('/sort')
@ns_films.doc(params=pgnate_param, description='Sorts films by their rating or year.')
class Sort(Resource):
    @ns_films.expect(api.model('sort_algo', {'algo': fields.String(required=True),
                                             'desc': fields.Boolean(required=True)}))
    def get(self):
        sort = request.json['algo']
        desc = request.json['desc']

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        if sort == 'rating':
            if desc:
                films = Movie.query.order_by(Movie.rating.desc()).paginate(page=page, per_page=per_page)
            else:
                films = Movie.query.order_by(Movie.rating).paginate(page=page, per_page=per_page)

        elif sort == 'year':
            if desc:
                films = Movie.query.order_by(Movie.year_release.desc()).paginate(page=page, per_page=per_page)
            else:
                films = Movie.query.order_by(Movie.year_release).paginate(page=page, per_page=per_page)

        else:
            return {'data': 'Please provide valid json data for sorting '
                            '(algo: year or algo: rating).'}

        films_on_page = []
        for film in films.items:
            films_on_page.append(film.as_dict())

        return films_on_page
