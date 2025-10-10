"""
List Command - List clients, providers, and deployments

Handles:
- Listing all clients in workspace
- Showing provider information and availability
- Displaying deployment status and history
- Showing template catalog
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional

from blackwell.core.config_manager import ConfigManager
from blackwell.core.client_manager import ClientManager

app = typer.Typer(help="List clients, providers, and deployments")
console = Console()


@app.command()
def clients(
    workspace: Optional[str] = typer.Option(None, "--workspace", "-w", help="Workspace path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
):
    """
    List all clients in the workspace.
    
    Shows client names, types, deployment status, and basic configuration.
    """
    console.print("=� [bold blue]Listing Clients[/bold blue]")
    
    try:
        config_manager = ConfigManager()
        client_manager = ClientManager(config_manager)
        
        clients_list = client_manager.list_clients()
        
        if not clients_list:
            console.print("[yellow]No clients found in workspace.[/yellow]")
            console.print("[dim]Run 'blackwell create client' to create your first client.[/dim]")
            return
        
        table = Table(title="Clients in Workspace")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Type", style="green")
        table.add_column("Status", style="yellow")
        
        if verbose:
            table.add_column("Providers", style="blue")
            table.add_column("Last Deploy", style="magenta")
        
        for client in clients_list:
            row = [client.get("name", "Unknown"), client.get("type", "Unknown"), client.get("status", "Unknown")]
            
            if verbose:
                providers = ", ".join(client.get("providers", []))
                last_deploy = client.get("last_deploy", "Never")
                row.extend([providers, last_deploy])
            
            table.add_row(*row)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing clients: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def providers(
    available_only: bool = typer.Option(False, "--available", help="Show only available providers"),
):
    """
    List all supported providers and their status.
    
    Shows CMS, e-commerce, and infrastructure providers with availability status.
    """
    console.print("=� [bold blue]Listing Providers[/bold blue]")
    
    # This would typically fetch from provider registry
    providers_data = {
        "CMS": ["Decap CMS", "Tina CMS", "Sanity", "Contentful"],
        "E-commerce": ["Snipcart", "Stripe", "Shopify", "WooCommerce"],
        "Infrastructure": ["AWS", "Vercel", "Netlify", "Railway"]
    }
    
    for category, providers in providers_data.items():
        table = Table(title=f"{category} Providers")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Cost Range", style="yellow")
        
        for provider in providers:
            # Mock status and cost data
            status = " Available" if not available_only else " Available"
            cost = "$5-50/month"  # This would come from cost calculator
            table.add_row(provider, status, cost)
        
        console.print(table)
        console.print()


@app.command()
def deployments(
    client: Optional[str] = typer.Option(None, "--client", "-c", help="Filter by client name"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
):
    """
    List deployment history and status.
    
    Shows recent deployments with status, timestamps, and basic metrics.
    """
    console.print("=� [bold blue]Listing Deployments[/bold blue]")
    
    try:
        config_manager = ConfigManager()
        
        # This would fetch actual deployment data
        console.print("[yellow]No deployments found.[/yellow]")
        console.print("[dim]Run 'blackwell deploy' to create your first deployment.[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error listing deployments: {e}[/red]")
        raise typer.Exit(1)


@app.command() 
def templates(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by template category"),
):
    """
    List available client templates.
    
    Shows template catalog with descriptions and provider combinations.
    """
    console.print("=� [bold blue]Available Templates[/bold blue]")
    
    # Mock template data - this would come from template registry
    templates_data = [
        {"name": "Blog + E-commerce", "cms": "Decap CMS", "ecommerce": "Snipcart", "cost": "$65/month"},
        {"name": "Portfolio + Shop", "cms": "Tina CMS", "ecommerce": "Stripe", "cost": "$85/month"},
        {"name": "Corporate Site", "cms": "Sanity", "ecommerce": "Shopify", "cost": "$150/month"},
    ]
    
    table = Table(title="Client Templates")
    table.add_column("Template", style="cyan")
    table.add_column("CMS", style="green")
    table.add_column("E-commerce", style="blue")
    table.add_column("Est. Cost", style="yellow")
    
    for template in templates_data:
        if category and category.lower() not in template["name"].lower():
            continue
        
        table.add_row(
            template["name"],
            template["cms"], 
            template["ecommerce"],
            template["cost"]
        )
    
    console.print(table)