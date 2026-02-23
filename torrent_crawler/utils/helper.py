import os
import sys
import subprocess
from torrent_crawler.utils.logger import logger

class Helper:
    @staticmethod
    def open_magnet_link(magnet):
        """Opens magnet link"""
        logger.info(f"Helper: Opening magnet link on platform {sys.platform}")
        try:
            if sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
                os.startfile(magnet)
            elif sys.platform.startswith('darwin'):
                subprocess.Popen(['open', magnet], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                subprocess.Popen(['xdg-open', magnet], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            logger.error(f"Helper: Failed to open magnet link: {str(e)}")

    @staticmethod
    def get_downloads_folder():
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
