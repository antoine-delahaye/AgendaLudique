from concurrent.futures.thread import ThreadPoolExecutor
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

import requests
from bs4 import BeautifulSoup


class RewriteScraper:
    domain = "https://boardgamegeek.com"
    page_url = "https://boardgamegeek.com/browse/boardgame/page/"
    list_pages = []

    def get_page(self, url):
        return BeautifulSoup(requests.get(url).text, "html.parser")

    def get_list_pages(self, from_page, to_page):
        with ThreadPoolExecutor(max_workers=50) as executor:
            for i in range(int(from_page), int(to_page) + 1):  # to_page + 1 bc its [from_page ; to_page[
                self.list_pages.append(executor.submit(self.get_page, self.page_url+str(i)).result())

    def get_game_from_page(self, page):
        pass
