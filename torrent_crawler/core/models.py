import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from torrent_crawler.core.constants import Constants


@dataclass
class Ratings:
    rotten_tomatoes_critics: str = ''
    rotten_tomatoes_audience: str = ''
    imdb: str = ''

    @classmethod
    def from_dict(cls, ratings: dict):
        return cls(
            rotten_tomatoes_critics=ratings.get(Constants.rotten_tomatoes_critics_rating, ''),
            rotten_tomatoes_audience=ratings.get(Constants.rotten_tomatoes_audience_rating, ''),
            imdb=ratings.get(Constants.imdb_rating, '')
        )


@dataclass
class Torrents:
    br3d: Optional[str] = None
    br1080: Optional[str] = None
    br720: Optional[str] = None
    web1080: Optional[str] = None
    web720: Optional[str] = None

    @classmethod
    def from_dict(cls, torrents: dict):
        return cls(
            br3d=torrents.get(Constants.blu_ray_3d),
            br1080=torrents.get(Constants.blu_ray_1080p),
            br720=torrents.get(Constants.blu_ray_720p),
            web1080=torrents.get(Constants.web_1080p),
            web720=torrents.get(Constants.web_720p)
        )


@dataclass
class Movie:
    id: int
    name: str
    link: str
    year: int
    torrents: Optional[Torrents] = None
    ratings: Optional[Ratings] = None
    subtitle_url: str = ''
    synopsis: str = ''
    trailer: str = ''
    screenshots: List[str] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    likes: int = 0
    runtime: str = ''
    image: str = ''
    similar_movies: List[dict] = field(default_factory=list)
    raw_torrents: Dict = field(default_factory=dict)

    def set_torrents(self, torrent_list):
        self.torrents = Torrents.from_dict(torrent_list)

    def set_ratings(self, ratings):
        self.ratings = Ratings.from_dict(ratings)

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), sort_keys=True, indent=4)


@dataclass
class SearchQuery:
    search_term: str
    quality: str
    genre: str
    rating: str
    order_by: str
    year: int = 0
    language: str = 'en'

    def get_url(self):
        return Constants.search_url.format(
            self.search_term, self.quality, self.genre,
            self.rating, self.order_by, self.year, self.language
        )
