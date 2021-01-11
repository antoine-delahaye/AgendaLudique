import json

import requests
import yaml
from bs4 import BeautifulSoup

domain = "https://boardgamegeek.com"
main_url = "https://boardgamegeek.com/browse/boardgame/page/"
cover_url = "https://api.geekdo.com/api/images/"
i = 1


def get_cover(image_id):
    json_file = requests.get(cover_url + str(image_id)).json()['images']
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


def get_game_info(url):
    raw_html = BeautifulSoup(  # Get raw html of domain + url
        requests.get(domain + url).text,
        "html.parser"
    )
    a = map(str, raw_html.find_all('script'))  # Transform it to an Iterator[str]
    json_text = None
    for elem in a:  # For each <script>
        if 'GEEK.geekitemPreload' in elem:  # if we got the infos
            temp = elem.split('GEEK.geekitemPreload = ')[1]  # Get rid of previous code
            temp2 = temp.split('};', 1)[0]  # Get rid of useless code after the JSON file
            temp2 = temp2 + '}'  # Restore the '}' we removed the line before
            json_text = json.loads(temp2)['item']  # Transform dirty string into proper JSON format
    return {
        "title": json_text["name"],
        "publication_year": json_text["yearpublished"],
        "min_players": json_text["minplayers"],
        "max_players": json_text["maxplayers"],
        "min_playtime": json_text["minplaytime"],
        "images": get_cover(json_text["imageid"])
    }


def create_game_list(raw_html):
    game_list_dict = {}
    global i
    for game in map(str, raw_html.find_all("a", {"class": "primary"})):  # This way we can iterate and parse html
        game = BeautifulSoup(game, "html.parser")  # Convert str into bs4 object
        href = game.find('a')['href']  # extract href content
        id_game = int(href.split('/')[2])  # extract id from href content
        game_list_dict[id_game] = get_game_info(href)  # store infos as values and id as key
        game_list_dict[id_game]["rank"] = i  # Add rank to save order
        print(f"Jeu n⁰{i}: {game_list_dict[id_game]['title']}")  # Just to inform where the program is
        i += 1
    return game_list_dict


def save_yaml(game_list_dict):
    with open('games-data.yaml', 'w') as f:
        f.write(yaml.dump(game_list_dict, sort_keys=False))  # write game_list_dict to the file and disable auto sort


def main():
    from_page = input("Scrap de la page : ")    # Get first page to scrape
    to_page = input("Jusqu'à la page : ")  # Get last page to scrape
    game_list_dict = {}  # Dict of all games (this is what's going into the yaml)
    for j in range(int(from_page), int(to_page) + 1):   # to_page + 1 bc its [from_page ; to_page[
        main_html = BeautifulSoup(  # Request raw page and make a bs4 object
            requests.get(main_url + str(j)).text,
            "html.parser"
        )
        game_list_dict = {**game_list_dict, **create_game_list(main_html)}  # Merge dict
    save_yaml(game_list_dict)   # Save yaml to ressources/games-data.yaml


if __name__ == '__main__':
    main()
