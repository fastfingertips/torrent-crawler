import typer

from torrent_crawler.api.app import run as run_api
from torrent_crawler.ui.cli import main as cli_main
from torrent_crawler.ui.tui import TorrentCrawlerApp
from torrent_crawler.utils.logger import enable_console_logging, logger

app = typer.Typer(help="Torrent Crawler - Search and download torrents with style.", add_completion=False)


@app.command(name="tui", help="Start the interactive Textual UI (Recommended)")
def start_tui():
    logger.info("Starting Torrent Crawler in TUI mode")
    tui_app = TorrentCrawlerApp()
    tui_app.run()


@app.command(name="cli", help="Start the legacy interactive CLI")
def start_cli():
    logger.info("Starting Torrent Crawler in CLI mode")
    cli_main()


@app.command(name="api", help="Start the Flask API server")
def start_api():
    enable_console_logging()
    logger.info("Starting Torrent Crawler API server")
    run_api()


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    """
    If no command is provided, default to TUI.
    """
    if ctx.invoked_subcommand is None:
        start_tui()


def main():
    app()


if __name__ == "__main__":
    main()
