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
from app.models import User, Game, BookmarkUser, HideUser, Note, Wish, KnowRules, Collect, Prefer


@admin_blueprint.cli.command('loaddb_games')
@click.argument('filename')
def loaddb_games(filename):
    """ Populates the database with games from a yml file """
    games = yaml.safe_load(open(filename))

    # creation d'un profil BGG
    bgg = User.from_username("BGG")
    if bgg == None:
        bgg = User(
            email="mmm.dupuis45@gmail.com",
            username="BGG",
            first_name="Board Game",
            last_name="Geek",
            password="BGGdu45",
            profile_picture="https://cf.geekdo-static.com/images/logos/navbar-logo-bgg-b2.svg")
        db.session.add(bgg)
        db.session.commit()

    # premier tour de boucle, creation des jeux
    nb_jeux_regetes = 0
    for game in games.values():
        if len(game["title"]) <= 64 and Game.from_title(game["title"]) == None: #
            o = Game(
                title=game["title"],
                publication_year=game["publication_year"],
                min_players=game["min_players"],
                max_players=game["max_players"],
                min_playtime=game["min_playtime"],
                image=game["images"]["original"])
            db.session.add(o)
            print("V", game["title"])
        else:
            print("X", game["title"])
            nb_jeux_regetes += 1
    db.session.commit()

    # deuxieme tour de boucle pour les notes de bgg
    for game in games.values():
        g = Game.from_title(game["title"])
        if g != None and Note.from_both_ids(bgg.id,g.id) == None:
            rating = Note(
                note=round(game["average_rating"]),
                message="Auto-generated note, the average rating of the game at boardgamegeek.com",
                user_id=bgg.id,
                game_id=g.id)
            db.session.add(rating)
            print("V Note pour : ", game["title"])
        else:
            print("X Note pour :", game["title"])
    db.session.commit()

    print("Nombre de jeux rejetés : ", nb_jeux_regetes)


@admin_blueprint.cli.command('loaddb_users')
@click.argument('filename')
def loaddb_users(filename):
    """ Populates the database with users and user-related relationships from a yml file """
    users = yaml.safe_load(open(filename))

    # premier tour de boucle, creation des users
    for u in users:
        if User.from_username(u["username"]) == None:
            o = User(
                email=u["email"],
                username=u["username"],
                first_name=u["first_name"],
                last_name=u["last_name"],
                password=u["password"],
                profile_picture=u["profile_picture"])
            db.session.add(o)
            print("V", u["username"])
        else:
            print("X", u["username"])
    db.session.commit()

    # deuxieme tour de boucle, creation des relations UserXGame et UserXUser
    for u in users:
        u_id = User.from_username(u["username"]).id # existe forcement
        for u2 in u["bookmarked_users"]:
            u2_id = User.from_username(u2).id
            if BookmarkUser.from_both_ids(u_id,u2_id) == None:
                o = BookmarkUser(user_id=u_id, user2_id=u2_id)
                db.session.add(o)
                print("V BookmarkUser", u["username"], u2)
            else:
                print("X BookmarkUser", u["username"], u2)
        for u2 in u["hidden_users"]:
            u2_id = User.from_username(u2).id
            if HideUser.from_both_ids(u_id,u2_id) == None:
                o = HideUser(user_id=u_id, user2_id=u2_id)
                db.session.add(o)
                print("V HideUser", u["username"], u2)
            else:
                print("X HideUser", u["username"], u2)
        for g in u["wishes"]:
            g_id = Game.from_title(g).id
            if Wish.from_both_ids(u_id, g_id):
                o = Wish(user_id=u_id, game_id=g_id)
                db.session.add(o)
                print("V Wish", u["username"], g)
            else:
                print("X Wish", u["username"], g)
        for g in u["known"]:
            g_id = Game.from_title(g).id
            if KnowRules.from_both_ids(u_id, g_id) == None:
                o = KnowRules(user_id=u_id, game_id=g_id)
                db.session.add(o)
                print("V KnowRules", u["username"], g)
            else:
                print("X KnowRules", u["username"], g)
        for g in u["collection"]:
            g_id = Game.from_title(g).id
            if Collect.from_both_ids(u_id, g_id) == None:
                o = Collect(user_id=u_id, game_id=g_id)
                db.session.add(o)
                print("V Collect", u["username"], g)
            else:
                print("X Collect", u["username"], g)
        for pref in u["preferences"]:
            g_id = Game.from_title(pref["title"]).id
            if Prefer.from_both_ids(u_id, g_id) == None:
                o = Prefer(
                    user_id=u_id,
                    game_id=g_id,
                    frequency=pref["frequency"])
                db.session.add(o)
                print("V Prefer", u["username"], pref["title"])
            else:
                print("X Prefer", u["username"], pref["title"])
        for note in u["notes"]:
            Game.from_title(note["title"]).id
            if Note.from_both_ids(u_id, g_id) == None:
                o = Note(
                    user_id=u_id,
                    game_id=g_id,
                    note=note["note"],
                    message=note["message"])
                db.session.add(o)
                print("V Note", u["username"], note["title"])
            else:
                print("X Note", u["username"], note["title"])
    db.session.commit()
