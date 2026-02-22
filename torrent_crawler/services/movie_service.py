from typing import List
from torrent_crawler.models import Movie, SearchQuery
from torrent_crawler.providers.yts import YTSProvider

MoviesList = List[Movie]

class MovieService:
    def __init__(self, api_flag=False, save_list=False, print_console=False):
        self.api_flag = api_flag
        self.should_save_list = save_list or False
        self.should_print_to_console = print_console or False
        self.provider = YTSProvider()

    def crawl_list(self, query: SearchQuery) -> MoviesList:
        movies = self.provider.search(query)
        
        if self.should_save_list:
            for movie in movies:
                movie.save_list()
                
        return movies

    def crawl_movie(self, movie: Movie) -> Movie:
        return self.provider.get_details(movie)
