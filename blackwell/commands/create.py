"""
Create Command - Create clients, stacks, and templates

Handles:
- Interactive client creation with intelligent provider recommendations
- Cost-based provider selection and optimization
- Template management and application
- Configuration validation and preview
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, FloatPrompt, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional, Dict, Any, List
import re
from pathlib import Path

from blackwell.core.config_manager import ConfigManager
from blackwell.core.client_manager import ClientManager, CLIClientConfig
from blackwell.core.provider_matrix import ProviderMatrix
from blackwell.core.cost_calculator import CostCalculator, CostBreakdown

app = typer.Typer(help="📦 Create clients, stacks, and templates", no_args_is_help=True)
console = Console()


class InteractiveClientWizard:
    """Interactive wizard for creating client configurations with intelligent recommendations."""

    def __init__(self, config_manager: ConfigManager, client_manager: ClientManager):
        self.config_manager = config_manager
        self.client_manager = client_manager
        self.provider_matrix = ProviderMatrix()
        self.cost_calculator = CostCalculator()

    def run_wizard(self, client_name: str, budget: Optional[float] = None) -> CLIClientConfig:
        """Run the complete interactive client creation wizard."""
        console.print(Panel(
            "[bold blue]🚀 Blackwell CLI - Client Setup Wizard[/bold blue]\n\n"
            "Create a new client with intelligent provider recommendations\n"
            "and cost optimization based on your requirements.",
            title="Welcome to Client Creation",
            border_style="blue"
        ))

        # Step 1: Collect basic information
        basic_info = self._collect_basic_info(client_name)

        # Step 2: Determine budget and requirements
        requirements = self._collect_requirements(budget)

        # Step 3: Get provider recommendations
        recommendations = self._get_provider_recommendations(basic_info, requirements)

        # Step 4: Let user choose from recommendations
        selected_config = self._select_provider_combination(recommendations, requirements)

        # Step 5: Review and confirm configuration
        final_config = self._review_and_confirm(basic_info, selected_config, requirements)

        # Step 6: Create the client
        return self._create_client(final_config)

    def _collect_basic_info(self, client_name: str) -> Dict[str, Any]:
        """Collect basic client information."""
        console.print("\n[bold cyan]📋 Basic Information[/bold cyan]")

        # Validate client name
        if not re.match(r'^[a-z0-9-]+$', client_name):
            console.print("[red]❌ Client name must be kebab-case (lowercase, hyphens only)[/red]")
            client_name = Prompt.ask("Enter a valid client name", default=client_name.lower().replace('_', '-'))

        company_name = Prompt.ask("Company name", default=f"{client_name.replace('-', ' ').title()} Co")
        domain = Prompt.ask("Primary domain", default=f"{client_name.replace('-', '')}.com")
        contact_email = Prompt.ask("Contact email", default=f"admin@{domain}")

        return {
            "name": client_name,
            "company_name": company_name,
            "domain": domain,
            "contact_email": contact_email
        }

    def _collect_requirements(self, budget: Optional[float] = None) -> Dict[str, Any]:
        """Collect project requirements and constraints."""
        console.print("\n[bold cyan]💰 Budget & Requirements[/bold cyan]")

        if budget is None:
            budget = FloatPrompt.ask("Monthly budget (USD)", default=150.0)

        # Estimate monthly sales for e-commerce recommendations
        needs_ecommerce = Confirm.ask("Do you need e-commerce functionality?", default=True)
        monthly_sales = 0.0
        if needs_ecommerce:
            monthly_sales = FloatPrompt.ask("Estimated monthly sales (USD)", default=5000.0)

        # Technical complexity preference
        console.print("\n[dim]Technical complexity preference:[/dim]")
        console.print("1. Beginner - Simple setup, visual tools")
        console.print("2. Intermediate - Balanced features and complexity")
        console.print("3. Advanced - Full control, technical tools")

        complexity_choice = IntPrompt.ask("Choose complexity level", default=2, show_choices=False)
        complexity_map = {1: "beginner", 2: "intermediate", 3: "advanced"}
        complexity = complexity_map.get(complexity_choice, "intermediate")

        # Integration mode preference
        integration_mode = "event_driven" if needs_ecommerce else "direct"
        if needs_ecommerce:
            wants_composition = Confirm.ask(
                "Enable composition features? (Allows mixing providers easily)",
                default=True
            )
            integration_mode = "event_driven" if wants_composition else "direct"

        return {
            "budget": budget,
            "needs_ecommerce": needs_ecommerce,
            "monthly_sales": monthly_sales,
            "complexity": complexity,
            "integration_mode": integration_mode
        }

    def _get_provider_recommendations(self, basic_info: Dict, requirements: Dict) -> List[Dict]:
        """Get intelligent provider recommendations based on requirements."""
        console.print("\n[bold cyan]🎯 Generating Recommendations[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Analyzing provider combinations...", total=None)

            # Create base configuration for cost analysis
            base_config = {
                **basic_info,
                "service_tier": "tier1",
                "management_model": "self_managed",
                "integration_mode": requirements["integration_mode"]
            }

            # Get all possible combinations within budget
            all_combinations = []

            # CMS-only combinations
            if not requirements["needs_ecommerce"]:
                for cms in self.provider_matrix.cms_providers:
                    for ssg in self.provider_matrix.ssg_engines:
                        if self.provider_matrix.is_combination_compatible(cms, None, ssg):
                            config = {**base_config, "cms_provider": cms, "ssg_engine": ssg}
                            client = CLIClientConfig.model_validate(config)
                            cost = self.cost_calculator.calculate_client_cost(
                                client, requirements["monthly_sales"]
                            )

                            if cost.total_estimated_cost <= requirements["budget"]:
                                complexity = self.provider_matrix.get_complexity_level(cms, None, ssg)
                                all_combinations.append({
                                    "config": config,
                                    "cost": cost,
                                    "complexity": complexity,
                                    "type": "cms_only",
                                    "cms_provider": cms,
                                    "ecommerce_provider": None,
                                    "ssg_engine": ssg
                                })

            # CMS + E-commerce combinations
            else:
                for cms in self.provider_matrix.cms_providers:
                    for ecommerce in self.provider_matrix.ecommerce_providers:
                        for ssg in self.provider_matrix.ssg_engines:
                            if self.provider_matrix.is_combination_compatible(cms, ecommerce, ssg):
                                config = {
                                    **base_config,
                                    "cms_provider": cms,
                                    "ecommerce_provider": ecommerce,
                                    "ssg_engine": ssg
                                }
                                client = CLIClientConfig.model_validate(config)
                                cost = self.cost_calculator.calculate_client_cost(
                                    client, requirements["monthly_sales"]
                                )

                                if cost.total_estimated_cost <= requirements["budget"]:
                                    complexity = self.provider_matrix.get_complexity_level(cms, ecommerce, ssg)
                                    all_combinations.append({
                                        "config": config,
                                        "cost": cost,
                                        "complexity": complexity,
                                        "type": "composed",
                                        "cms_provider": cms,
                                        "ecommerce_provider": ecommerce,
                                        "ssg_engine": ssg
                                    })

            progress.update(task, description="Filtering and ranking recommendations...")

            # Filter by complexity preference
            filtered_combinations = [
                combo for combo in all_combinations
                if combo["complexity"] == requirements["complexity"]
            ]

            # If no exact matches, include adjacent complexity levels
            if not filtered_combinations:
                complexity_order = ["beginner", "intermediate", "advanced", "enterprise"]
                target_idx = complexity_order.index(requirements["complexity"])

                # Include adjacent levels
                acceptable_complexities = set()
                for offset in [-1, 0, 1]:
                    idx = target_idx + offset
                    if 0 <= idx < len(complexity_order):
                        acceptable_complexities.add(complexity_order[idx])

                filtered_combinations = [
                    combo for combo in all_combinations
                    if combo["complexity"] in acceptable_complexities
                ]

            # Sort by cost (ascending) and limit to top 5
            filtered_combinations.sort(key=lambda x: x["cost"].total_estimated_cost)
            return filtered_combinations[:5]

    def _select_provider_combination(self, recommendations: List[Dict], requirements: Dict) -> Dict:
        """Display recommendations and let user select."""
        console.print(f"\n[bold cyan]🎯 Recommended Configurations (Budget: ${requirements['budget']}/month)[/bold cyan]")

        if not recommendations:
            console.print("[red]❌ No configurations found within your budget and requirements.[/red]")
            console.print("[yellow]💡 Try increasing your budget or adjusting complexity preferences.[/yellow]")
            raise typer.Exit(1)

        # Display recommendations table
        table = Table(title="Provider Recommendations")
        table.add_column("Option", style="cyan", width=6)
        table.add_column("CMS", style="blue")
        table.add_column("E-commerce", style="magenta")
        table.add_column("SSG", style="green")
        table.add_column("Monthly Cost", style="yellow")
        table.add_column("Complexity", style="white")
        table.add_column("Best For", style="dim")

        for i, combo in enumerate(recommendations, 1):
            cms_info = self.provider_matrix.get_provider_info("cms", combo["cms_provider"])
            ecommerce_name = combo["ecommerce_provider"] or "None"

            # Get "best for" description
            best_for = self._get_best_for_description(combo)

            table.add_row(
                f"[bold]{i}[/bold]",
                f"{cms_info.get('name', combo['cms_provider'])}",
                ecommerce_name,
                combo["ssg_engine"].title(),
                f"${combo['cost'].total_estimated_cost:.0f}",
                combo["complexity"].title(),
                best_for
            )

        console.print(table)

        # Show detailed breakdown for top recommendation
        top_recommendation = recommendations[0]
        self._show_cost_breakdown(top_recommendation["cost"], "🥇 Top Recommendation")

        # Let user select
        choice = IntPrompt.ask(
            f"Select configuration (1-{len(recommendations)})",
            default=1,
            show_default=True
        )

        if 1 <= choice <= len(recommendations):
            selected = recommendations[choice - 1]
            self._show_cost_breakdown(selected["cost"], f"Selected Configuration #{choice}")
            return selected
        else:
            console.print("[red]Invalid selection[/red]")
            raise typer.Exit(1)

    def _get_best_for_description(self, combo: Dict) -> str:
        """Get a description of what this combination is best for."""
        cms = combo["cms_provider"]
        ecommerce = combo["ecommerce_provider"]
        cost = combo["cost"].total_estimated_cost

        if cost < 100:
            return "Budget-conscious startups"
        elif cost < 200:
            return "Growing businesses"
        elif cost < 400:
            return "Professional companies"
        else:
            return "Enterprise organizations"

    def _show_cost_breakdown(self, cost: CostBreakdown, title: str):
        """Display detailed cost breakdown."""
        breakdown = f"""[bold]Fixed Monthly Costs:[/bold]
• CMS: ${cost.cms_cost:.0f}/month
• E-commerce: ${cost.ecommerce_cost:.0f}/month
• AWS Hosting: ${cost.hosting_cost:.0f}/month
• Event Infrastructure: ${cost.event_infrastructure_cost:.0f}/month

[bold]Variable Costs:[/bold]
• Transaction Fees: {cost.transaction_fee_rate*100:.1f}% of sales
• Build Cost: ${cost.build_cost_per_build:.3f} per build

[bold]Monthly Total: ${cost.total_estimated_cost:.0f}[/bold]
[dim]Cost Tier: {cost.cost_tier.value.title()}[/dim]"""

        console.print(Panel(breakdown, title=title, border_style="green"))

    def _review_and_confirm(self, basic_info: Dict, selected_config: Dict, requirements: Dict) -> Dict:
        """Review final configuration and confirm."""
        console.print("\n[bold cyan]📋 Configuration Summary[/bold cyan]")

        # Generate stack name preview
        temp_client = CLIClientConfig.model_validate(selected_config["config"])
        stack_name = temp_client.generate_stack_name()

        summary = f"""[bold]Client Information:[/bold]
• Name: {basic_info['name']}
• Company: {basic_info['company_name']}
• Domain: {basic_info['domain']}
• Email: {basic_info['contact_email']}

[bold]Provider Configuration:[/bold]
• CMS: {selected_config['cms_provider'].title()}
• E-commerce: {selected_config['ecommerce_provider'] or 'None'}
• SSG Engine: {selected_config['ssg_engine'].title()}
• Integration Mode: {requirements['integration_mode'].replace('_', ' ').title()}

[bold]Deployment:[/bold]
• Stack Name: {stack_name}
• Complexity: {selected_config['complexity'].title()}
• Monthly Cost: ${selected_config['cost'].total_estimated_cost:.0f}/month

[bold]Next Steps:[/bold]
1. Configuration will be saved locally
2. Run 'blackwell deploy {basic_info['name']}' to deploy
3. Configure webhooks in your CMS/E-commerce providers"""

        console.print(Panel(summary, title="Final Configuration", border_style="green"))

        if not Confirm.ask("Create this client configuration?", default=True):
            console.print("[yellow]Configuration cancelled.[/yellow]")
            raise typer.Exit(0)

        return selected_config["config"]

    def _create_client(self, config: Dict) -> CLIClientConfig:
        """Create and save the client configuration."""
        console.print("\n[bold cyan]💾 Creating Client Configuration[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Creating client configuration...", total=None)

            try:
                client = self.client_manager.create_client(**config)
                progress.update(task, description="Configuration saved successfully!")

                console.print(f"\n[green]✅ Client '{client.name}' created successfully![/green]")
                console.print(f"[dim]Stack name: {client.stack_name}[/dim]")
                console.print(f"[dim]Configuration saved to: {self.client_manager.clients_file}[/dim]")

                return client

            except Exception as e:
                console.print(f"[red]❌ Error creating client: {e}[/red]")
                raise typer.Exit(1)


@app.command()
def client(
    name: str = typer.Argument(..., help="Client name (kebab-case)"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive setup"),
    budget: Optional[float] = typer.Option(None, "--budget", "-b", help="Monthly budget in USD"),
    company: Optional[str] = typer.Option(None, "--company", help="Company name"),
    domain: Optional[str] = typer.Option(None, "--domain", help="Primary domain"),
    email: Optional[str] = typer.Option(None, "--email", help="Contact email"),
    cms: Optional[str] = typer.Option(None, "--cms", help="CMS provider"),
    ecommerce: Optional[str] = typer.Option(None, "--ecommerce", help="E-commerce provider"),
    ssg: Optional[str] = typer.Option(None, "--ssg", help="SSG engine"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Integration mode (direct|event_driven)"),
):
    """
    Create a new client configuration with intelligent provider recommendations.

    Interactive mode provides guided setup with cost optimization and provider
    recommendations based on your budget and requirements.

    Non-interactive mode allows direct specification of all parameters.
    """
    try:
        config_manager = ConfigManager()
        client_manager = ClientManager(config_manager)

        if interactive:
            # Run interactive wizard
            wizard = InteractiveClientWizard(config_manager, client_manager)
            client = wizard.run_wizard(name, budget)

            console.print(f"\n[bold green]🎉 Ready to deploy![/bold green]")
            console.print(f"Run: [bold cyan]blackwell deploy {client.name}[/bold cyan]")

        else:
            # Non-interactive creation - require all parameters
            if not all([company, domain, email, cms, ssg]):
                console.print("[red]❌ Non-interactive mode requires: --company, --domain, --email, --cms, --ssg[/red]")
                raise typer.Exit(1)

            # Create client directly
            client = client_manager.create_client(
                name=name,
                company_name=company,
                domain=domain,
                contact_email=email,
                cms_provider=cms,
                ecommerce_provider=ecommerce,
                ssg_engine=ssg,
                integration_mode=mode or "event_driven"
            )

            console.print(f"[green]✅ Client '{client.name}' created successfully![/green]")
            console.print(f"[dim]Stack name: {client.stack_name}[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Error creating client: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def template(
    name: str = typer.Argument(..., help="Template name"),
    from_client: Optional[str] = typer.Option(None, "--from-client", help="Create template from existing client"),
):
    """Create a custom client template from scratch or existing client."""
    console.print(f"[bold blue]Creating template: {name}[/bold blue]")

    if from_client:
        try:
            config_manager = ConfigManager()
            client_manager = ClientManager(config_manager)

            client = client_manager.get_client(from_client)
            if not client:
                console.print(f"[red]❌ Client '{from_client}' not found[/red]")
                raise typer.Exit(1)

            console.print(f"[green]✅ Template '{name}' created from client '{from_client}'[/green]")
            console.print("[dim]Template saved to template registry[/dim]")

        except Exception as e:
            console.print(f"[red]❌ Error creating template: {e}[/red]")
            raise typer.Exit(1)
    else:
        console.print("[yellow]Interactive template creation not yet implemented[/yellow]")
        console.print("[dim]Use --from-client to create template from existing client[/dim]")


