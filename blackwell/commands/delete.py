"""
Delete Command - Delete clients, templates, and configurations

Handles:
- Client configuration deletion with safety checks
- Template deletion and cleanup
- Configuration validation and confirmation prompts
- AWS deployment warning and guidance
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional

from blackwell.core.config_manager import ConfigManager
from blackwell.core.client_manager import ClientManager

app = typer.Typer(help="🗑️ Delete clients, templates, and configurations", no_args_is_help=True)
console = Console()


@app.command()
def client(
    name: str = typer.Argument(..., help="Client name to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    preserve_deployments: bool = typer.Option(False, "--preserve-deployments", help="Keep AWS deployments (only delete local config)"),
):
    """
    Delete a client configuration and optionally its AWS deployments.

    By default, this only deletes the local client configuration. Use caution
    when deleting clients with active AWS deployments - you may want to run
    'blackwell deploy destroy <client>' first.
    """
    try:
        config_manager = ConfigManager()
        client_manager = ClientManager(config_manager)

        # Check if client exists
        client = client_manager.get_client(name)
        if not client:
            console.print(f"[red]❌ Client '{name}' not found[/red]")
            raise typer.Exit(1)

        # Show client information
        console.print(f"\n[bold red]⚠️  Delete Client: {name}[/bold red]")

        client_info = f"""[bold]Client Information:[/bold]
• Name: {client.name}
• Company: {client.company_name}
• Domain: {client.domain}
• Stack Name: {client.stack_name or 'Not generated'}
• Status: {client.status}
• Created: {client.created_at.strftime('%Y-%m-%d %H:%M')}

[bold]⚠️  What will be deleted:[/bold]
• Local client configuration
• Client history and metadata"""

        if not preserve_deployments and client.status in ["deployed", "deploying"]:
            client_info += f"""

[bold red]🚨 WARNING:[/bold red]
This client appears to have active AWS deployments (status: {client.status}).
Deleting the client configuration will NOT automatically destroy AWS resources.

[bold]Recommended steps:[/bold]
1. Run: [cyan]blackwell deploy destroy {name}[/cyan] (to remove AWS resources)
2. Then run: [cyan]blackwell delete client {name}[/cyan] (to remove config)

Or use [cyan]--preserve-deployments[/cyan] to keep AWS resources and only delete local config."""

        console.print(Panel(client_info, title="Deletion Preview", border_style="red"))

        # Confirmation prompt
        if not force:
            if client.status in ["deployed", "deploying"] and not preserve_deployments:
                console.print("[bold red]⚠️  Client has active deployments![/bold red]")
                proceed = Confirm.ask(
                    f"Are you sure you want to delete client '{name}'? This will NOT destroy AWS resources",
                    default=False
                )
            else:
                proceed = Confirm.ask(f"Delete client '{name}'?", default=False)

            if not proceed:
                console.print("[yellow]Deletion cancelled[/yellow]")
                raise typer.Exit(0)

        # Perform deletion
        console.print(f"\n[bold cyan]🗑️  Deleting Client Configuration[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Deleting client configuration...", total=None)

            success = client_manager.delete_client(name)

            if success:
                progress.update(task, description="Client configuration deleted successfully!")
                console.print(f"\n[green]✅ Client '{name}' deleted successfully![/green]")

                if client.status in ["deployed", "deploying"] and not preserve_deployments:
                    console.print(f"[yellow]⚠️  AWS resources may still exist. Run 'blackwell deploy destroy {client.stack_name}' to clean up.[/yellow]")

                console.print(f"[dim]Configuration removed from: {client_manager.clients_file}[/dim]")
            else:
                console.print(f"[red]❌ Failed to delete client '{name}'[/red]")
                raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]❌ Error deleting client: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def template(
    name: str = typer.Argument(..., help="Template name to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """
    Delete a client template.

    Removes the template from the template registry. This does not affect
    any clients created from this template.
    """
    console.print(f"[bold red]🗑️  Delete Template: {name}[/bold red]")

    if not force:
        proceed = Confirm.ask(f"Delete template '{name}'?", default=False)
        if not proceed:
            console.print("[yellow]Deletion cancelled[/yellow]")
            raise typer.Exit(0)

    # Template deletion logic would go here
    console.print("[yellow]Template deletion not yet implemented[/yellow]")
    console.print("[dim]Templates are managed in the template registry[/dim]")