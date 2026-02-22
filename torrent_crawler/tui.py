from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Input, Select, Button, DataTable, Label
from textual.screen import Screen
from textual import work
from textual.message import Message

from torrent_crawler.constants import Constants
from torrent_crawler.services.movie_service import MovieService
from torrent_crawler.services.subtitle_service import SubtitleService
from torrent_crawler.helper import Helper
from torrent_crawler.search import Search, SearchQuery

class MovieDetailScreen(Screen):
    """Screen to show movie details and download links."""
    def __init__(self, movie, app_instance):
        super().__init__()
        self.movie = movie
        self.app_instance = app_instance

    class SubtitlesFetched(Message):
        def __init__(self, subtitles: dict):
            self.subtitles = subtitles
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="detail-container"):
            yield Label(f"[bold]{self.movie.name} ({self.movie.year})[/bold]", id="title")
            
            yield Label("\n[bold]Available Torrents:[/bold]")
            if hasattr(self.movie, 'raw_torrents') and self.movie.raw_torrents:
                available = self.movie.raw_torrents
            else:
                available = self.app_instance.search_handler.get_available_torrents(self.movie.torrents)
            
            if not available:
                yield Label("[red]No torrents available[/red]")
            else:
                for q, link in available.items():
                    safe_id = f"dl_{q.replace('.', '_')}"
                    btn = Button(f"Download {q}", id=safe_id, variant="success")
                    btn.link = link
                    yield btn
            
            if self.movie.subtitle_url:
                yield Label("\n[bold]Subtitles (Fetching...):[/bold]", id="sub-title-label")
                yield DataTable(id="sub-table")
                self.fetch_subtitles()
            
            yield Label("\n")
            yield Button("Back to Results", id="btn_back", variant="error")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id.startswith("dl_"):
            Helper.open_magnet_link(event.button.link)
            self.app.notify(f"Opening magnet link for {event.button.label}")
        elif event.button.id == "btn_subs":
            Helper.open_magnet_link(event.button.link)
            self.app.notify("Opening Subtitle link in browser")
        elif event.button.id == "btn_back":
            self.app.pop_screen()

    @work(thread=True)
    def fetch_subtitles(self) -> None:
        try:
            subtitles = SubtitleService.crawl_movie(self.movie.subtitle_url)
            self.post_message(self.SubtitlesFetched(subtitles))
        except Exception:
            self.post_message(self.SubtitlesFetched({}))

    def on_movie_detail_screen_subtitles_fetched(self, message: SubtitlesFetched) -> None:
        table = self.query_one("#sub-table", DataTable)
        label = self.query_one("#sub-title-label", Label)
        
        if not message.subtitles:
            label.update("\n[bold]Subtitles:[/bold] [red]No subtitles found[/red]")
            table.display = False
            return
            
        label.update("\n[bold]Subtitles:[/bold]")
        table.add_columns("Language", "Rating")
        table.cursor_type = "row"
        self.subtitle_links = {}
        
        row_id = 0
        for lang, subs in message.subtitles.items():
            for sub in subs:
                table.add_row(lang, sub.get('rating', ''), key=str(row_id))
                self.subtitle_links[str(row_id)] = sub.get('link')
                row_id += 1

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id == "sub-table":
            link = self.subtitle_links.get(event.row_key.value)
            if link:
                Helper.download_srt(link)
                self.app.notify(f"Downloading subtitle ZIP: {link}")
class TorrentCrawlerApp(App):
    CSS = """
    #sidebar {
        width: 30;
        dock: left;
        padding: 1;
        background: $boost;
        height: 100%;
    }
    .label {
        margin-top: 1;
    }
    #main-content {
        height: 100%;
        width: 1fr;
    }
    #movie-table {
        height: 1fr;
    }
    #subtitle-table {
        height: 1fr;
        display: none;
    }
    #detail-container {
        padding: 2;
        align: center middle;
    }
    #title {
        text-align: center;
        width: 100%;
        margin-bottom: 2;
        content-align: center middle;
    }
    MovieDetailScreen Button {
        margin: 1;
        width: 100%;
    }
    #sub-table {
        margin: 1;
        height: auto;
    }
    #btn_search, #btn_search_sub {
        width: 100%;
        margin-top: 1;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("down", "focus_next", "Next"),
        ("up", "focus_previous", "Previous"),
        ("right", "focus_next", "Next"),
        ("left", "focus_previous", "Previous"),
    ]

    def on_mount(self):
        self.movies = []
        self.search_handler = Search(SearchQuery("", "", "", 0, "", 0, ""), api_flag=True)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("Search Term", classes="label")
                yield Input(placeholder="e.g. Matrix", id="input_term")
                
                yield Label("Genre", classes="label")
                genre_options = [(g.title(), g) for g in Constants.options['genre']]
                yield Select(genre_options, id="select_genre", value="all")
                
                yield Label("Sort By", classes="label")
                order_options = [(o.title(), o) for o in Constants.options['order']]
                yield Select(order_options, id="select_order", value="latest")
                
                yield Button("Search Movies", id="btn_search", variant="primary")
                yield Button("Search Subtitles", id="btn_search_sub", variant="warning")
            
            with Vertical(id="main-content"):
                yield DataTable(id="movie-table")
                yield DataTable(id="subtitle-table")
                
        yield Footer()

    def on_ready(self) -> None:
        table_movies = self.query_one("#movie-table", DataTable)
        table_movies.add_columns("Title", "Year", "IMDb", "Links")
        table_movies.cursor_type = "row"
        
        table_subs = self.query_one("#subtitle-table", DataTable)
        table_subs.add_columns("Movie Title", "Subtitle Link")
        table_subs.cursor_type = "row"
        
        self.query_one("#input_term", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_search":
            self.action_search()
        elif event.button.id == "btn_search_sub":
            self.action_search_subtitles()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "input_term":
            self.action_search()

    def action_search(self) -> None:
        term = self.query_one("#input_term", Input).value
        if not term:
            self.notify("Please enter a search term", severity="warning")
            return
            
        genre = self.query_one("#select_genre", Select).value
        order = self.query_one("#select_order", Select).value
        
        query = SearchQuery(term, 'all', genre, 0, order, 0, 'all')
        
        movie_table = self.query_one("#movie-table", DataTable)
        sub_table = self.query_one("#subtitle-table", DataTable)
        movie_table.display = True
        sub_table.display = False
        movie_table.clear()
        
        self.notify("Searching... Please wait", timeout=3)
        self.run_search(query)

    class MoviesFetched(Message):
        def __init__(self, movies: list):
            self.movies = movies
            super().__init__()

    class IndependentSubtitlesFetched(Message):
        def __init__(self, subtitles: dict):
            self.subtitles = subtitles
            super().__init__()

    @work(thread=True)
    def run_search_subtitles(self, term: str) -> None:
        import urllib.parse
        try:
            url = SubtitleService.get_search_url(urllib.parse.quote(term), 1)
            # The subtitle service crawl_movie takes an IMDB/movie URL normally.
            # But here we would need a list of movies first to pick a subtitle, or directly use crawl_list.
            # However `crawl_list` in SubtitleService doesn't return anything.
            # Let's write a simple crawler for search results here:
            from curl_cffi import requests
            from bs4 import BeautifulSoup
            req = requests.get(url, impersonate="chrome")
            soup = BeautifulSoup(req.text, features='html5lib')
            media_list = soup.find_all('li', {'class': 'media-movie-clickable'})
            results = {}
            for media in media_list:
                media_body = media.find('div', {'class': 'media-body'})
                media_link = media_body.find('a').get('href')
                media_name = media.find('h3', {'class': 'media-heading'}).text
                full_link = f"https://yifysubtitles.ch{media_link}"
                results[media_name] = full_link
            self.post_message(self.IndependentSubtitlesFetched(results))
        except Exception:
            self.post_message(self.IndependentSubtitlesFetched({}))

    def action_search_subtitles(self) -> None:
        term = self.query_one("#input_term", Input).value
        if not term:
            self.notify("Please enter a search term for subtitles", severity="warning")
            return
            
        movie_table = self.query_one("#movie-table", DataTable)
        sub_table = self.query_one("#subtitle-table", DataTable)
        movie_table.display = False
        sub_table.display = True
        sub_table.clear()
        
        self.notify("Searching subtitles... Please wait", timeout=3)
        self.run_search_subtitles(term)

    def on_torrent_crawler_app_independent_subtitles_fetched(self, message: IndependentSubtitlesFetched) -> None:
        self.movies = [] # Clear movies focus
        table = self.query_one("#subtitle-table", DataTable)
        
        if not message.subtitles:
            self.notify("No subtitle results found.", severity="error")
            return
            
        self.independent_sub_links = {}
        for i, (name, link) in enumerate(message.subtitles.items()):
            table.add_row(name, "[blue]Click to fetch[/blue]", key=f"sub_{i}")
            self.independent_sub_links[f"sub_{i}"] = {"name": name, "url": link}
        
        self.notify(f"Found {len(message.subtitles)} subtitle pages.", severity="information")
        table.focus()

    @work(thread=True)
    def run_search(self, query: SearchQuery) -> None:
        # api_flag=True and print_console=False to ensure clean output without print mess
        service = MovieService(api_flag=True, print_console=False)
        movies = service.crawl_list(query.get_url())
        self.post_message(self.MoviesFetched(movies))

    def on_torrent_crawler_app_movies_fetched(self, message: MoviesFetched) -> None:
        self.movies = message.movies
        table = self.query_one("#movie-table", DataTable)
        
        if not self.movies:
            self.notify("No movies found.", severity="error")
            return
            
        for i, m in enumerate(self.movies):
            links = ", ".join(m.raw_torrents.keys()) if hasattr(m, 'raw_torrents') else ""
            table.add_row(m.name, str(m.year), m.ratings.imdb if hasattr(m, 'ratings') else "", links, key=str(i))
        
        self.notify(f"Found {len(self.movies)} movies.", severity="information")
        table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id == "movie-table":
            key = str(event.row_key.value)
            if key.isdigit() and self.movies:
                idx = int(key)
                movie = self.movies[idx]
                self.push_screen(MovieDetailScreen(movie, self))
        elif event.data_table.id == "subtitle-table":
            key = str(event.row_key.value)
            if key.startswith("sub_") and hasattr(self, 'independent_sub_links'):
                sub_data = self.independent_sub_links.get(key)
                if sub_data:
                    from torrent_crawler.models import Movie
                    dummy_movie = Movie(0, sub_data["name"], "", 0)
                    dummy_movie.subtitle_url = sub_data["url"]
                    dummy_movie.raw_torrents = {}
                    self.push_screen(MovieDetailScreen(dummy_movie, self))

if __name__ == "__main__":
    app = TorrentCrawlerApp()
    app.run()
