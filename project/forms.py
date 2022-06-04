from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, RadioField, URLField, SelectMultipleField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy

genres = ['action', 'thriller', 'comedy', 'drama', 'sci-fi']


class FilmForm(FlaskForm):
    title = StringField('title', validators=[InputRequired()])
    director = StringField('director', validators=[InputRequired()])
    year_released = IntegerField('year_released', validators=[InputRequired()])
    description = StringField('description')
    rating = RadioField('rating', choices=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
    poster = URLField('poster')
    selected = SelectMultipleField('genre', choices=genres)