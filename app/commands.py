import json
from concurrent.futures.thread import ThreadPoolExecutor
import requests
import yaml
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from app.models import User, Game, BookmarkUser, HideUser, Note, Wish, KnowRules, Collect, Prefer, Group, Participate, \
    Genre, Classification
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
            o = Game(
                title=title,
                publication_year=game["publication_year"],
                min_players=game["min_players"],
                max_players=game["max_players"],
                min_playtime=game["min_playtime"],
                image=game["images"]["original"])
            db.session.add(o)
            print("V", title)
        else:
            print("X", title)
            nb_jeux_rejetes += 1
        for typ in game["type"]:  # creation des genres
            if Genre.from_name(typ) is None:
                o = Genre(name=typ)
                db.session.add(o)
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
                    o = Classification(game_id=g_id, genre_id=genre_id)
                    db.session.add(o)

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
    # creation d'un profil BGG (existe deja)
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

    print("Premier tour de boucle...")
    # premier tour de boucle, creation des jeux et des genres
    nb_jeux_rejetes = 0
    dico_games = dict()  # {game.title: game}
    i = 0
    for title, game in games.items():
        if len(title) > 128 or 'á' in game["title"]:  # Continue la boucle et ignore le reste
            nb_jeux_rejetes += 1
            continue
        game_object = Game(
            title=game["title"],
            publication_year=game["publication_year"],
            min_players=game["min_players"],
            max_players=game["max_players"],
            min_playtime=game["min_playtime"],
            image=game["images"]["original"])
        db.session.add(game_object)
        dico_games[title] = game_object
        for typ in game["type"]:  # creation des genres
            if Genre.from_name(typ) is None:
                game_object = Genre(name=typ)
                db.session.add(game_object)
        i += 1
        if i % 100 == 0:
            print(f"{i} jeux insere")
    db.session.commit()

    print("Deuxieme tour de boucle...")
    # deuxieme tour de boucle pour les notes de bgg et les genres du jeu
    default_message = "Auto-generated note, the average rating of the game at boardgamegeek.com"
    i = 0
    for title, game in games.items():
        if 'á' in game["title"]:
            continue
        g_id = dico_games[title].id
        rating = Note(
            note=round(game["average_rating"]),
            message=default_message,
            user_id=bgg_id,
            game_id=g_id)
        db.session.add(rating)

        for typ in game["type"]:
            genre_id = Genre.from_name(typ).id
            game_object = Classification(game_id=g_id, genre_id=genre_id)
            db.session.add(game_object)
        i += 1
        if i % 100 == 0:
            print(f"{i} genres insere")
    db.session.commit()

    print("Nombre de jeux rejetés : ", nb_jeux_rejetes)
    print(f"Temps d'exécutuion : {time.perf_counter() - deb:0.4f} sec")


domain = "https://boardgamegeek.com"
main_url = "https://boardgamegeek.com/browse/boardgame/page/"
cover_url = "https://api.geekdo.com/api/images/"
i = 1
games_type_dict = {
    'Strategy ': "Stratégie",
    'Abstract ': "Abstrait",
    'War ': "Guerre",
    'Party ': "Fête",
    'Customizable': "Personnalisable",
    'Amiga': "Amiga",
    "Children's ": "Pour enfant",
    'Atari ST': "Atari ST",
    'Arcade': "Arcade",
    'Commodore 64': "Commodore 64",
    'Thematic': "Thématique",
    'Family ': "Familial"
}
game_name_set = set()  # Only storing name to save memory
engine = create_engine(
    'mysql+pymysql://al_admin:al_admin@agenda-ludique.ddns.net/agendaludique',
    pool_size=5,  # default in SQLAlchemy
    max_overflow=10,  # default in SQLAlchemy
    pool_timeout=1,  # raise an error faster than default
)
thread_safe_session_factory = scoped_session(sessionmaker(bind=engine))



def get_cover(image_id):
    try:
        json_file = requests.get(cover_url + str(image_id)).json()['images']
    except TypeError:  # If we can get the webpage we got a None type and so raise a TypeError exception
        return None

    if "pic1657689" in json_file["original"]["url"]:
        return None
    return {
        "micro": json_file["micro"]["url"],
        "small": json_file["small"]["url"],
        "medium": json_file["medium"]["url"],
        "large": json_file["large"]["url"],
        "square": json_file["square"]["url"],
        "expanded": json_file["expanded"]["url"],
        "crop_100": json_file["crop100"]["url"],
        "square_200": json_file["square200"]["url"],
        "original": json_file["original"]["url"]
    }


def get_type_game(json_obj):
    types = []
    for game_type in json_obj["rankinfo"]:
        if game_type["veryshortprettyname"] != "Overall":
            types.append(games_type_dict[game_type["veryshortprettyname"]])
    return types


def get_game_info(url):
    # Scrap du jeu de la page
    beautiful_html = BeautifulSoup(  # Get raw html of domain + url
        requests.get(domain + url).text,
        "html.parser"
    )
    # The JSON is embedded in script tag so we have to parse it
    a = map(str, beautiful_html.find_all('script'))  # Transform it to an Iterator[str]
    json_text = None

    for elem in a:  # For each <script>
        if 'GEEK.geekitemPreload' in elem:  # if we got the infos
            temp = elem.split('GEEK.geekitemPreload = ')[1]  # Get rid of previous code
            temp2 = temp.split('};', 1)[0]  # Get rid of useless code after the JSON file
            temp2 = temp2 + '}'  # Restore the '}' we removed the line before
            json_text = json.loads(temp2)['item']  # Transform dirty string into proper JSON format

    covers = get_cover(json_text["imageid"])
    if covers is None:
        return None

    return {
        "title": json_text["name"],
        "id": int(json_text["objectid"]),
        "publication_year": int(json_text["yearpublished"]),
        "min_players": int(json_text["minplayers"]),
        "max_players": int(json_text["maxplayers"]),
        "min_playtime": int(json_text["minplaytime"]),
        "average_rating": float(json_text["stats"]["average"]),
        "type": get_type_game(json_text),
        "images": covers
    }


def scrape_thread(j):
    global i
    global game_name_set
    main_html = BeautifulSoup(  # Request raw page and make a bs4 object
        requests.get(main_url + str(j)).text,
        "html.parser"
    )
    temp_games_infos_dict = {}

    # Iterate over the 100 games in the page
    for game in map(str, main_html.find_all("a", {"class": "primary"})):
        game = BeautifulSoup(game, "html.parser")
        href = game.find('a')['href']  # extract href content

        game_info = get_game_info(href)

        if game_info is not None:
            game_title = game_info["title"].upper()
            if game_title not in game_name_set:
                game_name_set.add(game_title)
                temp_games_infos_dict[game_title] = game_info
                temp_games_infos_dict[game_title]["rank"] = i
                i += 1
        if i % 100 == 0:
            print(f"{i} jeux scrapés")

    # Create Game object and send it to db
    global engine, thread_safe_session_factory
    session = thread_safe_session_factory()
    for title, infos in temp_games_infos_dict.items():
        session.add(Game(
            title=title,
            publication_year=infos["publication_year"],
            min_players=infos["min_players"],
            max_players=infos["max_players"],
            min_playtime=infos["min_playtime"],
            image=infos["images"]["original"]))
    session.commit()
    session.remove()


@admin_blueprint.cli.command('rapidfire_loaddb_games')
def rapidfire_loaddb_games():
    from_page = input("Scrap de la page : ")  # Get first page to scrape
    to_page = input("Jusqu'à la page : ")  # Get last page to scrape

    print("On commence à scrape... Ca va prendre un peu de temps... ")
    with ThreadPoolExecutor(max_workers=50) as executor:  # Overkill but it's faster :)
        for j in range(int(from_page), int(to_page) + 1):  # to_page + 1 bc its [from_page ; to_page[
            executor.submit(scrape_thread, j)


def load_relationship(user, u_id, keyword_yml, rs, get_id, kw, list_kwsup=[], get_id_kw=""):
    for elem in user[keyword_yml]:
        if get_id_kw:
            elem_id = get_id(elem[get_id_kw]).id
        else:
            elem_id = get_id(elem).id
        if rs.from_both_ids(u_id, elem_id) is None:
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
        if User.from_username(u["username"]) is None:
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
        u_id = User.from_username(u["username"]).id  # existe forcement
        relations_uxu = {"bookmarked_users": BookmarkUser, "hidden_users": HideUser}
        relations_uxg = {"wishes": Wish, "known": KnowRules, "collection": Collect}

        for kw_yml, rs in relations_uxu.items():
            load_relationship(u, u_id, kw_yml, rs, User.from_username, 'user2_id')
        get_id = Game.from_title
        kw = 'game_id'
        for kw_yml, rs in relations_uxg.items():
            load_relationship(u, u_id, kw_yml, rs, get_id, kw)
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
        if Group.from_name(g["name"]) is None:
            o = Group(
                name=g["name"],
                is_private=g["is_private"],
                password=g["password"],
                manager_id=User.from_username(g["manager"]).id)
            db.session.add(o)
            print("V", g["name"])
        else:
            print("X", g["name"])
    db.session.commit()

    # deuxieme tour de boucle, creation des relations UserXGroup
    for g in groups:
        g_id = Group.from_name(g["name"]).id
        for u in g["members"]:
            u_id = User.from_username(u).id
            if Participate.from_both_ids(u_id, g_id) is None:
                o = Participate(member_id=u_id, group_id=g_id)
                db.session.add(o)
                print("V", Participate, g_id, u_id)
            else:
                print("X", Participate, g_id, u_id)
    db.session.commit()
