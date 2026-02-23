from bs4 import BeautifulSoup
from curl_cffi import requests
from torrent_crawler.core.constants import Constants
from torrent_crawler.utils.helper import Helper
from torrent_crawler.utils.logger import logger

class SubtitleService:
    @staticmethod
    def get_search_url(search_term, page_no):
        q = search_term
        if page_no > 2:
            q += page_no
        return Constants.subtitle_search_url.format(q)

    def crawl_list(self, search_term):
        logger.info(f"SubtitleService: Searching for subtitle list for '{search_term}'")
        page_no = 1
        has_next_page = True
        while has_next_page:
            url = self.get_search_url(search_term, page_no)
            logger.debug(f"SubtitleService: Fetching search URL: {url}")
            try:
                req = requests.get(url, impersonate="chrome")
                soup = BeautifulSoup(req.text, features='html5lib')
                media_list = soup.find_all('li', {'class': 'media-movie-clickable'})
                logger.info(f"SubtitleService: Found {len(media_list)} matching items")
                for media in media_list:
                    media_body = media.find('div', {'class': 'media-body'})
                    _media_link = media_body.find('a').get('href')
                    _media_name = media.find('h3', {'class': 'media-heading'}).text
            except Exception as e:
                logger.error(f"SubtitleService: Failed to crawl subtitle list: {str(e)}")
                break
            has_next_page = False # Limit to first page for now if needed, or implement full loop

    @staticmethod
    def crawl_movie(url):
        logger.info(f"SubtitleService: Crawling movie subtitles from {url}")
        try:
            req = requests.get(url, impersonate="chrome")
            soup = BeautifulSoup(req.text, features='html5lib')
            subtitle_table_tag = soup.find('table', {'class': 'other-subs'})
            if not subtitle_table_tag:
                logger.warning("SubtitleService: No subtitle table found")
                return {}
            
            subtitle_table = subtitle_table_tag.find('tbody').find_all('tr')
            subtitles = {}
            for subtitle in subtitle_table:
                rating = subtitle.find('td', {'class': 'rating-cell'}).text
                language = subtitle.find('td', {'class': 'flag-cell'})\
                    .find('span', {'class': 'sub-lang'}).text
                download_link = subtitle.find('a').get('href').replace('/subtitles/', 'subtitle/')
                link = Constants.subtitle_base_url.format(download_link + '.zip')
                if language not in subtitles:
                    subtitles[language] = []
                subtitles[language].append({
                    'rating': rating,
                    'link': link
                })
            logger.info(f"SubtitleService: Extracted subtitles for {len(subtitles)} languages")
            return subtitles
        except Exception as e:
            logger.error(f"SubtitleService: Failed to crawl movie subtitles: {str(e)}")
            return {}

    def search_subtitle(self, url):
        subtitles = self.crawl_movie(url)
        lang = Helper.take_input('subtitle', list(subtitles.keys()))
        # Download first subtitle for that language as it is highest rated
        subtitle_link = subtitles[lang][0]['link']
        Helper.download_srt(subtitle_link)
