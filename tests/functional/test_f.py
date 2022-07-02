def test_home_get(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/')
    assert response.status_code == 200
    assert b"Home" in response.data
    assert b"Add a new film below" in response.data
    assert b"Added by User" in response.data
    assert b"Search" in response.data
    assert b"Filter by genre" in response.data
    assert b"Film genre (one or multiple):" in response.data


def test_home_post(test_client, new_film_form):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (POST)
    THEN check that the response is valid
    """
    response = test_client.post('/')
    print(response)
    assert response.status_code == 200
    assert b"Add a new film below" in response.data
    assert b"Submit" in response.data


def test_search_get(test_client):
    response = test_client.get('/search')

    assert response.status_code == 405
    assert b"Add a new film below" not in response.data


def test_search_post(test_client):
    response = test_client.post('/search')

    assert response.status_code == 302
    assert b"You should be redirected automatically to the target URL:" in response.data
    assert b"Add a new film below" not in response.data


# def test_search_post_302(test_client):
#     response = test_client.post('/search')
#
#     assert response.status_code == 302
#     assert b"Add a new film below" not in response.data


def test_search_query(test_client):
    response = test_client.get('/search/mad')
    assert response.status_code == 200
    assert b'Added by User' in response.data
    assert b'Search' in response.data


def test_filter(test_client):
    response = test_client.post('/filter')

    assert response.status_code == 200
    assert b'Added by User' and b'Rating' in response.data
    assert b'Home' in response.data


def test_sort(test_client):
    response = test_client.post('/sort')

    assert response.status_code == 302
    assert b"You should be redirected automatically to the target URL:" in response.data


def test_sorted_rating(test_client):
    response = test_client.get('/sorted_films/rating')

    assert response.status_code == 200
    assert b'Added by User' and b'Rating' and b'Home' in response.data


def test_sorted_rating_asc(test_client):
    response = test_client.get('/sorted_films/rating')

    assert response.status_code == 200
    assert b'Added by User' and b'Rating' and b'Home' in response.data


def test_sorted_year(test_client):
    response = test_client.get('/sorted_films/rating')

    assert response.status_code == 200
    assert b'Added by User' and b'Rating' and b'Home' in response.data


def test_sorted_year_asc(test_client):
    response = test_client.get('/sorted_films/rating')

    assert response.status_code == 200
    assert b'Added by User' and b'Rating' and b'Home' in response.data


def test_delete(test_client):
    response = test_client.get('/delete/1')

    assert response.status_code == 302
    assert b"You should be redirected automatically to the target URL:" in response.data
