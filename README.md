# Torrent Crawler
> **Note:** This is an enhanced fork of the original [torrent-crawler](https://github.com/rajat19/torrent-crawler) by [Rajat Srivastava](https://github.com/rajat19).

[![License](https://img.shields.io/github/license/fastfingertips/torrent-crawler?style=for-the-badge)](https://github.com/fastfingertips/torrent-crawler/blob/master/LICENSE)
![Python](https://img.shields.io/pypi/pyversions/search-torrent?style=for-the-badge)
[![GitHub last commit](https://img.shields.io/github/last-commit/fastfingertips/torrent-crawler?style=for-the-badge)](https://github.com/fastfingertips/torrent-crawler/commits/revive-crawler)

A lightweight and high-performance Terminal User Interface (TUI) for searching movie torrents and subtitles simultaneously. Built with Python and Textual.

## Features

- **Blazing Fast**: Uses `curl_cffi` for high-performance requests, bypassing basic web protections.
- **Dual View TUI**: Side-by-side or stacked view of Movies and Subtitles.
- **Simultaneous Search**: Single search triggers both Movie and Subtitle lookup.
- **Automatic Subtitle Matching**: Finds the exact correct subtitle URL directly from the movie source.
- **Robust Crawler**: Built-in error handling and pagination management to handle large search results without crashing.
- **Rich Metadata**: Extracts synopsis, genres, likes, and similar movies.
- **Modern Logging**: Integrated with Loguru for detailed performance tracking and debugging.

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

## Contributing
Feel free to fork and submit PRs. This project is currently undergoing a major refactor to improve speed and UI consistency.

---

## Credits
This project is a modernized version of the original [torrent-crawler](https://github.com/rajat19/torrent-crawler) created by [Rajat Srivastava](https://github.com/rajat19). Special thanks to him for the initial foundation.

Developed with focus on speed and ease of use.