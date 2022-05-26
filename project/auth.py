from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from . import get_db_connection
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, str(password)):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        conn = get_db_connection()
        cur = conn.cursor()

        if email:
            cur.execute(f"SELECT * FROM users WHERE email = '{email}'")
            if cur.fetchall():
                flash('User with this email already exists.', category='error')
                return redirect(url_for('views.home'))

        if not email or not username or not password1 or not password2:
            flash('Please make sure to fill in all fields.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(username) < 2:
            flash('Username must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            cur = conn.cursor()
            cur.execute('INSERT INTO users (username, email, password)'
                        'VALUES (%s, %s, %s)',
                        (username, email, generate_password_hash(
                            password1, method='sha256')))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)
