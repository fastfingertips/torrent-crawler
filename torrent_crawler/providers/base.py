import os
import re
from curl_cffi import requests
from torrent_crawler.core.models import Movie, SearchQuery
from typing import List
from torrent_crawler.utils.logger import logger

class BaseProvider:
    def __init__(self):
        self.session = requests.Session(impersonate="chrome")
        self.max_movies_in_page = 20
        self.debug_dir = "debug_html"
        self.debug_html_enabled = os.environ.get("TORRENT_CRAWLER_DEBUG_HTML") == "1"
        
        if self.debug_html_enabled and not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir)

    def get(self, url: str, **kwargs):
        """Perform a GET request using the shared session with logging and debugging."""
        try:
            logger.debug(f"Provider: Fetching {url}")
            response = self.session.get(url, timeout=15, **kwargs)
            if self.debug_html_enabled:
                self.save_html(url, response.text)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"Provider: Request failed for {url}: {str(e)}")
            raise

    def save_html(self, url: str, content: str):
        """Saves the raw HTML content to a local file for debugging."""
        safe_name = re.sub(r'[^\w\-_\. ]', '_', url.replace('https://', '').replace('http://', ''))
        filename = os.path.join(self.debug_dir, f"{safe_name}.html")
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            pass

    def search(self, query: SearchQuery) -> List[Movie]:
        raise NotImplementedError

    def get_details(self, movie: Movie) -> Movie:
        raise NotImplementedError
