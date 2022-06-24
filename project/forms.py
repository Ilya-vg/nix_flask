from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField,\
    RadioField, URLField, SelectMultipleField, SelectField
from wtforms.validators import InputRequired

from . import genres_list


class FilmForm(FlaskForm):
    title = StringField('title', validators=[InputRequired()])
    director = StringField('director', validators=[InputRequired()])
    year_released = IntegerField('year_released', validators=[InputRequired()])
    description = StringField('description')
    rating = RadioField('rating', choices=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
    poster = URLField('poster')
    genre = SelectMultipleField('genre', choices=genres_list)


class GenreFilter(FlaskForm):
    genre = SelectField('genre', choices=['Action', 'Thriller', 'Comedy', 'Drama', 'Sci-Fi'])


choices = [i for i in range(1888, 2022)]


class YearFilter(FlaskForm):
    start_year = SelectField('Start year', choices=choices)
    end_year = SelectField('End year', choices=choices)


class DirectorFilter(FlaskForm):
    director = StringField('director', validators=[InputRequired()])


class SearchForm(FlaskForm):
    search_query = StringField('search_query', validators=[InputRequired()])
