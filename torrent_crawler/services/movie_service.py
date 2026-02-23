from typing import List
from torrent_crawler.core.models import Movie, SearchQuery
from torrent_crawler.providers.yts import YTSProvider
from torrent_crawler.utils.logger import logger, log_runtime

MoviesList = List[Movie]

class MovieService:
    def __init__(self, api_flag=False):
        self.api_flag = api_flag
        self.provider = YTSProvider()

    @log_runtime
    def crawl_list(self, query: SearchQuery) -> MoviesList:
        logger.info("Service: Crawling movie list")
        return self.provider.search(query)

    @log_runtime
    def crawl_movie(self, movie: Movie) -> Movie:
        logger.info(f"Service: Fetching details for movie: {movie.name}")
        return self.provider.get_details(movie)
