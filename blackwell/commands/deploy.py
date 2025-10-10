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
        # Clean up temporary script
        try:
            os.unlink(script_path)
        except:
            pass
