from project import db, User, app, genres_list
from werkzeug.security import generate_password_hash
from project.models import Movie, MovieGenre


with app.app_context():
    # initialize database
    db.drop_all()
    db.create_all()

    # Insert data into the table
    db.session.add(User(username='admin',
                        email='ilyagvv@gmail.com',
                        password=generate_password_hash('1234567')))

    film = Movie(title='Mad Max',
                 director='George Miller',
                 year_release=1979,
                 description='Mad Max is an Australian post-apocalyptic action film series',
                 rating=9,
                 poster='https://en.wikipedia.org/wiki/Mad_Max_(film)#/media/File:MadMazAus.jpg',
                 added_by='admin')

    db.session.add(film)
    for g in ['action', 'drama']:
        db.session.add(MovieGenre(genres_list.index(g) + 1, film.id))

    film = Movie(title='Ninja Scroll',
                 director='Yoshiaki Kawajiri',
                 year_release=1993,
                 description='Ninja Scroll is a 1993 Japanese animated jidaigeki-chanbara film',
                 rating=10,
                 poster='https://en.wikipedia.org/wiki/Ninja_Scroll#/media/File:Ninja-Scroll-Poster.jpg',
                 added_by='admin')

    db.session.add(film)
    for g in ['action', 'thriller']:
        db.session.add(MovieGenre(genres_list.index(g) + 1, film.id))

    film = Movie(title='Mad Max: Fury Road',
                 director='George Miller',
                 year_release=2015,
                 description='In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler ',
                 rating=9,
                 poster='https://en.wikipedia.org/wiki/Mad_Max:_Fury_Road#/media/File:Mad_Max_Fury_Road.jpg',
                 added_by='admin')

    db.session.add(film)
    db.session.add(MovieGenre(genres_list.index('action') + 1, film.id))

    film = Movie(title='Home Alone',
                 director='Chris Columbus',
                 year_release=1990,
                 description='Home Alone is a 1990 American Christmas comedy film',
                 rating=8,
                 poster='https://en.wikipedia.org/wiki/Home_Alone#/media/File:Home_alone_poster.jpg',
                 added_by='admin')

    db.session.add(film)
    db.session.add(MovieGenre(genres_list.index('comedy') + 1, film.id))

    db.session.commit()

# SQL code to add genres

'''
INSERT INTO genre (genre)
VALUES 
        ('action'), ('thriller'), ('comedy'), ('drama'), ('sci-fi');
'''