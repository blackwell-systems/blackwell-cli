"""
CDK Bootstrap Checker - Detect and validate CDK bootstrap status

This module provides comprehensive CDK bootstrap detection and validation
for AWS accounts and regions, supporting the Blackwell CLI deployment workflows.
"""

import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel


@dataclass
class BootstrapResource:
    """Information about a CDK bootstrap resource."""
    name: str
    resource_type: str
    status: str
    arn: Optional[str] = None
    created_date: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class BootstrapStatus:
    """Complete CDK bootstrap status for an account/region."""
    account_id: str
    region: str
    profile: Optional[str]
    is_bootstrapped: bool
    cdk_toolkit_stack_exists: bool
    cdk_toolkit_version: Optional[str] = None
    resources: List[BootstrapResource] = None
    errors: List[str] = None
    checked_at: datetime = None

    def __post_init__(self):
        if self.resources is None:
            self.resources = []
        if self.errors is None:
            self.errors = []
        if self.checked_at is None:
            self.checked_at = datetime.utcnow()


class CDKBootstrapChecker:
    """
    CDK Bootstrap detection and validation utility.

    Provides methods to check if AWS accounts/regions are properly bootstrapped
    for CDK deployments, including validation of required resources.
    """

    def __init__(self, console: Optional[Console] = None):
        """Initialize the bootstrap checker."""
        self.console = console or Console()

    def check_bootstrap_status(
        self,
        account_id: Optional[str] = None,
        region: Optional[str] = None,
        profile: Optional[str] = None
    ) -> BootstrapStatus:
        """
        Check CDK bootstrap status for the specified account/region.

        Args:
            account_id: AWS account ID (if None, will be detected)
            region: AWS region (if None, will use default region)
            profile: AWS profile name (if None, will use default)

        Returns:
            BootstrapStatus with complete bootstrap information
        """
        try:
            # Get AWS account and region if not provided
            if not account_id or not region:
                detected_account, detected_region = self._get_aws_context(profile)
                account_id = account_id or detected_account
                region = region or detected_region

            if not account_id or not region:
                return BootstrapStatus(
                    account_id=account_id or "unknown",
                    region=region or "unknown",
                    profile=profile,
                    is_bootstrapped=False,
                    cdk_toolkit_stack_exists=False,
                    errors=["Could not determine AWS account ID or region"]
                )

            # Check for CDKToolkit stack
            toolkit_status = self._check_cdk_toolkit_stack(account_id, region, profile)

            # If toolkit stack exists, validate bootstrap resources
            resources = []
            if toolkit_status["exists"]:
                resources = self._validate_bootstrap_resources(account_id, region, profile)

            is_bootstrapped = (
                toolkit_status["exists"] and
                all(r.status == "healthy" for r in resources if r.resource_type in ["s3_bucket", "iam_roles"])
            )

            return BootstrapStatus(
                account_id=account_id,
                region=region,
                profile=profile,
                is_bootstrapped=is_bootstrapped,
                cdk_toolkit_stack_exists=toolkit_status["exists"],
                cdk_toolkit_version=toolkit_status.get("version"),
                resources=resources,
                errors=toolkit_status.get("errors", [])
            )

        except Exception as e:
            return BootstrapStatus(
                account_id=account_id or "unknown",
                region=region or "unknown",
                profile=profile,
                is_bootstrapped=False,
                cdk_toolkit_stack_exists=False,
                errors=[f"Bootstrap check failed: {str(e)}"]
            )

    def check_multiple_regions(
        self,
        regions: List[str],
        account_id: Optional[str] = None,
        profile: Optional[str] = None
    ) -> Dict[str, BootstrapStatus]:
        """
        Check bootstrap status across multiple regions.

        Args:
            regions: List of AWS regions to check
            account_id: AWS account ID (if None, will be detected)
            profile: AWS profile name (if None, will use default)

        Returns:
            Dictionary mapping region names to BootstrapStatus
        """
        results = {}

        for region in regions:
            results[region] = self.check_bootstrap_status(
                account_id=account_id,
                region=region,
                profile=profile
            )

        return results

    def run_bootstrap(
        self,
        account_id: Optional[str] = None,
        region: Optional[str] = None,
        profile: Optional[str] = None,
        trust_account_ids: Optional[List[str]] = None,
        force: bool = False
    ) -> bool:
        """
        Run CDK bootstrap for the specified account/region.

        Args:
            account_id: AWS account ID (if None, will be detected)
            region: AWS region (if None, will use default region)
            profile: AWS profile name (if None, will use default)
            trust_account_ids: Additional account IDs to trust
            force: Force bootstrap even if already bootstrapped

        Returns:
            True if bootstrap succeeded, False otherwise
        """
        try:
            # Get AWS context if not provided
            if not account_id or not region:
                detected_account, detected_region = self._get_aws_context(profile)
                account_id = account_id or detected_account
                region = region or detected_region

            if not account_id or not region:
                self.console.print("[red]Could not determine AWS account ID or region[/red]")
                return False

            # Check if already bootstrapped (unless force)
            if not force:
                status = self.check_bootstrap_status(account_id, region, profile)
                if status.is_bootstrapped:
                    self.console.print(f"[yellow]Account {account_id} region {region} is already bootstrapped[/yellow]")
                    return True

            # Build CDK bootstrap command
            cmd = ["cdk", "bootstrap"]

            if profile:
                cmd.extend(["--profile", profile])

            if trust_account_ids:
                cmd.extend(["--trust", ",".join(trust_account_ids)])

            # Add account/region
            cmd.append(f"{account_id}/{region}")

            self.console.print(f"[blue]Running CDK bootstrap for {account_id}/{region}...[/blue]")
            self.console.print(f"[dim]Command: {' '.join(cmd)}[/dim]")

            # Execute bootstrap command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                self.console.print(f"[green]✓ CDK bootstrap completed successfully for {account_id}/{region}[/green]")
                return True
            else:
                self.console.print(f"[red]✗ CDK bootstrap failed for {account_id}/{region}[/red]")
                self.console.print(f"[red]{result.stderr}[/red]")
                return False

        except subprocess.TimeoutExpired:
            self.console.print("[red]CDK bootstrap timed out after 5 minutes[/red]")
            return False
        except FileNotFoundError:
            self.console.print("[red]CDK CLI not found. Please install AWS CDK:[/red]")
            self.console.print("   npm install -g aws-cdk")
            return False
        except Exception as e:
            self.console.print(f"[red]Bootstrap failed: {e}[/red]")
            return False

    def display_bootstrap_status(self, status: BootstrapStatus, verbose: bool = False) -> None:
        """
        Display bootstrap status in a formatted table.

        Args:
            status: BootstrapStatus to display
            verbose: Show detailed resource information
        """
        # Create main status table
        table = Table(title=f"CDK Bootstrap Status - {status.account_id}/{status.region}")
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        table.add_row("Account ID", status.account_id)
        table.add_row("Region", status.region)
        table.add_row("Profile", status.profile or "default")

        # Bootstrap status with color coding
        if status.is_bootstrapped:
            bootstrap_display = "[green]✓ Bootstrapped[/green]"
        elif status.cdk_toolkit_stack_exists:
            bootstrap_display = "[yellow]⚠ Partial Bootstrap[/yellow]"
        else:
            bootstrap_display = "[red]✗ Not Bootstrapped[/red]"

        table.add_row("Bootstrap Status", bootstrap_display)

        # CDK Toolkit stack
        toolkit_display = "[green]✓ Exists[/green]" if status.cdk_toolkit_stack_exists else "[red]✗ Missing[/red]"
        table.add_row("CDKToolkit Stack", toolkit_display)

        if status.cdk_toolkit_version:
            table.add_row("CDK Version", status.cdk_toolkit_version)

        table.add_row("Checked At", status.checked_at.strftime("%Y-%m-%d %H:%M:%S UTC"))

        self.console.print(table)

        # Show errors if any
        if status.errors:
            self.console.print("\n[bold red]Errors:[/bold red]")
            for error in status.errors:
                self.console.print(f"  • [red]{error}[/red]")

        # Show detailed resource status if verbose
        if verbose and status.resources:
            self.console.print("\n")
            self._display_resource_details(status.resources)

        # Show guidance
        if not status.is_bootstrapped:
            self.console.print("\n[yellow]💡 To bootstrap this account/region:[/yellow]")
            if status.profile:
                self.console.print(f"   blackwell deploy bootstrap --profile {status.profile}")
            else:
                self.console.print("   blackwell deploy bootstrap")
            self.console.print("   [dim]or manually:[/dim]")
            if status.profile:
                self.console.print(f"   cdk bootstrap --profile {status.profile} {status.account_id}/{status.region}")
            else:
                self.console.print(f"   cdk bootstrap {status.account_id}/{status.region}")

    def display_multi_region_status(self, statuses: Dict[str, BootstrapStatus]) -> None:
        """
        Display bootstrap status for multiple regions in a summary table.

        Args:
            statuses: Dictionary mapping region names to BootstrapStatus
        """
        if not statuses:
            self.console.print("[yellow]No regions to display[/yellow]")
            return

        # Create summary table
        table = Table(title="CDK Bootstrap Status Summary")
        table.add_column("Region", style="cyan")
        table.add_column("Bootstrap Status", style="green")
        table.add_column("CDKToolkit Stack", style="blue")
        table.add_column("Resources", style="dim")

        for region, status in statuses.items():
            # Bootstrap status
            if status.is_bootstrapped:
                bootstrap_status = "[green]✓ Ready[/green]"
            elif status.cdk_toolkit_stack_exists:
                bootstrap_status = "[yellow]⚠ Partial[/yellow]"
            else:
                bootstrap_status = "[red]✗ Missing[/red]"

            # Toolkit stack status
            toolkit_status = "[green]✓[/green]" if status.cdk_toolkit_stack_exists else "[red]✗[/red]"

            # Resource count
            healthy_resources = len([r for r in status.resources if r.status == "healthy"])
            total_resources = len(status.resources)
            resource_info = f"{healthy_resources}/{total_resources}" if status.resources else "0/0"

            table.add_row(region, bootstrap_status, toolkit_status, resource_info)

        self.console.print(table)

        # Show guidance for missing bootstraps
        missing_regions = [region for region, status in statuses.items() if not status.is_bootstrapped]
        if missing_regions:
            self.console.print(f"\n[yellow]💡 Regions needing bootstrap: {', '.join(missing_regions)}[/yellow]")
            profile_info = list(statuses.values())[0].profile
            if profile_info:
                self.console.print(f"   blackwell deploy bootstrap --regions {','.join(missing_regions)} --profile {profile_info}")
            else:
                self.console.print(f"   blackwell deploy bootstrap --regions {','.join(missing_regions)}")

    def _get_aws_context(self, profile: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """Get current AWS account ID and region."""
        try:
            # Get account ID
            cmd = ["aws", "sts", "get-caller-identity", "--query", "Account", "--output", "text"]
            if profile:
                cmd.extend(["--profile", profile])

            result = subprocess.run(cmd, capture_output=True, text=True)
            account_id = result.stdout.strip() if result.returncode == 0 else None

            # Get region
            cmd = ["aws", "configure", "get", "region"]
            if profile:
                cmd.extend(["--profile", profile])

            result = subprocess.run(cmd, capture_output=True, text=True)
            region = result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else None

            # Fallback to environment variable or default
            if not region:
                import os
                region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

            return account_id, region

        except Exception:
            return None, None

    def _check_cdk_toolkit_stack(
        self,
        account_id: str,
        region: str,
        profile: Optional[str] = None
    ) -> Dict:
        """Check if CDKToolkit CloudFormation stack exists."""
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError

            # Create session with profile
            session = boto3.Session(profile_name=profile, region_name=region)
            cloudformation = session.client('cloudformation')

            try:
                response = cloudformation.describe_stacks(StackName="CDKToolkit")
                stack = response['Stacks'][0]

                # Extract CDK version from stack description or parameters
                version = None
                if 'Description' in stack and 'CDK' in stack['Description']:
                    # Try to extract version from description
                    description = stack['Description']
                    if 'version' in description.lower():
                        version = "detected"

                return {
                    "exists": True,
                    "status": stack['StackStatus'],
                    "version": version,
                    "creation_time": stack.get('CreationTime')
                }

            except ClientError as e:
                if e.response['Error']['Code'] == 'ValidationError':
                    return {"exists": False, "errors": []}
                else:
                    return {"exists": False, "errors": [str(e)]}

        except ImportError:
            return {"exists": False, "errors": ["boto3 not available"]}
        except Exception as e:
            return {"exists": False, "errors": [str(e)]}

    def _validate_bootstrap_resources(
        self,
        account_id: str,
        region: str,
        profile: Optional[str] = None
    ) -> List[BootstrapResource]:
        """Validate CDK bootstrap resources."""
        resources = []

        try:
            import boto3
            from botocore.exceptions import ClientError

            session = boto3.Session(profile_name=profile, region_name=region)

            # Check S3 staging bucket
            s3_resource = self._check_s3_staging_bucket(session, account_id, region)
            if s3_resource:
                resources.append(s3_resource)

            # Check ECR repository (if applicable)
            ecr_resource = self._check_ecr_repository(session)
            if ecr_resource:
                resources.append(ecr_resource)

            # Check IAM roles
            iam_resources = self._check_iam_roles(session)
            resources.extend(iam_resources)

        except Exception as e:
            # Add error resource
            resources.append(BootstrapResource(
                name="validation_error",
                resource_type="error",
                status="error",
                error=str(e)
            ))

        return resources

    def _check_s3_staging_bucket(self, session, account_id: str, region: str) -> Optional[BootstrapResource]:
        """Check CDK S3 staging bucket."""
        try:
            s3 = session.client('s3')
            bucket_name = f"cdk-{self._get_qualifier()}-assets-{account_id}-{region}"

            try:
                response = s3.head_bucket(Bucket=bucket_name)
                return BootstrapResource(
                    name=bucket_name,
                    resource_type="s3_bucket",
                    status="healthy",
                    arn=f"arn:aws:s3:::{bucket_name}"
                )
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    return BootstrapResource(
                        name=bucket_name,
                        resource_type="s3_bucket",
                        status="missing",
                        error="Bucket does not exist"
                    )
                else:
                    return BootstrapResource(
                        name=bucket_name,
                        resource_type="s3_bucket",
                        status="error",
                        error=str(e)
                    )
        except Exception as e:
            return BootstrapResource(
                name="s3_staging_bucket",
                resource_type="s3_bucket",
                status="error",
                error=str(e)
            )

    def _check_ecr_repository(self, session) -> Optional[BootstrapResource]:
        """Check CDK ECR repository."""
        try:
            ecr = session.client('ecr')
            repo_name = f"cdk-{self._get_qualifier()}-container-assets"

            try:
                response = ecr.describe_repositories(repositoryNames=[repo_name])
                repo = response['repositories'][0]
                return BootstrapResource(
                    name=repo_name,
                    resource_type="ecr_repository",
                    status="healthy",
                    arn=repo['repositoryArn'],
                    created_date=repo.get('createdAt')
                )
            except ClientError as e:
                if e.response['Error']['Code'] == 'RepositoryNotFoundException':
                    return BootstrapResource(
                        name=repo_name,
                        resource_type="ecr_repository",
                        status="missing",
                        error="Repository does not exist"
                    )
                else:
                    return BootstrapResource(
                        name=repo_name,
                        resource_type="ecr_repository",
                        status="error",
                        error=str(e)
                    )
        except Exception:
            # ECR repository is optional for some deployments
            return None

    def _check_iam_roles(self, session) -> List[BootstrapResource]:
        """Check CDK IAM roles."""
        roles = []

        try:
            from botocore.exceptions import ClientError

            iam = session.client('iam')
            qualifier = self._get_qualifier()

            # Check key IAM roles
            role_names = [
                f"cdk-{qualifier}-cfn-exec-role",
                f"cdk-{qualifier}-deploy-role",
                f"cdk-{qualifier}-file-publishing-role",
                f"cdk-{qualifier}-image-publishing-role"
            ]

            for role_name in role_names:
                try:
                    response = iam.get_role(RoleName=role_name)
                    role = response['Role']
                    roles.append(BootstrapResource(
                        name=role_name,
                        resource_type="iam_roles",
                        status="healthy",
                        arn=role['Arn'],
                        created_date=role.get('CreateDate')
                    ))
                except ClientError as e:
                    if e.response['Error']['Code'] == 'NoSuchEntity':
                        roles.append(BootstrapResource(
                            name=role_name,
                            resource_type="iam_roles",
                            status="missing",
                            error="Role does not exist"
                        ))
                    else:
                        roles.append(BootstrapResource(
                            name=role_name,
                            resource_type="iam_roles",
                            status="error",
                            error=str(e)
                        ))

        except Exception as e:
            roles.append(BootstrapResource(
                name="iam_roles_check",
                resource_type="iam_roles",
                status="error",
                error=str(e)
            ))

        return roles

    def _get_qualifier(self) -> str:
        """Get CDK bootstrap qualifier (usually 'hnb659fds')."""
        # The default CDK qualifier - could be made configurable in the future
        return "hnb659fds"

    def _display_resource_details(self, resources: List[BootstrapResource]) -> None:
        """Display detailed resource status table."""
        if not resources:
            return

        table = Table(title="Bootstrap Resource Details")
        table.add_column("Resource", style="cyan")
        table.add_column("Type", style="blue")
        table.add_column("Status", style="green")
        table.add_column("ARN/Details", style="dim")

        for resource in resources:
            # Status with color coding
            if resource.status == "healthy":
                status_display = "[green]✓ Healthy[/green]"
            elif resource.status == "missing":
                status_display = "[yellow]⚠ Missing[/yellow]"
            else:
                status_display = "[red]✗ Error[/red]"

            # Details column
            details = resource.arn or resource.error or ""
            if len(details) > 50:
                details = details[:47] + "..."

            table.add_row(
                resource.name,
                resource.resource_type.replace("_", " ").title(),
                status_display,
                details
            )

        self.console.print(table)