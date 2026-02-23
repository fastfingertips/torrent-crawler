import sys
from torrent_crawler.ui.tui import TorrentCrawlerApp
from torrent_crawler.ui.cli import main as cli_main

def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == '--cli':
            cli_main()
        elif arg == '--api':
            from torrent_crawler.api.app import run as run_api
            run_api()
    else:
        app = TorrentCrawlerApp()
        app.run()

if __name__ == "__main__":
    main()
