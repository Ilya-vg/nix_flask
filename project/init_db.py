import os
import psycopg2
from werkzeug.security import generate_password_hash

conn = psycopg2.connect(
    host="localhost",
    database="flask_movies",
    user=os.environ['DB_USERNAME'],
    password=os.environ['DB_PASSWORD'])

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
cur.execute('DROP TABLE IF EXISTS users;')
cur.execute('CREATE TABLE users (id serial PRIMARY KEY,'
            'username varchar (150) NOT NULL,'
            'email varchar (100) NOT NULL,'
            'password varchar (250) NOT NULL);'
            )

# Insert data into the table

cur.execute('INSERT INTO users (username, email, password)'
            'VALUES (%s, %s, %s)',
            ('admin',
             'ilyagvv@gmail.com',
             generate_password_hash('12345678'))
            )

cur.execute('DROP TABLE IF EXISTS movie;')
cur.execute('CREATE TABLE movie (id serial PRIMARY KEY UNIQUE,'
            'title varchar (255) NOT NULL,'
            'release_date date NOT NULL,'
            'description varchar (255),'
            'rating int,'
            'poster bytea,'
            'user_added varchar (255) NOT NULL);'
            )

cur.execute('DROP TABLE IF EXISTS genre;')
cur.execute('CREATE TABLE genre (id serial PRIMARY KEY UNIQUE,'
            'movie_id int);'
            )

cur.execute('DROP TABLE IF EXISTS director;')
cur.execute('CREATE TABLE director (id serial PRIMARY KEY UNIQUE,'
            'movie_id int);'
            )

cur.execute('DROP TABLE IF EXISTS movie_director;')
cur.execute('CREATE TABLE movie_director (id int references director(id),'
            'movie_id int references movie(id));'
            )

cur.execute('DROP TABLE IF EXISTS movie_genre;')
cur.execute('CREATE TABLE movie_genre (genre_id int references genre(id),'
            'movie_id int references movie(id));'
            )


conn.commit()

cur.close()
conn.close()
