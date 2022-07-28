from project import app, db, User
from project.models import Movie

client = app.test_client()

auth_header = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9'
                                '.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY1ODky'
                                'MDcwOSwianRpIjoiMjA5MmZhZTMtNzNlZC00M'
                                'TA3LTgyNTMtYTliOTEwMWE4OTUwIiwidHlw'
                                'ZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjo'
                                'xNjU4OTIwNzA5LCJleHAiOjE2NTk1MjU1MDl9'
                                '.MBhdKgQnM9Jey0v6SGTJioLQslHDtwKXBmCcVRRG68o '}

user1_header = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9'
                                 '.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY1ODkzNzMxN'
                                 'iwianRpIjoiZDBhM2IxOGUtYjQxNS00YzMxLTk2YmQ'
                                 'tMTEzZWQ2NTIwZDBiIiwidHlwZSI6ImFjY2VzcyIsI'
                                 'nN1YiI6MTQxLCJuYmYiOjE2NTg5MzczMTYsImV4cCI6'
                                 'MTY1OTU0MjExNn0.Gwge7TXkFiYsS8iiacMKkqhM4UF'
                                 'LQjoRcVcoRXoBwN8'}


class TestAuth:
    """
    test authentication functions: whoami, login, signup
    """
    def test_whoami(self, test_client):
        response = test_client.get('/api/auth/whoami', headers=auth_header)

        assert response.status_code == 200
        assert b'id' and b'username' and b'email' in response.data

    def test_signup(self, new_api_user_data,
                    test_client, user_email_exists,
                    user_name_exists):

        response = test_client.post('/api/auth/signup', json=new_api_user_data)
        user = User.query.filter_by(username=new_api_user_data['username']).first()

        assert user
        assert response.status_code == 200

        # attempt to sign up a user with existing email
        response = test_client.post('/api/auth/signup', json=user_email_exists)

        assert response.status_code == 200
        assert b'User with this email already exists.'

        # attempt to sign up a user with existing email
        response = test_client.post('/api/auth/signup', json=user_name_exists)

        assert response.status_code == 200
        assert b'User with this name already exists.'

    def test_login(self, new_api_user_data, test_client):
        response = test_client.post('/api/auth/login', json={
            'username': 'admin', 'password': '1234567'})

        assert response.status_code == 200
        assert b'ey' in response.data

        user = User.query.filter_by(username=new_api_user_data['username']).first()
        with client:
            db.session.delete(user)
            db.session.commit()

        assert not User.query.filter_by(username=new_api_user_data['username']).first()

        response = test_client.post('/api/auth/login', json={
            'username': 'admin', 'password': 'invalid'})

        assert response.status_code == 200
        assert b'Wrong username or password' in response.data


class TestFilm:
    def test_get(self, test_client):
        response = test_client.get('/api/films/1')

        assert response.status_code == 200
        assert b'Mad Max' in response.data

        # try with id that doesn't exist
        response = test_client.get('/api/films/878787')

        assert response.status_code == 404
        assert b'No film with provided id exists in the database.' in response.data

    def test_put(self, test_client):
        test_client.put('/api/films/1', json={'rating': '5'}, headers=auth_header)

        with client:
            film = Movie.query.filter_by(id=1).first()

        assert film.rating == 5

        response = test_client.put('/api/films/7878787', json={
            'rating': '5'}, headers=auth_header)

        assert response.status_code == 404
        assert b'No film with provided id exists in the database.' in response.data

        # changing the rating back to the initial one
        test_client.put('/api/films/1', json={'rating': '9'}, headers=auth_header)

        response = test_client.put('/api/films/1', json={'rating': '5'}, headers=user1_header)

        assert b'Only a user that added film in' in response.data

        # test changing genres of a film
        test_client.put('/api/films/1', json={'genres': ['comedy']}, headers=auth_header)

        with client:
            film = Movie.query.filter_by(id=1).first()
        film_genres = list(map(str, film.genres))

        assert 'comedy' in film_genres
        assert 'action' not in film_genres

        test_client.put('/api/films/1', json={'genres': ['action', 'drama']}, headers=auth_header)

    # this function tests both adding and deleting methods of API
    def test_add_delete(self, test_client, new_film_form):
        response = test_client.post('api/films/add', json=new_film_form, headers=auth_header)
        with client:
            film = Movie.query.filter_by(title=new_film_form['title']).first()

        assert film
        assert b'was added successfully.' in response.data

        test_client.delete(f'api/films/{film.id}', headers=auth_header)

        assert not Movie.query.filter_by(title=new_film_form['title']).first()

        response = test_client.delete(f'api/films/7878787', headers=auth_header)

        assert response.status_code == 404
        assert b'No film with provided id exists in the database.' in response.data

        response = test_client.delete('/api/films/1', headers=user1_header)

        assert b'if you were the user that added it' in response.data
        assert response.status_code == 400

        # try to add film without all required fields
        response = test_client.post('api/films/add', json={'title': 'Fake Film'}, headers=auth_header)

        assert response.status_code == 400
        assert b'Please provide the following' in response.data

    def test_list(self, test_client):
        response = test_client.get('api/films/')

        assert b'Mad Max' in response.data
        assert response.status_code == 200

    def test_search(self, test_client):
        response = test_client.get('api/films/search', json={'query': 'ninja'}, headers=auth_header)

        assert response.status_code == 200
        assert b'Ninja Scroll' in response.data

    def test_filter(self, test_client):
        response = test_client.get('api/films/filter', json={
            'algo': 'year', 'start_year': 1990, 'end_year': 1990}, headers=auth_header)

        assert response.status_code == 200
        assert b'Home Alone' in response.data

        response = test_client.get('api/films/filter', json={
            'algo': 'genre', 'genre': 'comedy'}, headers=auth_header)

        assert response.status_code == 200
        assert b'Home Alone' in response.data

        response = test_client.get('api/films/filter', json={
            'algo': 'director', 'director': 'miller'}, headers=auth_header)

        assert response.status_code == 200
        assert b'Mad Max' in response.data

        response = test_client.get('api/films/filter', json={
            'algo': 'invalid', 'director': 'miller'}, headers=auth_header)

        assert response.status_code == 400
        assert b'Unknown filtering condition.' in response.data

    def test_sort(self, test_client):
        # sort by rating, descending order
        response = test_client.get('api/films/sort', json={
            'algo': 'rating', 'desc': True}, headers=auth_header)

        assert response.status_code == 200
        assert b'Ninja Scroll' and b'Mad Max' in response.data

        # sort by rating, ascending order
        response = test_client.get('api/films/sort', json={
            'algo': 'rating', 'desc': False}, headers=auth_header)

        assert response.status_code == 200
        assert b'Ninja Scroll' and b'Mad Max' in response.data

        # sort by year of release, descending order
        response = test_client.get('api/films/sort', json={
            'algo': 'year', 'desc': True}, headers=auth_header)

        assert response.status_code == 200
        assert b'Ninja Scroll' and b'Mad Max' in response.data

        # sort by year of release, ascending order
        response = test_client.get('api/films/sort', json={
            'algo': 'year', 'desc': False}, headers=auth_header)

        assert response.status_code == 200
        assert b'Ninja Scroll' and b'Mad Max' in response.data

        # here the wrong sorting algo is provided
        response = test_client.get('api/films/sort', json={
            'algo': 'invalid', 'desc': True}, headers=auth_header)

        assert response.status_code == 200
        assert b'Please provide valid json data for sorting' in response.data
