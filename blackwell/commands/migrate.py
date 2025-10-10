"""Migrate Command - Provider and mode migration"""

import typer
from rich.console import Console

app = typer.Typer(help="= Migrate between providers and modes")
console = Console()

@app.command()
def cms(name: str = typer.Argument(..., help="Client name")):
    """Migrate CMS provider."""
    console.print(f"Migrating CMS for: {name}")
    console.print("[yellow]This command is under development[/yellow]")