from bs4 import BeautifulSoup

from torrent_crawler.core import constants as consts
from torrent_crawler.providers.base import HTTPClient
from torrent_crawler.utils.logger import logger


class SubtitleProvider(HTTPClient):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_search_url(search_term, page_no):
        q = search_term
        if page_no > 2:
            q += str(page_no)
        return consts.SUBTITLE_SEARCH_URL.format(q)

    def crawl_list(self, search_term):
        logger.info(f"SubtitleProvider: Searching for subtitle list for '{search_term}'")
        page_no = 1
        has_next_page = True
        while has_next_page:
            url = self.get_search_url(search_term, page_no)
            try:
                req = self.get(url)
                soup = BeautifulSoup(req.text, features="html5lib")
                media_list = soup.find_all("li", {"class": "media-movie-clickable"})
                logger.info(f"SubtitleProvider: Found {len(media_list)} matching items")
                for media in media_list:
                    media_body = media.find("div", {"class": "media-body"})
                    _media_link = media_body.find("a").get("href")
                    _media_name = media.find("h3", {"class": "media-heading"}).text
            except Exception:
                break
            has_next_page = False

    def crawl_movie(self, url):
        logger.info(f"SubtitleProvider: Crawling movie subtitles from {url}")
        try:
            req = self.get(url)
            soup = BeautifulSoup(req.text, features="html5lib")
            subtitle_table_tag = soup.find("table", {"class": "other-subs"})
            if not subtitle_table_tag:
                logger.warning("SubtitleProvider: No subtitle table found")
                return {}

            subtitle_table = subtitle_table_tag.find("tbody").find_all("tr")
            subtitles = {}
            for subtitle in subtitle_table:
                rating = subtitle.find("td", {"class": "rating-cell"}).text
                language = subtitle.find("td", {"class": "flag-cell"}).find("span", {"class": "sub-lang"}).text
                download_link = subtitle.find("a").get("href").replace("/subtitles/", "subtitle/")
                link = consts.SUBTITLE_BASE_URL.format(download_link + ".zip")
                if language not in subtitles:
                    subtitles[language] = []
                subtitles[language].append({"rating": rating, "link": link})
            logger.info(f"SubtitleProvider: Extracted subtitles for {len(subtitles)} languages")
            return subtitles
        except Exception:
            return {}
