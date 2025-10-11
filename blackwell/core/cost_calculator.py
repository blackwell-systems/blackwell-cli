"""
Cost Calculator for Blackwell CLI

CLI-specific cost estimation wrapper that integrates blackwell-core cost calculation
with CLI client configurations and workflow-specific functionality.
"""

from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

from blackwell_core.engine.cost_calculator import CostCalculator as CoreCostCalculator
from blackwell_core.models.cost import (
    CostComponent,
    CostBreakdown as CoreCostBreakdown,
    CostEstimate
)
from blackwell_core.models.enums import ComplexityLevel

from blackwell.core.client_manager import CLIClientConfig


class CostTier(str, Enum):
    """CLI-specific cost tier classifications."""

    BUDGET = "budget"  # Under $100/month
    STANDARD = "standard"  # $100-250/month
    PROFESSIONAL = "professional"  # $250-500/month
    ENTERPRISE = "enterprise"  # Over $500/month


class CostBreakdown:
    """
    CLI-specific cost breakdown wrapper around core cost models.

    Provides backward compatibility for CLI workflows while using blackwell-core
    calculation engine under the hood.
    """

    def __init__(self, core_breakdown: CoreCostBreakdown, cost_tier: CostTier):
        """Initialize from core cost breakdown."""
        self._core_breakdown = core_breakdown
        self.cost_tier = cost_tier
        self.currency = "USD"

    # Delegate properties to core breakdown
    @property
    def cms_cost(self) -> float:
        """CMS provider monthly cost."""
        cms_components = [c for c in self._core_breakdown.components if c.component_type == "cms"]
        return sum(c.total_monthly_cost for c in cms_components)

    @property
    def ecommerce_cost(self) -> float:
        """E-commerce provider monthly cost."""
        ecommerce_components = [c for c in self._core_breakdown.components if c.component_type == "ecommerce"]
        return sum(c.total_monthly_cost for c in ecommerce_components)

    @property
    def ssg_cost(self) -> float:
        """SSG engine cost (typically $0)."""
        ssg_components = [c for c in self._core_breakdown.components if c.component_type == "ssg"]
        return sum(c.total_monthly_cost for c in ssg_components)

    @property
    def hosting_cost(self) -> float:
        """AWS hosting infrastructure cost."""
        return self._core_breakdown.infrastructure_cost * 0.6  # Estimate hosting portion

    @property
    def event_infrastructure_cost(self) -> float:
        """Event-driven infrastructure cost."""
        return self._core_breakdown.infrastructure_cost * 0.4  # Estimate event portion

    @property
    def data_transfer_cost(self) -> float:
        """Data transfer and CDN costs."""
        return 5.0  # Fixed estimate for CLI compatibility

    @property
    def storage_cost(self) -> float:
        """Storage costs."""
        return 5.0  # Fixed estimate for CLI compatibility

    @property
    def transaction_fee_rate(self) -> float:
        """Transaction fee rate from e-commerce providers."""
        return self._core_breakdown.total_transaction_fee_rate

    @property
    def build_cost_per_build(self) -> float:
        """Estimated cost per build."""
        return 0.01  # Fixed estimate for CLI compatibility

    @property
    def estimated_builds_per_month(self) -> int:
        """Estimated builds per month."""
        return 30  # Default estimate

    @property
    def fixed_monthly_cost(self) -> float:
        """Fixed monthly costs."""
        return self._core_breakdown.estimated_monthly_total

    @property
    def estimated_variable_cost(self) -> float:
        """Variable costs based on usage."""
        # This would be calculated based on transaction volume
        return 0.0  # Simplified for CLI compatibility

    @property
    def total_estimated_cost(self) -> float:
        """Total estimated monthly cost."""
        return self.fixed_monthly_cost + self.estimated_variable_cost




class CostCalculator:
    """
    CLI-specific cost calculator wrapper around blackwell-core.

    Provides backward compatibility for CLI workflows while leveraging
    the blackwell-core calculation engine for accurate cost estimation.
    """

    def __init__(self):
        """Initialize CLI cost calculator with core engine."""
        self._core_calculator = CoreCostCalculator()

    def calculate_client_cost(
        self,
        client: CLIClientConfig,
        estimated_monthly_sales: float = 0,
        estimated_monthly_builds: int = 30,
    ) -> CostBreakdown:
        """
        Calculate comprehensive cost breakdown for a client.

        Args:
            client: CLI client configuration
            estimated_monthly_sales: Estimated monthly sales volume
            estimated_monthly_builds: Estimated number of builds per month

        Returns:
            CLI-compatible cost breakdown
        """
        # Convert CLI client config to core components
        components = self._convert_client_to_components(client, estimated_monthly_sales)

        # Calculate infrastructure cost estimate
        infrastructure_cost = self._estimate_infrastructure_cost(
            client.integration_mode,
            client.ssg_engine,
            estimated_monthly_builds
        )

        # Use core calculator
        core_breakdown = self._core_calculator.calculate_composition_cost(
            composition_id=f"cli-{client.client_id}",
            components=components,
            infrastructure_cost=infrastructure_cost,
            transaction_volume_assumptions={
                "monthly_sales": estimated_monthly_sales,
                "estimated_builds": estimated_monthly_builds
            } if estimated_monthly_sales > 0 else None
        )

        # Determine CLI-specific cost tier
        cost_tier = self._determine_cost_tier(core_breakdown.estimated_monthly_total)

        # Return CLI-compatible breakdown
        return CostBreakdown(core_breakdown, cost_tier)

    def _convert_client_to_components(
        self,
        client: CLIClientConfig,
        monthly_sales: float = 0
    ) -> List[CostComponent]:
        """Convert CLI client config to core cost components."""
        components = []

        # Add CMS component
        if client.cms_provider:
            cms_cost = self._get_cms_base_cost(client.cms_provider)
            components.append(CostComponent(
                component_type="cms",
                provider=client.cms_provider,
                base_cost=cms_cost,
                cost_model="fixed_monthly"
            ))

        # Add e-commerce component
        if client.ecommerce_provider:
            ecommerce_cost, transaction_fee = self._get_ecommerce_costs(
                client.ecommerce_provider, monthly_sales
            )
            components.append(CostComponent(
                component_type="ecommerce",
                provider=client.ecommerce_provider,
                base_cost=ecommerce_cost,
                transaction_fee_rate=transaction_fee,
                cost_model="hybrid" if transaction_fee > 0 else "fixed_monthly"
            ))

        # Add SSG component (usually free)
        components.append(CostComponent(
            component_type="ssg",
            provider=client.ssg_engine,
            base_cost=0.0,
            cost_model="free"
        ))

        return components

    def _get_cms_base_cost(self, cms_provider: str) -> float:
        """Get base CMS cost for CLI compatibility."""
        cms_costs = {
            "decap": 0.0,
            "tina": 29.0,  # Assume starter tier
            "sanity": 99.0,  # Assume team tier
            "contentful": 300.0  # Assume team tier
        }
        return cms_costs.get(cms_provider, 0.0)

    def _get_ecommerce_costs(self, provider: str, monthly_sales: float) -> Tuple[float, float]:
        """Get e-commerce base cost and transaction fee."""
        provider_data = {
            "snipcart": (29.0, 0.02),
            "foxy": (75.0, 0.015),
            "shopify_basic": (29.0, 0.029),
            "shopify_advanced": (79.0, 0.024),
        }
        return provider_data.get(provider, (0.0, 0.0))

    def _estimate_infrastructure_cost(
        self,
        integration_mode: str,
        ssg_engine: str,
        monthly_builds: int
    ) -> float:
        """Estimate AWS infrastructure costs."""
        base_cost = 45.0  # Basic AWS services

        # Add event-driven costs
        if integration_mode == "event_driven":
            base_cost += 15.0

        # Apply SSG engine factors
        ssg_factors = {
            "hugo": 0.8,
            "eleventy": 0.9,
            "astro": 1.0,
            "gatsby": 1.2,
            "nextjs": 1.1,
            "nuxtjs": 1.1
        }

        factor = ssg_factors.get(ssg_engine, 1.0)
        return base_cost * factor

    def _determine_cost_tier(self, total_cost: float) -> CostTier:
        """Determine CLI cost tier based on total monthly cost."""
        if total_cost < 100:
            return CostTier.BUDGET
        elif total_cost < 250:
            return CostTier.STANDARD
        elif total_cost < 500:
            return CostTier.PROFESSIONAL
        else:
            return CostTier.ENTERPRISE

    def compare_providers(
        self,
        base_config: Dict[str, Any],
        budget_limit: Optional[float] = None,
        monthly_sales: float = 0,
    ) -> List[Dict[str, Any]]:
        """
        Compare different provider combinations within budget.

        This is a simplified CLI wrapper around core comparison functionality.
        """
        # For now, provide basic comparison by testing a few key combinations
        combinations = []

        cms_options = ["decap", "sanity", "contentful"]
        ecommerce_options = [None, "snipcart", "foxy"]

        for cms in cms_options:
            for ecommerce in ecommerce_options:
                try:
                    config = base_config.copy()
                    config.update({
                        "cms_provider": cms,
                        "ecommerce_provider": ecommerce,
                    })
                    client = CLIClientConfig.model_validate(config)
                    cost = self.calculate_client_cost(client, monthly_sales)

                    if budget_limit is None or cost.total_estimated_cost <= budget_limit:
                        combinations.append({
                            "type": "composed" if ecommerce else "cms_only",
                            "cms_provider": cms,
                            "ecommerce_provider": ecommerce,
                            "cost": cost,
                            "config": config,
                        })
                except Exception:
                    # Skip invalid combinations
                    continue

        # Sort by total cost
        combinations.sort(key=lambda x: x["cost"].total_estimated_cost)
        return combinations

    def get_optimization_suggestions(
        self, client: CLIClientConfig, monthly_sales: float = 0
    ) -> List[Dict[str, Any]]:
        """
        Get cost optimization suggestions for a client.

        Simplified CLI version that provides basic optimization advice.
        """
        suggestions = []
        current_cost = self.calculate_client_cost(client, monthly_sales)

        # Integration mode optimization
        if client.integration_mode == "event_driven" and not client.ecommerce_provider:
            suggestions.append({
                "type": "integration_mode",
                "suggestion": "Consider Direct mode for CMS-only sites",
                "reason": "Event-driven mode adds infrastructure cost for CMS-only setups",
                "estimated_savings": 15.0,
                "trade_offs": ["Simplified architecture", "Lower costs"]
            })

        # SSG engine optimization for cost
        if client.ssg_engine in ["gatsby", "nextjs"] and current_cost.total_estimated_cost > 200:
            suggestions.append({
                "type": "ssg_engine",
                "suggestion": "Consider Hugo or Eleventy for lower costs",
                "reason": "Faster builds mean lower infrastructure costs",
                "estimated_savings": 20.0,
                "trade_offs": ["Different framework", "Potentially faster builds"]
            })

        return suggestions