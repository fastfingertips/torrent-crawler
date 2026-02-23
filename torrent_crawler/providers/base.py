import os
import re
from abc import ABC, abstractmethod
from curl_cffi import requests
from torrent_crawler.core.models import Movie, SearchQuery
from typing import List

class BaseProvider(ABC):
    def __init__(self):
        self.session = requests.Session(impersonate="chrome")
        self.max_movies_in_page = 20
        self.debug_dir = "debug_html"
        
        if not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir)

    def save_html(self, url: str, content: str):
        """Saves the raw HTML content to a local file for debugging."""
        # Clean URL to create a safe filename
        safe_name = re.sub(r'[^\w\-_\. ]', '_', url.replace('https://', '').replace('http://', ''))
        filename = os.path.join(self.debug_dir, f"{safe_name}.html")
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            pass

    @abstractmethod
    def search(self, query: SearchQuery) -> List[Movie]:
        pass

    @abstractmethod
    def get_details(self, movie: Movie) -> Movie:
        pass
