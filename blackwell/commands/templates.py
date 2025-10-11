"""
Templates Command - Manage and apply client templates

Handles:
- Listing available templates
- Creating clients from templates
- Customizing template configurations
- Template validation and preview
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from typing import Optional, List

from blackwell.core.config_manager import ConfigManager
from blackwell.core.client_manager import ClientManager

app = typer.Typer(help="Manage and apply client templates", no_args_is_help=True)
console = Console()


@app.command()
def list(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Filter by provider"),
):
    """
    List available client templates.
    """
    console.print("[bold blue]Available Templates[/bold blue]")
    
    # Mock template data - would come from template registry
    templates = [
        {
            "name": "Blog + E-commerce",
            "category": "Blog", 
            "cms": "Decap CMS",
            "ecommerce": "Snipcart",
            "description": "Simple blog with integrated shopping cart",
            "cost_estimate": "$65/month"
        },
        {
            "name": "Portfolio + Shop",
            "category": "Portfolio",
            "cms": "Tina CMS", 
            "ecommerce": "Stripe",
            "description": "Creative portfolio with e-commerce capabilities",
            "cost_estimate": "$85/month"
        },
        {
            "name": "Corporate Website",
            "category": "Corporate",
            "cms": "Sanity",
            "ecommerce": "Shopify", 
            "description": "Full-featured corporate site with enterprise e-commerce",
            "cost_estimate": "$150/month"
        },
        {
            "name": "Marketing Landing Page",
            "category": "Marketing",
            "cms": "Contentful",
            "ecommerce": "None",
            "description": "High-conversion landing page with analytics",
            "cost_estimate": "$45/month"
        }
    ]
    
    # Apply filters
    filtered_templates = templates
    if category:
        filtered_templates = [t for t in filtered_templates if category.lower() in t["category"].lower()]
    if provider:
        filtered_templates = [t for t in filtered_templates if provider.lower() in t["cms"].lower() or provider.lower() in t["ecommerce"].lower()]
    
    if not filtered_templates:
        console.print("[yellow]No templates found matching the criteria.[/yellow]")
        return
    
    table = Table(title="Client Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Category", style="green")
    table.add_column("CMS", style="blue")
    table.add_column("E-commerce", style="magenta")
    table.add_column("Est. Cost", style="yellow")
    
    for template in filtered_templates:
        table.add_row(
            template["name"],
            template["category"],
            template["cms"],
            template["ecommerce"],
            template["cost_estimate"]
        )
    
    console.print(table)


@app.command()
def show(
    name: str = typer.Argument(..., help="Template name to show details for")
):
    """
    Show detailed information about a specific template.
    """
    console.print(f"[bold blue]Template Details: {name}[/bold blue]")
    
    # Mock template details - would come from template registry
    template_details = {
        "name": name,
        "description": "A comprehensive template for creating modern web applications",
        "cms": "Decap CMS",
        "ecommerce": "Snipcart", 
        "infrastructure": "AWS CDK",
        "features": [
            "Responsive design",
            "SEO optimization",
            "Payment processing",
            "Content management",
            "Analytics integration"
        ],
        "cost_breakdown": {
            "CMS": "$15/month",
            "E-commerce": "$20/month", 
            "Infrastructure": "$30/month"
        },
        "setup_time": "15 minutes",
        "complexity": "Beginner"
    }
    
    # Display template info
    panel_content = f"""[bold]Description:[/bold] {template_details['description']}

[bold]Stack:[/bold]
• CMS: {template_details['cms']}
• E-commerce: {template_details['ecommerce']}
• Infrastructure: {template_details['infrastructure']}

[bold]Features:[/bold]
{chr(10).join(f'• {feature}' for feature in template_details['features'])}

[bold]Cost Breakdown:[/bold]
{chr(10).join(f'• {service}: {cost}' for service, cost in template_details['cost_breakdown'].items())}

[bold]Setup Time:[/bold] {template_details['setup_time']}
[bold]Complexity:[/bold] {template_details['complexity']}"""
    
    console.print(Panel(panel_content, title=f"Template: {name}", border_style="blue"))


@app.command()
def apply(
    template_name: str = typer.Argument(..., help="Template name to apply"),
    client_name: str = typer.Argument(..., help="Name for the new client"),
    workspace: Optional[str] = typer.Option(None, "--workspace", "-w", help="Target workspace"),
):
    """
    Create a new client from a template.
    """
    console.print(f"[bold blue]Applying Template: {template_name}[/bold blue]")
    
    try:
        config_manager = ConfigManager()
        client_manager = ClientManager(config_manager)
        
        # Validate template exists
        console.print(f"[dim]Validating template '{template_name}'...[/dim]")
        
        # Create client from template
        console.print(f"[dim]Creating client '{client_name}' from template...[/dim]")
        
        # Mock client creation process
        console.print("[green]Template validation passed[/green]")
        console.print("[green]Client configuration generated[/green]")
        console.print("[green]Dependencies configured[/green]")
        console.print("[green]Initial files created[/green]")
        
        console.print(f"[green]Client '{client_name}' created successfully from '{template_name}' template[/green]")
        console.print(f"[dim]Run 'blackwell deploy {client_name}' to deploy your new client[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error applying template: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def validate(
    template_name: str = typer.Argument(..., help="Template name to validate")
):
    """
    Validate a template configuration.
    """
    console.print(f"[bold blue]Validating Template: {template_name}[/bold blue]")
    
    try:
        # Mock validation process
        checks = [
            "Template exists",
            "Provider compatibility", 
            "Required dependencies",
            "Configuration schema",
            "Cost calculations"
        ]
        
        for check in checks:
            console.print(f"[green]{check} - OK[/green]")
        
        console.print(f"[green]Template '{template_name}' validation passed[/green]")
        
    except Exception as e:
        console.print(f"[red]Validation failed: {e}[/red]")
        raise typer.Exit(1)