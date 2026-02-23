# Torrent Crawler

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

## Usage

### Using the TUI (Recommended)
```bash
python -m torrent_crawler
```

### Using the CLI (Old version)
```bash
python -m torrent_crawler --cli
```

### Using the API
```bash
python -m torrent_crawler --api
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/fastfingertips/torrent-crawler.git
cd torrent-crawler
```

2. Setup virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Contributing
Feel free to fork and submit PRs. This project is currently undergoing a major refactor to improve speed and UI consistency.

---
Developed with focus on speed and ease of use.