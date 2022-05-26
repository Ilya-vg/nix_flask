import psycopg2
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "flask_movies"


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

    @login_manager.user_loader
    def load_user(u_id):
        return User.query.get(int(u_id))

    return app


def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='flask_movies',
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'])
    return conn
