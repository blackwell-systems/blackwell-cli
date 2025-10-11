"""
Cost Command - Cost estimation and optimization

Provides detailed cost analysis, optimization suggestions, and provider comparisons
based on the sophisticated cost calculation engine.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import FloatPrompt, Confirm
from typing import Optional, Dict, Any, List

from blackwell.core.config_manager import ConfigManager
from blackwell.core.client_manager import ClientManager
from blackwell.core.cost_calculator import CostCalculator, CostBreakdown
from blackwell.core.provider_matrix import ProviderMatrix

app = typer.Typer(help="💰 Estimate costs and optimize spending", no_args_is_help=True)
console = Console()


@app.command()
def estimate(
    name: str = typer.Argument(..., help="Client name"),
    monthly_sales: Optional[float] = typer.Option(None, "--sales", "-s", help="Estimated monthly sales (USD)"),
    monthly_builds: Optional[int] = typer.Option(None, "--builds", "-b", help="Estimated monthly builds"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed cost breakdown"),
):
    """
    Estimate monthly costs for a client configuration.

    Provides comprehensive cost analysis including provider costs, AWS infrastructure,
    and variable costs based on usage patterns.
    """
    try:
        config_manager = ConfigManager()
        client_manager = ClientManager(config_manager)
        cost_calculator = CostCalculator()

        # Get client configuration
        client = client_manager.get_client(name)
        if not client:
            console.print(f"[red]❌ Client '{name}' not found[/red]")
            console.print("[dim]Use 'blackwell list clients' to see available clients[/dim]")
            raise typer.Exit(1)

        # Prompt for missing parameters
        if monthly_sales is None and client.ecommerce_provider:
            monthly_sales = FloatPrompt.ask(
                "Estimated monthly sales (USD)",
                default=5000.0
            )
        elif monthly_sales is None:
            monthly_sales = 0.0

        if monthly_builds is None:
            monthly_builds = 30  # Default assumption

        console.print(f"\n[bold cyan]💰 Cost Estimation for '{name}'[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Calculating costs...", total=None)

            # Calculate cost breakdown
            cost_breakdown = cost_calculator.calculate_client_cost(
                client, monthly_sales, monthly_builds
            )

            progress.update(task, description="Cost analysis complete!")

        # Display cost summary
        _display_cost_summary(client, cost_breakdown, monthly_sales, monthly_builds)

        # Display detailed breakdown if requested
        if detailed:
            _display_detailed_breakdown(cost_breakdown)

        # Show cost tier information
        _display_cost_tier_info(cost_breakdown)

    except Exception as e:
        console.print(f"[red]❌ Error estimating costs: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def compare(
    budget: float = typer.Argument(..., help="Monthly budget limit (USD)"),
    monthly_sales: Optional[float] = typer.Option(0.0, "--sales", "-s", help="Estimated monthly sales (USD)"),
    complexity: Optional[str] = typer.Option(None, "--complexity", "-c", help="Preferred complexity (beginner|intermediate|advanced)"),
    needs_ecommerce: bool = typer.Option(True, "--ecommerce/--no-ecommerce", help="Include e-commerce providers"),
):
    """
    Compare provider combinations within a budget.

    Shows all possible provider combinations that fit within your budget,
    sorted by cost and complexity.
    """
    try:
        cost_calculator = CostCalculator()
        provider_matrix = ProviderMatrix()

        console.print(f"\n[bold cyan]🎯 Provider Comparison (Budget: ${budget}/month)[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Analyzing provider combinations...", total=None)

            # Get base configuration for comparison
            base_config = {
                "name": "comparison-temp",
                "company_name": "Comparison Company",
                "domain": "comparison.com",
                "contact_email": "admin@comparison.com",
                "service_tier": "tier1",
                "management_model": "self_managed",
                "integration_mode": "event_driven" if needs_ecommerce else "direct",
                "ssg_engine": "astro"  # Default SSG engine for comparison
            }

            # Get recommendations
            combinations = cost_calculator.compare_providers(
                base_config, budget, monthly_sales
            )

            # Filter by complexity if specified
            if complexity:
                filtered_combinations = []
                for combo in combinations:
                    combo_complexity = provider_matrix.get_complexity_level(
                        combo["cms_provider"],
                        combo["ecommerce_provider"],
                        combo["config"].get("ssg_engine", "astro")
                    )
                    if combo_complexity == complexity:
                        filtered_combinations.append(combo)
                combinations = filtered_combinations

            progress.update(task, description="Comparison complete!")

        if not combinations:
            console.print("[red]❌ No provider combinations found within your criteria[/red]")
            console.print("[yellow]💡 Try increasing your budget or adjusting complexity preferences[/yellow]")
            raise typer.Exit(1)

        # Display comparison table
        _display_provider_comparison_table(combinations, budget)

        # Show top 3 recommendations with details
        console.print(f"\n[bold cyan]🏆 Top Recommendations[/bold cyan]")
        for i, combo in enumerate(combinations[:3], 1):
            _display_combo_details(combo, f"#{i} Recommendation")

    except Exception as e:
        console.print(f"[red]❌ Error comparing providers: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def optimize(
    name: str = typer.Argument(..., help="Client name"),
    monthly_sales: Optional[float] = typer.Option(None, "--sales", "-s", help="Estimated monthly sales (USD)"),
):
    """
    Get cost optimization suggestions for a client.

    Analyzes the current configuration and provides specific recommendations
    for reducing costs while maintaining functionality.
    """
    try:
        config_manager = ConfigManager()
        client_manager = ClientManager(config_manager)
        cost_calculator = CostCalculator()

        # Get client configuration
        client = client_manager.get_client(name)
        if not client:
            console.print(f"[red]❌ Client '{name}' not found[/red]")
            raise typer.Exit(1)

        # Prompt for missing parameters
        if monthly_sales is None and client.ecommerce_provider:
            monthly_sales = FloatPrompt.ask(
                "Estimated monthly sales (USD)",
                default=5000.0
            )
        elif monthly_sales is None:
            monthly_sales = 0.0

        console.print(f"\n[bold cyan]🔧 Cost Optimization for '{name}'[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Analyzing optimization opportunities...", total=None)

            # Get current cost and optimization suggestions
            current_cost = cost_calculator.calculate_client_cost(client, monthly_sales)
            suggestions = cost_calculator.get_optimization_suggestions(client, monthly_sales)

            progress.update(task, description="Optimization analysis complete!")

        # Display current configuration
        _display_current_config_cost(client, current_cost, monthly_sales)

        # Display optimization suggestions
        if suggestions:
            _display_optimization_suggestions(suggestions)
        else:
            console.print(Panel(
                "[green]🎉 Your configuration is already well-optimized![/green]\n\n"
                "No significant cost savings opportunities found with your current requirements.",
                title="Optimization Analysis",
                border_style="green"
            ))

    except Exception as e:
        console.print(f"[red]❌ Error optimizing costs: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def roi(
    name: str = typer.Argument(..., help="Client name"),
    monthly_sales: Optional[float] = typer.Option(None, "--sales", "-s", help="Estimated monthly sales (USD)"),
    dev_hours_saved: Optional[int] = typer.Option(40, "--dev-hours", help="Development hours saved vs custom build"),
    hourly_rate: Optional[float] = typer.Option(100.0, "--hourly-rate", help="Developer hourly rate (USD)"),
):
    """
    Calculate ROI of using the platform vs custom development.

    Shows the financial benefit of using the Blackwell platform compared
    to building and maintaining a custom solution.
    """
    try:
        config_manager = ConfigManager()
        client_manager = ClientManager(config_manager)
        cost_calculator = CostCalculator()

        # Get client configuration
        client = client_manager.get_client(name)
        if not client:
            console.print(f"[red]❌ Client '{name}' not found[/red]")
            raise typer.Exit(1)

        # Prompt for missing parameters
        if monthly_sales is None and client.ecommerce_provider:
            monthly_sales = FloatPrompt.ask(
                "Estimated monthly sales (USD)",
                default=5000.0
            )
        elif monthly_sales is None:
            monthly_sales = 0.0

        console.print(f"\n[bold cyan]📊 ROI Analysis for '{name}'[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Calculating ROI...", total=None)

            # Calculate ROI
            roi_analysis = cost_calculator.estimate_roi(
                client, monthly_sales, dev_hours_saved, hourly_rate
            )

            progress.update(task, description="ROI analysis complete!")

        # Display ROI analysis
        _display_roi_analysis(roi_analysis, dev_hours_saved, hourly_rate)

    except Exception as e:
        console.print(f"[red]❌ Error calculating ROI: {e}[/red]")
        raise typer.Exit(1)


def _display_cost_summary(client, cost_breakdown: CostBreakdown, monthly_sales: float, monthly_builds: int):
    """Display cost summary for a client."""
    summary = f"""[bold]Configuration:[/bold]
• CMS: {client.cms_provider.title()}
• E-commerce: {client.ecommerce_provider.title() if client.ecommerce_provider else 'None'}
• SSG Engine: {client.ssg_engine.title()}
• Integration Mode: {client.integration_mode.replace('_', ' ').title()}

[bold]Monthly Cost Breakdown:[/bold]
• CMS: ${cost_breakdown.cms_cost:.0f}
• E-commerce: ${cost_breakdown.ecommerce_cost:.0f}
• AWS Infrastructure: ${cost_breakdown.hosting_cost + cost_breakdown.event_infrastructure_cost:.0f}
• Estimated Transaction Fees: {cost_breakdown.transaction_fee_rate*100:.1f}% of ${monthly_sales:,.0f} = ${monthly_sales * cost_breakdown.transaction_fee_rate:.0f}

[bold green]Total Monthly Cost: ${cost_breakdown.total_estimated_cost:.0f}[/bold green]
[dim]Cost Tier: {cost_breakdown.cost_tier.value.title()}[/dim]"""

    console.print(Panel(summary, title=f"Cost Estimation - {client.name}", border_style="green"))


def _display_detailed_breakdown(cost_breakdown: CostBreakdown):
    """Display detailed cost breakdown."""
    details = f"""[bold]Detailed AWS Infrastructure Costs:[/bold]
• Hosting (S3, CloudFront, Route53): ${cost_breakdown.hosting_cost:.2f}
• Event Infrastructure (SNS, DynamoDB, Lambda): ${cost_breakdown.event_infrastructure_cost:.2f}
• Data Transfer: ${cost_breakdown.data_transfer_cost:.2f}
• Storage: ${cost_breakdown.storage_cost:.2f}

[bold]Build Costs:[/bold]
• Cost per build: ${cost_breakdown.build_cost_per_build:.3f}
• Estimated builds/month: {cost_breakdown.estimated_builds_per_month}
• Monthly build cost: ${cost_breakdown.build_cost_per_build * cost_breakdown.estimated_builds_per_month:.2f}

[bold]Summary:[/bold]
• Fixed monthly cost: ${cost_breakdown.fixed_monthly_cost:.2f}
• Variable cost estimate: ${cost_breakdown.estimated_variable_cost:.2f}
• Total estimate: ${cost_breakdown.total_estimated_cost:.2f}"""

    console.print(Panel(details, title="Detailed Cost Breakdown", border_style="blue"))


def _display_cost_tier_info(cost_breakdown: CostBreakdown):
    """Display cost tier information and recommendations."""
    tier_info = {
        "budget": {
            "description": "Perfect for startups and small projects",
            "features": "Essential features, cost-effective providers",
            "color": "green"
        },
        "standard": {
            "description": "Great for growing businesses",
            "features": "Enhanced features, reliable providers",
            "color": "blue"
        },
        "professional": {
            "description": "Ideal for established companies",
            "features": "Advanced features, premium providers",
            "color": "yellow"
        },
        "enterprise": {
            "description": "Full-scale enterprise solutions",
            "features": "All features, enterprise-grade providers",
            "color": "red"
        }
    }

    tier = cost_breakdown.cost_tier.value
    info = tier_info.get(tier, tier_info["standard"])

    tier_details = f"""[bold]{tier.title()} Tier[/bold]
{info['description']}

[bold]Typical Features:[/bold]
{info['features']}

[bold]Monthly Range:[/bold]
• Budget: Under $100/month
• Standard: $100-250/month
• Professional: $250-500/month
• Enterprise: Over $500/month"""

    console.print(Panel(tier_details, title="Cost Tier Information", border_style=info["color"]))


def _display_provider_comparison_table(combinations: List[Dict], budget: float):
    """Display provider comparison table."""
    table = Table(title=f"Provider Combinations Within ${budget}/month Budget")
    table.add_column("Rank", style="cyan", width=6)
    table.add_column("CMS", style="blue")
    table.add_column("E-commerce", style="magenta")
    table.add_column("SSG", style="green")
    table.add_column("Monthly Cost", style="yellow")
    table.add_column("Type", style="white")

    for i, combo in enumerate(combinations[:10], 1):  # Limit to top 10
        table.add_row(
            str(i),
            combo["cms_provider"].title(),
            combo["ecommerce_provider"].title() if combo["ecommerce_provider"] else "None",
            combo["config"].get("ssg_engine", "astro").title(),
            f"${combo['cost'].total_estimated_cost:.0f}",
            combo["type"].replace("_", " ").title()
        )

    console.print(table)


def _display_combo_details(combo: Dict, title: str):
    """Display detailed information about a provider combination."""
    cost = combo["cost"]

    details = f"""[bold]Configuration:[/bold]
• CMS: {combo['cms_provider'].title()}
• E-commerce: {combo['ecommerce_provider'].title() if combo['ecommerce_provider'] else 'None'}
• SSG: {combo['config'].get('ssg_engine', 'astro').title()}

[bold]Monthly Costs:[/bold]
• CMS: ${cost.cms_cost:.0f}
• E-commerce: ${cost.ecommerce_cost:.0f}
• AWS: ${cost.hosting_cost + cost.event_infrastructure_cost:.0f}
• [bold]Total: ${cost.total_estimated_cost:.0f}[/bold]

[bold]Transaction Fees:[/bold] {cost.transaction_fee_rate*100:.1f}%"""

    console.print(Panel(details, title=title, border_style="blue"))


def _display_current_config_cost(client, cost: CostBreakdown, monthly_sales: float):
    """Display current configuration cost information."""
    config_info = f"""[bold]Current Configuration:[/bold]
• CMS: {client.cms_provider.title()}
• E-commerce: {client.ecommerce_provider.title() if client.ecommerce_provider else 'None'}
• SSG: {client.ssg_engine.title()}
• Integration: {client.integration_mode.replace('_', ' ').title()}

[bold]Current Monthly Cost: ${cost.total_estimated_cost:.0f}[/bold]
• Fixed costs: ${cost.fixed_monthly_cost:.0f}
• Transaction fees: {cost.transaction_fee_rate*100:.1f}% of ${monthly_sales:,.0f} = ${monthly_sales * cost.transaction_fee_rate:.0f}"""

    console.print(Panel(config_info, title="Current Configuration", border_style="blue"))


def _display_optimization_suggestions(suggestions: List[Dict]):
    """Display cost optimization suggestions."""
    console.print(f"\n[bold cyan]💡 Optimization Suggestions[/bold cyan]")

    for i, suggestion in enumerate(suggestions, 1):
        suggestion_text = f"""[bold]{suggestion['suggestion']}[/bold]
💰 Monthly Savings: ${suggestion['monthly_savings']:.0f}

[bold]Reason:[/bold] {suggestion['reason']}

[bold]Trade-offs:[/bold]
{chr(10).join(f'• {trade_off}' for trade_off in suggestion['trade_offs'])}"""

        color = "green" if suggestion['monthly_savings'] > 20 else "yellow"
        console.print(Panel(suggestion_text, title=f"Suggestion #{i}", border_style=color))


def _display_roi_analysis(roi_analysis: Dict, dev_hours_saved: int, hourly_rate: float):
    """Display ROI analysis."""
    analysis = f"""[bold]Cost Comparison:[/bold]
• Custom Development: ${roi_analysis['upfront_savings']:,.0f} upfront
• Custom Maintenance: ${roi_analysis['monthly_savings'] + roi_analysis['upfront_savings']/12:.0f}/month estimated
• Platform Cost: Included in monthly fee

[bold]ROI Analysis:[/bold]
• 6-month ROI: {roi_analysis['roi_6_months']*100:.1f}%
• 12-month ROI: {roi_analysis['roi_12_months']*100:.1f}%
• Break-even: {roi_analysis['break_even_months']:.1f} months

[bold]Assumptions:[/bold]
• Development hours saved: {dev_hours_saved} hours
• Developer hourly rate: ${hourly_rate:.0f}/hour
• Custom solution upfront cost: ${dev_hours_saved * hourly_rate:,.0f}"""

    roi_color = "green" if roi_analysis['roi_12_months'] > 0 else "yellow"
    console.print(Panel(analysis, title="ROI Analysis", border_style=roi_color))
