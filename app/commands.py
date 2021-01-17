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
        if len(game["title"]) <= 64 and Game.from_title(game["title"]) == None:  #
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
        if g != None and Note.from_both_ids(bgg.id, g.id) == None:
            rating = Note(
                note=round(game["average_rating"]),
                message="Auto-generated note, the average rating of the game at boardgamegeek.com",
                user_id=bgg.id,
                game_id=g.id)
            db.session.add(rating)
            print("V", Note, game["title"])
        else:
            print("X", Note, game["title"])
    db.session.commit()

    print("Nombre de jeux rejetés : ", nb_jeux_regetes)


def load_relationship(user, u_id, keyword_yml, rs, get_id, kw, list_kwsup=[], get_id_kw=""):
    for elem in user[keyword_yml]:
        if get_id_kw:
            elem_id = get_id(elem[get_id_kw]).id
        else:
            elem_id = get_id(elem).id
        if rs.from_both_ids(u_id,elem_id) == None:
            dico_kwsup = dict()
            for kwsup in list_kwsup:
                dico_kwsup[kwsup] = elem[kwsup]
            o = rs(user_id=u_id, **{kw: elem_id}, **dico_kwsup)
            db.session.add(o)
            print("V", rs, u_id, elem_id)
        else:
            print("X", rs, u_id, elem_id)


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
        relations_uxu = {"bookmarked_users": BookmarkUser, "hidden_users": HideUser}
        relations_uxg = {"wishes": Wish, "known": KnowRules, "collection": Collect}

        for kw_yml, rs in relations_uxu.items():
            load_relationship(u, u_id, kw_yml, rs, User.from_username, 'user2_id')
        get_id = Game.from_title
        kw = 'game_id'
        for kw_yml, rs in relations_uxg.items():
            load_relationship(u, u_id, kw_yml, rs , get_id, kw)
        get_id_kw = 'title'
        load_relationship(u, u_id, 'preferences', Prefer, get_id, kw, ['frequency'], get_id_kw)
        load_relationship(u, u_id, 'notes', Note, get_id, kw, ['note', 'message'], get_id_kw)
    db.session.commit()
