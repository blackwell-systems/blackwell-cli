"""
Blackwell CLI Core Components

This module contains the core functionality for the Blackwell CLI,
including configuration management, client operations, cost calculation,
and platform integration.
"""

from blackwell.core.config_manager import ConfigManager
from blackwell.core.client_manager import ClientManager
# Cost calculator removed - platform focuses on capabilities, not pricing

__all__ = [
    "ConfigManager",
    "ClientManager",
]