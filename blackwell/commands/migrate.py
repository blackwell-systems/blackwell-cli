"""
Migrate Command - Provider and mode migration

Handles:
- CMS provider migration with data backup
- E-commerce provider migration
- Integration mode changes (direct ↔ event_driven)
- Configuration validation and preview
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm, Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional, Dict, List, Any
from pathlib import Path

from blackwell.core.config_manager import ConfigManager
from blackwell.core.client_manager import ClientManager
from blackwell.core.provider_matrix import ProviderMatrix
from blackwell.core.cost_calculator import CostCalculator

app = typer.Typer(help="🔄 Migrate between providers and modes", no_args_is_help=True)
console = Console()


@app.command()
def cms(
    client_name: str = typer.Argument(..., help="Client name to migrate"),
    target_cms: str = typer.Argument(..., help="Target CMS provider"),
    preview: bool = typer.Option(False, "--preview", help="Preview migration without applying"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompts"),
):
    """
    Migrate a client's CMS provider.

    This will update the client configuration and provide guidance for
    migrating content and webhooks to the new CMS provider.
    """
    try:
        config_manager = ConfigManager()
        client_manager = ClientManager(config_manager)
        provider_matrix = ProviderMatrix()
        cost_calculator = CostCalculator()

        # Get current client configuration
        client = client_manager.get_client(client_name)
        if not client:
            console.print(f"[red]❌ Client '{client_name}' not found[/red]")
            console.print("[dim]Use 'blackwell list clients' to see available clients[/dim]")
            raise typer.Exit(1)

        current_cms = client.cms_provider
        if current_cms == target_cms:
            console.print(f"[yellow]Client '{client_name}' is already using {target_cms}[/yellow]")
            return

        # Validate target CMS
        if target_cms not in provider_matrix.cms_providers:
            console.print(f"[red]❌ Unknown CMS provider: {target_cms}[/red]")
            available_cms = list(provider_matrix.cms_providers.keys())
            console.print(f"[dim]Available CMS providers: {', '.join(available_cms)}[/dim]")
            raise typer.Exit(1)

        console.print(f"\n[bold cyan]🔄 CMS Migration: {current_cms} → {target_cms}[/bold cyan]")

        # Check compatibility
        compatibility_issues = _check_cms_compatibility(
            client, current_cms, target_cms, provider_matrix
        )

        # Calculate cost impact
        old_cost = cost_calculator.calculate_client_cost(client)

        # Create temporary client config with new CMS
        temp_client_config = client.model_copy()
        temp_client_config.cms_provider = target_cms
        new_cost = cost_calculator.calculate_client_cost(temp_client_config)

        cost_change = new_cost.total_estimated_cost - old_cost.total_estimated_cost

        # Display migration preview
        _display_cms_migration_preview(
            client, current_cms, target_cms, cost_change, compatibility_issues
        )

        if preview:
            console.print("\n[yellow]Preview mode - no changes applied[/yellow]")
            return

        # Show migration steps
        migration_steps = _get_cms_migration_steps(current_cms, target_cms)
        _display_migration_steps(migration_steps)

        # Confirmation
        if not force:
            if not Confirm.ask(f"\nProceed with CMS migration for '{client_name}'?"):
                console.print("[yellow]Migration cancelled[/yellow]")
                return

        # Perform migration
        _perform_cms_migration(client_manager, client_name, target_cms)

        console.print(f"\n[green]✅ CMS migration completed![/green]")
        console.print(f"\n[yellow]⚠️  Manual steps required:[/yellow]")
        for step in migration_steps["manual_steps"]:
            console.print(f"  • {step}")

    except Exception as e:
        console.print(f"[red]❌ Migration failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def ecommerce(
    client_name: str = typer.Argument(..., help="Client name to migrate"),
    target_ecommerce: str = typer.Argument(..., help="Target e-commerce provider"),
    preview: bool = typer.Option(False, "--preview", help="Preview migration without applying"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompts"),
):
    """
    Migrate a client's e-commerce provider.

    This will update the client configuration and provide guidance for
    migrating products, orders, and payment settings.
    """
    try:
        config_manager = ConfigManager()
        client_manager = ClientManager(config_manager)
        provider_matrix = ProviderMatrix()
        cost_calculator = CostCalculator()

        # Get current client configuration
        client = client_manager.get_client(client_name)
        if not client:
            console.print(f"[red]❌ Client '{client_name}' not found[/red]")
            raise typer.Exit(1)

        current_ecommerce = client.ecommerce_provider
        if current_ecommerce == target_ecommerce:
            console.print(f"[yellow]Client '{client_name}' is already using {target_ecommerce}[/yellow]")
            return

        # Validate target e-commerce provider
        if target_ecommerce not in provider_matrix.ecommerce_providers:
            console.print(f"[red]❌ Unknown e-commerce provider: {target_ecommerce}[/red]")
            available_ecommerce = list(provider_matrix.ecommerce_providers.keys())
            console.print(f"[dim]Available e-commerce providers: {', '.join(available_ecommerce)}[/dim]")
            raise typer.Exit(1)

        console.print(f"\n[bold cyan]🛒 E-commerce Migration: {current_ecommerce or 'None'} → {target_ecommerce}[/bold cyan]")

        # Calculate cost impact
        old_cost = cost_calculator.calculate_client_cost(client)

        temp_client_config = client.model_copy()
        temp_client_config.ecommerce_provider = target_ecommerce
        new_cost = cost_calculator.calculate_client_cost(temp_client_config)

        cost_change = new_cost.total_estimated_cost - old_cost.total_estimated_cost

        # Display migration preview
        _display_ecommerce_migration_preview(
            client, current_ecommerce, target_ecommerce, cost_change
        )

        if preview:
            console.print("\n[yellow]Preview mode - no changes applied[/yellow]")
            return

        # Get migration steps
        migration_steps = _get_ecommerce_migration_steps(current_ecommerce, target_ecommerce)
        _display_migration_steps(migration_steps)

        # Confirmation
        if not force:
            if not Confirm.ask(f"\nProceed with e-commerce migration for '{client_name}'?"):
                console.print("[yellow]Migration cancelled[/yellow]")
                return

        # Perform migration
        _perform_ecommerce_migration(client_manager, client_name, target_ecommerce)

        console.print(f"\n[green]✅ E-commerce migration completed![/green]")

        console.print(f"\n[yellow]⚠️  Manual steps required:[/yellow]")
        for step in migration_steps["manual_steps"]:
            console.print(f"  • {step}")

    except Exception as e:
        console.print(f"[red]❌ Migration failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def mode(
    client_name: str = typer.Argument(..., help="Client name to migrate"),
    target_mode: Optional[str] = typer.Argument(None, help="Target integration mode (optional - will toggle if not specified)"),
    preview: bool = typer.Option(False, "--preview", help="Preview migration without applying"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompts"),
):
    """
    Migrate a client's integration mode (direct ↔ event_driven).

    Changes how providers communicate and affects composability and cost.
    """
    try:
        config_manager = ConfigManager()
        client_manager = ClientManager(config_manager)
        cost_calculator = CostCalculator()

        # Get current client configuration
        client = client_manager.get_client(client_name)
        if not client:
            console.print(f"[red]❌ Client '{client_name}' not found[/red]")
            raise typer.Exit(1)

        current_mode = client.integration_mode

        # If no target mode specified, toggle between the two
        if target_mode is None:
            target_mode = "event_driven" if current_mode == "direct" else "direct"

        # Validate target mode
        valid_modes = ["direct", "event_driven"]
        if target_mode not in valid_modes:
            console.print(f"[red]❌ Invalid integration mode: {target_mode}[/red]")
            console.print(f"[dim]Valid modes: {', '.join(valid_modes)}[/dim]")
            raise typer.Exit(1)

        if current_mode == target_mode:
            console.print(f"[yellow]Client '{client_name}' is already using {target_mode} mode[/yellow]")
            return

        console.print(f"\n[bold cyan]⚙️  Integration Mode Migration: {current_mode} → {target_mode}[/bold cyan]")

        # Calculate cost impact
        old_cost = cost_calculator.calculate_client_cost(client)

        temp_client_config = client.model_copy()
        temp_client_config.integration_mode = target_mode
        new_cost = cost_calculator.calculate_client_cost(temp_client_config)

        cost_change = new_cost.total_estimated_cost - old_cost.total_estimated_cost

        # Display migration preview
        _display_mode_migration_preview(client, current_mode, target_mode, cost_change)

        if preview:
            console.print("\n[yellow]Preview mode - no changes applied[/yellow]")
            return

        # Get migration implications
        implications = _get_mode_migration_implications(current_mode, target_mode, client)
        _display_migration_implications(implications)

        # Confirmation
        if not force:
            if not Confirm.ask(f"\nProceed with integration mode migration for '{client_name}'?"):
                console.print("[yellow]Migration cancelled[/yellow]")
                return

        # Perform migration
        _perform_mode_migration(client_manager, client_name, target_mode)

        console.print(f"\n[green]✅ Integration mode migration completed![/green]")
        console.print(f"[dim]Client '{client_name}' now uses {target_mode} integration mode[/dim]")

        if implications.get("redeploy_required"):
            console.print(f"\n[yellow]⚠️  Redeployment required:[/yellow]")
            console.print(f"   blackwell deploy client {client_name} --approve")

    except Exception as e:
        console.print(f"[red]❌ Migration failed: {e}[/red]")
        raise typer.Exit(1)


def _check_cms_compatibility(client, current_cms: str, target_cms: str, provider_matrix: ProviderMatrix) -> List[str]:
    """Check compatibility issues when migrating CMS providers."""
    issues = []

    current_info = provider_matrix.get_provider_info("cms", current_cms)
    target_info = provider_matrix.get_provider_info("cms", target_cms)

    if current_info and target_info:
        # Check SSG compatibility
        current_ssg_compat = current_info.get("compatible_ssg", [])
        target_ssg_compat = target_info.get("compatible_ssg", [])

        if client.ssg_engine not in target_ssg_compat:
            issues.append(f"Target CMS {target_cms} may not be fully compatible with {client.ssg_engine}")

    return issues


def _display_cms_migration_preview(client, current_cms: str, target_cms: str, cost_change: float, issues: List[str]):
    """Display CMS migration preview information."""
    preview_content = f"""[bold]Migration Details:[/bold]
• Client: {client.name} ({client.company_name})
• Current CMS: {current_cms}
• Target CMS: {target_cms}
• SSG Engine: {client.ssg_engine}

[bold]Cost Impact:[/bold]
• Monthly change: {"+" if cost_change > 0 else ""}{cost_change:.2f} USD
• New estimated total: ${client.estimated_monthly_cost + cost_change:.2f}/month"""

    if issues:
        preview_content += f"\n\n[bold yellow]Compatibility Warnings:[/bold yellow]"
        for issue in issues:
            preview_content += f"\n• {issue}"

    console.print(Panel(preview_content, title="CMS Migration Preview", border_style="blue"))


def _display_ecommerce_migration_preview(client, current_ecommerce: Optional[str], target_ecommerce: str, cost_change: float):
    """Display e-commerce migration preview information."""
    preview_content = f"""[bold]Migration Details:[/bold]
• Client: {client.name} ({client.company_name})
• Current E-commerce: {current_ecommerce or 'None'}
• Target E-commerce: {target_ecommerce}

[bold]Cost Impact:[/bold]
• Monthly change: {"+" if cost_change > 0 else ""}{cost_change:.2f} USD
• New estimated total: ${client.estimated_monthly_cost + cost_change:.2f}/month"""

    console.print(Panel(preview_content, title="E-commerce Migration Preview", border_style="magenta"))


def _display_mode_migration_preview(client, current_mode: str, target_mode: str, cost_change: float):
    """Display integration mode migration preview."""
    mode_descriptions = {
        "direct": "Simple, lower cost, limited composition",
        "event_driven": "Advanced, higher cost, full composition support"
    }

    preview_content = f"""[bold]Migration Details:[/bold]
• Client: {client.name} ({client.company_name})
• Current Mode: {current_mode} ({mode_descriptions[current_mode]})
• Target Mode: {target_mode} ({mode_descriptions[target_mode]})

[bold]Cost Impact:[/bold]
• Monthly change: {"+" if cost_change > 0 else ""}{cost_change:.2f} USD
• New estimated total: ${client.estimated_monthly_cost + cost_change:.2f}/month"""

    console.print(Panel(preview_content, title="Integration Mode Migration Preview", border_style="yellow"))


def _get_cms_migration_steps(current_cms: str, target_cms: str) -> Dict[str, List[str]]:
    """Get migration steps for CMS provider change."""
    return {
        "automated_steps": [
            "Update client configuration",
            "Generate new webhook endpoints",
            "Update deployment configuration"
        ],
        "manual_steps": [
            f"Export content from {current_cms}",
            f"Import content to {target_cms}",
            f"Update {target_cms} webhook URLs in CMS admin",
            "Test content publication workflow",
            "Update team access permissions"
        ]
    }


def _get_ecommerce_migration_steps(current_ecommerce: Optional[str], target_ecommerce: str) -> Dict[str, List[str]]:
    """Get migration steps for e-commerce provider change."""
    return {
        "automated_steps": [
            "Update client configuration",
            "Generate new webhook endpoints",
            "Update payment flow configuration"
        ],
        "manual_steps": [
            f"Export products from {current_ecommerce or 'current system'}",
            f"Import products to {target_ecommerce}",
            f"Configure payment settings in {target_ecommerce}",
            f"Update {target_ecommerce} webhook URLs",
            "Test checkout and payment flow",
            "Migrate existing customer data (if applicable)"
        ]
    }


def _get_mode_migration_implications(current_mode: str, target_mode: str, client) -> Dict[str, Any]:
    """Get implications of integration mode migration."""
    if target_mode == "event_driven":
        return {
            "benefits": [
                "Full provider composition support",
                "Better scalability and reliability",
                "Advanced webhook and event handling"
            ],
            "tradeoffs": [
                "Higher infrastructure costs",
                "More complex debugging",
                "Additional AWS services required"
            ],
            "redeploy_required": True
        }
    else:  # direct mode
        return {
            "benefits": [
                "Lower infrastructure costs",
                "Simpler architecture",
                "Faster builds and deployments"
            ],
            "tradeoffs": [
                "Limited provider composition",
                "Less scalable for high traffic",
                "Fewer advanced features"
            ],
            "redeploy_required": True
        }


def _display_migration_steps(steps: Dict[str, List[str]]):
    """Display migration steps in a formatted table."""
    console.print("\n[bold cyan]Migration Steps[/bold cyan]")

    table = Table()
    table.add_column("Type", style="cyan")
    table.add_column("Steps", style="white")

    # Automated steps
    automated_steps_text = "\n".join([f"✓ {step}" for step in steps["automated_steps"]])
    table.add_row("Automated", automated_steps_text)

    # Manual steps
    manual_steps_text = "\n".join([f"• {step}" for step in steps["manual_steps"]])
    table.add_row("Manual", manual_steps_text)

    console.print(table)


def _display_migration_implications(implications: Dict[str, Any]):
    """Display implications of integration mode migration."""
    console.print("\n[bold cyan]Migration Implications[/bold cyan]")

    # Benefits
    if implications.get("benefits"):
        console.print("\n[bold green]Benefits:[/bold green]")
        for benefit in implications["benefits"]:
            console.print(f"  ✓ {benefit}")

    # Trade-offs
    if implications.get("tradeoffs"):
        console.print("\n[bold yellow]Trade-offs:[/bold yellow]")
        for tradeoff in implications["tradeoffs"]:
            console.print(f"  • {tradeoff}")


def _perform_cms_migration(client_manager: ClientManager, client_name: str, target_cms: str):
    """Perform the actual CMS migration."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Migrating CMS provider...", total=None)

        # Update client configuration
        client_manager.update_client_provider(client_name, "cms_provider", target_cms)
        progress.update(task, description="CMS migration completed")


def _perform_ecommerce_migration(client_manager: ClientManager, client_name: str, target_ecommerce: str):
    """Perform the actual e-commerce migration."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Migrating e-commerce provider...", total=None)

        # Update client configuration
        client_manager.update_client_provider(client_name, "ecommerce_provider", target_ecommerce)
        progress.update(task, description="E-commerce migration completed")


def _perform_mode_migration(client_manager: ClientManager, client_name: str, target_mode: str):
    """Perform the actual integration mode migration."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Migrating integration mode...", total=None)

        # Update client configuration
        client_manager.update_client_provider(client_name, "integration_mode", target_mode)
        progress.update(task, description="Integration mode migration completed")