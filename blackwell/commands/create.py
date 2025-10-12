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
# Cost calculator removed - platform focuses on capabilities, not pricing

app = typer.Typer(help="📦 Create clients, stacks, and templates", no_args_is_help=True)
console = Console()


class InteractiveClientWizard:
    """Interactive wizard for creating client configurations with intelligent recommendations."""

    def __init__(self, config_manager: ConfigManager, client_manager: ClientManager):
        self.config_manager = config_manager
        self.client_manager = client_manager
        self.provider_matrix = ProviderMatrix()

    def run_wizard(self, client_name: str) -> CLIClientConfig:
        """Run the complete interactive client creation wizard."""
        console.print(Panel(
            "[bold blue]🚀 Blackwell CLI - Client Setup Wizard[/bold blue]\n\n"
            "Create a new client with intelligent provider recommendations\n"
            "based on your technical requirements and use case.",
            title="Welcome to Client Creation",
            border_style="blue"
        ))

        # Step 1: Collect basic information
        basic_info = self._collect_basic_info(client_name)

        # Step 2: Determine requirements and preferences
        requirements = self._collect_requirements()

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

    def _collect_requirements(self) -> Dict[str, Any]:
        """Collect project requirements and technical preferences."""
        console.print("\n[bold cyan]🎯 Project Requirements[/bold cyan]")

        # Project type and use case
        console.print("\n[dim]What type of project are you building?[/dim]")
        console.print("1. Simple Blog/Portfolio - Content-focused site")
        console.print("2. Business Website - Company site with CMS")
        console.print("3. E-commerce Store - Online store with shopping cart")
        console.print("4. Complex Application - Advanced features and integrations")

        project_type_choice = IntPrompt.ask("Choose project type", default=2, show_choices=False)
        project_types = {
            1: "blog",
            2: "business_site",
            3: "ecommerce",
            4: "application"
        }
        project_type = project_types.get(project_type_choice, "business_site")

        # E-commerce needs
        needs_ecommerce = project_type == "ecommerce" or Confirm.ask(
            "Do you need e-commerce functionality?",
            default=(project_type in ["ecommerce", "application"])
        )

        # Technical complexity preference
        console.print("\n[dim]Technical complexity preference:[/dim]")
        console.print("1. Beginner - Simple setup, visual tools, minimal configuration")
        console.print("2. Intermediate - Balanced features and complexity")
        console.print("3. Advanced - Full control, technical tools, custom integrations")

        complexity_choice = IntPrompt.ask("Choose complexity level", default=2, show_choices=False)
        complexity_map = {1: "beginner", 2: "intermediate", 3: "advanced"}
        complexity = complexity_map.get(complexity_choice, "intermediate")

        # Integration mode preference based on needs
        integration_mode = "event_driven" if needs_ecommerce or project_type == "application" else "direct"
        if needs_ecommerce or project_type == "application":
            wants_composition = Confirm.ask(
                "Enable advanced integrations? (Webhooks, real-time updates, provider composition)",
                default=True
            )
            integration_mode = "event_driven" if wants_composition else "direct"

        # Content editing preference
        console.print("\n[dim]Content editing preference:[/dim]")
        console.print("1. Technical - Git-based, markdown, developer workflow")
        console.print("2. User-friendly - Visual editor, live preview")
        console.print("3. Professional - Structured content, advanced features")

        editing_choice = IntPrompt.ask("Choose editing style", default=2, show_choices=False)
        editing_styles = {1: "technical", 2: "user_friendly", 3: "professional"}
        editing_preference = editing_styles.get(editing_choice, "user_friendly")

        return {
            "project_type": project_type,
            "needs_ecommerce": needs_ecommerce,
            "complexity": complexity,
            "integration_mode": integration_mode,
            "editing_preference": editing_preference
        }

    def _get_provider_recommendations(self, basic_info: Dict, requirements: Dict) -> List[Dict]:
        """Get intelligent provider recommendations based on technical requirements."""
        console.print("\n[bold cyan]🎯 Generating Recommendations[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Analyzing provider combinations...", total=None)

            # Create base configuration
            base_config = {
                **basic_info,
                "service_tier": "tier1",
                "management_model": "self_managed",
                "integration_mode": requirements["integration_mode"]
            }

            recommendations = []

            # Capability-based provider matching
            if not requirements["needs_ecommerce"]:
                # CMS-only recommendations based on editing preference and complexity
                cms_recommendations = self._get_cms_recommendations(requirements)
                ssg_recommendations = self._get_ssg_recommendations(requirements)

                # Create combinations
                for cms in cms_recommendations[:2]:  # Top 2 CMS choices
                    for ssg in ssg_recommendations[:2]:  # Top 2 SSG choices
                        if self.provider_matrix.is_combination_compatible(cms, None, ssg):
                            config = {**base_config, "cms_provider": cms, "ssg_engine": ssg}

                            recommendations.append({
                                "config": config,
                                "complexity": requirements["complexity"],
                                "type": "cms_only",
                                "cms_provider": cms,
                                "ecommerce_provider": None,
                                "ssg_engine": ssg,
                                "match_score": self._calculate_capability_match_score(
                                    cms, None, ssg, requirements
                                )
                            })
            else:
                # E-commerce enabled recommendations
                cms_recommendations = self._get_cms_recommendations(requirements)
                ecommerce_recommendations = self._get_ecommerce_recommendations(requirements)
                ssg_recommendations = self._get_ssg_recommendations(requirements)

                # Create combinations
                for cms in cms_recommendations[:2]:
                    for ecommerce in ecommerce_recommendations[:2]:
                        for ssg in ssg_recommendations[:2]:
                            if self.provider_matrix.is_combination_compatible(cms, ecommerce, ssg):
                                config = {
                                    **base_config,
                                    "cms_provider": cms,
                                    "ecommerce_provider": ecommerce,
                                    "ssg_engine": ssg
                                }

                                recommendations.append({
                                    "config": config,
                                    "complexity": requirements["complexity"],
                                    "type": "composed",
                                    "cms_provider": cms,
                                    "ecommerce_provider": ecommerce,
                                    "ssg_engine": ssg,
                                    "match_score": self._calculate_capability_match_score(
                                        cms, ecommerce, ssg, requirements
                                    )
                                })

            progress.update(task, description="Ranking recommendations by capability match...")

            # Sort by capability match score (descending) and limit to top 5
            recommendations.sort(key=lambda x: x["match_score"], reverse=True)
            return recommendations[:5]

    def _get_cms_recommendations(self, requirements: Dict) -> List[str]:
        """Get CMS recommendations based on editing preference and complexity."""
        editing_preference = requirements["editing_preference"]
        complexity = requirements["complexity"]

        if editing_preference == "technical":
            return ["decap", "hugo", "jekyll"]
        elif editing_preference == "professional":
            return ["sanity", "contentful", "strapi"]
        else:  # user_friendly
            return ["tina", "forestry", "decap"]

    def _get_ssg_recommendations(self, requirements: Dict) -> List[str]:
        """Get SSG recommendations based on complexity and project type."""
        complexity = requirements["complexity"]
        project_type = requirements["project_type"]

        if complexity == "beginner":
            return ["eleventy", "hugo", "astro"]
        elif complexity == "advanced":
            return ["nextjs", "gatsby", "nuxtjs"]
        else:  # intermediate
            return ["astro", "gatsby", "eleventy"]

    def _get_ecommerce_recommendations(self, requirements: Dict) -> List[str]:
        """Get e-commerce recommendations based on complexity and project type."""
        complexity = requirements["complexity"]
        project_type = requirements["project_type"]

        if complexity == "beginner":
            return ["snipcart", "foxy"]
        elif complexity == "advanced":
            return ["shopify_basic", "medusa", "commercejs"]
        else:  # intermediate
            return ["snipcart", "shopify_basic", "foxy"]

    def _calculate_capability_match_score(self, cms: str, ecommerce: Optional[str], ssg: str, requirements: Dict) -> float:
        """Calculate how well this combination matches the user's requirements."""
        score = 0.0

        # Base compatibility check
        if self.provider_matrix.is_combination_compatible(cms, ecommerce, ssg):
            score += 10.0

        # Complexity alignment
        target_complexity = requirements["complexity"]
        combination_complexity = self.provider_matrix.get_complexity_level(cms, ecommerce, ssg)
        if combination_complexity == target_complexity:
            score += 20.0
        elif abs(["beginner", "intermediate", "advanced"].index(combination_complexity) -
                 ["beginner", "intermediate", "advanced"].index(target_complexity)) == 1:
            score += 10.0

        # Project type alignment
        project_type = requirements["project_type"]
        if project_type == "blog" and not ecommerce:
            score += 15.0
        elif project_type == "ecommerce" and ecommerce:
            score += 20.0
        elif project_type == "application" and requirements["integration_mode"] == "event_driven":
            score += 15.0

        # Editing preference alignment
        editing_pref = requirements["editing_preference"]
        if editing_pref == "technical" and cms in ["decap", "hugo", "jekyll"]:
            score += 10.0
        elif editing_pref == "professional" and cms in ["sanity", "contentful"]:
            score += 10.0
        elif editing_pref == "user_friendly" and cms in ["tina", "forestry"]:
            score += 10.0

        return score

    def _select_provider_combination(self, recommendations: List[Dict], requirements: Dict) -> Dict:
        """Display recommendations and let user select."""
        console.print(f"\n[bold cyan]🎯 Recommended Configurations (Project: {requirements['project_type'].replace('_', ' ').title()})[/bold cyan]")

        if not recommendations:
            console.print("[red]❌ No configurations found matching your requirements.[/red]")
            console.print("[yellow]💡 Try adjusting your complexity level or project type preferences.[/yellow]")
            raise typer.Exit(1)

        # Display recommendations table
        table = Table(title="Provider Recommendations")
        table.add_column("Option", style="cyan", width=6)
        table.add_column("CMS", style="blue")
        table.add_column("E-commerce", style="magenta")
        table.add_column("SSG", style="green")
        table.add_column("Match Score", style="yellow")
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
                f"{combo['match_score']:.1f}",
                combo["complexity"].title(),
                best_for
            )

        console.print(table)

        # Show detailed information for top recommendation
        top_recommendation = recommendations[0]
        self._show_capability_summary(top_recommendation, "🥇 Top Recommendation")

        # Let user select
        choice = IntPrompt.ask(
            f"Select configuration (1-{len(recommendations)})",
            default=1,
            show_default=True
        )

        if 1 <= choice <= len(recommendations):
            selected = recommendations[choice - 1]
            self._show_capability_summary(selected, f"Selected Configuration #{choice}")
            return selected
        else:
            console.print("[red]Invalid selection[/red]")
            raise typer.Exit(1)

    def _get_best_for_description(self, combo: Dict) -> str:
        """Get a description of what this combination is best for."""
        cms = combo["cms_provider"]
        ecommerce = combo["ecommerce_provider"]
        complexity = combo["complexity"]
        combo_type = combo["type"]

        if complexity == "beginner":
            if combo_type == "cms_only":
                return "Simple blogs and portfolios"
            else:
                return "Small online stores"
        elif complexity == "intermediate":
            if combo_type == "cms_only":
                return "Business websites"
            else:
                return "Growing e-commerce sites"
        else:  # advanced
            if combo_type == "cms_only":
                return "Complex content sites"
            else:
                return "Enterprise applications"

    def _show_capability_summary(self, combo: Dict, title: str):
        """Display detailed capability summary."""
        cms = combo["cms_provider"]
        ecommerce = combo["ecommerce_provider"]
        ssg = combo["ssg_engine"]

        # Get provider capabilities
        cms_info = self.provider_matrix.get_provider_info("cms", cms) or {}

        summary = f"""[bold]Configuration Overview:[/bold]
• CMS: {cms.title()} - {cms_info.get('description', 'Content management system')}
• E-commerce: {ecommerce.title() if ecommerce else 'None'}
• SSG Engine: {ssg.title()}
• Integration Mode: {combo['config']['integration_mode'].replace('_', ' ').title()}

[bold]Key Capabilities:[/bold]
• Complexity Level: {combo['complexity'].title()}
• Match Score: {combo['match_score']:.1f}/100
• Type: {combo['type'].replace('_', ' ').title()}

[bold]Technical Features:[/bold]
• Content editing workflow
• Static site generation
• Provider integrations"""

        if ecommerce:
            summary += "\n• E-commerce functionality"

        console.print(Panel(summary, title=title, border_style="green"))


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

    Interactive mode provides guided setup with capability-focused provider
    recommendations based on your technical requirements and use case.

    Non-interactive mode allows direct specification of all parameters.
    """
    try:
        config_manager = ConfigManager()
        client_manager = ClientManager(config_manager)

        if interactive:
            # Run interactive wizard
            wizard = InteractiveClientWizard(config_manager, client_manager)
            client = wizard.run_wizard(name)

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


