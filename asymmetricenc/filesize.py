

# demo_cli.py

from rich.console import Console
from rich.text import Text
from rich.table import Table
from colorama import Fore, Style, init
from alive_progress import alive_bar
import pyfiglet
import time

# Init colorama (for Windows compatibility)
init(autoreset=True)

console = Console()

def show_pyfiglet_banner():
    banner = pyfiglet.figlet_format("CLI DEMO", font="slant")
    console.print(banner, style="bold cyan")

def show_rich_colors():
    console.rule("[bold yellow]Rich Colors Demo[/bold yellow]")
    console.print("Normal text")
    console.print("[bold red]Bold Red[/bold red]")
    console.print("[green]Green[/green]")
    console.print("[blue underline]Blue Underlined[/blue underline]")
    console.print("[magenta italic]Magenta Italic[/magenta italic]")
    console.print("[reverse cyan]Cyan Background[/reverse cyan]")

def show_colorama_colors():
    console.rule("[bold yellow]Colorama Colors Demo[/bold yellow]")
    print(Fore.RED + "Red text" + Style.RESET_ALL)
    print(Fore.GREEN + "Green text" + Style.RESET_ALL)
    print(Fore.BLUE + "Blue text" + Style.RESET_ALL)
    print(Fore.YELLOW + "Yellow text" + Style.RESET_ALL)

def show_rich_table():
    console.rule("[bold yellow]Rich Table Demo[/bold yellow]")
    table = Table(title="User List")
    table.add_column("Username", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_row("Alice", "[green]Online[/green]")
    table.add_row("Bob", "[red]Offline[/red]")
    table.add_row("Charlie", "[yellow]Away[/yellow]")
    console.print(table)

def show_alive_progress():
    console.rule("[bold yellow]Alive Progress Demo[/bold yellow]")
    with alive_bar(5, title="Downloading") as bar:
        for i in range(5):
            time.sleep(0.5)  # simulate work
            bar()

def main():
    show_pyfiglet_banner()
    time.sleep(1)

    show_rich_colors()
    time.sleep(1)

    show_colorama_colors()
    time.sleep(1)

    show_rich_table()
    time.sleep(1)

    show_alive_progress()

    console.rule("[bold green]Demo Finished[/bold green]")

if __name__ == "__main__":
    main()
