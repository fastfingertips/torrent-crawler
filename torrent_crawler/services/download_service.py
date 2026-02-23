import os
import io
import sys
import zipfile
import subprocess
from torrent_crawler.utils.logger import logger
from torrent_crawler.providers.base import HTTPClient

class DownloadService:
    def __init__(self, http_client: HTTPClient = None):
        self.http_client = http_client if http_client else HTTPClient()

    def get_downloads_folder(self) -> str:
        """Returns the default downloads path for linux or windows"""
        if os.name == 'nt':
            try:
                import winreg
                sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
                downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                    location = winreg.QueryValueEx(key, downloads_guid)[0]
                return location
            except Exception:
                pass
        return os.path.join(os.path.expanduser('~'), 'Downloads', 'subtitles')

    def download_and_extract_subtitle(self, url: str) -> str:
        """Downloads and extracts .srt file from zip url using shared session. Returns the storage path if successful."""
        logger.info(f"DownloadService: Starting subtitle download from {url}")
        try:
            r = self.http_client.get(url)
            my_zip = zipfile.ZipFile(io.BytesIO(r.content))
            
            storage_path = self.get_downloads_folder()
            if not os.path.exists(storage_path):
                os.makedirs(storage_path, exist_ok=True)
                
            for file in my_zip.namelist():
                if file.endswith('.srt'):
                    logger.debug(f"DownloadService: Extracting subtitle file: {file}")
                    my_zip.extract(file, storage_path)
            logger.info(f"DownloadService: Subtitles extracted to {storage_path}")
            return storage_path
        except Exception as e:
            logger.error(f"DownloadService: Failed to download/extract subtitles: {str(e)}")
            return None

    def open_magnet_link(self, magnet: str) -> None:
        """Opens magnet link using system's default torrent client"""
        logger.info(f"DownloadService: Opening magnet link on platform {sys.platform}")
        try:
            if sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
                os.startfile(magnet)
            elif sys.platform.startswith('darwin'):
                subprocess.Popen(['open', magnet], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                subprocess.Popen(['xdg-open', magnet], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            logger.error(f"DownloadService: Failed to open magnet link: {str(e)}")
