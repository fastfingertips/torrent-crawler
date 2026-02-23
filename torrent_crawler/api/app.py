from flask import Flask, request, jsonify
from torrent_crawler.services.movie_service import MovieService
from torrent_crawler.core.models import SearchQuery
from torrent_crawler.utils.logger import logger

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "Torrent Crawler API is running!"})

@app.route('/movies', methods=['GET'])
def get_movies():
    search_string = request.args.get('search')
    if not search_string:
        logger.warning("API: Search request received without search term")
        return jsonify({"error": "Search term is required"}), 400
        
    order_by = request.args.get('order') or "latest"
    genre = request.args.get('genre') or "all"
    quality = request.args.get('quality') or "all"
    
    logger.info(f"API: Searching for '{search_string}' (genre: {genre}, order: {order_by})")
    
    try:
        search_query = SearchQuery(search_string, quality, genre, 0, order_by)
        service = MovieService(api_flag=True)
        movies = service.crawl_list(search_query)
        
        result = [movie.to_dict() for movie in movies]
        count = len(result)
        
        logger.info(f"API: Found {count} movies for '{search_string}'")
        
        return jsonify({
            'count': count,
            'message': f'Total {count} movies found',
            'result': result
        })
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

def run():
    logger.info("Starting Flask API server on port 5000")
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    run()
