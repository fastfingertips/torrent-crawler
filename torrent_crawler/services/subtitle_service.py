from bs4 import BeautifulSoup
from curl_cffi import requests
from torrent_crawler.core.constants import Constants
from torrent_crawler.utils.helper import Helper

class SubtitleService:
    @staticmethod
    def get_search_url(search_term, page_no):
        q = search_term
        if page_no > 2:
            q += page_no
        return Constants.subtitle_search_url.format(q)

    def crawl_list(self, search_term):
        page_no = 1
        has_next_page = True
        while has_next_page:
            url = self.get_search_url(search_term, page_no)
            req = requests.get(url, impersonate="chrome")
            soup = BeautifulSoup(req.text, features='html5lib')
            media_list = soup.find_all('li', {'class': 'media-movie-clickable'})
            for media in media_list:
                media_body = media.find('div', {'class': 'media-body'})
                _media_link = media_body.find('a').get('href')
                _media_name = media.find('h3', {'class': 'media-heading'}).text

    @staticmethod
    def crawl_movie(url):
        req = requests.get(url, impersonate="chrome")
        soup = BeautifulSoup(req.text, features='html5lib')
        subtitle_table = soup.find('table', {'class': 'other-subs'}).find('tbody').find_all('tr')
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
        return subtitles

    def search_subtitle(self, url):
        subtitles = self.crawl_movie(url)
        lang = Helper.take_input('subtitle', list(subtitles.keys()))
        # Download first subtitle for that language as it is highest rated
        subtitle_link = subtitles[lang][0]['link']
        Helper.download_srt(subtitle_link)
