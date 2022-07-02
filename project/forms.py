from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, \
    RadioField, URLField, SelectField, PasswordField, EmailField
from wtforms.validators import InputRequired, Length, EqualTo


class SignupForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=2, max=25)])
    email = EmailField('Email', validators=[InputRequired()])
    password1 = PasswordField('Password',
                              validators=[InputRequired(), Length(min=7, max=35),
                                          EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])


class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password', validators=[InputRequired(), Length(min=7, max=35)])


class FilmForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    director = StringField('Director', validators=[InputRequired()])
    year_release = IntegerField('Year of release', validators=[InputRequired()])
    description = StringField('Description', validators=[Length(min=12, max=250)])
    rating = RadioField('Rating',
                        choices=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
                        validators=[InputRequired()])
    poster = URLField('Poster')


class GenreFilter(FlaskForm):
    genre = SelectField('genre', choices=['Action', 'Thriller', 'Comedy', 'Drama', 'Sci-Fi'])


choices = list(range(1888, 2022))


class YearFilter(FlaskForm):
    start_year = SelectField('Start year', choices=choices)
    end_year = SelectField('End year', choices=choices)


class DirectorFilter(FlaskForm):
    director = StringField('director', validators=[InputRequired()])


class SearchForm(FlaskForm):
    search_query = StringField('search_query', validators=[InputRequired()])
