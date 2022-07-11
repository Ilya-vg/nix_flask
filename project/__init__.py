from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import logging

db = SQLAlchemy()
DB_NAME = "flask_films"

genres_list = ['action', 'thriller', 'comedy', 'drama', 'sci-fi']

logging.basicConfig(filename='record.log', level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


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
