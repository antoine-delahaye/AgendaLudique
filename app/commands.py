import click
from flask import Blueprint

# bp qui permet l'administration de l'application
admin_blueprint = Blueprint('admin', __name__)


@admin_blueprint.cli.command('resetDB')
def reset_db():
    """ réinitialise la base de données """
    pass


@admin_blueprint.cli.command('sendMail')
@click.argument('email')
def send_mail(email):
    """
   envoie un mail de test à l'adresse mentionnée
    """
    from . import mail
    mail.send_mail("Testing mail sending", email, 'mails/testing.html', url="google.com")
    print("mail successfully sent to " + email)
