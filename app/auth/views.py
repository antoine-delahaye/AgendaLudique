# app/auth/views.py

from flask import redirect, render_template, url_for, flash, request
from flask_login import login_required, login_user, logout_user

from app import db
from app.auth import auth
from app.auth.models.auth_tools import send_register_mail, generate_reset_mail, \
    user_change_password
from app.auth.models.forms import LoginForm, RegistrationForm, ResetPasswordForm, ForgotPasswordForm
from app.models import User  # , Statistic


@auth.route('/log', methods=['GET', 'POST'])
def login():
    """
    Handle requests to the /login route
    Log an user in through the login form
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            if user.verify_password(form.password.data):
                login_user(user)
                next = request.args.get("next")
                if next is not None:
                    return redirect(next)
                return redirect(url_for("jeux.catalog"))
            else:
                flash("Mot de passe incorrect.", "warning")
        else:
            flash("Adresse électronique inéxistante.", "warning")
    return render_template('login.html', form=form, stylesheet='login')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle requests to the /register route
    Add an user to the database through the registration form
    """

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
        flash("Inscription réussite, vous pouvez maintenant vous connecter !", "success")
        send_register_mail(user)
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


@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """
    Allows the user to request for a reset on his password
    Send him an email with his new mail
    """
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        generate_reset_mail(user)
        flash("Un mail vous a été envoyé pour réinitialiser votre mot de passe", "success")
        return redirect(url_for("auth.login"))
    return render_template("password_forgot.html", form=form, stylesheet="register")


@auth.route('/forgot_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Where the user changes his password
    """
    form = ResetPasswordForm()
    user = User.from_token(token)
    if not user:
        flash("Votre lien a expiré, veuillez en générer un nouveau", "danger")
        return redirect(url_for("auth.forgot_password"))
    if form.validate_on_submit():
        if user:
            user_change_password(user, form.password.data)
            flash("Votre mot de passe a bien été modifié", "success")
            return redirect(url_for("auth.login"))
    return render_template("password_reset.html", form=form, stylesheet="register")
