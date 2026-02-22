from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Input, Select, Button, DataTable, Label
from textual.screen import Screen
from textual import work
from textual.message import Message

from torrent_crawler.constants import Constants
from torrent_crawler.services.movie_service import MovieService
from torrent_crawler.helper import Helper
from torrent_crawler.search import Search, SearchQuery

class MovieDetailScreen(Screen):
    """Screen to show movie details and download links."""
    def __init__(self, movie, app_instance):
        super().__init__()
        self.movie = movie
        self.app_instance = app_instance

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
                    btn = Button(f"Download {q}", id=f"dl_{q}", variant="success")
                    btn.link = link
                    yield btn
            
            if self.movie.subtitle_url:
                yield Label("\n[bold]Subtitles:[/bold]")
                subtitle_btn = Button("Download Subtitles (Web)", id="btn_subs", variant="primary")
                subtitle_btn.link = self.movie.subtitle_url
                yield subtitle_btn
            
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
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
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
            
            with Vertical(id="main-content"):
                yield DataTable(id="movie-table")
                
        yield Footer()

    def on_ready(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Title", "Year", "IMDb", "Links")
        table.cursor_type = "row"
        self.query_one("#input_term", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_search":
            self.action_search()

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
        self.query_one(DataTable).clear()
        self.notify("Searching... Please wait", timeout=3)
        self.run_search(query)

    class MoviesFetched(Message):
        def __init__(self, movies: list):
            self.movies = movies
            super().__init__()

    @work(thread=True)
    def run_search(self, query: SearchQuery) -> None:
        # api_flag=True and print_console=False to ensure clean output without print mess
        service = MovieService(api_flag=True, print_console=False)
        movies = service.crawl_list(query.get_url())
        self.post_message(self.MoviesFetched(movies))

    def on_torrent_crawler_app_movies_fetched(self, message: MoviesFetched) -> None:
        self.movies = message.movies
        table = self.query_one(DataTable)
        if not self.movies:
            self.notify("No movies found.", severity="error")
            return
            
        for i, m in enumerate(self.movies):
            links = ", ".join(m.raw_torrents.keys()) if hasattr(m, 'raw_torrents') else ""
            table.add_row(m.name, str(m.year), m.ratings.imdb if hasattr(m, 'ratings') else "", links, key=str(i))
        
        self.notify(f"Found {len(self.movies)} movies.", severity="information")
        table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        idx = int(event.row_key.value)
        movie = self.movies[idx]
        self.push_screen(MovieDetailScreen(movie, self))

if __name__ == "__main__":
    app = TorrentCrawlerApp()
    app.run()
