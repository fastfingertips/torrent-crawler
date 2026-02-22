from torrent_crawler.services.movie_service import MovieService
from torrent_crawler.models import Movie
service = MovieService(api_flag=True, print_console=False)
movies = service.crawl_list("https://yts.bz/browse-movies/red/all/all/0/latest/0/all")
print("Movies", len(movies))
