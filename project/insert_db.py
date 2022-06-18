import os
import psycopg2
from werkzeug.security import generate_password_hash

conn = psycopg2.connect(
    host="localhost",
    database="flask_movies",
    user=os.environ['DB_USERNAME'],
    password=os.environ['DB_PASSWORD'])

genres = ['action', 'thriller', 'comedy', 'drama', 'sci-fi']

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

cur.execute('DROP TABLE IF EXISTS movie CASCADE;')
cur.execute('CREATE TABLE movie (id serial PRIMARY KEY UNIQUE,'
            'title varchar (255) NOT NULL,'
            'director varchar (255),'
            'release_year int NOT NULL,'
            'description varchar (4000),'
            'rating int NOT NULL,'
            'poster varchar (255),'
            'user_added varchar (255) NOT NULL);'
            )

cur.execute('DROP TABLE IF EXISTS genre CASCADE;')
cur.execute('CREATE TABLE genre (id serial PRIMARY KEY UNIQUE,'
            'genre varchar (255));'
            )

# cur.execute('INSERT INTO genre (genre) VALUES action', )

for i in genres:
    SQL = "INSERT INTO genre (genre) VALUES (%s);"
    data = (i, )
    cur.execute(SQL, data)

cur.execute('DROP TABLE IF EXISTS movie_genre;')
cur.execute('CREATE TABLE movie_genre (genre_id int REFERENCES genre(id),'
            'movie_id int REFERENCES movie(id));'
            )


conn.commit()

cur.close()
conn.close()
