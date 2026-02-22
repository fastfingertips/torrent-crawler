from abc import ABC, abstractmethod
from curl_cffi import requests
from torrent_crawler.models import Movie, SearchQuery
from typing import List

class BaseProvider(ABC):
    def __init__(self):
        self.session = requests.Session(impersonate="chrome")
        self.max_movies_in_page = 20

    @abstractmethod
    def search(self, query: SearchQuery) -> List[Movie]:
        pass

    @abstractmethod
    def get_details(self, movie: Movie) -> Movie:
        pass
