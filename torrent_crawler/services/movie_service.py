from bs4 import BeautifulSoup
import re
from curl_cffi import requests
from typing import List
from torrent_crawler.constants import Constants
from torrent_crawler.helper import Helper
from torrent_crawler.models import Movie
from rich.console import Console

console = Console()

MoviesList = List[Movie]

class MovieService:
    def __init__(self, api_flag=False, save_list=False, print_console=False):
        self.api_flag = api_flag
        self.list_url = Constants.list_url
        self.all_formats = []
        self.id = 1
        self.should_save_list = save_list or False
        self.should_print_to_console = print_console or False
        self.max_movies_in_page = 20
        self.update_progress = False if api_flag is True else True
        self.session = requests.Session(impersonate="chrome")

    def crawl_list(self, crawl_url: str) -> MoviesList:
        page_no = 1
        has_next_page = True
        movies = []
        current_movie_count = 1
        movies_count = 0
        crawl_url = crawl_url or self.list_url
        while has_next_page:
            request_url = crawl_url
            if page_no > 1:
                request_url = '{0}?page={1}'.format(crawl_url, page_no)
            req = self.session.get(request_url)
            soup = BeautifulSoup(req.text, features='html5lib')
            if page_no == 1:
                browse_content = soup.find('div', {'class': 'browse-content'})
                if not browse_content or not browse_content.find('h2'):
                    console.print("\n[red][Hata][/red] Sayfa icerigi okunamadi. Cloudflare engeline takilmis olabiliriz.")
                    console.print("Lutfen bir tarayicidan https://yts.bz adresine girip dogrulama yapmayi deneyin.")
                    return []
                h2_tag = browse_content.find('h2')
                movies_count_text = h2_tag.text if h2_tag else ""

                movies_count_text = movies_count_text.replace(',', '')
                match = re.search(r'(\d+)\s+.*found', movies_count_text, re.IGNORECASE)
                if match:
                    movies_count = int(match.group(1))
                    console.print(f'Total [green]{movies_count}[/green] movies found')
                else:
                    movies_count = 0
            
            movie_wraps = soup.find_all('div', {'class': 'browse-movie-wrap'})
            if page_no == 1 and movies_count == 0:
                movies_count = len(movie_wraps)
                if movies_count > 0:
                    console.print(f'Total [green]{movies_count}[/green] movies found')

            if len(movie_wraps) < self.max_movies_in_page:
                has_next_page = False
            for wrap in movie_wraps:
                if movies_count > 0 and current_movie_count > movies_count:
                    has_next_page = False
                    break
                movie_link = wrap.find('a', {'class': 'browse-movie-link'}).get('href')
                movie_details = wrap.find('div', {'class': 'browse-movie-bottom'})
                movie_name = movie_details.find('a', {'class': 'browse-movie-title'}).text
                movie_year = movie_details.find('div', {'class': 'browse-movie-year'}).text
                movie = Movie(current_movie_count, movie_name, movie_link, int(movie_year))
                movie = self.crawl_movie(movie)
                movies.append(movie)
                if self.should_print_to_console:
                    console.print(f'[yellow]{current_movie_count}:[/yellow] {movie_name}')
                if self.should_save_list:
                    movie.save_list()
                if self.update_progress:
                    Helper.update_progress(current_movie_count, movies_count)
                current_movie_count += 1
            page_no += 1
        return movies

    def crawl_movie(self, movie: Movie) -> Movie:
        try:
            req = self.session.get(movie.link, timeout=10)
            soup = BeautifulSoup(req.text, features='html5lib')
            movie_info = soup.find('div', {'id': 'movie-info'})
            if movie_info:
                movie_torrents = movie_info.find('p', {'class': 'hidden-xs hidden-sm'}).find_all('a')
                torrent_list = {}
                for torrent in movie_torrents:
                    torrent_link = torrent.get('href')
                    torrent_quality = torrent.text
                    if torrent_link and torrent_quality and "Subtitle" not in torrent_quality:
                        torrent_list[torrent_quality] = torrent_link
                movie_ratings = movie_info.find('div', {'class': 'bottom-info'}).find_all('div', {'itemprop': 'aggregateRating'})
                rating_list = {}
                for rating in movie_ratings:
                    rating_link = rating.find('a')
                    if rating_link:
                        rater = rating_link.get('title')
                        rating_given_span = rating.find('span', {'itemprop': 'ratingValue'})
                        if rater and rating_given_span:
                            rating_list[rater] = rating_given_span.text
                movie.set_torrents(torrent_list)
                movie.raw_torrents = torrent_list
                movie.set_ratings(rating_list)
            elif self.should_print_to_console:
                console.print(f"[red]{movie.name} got no info, not saving it[/red]")
            movie_tech_specs = soup.find('div', {'id': 'movie-tech-specs'})
            if movie_tech_specs:
                tech_spec = movie_tech_specs.find('div', {'class': 'tech-spec-info'})
                if tech_spec:
                    subtitle_url = tech_spec.find('a')
                    if subtitle_url:
                        movie.subtitle_url = subtitle_url.get('href')
        except Exception as e:
            if self.should_print_to_console:
                console.print(f"[red]Failed to get details for {movie.name}: {e}[/red]")
        return movie
