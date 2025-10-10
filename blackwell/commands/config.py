"""
Config Command - Manage CLI configuration and settings

Handles:
- Reading and writing configuration files
- Managing workspace settings
- Provider credentials and authentication
- CLI preferences and defaults
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
from typing import Optional

from blackwell.core.config_manager import ConfigManager

app = typer.Typer(help="Manage CLI configuration and settings")
console = Console()


@app.command()
def show(
    section: Optional[str] = typer.Option(None, "--section", "-s", help="Show specific config section")
):
    """
    Show current configuration settings.
    """
    console.print("[bold blue]Current Configuration[/bold blue]")
    
    try:
        config_manager = ConfigManager()
        
        if not config_manager.config_path.exists():
            console.print("[yellow]No configuration found. Run 'blackwell init workspace' to initialize.[/yellow]")
            return
        
        config_data = config_manager.config.model_dump()
        
        if section:
            if section in config_data:
                console.print(f"[bold cyan]{section}:[/bold cyan]")
                for key, value in config_data[section].items():
                    console.print(f"  {key}: {value}")
            else:
                console.print(f"[red]Section '{section}' not found in configuration.[/red]")
        else:
            table = Table(title="Configuration Settings")
            table.add_column("Section", style="cyan")
            table.add_column("Key", style="green") 
            table.add_column("Value", style="yellow")
            
            for section_name, section_data in config_data.items():
                if isinstance(section_data, dict):
                    for key, value in section_data.items():
                        table.add_row(section_name, key, str(value))
                else:
                    table.add_row(section_name, "", str(section_data))
            
            console.print(table)
            
    except Exception as e:
        console.print(f"[red]Error reading configuration: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def set(
    key: str = typer.Argument(..., help="Configuration key (section.key format)"),
    value: str = typer.Argument(..., help="Configuration value"),
):
    """
    Set a configuration value.
    
    Use dot notation for nested keys: section.key
    """
    console.print("[bold blue]Setting Configuration[/bold blue]")
    
    try:
        config_manager = ConfigManager()

        if '.' not in key:
            # Handle top-level keys
            config_manager.set(key, value)
        else:
            # Handle nested keys
            section, config_key = key.split('.', 1)
            config_manager.set(f"{section}.{config_key}", value)
        
        console.print(f"[green]Set {key} = {value}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error setting configuration: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def unset(
    key: str = typer.Argument(..., help="Configuration key to remove (section.key format)"),
):
    """
    Remove a configuration value.
    """
    console.print("[bold blue]Removing Configuration[/bold blue]")
    
    try:
        config_manager = ConfigManager()

        if '.' not in key:
            # Handle top-level keys
            config_manager.remove(key)
        else:
            # Handle nested keys
            section, config_key = key.split('.', 1)
            config_manager.remove(f"{section}.{config_key}")
        
        console.print(f"[green]Removed {key}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error removing configuration: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def reset():
    """
    Reset configuration to defaults.
    """
    console.print("[bold blue]Resetting Configuration[/bold blue]")
    
    if not typer.confirm("This will reset all configuration to defaults. Continue?"):
        console.print("[yellow]Reset cancelled.[/yellow]")
        return
    
    try:
        config_manager = ConfigManager()
        config_manager.reset_to_defaults()
        
        console.print("[green]Configuration reset to defaults[/green]")
        
    except Exception as e:
        console.print(f"[red]Error resetting configuration: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def path():
    """
    Show configuration file path.
    """
    try:
        config_manager = ConfigManager()
        console.print(f"Configuration file: {config_manager.config_path}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)