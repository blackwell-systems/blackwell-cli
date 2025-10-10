"""
Configuration Manager for Blackwell CLI

Handles all configuration operations including:
- CLI settings and preferences
- AWS configuration
- Platform-infrastructure integration
- User defaults and templates
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, ValidationError
from rich.console import Console
import sys

from blackwell import CLI_CONFIG_DIR, CLI_CONFIG_FILE

console = Console()


class AWSConfig(BaseModel):
    """AWS configuration settings."""

    profile: str = Field(default="default", description="AWS profile name")
    region: str = Field(default="us-east-1", description="Default AWS region")
    account_id: Optional[str] = Field(
        default=None, description="AWS account ID (auto-detected if not provided)"
    )


class DefaultsConfig(BaseModel):
    """Default settings for new clients."""

    cms_provider: str = Field(default="decap", description="Default CMS provider")
    ecommerce_provider: str = Field(
        default="snipcart", description="Default e-commerce provider"
    )
    ssg_engine: str = Field(default="astro", description="Default SSG engine")
    integration_mode: str = Field(
        default="event_driven", description="Default integration mode"
    )
    service_tier: str = Field(default="tier1", description="Default service tier")
    management_model: str = Field(
        default="self_managed", description="Default management model"
    )


class PlatformConfig(BaseModel):
    """Platform-infrastructure integration settings."""

    path: Optional[Path] = Field(
        default=None, description="Path to platform-infrastructure project"
    )
    auto_discover: bool = Field(
        default=True, description="Auto-discover platform-infrastructure path"
    )
    required_version: str = Field(
        default="1.0.0", description="Required platform-infrastructure version"
    )


class CLIConfig(BaseModel):
    """Main CLI configuration model."""

    version: str = Field(default="0.1.0", description="Configuration version")
    aws: AWSConfig = Field(default_factory=AWSConfig)
    defaults: DefaultsConfig = Field(default_factory=DefaultsConfig)
    platform_infrastructure: PlatformConfig = Field(default_factory=PlatformConfig)

    # CLI behavior settings
    verbose: bool = Field(default=False, description="Enable verbose output")
    auto_confirm: bool = Field(
        default=False, description="Auto-confirm operations (dangerous)"
    )
    check_updates: bool = Field(
        default=True, description="Check for CLI updates automatically"
    )
    telemetry: bool = Field(
        default=True, description="Send anonymous usage telemetry"
    )

    # Custom templates and overrides
    custom_templates_path: Optional[Path] = Field(
        default=None, description="Path to custom templates directory"
    )
    cost_alert_threshold: float = Field(
        default=200.0, description="Monthly cost alert threshold in USD"
    )

    # Advanced settings
    parallel_deployments: int = Field(
        default=3, description="Maximum parallel deployments", ge=1, le=10
    )
    deployment_timeout: int = Field(
        default=1800, description="Deployment timeout in seconds", ge=300, le=3600
    )


class ConfigManager:
    """
    Manages CLI configuration including loading, saving, and validation.

    Handles:
    - CLI configuration file (~/.blackwell/config.yml)
    - Environment variable overrides
    - Platform-infrastructure integration
    - Default settings management
    """

    def __init__(self, config_path: Optional[Path] = None, verbose: bool = False):
        """
        Initialize configuration manager.

        Args:
            config_path: Optional path to config file (defaults to ~/.blackwell/config.yml)
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.config_dir = Path(CLI_CONFIG_DIR).expanduser()
        self.config_path = config_path or self.config_dir / CLI_CONFIG_FILE

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self._config: Optional[CLIConfig] = None
        self.load_config()

    @property
    def config(self) -> CLIConfig:
        """Get the current configuration."""
        if self._config is None:
            self.load_config()
        return self._config

    def load_config(self) -> CLIConfig:
        """Load configuration from file or create default."""
        try:
            if self.config_path.exists():
                if self.verbose:
                    console.print(f"[dim]Loading config from {self.config_path}[/dim]")

                with open(self.config_path, "r") as f:
                    config_data = yaml.safe_load(f) or {}

                # Apply environment variable overrides
                self._apply_env_overrides(config_data)

                # Validate and load configuration
                self._config = CLIConfig.model_validate(config_data)
            else:
                if self.verbose:
                    console.print("[dim]Creating default configuration[/dim]")

                # Create default configuration
                self._config = CLIConfig()
                self.save_config()

        except (ValidationError, yaml.YAMLError, FileNotFoundError) as e:
            console.print(f"[red]Error loading configuration: {e}[/red]")
            console.print("[yellow]Creating fresh configuration...[/yellow]")
            self._config = CLIConfig()
            self.save_config()

        # Auto-discover platform-infrastructure if enabled
        if self._config.platform_infrastructure.auto_discover:
            self._auto_discover_platform()

        return self._config

    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            config_dict = self._config.model_dump(mode="json", exclude_none=True)

            with open(self.config_path, "w") as f:
                yaml.safe_dump(
                    config_dict,
                    f,
                    default_flow_style=False,
                    sort_keys=True,
                    indent=2,
                )

            if self.verbose:
                console.print(f"[green]Configuration saved to {self.config_path}[/green]")

        except Exception as e:
            console.print(f"[red]Error saving configuration: {e}[/red]")
            raise

    def _apply_env_overrides(self, config_data: Dict[str, Any]) -> None:
        """Apply environment variable overrides to configuration."""
        env_mappings = {
            "BLACKWELL_AWS_PROFILE": ("aws", "profile"),
            "BLACKWELL_AWS_REGION": ("aws", "region"),
            "BLACKWELL_PLATFORM_PATH": ("platform_infrastructure", "path"),
            "BLACKWELL_VERBOSE": ("verbose",),
            "AWS_PROFILE": ("aws", "profile"),  # Standard AWS env var
            "AWS_DEFAULT_REGION": ("aws", "region"),  # Standard AWS env var
        }

        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                self._set_nested_config(config_data, config_path, env_value)

    def _set_nested_config(
        self, config_data: Dict[str, Any], path: tuple, value: str
    ) -> None:
        """Set nested configuration value."""
        current = config_data
        for key in path[:-1]:
            current = current.setdefault(key, {})

        # Convert value to appropriate type
        if path[-1] in ["verbose", "auto_confirm", "check_updates", "telemetry"]:
            value = value.lower() in ("true", "1", "yes", "on")
        elif path[-1] in ["parallel_deployments", "deployment_timeout"]:
            value = int(value)
        elif path[-1] == "cost_alert_threshold":
            value = float(value)

        current[path[-1]] = value

    def _auto_discover_platform(self) -> None:
        """Auto-discover platform-infrastructure project location."""
        if self._config.platform_infrastructure.path:
            return  # Already configured

        # Search paths for platform-infrastructure
        search_paths = [
            Path.cwd() / "platform-infrastructure",
            Path.cwd().parent / "platform-infrastructure",
            Path.home() / "code" / "business" / "platform-infrastructure",
            Path("/home/blackwd/code/business/platform-infrastructure"),
        ]

        for path in search_paths:
            if self._is_valid_platform_path(path):
                self._config.platform_infrastructure.path = path
                if self.verbose:
                    console.print(
                        f"[green]Auto-discovered platform-infrastructure at {path}[/green]"
                    )
                self.save_config()
                return

        if self.verbose:
            console.print(
                "[yellow]Platform-infrastructure not auto-discovered. "
                "Set manually with: blackwell config set platform_infrastructure.path /path/to/platform-infrastructure[/yellow]"
            )

    def _is_valid_platform_path(self, path: Path) -> bool:
        """Check if path contains a valid platform-infrastructure project."""
        if not path.exists() or not path.is_dir():
            return False

        # Check for key files/directories
        required_items = [
            "pyproject.toml",
            "models/service_config.py",
            "models/client_templates.py",
            "stacks/",
            "shared/",
        ]

        return all((path / item).exists() for item in required_items)

    # Configuration getters and setters
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key."""
        try:
            keys = key.split(".")
            value = self.config.model_dump()
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot notation key."""
        keys = key.split(".")
        config_dict = self._config.model_dump()

        # Navigate to the parent dictionary
        current = config_dict
        for k in keys[:-1]:
            current = current.setdefault(k, {})

        # Set the value
        current[keys[-1]] = value

        # Validate and update configuration
        try:
            self._config = CLIConfig.model_validate(config_dict)
            self.save_config()
        except ValidationError as e:
            console.print(f"[red]Invalid configuration value: {e}[/red]")
            raise

    def get_platform_path(self) -> Optional[Path]:
        """Get platform-infrastructure project path."""
        return self.config.platform_infrastructure.path

    def is_platform_available(self) -> bool:
        """Check if platform-infrastructure is available and valid."""
        path = self.get_platform_path()
        return path is not None and self._is_valid_platform_path(path)

    def get_aws_config(self) -> Dict[str, str]:
        """Get AWS configuration as dictionary."""
        return {
            "profile": self.config.aws.profile,
            "region": self.config.aws.region,
            "account_id": self.config.aws.account_id or "auto-detect",
        }

    def get_defaults(self) -> Dict[str, str]:
        """Get default settings as dictionary."""
        return self.config.defaults.model_dump()

    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.config.verbose or os.getenv("BLACKWELL_DEBUG", "").lower() in (
            "true",
            "1",
            "yes",
        )

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        console.print("[yellow]Resetting configuration to defaults...[/yellow]")
        self._config = CLIConfig()
        self.save_config()
        console.print("[green]Configuration reset successfully[/green]")

    def validate_configuration(self) -> List[str]:
        """Validate current configuration and return list of issues."""
        issues = []

        # Check platform-infrastructure integration
        if not self.is_platform_available():
            issues.append("Platform-infrastructure project not found or invalid")

        # Check AWS configuration
        try:
            import boto3

            session = boto3.Session(profile_name=self.config.aws.profile)
            session.client("sts").get_caller_identity()
        except Exception as e:
            issues.append(f"AWS configuration invalid: {e}")

        # Check CDK availability
        import shutil

        if not shutil.which("cdk"):
            issues.append("AWS CDK CLI not found in PATH")

        return issues

    def show_config_summary(self) -> None:
        """Display configuration summary."""
        from rich.table import Table
        from rich.panel import Panel

        # Create configuration table
        table = Table(title="Blackwell CLI Configuration", show_header=True)
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        table.add_column("Source", style="dim")

        # Add configuration rows
        config_dict = self.config.model_dump()
        self._add_config_rows(table, config_dict, "")

        # Show validation status
        issues = self.validate_configuration()
        if issues:
            status = "[red]⚠ Issues found[/red]"
            for issue in issues:
                status += f"\n[red]• {issue}[/red]"
        else:
            status = "[green]✓ Configuration valid[/green]"

        # Display results
        console.print(table)
        console.print(Panel(status, title="Validation Status"))

    def _add_config_rows(self, table, config_dict: dict, prefix: str) -> None:
        """Recursively add configuration rows to table."""
        for key, value in config_dict.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                # Add section header
                table.add_row(f"[bold]{full_key}[/bold]", "", "")
                self._add_config_rows(table, value, full_key)
            else:
                # Determine source
                env_var = f"BLACKWELL_{full_key.upper().replace('.', '_')}"
                source = "environment" if os.getenv(env_var) else "config file"

                # Add value row
                table.add_row(f"  {key}", str(value), source)