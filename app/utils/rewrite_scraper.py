import json
import time
import requests
import threading
from tqdm import tqdm
from bs4 import BeautifulSoup
from concurrent.futures.thread import ThreadPoolExecutor


class RewriteScraper:
    def __init__(self):
        self.__domain = "https://boardgamegeek.com"
        self.__page_url = "https://boardgamegeek.com/browse/boardgame/page/"
        self.__cover_url = "https://api.geekdo.com/api/images/"
        self.__list_pages = []
        self.__games_type_dict = {
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
        self.__game_name_set = set()
        self.__game_number = 1
        self.__game_info_dict = {}

    def get_game_numer(self):
        return self.__game_number

    def __get_cover(self, image_id):
        try:
            json_file = requests.get(self.__cover_url + str(image_id)).json()['images']
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

    def __get_type_game(self, json_obj):
        types = []
        for game_type in json_obj["rankinfo"]:
            if game_type["veryshortprettyname"] != "Overall":
                types.append(self.__games_type_dict[game_type["veryshortprettyname"]])
        return types

    def __get_game_info(self, url):
        # Scrap du jeu de la page
        beautiful_html = BeautifulSoup(  # Get raw html of domain + url
            requests.get(self.__domain + url).text,
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

        covers = self.__get_cover(json_text["imageid"])
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
            "type": self.__get_type_game(json_text),
            "images": covers
        }

    def __get_games_from_page(self, page):
        for game in map(str, page.find_all("a", {"class": "primary"})):
            game = BeautifulSoup(game, "html.parser")
            href = game.find('a')['href']  # extract href content

            game_info = self.__get_game_info(href)

            if game_info is not None:
                game_title = game_info["title"].upper()
                if game_title not in self.__game_name_set:
                    self.__game_name_set.add(game_title)
                    self.__game_info_dict[game_title] = game_info
                    self.__game_info_dict[game_title]["rank"] = self.__game_number
                    self.__game_number += 1

    def __get_page(self, url):
        return BeautifulSoup(requests.get(url).text, "html.parser")

    def get_list_pages(self, from_page, to_page):
        list_thread = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            for i in range(int(from_page), int(to_page) + 1):  # to_page + 1 bc its [from_page ; to_page[
                e = executor.submit(self.__get_page, self.__page_url + str(i))
                list_thread.append(e)
        for thread in list_thread:
            self.__list_pages.append(thread.result())

    def scrap(self, from_page, to_page):
        print("Récupération des pages...")
        self.get_list_pages(from_page, to_page)

        print("Récupération des informations des jeux... Ca peut prendre longtemps")
        t = threading.Thread(target=self.__progression_bar, args=(1 * 100,))
        t.start()
        with ThreadPoolExecutor(max_workers=50) as executor:
            for page in self.__list_pages:
                executor.submit(self.__get_games_from_page, page)

        # To close the thread
        self.__game_number = to_page*100
        t.join()

        print("Le scraper à fini son travail, on va push sur la BDD maintenant")
        return self.__game_info_dict

    def __progression_bar(self, nb):
        pbar = tqdm(range(nb), position=0, leave=True)
        while nb > self.__game_number:
            pbar.n = self.__game_number
            pbar.refresh()
            time.sleep(0.1)
