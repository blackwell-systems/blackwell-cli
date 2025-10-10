"""Cost Command - Cost estimation and optimization"""

import typer
from rich.console import Console

app = typer.Typer(help="💰 Estimate costs and optimize spending")
console = Console()

@app.command()
def estimate(name: str = typer.Argument(..., help="Client name")):
    """Estimate monthly costs for a client."""
    console.print(f"Estimating costs for: {name}")
    console.print("[yellow]This command is under development[/yellow]")
