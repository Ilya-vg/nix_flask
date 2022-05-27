from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db, get_db_connection
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    s = 'SELECT title FROM movie'
    cur.execute(s)
    list_movies = cur.fetchall()
    return render_template('home.html', list_movies=list_movies, user=current_user)


@views.route('/delete-movie', methods=['POST'])
def delete_note():
    return 'Delete movie'
