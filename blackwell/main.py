"""
Blackwell CLI - Main Entry Point

This is the main entry point for the Blackwell CLI application.
It sets up the command structure and handles global configuration.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from pathlib import Path
import sys
from typing import Optional

# Import command modules
from blackwell.commands import (
    init,
    create,
    delete,
    deploy,
    migrate,
    list as list_cmd,
    config,
    templates,
    platform,
    bootstrap,
)

# Import core components
from blackwell.core.config_manager import ConfigManager
from blackwell import __version__, CLI_NAME

# Initialize Rich console for beautiful output
console = Console()

# Create the main Typer app
app = typer.Typer(
    name=CLI_NAME,
    help=f"""
    {CLI_NAME.title()} CLI - Simplify composable web stack deployment

    Create, deploy, and manage sophisticated multi-client web infrastructure
    with intelligent provider selection and capability-focused recommendations.

    Features:
    • Mix any CMS (Decap, Tina, Sanity, Contentful) with any E-commerce provider
    • Dual-mode architecture: Direct (simple) or Event-Driven (composition-ready)
    • Intelligent provider recommendations based on technical capabilities
    • Automated deployment with AWS CDK integration
    • Provider migration and upgrade assistance

    Get started: {CLI_NAME} init workspace
    """,
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)

# Global state
config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get or create the global configuration manager."""
    global config_manager
    if config_manager is None:
        config_manager = ConfigManager()
    return config_manager


def version_callback(value: bool):
    """Display version information and exit."""
    if value:
        version_panel = Panel(
            Text(f"{CLI_NAME.title()} CLI v{__version__}", style="bold blue"),
            title="Version Information",
            subtitle=f"Simplify composable web stack deployment",
            border_style="blue",
        )
        console.print(version_panel)
        raise typer.Exit()


def check_dependencies_callback(value: bool):
    """Check system dependencies and exit."""
    if value:
        from blackwell.core.dependency_checker import DependencyChecker

        checker = DependencyChecker()
        checker.check_all_dependencies()
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version information",
        callback=version_callback,
        is_eager=True,
    ),
    check_deps: bool = typer.Option(
        None,
        "--check-deps",
        help="Check system dependencies",
        callback=check_dependencies_callback,
        is_eager=True,
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
    config_path: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
):
    """
    Blackwell CLI - Simplify composable web stack deployment.

    Create and manage sophisticated multi-client web infrastructure with
    intelligent provider selection and capability-focused recommendations.
    """
    # Set up global configuration
    global config_manager
    try:
        config_manager = ConfigManager(config_path=config_path, verbose=verbose)
    except Exception as e:
        console.print(f"[red]Error initializing configuration: {e}[/red]")
        raise typer.Exit(1)

    # Set verbosity level
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")


# Register all command groups
app.add_typer(
    init.app,
    name="init",
    help="Initialize workspace and create new projects",
    rich_help_panel="Setup Commands",
)

app.add_typer(
    create.app,
    name="create",
    help="Create clients, stacks, and templates",
    rich_help_panel="Creation Commands",
)

app.add_typer(
    delete.app,
    name="delete",
    help="Delete clients, templates, and configurations",
    rich_help_panel="Deletion Commands",
)

app.add_typer(
    deploy.app,
    name="deploy",
    help="Deploy, update, and destroy infrastructure",
    rich_help_panel="Deployment Commands",
)

# Add bootstrap commands as subcommands under deploy
deploy.app.add_typer(
    bootstrap.app,
    name="bootstrap",
    help="Manage CDK bootstrap operations",
    rich_help_panel="Bootstrap Management",
)

# Cost command removed - platform focuses on capabilities, not pricing

app.add_typer(
    migrate.app,
    name="migrate",
    help="Migrate between providers and modes",
    rich_help_panel="Migration Commands",
)

app.add_typer(
    list_cmd.app,
    name="list",
    help="List clients, providers, and deployments",
    rich_help_panel="Information Commands",
)

app.add_typer(
    config.app,
    name="config",
    help="Manage CLI configuration and settings",
    rich_help_panel="Configuration",
)

app.add_typer(
    templates.app,
    name="templates",
    help="Manage and apply client templates",
    rich_help_panel="Template Management",
)

app.add_typer(
    platform.app,
    name="platform",
    help="Manage platform-infrastructure integration",
    rich_help_panel="Platform Integration",
)


@app.command(name="doctor", rich_help_panel="Utilities")
def doctor(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed diagnostic information"),
    deployment_check: bool = typer.Option(False, "--deployment-check", help="Check deployment readiness instead of full diagnosis"),
    account: Optional[str] = typer.Option(None, "--account", help="AWS account ID for deployment check"),
    region: Optional[str] = typer.Option(None, "--region", help="AWS region for deployment check"),
    profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile for deployment check"),
):
    """
    Run comprehensive system diagnostics.

    Checks system dependencies, AWS configuration, CDK bootstrap status,
    and platform-infrastructure integration to diagnose potential issues.
    """
    from blackwell.core.system_doctor import SystemDoctor

    doctor = SystemDoctor(config_manager=get_config_manager())

    if deployment_check:
        # Run deployment readiness check
        success = doctor.check_deployment_readiness(
            account_id=account,
            region=region,
            profile=profile
        )
        raise typer.Exit(0 if success else 1)
    else:
        # Run full system diagnosis
        success = doctor.run_full_diagnosis(verbose=verbose)
        raise typer.Exit(0 if success else 1)


@app.command(name="quickstart", rich_help_panel="Setup Commands")
def quickstart():
    """
    Interactive quickstart guide.

    Step-by-step guide to set up your first client with intelligent
    provider recommendations and cost optimization.
    """
    from blackwell.core.quickstart import QuickstartGuide

    guide = QuickstartGuide(config_manager=get_config_manager())
    guide.run_interactive_setup()


# Error handling
@app.command(hidden=True)
def _handle_error(error_code: int = 1):
    """Handle CLI errors gracefully."""
    console.print(
        f"[red]An error occurred. Use '{CLI_NAME} doctor' to diagnose issues.[/red]"
    )
    raise typer.Exit(error_code)


def cli_exception_handler(exc_type, exc_value, exc_traceback):
    """Custom exception handler for the CLI."""
    if exc_type == KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(130)  # Standard exit code for Ctrl+C

    # For development, show full traceback
    if get_config_manager().is_debug_mode():
        import traceback

        console.print("[red]Debug mode - Full traceback:[/red]")
        traceback.print_exception(exc_type, exc_value, exc_traceback)
    else:
        console.print(f"[red]Unexpected error: {exc_value}[/red]")
        console.print(f"[dim]Use --verbose or '{CLI_NAME} doctor' for more details[/dim]")

    sys.exit(1)


def main_entry_point():
    """
    Main entry point for the CLI when called from command line.
    This is what gets called when user runs 'blackwell' command.
    """
    # Set up custom exception handling
    sys.excepthook = cli_exception_handler

    try:
        app()
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        console.print(f"[dim]Run '{CLI_NAME} doctor' to diagnose the issue[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main_entry_point()