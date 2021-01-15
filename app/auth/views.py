# app/auth/views.py

from flask import redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user

from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm
from app import db
from app.models import User  # , Statistic


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle requests to the /login route
    Log an user in through the login form
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(
                form.password.data):
            login_user(user)
            return redirect(url_for('site.catalog'))
    return render_template('login.html', form=form, stylesheet='login')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle requests to the /register route
    Add an user to the database through the registration form
    """
    from .. import mail
    from flask import request
    form = RegistrationForm()
    if form.validate_on_submit():
        # stats = Statistic()
        user = User(email=form.email.data,
                    username=form.username.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    password=form.password.data,
                    # statistics_id=stats.id,
                    )
        db.session.add(user)
        db.session.commit()
        mail.send_mail("Confirmation inscription", form.email.data, "mails/registerMail.html", user=user,
                       url=request.base_url)
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form, stylesheet='register')


@auth.route('/logout')
@login_required
def logout():
    """
    Handle requests to the /logout route
    Logout an user out through the logout link
    """
    logout_user()
    return redirect(url_for('site.home'))
