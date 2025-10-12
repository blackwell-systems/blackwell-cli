"""
Client Manager for Blackwell CLI

Manages client configurations including:
- Client CRUD operations
- Client status tracking
- Configuration validation
- Integration with platform-infrastructure templates
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ValidationError
from rich.console import Console

# Legacy constant removed - using literal for migration compatibility
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


class ClientManifest(BaseModel):
    """Client configuration manifest - desired state."""

    # Schema reference
    schema: str = Field(
        default="https://blackwell.dev/schemas/manifest.schema.json",
        description="JSON Schema reference",
        alias="$schema"
    )
    # Schema versioning
    schema_version: str = Field(default="1.1", description="Manifest schema version")

    # Basic client information
    client_id: str = Field(..., description="Client identifier (kebab-case)")
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

    # Infrastructure settings
    aws_region: str = Field(default="us-east-1", description="AWS deployment region")

    # Metadata
    notes: str = Field(default="", description="Client notes")
    tags: Dict[str, str] = Field(default_factory=dict, description="Custom tags")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
    )

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
        client_pascal = "".join(word.capitalize() for word in self.client_id.split("-"))

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


class ClientState(BaseModel):
    """Client runtime state - observed state."""

    # Schema reference
    schema: str = Field(
        default="https://blackwell.dev/schemas/state.schema.json",
        description="JSON Schema reference",
        alias="$schema"
    )
    # Schema versioning
    schema_version: str = Field(default="1.1", description="State schema version")

    # Runtime status
    status: str = Field(default=ClientStatus.DRAFT, description="Current status")
    stack_name: Optional[str] = Field(
        default=None, description="Generated CDK stack name"
    )
    last_deployed_at: Optional[datetime] = Field(
        default=None, description="Last deployment timestamp"
    )

    # Cost tracking
    estimated_monthly_cost: Optional[float] = Field(
        default=None, description="Estimated monthly cost in USD"
    )
    actual_monthly_cost: Optional[float] = Field(
        default=None, description="Actual monthly cost in USD"
    )

    # Infrastructure state
    aws_stack_id: Optional[str] = Field(
        default=None, description="AWS CloudFormation stack ID"
    )
    drift_detected: bool = Field(
        default=False, description="Whether configuration drift was detected"
    )

    # Metadata
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last state update timestamp",
    )

    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)


class ClientHistoryEvent(BaseModel):
    """Single deployment history event."""

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Event timestamp"
    )
    action: str = Field(..., description="Action performed")
    status: str = Field(..., description="Result status")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional event details"
    )


class ClientHistory(BaseModel):
    """Client deployment history - append-only events."""

    # Schema reference
    schema: str = Field(
        default="https://blackwell.dev/schemas/history.schema.json",
        description="JSON Schema reference",
        alias="$schema"
    )
    # Schema versioning
    schema_version: str = Field(default="1.1", description="History schema version")

    # Event log
    events: List[ClientHistoryEvent] = Field(
        default_factory=list, description="Deployment history events"
    )

    def add_event(
        self, action: str, status: str, details: Optional[Dict[str, Any]] = None
    ):
        """Add a new event to history."""
        event = ClientHistoryEvent(
            action=action,
            status=status,
            details=details or {}
        )
        self.events.append(event)


class ClientIndexEntry(BaseModel):
    """Brief client information for fast lookup."""

    id: str = Field(..., description="Client identifier")
    domain: str = Field(..., description="Primary domain")
    status: str = Field(..., description="Current status")
    region: str = Field(..., description="AWS region")
    tier: str = Field(..., description="Service tier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class RegistryIndex(BaseModel):
    """Registry index for fast client discovery."""

    # Schema reference
    schema: str = Field(
        default="https://blackwell.dev/schemas/index.schema.json",
        description="JSON Schema reference",
        alias="$schema"
    )
    version: str = Field(default="2.0", description="Registry version")
    last_updated: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last registry update timestamp"
    )
    clients: List[ClientIndexEntry] = Field(
        default_factory=list, description="Client index entries"
    )

    def update_timestamp(self):
        """Update the last_updated timestamp."""
        self.last_updated = datetime.now(timezone.utc)

    def add_client_entry(self, manifest: ClientManifest, state: ClientState):
        """Add or update a client entry in the index."""
        entry = ClientIndexEntry(
            id=manifest.client_id,
            domain=manifest.domain,
            status=state.status,
            region=manifest.aws_region,
            tier=manifest.service_tier,
            created_at=manifest.created_at,
            updated_at=state.updated_at
        )

        # Remove existing entry if present
        self.clients = [c for c in self.clients if c.id != manifest.client_id]

        # Add new entry
        self.clients.append(entry)
        self.update_timestamp()

    def remove_client_entry(self, client_id: str):
        """Remove a client entry from the index."""
        self.clients = [c for c in self.clients if c.id != client_id]
        self.update_timestamp()


# Legacy model for backward compatibility during transition
class CLIClientConfig(BaseModel):
    """Legacy CLI client configuration model - DEPRECATED."""

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

        # New registry directory structure
        self.registry_dir = config_manager.config_dir / "registry"
        self.clients_dir = self.registry_dir / "clients"
        self.index_file = self.registry_dir / "index.json"

        # Legacy file for migration/fallback
        self.legacy_clients_file = config_manager.config_dir / "clients.yml"

        # Client storage - now using new models
        self._manifests: Dict[str, ClientManifest] = {}
        self._states: Dict[str, ClientState] = {}
        self._histories: Dict[str, ClientHistory] = {}
        self._index: Optional[RegistryIndex] = None

        # Ensure directory structure exists
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.clients_dir.mkdir(parents=True, exist_ok=True)

        # Load registry
        self.load_registry()

    def load_registry(self) -> None:
        """Load clients from registry directory structure."""
        try:
            # Load index file
            self._load_index()

            # Load all client data from directories
            if self.clients_dir.exists():
                for client_dir in self.clients_dir.iterdir():
                    if client_dir.is_dir():
                        client_id = client_dir.name
                        try:
                            self._load_client_files(client_id)
                        except Exception as e:
                            console.print(f"[red]Error loading client '{client_id}': {e}[/red]")
                            continue

            # Check for legacy migration
            elif self.legacy_clients_file.exists():
                console.print("[yellow]Migrating from legacy clients.yml format...[/yellow]")
                self._migrate_from_legacy()

            else:
                # Initialize empty registry
                self._index = RegistryIndex()
                self._save_index()

        except Exception as e:
            console.print(f"[red]Error loading registry: {e}[/red]")
            # Initialize empty registry on error
            self._manifests = {}
            self._states = {}
            self._histories = {}
            self._index = RegistryIndex()

    def _load_index(self) -> None:
        """Load the registry index file."""
        if self.index_file.exists():
            with open(self.index_file, "r") as f:
                index_data = json.load(f)
            self._index = RegistryIndex.model_validate(index_data)
        else:
            self._index = RegistryIndex()

    def _load_client_files(self, client_id: str) -> None:
        """Load individual client files (manifest, state, history)."""
        client_dir = self.clients_dir / client_id

        # Load manifest (required)
        manifest_file = client_dir / "manifest.json"
        if manifest_file.exists():
            with open(manifest_file, "r") as f:
                manifest_data = json.load(f)
            self._manifests[client_id] = ClientManifest.model_validate(manifest_data)
        else:
            raise FileNotFoundError(f"Missing manifest.json for client '{client_id}'")

        # Load state (required)
        state_file = client_dir / "state.json"
        if state_file.exists():
            with open(state_file, "r") as f:
                state_data = json.load(f)
            self._states[client_id] = ClientState.model_validate(state_data)
        else:
            # Create default state if missing
            self._states[client_id] = ClientState()

        # Load history (optional)
        history_file = client_dir / "history.json"
        if history_file.exists():
            with open(history_file, "r") as f:
                history_data = json.load(f)
            self._histories[client_id] = ClientHistory.model_validate(history_data)
        else:
            # Create empty history if missing
            self._histories[client_id] = ClientHistory()

    def _migrate_from_legacy(self) -> None:
        """Migrate from legacy YAML format to new registry structure."""
        try:
            with open(self.legacy_clients_file, "r") as f:
                legacy_data = yaml.safe_load(f) or {}

            for name, client_data in legacy_data.get("clients", {}).items():
                try:
                    # Convert legacy client to new format
                    legacy_client = CLIClientConfig.model_validate({**client_data, "name": name})

                    # Create manifest from legacy data
                    manifest = ClientManifest(
                        client_id=legacy_client.name,
                        company_name=legacy_client.company_name,
                        domain=legacy_client.domain,
                        contact_email=legacy_client.contact_email,
                        service_tier=legacy_client.service_tier,
                        management_model=legacy_client.management_model,
                        cms_provider=legacy_client.cms_provider,
                        ecommerce_provider=legacy_client.ecommerce_provider,
                        ssg_engine=legacy_client.ssg_engine,
                        integration_mode=legacy_client.integration_mode,
                        cms_settings=legacy_client.cms_settings,
                        ecommerce_settings=legacy_client.ecommerce_settings,
                        aws_region=legacy_client.aws_region,
                        notes=legacy_client.notes,
                        tags=legacy_client.tags,
                        created_at=legacy_client.created_at
                    )

                    # Create state from legacy data
                    state = ClientState(
                        status=legacy_client.status,
                        stack_name=legacy_client.stack_name,
                        last_deployed_at=legacy_client.last_deployed_at,
                        estimated_monthly_cost=legacy_client.estimated_monthly_cost,
                        actual_monthly_cost=legacy_client.actual_monthly_cost,
                        updated_at=legacy_client.updated_at
                    )

                    # Create history from legacy deployment_history
                    history = ClientHistory()
                    for record in legacy_client.deployment_history:
                        # Convert legacy record format
                        timestamp_str = record.get("timestamp", datetime.now(timezone.utc).isoformat())
                        if isinstance(timestamp_str, str):
                            try:
                                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                            except:
                                timestamp = datetime.now(timezone.utc)
                        else:
                            timestamp = datetime.now(timezone.utc)

                        event = ClientHistoryEvent(
                            timestamp=timestamp,
                            action=record.get("action", "unknown"),
                            status=record.get("status", "unknown"),
                            details=record.get("details", {})
                        )
                        history.events.append(event)

                    # Store migrated data
                    self._manifests[name] = manifest
                    self._states[name] = state
                    self._histories[name] = history

                    # Save to new format
                    self._save_client_files(name)

                except Exception as e:
                    console.print(f"[red]Error migrating client '{name}': {e}[/red]")
                    continue

            # Create and save index
            self._index = RegistryIndex()
            for client_id in self._manifests:
                self._index.add_client_entry(self._manifests[client_id], self._states[client_id])
            self._save_index()

            console.print(f"[green]Successfully migrated {len(self._manifests)} clients to new registry format[/green]")

        except Exception as e:
            console.print(f"[red]Error during migration: {e}[/red]")
            raise

    def _save_index(self) -> None:
        """Save the registry index file."""
        try:
            if self._index:
                with open(self.index_file, "w") as f:
                    json.dump(
                        self._index.model_dump(mode="json", by_alias=True),
                        f,
                        indent=2,
                        default=str
                    )
        except Exception as e:
            console.print(f"[red]Error saving index: {e}[/red]")
            raise

    def _save_client_files(self, client_id: str) -> None:
        """Save individual client files (manifest, state, history)."""
        try:
            client_dir = self.clients_dir / client_id
            client_dir.mkdir(parents=True, exist_ok=True)

            # Save manifest
            if client_id in self._manifests:
                manifest_file = client_dir / "manifest.json"
                with open(manifest_file, "w") as f:
                    json.dump(
                        self._manifests[client_id].model_dump(mode="json", by_alias=True),
                        f,
                        indent=2,
                        default=str
                    )

            # Save state
            if client_id in self._states:
                state_file = client_dir / "state.json"
                with open(state_file, "w") as f:
                    json.dump(
                        self._states[client_id].model_dump(mode="json", by_alias=True),
                        f,
                        indent=2,
                        default=str
                    )

            # Save history
            if client_id in self._histories:
                history_file = client_dir / "history.json"
                with open(history_file, "w") as f:
                    json.dump(
                        self._histories[client_id].model_dump(mode="json", by_alias=True),
                        f,
                        indent=2,
                        default=str
                    )

        except Exception as e:
            console.print(f"[red]Error saving client files for '{client_id}': {e}[/red]")
            raise

    def save_registry(self) -> None:
        """Save the entire registry (index and all clients)."""
        try:
            # Save index first
            self._save_index()

            # Save all client files
            for client_id in self._manifests:
                self._save_client_files(client_id)

        except Exception as e:
            console.print(f"[red]Error saving registry: {e}[/red]")
            raise

    def save_client(self, client_id: str) -> None:
        """Save a specific client and update index."""
        try:
            # Save client files
            self._save_client_files(client_id)

            # Update index if client exists in manifests and states
            if client_id in self._manifests and client_id in self._states and self._index:
                self._index.add_client_entry(self._manifests[client_id], self._states[client_id])
                self._save_index()

        except Exception as e:
            console.print(f"[red]Error saving client '{client_id}': {e}[/red]")
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
    ) -> ClientManifest:
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
            Created client manifest

        Raises:
            ValueError: If client already exists or validation fails
        """
        if name in self._manifests:
            raise ValueError(f"Client '{name}' already exists")

        # Use defaults from configuration
        defaults = self.config_manager.get_defaults()
        ssg_engine = ssg_engine or defaults["ssg_engine"]
        integration_mode = integration_mode or defaults["integration_mode"]

        try:
            # Create manifest
            manifest = ClientManifest(
                client_id=name,
                company_name=company_name,
                domain=domain,
                contact_email=contact_email,
                cms_provider=cms_provider,
                ecommerce_provider=ecommerce_provider,
                ssg_engine=ssg_engine,
                integration_mode=integration_mode,
                **{k: v for k, v in kwargs.items() if k in ClientManifest.model_fields}
            )

            # Create initial state
            state = ClientState(
                stack_name=manifest.generate_stack_name()
            )

            # Create empty history
            history = ClientHistory()

            # Add creation event to history
            history.add_event(
                action="create",
                status="draft",
                details={"created_by": "cli", "initial_setup": True}
            )

            # Store in memory
            self._manifests[name] = manifest
            self._states[name] = state
            self._histories[name] = history

            # Save to disk
            self.save_client(name)

            return manifest

        except ValidationError as e:
            raise ValueError(f"Invalid client configuration: {e}")

    def get_client(self, name: str) -> Optional[ClientManifest]:
        """Get client manifest by name."""
        return self._manifests.get(name)

    def get_client_state(self, name: str) -> Optional[ClientState]:
        """Get client state by name."""
        return self._states.get(name)

    def get_client_history(self, name: str) -> Optional[ClientHistory]:
        """Get client history by name."""
        return self._histories.get(name)

    def get_client_full(self, name: str) -> Optional[tuple[ClientManifest, ClientState, ClientHistory]]:
        """Get complete client data (manifest, state, history)."""
        if name in self._manifests and name in self._states and name in self._histories:
            return (self._manifests[name], self._states[name], self._histories[name])
        return None

    def update_client_manifest(self, name: str, **updates) -> ClientManifest:
        """
        Update client manifest (configuration).

        Args:
            name: Client name
            **updates: Manifest fields to update

        Returns:
            Updated client manifest

        Raises:
            ValueError: If client doesn't exist or validation fails
        """
        if name not in self._manifests:
            raise ValueError(f"Client '{name}' not found")

        manifest = self._manifests[name]
        manifest_data = manifest.model_dump(by_alias=False)
        manifest_data.update(updates)

        try:
            updated_manifest = ClientManifest.model_validate(manifest_data)
            self._manifests[name] = updated_manifest

            # Update state if stack name needs regeneration
            if any(key in updates for key in ["cms_provider", "ecommerce_provider", "ssg_engine"]):
                if name in self._states:
                    state = self._states[name]
                    state.stack_name = updated_manifest.generate_stack_name()
                    state.update_timestamp()

            # Add update event to history
            if name in self._histories:
                self._histories[name].add_event(
                    action="update",
                    status="draft",
                    details={"updated_fields": list(updates.keys()), "update_type": "manifest"}
                )

            self.save_client(name)
            return updated_manifest

        except ValidationError as e:
            raise ValueError(f"Invalid manifest update: {e}")

    def update_client_state(self, name: str, **updates) -> ClientState:
        """
        Update client state (runtime information).

        Args:
            name: Client name
            **updates: State fields to update

        Returns:
            Updated client state

        Raises:
            ValueError: If client doesn't exist or validation fails
        """
        if name not in self._states:
            raise ValueError(f"Client '{name}' not found")

        state = self._states[name]
        state_data = state.model_dump(by_alias=False)
        state_data.update(updates)

        try:
            updated_state = ClientState.model_validate(state_data)
            updated_state.update_timestamp()
            self._states[name] = updated_state

            # Add update event to history
            if name in self._histories:
                self._histories[name].add_event(
                    action="update",
                    status=updated_state.status,
                    details={"updated_fields": list(updates.keys()), "update_type": "state"}
                )

            self.save_client(name)
            return updated_state

        except ValidationError as e:
            raise ValueError(f"Invalid state update: {e}")

    def update_client(self, name: str, **updates) -> tuple[Optional[ClientManifest], Optional[ClientState]]:
        """
        Update client configuration - automatically determines which parts to update.

        Args:
            name: Client name
            **updates: Fields to update

        Returns:
            Tuple of (updated_manifest, updated_state) - either may be None if not updated

        Raises:
            ValueError: If client doesn't exist or validation fails
        """
        if name not in self._manifests:
            raise ValueError(f"Client '{name}' not found")

        # Separate updates by model type
        manifest_fields = set(ClientManifest.model_fields.keys())
        state_fields = set(ClientState.model_fields.keys())

        manifest_updates = {k: v for k, v in updates.items() if k in manifest_fields}
        state_updates = {k: v for k, v in updates.items() if k in state_fields}

        updated_manifest = None
        updated_state = None

        # Update manifest if needed
        if manifest_updates:
            updated_manifest = self.update_client_manifest(name, **manifest_updates)

        # Update state if needed
        if state_updates:
            updated_state = self.update_client_state(name, **state_updates)

        return updated_manifest, updated_state

    def delete_client(self, name: str) -> bool:
        """
        Delete client configuration.

        Args:
            name: Client name

        Returns:
            True if deleted, False if not found
        """
        if name not in self._manifests:
            return False

        # Add deletion event to history before removing
        if name in self._histories:
            self._histories[name].add_event(
                action="delete",
                status="deleted",
                details={"deleted_by": "cli", "deletion_time": datetime.now(timezone.utc).isoformat()}
            )

        # Remove from index
        if self._index:
            self._index.remove_client_entry(name)
            self._save_index()

        # Remove client files
        import shutil
        client_dir = self.clients_dir / name
        if client_dir.exists():
            shutil.rmtree(client_dir)

        # Remove from memory
        self._manifests.pop(name, None)
        self._states.pop(name, None)
        self._histories.pop(name, None)

        return True

    def list_clients(
        self, status_filter: Optional[str] = None, provider_filter: Optional[str] = None
    ) -> List[tuple[ClientManifest, ClientState]]:
        """
        List clients with optional filtering.

        Args:
            status_filter: Filter by status
            provider_filter: Filter by CMS or e-commerce provider

        Returns:
            List of (manifest, state) tuples
        """
        # Build list of (manifest, state) pairs
        clients = []
        for client_id in self._manifests:
            if client_id in self._states:
                manifest = self._manifests[client_id]
                state = self._states[client_id]
                clients.append((manifest, state))

        # Apply filters
        if status_filter:
            clients = [(m, s) for m, s in clients if s.status == status_filter]

        if provider_filter:
            clients = [
                (m, s)
                for m, s in clients
                if m.cms_provider == provider_filter
                or m.ecommerce_provider == provider_filter
            ]

        return sorted(clients, key=lambda x: x[0].created_at)

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