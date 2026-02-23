import io
import os
from curl_cffi import requests
import sys
import subprocess
import zipfile
import beaupy
from torrent_crawler.core.constants import Constants
from rich.console import Console

console = Console()


class Helper:
    @staticmethod
    def ask_for_options() -> bool:
        return beaupy.confirm("Proceed?")

    @staticmethod
    def take_int_input(no_of_options) -> int:
        index = None
        while True:
            try:
                index = int(console.input(f"[bold]{Constants.choose_option_text}[/bold]"))
                if 1 <= index <= no_of_options:
                    break
                else:
                    console.print(f"[red]{Constants.wrong_option_text}[/red]")
                    continue
            except ValueError:
                console.print(f"[red]{Constants.wrong_option_text}[/red]")
                continue
        return index

    @staticmethod
    def take_input(input_type, options) -> str:
        if input_type not in Constants.input_types:
            console.print(f"[bold]Wrong input type: {input_type}[/bold]")
            exit(1)
        specific_text = Constants.specific_text[input_type]
        console.print(f"[bold]{specific_text}[/bold]")
        
        # Use beaupy to select from options
        selected = beaupy.select(options, cursor=">", cursor_style="cyan")
        if not selected:
            exit(0) # User cancelled with Esc
        return selected

    @staticmethod
    def take_optional_input(input_type):
        if input_type not in Constants.input_types:
            console.print(f"[bold]Wrong input type: {input_type}[/bold]")
            exit(1)
        
        selection_text = Constants.selection_text[input_type]
        special_final_option = Constants.special_final_option[input_type]
        specific_final_option = Constants.specific_final_option[input_type]
        
        options = Constants.options[input_type]
        
        if beaupy.confirm(selection_text):
            final_option = Helper.take_input(input_type, options)
            console.print(f"[blue]Note::[/blue] {specific_final_option.format(final_option)}")
            return final_option
        
        console.print(f"[blue]Note::[/blue] {special_final_option}")
        return options[0]

    @staticmethod
    def update_progress(index, total):
        """Show update progress for index out of total"""
        bar_length = 30
        status = ""
        if total == 0:
            progress = 0
        else:
            progress = index / total
        if isinstance(progress, int):
            progress = float(progress)
        if not isinstance(progress, float):
            progress = 0
            status = "error: progress var must be float\r\n"
        if progress < 0:
            progress = 0
            status = "Halt...\r\n"
        if progress >= 1:
            progress = 1
            status = "Done...\r\n"
        block = int(round(bar_length * progress))
        text = "\rCrawling like a snake: [blue][{0}][/blue] {1}% [{2}/{3}] {4}".format(
            "=" * block + "-" * (bar_length - block), int(progress * 100), index, total, status)
        console.print(text, end="")

    @staticmethod
    def open_magnet_link(magnet):
        """Opens magnet link"""
        if sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
            os.startfile(magnet)
        elif sys.platform.startswith('darwin'):
            subprocess.Popen(['open', magnet], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            subprocess.Popen(['xdg-open', magnet], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @staticmethod
    def __get_downloads_folder():
        """Returns the default downloads path for linux or windows"""
        if os.name == 'nt':
            import winreg
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location = winreg.QueryValueEx(key, downloads_guid)[0]
            return location
        return os.path.join(os.path.expanduser('~'), 'Downloads', 'subtitles')

    @staticmethod
    def __get_zip_file(url):
        """Downloads zipped files from url"""
        r = requests.get(url, impersonate="chrome")
        return zipfile.ZipFile(io.BytesIO(r.content))

    @staticmethod
    def download_srt(url):
        """Downloads and extracts .srt file from zip url"""
        my_zip = Helper.__get_zip_file(url)
        storage_path = Helper.__get_downloads_folder()
        console.print(f"[bold]{Constants.download_zip_text.format('', storage_path)}[/bold]")
        for file in my_zip.namelist():
            if my_zip.getinfo(file).filename.endswith('.srt'):
                my_zip.extract(file, storage_path)  # extract the file to current folder if it is a text file
