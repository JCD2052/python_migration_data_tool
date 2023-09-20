import random

import cloudscraper
import requests


class GoogleSearchClient:
    def __init__(self) -> None:
        self.__user_agent_list = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        ]
        self.__url = "https://www.google.com/search"
        self.__session = cloudscraper.create_scraper(delay=15, browser={'custom': 'ScraperBot/1.0'})

    def get_response(self, searched_value) -> requests.Response:
        params = {"q": searched_value}
        headers = {'User-Agent': random.choice(self.__user_agent_list)}
        return self.__session.get(self.__url, params=params, headers=headers, allow_redirects=True)
