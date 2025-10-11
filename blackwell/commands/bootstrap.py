"""
Bootstrap Command - Manage CDK bootstrap operations

Provides commands for managing CDK bootstrap across AWS accounts and regions,
including status checking, bootstrapping, and validation.
"""

from typing import List, Optional
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from blackwell.core.config_manager import ConfigManager
from blackwell.core.cdk_bootstrap_checker import CDKBootstrapChecker


app = typer.Typer(
    help="Manage CDK bootstrap operations",
    no_args_is_help=True,
    rich_help_panel="Bootstrap Management"
)
console = Console()


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager."""
    from blackwell.main import get_config_manager
    return get_config_manager()


@app.command()
def status(
    account: Optional[str] = typer.Option(None, "--account", help="AWS account ID"),
    region: Optional[str] = typer.Option(None, "--region", help="AWS region"),
    profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile to use"),
    regions: Optional[str] = typer.Option(None, "--regions", help="Comma-separated list of regions to check"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed resource information"),
):
    """
    Check CDK bootstrap status for current or specified account/region.

    Shows comprehensive bootstrap status including CDKToolkit stack existence,
    resource validation, and recommendations for missing bootstrap.
    """
    console.print(Panel.fit(
        "[bold blue]CDK Bootstrap Status Check[/bold blue]\n\n"
        "Checking CDK bootstrap status and validating required resources\n"
        "for AWS CDK deployments.",
        border_style="blue"
    ))

    try:
        config = get_config_manager()
        bootstrap_checker = CDKBootstrapChecker(console=console)

        # Use config defaults if not provided
        account = account or config.config.aws.account_id
        region = region or config.config.aws.region
        profile = profile or config.config.aws.profile

        if regions:
            # Multi-region check
            region_list = [r.strip() for r in regions.split(",")]
            console.print(f"[dim]Checking bootstrap status across {len(region_list)} regions...[/dim]\n")

            statuses = bootstrap_checker.check_multiple_regions(
                regions=region_list,
                account_id=account,
                profile=profile
            )

            bootstrap_checker.display_multi_region_status(statuses)

            # Show detailed status for each region if verbose
            if verbose:
                for region_name, status in statuses.items():
                    console.print(f"\n[bold]Detailed status for {region_name}:[/bold]")
                    bootstrap_checker.display_bootstrap_status(status, verbose=True)

        else:
            # Single region check
            console.print(f"[dim]Checking bootstrap status for account/region...[/dim]\n")

            status = bootstrap_checker.check_bootstrap_status(
                account_id=account,
                region=region,
                profile=profile
            )

            bootstrap_checker.display_bootstrap_status(status, verbose=verbose)

    except KeyboardInterrupt:
        console.print("\n[yellow]Bootstrap status check cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Bootstrap status check failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def run(
    account: Optional[str] = typer.Option(None, "--account", help="AWS account ID"),
    region: Optional[str] = typer.Option(None, "--region", help="AWS region"),
    profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile to use"),
    trust_accounts: Optional[str] = typer.Option(None, "--trust", help="Comma-separated list of account IDs to trust"),
    force: bool = typer.Option(False, "--force", help="Force bootstrap even if already bootstrapped"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be bootstrapped without executing"),
    approve: bool = typer.Option(False, "--approve", "-y", help="Auto-approve bootstrap operation"),
):
    """
    Run CDK bootstrap for the specified account/region.

    Bootstraps an AWS account/region for CDK deployments by creating the
    CDKToolkit CloudFormation stack and required resources.
    """
    console.print(Panel.fit(
        f"[bold blue]CDK Bootstrap Operation[/bold blue]\n\n"
        f"{'[yellow]DRY RUN - No changes will be made[/yellow]' if dry_run else 'This will bootstrap your AWS account/region for CDK deployments.'}\n\n"
        "Bootstrap creates:\n"
        "• CDKToolkit CloudFormation stack\n"
        "• S3 bucket for CDK assets\n"
        "• ECR repository for container images\n"
        "• IAM roles for deployment permissions",
        border_style="yellow" if dry_run else "blue"
    ))

    try:
        config = get_config_manager()
        bootstrap_checker = CDKBootstrapChecker(console=console)

        # Use config defaults if not provided
        account = account or config.config.aws.account_id
        region = region or config.config.aws.region
        profile = profile or config.config.aws.profile

        console.print(f"[dim]Target: {account or 'current account'}/{region or 'default region'}[/dim]")
        if profile:
            console.print(f"[dim]Profile: {profile}[/dim]")

        # Parse trust accounts
        trust_account_list = None
        if trust_accounts:
            trust_account_list = [acc.strip() for acc in trust_accounts.split(",")]
            console.print(f"[dim]Trust accounts: {', '.join(trust_account_list)}[/dim]")

        console.print()

        # Check current bootstrap status first
        console.print("[blue]Checking current bootstrap status...[/blue]")
        status = bootstrap_checker.check_bootstrap_status(
            account_id=account,
            region=region,
            profile=profile
        )

        if status.is_bootstrapped and not force:
            console.print(f"[green]✓ Account {status.account_id} region {status.region} is already bootstrapped[/green]")
            console.print("\n[yellow]No action needed. Use --force to bootstrap anyway.[/yellow]")
            return

        if dry_run:
            console.print(f"\n[yellow]DRY RUN: Would bootstrap {status.account_id}/{status.region}[/yellow]")
            console.print("This would create CDK bootstrap resources in your AWS account.")
            return

        # Confirm bootstrap operation
        if not approve:
            console.print(f"\n[bold]Ready to bootstrap {status.account_id}/{status.region}[/bold]")
            if not Confirm.ask("Continue with CDK bootstrap?"):
                console.print("Bootstrap cancelled.")
                raise typer.Exit()

        # Run bootstrap
        console.print(f"\n[bold]Bootstrapping {status.account_id}/{status.region}...[/bold]")

        success = bootstrap_checker.run_bootstrap(
            account_id=account,
            region=region,
            profile=profile,
            trust_account_ids=trust_account_list,
            force=force
        )

        if success:
            console.print(f"\n[green]✅ CDK bootstrap completed successfully![/green]")
            console.print(f"[dim]Account {status.account_id} region {status.region} is now ready for CDK deployments[/dim]")

            # Show updated status
            console.print("\n[blue]Verifying bootstrap status...[/blue]")
            updated_status = bootstrap_checker.check_bootstrap_status(
                account_id=account,
                region=region,
                profile=profile
            )
            bootstrap_checker.display_bootstrap_status(updated_status)

        else:
            console.print(f"\n[red]❌ CDK bootstrap failed[/red]")
            console.print("\n[yellow]Troubleshooting tips:[/yellow]")
            console.print("• Check AWS credentials and permissions")
            console.print("• Ensure you have admin permissions in the target account")
            console.print("• Verify network connectivity to AWS services")
            console.print("• Run 'blackwell doctor' for comprehensive diagnostics")
            raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Bootstrap operation cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Bootstrap operation failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def validate(
    account: Optional[str] = typer.Option(None, "--account", help="AWS account ID"),
    region: Optional[str] = typer.Option(None, "--region", help="AWS region"),
    profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile to use"),
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix validation issues automatically"),
):
    """
    Validate CDK bootstrap completeness and health.

    Performs comprehensive validation of CDK bootstrap resources including
    CDKToolkit stack, S3 bucket, ECR repository, and IAM roles.
    """
    console.print(Panel.fit(
        "[bold blue]CDK Bootstrap Validation[/bold blue]\n\n"
        "Performing comprehensive validation of CDK bootstrap resources\n"
        "and checking for any issues or missing components.",
        border_style="blue"
    ))

    try:
        config = get_config_manager()
        bootstrap_checker = CDKBootstrapChecker(console=console)

        # Use config defaults if not provided
        account = account or config.config.aws.account_id
        region = region or config.config.aws.region
        profile = profile or config.config.aws.profile

        console.print(f"[dim]Validating: {account or 'current account'}/{region or 'default region'}[/dim]\n")

        # Get detailed bootstrap status
        status = bootstrap_checker.check_bootstrap_status(
            account_id=account,
            region=region,
            profile=profile
        )

        # Display detailed status
        bootstrap_checker.display_bootstrap_status(status, verbose=True)

        # Analyze validation results
        issues = []
        warnings = []

        if not status.cdk_toolkit_stack_exists:
            issues.append("CDKToolkit CloudFormation stack is missing")

        if not status.is_bootstrapped:
            issues.append("Bootstrap is not complete")

        # Check individual resources
        for resource in status.resources:
            if resource.status == "missing":
                issues.append(f"{resource.resource_type.replace('_', ' ').title()} is missing: {resource.name}")
            elif resource.status == "error":
                issues.append(f"{resource.resource_type.replace('_', ' ').title()} has errors: {resource.error}")
            elif resource.status != "healthy":
                warnings.append(f"{resource.resource_type.replace('_', ' ').title()} status: {resource.status}")

        # Display validation summary
        console.print("\n")
        if not issues and not warnings:
            console.print("[green]✅ Bootstrap validation passed[/green]")
            console.print("All CDK bootstrap resources are healthy and ready for deployment.")
        else:
            if issues:
                console.print("[red]❌ Bootstrap validation failed[/red]")
                console.print("\n[bold red]Issues found:[/bold red]")
                for issue in issues:
                    console.print(f"  • [red]{issue}[/red]")

            if warnings:
                console.print("\n[bold yellow]Warnings:[/bold yellow]")
                for warning in warnings:
                    console.print(f"  • [yellow]{warning}[/yellow]")

            # Suggest fixes
            console.print("\n[yellow]💡 Recommendations:[/yellow]")
            if not status.cdk_toolkit_stack_exists:
                console.print("   Run: blackwell deploy bootstrap run")
            elif issues:
                console.print("   Run: blackwell deploy bootstrap run --force")

            if fix and issues:
                console.print("\n[blue]Attempting automatic fix...[/blue]")
                if not status.cdk_toolkit_stack_exists or not status.is_bootstrapped:
                    # Automatically run bootstrap
                    if Confirm.ask("Run CDK bootstrap to fix issues?"):
                        success = bootstrap_checker.run_bootstrap(
                            account_id=account,
                            region=region,
                            profile=profile,
                            force=True
                        )

                        if success:
                            console.print("[green]✓ Automatic fix completed[/green]")
                        else:
                            console.print("[red]✗ Automatic fix failed[/red]")
                            raise typer.Exit(1)
                    else:
                        console.print("Automatic fix cancelled.")

            if issues:
                raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Bootstrap validation cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Bootstrap validation failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def regions(
    profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile to use"),
    account: Optional[str] = typer.Option(None, "--account", help="AWS account ID"),
    include_regions: Optional[str] = typer.Option(None, "--include", help="Comma-separated list of regions to check"),
    exclude_regions: Optional[str] = typer.Option(None, "--exclude", help="Comma-separated list of regions to exclude"),
    bootstrap_missing: bool = typer.Option(False, "--bootstrap-missing", help="Bootstrap all missing regions"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done without executing"),
):
    """
    Check bootstrap status across multiple AWS regions.

    Provides a comprehensive view of CDK bootstrap status across multiple
    regions, with options to bootstrap missing regions.
    """
    console.print(Panel.fit(
        "[bold blue]Multi-Region Bootstrap Status[/bold blue]\n\n"
        "Checking CDK bootstrap status across multiple AWS regions\n"
        "to provide a comprehensive deployment readiness overview.",
        border_style="blue"
    ))

    try:
        config = get_config_manager()
        bootstrap_checker = CDKBootstrapChecker(console=console)

        # Use config defaults if not provided
        account = account or config.config.aws.account_id
        profile = profile or config.config.aws.profile

        # Determine regions to check
        if include_regions:
            regions_to_check = [r.strip() for r in include_regions.split(",")]
        else:
            # Default to common AWS regions
            regions_to_check = [
                "us-east-1", "us-west-2", "eu-west-1", "eu-central-1",
                "ap-southeast-1", "ap-northeast-1"
            ]

        if exclude_regions:
            exclude_list = [r.strip() for r in exclude_regions.split(",")]
            regions_to_check = [r for r in regions_to_check if r not in exclude_list]

        console.print(f"[dim]Checking {len(regions_to_check)} regions: {', '.join(regions_to_check)}[/dim]\n")

        # Check bootstrap status across regions
        statuses = bootstrap_checker.check_multiple_regions(
            regions=regions_to_check,
            account_id=account,
            profile=profile
        )

        # Display results
        bootstrap_checker.display_multi_region_status(statuses)

        # Identify missing bootstraps
        missing_regions = [
            region for region, status in statuses.items()
            if not status.is_bootstrapped
        ]

        if missing_regions:
            console.print(f"\n[yellow]Found {len(missing_regions)} regions without complete bootstrap:[/yellow]")
            for region in missing_regions:
                console.print(f"  • {region}")

            if bootstrap_missing:
                if dry_run:
                    console.print(f"\n[yellow]DRY RUN: Would bootstrap {len(missing_regions)} regions[/yellow]")
                    return

                console.print(f"\n[bold]Ready to bootstrap {len(missing_regions)} regions[/bold]")
                if not Confirm.ask("Continue with multi-region bootstrap?"):
                    console.print("Multi-region bootstrap cancelled.")
                    return

                # Bootstrap missing regions
                success_count = 0
                for region in missing_regions:
                    console.print(f"\n[blue]Bootstrapping {region}...[/blue]")

                    success = bootstrap_checker.run_bootstrap(
                        account_id=account,
                        region=region,
                        profile=profile
                    )

                    if success:
                        console.print(f"[green]✓ {region} bootstrap completed[/green]")
                        success_count += 1
                    else:
                        console.print(f"[red]✗ {region} bootstrap failed[/red]")

                console.print(f"\n[bold]Multi-region bootstrap summary:[/bold]")
                console.print(f"• {success_count}/{len(missing_regions)} regions bootstrapped successfully")

                if success_count == len(missing_regions):
                    console.print("[green]✅ All regions bootstrapped successfully![/green]")
                else:
                    console.print(f"[yellow]⚠ {len(missing_regions) - success_count} regions failed to bootstrap[/yellow]")
                    raise typer.Exit(1)

        else:
            console.print(f"\n[green]✅ All {len(regions_to_check)} regions are properly bootstrapped![/green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Multi-region bootstrap cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Multi-region bootstrap failed: {e}[/red]")
        raise typer.Exit(1)