from rich.console import Console
from torrent_crawler.constants import Constants

console = Console()

class Print:
    @staticmethod
    def bold_string(string):
        console.print(f"[bold]{string}[/bold]")

    @staticmethod
    def long_hash():
        console.print('###########################################')

    @staticmethod
    def wrong_option():
        console.print(f"[red]{Constants.wrong_option_text}[/red]")

    @staticmethod
    def colored_note(note: str):
        console.print(f"[blue]Note::[/blue] {note}")

    @staticmethod
    def option(index: int, option: str):
        console.print(f"[yellow]{index}: {option}[/yellow]")

    @staticmethod
    def thanks():
        console.print(f"\n[blue]{Constants.thanks_text}[/blue]")
