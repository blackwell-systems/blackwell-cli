"""
Cost Calculator for Blackwell CLI

Provides intelligent cost estimation and optimization for client configurations.
Integrates with provider pricing models and AWS cost estimation.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel

from blackwell.core.client_manager import CLIClientConfig


class CostTier(str, Enum):
    """Cost tier classifications."""

    BUDGET = "budget"  # Under $100/month
    STANDARD = "standard"  # $100-250/month
    PROFESSIONAL = "professional"  # $250-500/month
    ENTERPRISE = "enterprise"  # Over $500/month


@dataclass
class CostBreakdown:
    """Detailed cost breakdown for a client configuration."""

    # Provider costs
    cms_cost: float
    ecommerce_cost: float
    ssg_cost: float

    # AWS infrastructure costs
    hosting_cost: float
    event_infrastructure_cost: float
    data_transfer_cost: float
    storage_cost: float

    # Variable costs
    transaction_fee_rate: float
    build_cost_per_build: float
    estimated_builds_per_month: int

    # Totals
    fixed_monthly_cost: float
    estimated_variable_cost: float
    total_estimated_cost: float

    # Metadata
    cost_tier: CostTier
    currency: str = "USD"


class ProviderPricing:
    """Provider pricing information and calculation logic."""

    # CMS Provider Pricing (monthly base costs)
    CMS_PRICING = {
        "decap": {"base": 0, "usage_fee": 0, "features": "basic"},
        "tina": {
            "base": 0,
            "tiers": [
                {"limit": 2, "cost": 0},  # Free tier
                {"limit": 10, "cost": 29},  # Starter
                {"limit": 100, "cost": 99},  # Team
            ],
            "features": "visual_editing",
        },
        "sanity": {
            "base": 0,
            "tiers": [
                {"limit": 3, "cost": 0},  # Free tier
                {"limit": 25, "cost": 99},  # Team
                {"limit": 100, "cost": 199},  # Business
            ],
            "features": "structured_content",
        },
        "contentful": {
            "base": 300,
            "tiers": [
                {"limit": 25, "cost": 300},  # Team
                {"limit": 100, "cost": 500},  # Business
                {"limit": 1000, "cost": 1000},  # Enterprise
            ],
            "features": "enterprise",
        },
    }

    # E-commerce Provider Pricing
    ECOMMERCE_PRICING = {
        "snipcart": {
            "base": 29,
            "transaction_fee": 0.02,  # 2%
            "free_threshold": 500,  # First $500 in sales is free
            "features": "simple_checkout",
        },
        "foxy": {
            "base": 75,
            "transaction_fee": 0.015,  # 1.5%
            "tiers": [
                {"sales_limit": 20000, "cost": 75},
                {"sales_limit": 100000, "cost": 150},
                {"sales_limit": 500000, "cost": 300},
            ],
            "features": "advanced_customization",
        },
        "shopify_basic": {
            "base": 29,
            "transaction_fee": 0.029,  # 2.9%
            "features": "full_ecommerce",
        },
        "shopify_advanced": {
            "base": 79,
            "transaction_fee": 0.024,  # 2.4%
            "features": "advanced_ecommerce",
        },
    }

    # SSG Engine Impact on AWS Costs
    SSG_COSTS = {
        "hugo": {"build_time_factor": 0.5, "complexity_factor": 0.8},
        "eleventy": {"build_time_factor": 0.7, "complexity_factor": 0.9},
        "astro": {"build_time_factor": 0.8, "complexity_factor": 1.0},
        "gatsby": {"build_time_factor": 1.2, "complexity_factor": 1.1},
        "nextjs": {"build_time_factor": 1.0, "complexity_factor": 1.2},
        "nuxtjs": {"build_time_factor": 1.0, "complexity_factor": 1.2},
    }

    # AWS Base Costs (monthly estimates)
    AWS_BASE_COSTS = {
        "s3_storage": 5,  # Basic storage for assets
        "cloudfront": 10,  # CDN distribution
        "route53": 1,  # DNS hosting
        "codebuild": 15,  # Build infrastructure
        "lambda": 5,  # Basic Lambda usage
        "api_gateway": 8,  # For webhooks
        "cloudwatch": 3,  # Monitoring and logs
    }

    # Event-driven infrastructure additional costs
    EVENT_DRIVEN_COSTS = {
        "sns": 2,  # Message publishing
        "dynamodb": 8,  # Content caching
        "lambda_additional": 5,  # Event processing
        "api_gateway_additional": 3,  # Additional endpoints
    }


class CostCalculator:
    """
    Calculate costs for client configurations with optimization recommendations.

    Provides:
    - Detailed cost breakdowns
    - Provider comparison
    - Optimization suggestions
    - Cost tier classification
    """

    def __init__(self):
        """Initialize cost calculator."""
        self.pricing = ProviderPricing()

    def calculate_client_cost(
        self,
        client: CLIClientConfig,
        estimated_monthly_sales: float = 0,
        estimated_monthly_builds: int = 30,
    ) -> CostBreakdown:
        """
        Calculate comprehensive cost breakdown for a client.

        Args:
            client: Client configuration
            estimated_monthly_sales: Estimated monthly sales volume
            estimated_monthly_builds: Estimated number of builds per month

        Returns:
            Detailed cost breakdown
        """
        # Calculate CMS costs
        cms_cost = self._calculate_cms_cost(client.cms_provider)

        # Calculate e-commerce costs
        ecommerce_cost = 0
        transaction_fee_rate = 0
        if client.ecommerce_provider:
            ecommerce_cost, transaction_fee_rate = self._calculate_ecommerce_cost(
                client.ecommerce_provider, estimated_monthly_sales
            )

        # Calculate SSG engine impact
        ssg_cost = 0  # SSG engines are free, but impact AWS costs

        # Calculate AWS infrastructure costs
        aws_costs = self._calculate_aws_costs(
            client.integration_mode,
            client.ssg_engine,
            estimated_monthly_builds,
            client.get_service_type(),
        )

        # Calculate totals
        fixed_monthly_cost = cms_cost + ecommerce_cost + aws_costs["total"]
        estimated_variable_cost = estimated_monthly_sales * transaction_fee_rate
        total_estimated_cost = fixed_monthly_cost + estimated_variable_cost

        # Determine cost tier
        cost_tier = self._determine_cost_tier(total_estimated_cost)

        return CostBreakdown(
            cms_cost=cms_cost,
            ecommerce_cost=ecommerce_cost,
            ssg_cost=ssg_cost,
            hosting_cost=aws_costs["hosting"],
            event_infrastructure_cost=aws_costs["event_infrastructure"],
            data_transfer_cost=aws_costs["data_transfer"],
            storage_cost=aws_costs["storage"],
            transaction_fee_rate=transaction_fee_rate,
            build_cost_per_build=aws_costs["build_cost_per_build"],
            estimated_builds_per_month=estimated_monthly_builds,
            fixed_monthly_cost=fixed_monthly_cost,
            estimated_variable_cost=estimated_variable_cost,
            total_estimated_cost=total_estimated_cost,
            cost_tier=cost_tier,
        )

    def _calculate_cms_cost(self, cms_provider: str) -> float:
        """Calculate CMS provider monthly cost."""
        if cms_provider not in self.pricing.CMS_PRICING:
            return 0

        pricing = self.pricing.CMS_PRICING[cms_provider]

        # Simple base cost for now
        # In a real implementation, this would consider usage tiers
        if "tiers" in pricing:
            # For tiered pricing, assume middle tier
            return pricing["tiers"][1]["cost"] if len(pricing["tiers"]) > 1 else 0
        else:
            return pricing["base"]

    def _calculate_ecommerce_cost(
        self, ecommerce_provider: str, monthly_sales: float
    ) -> Tuple[float, float]:
        """
        Calculate e-commerce provider cost and transaction fee rate.

        Returns:
            Tuple of (monthly_base_cost, transaction_fee_rate)
        """
        if ecommerce_provider not in self.pricing.ECOMMERCE_PRICING:
            return 0, 0

        pricing = self.pricing.ECOMMERCE_PRICING[ecommerce_provider]
        base_cost = pricing["base"]
        transaction_fee_rate = pricing["transaction_fee"]

        # Handle tiered pricing (e.g., Foxy.io)
        if "tiers" in pricing:
            for tier in pricing["tiers"]:
                if monthly_sales <= tier["sales_limit"]:
                    base_cost = tier["cost"]
                    break

        # Handle free thresholds (e.g., Snipcart)
        if "free_threshold" in pricing and monthly_sales <= pricing["free_threshold"]:
            base_cost = 0

        return base_cost, transaction_fee_rate

    def _calculate_aws_costs(
        self,
        integration_mode: str,
        ssg_engine: str,
        monthly_builds: int,
        service_type: str,
    ) -> Dict[str, float]:
        """Calculate AWS infrastructure costs."""
        base_costs = self.pricing.AWS_BASE_COSTS.copy()

        # Apply SSG engine cost factors
        ssg_factors = self.pricing.SSG_COSTS.get(
            ssg_engine, {"build_time_factor": 1.0, "complexity_factor": 1.0}
        )

        # Calculate base hosting costs
        hosting_cost = (
            base_costs["s3_storage"]
            + base_costs["cloudfront"]
            + base_costs["route53"]
            + base_costs["cloudwatch"]
        )

        # Calculate build costs
        build_cost_base = base_costs["codebuild"] * ssg_factors["build_time_factor"]
        build_cost_per_build = 0.01 * ssg_factors["build_time_factor"]

        # Calculate Lambda and API Gateway costs
        api_cost = base_costs["lambda"] + base_costs["api_gateway"]
        api_cost *= ssg_factors["complexity_factor"]

        # Add event-driven infrastructure costs
        event_infrastructure_cost = 0
        if integration_mode == "event_driven":
            event_costs = self.pricing.EVENT_DRIVEN_COSTS
            event_infrastructure_cost = (
                event_costs["sns"]
                + event_costs["dynamodb"]
                + event_costs["lambda_additional"]
                + event_costs["api_gateway_additional"]
            )

        # Estimate data transfer costs (varies by traffic)
        data_transfer_cost = 5  # Base estimate

        # Estimate storage costs (varies by content)
        storage_cost = base_costs["s3_storage"]

        total_aws_cost = (
            hosting_cost
            + build_cost_base
            + api_cost
            + event_infrastructure_cost
            + data_transfer_cost
            + storage_cost
        )

        return {
            "hosting": hosting_cost,
            "event_infrastructure": event_infrastructure_cost,
            "data_transfer": data_transfer_cost,
            "storage": storage_cost,
            "build_cost_per_build": build_cost_per_build,
            "total": total_aws_cost,
        }

    def _determine_cost_tier(self, total_cost: float) -> CostTier:
        """Determine cost tier based on total monthly cost."""
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

        Args:
            base_config: Base client configuration
            budget_limit: Maximum monthly budget
            monthly_sales: Estimated monthly sales

        Returns:
            List of provider combinations with cost analysis
        """
        combinations = []

        # Generate provider combinations
        cms_providers = list(self.pricing.CMS_PRICING.keys())
        ecommerce_providers = list(self.pricing.ECOMMERCE_PRICING.keys())

        for cms in cms_providers:
            # CMS-only configuration
            config = base_config.copy()
            config.update(
                {
                    "cms_provider": cms,
                    "ecommerce_provider": None,
                }
            )
            client = CLIClientConfig.model_validate(config)
            cost = self.calculate_client_cost(client, monthly_sales)

            if budget_limit is None or cost.total_estimated_cost <= budget_limit:
                combinations.append(
                    {
                        "type": "cms_only",
                        "cms_provider": cms,
                        "ecommerce_provider": None,
                        "cost": cost,
                        "config": config,
                    }
                )

            # CMS + E-commerce combinations
            for ecommerce in ecommerce_providers:
                config = base_config.copy()
                config.update(
                    {
                        "cms_provider": cms,
                        "ecommerce_provider": ecommerce,
                    }
                )
                client = CLIClientConfig.model_validate(config)
                cost = self.calculate_client_cost(client, monthly_sales)

                if budget_limit is None or cost.total_estimated_cost <= budget_limit:
                    combinations.append(
                        {
                            "type": "composed",
                            "cms_provider": cms,
                            "ecommerce_provider": ecommerce,
                            "cost": cost,
                            "config": config,
                        }
                    )

        # Sort by total cost
        combinations.sort(key=lambda x: x["cost"].total_estimated_cost)

        return combinations

    def get_optimization_suggestions(
        self, client: CLIClientConfig, monthly_sales: float = 0
    ) -> List[Dict[str, Any]]:
        """
        Get cost optimization suggestions for a client.

        Args:
            client: Client configuration
            monthly_sales: Estimated monthly sales

        Returns:
            List of optimization suggestions
        """
        suggestions = []
        current_cost = self.calculate_client_cost(client, monthly_sales)

        # Check integration mode optimization
        if client.integration_mode == "event_driven" and not client.ecommerce_provider:
            # Suggest direct mode for CMS-only sites
            test_client = client.model_copy()
            test_client.integration_mode = "direct"
            test_cost = self.calculate_client_cost(test_client, monthly_sales)

            if test_cost.total_estimated_cost < current_cost.total_estimated_cost:
                savings = (
                    current_cost.total_estimated_cost - test_cost.total_estimated_cost
                )
                suggestions.append(
                    {
                        "type": "integration_mode",
                        "suggestion": "Switch to Direct mode",
                        "reason": "Event-driven mode not needed for CMS-only sites",
                        "monthly_savings": savings,
                        "trade_offs": ["Lose composition capabilities"],
                    }
                )

        # Check SSG engine optimization
        ssg_alternatives = ["hugo", "eleventy", "astro"]
        for ssg in ssg_alternatives:
            if ssg != client.ssg_engine:
                test_client = client.model_copy()
                test_client.ssg_engine = ssg
                test_cost = self.calculate_client_cost(test_client, monthly_sales)

                if test_cost.total_estimated_cost < current_cost.total_estimated_cost:
                    savings = (
                        current_cost.total_estimated_cost
                        - test_cost.total_estimated_cost
                    )
                    suggestions.append(
                        {
                            "type": "ssg_engine",
                            "suggestion": f"Switch to {ssg.title()}",
                            "reason": f"{ssg.title()} has lower build costs",
                            "monthly_savings": savings,
                            "trade_offs": self._get_ssg_trade_offs(client.ssg_engine, ssg),
                        }
                    )

        # Check e-commerce provider optimization for high-volume sales
        if client.ecommerce_provider and monthly_sales > 10000:
            for provider in ["foxy", "shopify_advanced"]:
                if provider != client.ecommerce_provider:
                    test_client = client.model_copy()
                    test_client.ecommerce_provider = provider
                    test_cost = self.calculate_client_cost(test_client, monthly_sales)

                    if test_cost.total_estimated_cost < current_cost.total_estimated_cost:
                        savings = (
                            current_cost.total_estimated_cost
                            - test_cost.total_estimated_cost
                        )
                        suggestions.append(
                            {
                                "type": "ecommerce_provider",
                                "suggestion": f"Switch to {provider.replace('_', ' ').title()}",
                                "reason": f"Lower transaction fees for high-volume sales",
                                "monthly_savings": savings,
                                "trade_offs": self._get_ecommerce_trade_offs(
                                    client.ecommerce_provider, provider
                                ),
                            }
                        )

        # Sort by potential savings
        suggestions.sort(key=lambda x: x["monthly_savings"], reverse=True)

        return suggestions

    def _get_ssg_trade_offs(self, current: str, suggested: str) -> List[str]:
        """Get trade-offs for SSG engine changes."""
        trade_offs = {
            ("astro", "hugo"): ["More technical setup", "Less JavaScript ecosystem"],
            ("gatsby", "hugo"): ["Lose React ecosystem", "More technical setup"],
            ("nextjs", "eleventy"): ["Lose React features", "Less modern tooling"],
        }
        return trade_offs.get((current, suggested), ["Different tooling and workflow"])

    def _get_ecommerce_trade_offs(self, current: str, suggested: str) -> List[str]:
        """Get trade-offs for e-commerce provider changes."""
        trade_offs = {
            ("snipcart", "foxy"): ["More complex setup", "Higher base cost"],
            ("snipcart", "shopify_basic"): ["More complex integration", "Vendor lock-in"],
        }
        return trade_offs.get((current, suggested), ["Different features and workflow"])

    def estimate_roi(
        self,
        client: CLIClientConfig,
        monthly_sales: float,
        development_hours_saved: int = 40,
        developer_hourly_rate: float = 100,
    ) -> Dict[str, float]:
        """
        Estimate ROI of using the platform vs custom development.

        Args:
            client: Client configuration
            monthly_sales: Estimated monthly sales
            development_hours_saved: Hours saved vs custom development
            developer_hourly_rate: Developer hourly rate

        Returns:
            ROI analysis
        """
        # Calculate platform costs
        platform_cost = self.calculate_client_cost(client, monthly_sales)
        monthly_platform_cost = platform_cost.total_estimated_cost

        # Estimate custom development costs
        custom_development_cost = development_hours_saved * developer_hourly_rate
        custom_monthly_maintenance = 500  # Estimated monthly maintenance

        # Calculate savings
        upfront_savings = custom_development_cost
        monthly_savings = custom_monthly_maintenance - monthly_platform_cost

        # Calculate ROI over different periods
        roi_6_months = (
            upfront_savings + (monthly_savings * 6) - (monthly_platform_cost * 6)
        ) / (monthly_platform_cost * 6)
        roi_12_months = (
            upfront_savings + (monthly_savings * 12) - (monthly_platform_cost * 12)
        ) / (monthly_platform_cost * 12)

        return {
            "upfront_savings": upfront_savings,
            "monthly_savings": monthly_savings,
            "roi_6_months": roi_6_months,
            "roi_12_months": roi_12_months,
            "break_even_months": (
                custom_development_cost / monthly_platform_cost
                if monthly_platform_cost > 0
                else 0
            ),
        }