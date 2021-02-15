# app/auth/views.py

from flask import redirect, render_template, url_for, flash
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
        else:
            flash("warning", "Adresse électronique ou mot de passe invalide.")
    return render_template('login.html', form=form, stylesheet='login')


def check_register_error(form):
    if not User.query.filter_by(email=form.email.data):
        flash("danger", "Adresse mail déjà utilisée")

    if not User.query.filter_by(username=form.username.data) is not None:
        flash("danger", "Nom d'utilisateur déjà utilisé")


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
        flash("Inscription réussite, vous pouvez maintenant vous connecter !")
        mail.send_mail("Confirmation inscription", form.email.data, "mails/registerMail.html", user=user,
                       url=request.url_root)
        return redirect(url_for('auth.login'))
    else:
        check_register_error(form)
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


@auth.route('/forgotpassword')
def forgotpassword():
    """
    Allows the user to reset his password
    Send him an email with his new mail
    """

    return redirect(url_for('site.home'))
