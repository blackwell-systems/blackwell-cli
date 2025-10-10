# Blackwell CLI

**Simplify composable web stack deployment with intelligent provider selection and cost optimization**

The Blackwell CLI transforms the sophisticated [platform-infrastructure](../platform-infrastructure) system into an accessible, user-friendly tool that democratizes advanced web development capabilities. No Python or CDK expertise required.

## Overview

The Blackwell CLI abstracts the complexity of the platform-infrastructure system, providing:

- **Intelligent Provider Selection**: Mix any CMS (Decap, Tina, Sanity, Contentful) with any E-commerce provider (Snipcart, Foxy, Shopify)
- **Cost Optimization**: Based on provider choice, not architectural complexity
- **Dual-Mode Architecture**: Direct (simple) or Event-Driven (composition-ready) integration modes
- **Automated Deployment**: One-command deployment with AWS CDK integration
- **Provider Migration**: Easy switching between providers without infrastructure rewrites

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd blackwell-cli

# Install dependencies
uv sync

# Install the CLI (development mode)
uv pip install -e .

# Verify installation
blackwell --version
```

### Initialize Your Workspace

```bash
# Interactive workspace setup
blackwell init workspace

# Create your first project
blackwell init project my-startup --interactive
```

## Project Status

### Implemented

#### Core Infrastructure
- **CLI Framework**: Complete Typer-based CLI with Rich output styling
- **Configuration Management**: Comprehensive config system with validation
- **Client Management**: Full CRUD operations for client configurations
- **Cost Calculator**: Intelligent cost estimation and optimization engine

#### Command Structure
- **Main Entry Point**: `blackwell/main.py` with error handling and global options
- **Init Commands**: Workspace initialization and project creation
- **Command Stubs**: Basic structure for all planned commands

#### Key Features
- **Provider Intelligence**: Built-in knowledge of CMS/E-commerce provider costs and compatibility
- **Cost Analysis**: Detailed cost breakdowns with optimization suggestions
- **Template System**: Pre-built configurations for common use cases
- **Interactive Setup**: Guided project creation with intelligent recommendations
- **Configuration Validation**: Comprehensive validation with troubleshooting tips

### In Development

The following commands have placeholder implementations and are ready for development:

- `blackwell create` - Client and template creation
- `blackwell deploy` - Infrastructure deployment and management
- `blackwell cost` - Advanced cost analysis and monitoring
- `blackwell migrate` - Provider migration tools
- `blackwell list` - Inventory and status management
- `blackwell config` - CLI configuration management
- `blackwell templates` - Template management system

## Architecture

### Project Structure

```
blackwell-cli/
├── blackwell/                    # Main package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # CLI entry point
│   ├── commands/                # Command implementations
│   │   ├── __init__.py         # Command registration
│   │   ├── init.py             # Workspace and project init
│   │   ├── create.py           # Client/template creation
│   │   ├── deploy.py           # Infrastructure deployment
│   │   ├── cost.py             # Cost analysis
│   │   ├── migrate.py          # Provider migration
│   │   ├── list.py             # Listing commands
│   │   ├── config.py           # Configuration management
│   │   └── templates.py        # Template management
│   ├── core/                   # Core functionality
│   │   ├── __init__.py         # Core exports
│   │   ├── config_manager.py   # Configuration management
│   │   ├── client_manager.py   # Client CRUD operations
│   │   └── cost_calculator.py  # Cost estimation engine
│   ├── integrations/           # Platform integrations
│   ├── templates/              # Built-in templates
│   └── utils/                  # Utilities
├── tests/                      # Test suite
├── docs/                       # Documentation
├── pyproject.toml             # Package configuration
├── README.md                  # This file
└── BLACKWELL_CLI_PLAN.md      # Comprehensive design plan
```

### Core Components

#### ConfigManager (`blackwell/core/config_manager.py`)
- **Pydantic-based configuration** with automatic validation
- **Environment variable support** for CI/CD integration
- **Auto-discovery** of platform-infrastructure project
- **AWS integration** with profile and region management
- **Default preferences** for streamlined client creation

#### ClientManager (`blackwell/core/client_manager.py`)
- **Complete client lifecycle** management (CRUD operations)
- **Status tracking** with deployment history
- **Configuration validation** with detailed error reporting
- **Platform-infrastructure integration** via export functionality
- **Cost tracking** with estimated vs actual cost analysis

#### CostCalculator (`blackwell/core/cost_calculator.py`)
- **Comprehensive cost modeling** for all providers
- **Intelligent optimization suggestions** based on usage patterns
- **Provider comparison** within budget constraints
- **ROI analysis** vs custom development costs
- **Cost tier classification** (Budget/Standard/Professional/Enterprise)

## Usage Examples

### Initialize Workspace

```bash
# Interactive setup with guidance
blackwell init workspace

# Non-interactive with specific settings
blackwell init workspace --no-interactive
blackwell config set aws.profile production
blackwell config set aws.region us-west-2
```

### Create a New Project

```bash
# Interactive project creation with cost guidance
blackwell init project my-startup --interactive --budget 100

# Use a specific template
blackwell init project my-store --template budget-startup

# Non-interactive with explicit settings
blackwell init project my-site \
  --company "My Company" \
  --domain "mycompany.com" \
  --email "admin@mycompany.com" \
  --no-interactive
```

### Configuration Management

The CLI uses a hierarchical configuration system:

1. **Default values** in code
2. **Configuration file** (`~/.blackwell/config.yml`)
3. **Environment variables** (highest priority)

```yaml
# ~/.blackwell/config.yml
version: "0.1.0"
aws:
  profile: "default"
  region: "us-east-1"
defaults:
  cms_provider: "decap"
  ecommerce_provider: "snipcart"
  ssg_engine: "astro"
  integration_mode: "event_driven"
platform_infrastructure:
  path: "/path/to/platform-infrastructure"
  auto_discover: true
```

### Environment Variables

```bash
# AWS Configuration
export AWS_PROFILE=production
export AWS_DEFAULT_REGION=us-west-2

# Blackwell-specific
export BLACKWELL_PLATFORM_PATH=/custom/path/to/platform-infrastructure
export BLACKWELL_VERBOSE=true
```


## Platform-Infrastructure Integration

The CLI seamlessly integrates with the platform-infrastructure project:

### Auto-Discovery
The CLI automatically searches for platform-infrastructure in common locations:
- Current directory (`./platform-infrastructure`)
- Parent directory (`../platform-infrastructure`)
- Standard paths (`~/code/business/platform-infrastructure`)

### Configuration Export
Client configurations are automatically converted to platform-infrastructure format:

```python
# CLI configuration automatically becomes:
from models.client_templates import tier1_composed_client

client = tier1_composed_client(
    client_id="my-startup",
    company_name="My Startup Co",
    domain="mystartup.com",
    contact_email="admin@mystartup.com",
    cms_provider="decap",
    ecommerce_provider="snipcart",
    ssg_engine="astro",
    integration_mode=IntegrationMode.EVENT_DRIVEN
)
```

## Development

### Setting Up Development Environment

```bash
# Clone repository
git clone <repository-url>
cd blackwell-cli

# Install dependencies
uv sync

# Install development dependencies
uv sync --dev

# Install in development mode
uv pip install -e .

# Run tests (when implemented)
uv run pytest

# Format code
uv run black blackwell/
uv run ruff check blackwell/
```

### Adding New Commands

1. Create command file in `blackwell/commands/`
2. Import and register in `blackwell/commands/__init__.py`
3. Add to main app in `blackwell/main.py`

Example:
```python
# blackwell/commands/example.py
import typer
from rich.console import Console

app = typer.Typer(help="Example command")
console = Console()

@app.command()
def hello(name: str):
    """Say hello to someone."""
    console.print(f"Hello, {name}!")
```

### Testing

```bash
# Test CLI during development
uv run blackwell --help
uv run blackwell init workspace --help

# Test specific commands
uv run python -m blackwell.main init workspace --no-interactive
```

## Roadmap

### Phase 1: Core Functionality (Current)
- CLI framework and basic commands
- Configuration and client management
- Cost calculation engine
- Interactive project creation

### Phase 2: Deployment Integration
- CDK deployment wrapper
- Stack status monitoring
- AWS resource management
- Error handling and recovery

### Phase 3: Advanced Features
- Provider migration tools
- Cost monitoring and alerts
- Template customization
- Bulk operations

### Phase 4: Polish & Production
- Comprehensive test suite
- Documentation and guides
- Package distribution
- CI/CD integration

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Run formatting (`uv run black . && uv run ruff check .`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Design Philosophy

The Blackwell CLI is designed with these principles:

1. **Simplicity First**: Complex operations should be simple commands
2. **Cost Transparency**: Always show cost implications upfront
3. **Intelligent Defaults**: Smart recommendations based on requirements
4. **Provider Freedom**: No vendor lock-in, easy migration paths
5. **Progressive Enhancement**: Start simple, scale up as needed

## Support

- **Documentation**: See `BLACKWELL_CLI_PLAN.md` for comprehensive design details
- **Issues**: Report bugs and feature requests via GitHub issues
- **Development**: See the development section above for contribution guidelines

## License

MIT License - See `LICENSE` file for details.

---

**Built to democratize advanced web development through intelligent automation and cost optimization.**