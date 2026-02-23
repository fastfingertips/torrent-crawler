# Torrent Crawler
> **Note:** This is an enhanced fork of the original [torrent-crawler](https://github.com/rajat19/torrent-crawler) by [Rajat Srivastava](https://github.com/rajat19).

[![License](https://img.shields.io/github/license/fastfingertips/torrent-crawler?style=for-the-badge)](https://github.com/fastfingertips/torrent-crawler/blob/master/LICENSE)
![Python](https://img.shields.io/pypi/pyversions/search-torrent?style=for-the-badge)
[![GitHub last commit](https://img.shields.io/github/last-commit/fastfingertips/torrent-crawler?style=for-the-badge)](https://github.com/fastfingertips/torrent-crawler/commits/revive-crawler)

A Terminal User Interface (TUI) for searching movie torrents and subtitles. Built with Python and Textual.

## Features

- **Requests**: Uses `curl_cffi` for browser-impersonated HTTP requests.
- **Dual View TUI**: View of Movies and Subtitles.
- **Simultaneous Search**: Triggers both Movie and Subtitle lookup.
- **Automatic Subtitle Matching**: Finds subtitle URLs directly from the movie source.
- **Crawler**: Built-in error handling and pagination management.
- **Metadata**: Extracts synopsis, genres, and similar movies.
- **Logging**: Integrated with Loguru for tracking and debugging.

## Usage

### Using the TUI (Recommended)
```bash
python main.py
# or
python -m torrent_crawler
```

### Using the CLI (Old version)
```bash
python main.py cli
# or
python -m torrent_crawler cli
```

### Using the API
```bash
python main.py api
# or
python -m torrent_crawler api
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/fastfingertips/torrent-crawler.git
cd torrent-crawler
```

2. Setup virtual environment and install dependencies using `uv` (recommended for speed):
```bash
# If you don't have uv installed: pip install uv
uv venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

uv pip install -e .
```

*Alternatively, with standard pip:*
```bash
python -m venv .venv
# activate venv...
pip install .
```

## Dependencies Breakdown

This project uses the following dependencies:

- **textual**: The engine for the TUI.
- **curl_cffi**: HTTP client that impersonates browsers.
- **typer**: Manages CLI entry points.
- **beautifulsoup4 & lxml**: Used for parsing HTML.
- **Flask**: Powers the local API server.
- **dynaconf**: Configuration manager.
- **loguru**: Logging library.
- **rich**: Provides formatting for the CLI and TUI.
- **beaupy**: Used in the legacy CLI mode.

## Contributing
Feel free to fork and submit PRs. This project is currently undergoing a major refactor to improve speed and UI consistency.

---

## Credits

This project is a version of the original [torrent-crawler](https://github.com/rajat19/torrent-crawler) created by [Rajat Srivastava](https://github.com/rajat19).

Search and download torrents.