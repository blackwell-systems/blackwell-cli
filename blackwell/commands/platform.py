"""
Platform Command - Manage platform-infrastructure integration

Handles:
- Platform integration status checking
- Metadata refresh and caching
- Dynamic provider matrix management
- Integration diagnostics and troubleshooting
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
from typing import Optional

from blackwell.core.config_manager import ConfigManager

app = typer.Typer(help="Manage platform-infrastructure integration", no_args_is_help=True)
console = Console()


@app.command()
def status(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information")
):
    """
    Show platform integration status and diagnostics.

    Displays comprehensive information about platform-infrastructure integration,
    including configuration, availability, and metadata status.
    """
    console.print("[bold blue]Platform Integration Status[/bold blue]\n")

    try:
        config_manager = ConfigManager(verbose=verbose)
        config_manager.show_platform_status()

    except Exception as e:
        console.print(f"[red]Error checking platform status: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def refresh(
    force: bool = typer.Option(False, "--force", "-f", help="Force refresh even if static mode is enabled")
):
    """
    Refresh platform metadata cache.

    Reloads provider data from platform-infrastructure, ensuring the CLI
    has the latest stack types and configurations.
    """
    console.print("[bold blue]Refreshing Platform Metadata[/bold blue]\n")

    try:
        config_manager = ConfigManager()

        if force and config_manager.config.platform_infrastructure.force_static_mode:
            console.print("[yellow]Force refresh requested - temporarily enabling platform integration[/yellow]")
            original_static_mode = True
            config_manager.set("platform_infrastructure.force_static_mode", False)
        else:
            original_static_mode = False

        success = config_manager.refresh_platform_metadata()

        # Restore original static mode if we temporarily disabled it
        if original_static_mode:
            config_manager.set("platform_infrastructure.force_static_mode", True)
            console.print("[dim]Restored static mode setting[/dim]")

        if success:
            console.print("\n[green]✓ Platform metadata refresh completed successfully[/green]")
        else:
            console.print("\n[red]✗ Platform metadata refresh failed[/red]")
            console.print("[dim]Use 'blackwell platform status' to diagnose issues[/dim]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error refreshing platform metadata: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def enable():
    """
    Enable platform integration.

    Enables dynamic provider matrix with live data from platform-infrastructure.
    This provides the latest stack types and enhanced features.
    """
    console.print("[bold blue]Enabling Platform Integration[/bold blue]\n")

    try:
        config_manager = ConfigManager()
        config_manager.enable_platform_integration()

        # Test the integration
        console.print("[dim]Testing platform integration...[/dim]")
        status = config_manager.get_platform_integration_status()

        if status.get("platform_available"):
            console.print("[green]✓ Platform integration is now active[/green]")
            console.print(f"[dim]Metadata entries available: {status.get('metadata_count', 0)}[/dim]")
        else:
            console.print("[yellow]⚠ Platform integration enabled but platform is not available[/yellow]")
            console.print("[dim]Check 'blackwell platform status' for diagnostics[/dim]")

    except Exception as e:
        console.print(f"[red]Error enabling platform integration: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def disable():
    """
    Disable platform integration (enable static mode).

    Forces the CLI to use static provider definitions instead of live data
    from platform-infrastructure. Useful for offline work or troubleshooting.
    """
    console.print("[bold blue]Disabling Platform Integration[/bold blue]\n")

    try:
        config_manager = ConfigManager()
        config_manager.disable_platform_integration()

        console.print("[green]✓ Platform integration disabled[/green]")
        console.print("[dim]CLI will now use static provider matrix[/dim]")
        console.print("[dim]Use 'blackwell platform enable' to re-enable[/dim]")

    except Exception as e:
        console.print(f"[red]Error disabling platform integration: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def path(
    set_path: Optional[Path] = typer.Option(None, "--set", help="Set platform-infrastructure path"),
    auto_discover: bool = typer.Option(False, "--auto-discover", help="Auto-discover platform path")
):
    """
    Show or set platform-infrastructure project path.

    Manages the path to the platform-infrastructure project used for
    dynamic provider matrix and enhanced features.
    """
    try:
        config_manager = ConfigManager()

        if set_path:
            # Validate the path
            if not set_path.exists():
                console.print(f"[red]Path does not exist: {set_path}[/red]")
                raise typer.Exit(1)

            if not config_manager._is_valid_platform_path(set_path):
                console.print(f"[red]Invalid platform-infrastructure project at: {set_path}[/red]")
                console.print("[dim]Check that the path contains a valid platform-infrastructure project[/dim]")
                raise typer.Exit(1)

            config_manager.set("platform_infrastructure.path", str(set_path))
            console.print(f"[green]✓ Platform path set to: {set_path}[/green]")

            # Test the integration
            console.print("[dim]Testing platform integration...[/dim]")
            status = config_manager.get_platform_integration_status()
            if status.get("platform_available"):
                console.print("[green]✓ Platform integration working[/green]")
            else:
                console.print("[yellow]⚠ Path set but platform not available[/yellow]")

        elif auto_discover:
            console.print("[blue]Auto-discovering platform-infrastructure...[/blue]")
            original_auto_discover = config_manager.config.platform_infrastructure.auto_discover

            # Temporarily enable auto-discover
            config_manager.set("platform_infrastructure.auto_discover", True)
            config_manager._auto_discover_platform()

            current_path = config_manager.get_platform_path()
            if current_path:
                console.print(f"[green]✓ Found platform-infrastructure at: {current_path}[/green]")
            else:
                console.print("[yellow]⚠ Could not auto-discover platform-infrastructure[/yellow]")
                console.print("[dim]Try setting the path manually with --set[/dim]")

            # Restore original auto-discover setting
            config_manager.set("platform_infrastructure.auto_discover", original_auto_discover)

        else:
            # Show current path
            current_path = config_manager.get_platform_path()
            if current_path:
                console.print(f"Platform path: {current_path}")

                # Show validation status
                if config_manager.is_platform_available():
                    console.print("[green]✓ Path is valid[/green]")
                else:
                    console.print("[red]✗ Path exists but is not a valid platform project[/red]")
            else:
                console.print("[yellow]No platform path configured[/yellow]")
                console.print("[dim]Use --set to configure or --auto-discover to find automatically[/dim]")

    except Exception as e:
        console.print(f"[red]Error managing platform path: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def providers(
    source: Optional[str] = typer.Option(None, "--source", help="Show providers from specific source (platform/static)")
):
    """
    Show available providers and their source.

    Displays CMS, e-commerce, and SSG providers available through either
    platform-infrastructure integration or static definitions.
    """
    console.print("[bold blue]Available Providers[/bold blue]\n")

    try:
        config_manager = ConfigManager()
        provider_matrix = config_manager.get_provider_matrix()

        # Get data source information
        if hasattr(provider_matrix, 'get_data_source'):
            data_source = provider_matrix.get_data_source()
            console.print(f"[dim]Data source: {data_source}[/dim]\n")
        else:
            data_source = "static"
            console.print("[dim]Data source: static[/dim]\n")

        # Filter by source if requested
        if source and source != data_source:
            console.print(f"[yellow]Requested source '{source}' not available (current: {data_source})[/yellow]")
            return

        # Get provider information
        if hasattr(provider_matrix, 'list_all_providers_with_source'):
            providers_info = provider_matrix.list_all_providers_with_source()
        else:
            providers_info = provider_matrix.list_all_providers()

        # Create tables for each provider type
        for provider_type in ["cms", "ecommerce", "ssg"]:
            if provider_type in providers_info:
                providers = providers_info[provider_type]

                if providers:
                    table = Table(title=f"{provider_type.upper()} Providers")
                    table.add_column("Provider", style="cyan")
                    table.add_column("Name", style="green")
                    table.add_column("Features", style="dim")

                    # Handle both list and dictionary formats
                    if isinstance(providers, dict):
                        # Dictionary format - iterate over items
                        for provider_key, provider_data in providers.items():
                            if isinstance(provider_data, dict):
                                name = provider_data.get("name", provider_key.title())
                                features = ", ".join(provider_data.get("features", [])[:3])  # Show first 3 features
                                if len(provider_data.get("features", [])) > 3:
                                    features += "..."
                            else:
                                name = str(provider_data)
                                features = ""

                            table.add_row(provider_key, name, features)
                    else:
                        # List format - get detailed info from provider matrix
                        for provider_key in providers:
                            provider_data = provider_matrix.get_provider_info(provider_type, provider_key)

                            if isinstance(provider_data, dict):
                                name = provider_data.get("name", provider_key.title())
                                features = ", ".join(provider_data.get("features", [])[:3])  # Show first 3 features
                                if len(provider_data.get("features", [])) > 3:
                                    features += "..."
                            else:
                                name = provider_key.title()
                                features = ""

                            table.add_row(provider_key, name, features)

                    console.print(table)
                    console.print()  # Add spacing

        # Show metadata if available
        if hasattr(provider_matrix, 'get_platform_status'):
            status = provider_matrix.get_platform_status()
            if "meta" in providers_info or status.get("platform_metadata_count", 0) > 0:
                meta_info = providers_info.get("meta", status)
                console.print("[bold]Integration Summary:[/bold]")
                console.print(f"Data source: {meta_info.get('data_source', 'unknown')}")
                console.print(f"Platform available: {meta_info.get('platform_available', False)}")
                if meta_info.get('total_combinations'):
                    console.print(f"Total combinations: {meta_info['total_combinations']}")

    except Exception as e:
        console.print(f"[red]Error retrieving provider information: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def doctor():
    """
    Run platform integration diagnostics.

    Comprehensive diagnostics for platform-infrastructure integration,
    including dependency checks, configuration validation, and connectivity tests.
    """
    console.print("[bold blue]Platform Integration Diagnostics[/bold blue]\n")

    try:
        config_manager = ConfigManager(verbose=True)

        # Run status check first
        console.print("[bold]1. Integration Status[/bold]")
        config_manager.show_platform_status()
        console.print()

        # Test provider matrix functionality
        console.print("[bold]2. Provider Matrix Test[/bold]")
        try:
            provider_matrix = config_manager.get_provider_matrix()
            providers = provider_matrix.list_all_providers()

            cms_count = len(providers.get("cms", {}))
            ecommerce_count = len(providers.get("ecommerce", {}))
            ssg_count = len(providers.get("ssg", {}))

            console.print(f"✓ Provider matrix functional: {cms_count} CMS, {ecommerce_count} E-commerce, {ssg_count} SSG")

            # Test enhanced features if available
            if hasattr(provider_matrix, 'get_data_source'):
                data_source = provider_matrix.get_data_source()
                console.print(f"✓ Data source: {data_source}")

                if data_source == "platform":
                    # Test platform-specific features
                    if hasattr(provider_matrix, 'get_platform_status'):
                        platform_status = provider_matrix.get_platform_status()
                        console.print(f"✓ Platform metadata: {platform_status.get('platform_metadata_count', 0)} entries")

                    if hasattr(provider_matrix, 'refresh_from_platform'):
                        console.print("✓ Refresh capability available")

        except Exception as e:
            console.print(f"✗ Provider matrix test failed: {e}")

        console.print()

        # Configuration validation
        console.print("[bold]3. Configuration Validation[/bold]")
        issues = config_manager.validate_configuration()
        if issues:
            for issue in issues:
                console.print(f"⚠ {issue}")
        else:
            console.print("✓ Configuration validation passed")

        console.print()

        # Recommendations
        console.print("[bold]4. Recommendations[/bold]")
        status = config_manager.get_platform_integration_status()

        recommendations = []
        if not status.get("config_path_available"):
            recommendations.append("Set platform path: blackwell platform path --set /path/to/platform-infrastructure")
        elif not status.get("platform_available"):
            recommendations.append("Check platform-infrastructure installation and Python path")
        elif status.get("force_static_mode"):
            recommendations.append("Enable platform integration: blackwell platform enable")
        else:
            recommendations.append("Platform integration is working well!")

        for rec in recommendations:
            console.print(f"• {rec}")

    except Exception as e:
        console.print(f"[red]Error running diagnostics: {e}[/red]")
        raise typer.Exit(1)