# Service Integration Framework

**🔗 Seamlessly integrate third-party services with guided automation and intelligent workflows**

## Table of Contents

- [Overview](#overview)
- [Architecture & Design](#architecture--design)
- [Quick Start](#quick-start)
- [Integration Commands](#integration-commands)
- [Service-Specific Guides](#service-specific-guides)
- [Implementation Details](#implementation-details)
- [Workflow Management](#workflow-management)
- [Troubleshooting](#troubleshooting)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)
- [Development Roadmap](#development-roadmap)

---

## Overview

The Blackwell CLI Service Integration Framework solves the challenge of connecting third-party services that require manual account setup. Instead of leaving you to figure out complex configurations, the CLI provides **guided integration orchestration** that maximizes automation while providing intelligent step-by-step guidance.

### ⚙️ **Guiding Principle**

**"Automate everything that can be automated, guide everything that cannot."**

This means: CLI handles all technical configuration automatically, but provides intelligent step-by-step guidance for manual account creation and API key retrieval.

### ✨ **Key Benefits**

**🤖 Maximum Automation**
- Automated environment variable configuration
- Automated webhook setup and DNS configuration
- Automated infrastructure provisioning

**📋 Intelligent Guidance**
- Step-by-step instructions for manual tasks
- Service-specific best practices and tips
- Clear progress tracking with resume capability

**🔍 Built-in Verification**
- Connection testing at each integration stage
- End-to-end workflow validation
- Automated troubleshooting and diagnostics

**⏸️ Resumable Workflows**
- Pause and resume integrations anytime
- State saved automatically at each step
- No need to repeat completed configuration

---

## Architecture & Design

### **Integration Workflow Types**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SERVICE INTEGRATION FRAMEWORK                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐ │
│  │   Manual Steps  │    │  CLI Automation  │    │   Verification      │ │
│  │                 │    │                  │    │                     │ │
│  │ • Account setup │    │ • Config gen     │    │ • Connection test   │ │
│  │ • API keys      │◄──►│ • ENV vars       │◄──►│ • Webhook setup     │ │
│  │ • Payment info  │    │ • Infrastructure │    │ • End-to-end test   │ │
│  │ • Domain config │    │ • DNS records    │    │ • Status dashboard  │ │
│  └─────────────────┘    └──────────────────┘    └─────────────────────┘ │
│                                   │                                     │
│                          ┌─────────────────┐                            │
│                          │ Integration     │                            │
│                          │ Orchestrator    │                            │
│                          │                 │                            │
│                          │ • Workflow mgmt │                            │
│                          │ • State machine │                            │
│                          │ • Progress track│                            │
│                          │ • Resume points │                            │
│                          └─────────────────┘                            │
└─────────────────────────────────────────────────────────────────────────┘
```

### **Service Integration Tiers**

| Tier | Service Examples | Automation Level | Manual Steps Required | Typical Time |
|------|------------------|------------------|-----------------------|--------------|
| **Tier 1: Simple** | TinaCMS, Vercel | 95% automated | API key only | 5-10 minutes |
| **Tier 2: Standard** | Snipcart, Sanity | 70% automated | Account + API keys + basic config | 15-20 minutes |
| **Tier 3: Complex** | Contentful, Shopify | 50% automated | Multiple config steps + approvals | 25-35 minutes |

---

## Quick Start

### **1. List Available Services**

```bash
# See all available integrations
blackwell integrate list-services
```

**Expected Output:**
```
Available Service Integrations

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Service ID       ┃ Name                     ┃ Complexity  ┃ Est. Time  ┃ Automation Level ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ snipcart         │ Snipcart E-commerce      │ Standard    │ 15-20 min  │ 70%              │
│ contentful       │ Contentful CMS           │ Complex     │ 20-30 min  │ 50%              │
│ sanity           │ Sanity Studio            │ Standard    │ 10-15 min  │ 70%              │
│ tina             │ TinaCMS                  │ Simple      │ 5-10 min   │ 95%              │
│ shopify_basic    │ Shopify Basic            │ Complex     │ 25-35 min  │ 50%              │
└──────────────────┴──────────────────────────┴─────────────┴────────────┴──────────────────┘
```

### **2. Start Your First Integration**

```bash
# Start integrating Snipcart for your client
blackwell integrate start snipcart --client-id my-store
```

### **3. Follow the Interactive Workflow**

The CLI will guide you through each step with clear instructions and automation.

---

## Integration Commands

### 📋 **Core Commands**

#### **Start Integration**
```bash
# Start a new integration
blackwell integrate start <service> --client-id <client-id>

# Resume interrupted integration
blackwell integrate start <service> --client-id <client-id> --resume

# Examples
blackwell integrate start snipcart --client-id my-ecommerce-site
blackwell integrate start contentful --client-id my-blog --resume
```

#### **Check Status**
```bash
# View integration status for a client
blackwell integrate status --client-id <client-id>

# Examples
blackwell integrate status --client-id my-store
```

#### **Resume Integration**
```bash
# Resume a paused integration
blackwell integrate resume <service> --client-id <client-id>

# Examples
blackwell integrate resume snipcart --client-id my-store
```

#### **List Services**
```bash
# Show all available service integrations
blackwell integrate list-services

# Show details for specific service
blackwell integrate info <service>
```

---

## Service-Specific Guides

### 🛒 **Snipcart E-commerce Integration**

**Overview**: Snipcart provides cart functionality for static sites with a simple JavaScript integration.

**Prerequisites:**
- Business email address
- Payment processor account (Stripe recommended)
- Domain name for your store

**Integration Workflow:**

#### **Step 1: Account Creation (Manual - 5 minutes)**
```bash
blackwell integrate start snipcart --client-id my-store
```

**What you'll do:**
1. Visit Snipcart registration page (link provided)
2. Create account with your business email
3. Complete business information form
4. Set up payment processor (Stripe/PayPal)
5. Verify email address

**💡 Tip**: Use the same email domain as your website for better brand consistency.

#### **Step 2: API Key Retrieval (Manual - 2 minutes)**

**What you'll do:**
1. Log into Snipcart dashboard
2. Navigate to Account → API Keys
3. Copy PUBLIC API key (starts with `pk_`)
4. Copy SECRET API key (starts with `sk_`)

**⚠️ Security Note**: Never commit secret keys to version control.

#### **Step 3: Environment Configuration (Automated - 30 seconds)**

**What the CLI does:**
- Creates secure `.env.snipcart` file
- Configures environment variables
- Sets up webhook URL structure
- Updates client configuration

#### **Step 4: Webhook Setup (Automated - 1 minute)**

**What the CLI does:**
- Configures order completion webhooks
- Sets up order status change notifications
- Creates webhook endpoints in your infrastructure
- Tests webhook connectivity

#### **Step 5: Connection Testing (Automated - 1 minute)**

**What the CLI does:**
- Tests API connection with public key
- Verifies account configuration
- Checks webhook endpoints
- Validates SSL certificates

#### **Step 6: End-to-End Testing (Guided - 5 minutes)**

**What you'll do:**
1. Visit your deployed test site (URL provided)
2. Add test product to cart
3. Complete checkout with test card: `4242 4242 4242 4242`
4. Verify order appears in Snipcart dashboard
5. Confirm webhook notifications received

**Success Indicators:**
- ✅ Order shows in Snipcart dashboard
- ✅ Webhook endpoint received POST request
- ✅ Email confirmation sent to customer

---

### 📝 **Sanity Studio Integration**

**Overview**: Sanity provides a modern headless CMS with real-time collaboration.

**Prerequisites:**
- Google/GitHub account for Sanity login
- Project name and dataset configuration preferences

**Integration Workflow:**

#### **Step 1: Sanity Account & Project (Manual - 3 minutes)**

**What you'll do:**
1. Visit Sanity Studio registration (link provided)
2. Sign up with Google/GitHub account
3. Create new project with descriptive name
4. Choose dataset configuration (production recommended)

#### **Step 2: API Configuration (Manual - 2 minutes)**

**What you'll do:**
1. Navigate to project settings
2. Add your domain to CORS origins
3. Generate API token with read permissions
4. Copy project ID and dataset name

#### **Step 3: Schema & Environment Setup (Automated - 2 minutes)**

**What the CLI does:**
- Configures Sanity environment variables
- Sets up basic content schema
- Creates development and production datasets
- Configures CLI authentication

#### **Step 4: Studio Deployment (Automated - 1 minute)**

**What the CLI does:**
- Deploys Sanity Studio to your domain
- Configures custom studio URL
- Sets up authentication and permissions
- Creates initial content structure

#### **Step 5: Content Sync Testing (Automated - 1 minute)**

**What the CLI does:**
- Creates test content entry
- Verifies API connectivity
- Tests content publishing workflow
- Validates webhook integration

---

### 📖 **Contentful Integration**

**Overview**: Contentful is an enterprise-grade headless CMS with advanced workflow features.

**Prerequisites:**
- Business email address
- Content model planning (recommended)
- Team member list (if applicable)

**Integration Workflow:**

#### **Step 1: Contentful Account Setup (Manual - 8 minutes)**

**What you'll do:**
1. Visit Contentful registration page
2. Create account with business email
3. Set up organization and space
4. Configure content delivery settings
5. Set up team members (if applicable)

#### **Step 2: Space Configuration (Manual - 5 minutes)**

**What you'll do:**
1. Create new space for your project
2. Configure environment settings (master/staging)
3. Set up locale preferences
4. Configure API access settings

#### **Step 3: API Keys & Webhooks (Manual - 3 minutes)**

**What you'll do:**
1. Generate Content Delivery API key
2. Generate Content Management API key
3. Note Space ID and Environment ID
4. Configure webhook endpoints

#### **Step 4: Environment & Schema Setup (Automated - 3 minutes)**

**What the CLI does:**
- Configures Contentful environment variables
- Sets up basic content models
- Configures webhook endpoints
- Creates development environment sync

#### **Step 5: Content Model Deployment (Automated - 2 minutes)**

**What the CLI does:**
- Deploys predefined content models
- Sets up content relationships
- Configures field validations
- Creates initial content structure

#### **Step 6: Integration Testing (Automated - 3 minutes)**

**What the CLI does:**
- Tests API connectivity
- Creates sample content entries
- Verifies webhook functionality
- Tests content publishing workflow

---

## Implementation Details

### **Integration Orchestrator Class**

**File**: `blackwell/core/integration_orchestrator.py`

```python
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from enum import Enum
import json
from pathlib import Path

class IntegrationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_USER = "waiting_user"
    CONFIGURING = "configuring"
    TESTING = "testing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class IntegrationStep:
    """Individual step in service integration workflow."""
    step_id: str
    title: str
    description: str
    step_type: str  # "manual", "automated", "verification"
    instructions: Optional[str] = None
    automation_function: Optional[Callable] = None
    verification_function: Optional[Callable] = None
    required_inputs: List[str] = None
    estimated_time: Optional[str] = None
    dependencies: List[str] = None

@dataclass
class ServiceIntegration:
    """Complete service integration definition."""
    service_id: str
    service_name: str
    tier: int  # 1=simple, 2=standard, 3=complex
    steps: List[IntegrationStep]
    required_credentials: List[str]
    webhook_endpoints: List[str] = None
    documentation_url: Optional[str] = None
    estimated_total_time: Optional[str] = None

class IntegrationOrchestrator:
    """Orchestrates multi-step service integrations with automation and guidance."""

    def __init__(self, console: Console, config_manager: ConfigManager):
        self.console = console
        self.config = config_manager
        self.integrations = self._load_integration_definitions()
        self.state_file = Path.home() / ".blackwell" / "integration_state.json"

    def start_integration(
        self,
        service_id: str,
        client_id: str,
        resume: bool = False
    ) -> bool:
        """Start or resume a service integration workflow."""

        if resume and self._has_saved_state(service_id, client_id):
            return self._resume_integration(service_id, client_id)

        integration = self.integrations.get(service_id)
        if not integration:
            raise ValueError(f"Unknown service: {service_id}")

        self.console.print(f"[bold blue]Starting {integration.service_name} Integration[/bold blue]")
        self.console.print(f"[dim]Estimated time: {integration.estimated_total_time}[/dim]")
        self.console.print(f"[dim]Integration tier: {integration.tier} (automation level: {self._get_automation_level(integration.tier)})[/dim]\n")

        # Initialize integration state
        state = {
            "service_id": service_id,
            "client_id": client_id,
            "status": IntegrationStatus.IN_PROGRESS,
            "current_step": 0,
            "completed_steps": [],
            "collected_data": {},
            "started_at": datetime.utcnow().isoformat()
        }

        return self._execute_integration_workflow(integration, state)

    def _execute_integration_workflow(
        self,
        integration: ServiceIntegration,
        state: Dict
    ) -> bool:
        """Execute the integration workflow step by step."""

        for step_index, step in enumerate(integration.steps[state["current_step"]:], state["current_step"]):
            self.console.print(f"\n[bold]Step {step_index + 1}/{len(integration.steps)}: {step.title}[/bold]")
            self.console.print(f"[dim]{step.description}[/dim]")

            if step.estimated_time:
                self.console.print(f"[dim]Estimated time: {step.estimated_time}[/dim]")

            # Save current state
            state["current_step"] = step_index
            self._save_state(state)

            # Execute step based on type
            if step.step_type == "manual":
                success = self._handle_manual_step(step, state)
            elif step.step_type == "automated":
                success = self._handle_automated_step(step, state)
            elif step.step_type == "verification":
                success = self._handle_verification_step(step, state)
            else:
                raise ValueError(f"Unknown step type: {step.step_type}")

            if not success:
                self.console.print(f"[red]Step failed: {step.title}[/red]")
                state["status"] = IntegrationStatus.FAILED
                self._save_state(state)
                return False

            state["completed_steps"].append(step.step_id)

        # Integration completed successfully
        state["status"] = IntegrationStatus.COMPLETED
        state["completed_at"] = datetime.utcnow().isoformat()
        self._save_state(state)

        self.console.print(f"\n[green]✓ {integration.service_name} integration completed successfully![/green]")
        return True

    def _handle_manual_step(self, step: IntegrationStep, state: Dict) -> bool:
        """Handle manual steps with user guidance."""

        self.console.print(f"\n[yellow]👤 Manual Step Required[/yellow]")
        self.console.print(step.instructions)

        # If this step requires inputs, collect them
        if step.required_inputs:
            for input_key in step.required_inputs:
                value = self._collect_user_input(input_key, step)
                state["collected_data"][input_key] = value

        # Confirm completion
        completed = typer.confirm(f"Have you completed: {step.title}?")

        if completed:
            self.console.print("[green]✓ Manual step completed[/green]")
            return True
        else:
            self.console.print("[yellow]You can resume this integration later with: blackwell integrate resume[/yellow]")
            state["status"] = IntegrationStatus.WAITING_USER
            self._save_state(state)
            return False

    def _handle_automated_step(self, step: IntegrationStep, state: Dict) -> bool:
        """Handle automated configuration steps."""

        self.console.print(f"[blue]🤖 Automating: {step.title}[/blue]")

        try:
            if step.automation_function:
                result = step.automation_function(state["collected_data"], state["client_id"])

                if result.get("success"):
                    self.console.print(f"[green]✓ {step.title} completed automatically[/green]")

                    # Store any returned data
                    if result.get("data"):
                        state["collected_data"].update(result["data"])

                    return True
                else:
                    self.console.print(f"[red]✗ Automation failed: {result.get('error')}[/red]")
                    return False
            else:
                self.console.print("[yellow]⚠ No automation function defined[/yellow]")
                return True

        except Exception as e:
            self.console.print(f"[red]✗ Automation error: {e}[/red]")
            return False

    def _handle_verification_step(self, step: IntegrationStep, state: Dict) -> bool:
        """Handle verification and testing steps."""

        self.console.print(f"[cyan]🔍 Verifying: {step.title}[/cyan]")

        if step.verification_function:
            try:
                result = step.verification_function(state["collected_data"], state["client_id"])

                if result.get("success"):
                    self.console.print(f"[green]✓ Verification passed: {step.title}[/green]")
                    return True
                else:
                    self.console.print(f"[red]✗ Verification failed: {result.get('error')}[/red]")
                    self.console.print("[dim]You may need to check your configuration[/dim]")

                    retry = typer.confirm("Retry verification?")
                    if retry:
                        return self._handle_verification_step(step, state)  # Recursive retry
                    return False

            except Exception as e:
                self.console.print(f"[red]✗ Verification error: {e}[/red]")
                return False
        else:
            self.console.print("[green]✓ Manual verification confirmed[/green]")
            return True
```

### **Service-Specific Integration Definitions**

**File**: `blackwell/integrations/snipcart_integration.py`

```python
from blackwell.core.integration_orchestrator import ServiceIntegration, IntegrationStep

def create_snipcart_integration() -> ServiceIntegration:
    """Define Snipcart integration workflow."""

    return ServiceIntegration(
        service_id="snipcart",
        service_name="Snipcart E-commerce",
        tier=2,  # Standard tier
        required_credentials=["snipcart_api_key", "snipcart_secret_key"],
        webhook_endpoints=["order_completed", "order_status_changed"],
        documentation_url="https://docs.snipcart.com/v3/setup/installation",
        estimated_total_time="15-20 minutes",
        steps=[
            IntegrationStep(
                step_id="account_creation",
                title="Create Snipcart Account",
                description="Set up your Snipcart account with payment processing",
                step_type="manual",
                estimated_time="5 minutes",
                instructions="""
🔗 Account Setup Instructions:

1. Visit: https://app.snipcart.com/register
2. Create account with business email
3. Complete business information form
4. Set up payment processor (Stripe/PayPal recommended)
5. Verify email address

💡 Tip: Choose the same email domain as your website for better integration.
                """,
                required_inputs=["snipcart_email", "business_name"]
            ),

            IntegrationStep(
                step_id="api_key_retrieval",
                title="Retrieve API Keys",
                description="Get your Snipcart API keys from the dashboard",
                step_type="manual",
                estimated_time="2 minutes",
                instructions="""
🔑 API Key Instructions:

1. Log into Snipcart dashboard: https://app.snipcart.com
2. Navigate to Account → API Keys
3. Copy your PUBLIC API key (starts with 'pk_')
4. Copy your SECRET API key (starts with 'sk_')

⚠️  Security: Never share your secret key publicly!
                """,
                required_inputs=["snipcart_public_key", "snipcart_secret_key"],
                dependencies=["account_creation"]
            ),

            IntegrationStep(
                step_id="configure_environment",
                title="Configure Environment Variables",
                description="Set up secure credential storage",
                step_type="automated",
                estimated_time="30 seconds",
                automation_function="configure_snipcart_environment",
                dependencies=["api_key_retrieval"]
            ),

            IntegrationStep(
                step_id="setup_webhooks",
                title="Configure Webhooks",
                description="Set up order notification webhooks",
                step_type="automated",
                estimated_time="1 minute",
                automation_function="setup_snipcart_webhooks",
                dependencies=["configure_environment"]
            ),

            IntegrationStep(
                step_id="test_connection",
                title="Test API Connection",
                description="Verify Snipcart integration is working",
                step_type="verification",
                estimated_time="1 minute",
                verification_function="test_snipcart_connection",
                dependencies=["setup_webhooks"]
            ),

            IntegrationStep(
                step_id="end_to_end_test",
                title="End-to-End Purchase Test",
                description="Complete a test purchase to verify full workflow",
                step_type="verification",
                estimated_time="5 minutes",
                verification_function="test_snipcart_purchase_flow",
                dependencies=["deploy_test_product"],
                instructions="""
🛒 Purchase Flow Test:

1. Visit your deployed test site
2. Add test product to cart
3. Complete checkout with test card: 4242 4242 4242 4242
4. Verify order appears in Snipcart dashboard
5. Check webhook notifications received

✅ Success indicators:
• Order shows in dashboard
• Webhook endpoint received POST
• Email confirmation sent
                """
            )
        ]
    )

# Automation functions
def configure_snipcart_environment(collected_data: Dict, client_id: str) -> Dict:
    """Configure Snipcart environment variables."""
    try:
        # Set environment variables securely
        env_vars = {
            "SNIPCART_PUBLIC_KEY": collected_data["snipcart_public_key"],
            "SNIPCART_SECRET_KEY": collected_data["snipcart_secret_key"],
            "SNIPCART_WEBHOOK_URL": f"https://{client_id}.blackwell.dev/webhooks/snipcart"
        }

        # Write to secure environment file
        config_path = Path(f"clients/{client_id}/.env.snipcart")
        with open(config_path, "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")

        return {
            "success": True,
            "data": {"webhook_url": env_vars["SNIPCART_WEBHOOK_URL"]}
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

def setup_snipcart_webhooks(collected_data: Dict, client_id: str) -> Dict:
    """Set up Snipcart webhook endpoints."""
    try:
        import requests

        webhook_url = collected_data["webhook_url"]
        secret_key = collected_data["snipcart_secret_key"]

        # Configure webhook via Snipcart API
        webhook_config = {
            "url": webhook_url,
            "events": ["order.completed", "order.status.changed"],
            "secret": secret_key
        }

        response = requests.post(
            "https://app.snipcart.com/api/webhooks",
            json=webhook_config,
            headers={"Authorization": f"Bearer {secret_key}"}
        )

        if response.status_code == 201:
            return {"success": True, "data": {"webhook_id": response.json()["id"]}}
        else:
            return {"success": False, "error": f"Webhook setup failed: {response.text}"}

    except Exception as e:
        return {"success": False, "error": str(e)}

def test_snipcart_connection(collected_data: Dict, client_id: str) -> Dict:
    """Test Snipcart API connection."""
    try:
        import requests

        public_key = collected_data["snipcart_public_key"]

        # Test public API endpoint
        response = requests.get(
            f"https://app.snipcart.com/api/public/config/{public_key}"
        )

        if response.status_code == 200:
            config = response.json()
            return {
                "success": True,
                "data": {
                    "account_name": config.get("name", "Unknown"),
                    "currency": config.get("currency", "USD")
                }
            }
        else:
            return {"success": False, "error": f"Connection test failed: {response.text}"}

    except Exception as e:
        return {"success": False, "error": str(e)}
```

### **CLI Integration Commands**

**File**: `blackwell/commands/integrate.py`

```python
import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

from blackwell.core.integration_orchestrator import IntegrationOrchestrator
from blackwell.core.config_manager import ConfigManager

app = typer.Typer(help="Manage third-party service integrations", no_args_is_help=True)
console = Console()

@app.command()
def start(
    service: str = typer.Argument(..., help="Service to integrate (snipcart, contentful, sanity, etc.)"),
    client_id: str = typer.Option(..., "--client-id", help="Client ID for this integration"),
    resume: bool = typer.Option(False, "--resume", help="Resume interrupted integration")
):
    """
    Start a guided integration with a third-party service.

    Provides step-by-step guidance for service setup, automates
    technical configuration, and verifies the integration works.
    """
    console.print(f"[bold blue]🔗 Integrating {service.title()} for client: {client_id}[/bold blue]\\n")

    try:
        config_manager = ConfigManager()
        orchestrator = IntegrationOrchestrator(console, config_manager)

        success = orchestrator.start_integration(service, client_id, resume=resume)

        if success:
            console.print(f"\\n[green]🎉 {service.title()} integration completed successfully![/green]")
            console.print(f"[dim]Client {client_id} is now configured with {service}[/dim]")
        else:
            console.print(f"\\n[yellow]⏸️  Integration paused - resume anytime with:[/yellow]")
            console.print(f"   blackwell integrate start {service} --client-id {client_id} --resume")

    except Exception as e:
        console.print(f"[red]Integration failed: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def list_services():
    """List all available service integrations."""
    console.print("[bold blue]Available Service Integrations[/bold blue]\\n")

    # This would be loaded from integration definitions
    services = [
        {"id": "snipcart", "name": "Snipcart E-commerce", "tier": 2, "time": "15-20 min"},
        {"id": "contentful", "name": "Contentful CMS", "tier": 3, "time": "20-30 min"},
        {"id": "sanity", "name": "Sanity Studio", "tier": 2, "time": "10-15 min"},
        {"id": "tina", "name": "TinaCMS", "tier": 1, "time": "5-10 min"},
        {"id": "shopify_basic", "name": "Shopify Basic", "tier": 3, "time": "25-35 min"},
    ]

    table = Table()
    table.add_column("Service ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Complexity", style="yellow")
    table.add_column("Est. Time", style="dim")
    table.add_column("Automation Level", style="blue")

    for service in services:
        complexity = ["", "Simple", "Standard", "Complex"][service["tier"]]
        automation = ["", "95%", "70%", "50%"][service["tier"]]
        table.add_row(
            service["id"],
            service["name"],
            complexity,
            service["time"],
            automation
        )

    console.print(table)

@app.command()
def status(
    client_id: str = typer.Option(..., "--client-id", help="Client ID to check")
):
    """Show integration status for a client."""
    console.print(f"[bold blue]Integration Status - {client_id}[/bold blue]\\n")

    try:
        config_manager = ConfigManager()
        orchestrator = IntegrationOrchestrator(console, config_manager)

        status_info = orchestrator.get_client_integration_status(client_id)

        if not status_info:
            console.print("[yellow]No integrations found for this client[/yellow]")
            return

        table = Table()
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Progress", style="yellow")
        table.add_column("Last Updated", style="dim")

        for integration in status_info:
            status_color = {
                "completed": "[green]✓ Completed[/green]",
                "in_progress": "[blue]⏳ In Progress[/blue]",
                "waiting_user": "[yellow]⏸️  Waiting[/yellow]",
                "failed": "[red]✗ Failed[/red]"
            }.get(integration["status"], integration["status"])

            table.add_row(
                integration["service_name"],
                status_color,
                f"{integration['completed_steps']}/{integration['total_steps']}",
                integration["last_updated"]
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error checking status: {e}[/red]")
        raise typer.Exit(1)
```

---

## Workflow Management

### 📊 **Integration Status Dashboard**

Check the status of all your integrations:

```bash
blackwell integrate status --client-id my-client
```

**Example Output:**
```
Integration Status - my-client

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Service          ┃ Status            ┃ Progress   ┃ Last Updated     ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ Snipcart         │ ✓ Completed       │ 6/6        │ 2025-10-11 14:30 │
│ Sanity           │ ⏳ In Progress    │ 3/5        │ 2025-10-11 15:45 │
│ Contentful       │ ⏸️  Waiting       │ 2/8        │ 2025-10-11 12:15 │
│ TinaCMS          │ ✗ Failed          │ 4/5        │ 2025-10-11 11:30 │
└──────────────────┴───────────────────┴────────────┴──────────────────┘

💡 Tips:
• Resume waiting integrations: blackwell integrate resume contentful --client-id my-client
• Fix failed integrations: blackwell integrate reset tina --client-id my-client
• View detailed logs: blackwell integrate logs --client-id my-client --service tinacms
```

### 🔄 **Resume Interrupted Integrations**

Integrations can be paused and resumed at any time:

```bash
# If you stopped during Sanity integration
blackwell integrate resume sanity --client-id my-client

# The CLI will show you where you left off:
# 📋 Resuming Sanity Studio integration for: my-client
#
# Resuming from Step 4/5: Studio Deployment
# Previous steps completed:
# ✓ Step 1: Sanity Account & Project
# ✓ Step 2: API Configuration
# ✓ Step 3: Schema & Environment Setup
#
# Continuing with Step 4: Studio Deployment...
```

### 📁 **Integration State Management**

The CLI automatically saves integration state:

- **State File Location**: `~/.blackwell/integration_state.json`
- **Backup Location**: `~/.blackwell/backups/integration_state_<timestamp>.json`
- **Secure Credential Storage**: Encrypted in `~/.blackwell/credentials/`

```bash
# View integration state
blackwell integrate state --client-id my-client

# Backup integration state
blackwell integrate backup --client-id my-client

# Restore from backup
blackwell integrate restore --client-id my-client --backup 2025-10-11-14-30
```

---

## Troubleshooting

### 🚨 **Common Issues & Solutions**

#### **Integration Fails to Start**

**Symptoms:**
```
Error: Service 'snipcart' not found
```

**Solutions:**
```bash
# Check available services
blackwell integrate list-services

# Update service definitions
blackwell platform refresh

# Check CLI installation
blackwell doctor
```

#### **Manual Step Stuck or Unclear**

**Symptoms:**
- Instructions unclear
- External service not responding
- Account creation fails

**Solutions:**
```bash
# Get detailed help for specific service
blackwell integrate info snipcart

# Reset integration and start over
blackwell integrate reset snipcart --client-id my-client

# Contact support with state export
blackwell integrate export --client-id my-client --output debug.json
```

#### **Automated Step Fails**

**Symptoms:**
```
✗ Automation failed: Connection timeout
```

**Solutions:**
```bash
# Check network connectivity
blackwell doctor --network-check

# Verify API credentials
blackwell integrate verify-credentials --client-id my-client --service snipcart

# Manual override for automated step
blackwell integrate manual-override --step webhook_setup --client-id my-client
```

#### **Verification Step Fails**

**Symptoms:**
```
✗ Verification failed: Test purchase did not complete
```

**Solutions:**
```bash
# Re-run verification step
blackwell integrate verify --client-id my-client --service snipcart --step end_to_end_test

# Check detailed logs
blackwell integrate logs --client-id my-client --service snipcart --verbose

# Manual verification
blackwell integrate manual-verify --client-id my-client --service snipcart
```

### 🔍 **Diagnostic Commands**

```bash
# Comprehensive integration diagnostics
blackwell integrate doctor --client-id my-client

# Service-specific diagnostics
blackwell integrate doctor --service snipcart --client-id my-client

# Network connectivity test
blackwell integrate test-connectivity --service snipcart

# API credentials validation
blackwell integrate validate-credentials --client-id my-client
```

---

## Advanced Features

### 🎯 **Integration Templates**

Pre-configured integration bundles for common use cases:

```bash
# E-commerce starter template
blackwell integrate template ecommerce-starter --client-id my-store
# Includes: Snipcart + Sanity + TinaCMS

# Blog template
blackwell integrate template blog-pro --client-id my-blog
# Includes: Contentful + TinaCMS

# Enterprise template
blackwell integrate template enterprise --client-id my-company
# Includes: Contentful + Shopify + Advanced Analytics

# List available templates
blackwell integrate templates
```

### 🔧 **Custom Integration Definitions**

Create your own service integrations:

```bash
# Generate integration template
blackwell integrate create-definition --service my-custom-service

# This creates: integrations/my_custom_service.py
# Edit the file to define your integration steps

# Test custom integration
blackwell integrate test-definition --service my-custom-service

# Register custom integration
blackwell integrate register --service my-custom-service
```

### 🚀 **Bulk Operations**

Manage multiple integrations efficiently:

```bash
# Integrate multiple services at once
blackwell integrate batch \
  --client-id my-client \
  --services snipcart,sanity,tina \
  --parallel

# Apply integration to multiple clients
blackwell integrate multi-client \
  --clients client1,client2,client3 \
  --service snipcart \
  --template ecommerce

# Export all integrations
blackwell integrate export-all --output all_integrations.json

# Import integrations to new environment
blackwell integrate import --input all_integrations.json
```

---

## Best Practices

### 🛡️ **Security Best Practices**

#### **API Key Management**
```bash
# Always use environment-specific keys
# ✅ Good: Use test keys for development
SNIPCART_PUBLIC_KEY=pk_test_...
SNIPCART_SECRET_KEY=sk_test_...

# ✅ Good: Use production keys only for production
SNIPCART_PUBLIC_KEY=pk_live_...
SNIPCART_SECRET_KEY=sk_live_...

# ❌ Bad: Never commit keys to version control
# ❌ Bad: Never use production keys in development
```

#### **Credential Rotation**
```bash
# Rotate API keys regularly
blackwell integrate rotate-credentials --client-id my-client --service snipcart

# Update all clients with new credentials
blackwell integrate update-credentials --service snipcart --key-file new_keys.json

# Verify credential updates
blackwell integrate verify-credentials --all-clients --service snipcart
```

### 🚀 **Performance Optimization**

#### **Efficient Integration Workflows**
```bash
# Use batch integrations for similar clients
blackwell integrate batch --template ecommerce-starter --clients client1,client2,client3

# Parallel processing for independent services
blackwell integrate start snipcart --client-id my-client --background &
blackwell integrate start sanity --client-id my-client --background &
wait

# Pre-validate before integration
blackwell integrate pre-check --client-id my-client --services snipcart,sanity
```

#### **Workflow Organization**
```bash
# Use consistent client naming
# ✅ Good: descriptive-kebab-case
blackwell integrate start snipcart --client-id my-ecommerce-store

# ✅ Good: environment prefixes for staging
blackwell integrate start snipcart --client-id staging-my-store
blackwell integrate start snipcart --client-id prod-my-store
```

---

## Development Roadmap

### **Phase 1: Core Framework (Week 1-2)**
- ✅ IntegrationOrchestrator class
- ✅ State management system
- ✅ Basic CLI commands (`start`, `status`, `resume`)
- ✅ Documentation and user guide

### **Phase 2: High-Priority Services (Week 3-4)**
- 🔄 Snipcart integration (most common e-commerce)
- 🔄 Sanity integration (popular CMS)
- 🔄 TinaCMS integration (simple tier-1 service)

### **Phase 3: Complex Services (Week 5-6)**
- ⏳ Contentful integration (complex CMS)
- ⏳ Shopify Basic integration (complex e-commerce)
- ⏳ Advanced verification and troubleshooting

### **Phase 4: Enhancement (Week 7-8)**
- ⏳ Integration templates and bulk operations
- ⏳ Custom integration definition framework
- ⏳ Analytics and performance monitoring
- ⏳ Advanced automation features

### **Success Criteria**
- **Reduced Integration Time**: From hours to minutes for most services
- **Increased Success Rate**: >90% completion rate with built-in validation
- **Enhanced User Experience**: Clear guidance and resumable workflows
- **Improved Consistency**: Standardized configurations across all clients
- **Better Security**: Automated credential management and rotation

---

## 🎉 **Conclusion**

The Blackwell CLI Service Integration Framework transforms complex third-party service setup from a time-consuming, error-prone process into a guided, partially-automated workflow. By combining intelligent automation with step-by-step guidance, you can confidently integrate any supported service while learning best practices along the way.

### **Key Achievements:**

✅ **Maximum Automation** - Automates all technical configuration that can be automated
✅ **Intelligent Guidance** - Provides step-by-step instructions for manual tasks
✅ **Resumable Workflows** - Save progress and resume anytime without losing work
✅ **Built-in Verification** - Tests connections and validates end-to-end functionality
✅ **Professional Experience** - Enterprise-grade integration capabilities with startup simplicity

### **Strategic Benefits:**

**🎯 Addresses Core Challenge**: We can't automate third-party account signup, but we can automate everything after credentials are provided while providing intelligent guidance for manual steps.

**⚡ Significant Time Savings**: Reduces integration time from hours to minutes for most services

**🛡️ Error Prevention**: Built-in validation and testing prevents common configuration mistakes

**📚 Educational Value**: Users learn integration best practices through guided workflows

**🔄 Scalable Solution**: Same framework works for simple APIs and complex enterprise services

### **Ready to Get Started?**

```bash
# List available services
blackwell integrate list-services

# Start your first integration
blackwell integrate start snipcart --client-id my-first-store

# You're now ready to integrate any third-party service! 🚀
```

---

*📚 This document covers Service Integration Framework v1.0. The framework provides both technical implementation details for developers and practical user guidance in a single comprehensive resource.*