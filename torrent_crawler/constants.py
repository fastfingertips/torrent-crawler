from torrent_crawler.config import settings

class Constants:
    # movie search constants
    input_types = settings.INPUT_TYPES
    options = settings.OPTIONS
    list_url = settings.URLS.list_url
    search_url = settings.URLS.search_url

    # yts constants
    rotten_tomatoes_critics_rating = settings.RATINGS.rotten_tomatoes_critics_rating
    rotten_tomatoes_audience_rating = settings.RATINGS.rotten_tomatoes_audience_rating
    imdb_rating = settings.RATINGS.imdb_rating
    blu_ray_3d = settings.QUALITIES.blu_ray_3d
    blu_ray_1080p = settings.QUALITIES.blu_ray_1080p
    blu_ray_720p = settings.QUALITIES.blu_ray_720p
    web_1080p = settings.QUALITIES.web_1080p
    web_720p = settings.QUALITIES.web_720p

    # subtitle search constants
    subtitle_base_url = settings.URLS.subtitle_base_url
    subtitle_search_url = settings.URLS.subtitle_search_url
    subtitle_movie_url = settings.URLS.subtitle_movie_url

    # texts
    search_string_text = settings.TEXTS.search_string_text
    selection_text = settings.TEXTS.selection_text
    specific_text = settings.TEXTS.specific_text
    specific_final_option = settings.TEXTS.specific_final_option
    special_final_option = settings.TEXTS.special_final_option
    choose_option_text = settings.TEXTS.choose_option_text
    wrong_option_text = settings.TEXTS.wrong_option_text
    movie_download_text = settings.TEXTS.movie_download_text
    available_torrents_text = settings.TEXTS.available_torrents_text
    no_torrent_text = settings.TEXTS.no_torrent_text
    movie_quality_text = settings.TEXTS.movie_quality_text
    click_link_text = settings.TEXTS.click_link_text
    restart_search_text = settings.TEXTS.restart_search_text
    thanks_text = settings.TEXTS.thanks_text
    download_zip_text = settings.TEXTS.download_zip_text
    another_movies_text = settings.TEXTS.another_movies_text
