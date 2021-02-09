from concurrent.futures.thread import ThreadPoolExecutor


class RewriteScraper:
    domain = "https://boardgamegeek.com"
    page_url = "https://boardgamegeek.com/browse/boardgame/page/"

    def get_page(self, url):
        pass

    def get_list_pages(self, from_page, to_page):
        with ThreadPoolExecutor(max_workers=50) as executor:  # Overkill but it's faster :)
            for i in range(int(from_page), int(to_page) + 1):  # to_page + 1 bc its [from_page ; to_page[
                executor.submit(self.get_page, self.page_url+str(i))

    def get_game_from_page(self, page):
        pass
