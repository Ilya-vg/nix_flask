from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

from . import db
from .models import User
from .forms import SignupForm, LoginForm

auth = Blueprint('auth', __name__)

from main import app


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                app.logger.info(f'User {user.username} logged in successfully.')
                return redirect(url_for('views.home'))

            flash('Incorrect password, try again.', category='error')
            app.logger.info('Failed login attempt: invalid password')
        else:
            flash('User with this name does not exist.', category='error')
            app.logger.info('Failed login attempt: invalid username')

        return redirect(url_for('auth.login', user=current_user))

    return render_template('login.html', user=current_user, form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    app.logger.info('User was logged out successfully.')
    return redirect(url_for('views.home'))


@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    form = SignupForm()

    if request.method == 'POST' and form.validate:

        username = form.username.data
        email = form.email.data
        password = form.password1.data

        by_email = User.query.filter_by(email=email).all()
        by_name = User.query.filter_by(username=username).all()

        if by_email:
            flash('User with this email already exists.', category='error')
            return redirect(url_for('auth.sign_up'))
        if by_name:
            flash('User with this name already exists.', category='error')
            return redirect(url_for('auth.sign_up'))

        user = User(username, email, generate_password_hash(password))

        db.session.add(user)
        db.session.commit()
        flash('You may log in with provided credentials.')

        app.logger.info(f'A new user with username {user.username} was created.')

        return redirect(url_for('auth.login'))

    return render_template("signup.html", user=current_user, form=form)
