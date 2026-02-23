from typing import List
from torrent_crawler.core.models import Movie, SearchQuery
from torrent_crawler.providers.yts import YTSProvider
from torrent_crawler.utils.logger import logger

MoviesList = List[Movie]

class MovieService:
    def __init__(self, api_flag=False, save_list=False, print_console=False):
        self.api_flag = api_flag
        self.should_save_list = save_list or False
        self.should_print_to_console = print_console or False
        self.provider = YTSProvider()

    def crawl_list(self, query: SearchQuery) -> MoviesList:
        logger.info("Service: Crawling movie list")
        movies = self.provider.search(query)
        
        if self.should_save_list:
            for movie in movies:
                movie.save_list()
                
        return movies

    def crawl_movie(self, movie: Movie) -> Movie:
        logger.info(f"Service: Fetching details for movie: {movie.name}")
        return self.provider.get_details(movie)
