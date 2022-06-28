from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

    def get_username(self):
        return self.username


class Movie(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    director = db.Column(db.String(30))
    year_release = db.Column(db.Integer)
    description = db.Column(db.String(2000))
    rating = db.Column(db.Integer)
    poster = db.Column(db.String(100))
    added_by = db.Column(db.String(150))

    children = relationship("MovieGenre", cascade="all,delete", backref="movie")


class Genre(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(30))

    genre_name_id = relationship("MovieGenre")


class MovieGenre(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    genre_id = db.Column(db.Integer, ForeignKey('genre.id'))
    movie_id = db.Column(db.Integer, ForeignKey('movie.id', ondelete="CASCADE"))



