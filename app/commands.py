import click
from flask import Blueprint
from app import db
import time

# bp qui permet l'administration de l'application
admin_blueprint = Blueprint('admin', __name__)


@admin_blueprint.cli.command('resetDB')
def reset_db():
    """ Clear all the data of the database """
    for table in reversed(db.metadata.sorted_tables):
        print(f'Clear table {table}')
        db.session.execute(table.delete())
    db.session.commit()


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


import yaml
from app.models import User, Game, BookmarkUser, HideUser, Note, Wish, KnowRules, Collect, Prefer, Group, Participate, Genre, Classification


@admin_blueprint.cli.command('loaddb_games')
@click.argument('filename')
def loaddb_games(filename):
    """ Populates the database with games from a yml file """
    games = yaml.safe_load(open(filename))

    deb = time.perf_counter()
    # creation d'un profil BGG
    bgg = User.from_username("BGG")
    if bgg is None:
        bgg = User(
            email="mmm.dupuis45@gmail.com",
            username="BGG",
            first_name="Board Game",
            last_name="Geek",
            password="BGGdu45",
            profile_picture="https://cf.geekdo-static.com/images/logos/navbar-logo-bgg-b2.svg")
        db.session.add(bgg)
        db.session.commit()
    bgg_id = bgg.id

    # premier tour de boucle, creation des jeux et des genres
    nb_jeux_rejetes = 0
    for title, game in games.items():
        if len(title) <= 128 and Game.from_title(title) is None:
            game_object = Game(
                title=game["title"],
                publication_year=game["publication_year"],
                min_players=game["min_players"],
                max_players=game["max_players"],
                min_playtime=game["min_playtime"],
                image=game["images"]["original"])
            db.session.add(game_object)
            print("V", title)
        else:
            print("X", title)
            nb_jeux_rejetes += 1
        for typ in game["type"]: # creation des genres
            if Genre.from_name(typ) is None:
                genre_object = Genre(name=typ)
                db.session.add(genre_object)
    db.session.commit()

    # deuxieme tour de boucle pour les notes de bgg et les genres du jeu
    for title, game in games.items():
        g = Game.from_title(title)
        if g != None:
            g_id = g.id
            if Note.from_both_ids(bgg_id, g_id) is None:
                rating = Note(
                    note=round(game["average_rating"]),
                    message="Auto-generated note, the average rating of the game at boardgamegeek.com",
                    user_id=bgg_id,
                    game_id=g_id)
                db.session.add(rating)
                print("V", Note, title)
            else:
                print("X", Note, title)

            for typ in game["type"]:
                genre_id = Genre.from_name(typ).id
                if Classification.from_both_ids(g_id, genre_id) is None:
                    classification = Classification(game_id=g_id, genre_id=genre_id)
                    db.session.add(classification)

    db.session.commit()

    print("Nombre de jeux rejetés : ", nb_jeux_rejetes)
    print(f"Temps d'exécutuion : {time.perf_counter() - deb:0.4f} sec")


@admin_blueprint.cli.command('fast_loaddb_games')
@click.argument('filename')
def fast_loaddb_games(filename):
    """ WARNING ! ONLY WITH AN EMPTY DATABASE ! Populates the database with games from a yml file """
    print("Chargement du fichier yaml en memoire")
    games = yaml.safe_load(open(filename))

    deb = time.perf_counter()
    # creation d'un profil BGG
    bgg = User(
        email="mmm.dupuis45@gmail.com",
        username="BGG",
        first_name="Board Game",
        last_name="Geek",
        password="BGGdu45",
        profile_picture="https://cf.geekdo-static.com/images/logos/navbar-logo-bgg-b2.svg")
    db.session.add(bgg)
    db.session.commit()
    bgg_id = bgg.id

    # premier tour de boucle, creation des jeux et des genres
    dico_games = dict()  # {game.title: game}
    for title, game in games.items():
        if len(title) > 128:    # Continue la boucle et ignore le reste
            continue
        game_object = Game(
            title=game["title"],
            publication_year=game["publication_year"],
            min_players=game["min_players"],
            max_players=game["max_players"],
            min_playtime=game["min_playtime"],
            image=game["images"]["original"])
        db.session.add(game_object)
        print("V", title)
        dico_games[title] = game_object
        for typ in game["type"]:  # creation des genres
            if Genre.from_name(typ) is None:
                game_object = Genre(name=typ)
                db.session.add(game_object)
    db.session.commit()

    # deuxieme tour de boucle pour les notes de bgg et les genres du jeu
    default_message = "Auto-generated note, the average rating of the game at boardgamegeek.com"
    for title, game in games.items():
        g_id = dico_games[title].id
        rating = Note(
            note=round(game["average_rating"]),
            message=default_message,
            user_id=bgg_id,
            game_id=g_id)
        db.session.add(rating)
        print("V Note", title)

        for typ in game["type"]:
            genre_id = Genre.from_name(typ).id
            classification = Classification(game_id=g_id, genre_id=genre_id)
            db.session.add(classification)
    db.session.commit()

    print(f"Temps d'exécutuion : {time.perf_counter() - deb:0.4f} sec")


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
    """ Populates the database with users and user-related relationships from a yml file. Require loaddb_games. """
    users = yaml.safe_load(open(filename))

    # premier tour de boucle, creation des users
    for u in users:
        if User.from_username(u["username"]) == None:
            user_object = User(
                email=u["email"],
                username=u["username"],
                first_name=u["first_name"],
                last_name=u["last_name"],
                password=u["password"],
                profile_picture=u["profile_picture"])
            db.session.add(user_object)
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


@admin_blueprint.cli.command('loaddb_groups')
@click.argument('filename')
def loaddb_groups(filename):
    """ Populates the database with groups and group-related relationships from a yml file. Require loaddb_users. """
    groups = yaml.safe_load(open(filename))

    # premier tour de boucle, creation des groupes
    for g in groups:
        if Group.from_name(g["name"]) == None:
            group_object = Group(
                name=g["name"],
                is_private=g["is_private"],
                password=g["password"],
                manager_id=User.from_username(g["manager"]).id)
            db.session.add(group_object)
            print("V", g["name"])
        else:
            print("X", g["name"])
    db.session.commit()

    # deuxieme tour de boucle, creation des relations UserXGroup
    for g in groups:
        g_id = Group.from_name(g["name"]).id
        for u in g["members"]:
            u_id = User.from_username(u).id
            if Participate.from_both_ids(u_id, g_id) == None:
                participation = Participate(member_id=u_id, group_id=g_id)
                db.session.add(participation)
                print("V", Participate, g_id, u_id)
            else:
                print("X", Participate, g_id, u_id)
    db.session.commit()
