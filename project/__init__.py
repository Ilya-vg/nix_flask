from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
import logging

db = SQLAlchemy()
DB_NAME = "flask_films"

genres_list = ['action', 'thriller', 'comedy', 'drama', 'sci-fi']

logging.basicConfig(filename='record.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


app = Flask(__name__)
app.config['SECRET_KEY'] = '1'
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://nix:1@localhost/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "2"
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['ERROR_404_HELP'] = False

jwt = JWTManager(app)

db.init_app(app)

from .views import views
from .auth import auth
from .api import blueprint as api

app.register_blueprint(views, url_prefix='/')
app.register_blueprint(auth, url_prefix='/')
app.register_blueprint(api, url_prefix='/api')

from .models import User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(u_id):
    return User.query.get(int(u_id))
