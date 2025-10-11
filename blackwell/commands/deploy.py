"""Deploy Command - Deploy and manage infrastructure"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from blackwell.core.config_manager import ConfigManager

app = typer.Typer(help="Deploy, update, and destroy infrastructure", no_args_is_help=True)
console = Console()


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager."""
    from blackwell.main import get_config_manager
    return get_config_manager()


def find_platform_infrastructure_path() -> Optional[Path]:
    """Find the platform-infrastructure project path."""
    config = get_config_manager()

    if config.config.platform_infrastructure.path:
        path = Path(config.config.platform_infrastructure.path)
        if path.exists() and (path / "app.py").exists():
            return path

    search_paths = [
        Path.cwd() / "platform-infrastructure",
        Path.cwd().parent / "platform-infrastructure",
        Path.home() / "code" / "business" / "platform-infrastructure",
        Path("/home/blackwd/code/business/platform-infrastructure"),
    ]

    for path in search_paths:
        if path.exists() and (path / "app.py").exists():
            return path

    return None


def check_cdk_prerequisites(profile: Optional[str] = None) -> bool:
    """Check if CDK and AWS CLI are properly configured for a specific profile."""
    try:
        # Check that CDK is installed
        result = subprocess.run(["cdk", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            console.print("[red]AWS CDK not found. Please install CDK:[/red]")
            console.print("   npm install -g aws-cdk")
            return False

        # Validate AWS credentials using the specified profile
        sts_cmd = ["aws", "sts", "get-caller-identity"]
        if profile:
            sts_cmd.extend(["--profile", profile])

        result = subprocess.run(sts_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            console.print(f"[red]AWS CLI not configured or invalid credentials for profile '{profile}'.[/red]")
            console.print(f"   Please run: aws configure --profile {profile}")
            return False

        console.print(f"[green]CDK identity check:[/green] {result.stdout.strip()}")
        return True

    except FileNotFoundError as e:
        if "cdk" in str(e):
            console.print("[red]AWS CDK not found. Please install CDK:[/red]")
            console.print("   npm install -g aws-cdk")
        else:
            console.print("[red]AWS CLI not found. Please install AWS CLI.[/red]")
        return False


@app.command()
def client(
    name: str = typer.Argument(..., help="Client name to deploy"),
    account: Optional[str] = typer.Option(None, "--account", help="AWS account ID"),
    region: Optional[str] = typer.Option(None, "--region", help="AWS region"),
    profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile to use"),
    preview: bool = typer.Option(False, "--preview", help="Preview deployment without applying"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deployed without deploying"),
    approve: bool = typer.Option(False, "--approve", "-y", help="Auto-approve deployment"),
    force: bool = typer.Option(False, "--force", help="Force deployment even if validation fails"),
):
    """Deploy client infrastructure."""
    console.print(Panel.fit(
        f"[bold blue]Client Deployment: {name}[/bold blue]\n\n"
        "Deploying client infrastructure including:\n"
        "• Static site hosting (S3 + CloudFront)\n"
        "• CMS integration and webhooks\n"
        "• E-commerce provider connections\n"
        "• Custom domain and SSL certificates",
        border_style="blue"
    ))

    try:
        # Initialize managers
        config_manager = get_config_manager()

        from blackwell.core.client_manager import ClientManager
        client_manager = ClientManager(config_manager)

        # Find platform-infrastructure path
        platform_path = find_platform_infrastructure_path()
        if not platform_path:
            console.print("[red]Could not find platform-infrastructure project.[/red]")
            console.print("\n[dim]Configure the path with:[/dim]")
            console.print("blackwell config set platform_infrastructure.path /path/to/platform-infrastructure")
            raise typer.Exit(1)

        # Load client configuration
        client = client_manager.get_client(name)
        if not client:
            console.print(f"[red]Client '{name}' not found.[/red]")
            console.print("\n[dim]Available clients:[/dim]")
            for c in client_manager.list_clients():
                console.print(f"  • {c.name} ({c.company_name})")
            console.print(f"\n[dim]Create client with:[/dim] blackwell create client {name}")
            raise typer.Exit(1)

        console.print(f"[green]Found client configuration:[/green] {client.company_name}")

        # Validate client configuration
        if not force:
            console.print("\n[bold]Validating client configuration...[/bold]")
            issues = client_manager.validate_client(name)
            if issues:
                console.print("[red]⚠ Configuration issues found:[/red]")
                for issue in issues:
                    console.print(f"  • [red]{issue}[/red]")
                console.print("\n[dim]Fix issues or use --force to deploy anyway[/dim]")
                if not Confirm.ask("Continue with deployment despite issues?"):
                    raise typer.Exit(1)
            else:
                console.print("[green]✓ Configuration valid[/green]")

        # Get AWS configuration from arguments or config
        aws_account = account or config_manager.config.aws.account_id
        aws_region = region or config_manager.config.aws.region
        aws_profile = profile or config_manager.config.aws.profile

        console.print(f"[dim]CDK Context → Account: {aws_account}, Region: {aws_region}, Profile: {aws_profile}[/dim]")

        # Check prerequisites
        if not check_cdk_prerequisites(profile=aws_profile):
            raise typer.Exit(1)

        # Update client status
        client_manager.update_client_status(name, "deploying", {"deployment_type": "client_infrastructure"})

        # Generate deployment script
        console.print("\n[bold]Generating deployment script...[/bold]")
        deploy_script = _generate_client_deployment_script(client, platform_path)

        if preview:
            console.print("\n[bold]Deployment Script Preview:[/bold]")
            console.print(Panel(deploy_script, title="Generated Python Script", border_style="dim"))
            console.print("\n[yellow]Preview mode - no deployment performed[/yellow]")
            return

        # Execute deployment or dry-run
        action = "dry-run" if dry_run else "deployment"
        console.print(f"\n[bold]{'Running dry-run for' if dry_run else 'Deploying'} {client.stack_name}...[/bold]")

        success = _execute_client_deployment(
            client=client,
            platform_path=platform_path,
            deploy_script=deploy_script,
            config_manager=config_manager,
            approve=approve,
            dry_run=dry_run,
            aws_account=aws_account,
            aws_region=aws_region,
            aws_profile=aws_profile
        )

        if success:
            if dry_run:
                console.print(f"\n[green]✅ Dry-run completed successfully for client '{name}'![/green]")
                console.print(f"\n[bold]Stack Name:[/bold] {client.stack_name}")
                console.print(f"[bold]Domain:[/bold] {client.domain}")
                console.print("\n[yellow]The above shows what would be deployed.[/yellow]")
                console.print(f"[dim]To actually deploy, run:[/dim] blackwell deploy client {name} --approve")
            else:
                client_manager.update_client_status(
                    name, "deployed",
                    {"deployment_time": "now", "stack_name": client.stack_name},
                    update_deployment_time=True
                )
                console.print(f"\n[green]✅ Client '{name}' deployed successfully![/green]")
                console.print(f"\n[bold]Stack Name:[/bold] {client.stack_name}")
                console.print(f"[bold]Domain:[/bold] {client.domain}")
                console.print(f"[bold]Status:[/bold] {client.status}")

                console.print("\n[yellow]Next steps:[/yellow]")
                console.print(f"• Configure DNS: Point {client.domain} to CloudFront distribution")
                console.print(f"• Test site: Visit https://{client.domain}")
                console.print(f"• Monitor costs: blackwell cost analyze {name}")
        else:
            if not dry_run:
                client_manager.update_client_status(name, "error", {"error": "deployment_failed"})
            console.print(f"\n[red]❌ {'Dry-run' if dry_run else 'Deployment'} failed for client '{name}'[/red]")
            raise typer.Exit(1)

    except KeyboardInterrupt:
        if 'client_manager' in locals() and 'name' in locals():
            client_manager.update_client_status(name, "error", {"error": "deployment_cancelled"})
        console.print("\n[yellow]Deployment cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        if 'client_manager' in locals() and 'name' in locals():
            client_manager.update_client_status(name, "error", {"error": str(e)})
        console.print(f"\n[red]Deployment failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def shared(
    account: Optional[str] = typer.Option(None, "--account", help="AWS account ID"),
    region: Optional[str] = typer.Option(None, "--region", help="AWS region"),
    profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile to use"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deployed without deploying"),
    approve: bool = typer.Option(False, "--approve", "-y", help="Auto-approve deployment"),
):
    """Deploy shared infrastructure required for all client deployments."""

    console.print(Panel.fit(
        "[bold blue]Shared Infrastructure Deployment[/bold blue]\n\n"
        "This deploys the foundational infrastructure required before any client deployments:\n"
        "• Business domain management (Route53)\n"
        "• Cost allocation and monitoring\n"
        "• Operational dashboards and alerts\n"
        "• Shared storage and backup coordination",
        border_style="blue"
    ))

    platform_path = find_platform_infrastructure_path()
    if not platform_path:
        console.print("[red]Could not find platform-infrastructure project.[/red]")
        console.print("\n[yellow]Searched in:[/yellow]")
        console.print("• ./platform-infrastructure")
        console.print("• ../platform-infrastructure")
        console.print("• ~/code/business/platform-infrastructure")
        console.print("\n[dim]Configure the path with:[/dim]")
        console.print("blackwell config set platform_infrastructure.path /path/to/platform-infrastructure")
        raise typer.Exit(1)

    console.print(f"[green]Found platform-infrastructure at:[/green] {platform_path}")

    # Check prerequisites under the selected profile
    if not check_cdk_prerequisites(profile=profile):
        raise typer.Exit(1)

    config = get_config_manager()

    aws_account = account or config.config.aws.account_id
    aws_region = region or config.config.aws.region
    aws_profile = profile or config.config.aws.profile

    # Isolate environment variables to avoid SSO pollution
    env = {k: v for k, v in os.environ.items() if not k.startswith("AWS_")}
    env["AWS_PROFILE"] = aws_profile
    env["AWS_DEFAULT_REGION"] = aws_region or "us-east-1"
    env["AWS_SDK_LOAD_CONFIG"] = "1"

    console.print(f"[dim]CDK Context → Account: {aws_account}, Region: {aws_region}, Profile: {aws_profile}[/dim]")

    original_cwd = os.getcwd()
    try:
        os.chdir(platform_path)

        # Build CDK command with explicit profile and context
        cdk_cmd = [
            "cdk",
            "diff" if dry_run else "deploy",
            "WebServices-SharedInfra",
            "--profile", aws_profile or "default",
            "-c", f"account={aws_account}",
            "-c", f"region={aws_region or 'us-east-1'}",
        ]

        if not dry_run and approve:
            cdk_cmd.append("--require-approval=never")

        console.print(f"[blue]{'Running dry-run' if dry_run else 'Deploying shared infrastructure'}...[/blue]")
        console.print(f"[dim]Executing: {' '.join(cdk_cmd)}[/dim]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=False if dry_run else True
        ) as progress:
            if not dry_run:
                task = progress.add_task("Deploying shared infrastructure...", total=None)

            process = subprocess.Popen(
                cdk_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                bufsize=1,
                universal_newlines=True
            )

            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    if dry_run:
                        console.print(line.rstrip())
                    else:
                        if "CREATE_COMPLETE" in line or "UPDATE_COMPLETE" in line:
                            console.print(f"[green]{line.strip()}[/green]")
                        elif "CREATE_IN_PROGRESS" in line or "UPDATE_IN_PROGRESS" in line:
                            console.print(f"[blue]{line.strip()}[/blue]")
                        elif "FAILED" in line or "ERROR" in line:
                            console.print(f"[red]{line.strip()}[/red]")
                        else:
                            console.print(f"[dim]{line.strip()}[/dim]")

            return_code = process.wait()

            if return_code == 0:
                if dry_run:
                    console.print("\n[green]Dry-run completed successfully[/green]")
                else:
                    console.print("\n[green]Shared infrastructure deployed successfully![/green]")
                    console.print("\n[yellow]Next steps:[/yellow]")
                    console.print("• View operational dashboard in AWS CloudWatch")
                    console.print("• Deploy client infrastructure with: blackwell deploy client <name>")
                    console.print("• Check cost allocation: blackwell cost analyze")
            else:
                console.print(f"\n[red]Deployment failed with exit code {return_code}[/red]")
                raise typer.Exit(return_code)

    except KeyboardInterrupt:
        console.print("\n[yellow]Deployment cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Deployment failed: {e}[/red]")
        raise typer.Exit(1)
    finally:
        os.chdir(original_cwd)


def _resolve_destroy_target(target: str, config) -> Tuple[Optional[str], bool]:
    """
    Resolve a user-friendly target name to actual stack name.

    Returns:
        tuple: (stack_name, is_shared) or (None, False) if not found
    """
    if target == "shared":
        return "WebServices-SharedInfra", True

    # Try to find as client name
    try:
        from blackwell.core.client_manager import ClientManager
        client_manager = ClientManager(config)
        client = client_manager.get_client(target)
        if client:
            # Return the client's stack name
            return getattr(client, 'stack_name', f"{target.title()}-Prod-Stack"), False
    except Exception:
        pass

    return None, False


@app.command()
def status(
    account: Optional[str] = typer.Option(None, "--account", help="AWS account ID"),
    region: Optional[str] = typer.Option(None, "--region", help="AWS region"),
    profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile to use"),
):
    """Check status of deployed infrastructure."""
    console.print(Panel.fit(
        "[bold blue]Infrastructure Status Check[/bold blue]\n\n"
        "Checking deployment status of shared and client infrastructure",
        border_style="blue"
    ))

    try:
        config = get_config_manager()

        # Use provided parameters with fallback to config
        aws_account = account or config.config.aws.account_id
        aws_region = region or config.config.aws.region
        aws_profile = profile or config.config.aws.profile

        console.print(f"[dim]Using AWS profile: {aws_profile}, region: {aws_region}, account: {aws_account}[/dim]\n")

        # Check shared infrastructure status
        shared_status = _check_shared_infrastructure_status(aws_profile, aws_region)

        # Display shared infrastructure status
        _display_shared_status(shared_status)

        # Check client infrastructure status
        from blackwell.core.client_manager import ClientManager
        client_manager = ClientManager(config)
        client_summary = client_manager.get_client_summary()

        # Display client status summary
        _display_client_status_summary(client_summary)

    except Exception as e:
        console.print(f"[red]Error checking infrastructure status: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def destroy(
    target: str = typer.Argument(..., help="What to destroy: 'shared' or client name"),
    account: Optional[str] = typer.Option(None, "--account", help="AWS account ID"),
    region: Optional[str] = typer.Option(None, "--region", help="AWS region"),
    profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile to use"),
    force: bool = typer.Option(False, "--force", help="Skip all confirmation prompts"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be destroyed without destroying"),
):
    """
    Destroy deployed infrastructure.

    ⚠️  DANGER: This permanently deletes AWS resources and data.

    Examples:
    • blackwell deploy destroy shared - Destroy shared infrastructure
    • blackwell deploy destroy my-client - Destroy specific client infrastructure

    Use --dry-run first to see what will be destroyed.
    """
    try:
        # Get configuration
        config = get_config_manager()
        aws_account = account or config.config.aws.account_id
        aws_region = region or config.config.aws.region
        aws_profile = profile or config.config.aws.profile

        # Resolve the target to actual stack name
        stack_name, is_shared = _resolve_destroy_target(target, config)
        if not stack_name:
            console.print(f"[red]Target '{target}' not found.[/red]")
            if target != "shared":
                console.print("\n[dim]Available clients:[/dim]")
                from blackwell.core.client_manager import ClientManager
                client_manager = ClientManager(config)
                clients = client_manager.list_clients()
                for client in clients:
                    console.print(f"  • {client.name}")
                console.print(f"\n[dim]Or use 'shared' to destroy shared infrastructure[/dim]")
            raise typer.Exit(1)

        console.print(Panel.fit(
            f"[bold red]{'DRY RUN - ' if dry_run else ''}Infrastructure Destruction: {target}[/bold red]\n\n"
            f"[dim]Actual stack: {stack_name}[/dim]\n\n"
            f"{'[yellow]This is a dry run - no resources will be destroyed[/yellow]' if dry_run else '[red]⚠️  WARNING: This will permanently delete AWS resources![/red]'}\n\n"
            "This action will destroy:\n"
            "• All AWS resources in the stack\n"
            "• All data stored in those resources\n"
            "• All configurations and settings\n\n"
            f"{'Preview what would be destroyed' if dry_run else 'This action cannot be undone'}",
            border_style="red" if not dry_run else "yellow"
        ))

        console.print(f"[dim]Using AWS profile: {aws_profile}, region: {aws_region}, account: {aws_account}[/dim]\n")

        # Check prerequisites
        if not check_cdk_prerequisites(profile=aws_profile):
            raise typer.Exit(1)

        # Check if stack exists
        console.print("[blue]Checking stack status...[/blue]")
        stack_status = _check_stack_status(stack_name, aws_profile, aws_region)

        if not stack_status['exists']:
            if stack_status['status'] == 'NOT_DEPLOYED':
                console.print(f"[yellow]Stack '{stack_name}' does not exist or is not deployed.[/yellow]")
                console.print("[dim]Nothing to destroy.[/dim]")
                return
            else:
                console.print(f"[red]Error checking stack status: {stack_status.get('error', 'Unknown error')}[/red]")
                raise typer.Exit(1)

        # Display what will be destroyed
        console.print(f"[yellow]Stack found:[/yellow] {stack_name}")
        console.print(f"[yellow]Status:[/yellow] {stack_status['status']}")
        if stack_status.get('creation_time'):
            console.print(f"[yellow]Created:[/yellow] {stack_status['creation_time'].strftime('%Y-%m-%d %H:%M:%S UTC')}")

        # Find platform-infrastructure path
        platform_path = find_platform_infrastructure_path()
        if not platform_path:
            console.print("[red]Could not find platform-infrastructure project.[/red]")
            console.print("\n[dim]Configure the path with:[/dim]")
            console.print("blackwell config set platform_infrastructure.path /path/to/platform-infrastructure")
            raise typer.Exit(1)

        console.print(f"[green]Found platform-infrastructure at:[/green] {platform_path}")

        # Enhanced safety checks for shared infrastructure
        if is_shared and not dry_run:
            console.print("\n[red]⚠️  CRITICAL WARNING: You are about to destroy SHARED INFRASTRUCTURE![/red]")
            console.print("[red]This will affect ALL client deployments and may cause:[/red]")
            console.print("• All client sites to become unavailable")
            console.print("• Loss of shared DNS and routing configuration")
            console.print("• Loss of monitoring and operational dashboards")
            console.print("• Potential data loss in shared storage systems")

            if not force:
                console.print(f"\n[bold red]Type 'shared' to confirm destruction of shared infrastructure:[/bold red]")
                confirmation = typer.prompt("Confirmation")
                if confirmation != "shared":
                    console.print("[yellow]Confirmation mismatch. Cancelled.[/yellow]")
                    raise typer.Exit()

                if not Confirm.ask(f"[red]Are you absolutely sure you want to destroy shared infrastructure?[/red]"):
                    console.print("Cancelled.")
                    raise typer.Exit()

        elif not dry_run and not force:
            display_name = "shared infrastructure" if is_shared else f"client '{target}'"
            if not Confirm.ask(f"[red]Are you sure you want to destroy {display_name}?[/red]"):
                console.print("Cancelled.")
                raise typer.Exit()

        # Execute destruction
        success = _execute_stack_destruction(
            stack_name=stack_name,
            platform_path=platform_path,
            aws_account=aws_account,
            aws_region=aws_region,
            aws_profile=aws_profile,
            dry_run=dry_run
        )

        if success:
            if dry_run:
                display_name = "shared infrastructure" if is_shared else f"client '{target}'"
                console.print(f"\n[green]✅ Dry-run completed for {display_name}[/green]")
                console.print("[yellow]The above shows what would be destroyed.[/yellow]")
                console.print(f"[dim]To actually destroy, run:[/dim] blackwell deploy destroy {target} --force")
            else:
                if is_shared:
                    console.print(f"\n[green]✅ Shared infrastructure destroyed successfully![/green]")
                    console.print("\n[yellow]⚠️  All client deployments may be affected.[/yellow]")
                    console.print("Redeploy shared infrastructure before deploying clients:")
                    console.print("   blackwell deploy shared --approve")
                else:
                    console.print(f"\n[green]✅ Client '{target}' infrastructure destroyed successfully![/green]")
        else:
            display_name = "shared infrastructure" if is_shared else f"client '{target}'"
            console.print(f"\n[red]❌ {'Dry-run' if dry_run else 'Destruction'} failed for {display_name}[/red]")
            raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Destruction cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Destruction failed: {e}[/red]")
        raise typer.Exit(1)


def _check_shared_infrastructure_status(aws_profile: str, aws_region: str) -> dict:
    """Check the status of the shared infrastructure stack."""
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, ClientError

        # Create CloudFormation client with the specified profile
        session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
        cloudformation = session.client('cloudformation')

        stack_name = "WebServices-SharedInfra"

        try:
            # Get stack status
            response = cloudformation.describe_stacks(StackName=stack_name)
            stack = response['Stacks'][0]

            return {
                'exists': True,
                'stack_name': stack['StackName'],
                'status': stack['StackStatus'],
                'creation_time': stack.get('CreationTime'),
                'last_updated_time': stack.get('LastUpdatedTime'),
                'description': stack.get('Description', ''),
                'drift_status': None  # We'll check this separately if needed
            }

        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationError':
                # Stack doesn't exist
                return {
                    'exists': False,
                    'stack_name': stack_name,
                    'status': 'NOT_DEPLOYED',
                    'error': None
                }
            else:
                raise e

    except (NoCredentialsError, ClientError) as e:
        return {
            'exists': False,
            'stack_name': 'WebServices-SharedInfra',
            'status': 'ERROR',
            'error': str(e)
        }
    except ImportError:
        return {
            'exists': False,
            'stack_name': 'WebServices-SharedInfra',
            'status': 'ERROR',
            'error': 'boto3 not available - please install with: pip install boto3'
        }


def _display_shared_status(status_info: dict) -> None:
    """Display shared infrastructure status in a formatted way."""
    from rich.table import Table

    # Create status table
    table = Table(title="Shared Infrastructure Status", show_header=True, header_style="bold magenta")
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    table.add_row("Stack Name", status_info['stack_name'])

    # Color-code the status
    status = status_info['status']
    if status in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
        status_display = f"[green]✅ {status}[/green]"
    elif status in ['CREATE_IN_PROGRESS', 'UPDATE_IN_PROGRESS']:
        status_display = f"[yellow]🔄 {status}[/yellow]"
    elif status == 'NOT_DEPLOYED':
        status_display = f"[yellow]❌ Not Deployed[/yellow]"
    elif 'FAILED' in status or status == 'ERROR':
        status_display = f"[red]❌ {status}[/red]"
    else:
        status_display = f"[dim]{status}[/dim]"

    table.add_row("Status", status_display)

    if status_info['exists']:
        if status_info.get('creation_time'):
            table.add_row("Created", status_info['creation_time'].strftime('%Y-%m-%d %H:%M:%S UTC'))
        if status_info.get('last_updated_time'):
            table.add_row("Last Updated", status_info['last_updated_time'].strftime('%Y-%m-%d %H:%M:%S UTC'))
        if status_info.get('description'):
            table.add_row("Description", status_info['description'])

    if status_info.get('error'):
        table.add_row("Error", f"[red]{status_info['error']}[/red]")

    console.print(table)

    # Show deployment guidance
    if not status_info['exists'] and status_info['status'] == 'NOT_DEPLOYED':
        console.print("\n[yellow]💡 To deploy shared infrastructure:[/yellow]")
        console.print("   blackwell deploy shared --approve")
    elif status_info['status'] == 'ERROR':
        console.print("\n[red]⚠ There was an error checking the shared infrastructure status.[/red]")
        console.print("   Please check your AWS credentials and try again.")


def _display_client_status_summary(client_summary: dict) -> None:
    """Display client infrastructure status summary."""
    from rich.table import Table

    if client_summary['total'] == 0:
        console.print("\n[dim]No clients configured yet.[/dim]")
        console.print("[yellow]💡 Create your first client with:[/yellow] blackwell create client")
        return

    # Create client summary table
    table = Table(title="Client Infrastructure Summary", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    table.add_row("Total Clients", str(client_summary['total']))
    table.add_row("Deployed Clients", str(client_summary['deployed']))

    # Status breakdown
    if client_summary.get('status_breakdown'):
        status_text = []
        for status, count in client_summary['status_breakdown'].items():
            if status == 'deployed':
                status_text.append(f"[green]{count} {status}[/green]")
            elif status == 'error':
                status_text.append(f"[red]{count} {status}[/red]")
            elif status in ['deploying', 'updating']:
                status_text.append(f"[yellow]{count} {status}[/yellow]")
            else:
                status_text.append(f"[dim]{count} {status}[/dim]")
        table.add_row("Status Breakdown", " | ".join(status_text))

    # Cost information
    if client_summary.get('total_estimated_cost', 0) > 0:
        table.add_row("Est. Monthly Cost", f"${client_summary['total_estimated_cost']:.2f}")
    if client_summary.get('total_actual_cost', 0) > 0:
        table.add_row("Actual Monthly Cost", f"${client_summary['total_actual_cost']:.2f}")

    console.print("\n")
    console.print(table)

    # Show management guidance
    if client_summary['deployed'] > 0:
        console.print(f"\n[green]✅ {client_summary['deployed']} client(s) successfully deployed![/green]")

    if client_summary['total'] > client_summary['deployed']:
        remaining = client_summary['total'] - client_summary['deployed']
        console.print(f"\n[yellow]💡 {remaining} client(s) ready for deployment:[/yellow]")
        console.print("   blackwell deploy client <name> --approve")


def _generate_client_deployment_script(client, platform_path: Path) -> str:
    """Generate deployment script for client infrastructure."""
    from blackwell.core.client_manager import CLIClientConfig

    if not isinstance(client, CLIClientConfig):
        raise ValueError("Invalid client configuration")

    # Determine stack type and import based on client configuration
    service_type = client.get_service_type()
    stack_imports = []
    stack_class = None
    stack_params = {}

    if service_type == "static_site":
        # Use the lightest base SSG stack
        stack_imports.append("from stacks.shared.base_ssg_stack import BaseSSGStack")
        stack_class = "BaseSSGStack"
        stack_params = {
            "client_id": client.name,
            "domain": client.domain
        }

    elif service_type == "cms_tier":
        # Use the lightest available stack - base SSG stack
        stack_imports.append("from stacks.shared.base_ssg_stack import BaseSSGStack")
        stack_class = "BaseSSGStack"
        stack_params = {
            "client_id": client.name,
            "domain": client.domain
        }

    elif service_type == "ecommerce_tier":
        # Use base SSG stack for e-commerce tiers too
        stack_imports.append("from stacks.shared.base_ssg_stack import BaseSSGStack")
        stack_class = "BaseSSGStack"
        stack_params = {
            "client_id": client.name,
            "domain": client.domain
        }

    else:
        # Fallback to lightest stack - base SSG stack
        stack_imports.append("from stacks.shared.base_ssg_stack import BaseSSGStack")
        stack_class = "BaseSSGStack"
        stack_params = {
            "client_id": client.name,
            "domain": client.domain
        }

    # Generate the deployment script
    script_template = f'''#!/usr/bin/env python3
"""
Generated deployment script for client: {client.name}
Company: {client.company_name}
Generated by Blackwell CLI
"""

import aws_cdk as cdk
from stacks.shared.base_ssg_stack import BaseSSGStack
from models.service_config import ClientServiceConfig

def main():
    """Deploy {client.name} infrastructure."""
    app = cdk.App()

    # Create client configuration
    client_config = ClientServiceConfig(
        client_id="{client.name}",
        company_name="{client.company_name}",
        contact_email="{client.contact_email}",
        domain="{client.domain}",
        service_tier="{client.service_tier}",
        management_model="{client.management_model}",
        service_integration={{"service_type": "static_site", "ssg_engine": "{client.ssg_engine}"}}
    )

    # Deploy {client.stack_name}
    BaseSSGStack(
        app,
        "{client.stack_name}",
        client_config=client_config,
        description="Lightest infrastructure for {client.company_name} ({client.name})",
        env=cdk.Environment(
            account=app.node.try_get_context("account"),
            region=app.node.try_get_context("region") or "{client.aws_region}"
        ),
        tags={{
            "Client": "{client.name}",
            "Company": "{client.company_name}",
            "ManagedBy": "BlackwellCLI",
            "Environment": "prod"
        }}
    )

    app.synth()

if __name__ == "__main__":
    main()
'''

    return script_template


def _format_stack_params(params: dict) -> str:
    """Format stack parameters for Python code generation."""
    lines = []
    for key, value in params.items():
        if isinstance(value, str):
            lines.append(f'        {key}="{value}",')
        else:
            lines.append(f'        {key}={value},')
    return '\n'.join(lines)


def _execute_client_deployment(
    client, platform_path: Path, deploy_script: str, config_manager, approve: bool = False, dry_run: bool = False,
    aws_account: Optional[str] = None, aws_region: Optional[str] = None, aws_profile: Optional[str] = None
) -> bool:
    """Execute client deployment using generated script."""
    import tempfile
    import subprocess

    # Create temporary deployment script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(deploy_script)
        script_path = f.name

    original_cwd = os.getcwd()
    try:
        os.chdir(platform_path)

        # Set up environment
        env = {k: v for k, v in os.environ.items() if not k.startswith("AWS_")}
        env["AWS_PROFILE"] = aws_profile or "default"
        env["AWS_DEFAULT_REGION"] = aws_region or "us-east-1"
        env["AWS_SDK_LOAD_CONFIG"] = "1"

        console.print(f"[dim]Using AWS profile: {aws_profile}, region: {aws_region}[/dim]")

        # First, synthesize the CDK app to check for errors
        console.print("[blue]Synthesizing CDK application...[/blue]")
        synth_cmd = ["python", script_path]
        synth_result = subprocess.run(
            synth_cmd,
            env=env,
            capture_output=True,
            text=True
        )

        if synth_result.returncode != 0:
            console.print(f"[red]CDK synthesis failed:[/red]")
            console.print(synth_result.stderr)
            return False

        console.print("[green]✓ CDK synthesis successful[/green]")

        # Now deploy or diff using CDK
        action = "diff" if dry_run else "deploy"
        console.print(f"[blue]{'Running diff for' if dry_run else 'Deploying'} {client.stack_name}...[/blue]")

        cdk_cmd = [
            "cdk", action, client.stack_name,
            "--app", f"python {script_path}",
            "--profile", aws_profile or "default",
            "-c", f"account={aws_account}",
            "-c", f"region={aws_region or 'us-east-1'}"
        ]

        if not dry_run and approve:
            cdk_cmd.append("--require-approval=never")

        console.print(f"[dim]Executing: {' '.join(cdk_cmd)}[/dim]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=False if dry_run else True
        ) as progress:
            if not dry_run:
                task = progress.add_task("Deploying infrastructure...", total=None)

            process = subprocess.Popen(
                cdk_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                bufsize=1,
                universal_newlines=True
            )

            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    if dry_run:
                        console.print(line.rstrip())
                    else:
                        if "CREATE_COMPLETE" in line or "UPDATE_COMPLETE" in line:
                            console.print(f"[green]{line.strip()}[/green]")
                        elif "CREATE_IN_PROGRESS" in line or "UPDATE_IN_PROGRESS" in line:
                            console.print(f"[blue]{line.strip()}[/blue]")
                        elif "FAILED" in line or "ERROR" in line:
                            console.print(f"[red]{line.strip()}[/red]")
                        else:
                            console.print(f"[dim]{line.strip()}[/dim]")

            return_code = process.wait()
            return return_code == 0

    finally:
        os.chdir(original_cwd)




def _check_stack_status(stack_name: str, aws_profile: str, aws_region: str) -> dict:
    """Check the status of any CloudFormation stack."""
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, ClientError

        # Create CloudFormation client with the specified profile
        session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
        cloudformation = session.client('cloudformation')

        try:
            # Get stack status
            response = cloudformation.describe_stacks(StackName=stack_name)
            stack = response['Stacks'][0]

            return {
                'exists': True,
                'stack_name': stack['StackName'],
                'status': stack['StackStatus'],
                'creation_time': stack.get('CreationTime'),
                'last_updated_time': stack.get('LastUpdatedTime'),
                'description': stack.get('Description', ''),
                'drift_status': None  # We'll check this separately if needed
            }

        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationError':
                # Stack doesn't exist
                return {
                    'exists': False,
                    'stack_name': stack_name,
                    'status': 'NOT_DEPLOYED',
                    'error': None
                }
            else:
                raise e

    except (NoCredentialsError, ClientError) as e:
        return {
            'exists': False,
            'stack_name': stack_name,
            'status': 'ERROR',
            'error': str(e)
        }
    except ImportError:
        return {
            'exists': False,
            'stack_name': stack_name,
            'status': 'ERROR',
            'error': 'boto3 not available - please install with: pip install boto3'
        }


def _execute_stack_destruction(
    stack_name: str,
    platform_path: Path,
    aws_account: str,
    aws_region: str,
    aws_profile: str,
    dry_run: bool = False
) -> bool:
    """Execute stack destruction using CDK destroy command."""
    original_cwd = os.getcwd()
    try:
        os.chdir(platform_path)

        # Set up environment
        env = {k: v for k, v in os.environ.items() if not k.startswith("AWS_")}
        env["AWS_PROFILE"] = aws_profile or "default"
        env["AWS_DEFAULT_REGION"] = aws_region or "us-east-1"
        env["AWS_SDK_LOAD_CONFIG"] = "1"

        # Build CDK command
        if dry_run:
            # For dry run, use diff to show what would be destroyed
            cdk_cmd = [
                "cdk", "diff", stack_name,
                "--profile", aws_profile or "default",
                "-c", f"account={aws_account}",
                "-c", f"region={aws_region or 'us-east-1'}"
            ]
            console.print("[blue]Running destruction preview (diff)...[/blue]")
        else:
            # For actual destruction, use destroy
            cdk_cmd = [
                "cdk", "destroy", stack_name,
                "--profile", aws_profile or "default",
                "-c", f"account={aws_account}",
                "-c", f"region={aws_region or 'us-east-1'}",
                "--force"  # Skip CDK confirmation since we handle our own
            ]
            console.print(f"[red]Destroying stack '{stack_name}'...[/red]")

        console.print(f"[dim]Executing: {' '.join(cdk_cmd)}[/dim]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=False if dry_run else True
        ) as progress:
            if not dry_run:
                task = progress.add_task("Destroying infrastructure...", total=None)

            process = subprocess.Popen(
                cdk_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                bufsize=1,
                universal_newlines=True
            )

            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    if dry_run:
                        console.print(line.rstrip())
                    else:
                        if "DELETE_COMPLETE" in line:
                            console.print(f"[green]{line.strip()}[/green]")
                        elif "DELETE_IN_PROGRESS" in line:
                            console.print(f"[yellow]{line.strip()}[/yellow]")
                        elif "FAILED" in line or "ERROR" in line:
                            console.print(f"[red]{line.strip()}[/red]")
                        else:
                            console.print(f"[dim]{line.strip()}[/dim]")

            return_code = process.wait()
            return return_code == 0

    finally:
        os.chdir(original_cwd)


