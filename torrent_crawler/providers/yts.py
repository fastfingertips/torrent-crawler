import re
from bs4 import BeautifulSoup
from typing import List
from torrent_crawler.providers.base import BaseProvider
from torrent_crawler.core.models import Movie, SearchQuery
from torrent_crawler.core.constants import Constants
from torrent_crawler.utils.logger import logger, log_runtime

class YTSProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self.list_url = Constants.list_url

    @log_runtime
    def search(self, search_query: SearchQuery) -> List[Movie]:
        search_url = search_query.get_url()
        page_no = 1
        has_next_page = True
        movies = []
        current_movie_count = 1
        movies_count = 0
        
        logger.info(f"Searching for: {search_query.search_term}")
        
        while has_next_page:
            request_url = search_url
            if page_no > 1:
                request_url = '{0}?page={1}'.format(search_url, page_no)
            
            try:
                req = self.get(request_url)
                soup = BeautifulSoup(req.text, features='html5lib')
            except Exception:
                break

            if page_no == 1:
                browse_content = soup.find('div', {'class': 'browse-content'})
                if not browse_content or not browse_content.find('h2'):
                    logger.warning("No search results found or content structure changed.")
                    break
                h2_tag = browse_content.find('h2')
                movies_count_text = h2_tag.text if h2_tag else ""
                movies_count_text = movies_count_text.replace(',', '')
                match = re.search(r'(\d+)\s+.*found', movies_count_text, re.IGNORECASE)
                if match:
                    movies_count = int(match.group(1))
                    logger.info(f"Found {movies_count} total movies matches")
                else:
                    movies_count = 0
            
            movie_wraps = soup.find_all('div', {'class': 'browse-movie-wrap'})
            if not movie_wraps:
                break

            if page_no == 1 and movies_count == 0:
                movies_count = len(movie_wraps)

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
                
                # Extract basic info from browse page to avoid extra requests
                # 1. Rating
                rating_tag = wrap.find('h4', {'class': 'rating'})
                if rating_tag:
                    movie.set_ratings({Constants.imdb_rating: rating_tag.text.split('/')[0].strip()})
                
                # 2. Qualities
                tags_div = wrap.find('div', {'class': 'browse-movie-tags'})
                if tags_div:
                    tags = tags_div.find_all('a')
                    torrent_list = {tag.text: "" for tag in tags} # We don't have magnet yet, but we have types
                    movie.set_torrents(torrent_list)
                    movie.raw_torrents = torrent_list
                
                movies.append(movie)
                current_movie_count += 1
                
            page_no += 1
            if current_movie_count > self.max_movies_in_page:
                has_next_page = False
                
        return movies

    @log_runtime
    def get_details(self, movie: Movie) -> Movie:
        try:
            req = self.get(movie.link)
            soup = BeautifulSoup(req.text, features='html5lib')
            
            # Extract cover image
            img_container = soup.find('div', {'id': 'movie-poster'})
            if img_container:
                img_tag = img_container.find('img')
                if img_tag:
                    movie.image = img_tag.get('src')

            movie_info = soup.find('div', {'id': 'movie-info'})
            if movie_info:
                # Torrent Info
                movie_torrents_p = movie_info.find('p', {'class': 'hidden-xs hidden-sm'})
                if movie_torrents_p:
                    movie_torrents = movie_torrents_p.find_all('a')
                    torrent_list = {}
                    for torrent in movie_torrents:
                        torrent_link = torrent.get('href')
                        torrent_quality = torrent.text
                        if torrent_link and torrent_quality and "Subtitle" not in torrent_quality:
                            torrent_list[torrent_quality] = torrent_link
                    
                    movie.set_torrents(torrent_list)
                    movie.raw_torrents = torrent_list
                
                # Rating Info
                movie_ratings = movie_info.find('div', {'class': 'bottom-info'}).find_all('div', {'itemprop': 'aggregateRating'})
                rating_list = {}
                for rating in movie_ratings:
                    rating_link = rating.find('a')
                    if rating_link:
                        rater = rating_link.get('title')
                        rating_given_span = rating.find('span', {'itemprop': 'ratingValue'})
                        if rater and rating_given_span:
                            rating_list[rater] = rating_given_span.text
                movie.set_ratings(rating_list)

                # Extract synopsis
                synopsis_div = soup.find('div', {'id': 'synopsis'})
                if synopsis_div:
                    movie.synopsis = synopsis_div.find('p').text.strip()

                # Extract trailer
                trailer_link = soup.find('a', {'id': 'playTrailer'})
                if trailer_link:
                    movie.trailer = trailer_link.get('href')

                # Extract screenshots
                screenshot_links = soup.find_all('a', {'class': 'screenshot-group'})
                movie.screenshots = [s.get('href') for s in screenshot_links if s.get('href')]

                # Extract likes
                likes_span = soup.find('span', {'id': 'movie-likes'})
                if likes_span:
                    movie.likes = likes_span.text.strip()

                # Extract genres
                info_h2s = movie_info.find_all('h2')
                if len(info_h2s) > 1:
                    genres_text = info_h2s[1].text
                    movie.genres = [g.strip() for g in genres_text.split('/')]

            # Extract similar movies
            related_div = soup.find('div', {'id': 'movie-related'})
            if related_div:
                similar_movies = []
                for a in related_div.find_all('a'):
                    title = a.get('title')
                    link = a.get('href')
                    img = a.find('img').get('src') if a.find('img') else ''
                    if title and link:
                        similar_movies.append({
                            'title': title,
                            'link': link,
                            'image': img
                        })
                movie.similar_movies = similar_movies

            # Extract subtitle URL if available (usually in tech specs)
            movie_tech_specs = soup.find('div', {'id': 'movie-tech-specs'})
            if movie_tech_specs:
                tech_spec = movie_tech_specs.find('div', {'class': 'tech-spec-info'})
                if tech_spec:
                    subtitle_link = tech_spec.find('a')
                    if subtitle_link:
                        movie.subtitle_url = subtitle_link.get('href')
                        
        except Exception as e:
            logger.error(f"Error parsing details for {movie.name}: {str(e)}")
            
        return movie
