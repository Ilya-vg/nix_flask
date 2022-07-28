import pytest
from werkzeug.security import generate_password_hash
from project import app
from project.models import User, Movie


@pytest.fixture()
def test_client():
    # Create a test client using the Flask application configured for testing
    with app.test_client() as testing_client:
        # Establish an application context
        with app.app_context():
            yield testing_client  # this is where the testing happens!


@pytest.fixture()
def new_user_form():
    data = {'username': 'userpytest',
            'email': 'uniqueemail@gmail.com',
            'password1': '1234567'}
    return data


@pytest.fixture()
def new_api_user_data():
    data = {'username': 'api_test_user',
            'email': 'apitestuser@mail.com',
            'password': '1234567'}
    return data


@pytest.fixture()
def new_user():
    user = User(username='test1', email='mockemail@gmail.com',
                password=generate_password_hash('12345'))
    return user


@pytest.fixture()
def user_email_exists():
    data = {'username': 'new_user444',
            'email': 'ilyagvv@gmail.com',
            'password': '1234567'}
    return data


@pytest.fixture()
def user_name_exists():
    data = {'username': 'admin',
            'email': 'newmail@gmail.com',
            'password': '1234567'}
    return data


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
