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
    from flask import current_app
    with current_app.test_request_context("localhost.com"):
        mail.send_mail("Testing mail sending", email, 'mails/testing.html', url="google.com")
        print("mail successfully sent to " + email)


from app import db


@admin_blueprint.cli.command('syncdb')
def syncdb():
    """ Creates all missing tables """
    db.create_all()


import yaml
from app.models import User, Game, BookmarkUser, HideUser


@admin_blueprint.cli.command('loaddb_games')
@click.argument('filename')
def loaddb_games(filename):
    """ Populates the database with games from a yml file """
    games = yaml.safe_load(open(filename))

    cpt = 0
    for game in games.values():
        if len(game["title"]) <= 64: #
            o = Game(
                title=game["title"],
                publication_year=game["publication_year"],
                min_players=game["min_players"],
                max_players=game["max_players"],
                min_playtime=game["min_playtime"],
                image=game["images"]["original"])
            db.session.add(o)
        else:
            print(game["title"], " - ", len(game["title"]))
            cpt += 1
    db.session.commit()
    print("Nombre de jeux rejetés : ", cpt)


@admin_blueprint.cli.command('loaddb_users')
@click.argument('filename')
def loaddb_users(filename):
    """ Populates the database with users and user-related relationships from a yml file """
    users = yaml.safe_load(open(filename))

    # premier tour de boucle, creation des users

    dico_users = dict()
    for u in users:
        o = User(
            email=u["email"],
            username=u["username"],
            first_name=u["first_name"],
            last_name=u["last_name"],
            password=u["password"],
            profile_picture=u["profile_picture"])
        db.session.add(o)
        dico_users[u["username"]] = o
    db.session.commit()

    # deuxieme tour de boucle, creation des relations UserXGame et UserXUser
    for u in users:
        u_id = dico_users[u["username"]].id
        for u2 in u["bookmarked_users"]:
            o = BookmarkUser(
                user_id=u_id,
                user2_id=dico_users[u2].id)
            db.session.add(o)
        for u2 in u["hidden_users"]:
            o = HideUser(
                user_id=u_id,
                user2_id=dico_users[u2].id)
            db.session.add(o)
    db.session.commit()
