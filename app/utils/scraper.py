import json
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from app.models import Game, Genre

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
genres_set = set()  # List all genres to avoid creating new genre object each time
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
    global genres_set
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
        if len(title) > 128 or 'á' in infos["title"]:  # Fix très sale
            continue
        session.add(Game(
            title=title,
            publication_year=infos["publication_year"],
            min_players=infos["min_players"],
            max_players=infos["max_players"],
            min_playtime=infos["min_playtime"],
            image=infos["images"]["original"]))
        for genre in infos["type"]:
            if genre not in genres_set:
                genres_set.add(genre)
                session.add(Genre(name=genre))
    session.commit()
    session.remove()
