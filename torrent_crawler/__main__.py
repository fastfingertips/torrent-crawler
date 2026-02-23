import sys
from torrent_crawler.ui.tui import TorrentCrawlerApp
from torrent_crawler.ui.cli import main as cli_main

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        cli_main()
    else:
        app = TorrentCrawlerApp()
        app.run()

if __name__ == "__main__":
    main()
