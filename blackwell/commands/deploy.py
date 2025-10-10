"""Deploy Command - Deploy and manage infrastructure"""

import os
import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from blackwell.core.config_manager import ConfigManager

app = typer.Typer(help="Deploy, update, and destroy infrastructure")
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
def client(name: str = typer.Argument(..., help="Client name")):
    """Deploy client infrastructure."""
    console.print(f"Deploying client: {name}")
    console.print("[yellow]This command is under development[/yellow]")
    console.print("[dim]Hint: Deploy shared infrastructure first with 'blackwell deploy shared'[/dim]")


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


@app.command()
def status():
    """Check status of deployed infrastructure."""
    console.print("Checking infrastructure status...")
    console.print("[yellow]This command is under development[/yellow]")


@app.command()
def destroy(
    stack_name: str = typer.Argument(..., help="Stack name to destroy"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompt"),
):
    """Destroy deployed infrastructure."""
    if not force:
        if not Confirm.ask(f"[red]Are you sure you want to destroy {stack_name}?[/red]"):
            console.print("Cancelled.")
            raise typer.Exit()

    console.print(f"Destroying {stack_name}...")
    console.print("[yellow]This command is under development[/yellow]")
