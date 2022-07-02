import pytest
from werkzeug.security import generate_password_hash
from project import create_app
from project.models import User, Movie


@pytest.fixture()
def test_client():
    flask_app = create_app()

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!


@pytest.fixture()
def new_user():
    user = User(username='test1', email='mockemail@gmail.com',
                password=generate_password_hash('12345', method='sha256'))
    return user


@pytest.fixture()
def new_film_form():
    data = {'title': 'Test film 1', 'director': 'Test director 1',
            'year_release': '2000', 'description': 'Test description 1',
            'rating': 10,
            'poster': 'https://www.amazon.com/Movie-Poster-Marvel-Holographic-Authenticity/dp/B07Q1YWKD9',
            'genre': ['action', 'thriller']}
    return data


@pytest.fixture()
def new_film(new_film_form):
    film = Movie(title=new_film_form['title'],
                 director=new_film_form['director'],
                 year_release=new_film_form['year_release'],
                 description=new_film_form['description'],
                 rating=new_film_form['rating'],
                 poster=new_film_form['poster'],
                 added_by='admin')
    return film


