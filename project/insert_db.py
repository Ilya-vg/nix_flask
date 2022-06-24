import os
import psycopg2
from werkzeug.security import generate_password_hash

conn = psycopg2.connect(
    host="localhost",
    database="flask_films",
    user=os.environ['DB_USERNAME'],
    password=os.environ['DB_PASSWORD'])

genres = ['action', 'thriller', 'comedy', 'drama', 'sci-fi']

# Open a cursor to perform database operations
cur = conn.cursor()

# Insert data into the table

# cur.execute('INSERT INTO users (username, email, password)'
#             'VALUES (%s, %s, %s);',
#             ('admin',
#              'ilyagvv@gmail.com',
#              generate_password_hash('12345678'))
#             )

for i in genres:
    SQL = "INSERT INTO genre (genre) VALUES (%s);"
    data = (i,)
    cur.execute(SQL, data)

cur.execute('INSERT INTO movie '
            '(title, director, year_release, description, rating, poster, added_by) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s);',
            ('Mad Max',
             'George Miller',
             '1979',
             'Mad Max is an Australian post-apocalyptic action film series',
             '8',
             'https://en.wikipedia.org/wiki/Mad_Max_(film)#/media/File:MadMazAus.jpg',
             'admin')
            )

cur.execute('INSERT INTO movie '
            '(title, director, year_release, description, rating, poster, added_by) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s);',
            ('Ninja Scroll',
             'Yoshiaki Kawajiri',
             '1993',
             'Ninja Scroll is a 1993 Japanese animated jidaigeki-chanbara film',
             '10',
             'https://en.wikipedia.org/wiki/Ninja_Scroll#/media/File:Ninja-Scroll-Poster.jpg',
             'admin')
            )

cur.execute('INSERT INTO movie_genre '
            '(genre_id, movie_id) '
            'VALUES (%s, %s);',
            ('1', '1')
            )

cur.execute('INSERT INTO movie_genre '
            '(genre_id, movie_id) '
            'VALUES (%s, %s);',
            ('4', '1')
            )

cur.execute('INSERT INTO movie_genre '
            '(genre_id, movie_id) '
            'VALUES (%s, %s);',
            ('1', '2')
            )

cur.execute('INSERT INTO movie_genre '
            '(genre_id, movie_id) '
            'VALUES (%s, %s);',
            ('4', '2')
            )

conn.commit()

cur.close()
conn.close()

