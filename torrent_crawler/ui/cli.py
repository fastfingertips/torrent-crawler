import signal

import beaupy
from rich.console import Console

from torrent_crawler.core import constants as consts
from torrent_crawler.core.models import Movie, SearchQuery, Torrents
from torrent_crawler.providers.subtitles import SubtitleProvider
from torrent_crawler.services.download_service import DownloadService
from torrent_crawler.services.movie_service import MovieService
from torrent_crawler.utils.logger import logger

console = Console()


class CLIInputManager:
    @staticmethod
    def take_input(input_type, options) -> str:
        if input_type not in consts.INPUT_TYPES:
            console.print(f"[bold]Wrong input type: {input_type}[/bold]")
            exit(1)
        specific_text = consts.SPECIFIC_TEXT[input_type]
        console.print(f"[bold]{specific_text}[/bold]")

        selected = beaupy.select(options, cursor=">", cursor_style="cyan")
        if not selected:
            exit(0)
        return selected

    @staticmethod
    def take_optional_input(input_type):
        if input_type not in consts.INPUT_TYPES:
            console.print(f"[bold]Wrong input type: {input_type}[/bold]")
            exit(1)

        selection_text = consts.SELECTION_TEXT[input_type]
        special_final_option = consts.SPECIAL_FINAL_OPTION[input_type]
        specific_final_option = consts.SPECIFIC_FINAL_OPTION[input_type]
        options = consts.OPTIONS[input_type]

        if beaupy.confirm(selection_text):
            final_option = CLIInputManager.take_input(input_type, options)
            console.print(f"[blue]Note::[/blue] {specific_final_option.format(final_option)}")
            return final_option

        console.print(f"[blue]Note::[/blue] {special_final_option}")
        return options[0]


def sigint_handler(signum, frame):
    console.print(f"\n[blue]{consts.THANKS_TEXT}[/blue]")
    exit(1)


signal.signal(signal.SIGINT, sigint_handler)


class Search:
    def __init__(self, search_query: SearchQuery, api_flag: bool = False):
        self.search_query = search_query
        self.api_flag = api_flag

    def get_available_torrents(self, torrents: Torrents) -> dict:
        available_torrents = {}
        if self.search_query.quality in ["all", "3D"] and torrents.br3d:
            available_torrents["3D.BluRay"] = torrents.br3d
        if self.search_query.quality in ["all", "720"] and torrents.br720:
            available_torrents["720p.BluRay"] = torrents.br720
        if self.search_query.quality in ["all", "1080"] and torrents.br1080:
            available_torrents["1080p.BluRay"] = torrents.br1080
        if self.search_query.quality in ["all", "720"] and torrents.web720:
            available_torrents["720p.WEB"] = torrents.web720
        if self.search_query.quality in ["all", "1080"] and torrents.web1080:
            available_torrents["1080p.WEB"] = torrents.web1080
        return available_torrents

    MoviesList = list[Movie]

    def show_movies(self, movies: MoviesList):
        console.print("[bold]Select a movie: [/bold]")
        choices = [f"{ind + 1}: {movie.name} ({movie.year})" for ind, movie in enumerate(movies)]
        selected_choice = beaupy.select(choices, cursor=">", cursor_style="cyan")

        if not selected_choice:
            return

        mid = int(selected_choice.split(":")[0])
        movie_selected = movies[mid - 1]
        logger.info(f"CLI: User selected movie: {movie_selected.name}")

        # Fetch full details (magnets, etc) now that user picked one
        service = MovieService()
        movie_selected = service.crawl_movie(movie_selected)

        console.print(f"[bold]{consts.AVAILABLE_TORRENTS_TEXT}[/bold]")

        if hasattr(movie_selected, "raw_torrents"):
            available_torrents = movie_selected.raw_torrents
        else:
            available_torrents = self.get_available_torrents(movie_selected.torrents)

        if len(available_torrents) == 0:
            console.print(f"[red]{consts.NO_TORRENT_TEXT}[/red]")
        else:
            available_keys = list(available_torrents.keys())
            if len(available_torrents) == 1:
                if beaupy.confirm(f"Download {available_keys[0]}?"):
                    torrent_link = available_torrents[available_keys[0]]
                    DownloadService().open_magnet_link(torrent_link)
                    console.print(f"{consts.CLICK_LINK_TEXT} [red]{torrent_link}[/red]")
            else:
                console.print("[bold]Select quality:[/bold]")
                selected_quality = beaupy.select(available_keys, cursor=">", cursor_style="cyan")
                if selected_quality:
                    torrent_link = available_torrents[selected_quality]
                    DownloadService().open_magnet_link(torrent_link)
                    console.print(f"{consts.CLICK_LINK_TEXT} [red]{torrent_link}[/red]")

            if movie_selected.subtitle_url and movie_selected.subtitle_url != "":
                if beaupy.confirm(consts.SELECTION_TEXT["subtitle"]):
                    subtitle_prov = SubtitleProvider()
                    subtitles = subtitle_prov.crawl_movie(movie_selected.subtitle_url)
                    if subtitles:
                        lang = CLIInputManager.take_input("subtitle", list(subtitles.keys()))
                        subtitle_link = subtitles[lang][0]["link"]
                        downloaded_path = DownloadService().download_and_extract_subtitle(subtitle_link)
                        if downloaded_path:
                            console.print(f"[bold]{consts.DOWNLOAD_ZIP_TEXT.format('', downloaded_path)}[/bold]")

            if beaupy.confirm(consts.ANOTHER_MOVIES_TEXT.format("", self.search_query.search_term)):
                self.show_movies(movies)

    def start(self, search_query: SearchQuery):
        crawler = MovieService(api_flag=self.api_flag)
        movies = crawler.crawl_list(search_query)
        if self.api_flag is True:
            return movies
        self.show_movies(movies)


class SearchInput:
    @staticmethod
    def create_query() -> SearchQuery:
        s = console.input("[bold cyan]❯[/bold cyan] Please enter search string: ")
        while not s:
            s = console.input("[bold cyan]❯[/bold cyan] Please enter search string: ")

        q = "all"
        g = CLIInputManager.take_optional_input("genre")
        o = CLIInputManager.take_optional_input("order")

        logger.info(f"CLI: Validated search query created: term='{s}', genre='{g}', order='{o}'")
        return SearchQuery(s, q, g, 0, o, 0, "all")


def main():
    while True:
        query = SearchInput.create_query()
        search_engine = Search(query)
        search_engine.start(query)
        if not beaupy.confirm(consts.RESTART_SEARCH_TEXT):
            console.print(f"\n[blue]{consts.THANKS_TEXT}[/blue]")
            break


if __name__ == "__main__":
    main()
