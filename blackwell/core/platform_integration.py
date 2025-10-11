"""
Platform Integration Module for Blackwell CLI

Provides safe integration with platform-infrastructure's PlatformStackFactory,
enabling the CLI to use live platform metadata while gracefully falling back
to static data when the platform is unavailable.

Key Features:
- Safe import pattern with graceful fallback
- Metadata transformation from platform format to CLI format
- Platform availability detection
- Zero dependencies when platform unavailable
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# Safe Import Pattern - CLI works even without platform-infrastructure
try:
    from shared.factories.platform_stack_factory import PlatformStackFactory
    PLATFORM_AVAILABLE = True
    logger.info("Platform integration available: PlatformStackFactory imported successfully")
except ImportError as e:
    PlatformStackFactory = None
    PLATFORM_AVAILABLE = False
    logger.debug(f"Platform integration unavailable: {e}")


def is_platform_available() -> bool:
    """Check if platform integration is available."""
    return PLATFORM_AVAILABLE and PlatformStackFactory is not None


def get_platform_metadata() -> Dict[str, Any]:
    """
    Get platform metadata with graceful fallback.

    Returns:
        Platform metadata dictionary, or empty dict if unavailable
    """
    if is_platform_available():
        try:
            metadata = PlatformStackFactory.STACK_METADATA
            logger.debug(f"Retrieved platform metadata: {len(metadata)} stack types")
            return metadata
        except Exception as e:
            logger.warning(f"Failed to retrieve platform metadata: {e}")
            return {}
    else:
        logger.debug("Platform metadata unavailable - using fallback")
        return {}


def get_platform_recommendations(requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get intelligent recommendations from platform factory.

    Args:
        requirements: Client requirements dictionary

    Returns:
        List of recommendations, or empty list if unavailable
    """
    if is_platform_available():
        try:
            recommendations = PlatformStackFactory.get_recommendations(requirements)
            logger.debug(f"Retrieved {len(recommendations)} platform recommendations")
            return recommendations
        except Exception as e:
            logger.warning(f"Failed to get platform recommendations: {e}")
            return []
    else:
        logger.debug("Platform recommendations unavailable")
        return []


def estimate_platform_cost(stack_type: str, ssg_engine: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get cost estimation from platform factory.

    Args:
        stack_type: Stack type identifier
        ssg_engine: Optional SSG engine

    Returns:
        Cost estimation dictionary, or None if unavailable
    """
    if is_platform_available():
        try:
            cost_estimate = PlatformStackFactory.estimate_total_cost(stack_type, ssg_engine)
            logger.debug(f"Retrieved cost estimate for {stack_type}: {cost_estimate.get('total_first_year_estimate', 'N/A')}")
            return cost_estimate
        except Exception as e:
            logger.warning(f"Failed to get platform cost estimate: {e}")
            return None
    else:
        logger.debug("Platform cost estimation unavailable")
        return None


def get_compatible_ssg_engines(stack_type: str) -> List[str]:
    """
    Get compatible SSG engines from platform factory.

    Args:
        stack_type: Stack type identifier

    Returns:
        List of compatible SSG engines, or empty list if unavailable
    """
    if is_platform_available():
        try:
            engines = PlatformStackFactory.get_compatible_ssg_engines(stack_type)
            logger.debug(f"Retrieved compatible SSG engines for {stack_type}: {engines}")
            return engines
        except Exception as e:
            logger.warning(f"Failed to get compatible SSG engines: {e}")
            return []
    else:
        logger.debug("Platform SSG compatibility unavailable")
        return []


def transform_to_cli_format(platform_metadata: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Transform platform factory metadata to CLI provider matrix format.

    Args:
        platform_metadata: Raw platform metadata from PlatformStackFactory

    Returns:
        Transformed metadata in CLI provider matrix format
    """
    if not platform_metadata:
        return {"cms": {}, "ecommerce": {}, "ssg": {}}

    cms_providers = {}
    ecommerce_providers = {}
    ssg_engines = {}

    logger.debug(f"Transforming {len(platform_metadata)} platform metadata entries")

    for stack_type, metadata in platform_metadata.items():
        category = metadata.get("category", "")

        # Transform CMS tier metadata
        if category == "cms_tier_service":
            provider = metadata.get("cms_provider")
            if provider:
                cms_providers[provider] = {
                    "name": metadata.get("tier_name", "").split(" - ")[0],  # Extract clean name
                    "cost": metadata.get("monthly_cost_range", [0, 0])[1],  # Use max cost
                    "features": metadata.get("key_features", []),
                    "compatible_ssg": metadata.get("ssg_engine_options", []),
                    "complexity": _map_complexity_level(metadata.get("complexity_level", "intermediate")),
                }

        # Transform E-commerce tier metadata
        elif category == "ecommerce_tier_service":
            provider = metadata.get("ecommerce_provider")
            if provider:
                ecommerce_providers[provider] = {
                    "name": metadata.get("tier_name", "").split(" - ")[0],  # Extract clean name
                    "cost": metadata.get("monthly_cost_range", [0, 0])[1],  # Use max cost
                    "transaction_fee": _extract_transaction_fee(metadata),
                    "features": metadata.get("key_features", []),
                    "compatible_ssg": metadata.get("ssg_engine_options", []),
                    "complexity": _map_complexity_level(metadata.get("complexity_level", "intermediate")),
                }

        # Transform SSG template and foundation stacks
        elif category in ["ssg_template_business_service", "foundation_ssg_service"]:
            ssg_engine = metadata.get("ssg_engine")
            if ssg_engine:
                ssg_engines[ssg_engine] = {
                    "name": _extract_ssg_display_name(ssg_engine),
                    "build_speed": _infer_build_speed(ssg_engine),
                    "language": _infer_language(ssg_engine),
                    "features": metadata.get("key_features", []),
                    "complexity": _map_complexity_level(metadata.get("complexity_level", "intermediate")),
                    "ecosystem": _infer_ecosystem(ssg_engine),
                }

    result = {
        "cms": cms_providers,
        "ecommerce": ecommerce_providers,
        "ssg": ssg_engines
    }

    logger.info(f"Transformed platform metadata: {len(cms_providers)} CMS, {len(ecommerce_providers)} E-commerce, {len(ssg_engines)} SSG")
    return result


def _map_complexity_level(platform_complexity: str) -> str:
    """Map platform complexity levels to CLI format."""
    mapping = {
        "low_to_medium": "beginner",
        "medium_to_high": "intermediate",
        "high": "advanced",
        "enterprise": "enterprise"
    }
    return mapping.get(platform_complexity, platform_complexity)


def _extract_transaction_fee(metadata: Dict[str, Any]) -> float:
    """Extract transaction fee from platform metadata."""
    # Look for common transaction fee indicators
    provider = metadata.get("ecommerce_provider", "")
    if provider == "snipcart":
        return 0.02  # 2%
    elif provider == "foxy":
        return 0.015  # 1.5%
    elif provider == "shopify_basic":
        return 0.029  # 2.9%
    return 0.0


def _extract_ssg_display_name(ssg_engine: str) -> str:
    """Extract display name for SSG engine."""
    names = {
        "hugo": "Hugo",
        "eleventy": "Eleventy",
        "astro": "Astro",
        "gatsby": "Gatsby",
        "nextjs": "Next.js",
        "nuxt": "Nuxt.js",
        "jekyll": "Jekyll"
    }
    return names.get(ssg_engine, ssg_engine.title())


def _infer_build_speed(ssg_engine: str) -> str:
    """Infer build speed for SSG engine."""
    speeds = {
        "hugo": "fastest",
        "eleventy": "fast",
        "astro": "fast",
        "gatsby": "medium",
        "nextjs": "medium",
        "nuxt": "medium",
        "jekyll": "medium"
    }
    return speeds.get(ssg_engine, "medium")


def _infer_language(ssg_engine: str) -> str:
    """Infer primary language for SSG engine."""
    languages = {
        "hugo": "go",
        "eleventy": "javascript",
        "astro": "javascript",
        "gatsby": "javascript",
        "nextjs": "javascript",
        "nuxt": "javascript",
        "jekyll": "ruby"
    }
    return languages.get(ssg_engine, "javascript")


def _infer_ecosystem(ssg_engine: str) -> str:
    """Infer ecosystem for SSG engine."""
    ecosystems = {
        "hugo": "go_templates",
        "eleventy": "javascript",
        "astro": "multi_framework",
        "gatsby": "react",
        "nextjs": "react",
        "nuxt": "vue",
        "jekyll": "ruby"
    }
    return ecosystems.get(ssg_engine, "javascript")


def get_integration_status() -> Dict[str, Any]:
    """
    Get detailed integration status for diagnostics.

    Returns:
        Status dictionary with integration details
    """
    status = {
        "platform_available": is_platform_available(),
        "metadata_count": 0,
        "last_error": None,
        "integration_mode": "static"
    }

    if is_platform_available():
        try:
            metadata = get_platform_metadata()
            status["metadata_count"] = len(metadata)
            status["integration_mode"] = "dynamic"

            # Test functionality
            test_recommendations = get_platform_recommendations({"test": True})
            status["recommendations_working"] = len(test_recommendations) >= 0

        except Exception as e:
            status["last_error"] = str(e)
            status["integration_mode"] = "static (error)"

    logger.debug(f"Integration status: {status}")
    return status