# app/auth/views.py

from flask import flash, redirect, render_template, url_for, request
from flask_login import login_required, login_user, logout_user

from . import auth
from .forms import LoginForm, RegistrationForm
from .. import db
from ..models import User


@auth.route('/', methods=['GET', 'POST'])
def log_method():
    if request.method == 'POST':
        if request.form['auth-button'] == "login":
            return redirect(url_for('auth.login'))
        elif request.form['auth-button'] == 'register':
            return redirect(url_for('auth.register'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle requests to the /login route
    Log an employee in through the login form
    """
    form = LoginForm()
    if form.validate_on_submit():

        # check whether employee exists in the database and whether
        # the password entered matches the password in the database
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(
                form.password.data):
            # log employee in
            login_user(user)

            # redirect to the dashboard page after login
            return redirect(url_for('site.catalog'))

        # when login details are incorrect
        else:
            flash('Invalid email or password.')

    # load login template
    return render_template('login.html', form=form, stylesheet='login')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle requests to the /register route
    Add an user to the database through the registration form
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    password=form.password.data)

        # add employee to the database
        db.session.add(user)
        db.session.commit()
        flash('Votre inscription est finalisé, vous pouvez maintenant vous connecter')

        # redirect to the login page
        return redirect(url_for('auth.login'))

    # load registration template
    return render_template('register.html', form=form, stylesheet='register')


@auth.route('/logout')
@login_required
def logout():
    """
    Handle requests to the /logout route
    Log an employee out through the logout link
    """
    logout_user()
    flash('Vous êtes maintenant déconecté')

    # redirect to the login page
    return redirect(url_for('auth.login'))
