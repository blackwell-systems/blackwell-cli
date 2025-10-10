"""
Init Command - Initialize workspace and create new projects

Handles:
- Workspace initialization (~/.blackwell setup)
- New project creation with guided setup
- Platform-infrastructure integration
- Environment validation
"""

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
from typing import Optional

from blackwell.core.config_manager import ConfigManager
from blackwell.core.client_manager import ClientManager
from blackwell.core.cost_calculator import CostCalculator

app = typer.Typer(help="🔧 Initialize workspace and create new projects")
console = Console()


@app.command()
def workspace(
    force: bool = typer.Option(False, "--force", help="Force reinitialize workspace"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive setup"),
):
    """
    Initialize Blackwell CLI workspace.

    Sets up configuration directory, validates dependencies,
    and configures platform-infrastructure integration.
    """
    console.print("🚀 [bold blue]Initializing Blackwell CLI Workspace[/bold blue]")

    try:
        # Initialize configuration manager
        config_manager = ConfigManager()

        # Check if already initialized
        if config_manager.config_path.exists() and not force:
            if not Confirm.ask("Workspace already initialized. Reinitialize?"):
                console.print("[yellow]Workspace initialization cancelled.[/yellow]")
                return

        # Interactive setup
        if interactive:
            console.print("\n[dim]Let's set up your Blackwell CLI workspace...[/dim]")

            # AWS Configuration
            console.print("\n[bold]AWS Configuration[/bold]")
            current_profile = config_manager.config.aws.profile
            aws_profile = Prompt.ask(
                "AWS Profile",
                default=current_profile,
                show_default=True
            )

            current_region = config_manager.config.aws.region
            aws_region = Prompt.ask(
                "AWS Region",
                default=current_region,
                show_default=True
            )

            # Update AWS configuration
            config_manager.set("aws.profile", aws_profile)
            config_manager.set("aws.region", aws_region)

            # Platform-infrastructure setup
            console.print("\n[bold]Platform-Infrastructure Integration[/bold]")
            platform_path = _setup_platform_integration(config_manager, interactive=True)

            # Default preferences
            console.print("\n[bold]Default Preferences[/bold]")
            _setup_default_preferences(config_manager)

        # Validate configuration
        console.print("\n[bold]Validating Configuration[/bold]")
        issues = config_manager.validate_configuration()

        if issues:
            console.print("[yellow]⚠ Configuration Issues Found:[/yellow]")
            for issue in issues:
                console.print(f"  • [red]{issue}[/red]")

            if interactive and Confirm.ask("Would you like to see troubleshooting tips?"):
                _show_troubleshooting_tips(issues)
        else:
            console.print("[green]✓ Configuration valid[/green]")

        # Show summary
        _show_workspace_summary(config_manager)

        console.print("\n[green]🎉 Workspace initialized successfully![/green]")
        console.print("[dim]Next steps:[/dim]")
        console.print("  • blackwell create client --interactive")
        console.print("  • blackwell templates list")
        console.print("  • blackwell doctor (to run diagnostics)")

    except Exception as e:
        console.print(f"[red]Error initializing workspace: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def project(
    name: str = typer.Argument(..., help="Project name (kebab-case)"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive project setup"),
    template: Optional[str] = typer.Option(None, "--template", help="Template to use"),
    company: Optional[str] = typer.Option(None, "--company", help="Company name"),
    domain: Optional[str] = typer.Option(None, "--domain", help="Primary domain"),
    email: Optional[str] = typer.Option(None, "--email", help="Contact email"),
    budget: Optional[float] = typer.Option(None, "--budget", help="Monthly budget limit"),
):
    """
    Create a new client project with guided setup.

    Provides intelligent provider recommendations based on budget
    and requirements. Includes cost estimation and optimization.
    """
    console.print(f"📦 [bold blue]Creating new project: {name}[/bold blue]")

    try:
        # Initialize managers
        config_manager = ConfigManager()
        client_manager = ClientManager(config_manager)
        cost_calculator = CostCalculator()

        # Check if client already exists
        if client_manager.get_client(name):
            console.print(f"[red]Client '{name}' already exists[/red]")
            if not Confirm.ask("Would you like to update the existing client?"):
                raise typer.Exit(1)

        # Gather client information
        if interactive:
            client_info = _gather_client_info_interactive(
                name, company, domain, email, budget
            )
        else:
            if not all([company, domain, email]):
                console.print("[red]Non-interactive mode requires --company, --domain, and --email[/red]")
                raise typer.Exit(1)

            client_info = {
                "name": name,
                "company_name": company,
                "domain": domain,
                "contact_email": email,
                "budget": budget,
            }

        # Provider selection
        if template:
            # Use specified template
            provider_config = _apply_template(template, client_info)
        elif interactive:
            # Interactive provider selection
            provider_config = _select_providers_interactive(
                client_info, cost_calculator
            )
        else:
            # Use defaults
            defaults = config_manager.get_defaults()
            provider_config = {
                "cms_provider": defaults["cms_provider"],
                "ecommerce_provider": defaults["ecommerce_provider"],
                "ssg_engine": defaults["ssg_engine"],
                "integration_mode": defaults["integration_mode"],
            }

        # Create client configuration
        client_config = {**client_info, **provider_config}

        # Create client
        client = client_manager.create_client(**client_config)

        # Show cost estimation
        if interactive or budget:
            console.print("\n[bold]💰 Cost Estimation[/bold]")
            cost_breakdown = cost_calculator.calculate_client_cost(client)
            _show_cost_breakdown(cost_breakdown)

            if budget and cost_breakdown.total_estimated_cost > budget:
                console.print(f"[yellow]⚠ Estimated cost (${cost_breakdown.total_estimated_cost:.2f}) exceeds budget (${budget:.2f})[/yellow]")

                if Confirm.ask("Would you like to see optimization suggestions?"):
                    suggestions = cost_calculator.get_optimization_suggestions(client)
                    _show_optimization_suggestions(suggestions)

        # Show next steps
        console.print(f"\n[green]✅ Project '{name}' created successfully![/green]")
        console.print("\n[bold]Next Steps:[/bold]")
        console.print(f"  • blackwell deploy client {name} --preview")
        console.print(f"  • blackwell cost estimate {name}")
        console.print(f"  • blackwell list clients")

    except Exception as e:
        console.print(f"[red]Error creating project: {e}[/red]")
        raise typer.Exit(1)


def _setup_platform_integration(config_manager: ConfigManager, interactive: bool = True) -> Optional[Path]:
    """Set up platform-infrastructure integration."""
    current_path = config_manager.get_platform_path()

    if current_path and config_manager.is_platform_available():
        console.print(f"[green]✓ Platform-infrastructure found at: {current_path}[/green]")
        if not interactive or not Confirm.ask("Change platform-infrastructure path?"):
            return current_path

    if interactive:
        console.print("[yellow]Platform-infrastructure not found or invalid[/yellow]")
        console.print("Please provide the path to your platform-infrastructure project:")

        while True:
            path_input = Prompt.ask("Platform-infrastructure path", default="auto-discover")

            if path_input == "auto-discover":
                console.print("[dim]Auto-discovering platform-infrastructure...[/dim]")
                config_manager.load_config()  # Trigger auto-discovery
                if config_manager.is_platform_available():
                    return config_manager.get_platform_path()
                else:
                    console.print("[red]Auto-discovery failed[/red]")
                    continue

            platform_path = Path(path_input).expanduser().resolve()
            if config_manager._is_valid_platform_path(platform_path):
                config_manager.set("platform_infrastructure.path", str(platform_path))
                console.print(f"[green]✓ Platform-infrastructure configured: {platform_path}[/green]")
                return platform_path
            else:
                console.print(f"[red]Invalid platform-infrastructure path: {platform_path}[/red]")
                console.print("[dim]Path should contain: pyproject.toml, models/, stacks/, shared/[/dim]")

    return None


def _setup_default_preferences(config_manager: ConfigManager):
    """Set up default preferences."""
    console.print("[dim]Setting up default preferences for new clients...[/dim]")

    # CMS Provider
    cms_options = ["decap", "tina", "sanity", "contentful"]
    current_cms = config_manager.get("defaults.cms_provider")
    console.print(f"\nCMS Provider Options: {', '.join(cms_options)}")
    cms_provider = Prompt.ask(
        "Default CMS Provider",
        choices=cms_options,
        default=current_cms,
        show_choices=False
    )
    config_manager.set("defaults.cms_provider", cms_provider)

    # E-commerce Provider
    ecommerce_options = ["snipcart", "foxy", "shopify_basic"]
    current_ecommerce = config_manager.get("defaults.ecommerce_provider")
    console.print(f"\nE-commerce Provider Options: {', '.join(ecommerce_options)}")
    ecommerce_provider = Prompt.ask(
        "Default E-commerce Provider",
        choices=ecommerce_options,
        default=current_ecommerce,
        show_choices=False
    )
    config_manager.set("defaults.ecommerce_provider", ecommerce_provider)

    # SSG Engine
    ssg_options = ["hugo", "eleventy", "astro", "gatsby", "nextjs", "nuxtjs"]
    current_ssg = config_manager.get("defaults.ssg_engine")
    console.print(f"\nSSG Engine Options: {', '.join(ssg_options)}")
    ssg_engine = Prompt.ask(
        "Default SSG Engine",
        choices=ssg_options,
        default=current_ssg,
        show_choices=False
    )
    config_manager.set("defaults.ssg_engine", ssg_engine)

    # Integration Mode
    mode_options = ["direct", "event_driven"]
    current_mode = config_manager.get("defaults.integration_mode")
    console.print(f"\nIntegration Mode Options: {', '.join(mode_options)}")
    console.print("[dim]• direct: Simple, lower cost[/dim]")
    console.print("[dim]• event_driven: Composition-ready, more features[/dim]")
    integration_mode = Prompt.ask(
        "Default Integration Mode",
        choices=mode_options,
        default=current_mode,
        show_choices=False
    )
    config_manager.set("defaults.integration_mode", integration_mode)


def _gather_client_info_interactive(
    name: str, company: Optional[str], domain: Optional[str],
    email: Optional[str], budget: Optional[float]
) -> dict:
    """Gather client information interactively."""
    console.print("\n[bold]📋 Client Information[/bold]")

    # Company name
    company_name = company or Prompt.ask("Company Name")

    # Domain
    if not domain:
        suggested_domain = f"{name.replace('-', '')}.com"
        domain = Prompt.ask("Primary Domain", default=suggested_domain)

    # Email
    if not email:
        email = Prompt.ask("Contact Email")

    # Budget
    if budget is None:
        budget_input = Prompt.ask(
            "Monthly Budget (USD)",
            default="no-limit",
            show_default=True
        )
        budget = None if budget_input == "no-limit" else float(budget_input)

    return {
        "name": name,
        "company_name": company_name,
        "domain": domain,
        "contact_email": email,
        "budget": budget,
    }


def _select_providers_interactive(client_info: dict, cost_calculator: CostCalculator) -> dict:
    """Interactive provider selection with cost guidance."""
    console.print("\n[bold]🎯 Provider Selection[/bold]")

    # Budget analysis
    budget = client_info.get("budget")
    if budget:
        console.print(f"[dim]Analyzing options within ${budget:.2f}/month budget...[/dim]")

        # Show budget-appropriate combinations
        base_config = {
            "name": client_info["name"],
            "company_name": client_info["company_name"],
            "domain": client_info["domain"],
            "contact_email": client_info["contact_email"],
            "ssg_engine": "astro",  # Default for comparison
            "integration_mode": "event_driven",
        }

        combinations = cost_calculator.compare_providers(
            base_config, budget_limit=budget
        )

        if combinations:
            console.print(f"\n[green]Found {len(combinations)} options within budget:[/green]")

            table = Table(title="Budget-Friendly Options")
            table.add_column("Option", style="cyan")
            table.add_column("CMS", style="green")
            table.add_column("E-commerce", style="blue")
            table.add_column("Monthly Cost", style="yellow")
            table.add_column("Cost Tier", style="magenta")

            for i, combo in enumerate(combinations[:5], 1):  # Show top 5
                table.add_row(
                    str(i),
                    combo["cms_provider"],
                    combo["ecommerce_provider"] or "None",
                    f"${combo['cost'].total_estimated_cost:.2f}",
                    combo["cost"].cost_tier.value
                )

            console.print(table)

            # Let user choose from recommendations
            choice = Prompt.ask(
                "Select an option (1-5) or 'custom'",
                choices=[str(i) for i in range(1, min(6, len(combinations) + 1))] + ["custom"],
                default="1"
            )

            if choice != "custom":
                selected = combinations[int(choice) - 1]
                return {
                    "cms_provider": selected["cms_provider"],
                    "ecommerce_provider": selected["ecommerce_provider"],
                    "ssg_engine": "astro",
                    "integration_mode": "event_driven",
                }

    # Custom provider selection
    console.print("\n[bold]Custom Provider Selection[/bold]")

    # CMS Provider
    cms_options = ["decap", "tina", "sanity", "contentful"]
    console.print("\n[bold]CMS Providers:[/bold]")
    console.print("• [green]decap[/green]: FREE, git-based, technical")
    console.print("• [green]tina[/green]: $29/month, visual editing")
    console.print("• [green]sanity[/green]: $99/month, structured content")
    console.print("• [green]contentful[/green]: $300/month, enterprise features")

    cms_provider = Prompt.ask(
        "CMS Provider",
        choices=cms_options,
        default="decap"
    )

    # E-commerce Provider (optional)
    need_ecommerce = Confirm.ask("Do you need e-commerce functionality?")
    ecommerce_provider = None

    if need_ecommerce:
        ecommerce_options = ["snipcart", "foxy", "shopify_basic"]
        console.print("\n[bold]E-commerce Providers:[/bold]")
        console.print("• [blue]snipcart[/blue]: $29/month + 2% fees, simple")
        console.print("• [blue]foxy[/blue]: $75/month + 1.5% fees, advanced")
        console.print("• [blue]shopify_basic[/blue]: $29/month + 2.9% fees, full platform")

        ecommerce_provider = Prompt.ask(
            "E-commerce Provider",
            choices=ecommerce_options,
            default="snipcart"
        )

    # SSG Engine
    ssg_options = ["hugo", "eleventy", "astro", "gatsby", "nextjs", "nuxtjs"]
    console.print("\n[bold]SSG Engines:[/bold]")
    console.print("• [cyan]hugo[/cyan]: Fastest builds, technical")
    console.print("• [cyan]eleventy[/cyan]: Balanced, flexible")
    console.print("• [cyan]astro[/cyan]: Modern, component islands")
    console.print("• [cyan]gatsby[/cyan]: React ecosystem")
    console.print("• [cyan]nextjs[/cyan]: React apps, enterprise")
    console.print("• [cyan]nuxtjs[/cyan]: Vue ecosystem")

    ssg_engine = Prompt.ask(
        "SSG Engine",
        choices=ssg_options,
        default="astro"
    )

    # Integration Mode
    mode_options = ["direct", "event_driven"]
    console.print("\n[bold]Integration Mode:[/bold]")
    console.print("• [yellow]direct[/yellow]: Simple, lower cost")
    console.print("• [yellow]event_driven[/yellow]: Composition-ready, more features")

    # Auto-select based on composition needs
    default_mode = "event_driven" if ecommerce_provider else "direct"
    integration_mode = Prompt.ask(
        "Integration Mode",
        choices=mode_options,
        default=default_mode
    )

    return {
        "cms_provider": cms_provider,
        "ecommerce_provider": ecommerce_provider,
        "ssg_engine": ssg_engine,
        "integration_mode": integration_mode,
    }


def _apply_template(template: str, client_info: dict) -> dict:
    """Apply a template to get provider configuration."""
    # Built-in templates
    templates = {
        "budget-startup": {
            "cms_provider": "decap",
            "ecommerce_provider": "snipcart",
            "ssg_engine": "eleventy",
            "integration_mode": "event_driven",
        },
        "growing-business": {
            "cms_provider": "sanity",
            "ecommerce_provider": "snipcart",
            "ssg_engine": "astro",
            "integration_mode": "event_driven",
        },
        "enterprise": {
            "cms_provider": "contentful",
            "ecommerce_provider": "shopify_basic",
            "ssg_engine": "gatsby",
            "integration_mode": "event_driven",
        },
        "cms-only": {
            "cms_provider": "tina",
            "ecommerce_provider": None,
            "ssg_engine": "astro",
            "integration_mode": "direct",
        },
    }

    if template not in templates:
        console.print(f"[red]Unknown template: {template}[/red]")
        console.print(f"Available templates: {', '.join(templates.keys())}")
        raise typer.Exit(1)

    return templates[template]


def _show_cost_breakdown(cost_breakdown) -> None:
    """Show detailed cost breakdown."""
    table = Table(title="Cost Breakdown")
    table.add_column("Component", style="cyan")
    table.add_column("Monthly Cost", style="green")
    table.add_column("Notes", style="dim")

    table.add_row("CMS Provider", f"${cost_breakdown.cms_cost:.2f}", "Content management")
    table.add_row("E-commerce Provider", f"${cost_breakdown.ecommerce_cost:.2f}", "Online store platform")
    table.add_row("AWS Hosting", f"${cost_breakdown.hosting_cost:.2f}", "Infrastructure hosting")
    table.add_row("Event Infrastructure", f"${cost_breakdown.event_infrastructure_cost:.2f}", "Composition features")
    table.add_row("Data Transfer", f"${cost_breakdown.data_transfer_cost:.2f}", "CDN and bandwidth")
    table.add_row("Storage", f"${cost_breakdown.storage_cost:.2f}", "File and asset storage")
    table.add_row("", "", "")
    table.add_row("[bold]Total Fixed Cost[/bold]", f"[bold]${cost_breakdown.fixed_monthly_cost:.2f}[/bold]", "Monthly fixed costs")

    if cost_breakdown.transaction_fee_rate > 0:
        table.add_row("Transaction Fees", f"{cost_breakdown.transaction_fee_rate:.1%}", "Per-sale variable cost")

    console.print(table)

    # Cost tier indication
    tier_colors = {
        "budget": "green",
        "standard": "yellow",
        "professional": "blue",
        "enterprise": "red",
    }
    tier_color = tier_colors.get(cost_breakdown.cost_tier.value, "white")
    console.print(f"\n[{tier_color}]Cost Tier: {cost_breakdown.cost_tier.value.title()}[/{tier_color}]")


def _show_optimization_suggestions(suggestions: list) -> None:
    """Show cost optimization suggestions."""
    if not suggestions:
        console.print("[green]No optimization suggestions available[/green]")
        return

    console.print("\n[bold]💡 Cost Optimization Suggestions[/bold]")

    for i, suggestion in enumerate(suggestions, 1):
        panel_content = f"[bold]{suggestion['suggestion']}[/bold]\n"
        panel_content += f"Reason: {suggestion['reason']}\n"
        panel_content += f"Monthly Savings: [green]${suggestion['monthly_savings']:.2f}[/green]\n"

        if suggestion.get('trade_offs'):
            panel_content += f"Trade-offs: {', '.join(suggestion['trade_offs'])}"

        console.print(Panel(
            panel_content,
            title=f"Suggestion {i}",
            border_style="blue"
        ))


def _show_troubleshooting_tips(issues: list) -> None:
    """Show troubleshooting tips for configuration issues."""
    console.print("\n[bold]🛠 Troubleshooting Tips[/bold]")

    for issue in issues:
        if "Platform-infrastructure" in issue:
            console.print(Panel(
                "1. Clone the platform-infrastructure repository\n"
                "2. Set the path with: blackwell config set platform_infrastructure.path /path/to/repo\n"
                "3. Ensure the repository has: pyproject.toml, models/, stacks/, shared/",
                title="Platform-Infrastructure Setup",
                border_style="yellow"
            ))

        elif "AWS configuration" in issue:
            console.print(Panel(
                "1. Install AWS CLI: https://aws.amazon.com/cli/\n"
                "2. Configure credentials: aws configure\n"
                "3. Verify access: aws sts get-caller-identity",
                title="AWS Configuration",
                border_style="yellow"
            ))

        elif "CDK CLI not found" in issue:
            console.print(Panel(
                "1. Install Node.js: https://nodejs.org/\n"
                "2. Install CDK: npm install -g aws-cdk\n"
                "3. Verify installation: cdk --version",
                title="AWS CDK Setup",
                border_style="yellow"
            ))


def _show_workspace_summary(config_manager: ConfigManager) -> None:
    """Show workspace configuration summary."""
    console.print("\n[bold]📊 Workspace Summary[/bold]")

    table = Table()
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Config Directory", str(config_manager.config_dir))
    table.add_row("AWS Profile", config_manager.config.aws.profile)
    table.add_row("AWS Region", config_manager.config.aws.region)

    platform_path = config_manager.get_platform_path()
    table.add_row("Platform-Infrastructure", str(platform_path) if platform_path else "Not configured")

    table.add_row("Default CMS", config_manager.config.defaults.cms_provider)
    table.add_row("Default E-commerce", config_manager.config.defaults.ecommerce_provider)
    table.add_row("Default SSG", config_manager.config.defaults.ssg_engine)

    console.print(table)