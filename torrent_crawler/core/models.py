import json
from dataclasses import asdict, dataclass, field
from typing import Optional

from torrent_crawler.core import constants as consts


@dataclass
class Ratings:
    rotten_tomatoes_critics: str = ""
    rotten_tomatoes_audience: str = ""
    imdb: str = ""

    @classmethod
    def from_dict(cls, ratings: dict):
        return cls(
            rotten_tomatoes_critics=ratings.get(consts.ROTTEN_TOMATOES_CRITICS_RATING, ""),
            rotten_tomatoes_audience=ratings.get(consts.ROTTEN_TOMATOES_AUDIENCE_RATING, ""),
            imdb=ratings.get(consts.IMDB_RATING, ""),
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
            br3d=torrents.get(consts.BLU_RAY_3D),
            br1080=torrents.get(consts.BLU_RAY_1080P),
            br720=torrents.get(consts.BLU_RAY_720P),
            web1080=torrents.get(consts.WEB_1080P),
            web720=torrents.get(consts.WEB_720P),
        )


@dataclass
class Movie:
    id: int
    name: str
    link: str
    year: int
    torrents: Optional[Torrents] = None
    ratings: Optional[Ratings] = None
    subtitle_url: str = ""
    synopsis: str = ""
    trailer: str = ""
    screenshots: list[str] = field(default_factory=list)
    genres: list[str] = field(default_factory=list)
    likes: int = 0
    runtime: str = ""
    image: str = ""
    similar_movies: list[dict] = field(default_factory=list)
    raw_torrents: dict = field(default_factory=dict)

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
    language: str = "en"

    def get_url(self):
        return consts.SEARCH_URL.format(
            self.search_term, self.quality, self.genre, self.rating, self.order_by, self.year, self.language
        )
