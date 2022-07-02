import os
import psycopg2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "flask_films"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '1'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://nix:1@localhost/{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(u_id):
        return User.query.get(int(u_id))

    return app


def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='flask_films',
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'])
    return conn


def get_genres():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT array_agg (genre), movie.id FROM movie '
                'INNER JOIN movie_genre on movie.id = movie_id '
                'INNER JOIN genre ON genre.id = movie_genre.genre_id '
                'GROUP BY movie.id '
                'ORDER BY movie.id;')

    genres_l = cur.fetchall()

    genres = {}

    for g in genres_l:
        genres[g[1]] = ', '.join(g[0])

    conn.commit()
    cur.close()
    conn.close()

    return genres


genres_list = ['action', 'thriller', 'comedy', 'drama', 'sci-fi']
