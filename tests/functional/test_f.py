from flask_login import FlaskLoginClient

from project import db, create_app
from project.models import User, Movie


class TestClassHome:
    def test_home_get(self, test_client):
        """
        WHEN the '/' page is requested (GET)
        THEN the response is valid, code 200
        """
        response = test_client.get('/')

        assert response.status_code == 200
        assert b"Home" in response.data
        assert b"Film genre (one or multiple):" in response.data

    def test_home_post_no_user(self, test_client):
        """
        WHEN the '/' page is requested (POST) with no user provided
        THEN the response is valid, code 200
        """
        response = test_client.post('/')

        assert response.status_code == 200
        assert b"Add a new film below" in response.data
        assert b"Submit" in response.data

    def test_home_post_valid_user(self, test_client, new_film_form):
        """
        WHEN the '/' page is requested (POST) with valid user (admin) provided
        THEN response is valid and the film is created
        """

        app = create_app()
        app.test_client_class = FlaskLoginClient

        user = User.query.filter_by(username='admin').first()
        with app.test_client(user=user) as client:
            response = client.post('/', data={'title': 'Test film 1',
                                              'director': 'Test director 1',
                                              'year_release': '2000', 'description': 'Test description 1',
                                              'rating': 10,
                                              'poster': 'https://www.amazon.com/Movie-Poster-Marvel-Holographic'
                                                        '-Authenticity/dp/B07Q1YWKD9',
                                              'genre': ["action", "thriller"]})

        film = Movie.query.filter_by(title='Test film 1').first()

        assert response.status_code == 200
        assert b"Add a new film below" and b"Submit" in response.data
        assert film


class TestClassSearch:
    def test_search_get(self, test_client):
        """
        WHEN the '/search' page is requested (GET) - wrong method
        THEN the response is method not allowed
        """
        response = test_client.get('/search')

        assert response.status_code == 405
        assert b"Add a new film below" not in response.data

    def test_search_post(self, test_client):
        """
        WHEN the '/search' page is requested (POST)
        THEN the response is a valid redirection
        """
        response = test_client.post('/search')

        assert response.status_code == 302
        assert b"You should be redirected automatically to the target URL:" in response.data
        assert b"Add a new film below" not in response.data

    def test_search_query(self, test_client):
        """
        WHEN the '/search/<search_query>' page is requested (POST)
        THEN all films with titles matching the search query are found
        """
        response = test_client.get('/search/mad')
        print(response.data)
        assert response.status_code == 200
        assert b'Added by User' and b'Mad Max' in response.data
        assert b'Search' in response.data


class TestClassFilter:
    def test_filter_genre(self, test_client):
        """
        WHEN the '/filter' page is requested (POST)
        THEN the response filters films according to the request
        """
        app = create_app()

        with app.test_client() as client:
            response = client.post('/filter', data={'genre': 'Comedy', 'submit1': True})

        assert response.status_code == 200
        assert b'Added by User' and b'Home Alone' in response.data
        assert b'Home' in response.data

    def test_filter_year(self, test_client):
        """
        WHEN the '/filter' page is requested (POST)
        THEN the response filters films according to the request
        """
        response = test_client.post('/filter', data={'start_year': '1992', 'end_year': '1994', 'submit2': True})

        assert response.status_code == 200
        assert b'Added by User' and b'Ninja Scroll' in response.data
        assert b'Home' in response.data

    def test_filter_director(self, test_client):
        """
        WHEN the '/filter' page is requested (POST)
        THEN the response filters films according to the request
        """
        response = test_client.post('/filter', data={'director': 'George Miller', 'submit3': True})

        assert response.status_code == 200
        assert b'Added by User' and b'Mad Max' in response.data
        assert b'Home' in response.data


class TestClassSort:
    def test_sort_rating(self, test_client):
        """
        WHEN sorting page is requested
        THEN this page redirects to a list of films sorted correctly
        """
        response = test_client.post('/sort', data={'algo': 'rating', 'asc': '', 'sort_submit': True})
        assert response.status_code == 302
        assert b'<a href="/sorted_films/rating">' in response.data

    def test_sort_rating_asc(self, test_client):
        """
        WHEN sorting page is requested
        THEN this page redirects to a list of films sorted correctly
        """
        response = test_client.post('/sort', data={'algo': 'rating', 'asc': True, 'sort_submit': True})

        assert response.status_code == 302
        assert b'<a href="/sorted_films/rating_asc">' in response.data

    def test_sort_year(self, test_client):
        """
        WHEN sorting page is requested
        THEN this page redirects to a list of films sorted correctly
        """
        response = test_client.post('/sort', data={'algo': 'year', 'asc': True, 'sort_submit': True})

        assert response.status_code == 302
        assert b'<a href="/sorted_films/year_asc">' in response.data

    def test_sort_year_asc(self, test_client):
        """
        WHEN sorting page is requested
        THEN this page redirects to a list of films sorted correctly
        """
        response = test_client.post('/sort')

        assert response.status_code == 302
        assert b'<a href="/sorted_films/year">' in response.data

    def test_sorted_rating(self, test_client):
        """
        WHEN page with films sorted by rating is requested
        THEN this page returned with code 200
        """
        response = test_client.get('/sorted_films/rating')

        assert response.status_code == 200
        assert b'Added by User' and b'Rating' and b'Home' in response.data

    def test_sorted_rating_asc(self, test_client):
        """
        WHEN page with films sorted by rating (asc) is requested
        THEN this page returned with code 200
        """
        response = test_client.get('/sorted_films/rating_asc')

        assert response.status_code == 200
        assert b'Added by User' and b'Rating' and b'Home' in response.data

    def test_sorted_year(self, test_client):
        """
        WHEN page with films sorted by year is requested
        THEN this page returned with code 200
        """
        response = test_client.get('/sorted_films/year')

        assert response.status_code == 200
        assert b'Added by User' and b'Rating' and b'Home' in response.data

    def test_sorted_year_asc(self, test_client):
        """
        WHEN page with films sorted by year (asc) is requested
        THEN this page returned with code 200
        """
        response = test_client.get('/sorted_films/year_asc')
        print(response.data)

        assert response.status_code == 200
        assert b'Added by User' and b'Rating' and b'Home' in response.data


class TestClassLogin:
    def test_login_get(self, test_client):
        """
        WHEN a login page is requested
        THEN return it with 200 code
        """
        response = test_client.get('/login')

        assert response.status_code == 200
        assert b'Login' and b'Username' and b'Password' in response.data

    def test_login_post_valid_user(self, test_client):
        """
        WHEN an existing user tries to log in
        THEN redirect him to home page
        """
        response = test_client.post('/login', data={'username': 'admin', 'password': '1234567'})

        assert response.status_code == 302
        assert b">/</a>." in response.data

    def test_login_post_invalid_username(self, test_client):
        """
        WHEN user that doesn't exist tries to log in
        THEN redirect back to login page
        """
        response = test_client.post('/login', data={'username': 'idontexist', 'password': '123456hjh7'})

        assert response.status_code == 302
        assert b"/login?" and b"AnonymousUserMixin" in response.data

    def test_login_post_invalid_password(self, test_client):
        """
        WHEN user tries to log in with wrong password
        THEN redirect back to login page
        """
        response = test_client.post('/login', data={'username': 'admin', 'password': '123456hjh7'})

        assert response.status_code == 302
        assert b"/login?" and b"AnonymousUserMixin" in response.data

    def test_logout(self, test_client):
        """
        WHEN user logs out
        THEN he is redirected to login page
        """
        response = test_client.get('logout')

        assert response.status_code == 302
        assert b'/login' in response.data


class TestClassSignUp:
    def test_signup_get(self, test_client):
        """
        WHEN sign-up page is requested
        THEN it is returned with 200 code
        """
        response = test_client.get('/signup')

        assert response.status_code == 200
        assert b'Login' and b'Username' and b'Password' and b'Confirm password' in response.data

    def test_signup_post(self, test_client, new_user_form):
        """
        WHEN a post request on /signup is sent with new valid user data
        THEN user is  redirected to login page
        """
        response = test_client.post('/signup', data=new_user_form)

        assert User.query.filter_by(username='userpytest')

        # this part deletes created user
        app = create_app()
        with app.app_context():
            user = User.query.filter_by(username=new_user_form['username']).first()
            if user:
                db.session.delete(user)
                db.session.commit()
        assert not User.query.filter_by(username=new_user_form['username']).first()

        assert response.status_code == 302
        assert b'/login' in response.data

    def test_signup_post_existing_email(self, test_client):
        """
        WHEN a post request on /signup is sent with existing email
        THEN the redirect back to sign in page
        """
        response = test_client.post('/signup', data={'username': 'new_user444',
                                                     'email': 'ilyagvv@gmail.com',
                                                     'password': '1234567'})

        assert response.status_code == 302
        assert b' <a href="/signup">/signup</a>' in response.data

    def test_signup_post_existing_name(self, test_client):
        """
        WHEN a post request on /signup is sent with existing username
        THEN the redirect back to sign in page
        """
        response = test_client.post('/signup', data={'username': 'admin',
                                                     'email': 'new56565@gmail.com',
                                                     'password': '1234567'})

        assert response.status_code == 302
        assert b' <a href="/signup">/signup</a>' in response.data


class TestClassEdit:
    def test_edit_post(self, test_client):
        """
        WHEN valid user tries to edit film
        THEN film is edited successfully
        """
        app = create_app()
        app.test_client_class = FlaskLoginClient

        user = User.query.filter_by(username='admin').first()
        film = Movie.query.filter_by(title='Test film 1').first()
        with app.test_client(user=user) as client:
            client.post(f'edit/{film.id}', data={'title': 'Test film_edited', 'director': 'Test director_edited',
                                                 'year_release': '2010', 'description': 'Test description_edited',
                                                 'rating': 10,
                                                 'poster': 'https://www.amazon.com/Movie-Poster-Marvel-Holographic'
                                                           '-Authenticity/dp/B07Q1YWKD9',
                                                 'genre': ['action', 'thriller', 'drama']})

        assert Movie.query.filter_by(title='Test film_edited').first()

    def test_edit_post_invalid_user(self, test_client):
        """
        WHEN invalid user tries to edit film (invalid means the one that didn't add the film to a database)
        THEN user is redirected to home
        """
        app = create_app()
        app.test_client_class = FlaskLoginClient

        user = User.query.filter_by(username='user1').first()

        with app.test_client(user=user) as client:
            response = client.get(f'edit/1')

        assert response.status_code == 302
        assert b'<a href="/">/</a>' in response.data

    def test_edit_get_correct_user(self, test_client):
        """
        WHEN valid user tries to edit film (valid = the one that added a film or admin)
        THEN user is redirected to /edit page
        """
        app = create_app()
        app.test_client_class = FlaskLoginClient

        user = User.query.filter_by(username='admin').first()
        with app.test_client(user=user) as client:
            response = client.get('edit/1')

        assert response.status_code == 200
        assert b'You can edit a film below' in response.data


class TestClassDelete:
    def test_delete_valid_user(self, test_client):
        """
        WHEN valid user tries to delete a film (valid = the one that added a film or admin)
        THEN film is deleted
        """
        app = create_app()
        app.test_client_class = FlaskLoginClient

        user = User.query.filter_by(username='admin').first()
        with app.test_client(user=user) as client:
            film = Movie.query.filter_by(title='Test film_edited').first()
            client.get(f'/delete/{film.id}')

        assert not Movie.query.filter_by(title='Test film_edited').first()

    def test_delete_invalid_user(self, test_client):
        """
        WHEN invalid user tries to edit film
        THEN film is not deleted
        """
        app = create_app()
        app.test_client_class = FlaskLoginClient

        user = User.query.filter_by(username='user1').first()
        with app.test_client(user=user) as client:
            response = client.get(f'/delete/{1}')

        assert Movie.query.filter_by(id=1).first()
        assert response.status_code == 200

    def test_delete_no_user(self, test_client):
        """
        WHEN there is a delete request with specified movie id
        THEN redirect to home URL, film is not deleted
        """
        response = test_client.get('/delete/1')

        film = Movie.query.filter_by(id=1).first()

        assert response.status_code == 302
        assert film
        assert b"Redirecting" and b">/</a>" in response.data
