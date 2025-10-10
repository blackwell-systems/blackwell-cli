"""
Client Manager for Blackwell CLI

Manages client configurations including:
- Client CRUD operations
- Client status tracking
- Configuration validation
- Integration with platform-infrastructure templates
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ValidationError
from rich.console import Console

from blackwell import CLI_CLIENTS_FILE
from blackwell.core.config_manager import ConfigManager

console = Console()


class ClientStatus(str):
    """Client status enumeration."""

    DRAFT = "draft"
    READY = "ready"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    ERROR = "error"
    UPDATING = "updating"
    DESTROYING = "destroying"


class CLIClientConfig(BaseModel):
    """CLI client configuration model."""

    # Basic client information
    name: str = Field(..., description="Client identifier (kebab-case)")
    company_name: str = Field(..., description="Company display name")
    domain: str = Field(..., description="Primary domain")
    contact_email: str = Field(..., description="Primary contact email")

    # Service configuration
    service_tier: str = Field(default="tier1", description="Service tier")
    management_model: str = Field(
        default="self_managed", description="Management model"
    )
    cms_provider: str = Field(..., description="CMS provider")
    ecommerce_provider: Optional[str] = Field(
        default=None, description="E-commerce provider (optional)"
    )
    ssg_engine: str = Field(..., description="SSG engine")
    integration_mode: str = Field(
        default="event_driven", description="Integration mode"
    )

    # Provider-specific settings
    cms_settings: Dict[str, Any] = Field(
        default_factory=dict, description="CMS provider settings"
    )
    ecommerce_settings: Dict[str, Any] = Field(
        default_factory=dict, description="E-commerce provider settings"
    )

    # Deployment information
    stack_name: Optional[str] = Field(
        default=None, description="Generated CDK stack name"
    )
    status: str = Field(default=ClientStatus.DRAFT, description="Current status")
    aws_region: str = Field(default="us-east-1", description="AWS deployment region")

    # Cost and metadata
    estimated_monthly_cost: Optional[float] = Field(
        default=None, description="Estimated monthly cost in USD"
    )
    actual_monthly_cost: Optional[float] = Field(
        default=None, description="Actual monthly cost in USD"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp",
    )
    last_deployed_at: Optional[datetime] = Field(
        default=None, description="Last deployment timestamp"
    )

    # Deployment history and notes
    deployment_history: List[Dict[str, Any]] = Field(
        default_factory=list, description="Deployment history"
    )
    notes: str = Field(default="", description="Client notes")
    tags: Dict[str, str] = Field(default_factory=dict, description="Custom tags")

    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)

    def add_deployment_record(
        self, action: str, status: str, details: Optional[Dict[str, Any]] = None
    ):
        """Add a deployment record to history."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "status": status,
            "details": details or {},
        }
        self.deployment_history.append(record)
        self.update_timestamp()

    def get_service_type(self) -> str:
        """Determine service type based on providers."""
        if self.cms_provider and self.ecommerce_provider:
            return "composed_stack"
        elif self.cms_provider:
            return "cms_tier"
        elif self.ecommerce_provider:
            return "ecommerce_tier"
        else:
            return "static_site"

    def generate_stack_name(self) -> str:
        """Generate CDK stack name using platform-infrastructure naming convention."""
        # Convert client name to PascalCase
        client_pascal = "".join(word.capitalize() for word in self.name.split("-"))

        # Determine environment (default to Prod)
        env = "Prod"

        # Generate stack type
        service_type = self.get_service_type()

        if service_type == "composed_stack":
            cms_part = self.cms_provider.capitalize()
            ecommerce_part = self.ecommerce_provider.capitalize()
            if ecommerce_part.endswith("_basic"):
                ecommerce_part = ecommerce_part.replace("_basic", "Basic")
            stack_type = f"{cms_part}{ecommerce_part}ComposedStack"
        elif service_type == "cms_tier":
            stack_type = f"{self.cms_provider.capitalize()}CmsTier"
        elif service_type == "ecommerce_tier":
            stack_type = f"{self.ecommerce_provider.capitalize()}EcommerceTier"
        else:
            stack_type = f"{self.ssg_engine.capitalize()}StaticStack"

        return f"{client_pascal}-{env}-{stack_type}"


class ClientManager:
    """
    Manages client configurations and operations.

    Handles:
    - Loading and saving client configurations
    - Client CRUD operations
    - Status management
    - Integration with platform-infrastructure
    """

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize client manager.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.clients_file = config_manager.config_dir / CLI_CLIENTS_FILE
        self._clients: Dict[str, CLIClientConfig] = {}
        self.load_clients()

    def load_clients(self) -> Dict[str, CLIClientConfig]:
        """Load clients from file."""
        try:
            if self.clients_file.exists():
                with open(self.clients_file, "r") as f:
                    clients_data = yaml.safe_load(f) or {}

                # Load and validate each client
                self._clients = {}
                for name, data in clients_data.get("clients", {}).items():
                    try:
                        # Ensure name matches the key
                        data["name"] = name
                        self._clients[name] = CLIClientConfig.model_validate(data)
                    except ValidationError as e:
                        console.print(f"[red]Error loading client '{name}': {e}[/red]")
                        continue

            else:
                # Create empty clients file
                self._clients = {}
                self.save_clients()

        except Exception as e:
            console.print(f"[red]Error loading clients: {e}[/red]")
            self._clients = {}

        return self._clients

    def save_clients(self) -> None:
        """Save clients to file."""
        try:
            clients_data = {
                "version": "1.0",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "clients": {
                    name: client.model_dump(mode="json", exclude_none=True)
                    for name, client in self._clients.items()
                },
            }

            with open(self.clients_file, "w") as f:
                yaml.safe_dump(
                    clients_data,
                    f,
                    default_flow_style=False,
                    sort_keys=True,
                    indent=2,
                )

        except Exception as e:
            console.print(f"[red]Error saving clients: {e}[/red]")
            raise

    def create_client(
        self,
        name: str,
        company_name: str,
        domain: str,
        contact_email: str,
        cms_provider: str,
        ecommerce_provider: Optional[str] = None,
        ssg_engine: Optional[str] = None,
        integration_mode: Optional[str] = None,
        **kwargs,
    ) -> CLIClientConfig:
        """
        Create a new client configuration.

        Args:
            name: Client identifier (kebab-case)
            company_name: Company display name
            domain: Primary domain
            contact_email: Contact email
            cms_provider: CMS provider
            ecommerce_provider: E-commerce provider (optional)
            ssg_engine: SSG engine (optional, uses default if not provided)
            integration_mode: Integration mode (optional, uses default if not provided)
            **kwargs: Additional client settings

        Returns:
            Created client configuration

        Raises:
            ValueError: If client already exists or validation fails
        """
        if name in self._clients:
            raise ValueError(f"Client '{name}' already exists")

        # Use defaults from configuration
        defaults = self.config_manager.get_defaults()
        ssg_engine = ssg_engine or defaults["ssg_engine"]
        integration_mode = integration_mode or defaults["integration_mode"]

        # Create client configuration
        client_data = {
            "name": name,
            "company_name": company_name,
            "domain": domain,
            "contact_email": contact_email,
            "cms_provider": cms_provider,
            "ecommerce_provider": ecommerce_provider,
            "ssg_engine": ssg_engine,
            "integration_mode": integration_mode,
            **kwargs,
        }

        try:
            client = CLIClientConfig.model_validate(client_data)
            client.stack_name = client.generate_stack_name()
            self._clients[name] = client
            self.save_clients()
            return client
        except ValidationError as e:
            raise ValueError(f"Invalid client configuration: {e}")

    def get_client(self, name: str) -> Optional[CLIClientConfig]:
        """Get client by name."""
        return self._clients.get(name)

    def update_client(self, name: str, **updates) -> CLIClientConfig:
        """
        Update client configuration.

        Args:
            name: Client name
            **updates: Fields to update

        Returns:
            Updated client configuration

        Raises:
            ValueError: If client doesn't exist or validation fails
        """
        if name not in self._clients:
            raise ValueError(f"Client '{name}' not found")

        client = self._clients[name]
        client_data = client.model_dump()
        client_data.update(updates)

        try:
            updated_client = CLIClientConfig.model_validate(client_data)
            updated_client.update_timestamp()

            # Regenerate stack name if providers changed
            if any(
                key in updates
                for key in ["cms_provider", "ecommerce_provider", "ssg_engine"]
            ):
                updated_client.stack_name = updated_client.generate_stack_name()

            self._clients[name] = updated_client
            self.save_clients()
            return updated_client
        except ValidationError as e:
            raise ValueError(f"Invalid client update: {e}")

    def delete_client(self, name: str) -> bool:
        """
        Delete client configuration.

        Args:
            name: Client name

        Returns:
            True if deleted, False if not found
        """
        if name in self._clients:
            del self._clients[name]
            self.save_clients()
            return True
        return False

    def list_clients(
        self, status_filter: Optional[str] = None, provider_filter: Optional[str] = None
    ) -> List[CLIClientConfig]:
        """
        List clients with optional filtering.

        Args:
            status_filter: Filter by status
            provider_filter: Filter by CMS or e-commerce provider

        Returns:
            List of client configurations
        """
        clients = list(self._clients.values())

        if status_filter:
            clients = [c for c in clients if c.status == status_filter]

        if provider_filter:
            clients = [
                c
                for c in clients
                if c.cms_provider == provider_filter
                or c.ecommerce_provider == provider_filter
            ]

        return sorted(clients, key=lambda c: c.created_at)

    def update_client_status(
        self,
        name: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        update_deployment_time: bool = False,
    ) -> None:
        """
        Update client status.

        Args:
            name: Client name
            status: New status
            details: Additional status details
            update_deployment_time: Whether to update last deployment time
        """
        if name not in self._clients:
            raise ValueError(f"Client '{name}' not found")

        client = self._clients[name]
        old_status = client.status
        client.status = status
        client.update_timestamp()

        if update_deployment_time and status == ClientStatus.DEPLOYED:
            client.last_deployed_at = datetime.now(timezone.utc)

        # Add deployment record
        client.add_deployment_record(
            action="status_change",
            status=status,
            details={"old_status": old_status, "new_status": status, **(details or {})},
        )

        self.save_clients()

    def get_clients_by_status(self, status: str) -> List[CLIClientConfig]:
        """Get all clients with specific status."""
        return [client for client in self._clients.values() if client.status == status]

    def get_client_summary(self) -> Dict[str, Any]:
        """Get summary statistics of all clients."""
        clients = list(self._clients.values())
        total_clients = len(clients)

        if total_clients == 0:
            return {"total": 0}

        # Status breakdown
        status_counts = {}
        for client in clients:
            status_counts[client.status] = status_counts.get(client.status, 0) + 1

        # Provider usage
        cms_providers = {}
        ecommerce_providers = {}
        for client in clients:
            cms_providers[client.cms_provider] = (
                cms_providers.get(client.cms_provider, 0) + 1
            )
            if client.ecommerce_provider:
                ecommerce_providers[client.ecommerce_provider] = (
                    ecommerce_providers.get(client.ecommerce_provider, 0) + 1
                )

        # Cost analysis
        deployed_clients = [c for c in clients if c.status == ClientStatus.DEPLOYED]
        total_estimated_cost = sum(
            c.estimated_monthly_cost or 0 for c in deployed_clients
        )
        total_actual_cost = sum(c.actual_monthly_cost or 0 for c in deployed_clients)

        return {
            "total": total_clients,
            "deployed": len(deployed_clients),
            "status_breakdown": status_counts,
            "cms_providers": cms_providers,
            "ecommerce_providers": ecommerce_providers,
            "total_estimated_cost": total_estimated_cost,
            "total_actual_cost": total_actual_cost,
        }

    def validate_client(self, name: str) -> List[str]:
        """
        Validate client configuration.

        Args:
            name: Client name

        Returns:
            List of validation issues
        """
        client = self.get_client(name)
        if not client:
            return [f"Client '{name}' not found"]

        issues = []

        # Check required fields
        if not client.company_name.strip():
            issues.append("Company name is required")

        if not client.domain.strip():
            issues.append("Domain is required")

        if "@" not in client.contact_email:
            issues.append("Valid contact email is required")

        # Check provider compatibility
        from blackwell.core.provider_matrix import ProviderMatrix

        matrix = ProviderMatrix()
        if not matrix.is_provider_valid("cms", client.cms_provider):
            issues.append(f"Invalid CMS provider: {client.cms_provider}")

        if client.ecommerce_provider and not matrix.is_provider_valid(
            "ecommerce", client.ecommerce_provider
        ):
            issues.append(
                f"Invalid e-commerce provider: {client.ecommerce_provider}"
            )

        if not matrix.is_provider_valid("ssg", client.ssg_engine):
            issues.append(f"Invalid SSG engine: {client.ssg_engine}")

        # Check integration mode compatibility
        if (
            client.integration_mode == "direct"
            and client.get_service_type() == "composed_stack"
        ):
            issues.append(
                "Direct integration mode not supported for composed stacks"
            )

        return issues

    def export_client_config(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Export client configuration for platform-infrastructure integration.

        Args:
            name: Client name

        Returns:
            Configuration dictionary compatible with platform-infrastructure
        """
        client = self.get_client(name)
        if not client:
            return None

        # Convert to platform-infrastructure format
        config = {
            "client_id": client.name,
            "company_name": client.company_name,
            "domain": client.domain,
            "contact_email": client.contact_email,
            "service_tier": client.service_tier,
            "management_model": client.management_model,
            "service_integration": {
                "service_type": client.get_service_type(),
                "ssg_engine": client.ssg_engine,
                "integration_mode": client.integration_mode,
            },
        }

        # Add CMS configuration if present
        if client.cms_provider:
            config["service_integration"]["cms_config"] = {
                "provider": client.cms_provider,
                "admin_users": [client.contact_email],
                "settings": client.cms_settings,
            }

        # Add e-commerce configuration if present
        if client.ecommerce_provider:
            config["service_integration"]["ecommerce_config"] = {
                "provider": client.ecommerce_provider,
                "settings": client.ecommerce_settings,
            }

        return config