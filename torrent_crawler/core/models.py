import json
import os
from torrent_crawler.core.constants import Constants


class Ratings:
    def __init__(self, ratings):
        self.rotten_tomatoes_critics = ratings.get(Constants.rotten_tomatoes_critics_rating, '')
        self.rotten_tomatoes_audience = ratings.get(Constants.rotten_tomatoes_audience_rating, '')
        self.imdb = ratings.get(Constants.imdb_rating, '')


class Torrents:
    def __init__(self, torrents):
        self.br3d = torrents[Constants.blu_ray_3d] if Constants.blu_ray_3d in torrents else None
        self.br1080 = torrents[Constants.blu_ray_1080p] if Constants.blu_ray_1080p in torrents else None
        self.br720 = torrents[Constants.blu_ray_720p] if Constants.blu_ray_720p in torrents else None
        self.web1080 = torrents[Constants.web_1080p] if Constants.web_1080p in torrents else None
        self.web720 = torrents[Constants.web_720p] if Constants.web_720p in torrents else None


class Movie:
    def __init__(self, movie_id, name, link, year):
        self.id = movie_id
        self.name = name
        self.link = link
        self.year = year
        self.torrents = None
        self.ratings = None
        self.subtitle_url = ''
        self.synopsis = ''
        self.trailer = ''
        self.screenshots = []
        self.genres = []
        self.likes = 0
        self.runtime = ''
        self.image = ''
        self.similar_movies = []

    def set_torrents(self, torrent_list):
        self.torrents = Torrents(torrent_list)

    def set_ratings(self, ratings):
        self.ratings = Ratings(ratings)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'year': self.year,
            'link': self.link,
            'torrents': self.torrents.__dict__ if self.torrents else {},
            'ratings': self.ratings.__dict__ if self.ratings else {},
            'synopsis': self.synopsis,
            'genres': self.genres,
            'likes': self.likes,
            'image': self.image,
            'trailer': self.trailer,
            'screenshots': self.screenshots,
            'similar_movies': self.similar_movies
        }

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


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
