# app/auth/views.py

from flask import redirect, render_template, url_for, flash, request
from flask_login import login_required, login_user, logout_user

from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordForm, ForgotPasswordForm
from app import db
from app.models import User  # , Statistic
import uuid


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
    """
    flashes all users errors during registration
    :param form: which contains user inputs
    """
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


# TODO à déplacer dans un model
def generate_reset_mail(user):
    """
    sends user reset password mail + generate his token
    :param user: User have to reset his password
    :return: None
    """
    from .. import mail

    if not user:  # user with email not found
        return
    token = uuid.uuid4().hex
    user.token_pwd = token
    db.session.commit()

    mail.send_mail("Demande réinitialisation mot de passe", user.email, "mails/password_forgot_mail.html", user=user,
                   url=request.url_root[:-1] + url_for("auth.forgot_password") + "/" + token)


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
        flash("success", "Un mail vous a été envoyé pour réinitialiser votre mot de passe")
        return redirect(url_for("auth.login"))

    return render_template("password_forgot.html", form=form, stylesheet="register")


# TODO move it to models

def user_change_password(user, newpassword):
    """
    :param user: user to  change password
    :param newpassword: new pwd
    :return: none
    """
    user.password = newpassword
    db.session.commit()


@auth.route('/forgot_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Where the user changes his password
    """
    form = ResetPasswordForm()
    user = User.query.filter_by(token_pwd=token).first_or_404()
    if form.validate_on_submit():
        if user:
            user_change_password(user, form.password.data)
            flash("success", "Votre mot de passe a bien été modifié")
            return redirect(url_for("auth.login"))
    elif not user:
        flash("danger", "Votre lien a expiré, veuillez en générer un nouveau")
        return redirect(url_for("auth.forgot_password"))
    return render_template("password_reset.html", form=form, stylesheet="register")
