import uuid

from flask import flash, request, url_for

from app import db
from app.models import User


def check_register_error(form):
    """
    flashes all users errors during registration
    :param form: which contains user inputs
    """
    if not User.from_email(form.email.data):
        flash("Adresse mail déjà utilisée", "danger")

    if User.from_username(form.username.data) is None:
        flash("Nom d'utilisateur déjà utilisé", "danger")


def send_register_mail(user):
    """
    send a registration mail
    :param user: user to send
    """
    from app import mail

    mail.send_mail("Confirmation inscription", user.email, "registerMail.html", user=user,
                   url=request.url_root)


def get_user_token():
    """
    :return: a token used to reset user password
    """
    return uuid.uuid4().hex


def generate_reset_mail(user):
    """
    sends user reset password mail + generate his token
    :param user: User have to reset his password
    :return: None
    """
    from app import mail

    if not user:  # user with email not found
        return
    token = get_user_token()
    user.token_pwd = token
    db.session.commit()

    mail.send_mail("Demande réinitialisation mot de passe", user.email, "password_forgot_mail.html", user=user,
                   url=request.url_root[:-1] + url_for("auth.forgot_password") + "/" + token)


def user_change_password(user, newpassword):
    """
    :param user: user to  change password
    :param newpassword: new pwd
    :return: none
    """
    user.password = newpassword
    db.session.commit()
