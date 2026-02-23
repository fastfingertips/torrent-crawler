from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Input, Select, Button, DataTable, Label
from textual.screen import Screen
from textual import work
from textual.message import Message

from torrent_crawler.core.constants import Constants
from torrent_crawler.services.movie_service import MovieService
from torrent_crawler.services.subtitle_service import SubtitleService
from torrent_crawler.utils.helper import Helper
from torrent_crawler.core.models import Movie, SearchQuery
from torrent_crawler.ui.cli import Search


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
            # Header Section
            yield Label(f"[bold cyan]{self.movie.name} ({self.movie.year})[/bold cyan]", id="detail-title")
            
            # Metadata Row
            meta_info = []
            if self.movie.genres:
                meta_info.append(f"[yellow]{' / '.join(self.movie.genres)}[/yellow]")
            if self.movie.likes:
                meta_info.append(f"[red]❤ {self.movie.likes} Likes[/red]")
            if hasattr(self.movie, 'ratings') and self.movie.ratings:
                meta_info.append(f"[bold gold3]⭐ {self.movie.ratings.imdb} IMDb[/bold gold3]")
            
            if meta_info:
                yield Label(" | ".join(meta_info), id="detail-meta")

            # Synopsis
            if self.movie.synopsis:
                yield Label("\n[bold]Synopsis:[/bold]")
                yield Label(f"[italic]{self.movie.synopsis}[/italic]", id="detail-synopsis")

            # Actions Row
            with Horizontal(id="detail-actions"):
                if self.movie.trailer:
                    btn_trailer = Button("Watch Trailer", id="btn_trailer", variant="primary")
                    btn_trailer.link = self.movie.trailer
                    yield btn_trailer
                
                yield Button("Back to Results", id="btn_back", variant="error")

            # Torrents Section
            yield Label("\n[bold]Available Torrents:[/bold]")
            if hasattr(self.movie, 'raw_torrents') and self.movie.raw_torrents:
                available = self.movie.raw_torrents
            else:
                available = self.app_instance.search_handler.get_available_torrents(self.movie.torrents)
            
            if not available:
                yield Label("[red]No torrents available[/red]")
            else:
                with Horizontal(id="torrent-buttons"):
                    for q, link in available.items():
                        safe_id = f"dl_{q.replace('.', '_')}"
                        btn = Button(f"Download {q}", id=safe_id, variant="success")
                        btn.link = link
                        yield btn
            
            # Subtitles Section
            if self.movie.subtitle_url:
                yield Label("\n[bold]Subtitles (Fetching...):[/bold]", id="sub-title-label")
                yield DataTable(id="sub-table")
                self.fetch_subtitles()
            
            yield Label("\n")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id.startswith("dl_"):
            Helper.open_magnet_link(event.button.link)
            self.app.notify(f"Opening magnet link for {event.button.label}")
        elif event.button.id == "btn_trailer":
            Helper.open_magnet_link(event.button.link)
            self.app.notify("Opening Trailer in browser")
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
    #tables-container {
        width: 1fr;
        height: 100%;
    }
    #movie-table, #subtitle-table {
        height: 1fr;
        width: 100%;
        margin: 0 1;
    }
    .table-label {
        margin: 1 0 0 1;
        text-style: bold;
        color: $accent;
    }
    #detail-container {
        padding: 2;
    }
    #detail-title {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
        content-align: center middle;
        background: $boost;
        padding: 1;
    }
    #detail-meta {
        text-align: center;
        width: 100%;
        color: $text-muted;
    }
    #detail-synopsis {
        padding: 1;
        background: $surface;
        border-left: solid $accent;
        margin: 1 0;
    }
    #detail-actions, #torrent-buttons {
        height: auto;
        margin: 1 0;
    }
    MovieDetailScreen Button {
        margin-right: 1;
        width: auto;
        min-width: 15;
    }
    #sub-table {
        margin: 1;
        height: auto;
    }
    #btn_search {
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
                
                yield Button("Search", id="btn_search", variant="primary")
            
            with Vertical(id="main-content"):
                with Vertical(id="tables-container"):
                    yield Label("Movies", classes="table-label")
                    yield DataTable(id="movie-table")
                    yield Label("Subtitles", classes="table-label")
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
        movie_table.clear()
        sub_table.clear()
        
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
        movies = service.crawl_list(query)
        self.post_message(self.MoviesFetched(movies))

    def on_torrent_crawler_app_movies_fetched(self, message: MoviesFetched) -> None:
        self.movies = message.movies
        table_movies = self.query_one("#movie-table", DataTable)
        table_subs = self.query_one("#subtitle-table", DataTable)
        
        if not self.movies:
            self.notify("No movies found.", severity="error")
            return
            
        self.independent_sub_links = {}
        for i, m in enumerate(self.movies):
            links = ", ".join(m.raw_torrents.keys()) if hasattr(m, 'raw_torrents') else ""
            table_movies.add_row(m.name, str(m.year), m.ratings.imdb if hasattr(m, 'ratings') else "", links, key=str(i))
            
            if hasattr(m, 'subtitle_url') and m.subtitle_url:
                table_subs.add_row(m.name, "[blue]Click to fetch subtitles[/blue]", key=f"sub_{i}")
                self.independent_sub_links[f"sub_{i}"] = {"name": m.name, "url": m.subtitle_url}
        
        self.notify(f"Found {len(self.movies)} movies.", severity="information")
        table_movies.focus()

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
                    dummy_movie = Movie(0, sub_data["name"], "", 0)
                    dummy_movie.subtitle_url = sub_data["url"]
                    dummy_movie.raw_torrents = {}
                    self.push_screen(MovieDetailScreen(dummy_movie, self))


if __name__ == "__main__":
    app = TorrentCrawlerApp()
    app.run()
