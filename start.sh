#! /bin/bash

python init_db.py

exec pipenv gunicorn main:app --workers 3 --bind 0.0.0.0:5000