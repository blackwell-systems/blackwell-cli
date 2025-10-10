"""
Provider Matrix for Blackwell CLI

Defines the compatibility matrix for CMS, E-commerce, and SSG providers.
Used for validation and intelligent provider recommendations.
"""

from typing import Dict, List, Set
from enum import Enum


class ProviderType(str, Enum):
    """Provider type enumeration."""
    CMS = "cms"
    ECOMMERCE = "ecommerce"
    SSG = "ssg"


class ProviderMatrix:
    """
    Provider compatibility and validation matrix.

    Defines:
    - Valid providers for each type
    - Cost information
    - Feature compatibility
    - Integration requirements
    """

    def __init__(self):
        """Initialize provider matrix with current provider definitions."""

        # CMS Providers
        self.cms_providers: Dict[str, Dict] = {
            "decap": {
                "name": "Decap CMS",
                "cost": 0.0,
                "features": ["git_based", "free", "open_source"],
                "compatible_ssg": ["hugo", "eleventy", "astro", "gatsby"],
                "complexity": "intermediate",
            },
            "tina": {
                "name": "Tina CMS",
                "cost": 29.0,
                "features": ["visual_editing", "git_based", "live_preview"],
                "compatible_ssg": ["astro", "eleventy", "nextjs", "nuxt"],
                "complexity": "beginner",
            },
            "sanity": {
                "name": "Sanity CMS",
                "cost": 99.0,
                "features": ["structured_content", "real_time", "api_first"],
                "compatible_ssg": ["astro", "gatsby", "nextjs", "nuxt"],
                "complexity": "advanced",
            },
            "contentful": {
                "name": "Contentful",
                "cost": 300.0,
                "features": ["enterprise", "cdn", "multi_env", "workflows"],
                "compatible_ssg": ["gatsby", "astro", "nextjs", "nuxt"],
                "complexity": "enterprise",
            },
        }

        # E-commerce Providers
        self.ecommerce_providers: Dict[str, Dict] = {
            "snipcart": {
                "name": "Snipcart",
                "cost": 29.0,
                "transaction_fee": 0.02,
                "features": ["simple", "embed", "quick_setup"],
                "compatible_ssg": ["hugo", "eleventy", "astro", "gatsby"],
                "complexity": "beginner",
            },
            "foxy": {
                "name": "Foxy.io",
                "cost": 75.0,
                "transaction_fee": 0.015,
                "features": ["advanced", "customizable", "api_rich"],
                "compatible_ssg": ["hugo", "eleventy", "astro", "gatsby"],
                "complexity": "intermediate",
            },
            "shopify_basic": {
                "name": "Shopify Basic",
                "cost": 29.0,
                "transaction_fee": 0.029,
                "features": ["full_platform", "inventory", "analytics"],
                "compatible_ssg": ["eleventy", "astro", "nextjs", "nuxt"],
                "complexity": "intermediate",
            },
        }

        # SSG Engines
        self.ssg_engines: Dict[str, Dict] = {
            "hugo": {
                "name": "Hugo",
                "build_speed": "fastest",
                "language": "go",
                "features": ["blazing_fast", "simple", "powerful"],
                "complexity": "intermediate",
                "ecosystem": "go_templates",
            },
            "eleventy": {
                "name": "Eleventy",
                "build_speed": "fast",
                "language": "javascript",
                "features": ["flexible", "simple", "zero_config"],
                "complexity": "beginner",
                "ecosystem": "javascript",
            },
            "astro": {
                "name": "Astro",
                "build_speed": "fast",
                "language": "javascript",
                "features": ["component_islands", "framework_agnostic", "modern"],
                "complexity": "intermediate",
                "ecosystem": "multi_framework",
            },
            "gatsby": {
                "name": "Gatsby",
                "build_speed": "medium",
                "language": "javascript",
                "features": ["react_based", "graphql", "plugin_ecosystem"],
                "complexity": "advanced",
                "ecosystem": "react",
            },
            "nextjs": {
                "name": "Next.js",
                "build_speed": "medium",
                "language": "javascript",
                "features": ["react_framework", "ssr", "enterprise_ready"],
                "complexity": "advanced",
                "ecosystem": "react",
            },
            "nuxt": {
                "name": "Nuxt.js",
                "build_speed": "medium",
                "language": "javascript",
                "features": ["vue_framework", "ssr", "modular"],
                "complexity": "advanced",
                "ecosystem": "vue",
            },
        }

    def is_provider_valid(self, provider_type: str, provider_name: str) -> bool:
        """Check if a provider is valid for the given type."""
        if provider_type == "cms":
            return provider_name in self.cms_providers
        elif provider_type == "ecommerce":
            return provider_name in self.ecommerce_providers
        elif provider_type == "ssg":
            return provider_name in self.ssg_engines
        return False

    def get_provider_info(self, provider_type: str, provider_name: str) -> Dict:
        """Get detailed information about a provider."""
        if provider_type == "cms":
            return self.cms_providers.get(provider_name, {})
        elif provider_type == "ecommerce":
            return self.ecommerce_providers.get(provider_name, {})
        elif provider_type == "ssg":
            return self.ssg_engines.get(provider_name, {})
        return {}

    def is_combination_compatible(
        self, cms_provider: str, ecommerce_provider: str, ssg_engine: str
    ) -> bool:
        """Check if a combination of providers is compatible."""
        cms_info = self.get_provider_info("cms", cms_provider)
        ecommerce_info = self.get_provider_info("ecommerce", ecommerce_provider) if ecommerce_provider else {}

        # Check SSG compatibility with CMS
        if cms_info and ssg_engine not in cms_info.get("compatible_ssg", []):
            return False

        # Check SSG compatibility with e-commerce (if present)
        if ecommerce_info and ssg_engine not in ecommerce_info.get("compatible_ssg", []):
            return False

        return True

    def get_compatible_ssg_engines(
        self, cms_provider: str, ecommerce_provider: str = None
    ) -> List[str]:
        """Get list of SSG engines compatible with the given providers."""
        cms_info = self.get_provider_info("cms", cms_provider)
        cms_compatible = set(cms_info.get("compatible_ssg", []))

        if ecommerce_provider:
            ecommerce_info = self.get_provider_info("ecommerce", ecommerce_provider)
            ecommerce_compatible = set(ecommerce_info.get("compatible_ssg", []))
            # Return intersection of compatible engines
            return list(cms_compatible.intersection(ecommerce_compatible))

        return list(cms_compatible)

    def calculate_provider_cost(
        self, cms_provider: str, ecommerce_provider: str = None
    ) -> Dict[str, float]:
        """Calculate cost breakdown for provider combination."""
        cost_breakdown = {"cms_cost": 0.0, "ecommerce_cost": 0.0, "total_fixed": 0.0}

        # CMS cost
        cms_info = self.get_provider_info("cms", cms_provider)
        cms_cost = cms_info.get("cost", 0.0)
        cost_breakdown["cms_cost"] = cms_cost

        # E-commerce cost
        if ecommerce_provider:
            ecommerce_info = self.get_provider_info("ecommerce", ecommerce_provider)
            ecommerce_cost = ecommerce_info.get("cost", 0.0)
            cost_breakdown["ecommerce_cost"] = ecommerce_cost
            cost_breakdown["transaction_fee_rate"] = ecommerce_info.get("transaction_fee", 0.0)

        # Total fixed cost
        cost_breakdown["total_fixed"] = cms_cost + cost_breakdown["ecommerce_cost"]

        return cost_breakdown

    def get_providers_by_budget(self, max_monthly_cost: float) -> Dict[str, List[str]]:
        """Get providers within budget limit."""
        budget_providers = {"cms": [], "ecommerce": []}

        # Find CMS providers within budget
        for provider, info in self.cms_providers.items():
            if info["cost"] <= max_monthly_cost:
                budget_providers["cms"].append(provider)

        # Find e-commerce providers within budget
        for provider, info in self.ecommerce_providers.items():
            if info["cost"] <= max_monthly_cost:
                budget_providers["ecommerce"].append(provider)

        return budget_providers

    def get_complexity_level(
        self, cms_provider: str, ecommerce_provider: str = None, ssg_engine: str = "astro"
    ) -> str:
        """Determine overall complexity level for provider combination."""
        complexity_scores = {"beginner": 1, "intermediate": 2, "advanced": 3, "enterprise": 4}

        cms_info = self.get_provider_info("cms", cms_provider)
        cms_complexity = complexity_scores.get(cms_info.get("complexity", "intermediate"), 2)

        ssg_info = self.get_provider_info("ssg", ssg_engine)
        ssg_complexity = complexity_scores.get(ssg_info.get("complexity", "intermediate"), 2)

        max_complexity = max(cms_complexity, ssg_complexity)

        if ecommerce_provider:
            ecommerce_info = self.get_provider_info("ecommerce", ecommerce_provider)
            ecommerce_complexity = complexity_scores.get(ecommerce_info.get("complexity", "intermediate"), 2)
            max_complexity = max(max_complexity, ecommerce_complexity)

        # Convert back to string
        for level, score in complexity_scores.items():
            if score == max_complexity:
                return level

        return "intermediate"

    def list_all_providers(self) -> Dict[str, List[str]]:
        """Get all available providers by type."""
        return {
            "cms": list(self.cms_providers.keys()),
            "ecommerce": list(self.ecommerce_providers.keys()),
            "ssg": list(self.ssg_engines.keys()),
        }

    def get_recommended_combinations(self, budget: float = None, complexity: str = None) -> List[Dict]:
        """Get recommended provider combinations based on criteria."""
        recommendations = []

        for cms in self.cms_providers:
            for ssg in self.ssg_engines:
                if self.is_combination_compatible(cms, None, ssg):
                    combo = {
                        "cms_provider": cms,
                        "ecommerce_provider": None,
                        "ssg_engine": ssg,
                        "cost": self.calculate_provider_cost(cms),
                        "complexity": self.get_complexity_level(cms, None, ssg),
                    }

                    # Apply filters
                    if budget and combo["cost"]["total_fixed"] > budget:
                        continue
                    if complexity and combo["complexity"] != complexity:
                        continue

                    recommendations.append(combo)

                # Also check with e-commerce providers
                for ecommerce in self.ecommerce_providers:
                    if self.is_combination_compatible(cms, ecommerce, ssg):
                        combo = {
                            "cms_provider": cms,
                            "ecommerce_provider": ecommerce,
                            "ssg_engine": ssg,
                            "cost": self.calculate_provider_cost(cms, ecommerce),
                            "complexity": self.get_complexity_level(cms, ecommerce, ssg),
                        }

                        # Apply filters
                        if budget and combo["cost"]["total_fixed"] > budget:
                            continue
                        if complexity and combo["complexity"] != complexity:
                            continue

                        recommendations.append(combo)

        # Sort by cost
        recommendations.sort(key=lambda x: x["cost"]["total_fixed"])
        return recommendations