"""
System Doctor - Comprehensive system diagnostics for Blackwell CLI

Provides comprehensive health checks for all CLI dependencies including:
- System dependencies (CDK, AWS CLI, Node.js)
- AWS configuration and credentials
- CDK bootstrap status
- Platform integration status
- Configuration validation
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from blackwell.core.config_manager import ConfigManager
from blackwell.core.cdk_bootstrap_checker import CDKBootstrapChecker


@dataclass
class DiagnosticResult:
    """Result of a diagnostic check."""
    name: str
    status: str  # "healthy", "warning", "error", "info"
    message: str
    details: Optional[str] = None
    fix_suggestion: Optional[str] = None


class SystemDoctor:
    """
    Comprehensive system diagnostics for Blackwell CLI.

    Runs health checks across all CLI dependencies and integrations,
    providing actionable feedback for fixing issues.
    """

    def __init__(self, config_manager: Optional[ConfigManager] = None, console: Optional[Console] = None):
        """Initialize the system doctor."""
        self.config_manager = config_manager or ConfigManager()
        self.console = console or Console()
        self.bootstrap_checker = CDKBootstrapChecker(console=self.console)

    def run_full_diagnosis(self, verbose: bool = False) -> bool:
        """
        Run comprehensive system diagnostics.

        Args:
            verbose: Show detailed diagnostic information

        Returns:
            True if all critical checks pass, False otherwise
        """
        self.console.print(Panel.fit(
            "[bold blue]Blackwell CLI System Diagnostics[/bold blue]\n\n"
            "Running comprehensive health checks for CLI dependencies,\n"
            "AWS configuration, CDK bootstrap status, and platform integration.",
            border_style="blue"
        ))

        results = []
        critical_failures = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            # 1. System Dependencies
            task = progress.add_task("Checking system dependencies...", total=None)
            sys_results = self._check_system_dependencies()
            results.extend(sys_results)
            critical_failures += len([r for r in sys_results if r.status == "error"])

            # 2. AWS Configuration
            progress.update(task, description="Checking AWS configuration...")
            aws_results = self._check_aws_configuration()
            results.extend(aws_results)
            critical_failures += len([r for r in aws_results if r.status == "error"])

            # 3. CDK Bootstrap Status
            progress.update(task, description="Checking CDK bootstrap status...")
            bootstrap_results = self._check_cdk_bootstrap_status()
            results.extend(bootstrap_results)
            # Bootstrap is warning, not critical for basic CLI functionality

            # 4. Platform Integration
            progress.update(task, description="Checking platform integration...")
            platform_results = self._check_platform_integration()
            results.extend(platform_results)
            # Platform integration is also warning, not critical

            # 5. Configuration Validation
            progress.update(task, description="Validating configuration...")
            config_results = self._check_configuration_health()
            results.extend(config_results)

        # Display results
        self._display_diagnostic_results(results, verbose)

        # Summary
        self._display_diagnostic_summary(results, critical_failures)

        return critical_failures == 0

    def check_deployment_readiness(
        self,
        account_id: Optional[str] = None,
        region: Optional[str] = None,
        profile: Optional[str] = None
    ) -> bool:
        """
        Check if system is ready for deployment.

        Args:
            account_id: Target AWS account ID
            region: Target AWS region
            profile: AWS profile to use

        Returns:
            True if ready for deployment, False otherwise
        """
        self.console.print("[bold blue]Deployment Readiness Check[/bold blue]\n")

        ready = True
        issues = []

        # Check CDK installation
        if not self._check_cdk_available():
            issues.append("AWS CDK is not installed")
            ready = False

        # Check AWS credentials
        if not self._check_aws_credentials(profile):
            issues.append("AWS credentials are not configured or invalid")
            ready = False

        # Check CDK bootstrap
        bootstrap_status = self.bootstrap_checker.check_bootstrap_status(
            account_id=account_id,
            region=region,
            profile=profile
        )

        if not bootstrap_status.is_bootstrapped:
            issues.append(f"CDK is not bootstrapped in {bootstrap_status.account_id}/{bootstrap_status.region}")
            ready = False

        # Check platform path if deploying clients
        if not self.config_manager.is_platform_available():
            issues.append("Platform-infrastructure path is not configured")
            ready = False

        # Display results
        if ready:
            self.console.print("[green]✅ System is ready for deployment![/green]")
            self.console.print(f"[dim]Target: {bootstrap_status.account_id}/{bootstrap_status.region}[/dim]")
        else:
            self.console.print("[red]❌ System is not ready for deployment[/red]")
            self.console.print("\n[bold red]Issues to resolve:[/bold red]")
            for issue in issues:
                self.console.print(f"  • [red]{issue}[/red]")

            self.console.print("\n[yellow]💡 Quick fixes:[/yellow]")
            if "CDK is not installed" in issues:
                self.console.print("   npm install -g aws-cdk")
            if "AWS credentials" in str(issues):
                if profile:
                    self.console.print(f"   aws configure --profile {profile}")
                else:
                    self.console.print("   aws configure")
            if "not bootstrapped" in str(issues):
                self.console.print("   blackwell deploy bootstrap")
            if "platform-infrastructure" in str(issues):
                self.console.print("   blackwell platform path --auto-discover")

        return ready

    def _check_system_dependencies(self) -> List[DiagnosticResult]:
        """Check system-level dependencies."""
        results = []

        # Check Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        if sys.version_info >= (3, 13):
            results.append(DiagnosticResult(
                name="Python Version",
                status="healthy",
                message=f"Python {python_version} (compatible)",
                details="Blackwell CLI requires Python 3.13+"
            ))
        else:
            results.append(DiagnosticResult(
                name="Python Version",
                status="error",
                message=f"Python {python_version} (incompatible)",
                details="Blackwell CLI requires Python 3.13+",
                fix_suggestion="Upgrade Python to 3.13 or higher"
            ))

        # Check Node.js (required for CDK)
        node_result = self._check_command_available("node", "--version")
        if node_result[0]:
            results.append(DiagnosticResult(
                name="Node.js",
                status="healthy",
                message=f"Node.js {node_result[1].strip()} (available)",
                details="Required for AWS CDK"
            ))
        else:
            results.append(DiagnosticResult(
                name="Node.js",
                status="error",
                message="Node.js not found",
                details="Node.js is required for AWS CDK",
                fix_suggestion="Install Node.js from https://nodejs.org"
            ))

        # Check AWS CDK
        cdk_result = self._check_command_available("cdk", "--version")
        if cdk_result[0]:
            results.append(DiagnosticResult(
                name="AWS CDK",
                status="healthy",
                message=f"CDK {cdk_result[1].strip()} (available)",
                details="AWS Cloud Development Kit"
            ))
        else:
            results.append(DiagnosticResult(
                name="AWS CDK",
                status="error",
                message="AWS CDK not found",
                details="CDK is required for infrastructure deployment",
                fix_suggestion="Install CDK with: npm install -g aws-cdk"
            ))

        # Check AWS CLI
        aws_result = self._check_command_available("aws", "--version")
        if aws_result[0]:
            results.append(DiagnosticResult(
                name="AWS CLI",
                status="healthy",
                message=f"AWS CLI {aws_result[1].split()[0]} (available)",
                details="AWS Command Line Interface"
            ))
        else:
            results.append(DiagnosticResult(
                name="AWS CLI",
                status="error",
                message="AWS CLI not found",
                details="AWS CLI is required for deployment and configuration",
                fix_suggestion="Install AWS CLI from https://aws.amazon.com/cli/"
            ))

        # Check Git (helpful for version control)
        git_result = self._check_command_available("git", "--version")
        if git_result[0]:
            results.append(DiagnosticResult(
                name="Git",
                status="info",
                message=f"Git {git_result[1].strip()} (available)",
                details="Version control system (recommended)"
            ))
        else:
            results.append(DiagnosticResult(
                name="Git",
                status="warning",
                message="Git not found (optional)",
                details="Git is recommended for version control",
                fix_suggestion="Install Git from https://git-scm.com"
            ))

        return results

    def _check_aws_configuration(self) -> List[DiagnosticResult]:
        """Check AWS configuration and credentials."""
        results = []

        # Check default AWS credentials
        credentials_valid, creds_info = self._check_aws_credentials()
        if credentials_valid:
            results.append(DiagnosticResult(
                name="AWS Credentials",
                status="healthy",
                message="AWS credentials are configured and valid",
                details=creds_info
            ))
        else:
            results.append(DiagnosticResult(
                name="AWS Credentials",
                status="error",
                message="AWS credentials are missing or invalid",
                details=creds_info,
                fix_suggestion="Run: aws configure"
            ))

        # Check AWS region configuration
        region = self._get_aws_region()
        if region:
            results.append(DiagnosticResult(
                name="AWS Region",
                status="healthy",
                message=f"Default region: {region}",
                details="AWS region is configured"
            ))
        else:
            results.append(DiagnosticResult(
                name="AWS Region",
                status="warning",
                message="No default AWS region configured",
                details="Will use us-east-1 as fallback",
                fix_suggestion="Set region with: aws configure set region <region>"
            ))

        # Check AWS profiles
        profiles = self._get_aws_profiles()
        if profiles:
            results.append(DiagnosticResult(
                name="AWS Profiles",
                status="info",
                message=f"Available profiles: {', '.join(profiles[:3])}{'...' if len(profiles) > 3 else ''}",
                details=f"Total profiles: {len(profiles)}"
            ))
        else:
            results.append(DiagnosticResult(
                name="AWS Profiles",
                status="info",
                message="Using default profile only",
                details="Additional profiles can be configured for multi-account deployment"
            ))

        return results

    def _check_cdk_bootstrap_status(self) -> List[DiagnosticResult]:
        """Check CDK bootstrap status for current account/region."""
        results = []

        try:
            # Get current AWS context
            account_id, region = self.bootstrap_checker._get_aws_context()

            if not account_id or not region:
                results.append(DiagnosticResult(
                    name="CDK Bootstrap Status",
                    status="warning",
                    message="Cannot check bootstrap status",
                    details="AWS account ID or region could not be determined",
                    fix_suggestion="Ensure AWS credentials are properly configured"
                ))
                return results

            # Check bootstrap status
            bootstrap_status = self.bootstrap_checker.check_bootstrap_status(
                account_id=account_id,
                region=region
            )

            if bootstrap_status.is_bootstrapped:
                results.append(DiagnosticResult(
                    name="CDK Bootstrap",
                    status="healthy",
                    message=f"Account {account_id} region {region} is bootstrapped",
                    details=f"CDK version: {bootstrap_status.cdk_toolkit_version or 'detected'}"
                ))
            elif bootstrap_status.cdk_toolkit_stack_exists:
                results.append(DiagnosticResult(
                    name="CDK Bootstrap",
                    status="warning",
                    message=f"Partial bootstrap in {account_id}/{region}",
                    details="CDKToolkit stack exists but some resources may be missing",
                    fix_suggestion="Run: blackwell deploy bootstrap"
                ))
            else:
                results.append(DiagnosticResult(
                    name="CDK Bootstrap",
                    status="warning",
                    message=f"Account {account_id} region {region} is not bootstrapped",
                    details="CDK bootstrap is required for deployment",
                    fix_suggestion="Run: blackwell deploy bootstrap"
                ))

            # Check for errors
            if bootstrap_status.errors:
                for error in bootstrap_status.errors:
                    results.append(DiagnosticResult(
                        name="CDK Bootstrap Error",
                        status="warning",
                        message="Bootstrap check encountered issues",
                        details=error
                    ))

        except Exception as e:
            results.append(DiagnosticResult(
                name="CDK Bootstrap Check",
                status="warning",
                message="Bootstrap status check failed",
                details=str(e),
                fix_suggestion="Check AWS credentials and permissions"
            ))

        return results

    def _check_platform_integration(self) -> List[DiagnosticResult]:
        """Check platform-infrastructure integration status."""
        results = []

        try:
            # Check if platform path is configured
            platform_path = self.config_manager.get_platform_path()
            if platform_path:
                results.append(DiagnosticResult(
                    name="Platform Path",
                    status="healthy",
                    message=f"Platform path configured: {platform_path}",
                    details="Path to platform-infrastructure project"
                ))

                # Check if platform is available
                if self.config_manager.is_platform_available():
                    results.append(DiagnosticResult(
                        name="Platform Integration",
                        status="healthy",
                        message="Platform integration is active",
                        details="Dynamic provider matrix available"
                    ))

                    # Check provider matrix
                    try:
                        provider_matrix = self.config_manager.get_provider_matrix()
                        providers = provider_matrix.list_all_providers()

                        cms_count = len(providers.get("cms", {}))
                        ecommerce_count = len(providers.get("ecommerce", {}))
                        ssg_count = len(providers.get("ssg", {}))

                        results.append(DiagnosticResult(
                            name="Provider Matrix",
                            status="healthy",
                            message=f"Providers available: {cms_count} CMS, {ecommerce_count} E-commerce, {ssg_count} SSG",
                            details="Provider data loaded successfully"
                        ))
                    except Exception as e:
                        results.append(DiagnosticResult(
                            name="Provider Matrix",
                            status="warning",
                            message="Provider matrix load failed",
                            details=str(e)
                        ))
                else:
                    results.append(DiagnosticResult(
                        name="Platform Integration",
                        status="warning",
                        message="Platform path configured but not available",
                        details="Check platform-infrastructure installation",
                        fix_suggestion="Verify platform-infrastructure is properly installed"
                    ))
            else:
                results.append(DiagnosticResult(
                    name="Platform Path",
                    status="warning",
                    message="Platform path not configured",
                    details="Using static provider definitions",
                    fix_suggestion="Run: blackwell platform path --auto-discover"
                ))

        except Exception as e:
            results.append(DiagnosticResult(
                name="Platform Integration Check",
                status="warning",
                message="Platform integration check failed",
                details=str(e)
            ))

        return results

    def _check_configuration_health(self) -> List[DiagnosticResult]:
        """Check CLI configuration health."""
        results = []

        try:
            # Check configuration file
            config_path = self.config_manager.get_config_path()
            if config_path and config_path.exists():
                results.append(DiagnosticResult(
                    name="Configuration File",
                    status="healthy",
                    message=f"Configuration loaded from {config_path}",
                    details="CLI configuration file exists and loaded"
                ))
            else:
                results.append(DiagnosticResult(
                    name="Configuration File",
                    status="info",
                    message="Using default configuration",
                    details="No custom configuration file found (using defaults)"
                ))

            # Validate configuration
            issues = self.config_manager.validate_configuration()
            if issues:
                for issue in issues:
                    results.append(DiagnosticResult(
                        name="Configuration Issue",
                        status="warning",
                        message="Configuration validation issue",
                        details=issue,
                        fix_suggestion="Check configuration settings"
                    ))
            else:
                results.append(DiagnosticResult(
                    name="Configuration Validation",
                    status="healthy",
                    message="Configuration validation passed",
                    details="All configuration settings are valid"
                ))

        except Exception as e:
            results.append(DiagnosticResult(
                name="Configuration Check",
                status="warning",
                message="Configuration check failed",
                details=str(e)
            ))

        return results

    def _display_diagnostic_results(self, results: List[DiagnosticResult], verbose: bool = False) -> None:
        """Display diagnostic results in formatted tables."""
        # Group results by status
        status_groups = {
            "healthy": [],
            "warning": [],
            "error": [],
            "info": []
        }

        for result in results:
            status_groups[result.status].append(result)

        # Display each group
        for status, group_results in status_groups.items():
            if not group_results:
                continue

            # Status styling
            status_styles = {
                "healthy": ("green", "✓ Healthy"),
                "warning": ("yellow", "⚠ Warnings"),
                "error": ("red", "✗ Errors"),
                "info": ("blue", "ℹ Information")
            }

            color, title = status_styles[status]

            table = Table(title=title, title_style=color)
            table.add_column("Check", style="cyan", no_wrap=True)
            table.add_column("Status", style=color)

            if verbose:
                table.add_column("Details", style="dim")

            for result in group_results:
                row = [result.name, result.message]
                if verbose:
                    details = result.details or ""
                    if result.fix_suggestion:
                        details += f"\nFix: {result.fix_suggestion}"
                    row.append(details)

                table.add_row(*row)

            self.console.print(table)
            self.console.print()

    def _display_diagnostic_summary(self, results: List[DiagnosticResult], critical_failures: int) -> None:
        """Display diagnostic summary."""
        # Count results by status
        status_counts = {"healthy": 0, "warning": 0, "error": 0, "info": 0}
        for result in results:
            status_counts[result.status] += 1

        # Summary panel
        if critical_failures == 0:
            summary_color = "green"
            summary_title = "✅ System Health: Good"
            summary_message = "All critical checks passed! The CLI is ready for basic operations."
        else:
            summary_color = "red"
            summary_title = "❌ System Health: Issues Found"
            summary_message = f"{critical_failures} critical issue(s) need attention before deployment."

        summary_text = f"""[bold]{summary_title}[/bold]

{summary_message}

[dim]Results Summary:[/dim]
• {status_counts['healthy']} healthy checks
• {status_counts['warning']} warnings
• {status_counts['error']} errors
• {status_counts['info']} informational"""

        if status_counts['warning'] > 0:
            summary_text += f"\n\n[yellow]Note: {status_counts['warning']} warning(s) may affect deployment functionality.[/yellow]"

        self.console.print(Panel(
            summary_text,
            border_style=summary_color,
            padding=(1, 2)
        ))

        # Next steps
        if critical_failures > 0:
            self.console.print("\n[bold red]Next Steps:[/bold red]")
            self.console.print("1. Fix the critical errors listed above")
            self.console.print("2. Run 'blackwell doctor' again to verify fixes")
            self.console.print("3. Use 'blackwell deploy bootstrap' if CDK bootstrap is needed")
        elif status_counts['warning'] > 0:
            self.console.print("\n[bold yellow]Recommendations:[/bold yellow]")
            self.console.print("• Review warnings above to optimize your setup")
            self.console.print("• Run 'blackwell deploy bootstrap' if planning to deploy")
            self.console.print("• Use 'blackwell platform path --auto-discover' for enhanced features")

    def _check_command_available(self, command: str, version_arg: str = "--version") -> Tuple[bool, str]:
        """Check if a command is available and get version info."""
        try:
            result = subprocess.run(
                [command, version_arg],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout or result.stderr
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False, ""

    def _check_cdk_available(self) -> bool:
        """Check if CDK is available."""
        return self._check_command_available("cdk", "--version")[0]

    def _check_aws_credentials(self, profile: Optional[str] = None) -> Tuple[bool, str]:
        """Check AWS credentials validity."""
        try:
            cmd = ["aws", "sts", "get-caller-identity"]
            if profile:
                cmd.extend(["--profile", profile])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                # Parse account info
                import json
                identity = json.loads(result.stdout)
                account_id = identity.get("Account", "unknown")
                user_arn = identity.get("Arn", "unknown")
                return True, f"Account: {account_id}, Identity: {user_arn.split('/')[-1]}"
            else:
                return False, result.stderr.strip() or "Invalid credentials"

        except Exception as e:
            return False, str(e)

    def _get_aws_region(self, profile: Optional[str] = None) -> Optional[str]:
        """Get configured AWS region."""
        try:
            cmd = ["aws", "configure", "get", "region"]
            if profile:
                cmd.extend(["--profile", profile])

            result = subprocess.run(cmd, capture_output=True, text=True)
            region = result.stdout.strip() if result.returncode == 0 else None

            # Fallback to environment variable
            if not region:
                import os
                region = os.environ.get("AWS_DEFAULT_REGION")

            return region
        except Exception:
            return None

    def _get_aws_profiles(self) -> List[str]:
        """Get list of configured AWS profiles."""
        try:
            from pathlib import Path
            import configparser

            aws_config_path = Path.home() / ".aws" / "config"
            if not aws_config_path.exists():
                return []

            config = configparser.ConfigParser()
            config.read(aws_config_path)

            profiles = []
            for section in config.sections():
                if section.startswith("profile "):
                    profiles.append(section.replace("profile ", ""))

            return profiles
        except Exception:
            return []