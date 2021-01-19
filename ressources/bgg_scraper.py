import json
import os
import sys
from concurrent.futures.thread import ThreadPoolExecutor

import mariadb
import requests
import yaml
from bs4 import BeautifulSoup

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


def create_game_list(raw_html):
    game_list_dict = {}
    global i

    for game in map(str, raw_html.find_all("a", {"class": "primary"})):  # This way we can iterate and parse html
        game = BeautifulSoup(game, "html.parser")  # Convert str into bs4 object
        href = game.find('a')['href']  # extract href content

        game_info = get_game_info(href)  # Get game info into dict

        if game_info is not None:  # Check if we have game info, if not skip this game
            game_title = game_info["title"].upper()  # Assign title
            game_list_dict[game_title] = game_info  # Transfer game info into the big ass dict
            game_list_dict[game_title]["rank"] = i  # Add rank to save order
            i += 1
    return game_list_dict


def save_yaml(game_list_dict):
    with open('games-data.yaml', 'a') as f:
        f.write(yaml.dump(game_list_dict, sort_keys=False, allow_unicode=True))  # write game_list_dict to the file
        # and disable auto sort


def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.full_load(f)


def save_yaml_to_db(path):
    try:
        conn = mariadb.connect(
            user='al_admin',
            password='al_admin',
            host='agenda-ludique.ddns.net',
            port=3306,
            database='agendaludique'

        )
    except mariadb.Error as e:
        print(f'Error connecting to MariaDB Platform: {e}')
        sys.exit(1)

    cur = conn.cursor()
    game_id = 0
    cur.execute("SELECT * FROM games")
    for max_game_id in cur:
        if max_game_id[0] is not None:
            game_id = int(max_game_id)

    # Since we have the name of the game as key, we don't have to check for duplicates because if a game have
    # the same name, so the same key, it will not be added to the dict due to the nature of dict implementation
    # Now... Time to load some data !
    games_from_yaml = load_yaml(path)
    for title, data in games_from_yaml.items():
        try:
            cur.execute("INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, ?)", (game_id,
                                                                           title,
                                                                           data['publication_year'],
                                                                           data['min_players'],
                                                                           data['max_players'],
                                                                           data['min_playtime'],
                                                                           data['images']['original']))
        except mariadb.Error as e:
            print(f'Error: {e}')
        conn.commit()
        game_id = game_id + 1


def scrape_thread(j):
    main_html = BeautifulSoup(  # Request raw page and make a bs4 object
        requests.get(main_url + str(j)).text,
        "html.parser"
    )
    game_list_dict = create_game_list(main_html)
    print("Ajout des jeux scrapé dans le yaml...")
    save_yaml(game_list_dict)  # Save yaml into games-data.yaml
    print("Fini !")


def scraper():
    from_page = input("Scrap de la page : ")  # Get first page to scrape
    to_page = input("Jusqu'à la page : ")  # Get last page to scrape

    try:
        os.remove("games-data.yaml")
        print("Ancien game-data.yaml supprimé et création d'un nouveau")
    except FileNotFoundError:
        print("Création de game-data.yaml")
    print("On commence à scrape... Ca va prendre un peu de temps... ")
    with ThreadPoolExecutor(max_workers=50) as executor:  # Overkill but it's faster :)
        for j in range(int(from_page), int(to_page) + 1):  # to_page + 1 bc its [from_page ; to_page[
            executor.submit(scrape_thread, j)


def main():
    while True:
        usr_input = int(input("Mode :\n"
                              " (1) Juste scrape des pages\n"
                              " (2) Charger un yaml dans la BDD\n"
                              " (3) Quitter\n"
                              ))

        if usr_input == 1:
            scraper()
        elif usr_input == 2:
            path = input("Chemin vers le yaml : ")
            save_yaml_to_db(path)
        elif usr_input == 3:
            sys.exit(0)


if __name__ == '__main__':
    main()
