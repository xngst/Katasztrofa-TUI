from datetime import datetime
from bs4 import BeautifulSoup
import requests
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()

def fetch_archives(date_str: str):
    """Fetches and parses the archive page for a given date."""
    url = "https://www.katasztrofavedelem.hu/modules/vesz/archivum/"
    params = {"date": date_str, "type": "date"}
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        console.print(f"[bold red]Hálózati hiba történt: {e}[/bold red]")
        return None

def main():
    console.clear()
    console.print(Panel.fit(
        "[bold cyan]BM Országos Katasztrófavédelmi Főigazgatóság[/bold cyan]\n[yellow]Interaktív Archívum Lekérdező (TUI)[/yellow]",
        box=box.ROUNDED
    ))
    
    while True:
        # Prompt user for a date (defaults to today)
        default_date = datetime.now().strftime("%Y-%m-%d")
        date_str = Prompt.ask(
            "\n[bold green]Adja meg a keresett dátumot[/bold green] (YYYY-MM-DD)",
            default=default_date
        )
        
        if date_str.lower() in ["exit", "q", "kilépés"]:
            console.print("[dim]Kilépés... Viszlát![/dim]")
            break
            
        console.print(f"[dim]Adatok lekérdezése erre a napra: {date_str}...[/dim]")
        soup = fetch_archives(date_str)
        
        if not soup:
            continue
            
        dates = [i.text.split(" -")[0].strip() for i in soup.find_all(class_="date")]
        titles = [i.text.strip() for i in soup.find_all(class_="title")]
        
        if not dates:
            console.print(f"[bold yellow]Nincs találat a megadott dátumhoz: {date_str}[/bold yellow]")
            continue
            
        # Build a structured rich table
        table = Table(
            title=f"Katasztrófavédelmi Események ({date_str})", 
            box=box.HEAVY_EDGE,
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Időpont", style="cyan", no_wrap=True)
        table.add_column("Esemény / Cím", style="white")
        
        for d, t in zip(dates, titles):
            table.add_row(d, t)
            
        console.print(table)
        
        # Ask if the user wants to check another date
        if Prompt.ask("\nSzeretne másik dátumot is lekérdezni?", choices=["i", "n"], default="i") == "n":
            console.print("[dim]Köszönöm a használatot, viszlát![/dim]")
            break

if __name__ == "__main__":
    main()
