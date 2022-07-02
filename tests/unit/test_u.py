from werkzeug.security import check_password_hash
from project.models import Genre, MovieGenre
from project import genres_list


def test_new_user(new_user):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, hashed_password, authenticated, and role fields are defined correctly
    """
    assert new_user.username == 'test1'
    assert new_user.email == 'mockemail@gmail.com'
    assert check_password_hash(new_user.password, '12345')
    assert new_user.__repr__() == f'<User: test1, email: mockemail@gmail.com'
    assert new_user.is_authenticated
    assert new_user.is_active
    assert not new_user.is_anonymous



def test_new_film(new_film):
    """
    GIVEN a Movie model
    WHEN a new Movie is created
    THEN check that all fields are defined correctly
    """
    assert new_film.title == 'Test film 1'
    assert new_film.director == 'Test director 1'
    assert new_film.year_release == '2000'
    assert new_film.description == 'Test description 1'
    assert new_film.rating == 10
    assert new_film.poster == 'https://www.amazon.com/Movie-Poster-Marvel-Holographic-Authenticity/dp/B07Q1YWKD9'

    for i in ['action', 'thriller']:
        m_g = MovieGenre(genres_list.index(i)+1, new_film.id)
        assert m_g.genre_id == genres_list.index(i)+1
        assert m_g.movie_id == new_film.id


def test_delete():
    pass