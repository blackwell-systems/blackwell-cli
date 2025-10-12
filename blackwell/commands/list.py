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

app = typer.Typer(help="List clients, providers, and deployments", no_args_is_help=True)
console = Console()


@app.command()
def clients(
    client_name: Optional[str] = typer.Argument(None, help="Show detailed config for specific client"),
    workspace: Optional[str] = typer.Option(None, "--workspace", "-w", help="Workspace path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
):
    """
    List all clients or show detailed configuration for a specific client.

    If no client name is provided, shows all clients in workspace.
    If client name is provided, shows detailed configuration for that client.
    """
    try:
        config_manager = ConfigManager()
        client_manager = ClientManager(config_manager)

        if client_name:
            # Show detailed configuration for specific client
            console.print(f"=� [bold blue]Client Configuration: {client_name}[/bold blue]")

            client = client_manager.get_client(client_name)
            if not client:
                console.print(f"[red]Client '{client_name}' not found.[/red]")
                console.print("\n[dim]Available clients:[/dim]")
                clients_list = client_manager.list_clients()
                for manifest, state in clients_list:
                    console.print(f"  • {manifest.client_id}")
                console.print(f"\n[dim]Create client with:[/dim] blackwell create client {client_name}")
                raise typer.Exit(1)

            # Display detailed client configuration
            _display_client_details(client)

        else:
            # Show all clients in table format (existing behavior)
            console.print("=� [bold blue]Listing Clients[/bold blue]")

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

            for manifest, state in clients_list:
                # Build providers list
                providers_list = [manifest.cms_provider]
                if manifest.ecommerce_provider:
                    providers_list.append(manifest.ecommerce_provider)

                # Format last deployment time
                last_deploy_str = "Never"
                if state.last_deployed_at:
                    last_deploy_str = state.last_deployed_at.strftime("%Y-%m-%d %H:%M")

                row = [manifest.client_id, manifest.get_service_type(), state.status]

                if verbose:
                    providers = ", ".join(providers_list)
                    row.extend([providers, last_deploy_str])

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

    Shows CMS and e-commerce providers with availability status.
    Infrastructure is handled by AWS.
    """
    console.print("=� [bold blue]Listing Providers[/bold blue]")
    
    # This would typically fetch from provider registry
    providers_data = {
        "CMS": ["Decap CMS", "Tina CMS", "Sanity", "Contentful"],
        "E-commerce": ["Snipcart", "Stripe", "Shopify", "WooCommerce"]
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


def _display_client_details(client) -> None:
    """Display detailed configuration for a specific client."""
    from rich.text import Text

    # Create client info panel
    info_text = Text()
    info_text.append(f"Company: ", style="bold")
    info_text.append(f"{client.company_name}\n", style="cyan")

    info_text.append(f"Contact: ", style="bold")
    info_text.append(f"{client.contact_email}\n", style="cyan")

    info_text.append(f"Domain: ", style="bold")
    info_text.append(f"{client.domain}\n", style="cyan")

    info_text.append(f"Service Type: ", style="bold")
    info_text.append(f"{client.get_service_type()}\n", style="green")

    # Status with color coding
    info_text.append(f"Status: ", style="bold")
    status_color = "green" if client.status == "deployed" else "yellow" if client.status in ["ready", "configured"] else "red"
    info_text.append(f"{client.status}\n", style=status_color)

    console.print(Panel(info_text, title="Client Information", border_style="blue"))

    # Configuration details
    config_table = Table(title="Configuration Details", show_header=True, header_style="bold magenta")
    config_table.add_column("Property", style="cyan", no_wrap=True, width=20)
    config_table.add_column("Value", style="green", width=30)

    config_table.add_row("Service Tier", client.service_tier)
    config_table.add_row("Management Model", client.management_model)
    config_table.add_row("SSG Engine", getattr(client, 'ssg_engine', 'N/A'))
    config_table.add_row("AWS Region", getattr(client, 'aws_region', 'us-east-1'))
    config_table.add_row("Stack Name", getattr(client, 'stack_name', 'N/A'))

    console.print(config_table)

    # Provider configuration
    providers_table = Table(title="Provider Configuration", show_header=True, header_style="bold magenta")
    providers_table.add_column("Type", style="cyan", no_wrap=True, width=15)
    providers_table.add_column("Provider", style="green", width=20)
    providers_table.add_column("Status", style="yellow", width=15)

    providers_table.add_row("CMS", client.cms_provider, "✓ Configured")
    if client.ecommerce_provider:
        providers_table.add_row("E-commerce", client.ecommerce_provider, "✓ Configured")
    else:
        providers_table.add_row("E-commerce", "None", "- Not configured")

    console.print(providers_table)

    # Deployment information
    deploy_table = Table(title="Deployment Information", show_header=True, header_style="bold magenta")
    deploy_table.add_column("Property", style="cyan", no_wrap=True, width=20)
    deploy_table.add_column("Value", style="green", width=30)

    if client.last_deployed_at:
        last_deploy_str = client.last_deployed_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        deploy_table.add_row("Last Deployed", last_deploy_str)
    else:
        deploy_table.add_row("Last Deployed", "Never")

    # Add any additional deployment details if available
    if hasattr(client, 'deployment_url') and client.deployment_url:
        deploy_table.add_row("Site URL", client.deployment_url)
    elif client.domain:
        deploy_table.add_row("Expected URL", f"https://{client.domain}")

    console.print(deploy_table)

    # Show next steps or commands
    if client.status == "configured":
        console.print(f"\n[yellow]💡 Next steps:[/yellow]")
        console.print(f"   blackwell deploy client {client.name} --approve")
    elif client.status == "deployed":
        console.print(f"\n[green]✅ Client is deployed and ready![/green]")
        console.print(f"   Visit: https://{client.domain}")
        console.print(f"   Monitor: blackwell cost analyze {client.name}")
    elif client.status == "error":
        console.print(f"\n[red]⚠ Client has deployment errors.[/red]")
        console.print(f"   Check logs: blackwell deploy status")
        console.print(f"   Retry: blackwell deploy client {client.name} --approve")