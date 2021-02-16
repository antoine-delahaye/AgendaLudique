from . import mail
import click


@mail.cli.command('sendMail')
@click.argument('email')
def send_mail(email):
    """
   envoie un mail de test à l'adresse mentionnée
    """
    from app import mail
    from flask import current_app
    with current_app.test_request_context("localhost.com"):
        mail.send_mail("Testing mail sending", email, 'testing.html', url="google.com")
        print("mail successfully sent to " + email)


@mail.cli.command('sendResetMail')
@click.argument('email')
def send_reset_mail(email):
    """
    envoie un mail de reset password à l'adresse mentionnée
    """
    from app import mail
    from flask import current_app
    with current_app.test_request_context("localhost.com"):
        mail.send_mail("Testing reset password", email, 'password_forgot_mail.html', url="google.com")
        print("mail successfully sent to " + email)
