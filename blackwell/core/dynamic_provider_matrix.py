"""
Dynamic Provider Matrix for Blackwell CLI

Extends the static ProviderMatrix to use live data from platform-infrastructure's
PlatformStackFactory. Uses direct metadata access for instant updates without
file scanning complexity.

Key Features:
- Direct integration with PlatformStackFactory.STACK_METADATA
- Instant reflection of platform changes
- Graceful fallback to static data when platform unavailable
- Full backward compatibility with existing CLI code
- Enhanced intelligence using platform capabilities
"""

import logging
from typing import Dict, List, Any, Optional
from .provider_matrix import ProviderMatrix
from .platform_integration import (
    get_platform_metadata,
    transform_to_cli_format,
    is_platform_available,
    get_platform_recommendations,
    estimate_platform_cost,
    get_compatible_ssg_engines,
    get_integration_status
)

logger = logging.getLogger(__name__)


class DynamicProviderMatrix(ProviderMatrix):
    """
    Provider matrix that builds itself from platform-infrastructure metadata.

    Uses the refined pattern: Direct metadata access instead of file discovery.
    Maintains full compatibility with existing ProviderMatrix API while adding
    intelligence from the platform factory system.
    """

    def __init__(self):
        """Initialize dynamic provider matrix with platform integration."""
        logger.debug("Initializing DynamicProviderMatrix")

        # Track data source for diagnostics
        self._data_source = "static"
        self._platform_metadata_count = 0
        self._integration_status = get_integration_status()

        # Attempt to load from platform
        self._load_from_platform()

        # Call parent initialization (may use static data as fallback)
        super().__init__()

        logger.info(f"DynamicProviderMatrix initialized: {self._data_source} mode, "
                   f"{len(self.cms_providers)} CMS, {len(self.ecommerce_providers)} E-commerce, "
                   f"{len(self.ssg_engines)} SSG providers")

    def _load_from_platform(self) -> None:
        """Load provider data from platform metadata using direct access pattern."""
        try:
            # Get platform metadata using safe import pattern
            platform_metadata = get_platform_metadata()

            if platform_metadata:
                # Transform to CLI format
                cli_format = transform_to_cli_format(platform_metadata)

                # Load transformed metadata
                self._load_from_metadata(cli_format)

                # Update status tracking
                self._data_source = "platform"
                self._platform_metadata_count = len(platform_metadata)

                logger.info(f"Loaded provider data from platform: {len(platform_metadata)} stack types")
            else:
                logger.debug("No platform metadata available, using static fallback")

        except Exception as e:
            logger.warning(f"Failed to load from platform, using static fallback: {e}")

    def _load_from_metadata(self, metadata: Dict[str, Dict[str, Any]]) -> None:
        """Load provider dictionaries from transformed metadata."""
        if "cms" in metadata:
            self.cms_providers = metadata["cms"]
            logger.debug(f"Loaded {len(self.cms_providers)} CMS providers from platform")

        if "ecommerce" in metadata:
            self.ecommerce_providers = metadata["ecommerce"]
            logger.debug(f"Loaded {len(self.ecommerce_providers)} E-commerce providers from platform")

        if "ssg" in metadata:
            self.ssg_engines = metadata["ssg"]
            logger.debug(f"Loaded {len(self.ssg_engines)} SSG engines from platform")

    def get_data_source(self) -> str:
        """Get current data source for diagnostics."""
        return self._data_source

    def get_platform_status(self) -> Dict[str, Any]:
        """Get platform integration status."""
        return {
            "data_source": self._data_source,
            "platform_available": is_platform_available(),
            "platform_metadata_count": self._platform_metadata_count,
            "integration_status": self._integration_status
        }

    def refresh_from_platform(self) -> bool:
        """
        Refresh provider data from platform.

        Returns:
            True if refresh successful, False otherwise
        """
        logger.info("Refreshing provider data from platform")

        try:
            # Clear current data
            self.cms_providers = {}
            self.ecommerce_providers = {}
            self.ssg_engines = {}

            # Reload from platform
            self._load_from_platform()

            # Reinitialize parent static data if needed
            if self._data_source == "static":
                super().__init__()

            logger.info(f"Provider data refreshed: {self._data_source} mode")
            return True

        except Exception as e:
            logger.error(f"Failed to refresh provider data: {e}")
            return False

    # Enhanced methods using platform intelligence

    def get_intelligent_recommendations(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get intelligent recommendations using platform factory.

        Args:
            requirements: Client requirements dictionary

        Returns:
            List of recommendations with enhanced platform intelligence
        """
        if self._data_source == "platform":
            try:
                platform_recommendations = get_platform_recommendations(requirements)
                if platform_recommendations:
                    logger.debug(f"Retrieved {len(platform_recommendations)} platform recommendations")
                    return platform_recommendations
            except Exception as e:
                logger.warning(f"Failed to get platform recommendations: {e}")

        # Fallback to parent method for static recommendations
        logger.debug("Using static recommendations fallback")
        return self.get_recommended_combinations(**requirements)

    def get_accurate_cost_estimate(self, cms_provider: str, ecommerce_provider: Optional[str] = None,
                                 ssg_engine: str = "astro") -> Dict[str, Any]:
        """
        Get accurate cost estimate using platform factory.

        Args:
            cms_provider: CMS provider name
            ecommerce_provider: Optional e-commerce provider name
            ssg_engine: SSG engine name

        Returns:
            Enhanced cost estimate with platform intelligence
        """
        if self._data_source == "platform":
            try:
                # Try to get platform cost estimate
                if ecommerce_provider:
                    # For composed stacks, we'd need to estimate both
                    cms_cost = estimate_platform_cost(f"{cms_provider}_cms_tier", ssg_engine)
                    ecommerce_cost = estimate_platform_cost(f"{ecommerce_provider}_ecommerce", ssg_engine)

                    if cms_cost and ecommerce_cost:
                        return {
                            "cms_cost": cms_cost["monthly_cost_range"],
                            "ecommerce_cost": ecommerce_cost["monthly_cost_range"],
                            "total_monthly_range": [
                                cms_cost["monthly_cost_range"][0] + ecommerce_cost["monthly_cost_range"][0],
                                cms_cost["monthly_cost_range"][1] + ecommerce_cost["monthly_cost_range"][1]
                            ],
                            "setup_cost_estimate": {
                                "min": cms_cost["setup_cost_range"][0] + ecommerce_cost["setup_cost_range"][0],
                                "max": cms_cost["setup_cost_range"][1] + ecommerce_cost["setup_cost_range"][1]
                            },
                            "source": "platform"
                        }
                else:
                    # CMS only
                    cost_estimate = estimate_platform_cost(f"{cms_provider}_cms_tier", ssg_engine)
                    if cost_estimate:
                        return {
                            "cms_cost": cost_estimate["monthly_cost_range"],
                            "ecommerce_cost": [0, 0],
                            "total_monthly_range": cost_estimate["monthly_cost_range"],
                            "setup_cost_estimate": {
                                "min": cost_estimate["setup_cost_range"][0],
                                "max": cost_estimate["setup_cost_range"][1]
                            },
                            "source": "platform"
                        }

            except Exception as e:
                logger.warning(f"Failed to get platform cost estimate: {e}")

        # Fallback to parent method
        logger.debug("Using static cost calculation fallback")
        static_cost = self.calculate_provider_cost(cms_provider, ecommerce_provider)
        static_cost["source"] = "static"
        return static_cost

    def get_enhanced_compatibility_check(self, cms_provider: str, ecommerce_provider: str,
                                       ssg_engine: str) -> Dict[str, Any]:
        """
        Enhanced compatibility check using platform intelligence.

        Args:
            cms_provider: CMS provider name
            ecommerce_provider: E-commerce provider name
            ssg_engine: SSG engine name

        Returns:
            Detailed compatibility analysis
        """
        result = {
            "compatible": False,
            "issues": [],
            "recommendations": [],
            "source": "static"
        }

        if self._data_source == "platform":
            try:
                # Use platform compatibility data
                cms_engines = get_compatible_ssg_engines(f"{cms_provider}_cms_tier")
                ecommerce_engines = get_compatible_ssg_engines(f"{ecommerce_provider}_ecommerce")

                if cms_engines and ecommerce_engines:
                    compatible_engines = set(cms_engines).intersection(set(ecommerce_engines))

                    result["compatible"] = ssg_engine in compatible_engines
                    result["source"] = "platform"

                    if not result["compatible"]:
                        result["issues"].append(f"SSG engine '{ssg_engine}' not compatible with both providers")
                        if compatible_engines:
                            result["recommendations"].append(f"Compatible engines: {', '.join(sorted(compatible_engines))}")

                    logger.debug(f"Platform compatibility check: {cms_provider}/{ecommerce_provider}/{ssg_engine} = {result['compatible']}")
                    return result

            except Exception as e:
                logger.warning(f"Failed platform compatibility check: {e}")

        # Fallback to parent method
        logger.debug("Using static compatibility check fallback")
        result["compatible"] = self.is_combination_compatible(cms_provider, ecommerce_provider, ssg_engine)
        result["source"] = "static"

        if not result["compatible"]:
            result["issues"].append("Combination not supported by static matrix")

        return result

    def list_all_providers_with_source(self) -> Dict[str, Any]:
        """
        Get all providers with source information for diagnostics.

        Returns:
            Provider information with full provider dictionaries and source details
        """
        # Return full provider dictionaries instead of just lists of keys
        return {
            "cms": self.cms_providers,
            "ecommerce": self.ecommerce_providers,
            "ssg": self.ssg_engines,
            "meta": {
                "data_source": self._data_source,
                "platform_available": is_platform_available(),
                "total_combinations": len(self.cms_providers) * len(self.ecommerce_providers) * len(self.ssg_engines),
                "last_updated": self._integration_status
            }
        }