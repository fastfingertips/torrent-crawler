import signal
import traceback
import beaupy
from rich.panel import Panel
from typing import Dict, List
from torrent_crawler.constants import Constants
from torrent_crawler.services.movie_service import MovieService
from torrent_crawler.services.subtitle_service import SubtitleService
from torrent_crawler.helper import Helper
from torrent_crawler.models import Movie, Torrents
from torrent_crawler.print import Print, console


def sigint_handler(signum, frame):
    Print.thanks()
    exit(1)


signal.signal(signal.SIGINT, sigint_handler)


class SearchQuery:
    def __init__(self, search_term, quality, genre, rating, order_by, year=0, language='en'):
        self.search_term = search_term
        self.quality = quality
        self.genre = genre
        self.rating = rating
        self.order_by = order_by
        self.language = language
        self.year = year

    def get_url(self):
        return Constants.search_url.format(self.search_term, self.quality, self.genre,
                                           self.rating, self.order_by, self.year, self.language)


class Search:
    def __init__(self, search_query: SearchQuery, api_flag: bool = False):
        self.search_query = search_query
        self.api_flag = api_flag

    def get_available_torrents(self, torrents: Torrents) -> Dict:
        available_torrents = {}
        if self.search_query.quality in ['all', '3D'] and torrents.br3d:
            available_torrents['3D.BluRay'] = torrents.br3d
        if self.search_query.quality in ['all', '720'] and torrents.br720:
            available_torrents['720p.BluRay'] = torrents.br720
        if self.search_query.quality in ['all', '1080'] and torrents.br1080:
            available_torrents['1080p.BluRay'] = torrents.br1080
        if self.search_query.quality in ['all', '720'] and torrents.web720:
            available_torrents['720p.WEB'] = torrents.web720
        if self.search_query.quality in ['all', '1080'] and torrents.web1080:
            available_torrents['1080p.WEB'] = torrents.web1080
        return available_torrents

    MoviesList = List[Movie]

    def show_movies(self, movies: MoviesList):
        Print.bold_string('Select a movie: ')
        choices = ['{}: {} ({})'.format(ind + 1, movie.name, movie.year) for ind, movie in enumerate(movies)]
        selected_choice = beaupy.select(choices, cursor=">", cursor_style="cyan")
        
        if not selected_choice:
            return

        mid = int(selected_choice.split(':')[0])
        movie_selected = movies[mid - 1]
        Print.bold_string(Constants.available_torrents_text)

        if hasattr(movie_selected, 'raw_torrents'):
            available_torrents = movie_selected.raw_torrents
        else:
            available_torrents = self.get_available_torrents(movie_selected.torrents)

        if len(available_torrents) == 0:
            console.print(f"[red]{Constants.no_torrent_text}[/red]")
        else:
            available_keys = list(available_torrents.keys())
            if len(available_torrents) == 1:
                if beaupy.confirm("Download {}?".format(available_keys[0])):
                    torrent_link = available_torrents[available_keys[0]]
                    Helper.open_magnet_link(torrent_link)
                    console.print(f"{Constants.click_link_text} [red]{torrent_link}[/red]")
            else:
                Print.bold_string("Select quality:")
                selected_quality = beaupy.select(available_keys, cursor=">", cursor_style="cyan")
                if selected_quality:
                    torrent_link = available_torrents[selected_quality]
                    Helper.open_magnet_link(torrent_link)
                    console.print(f"{Constants.click_link_text} [red]{torrent_link}[/red]")


            if movie_selected.subtitle_url and movie_selected.subtitle_url != '':
                if beaupy.confirm(Constants.selection_text['subtitle']):
                    subtitle = SubtitleService()
                    subtitle.search_subtitle(movie_selected.subtitle_url)

            
            if beaupy.confirm(Constants.another_movies_text.format("", self.search_query.search_term)):
                self.show_movies(movies)

    def start(self, search_query: SearchQuery):
        url = search_query.get_url()
        crawler = MovieService(api_flag=self.api_flag)
        movies = crawler.crawl_list(url)
        if self.api_flag is True:
            return movies
        self.show_movies(movies)
        if beaupy.confirm(Constants.restart_search_text):
            main()
        else:
            Print.thanks()


class SearchInput:
    @staticmethod
    def create_query() -> SearchQuery:
        s = console.input("[bold cyan]❯[/bold cyan] Please enter search string: ")
        while not s:
            s = console.input("[bold cyan]❯[/bold cyan] Please enter search string: ")

        q = 'all'
        g = Helper.take_optional_input('genre')
        o = Helper.take_optional_input('order')

        return SearchQuery(s, q, g, 0, o, 0, 'all')


def main():
    from torrent_crawler.tui import TorrentCrawlerApp
    app = TorrentCrawlerApp()
    app.run()


if __name__ == '__main__':
    main()
