# Home Movie Database

Steps to start working with the app after you cloned this repo:

1. run **docker compose up -d**. This will run the app in detached mode.
2. get inside the running database container with the command **docker exec {container_id} psql -U postgres**
3. now check the **insert_db.py** file in a project directory. execute first sql command that is commented at the start of this file.
   it will add genres in genre table.
   
Now it's all set for you to run your dockerized copy of app on you machine. There's a /api URL with API functionality as well.

Note that insert_db.py also has more useful stuff that you can use to add test records to a database either via Python console or psql.
