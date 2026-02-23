import typer
from typing import Optional
from torrent_crawler.ui.tui import TorrentCrawlerApp
from torrent_crawler.ui.cli import main as cli_main
from torrent_crawler.api.app import run as run_api

app = typer.Typer(
    help="Torrent Crawler - Search and download torrents with style.",
    add_completion=False
)

@app.command(name="tui", help="Start the interactive Textual UI (Recommended)")
def start_tui():
    tui_app = TorrentCrawlerApp()
    tui_app.run()

@app.command(name="cli", help="Start the legacy interactive CLI")
def start_cli():
    cli_main()

@app.command(name="api", help="Start the Flask API server")
def start_api():
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
