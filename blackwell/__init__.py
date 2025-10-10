"""
Blackwell CLI - Simplify composable web stack deployment.

The Blackwell CLI makes the sophisticated platform-infrastructure system accessible
to users without requiring Python/CDK expertise. It provides intelligent provider
selection, cost optimization, and simplified deployment workflows.
"""

__version__ = "0.1.0"
__author__ = "Blackwell Development Team"
__email__ = "dev@blackwell.dev"
__description__ = "Simplify composable web stack deployment with intelligent provider selection and cost optimization"

# Version info
VERSION_INFO = {
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "email": __email__,
}

# CLI Constants
CLI_NAME = "blackwell"
CLI_CONFIG_DIR = "~/.blackwell"
CLI_CONFIG_FILE = "config.yml"
CLI_CLIENTS_FILE = "clients.yml"

# Platform Integration
PLATFORM_INFRASTRUCTURE_REQUIRED_VERSION = "1.0.0"
CDK_REQUIRED_VERSION = "2.100.0"
PYTHON_REQUIRED_VERSION = "3.13"

# Export main components
from blackwell.core.config_manager import ConfigManager
from blackwell.core.client_manager import ClientManager
from blackwell.core.cost_calculator import CostCalculator

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "VERSION_INFO",
    "CLI_NAME",
    "CLI_CONFIG_DIR",
    "CLI_CONFIG_FILE",
    "CLI_CLIENTS_FILE",
    "ConfigManager",
    "ClientManager",
    "CostCalculator",
]