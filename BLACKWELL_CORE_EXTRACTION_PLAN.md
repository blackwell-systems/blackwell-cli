# Blackwell Core Extraction Plan

## Executive Summary

This document outlines the strategic extraction of a clean `blackwell-core` package from the existing Blackwell platform architecture. The goal is to separate the composition engine and business logic from implementation details (AWS/CDK) and presentation layers (CLI), creating a fundable, extensible product core.

## Current State Analysis

### Architectural Assessment

The Blackwell system has evolved into a sophisticated but complex multi-repository architecture with the following characteristics:

**Strengths:**
- Sophisticated Provider System: `ProviderMatrix` and `DynamicProviderMatrix` are already core-like
- Rich Metadata: Platform factory has comprehensive stack metadata with cost estimation
- Composition Logic: Well-developed compatibility checking and recommendation engine
- Safe Integration Pattern: Platform integration with graceful fallbacks

**Issues:**
- **Mixed Concerns**: CLI has AWS dependencies (`boto3`, `botocore`) it shouldn't need
- **Tight Coupling**: Direct dependency on `web-services-infrastructure` creates circular complexity
- **Scattered Logic**: Core business logic is distributed across three repositories

### Dependency Analysis (from blackwell-cli/pyproject.toml)

**Current Dependencies:**
```toml
dependencies = [
    "typer[all]>=0.9.0",           # ✅ CLI-appropriate
    "rich>=13.0.0",                # ✅ CLI-appropriate
    "pydantic>=2.0.0",             # ✅ Should be in core
    "pyyaml>=6.0.0",               # ✅ CLI-appropriate
    "boto3>=1.26.0",               # ❌ Should NOT be in CLI
    "botocore>=1.29.0",            # ❌ Should NOT be in CLI
    "pathlib2>=2.3.0",             # ✅ Utility dependency
    "python-dateutil>=2.8.0",     # ✅ Utility dependency
    "httpx>=0.24.0",               # ✅ CLI-appropriate
    "click-spinner>=0.1.10",       # ✅ CLI-appropriate
    "tabulate>=0.9.0",             # ✅ CLI-appropriate
    "web-services-infrastructure", # ❌ Tight coupling issue
]
```

## Strategic Vision

### What Should Be "Core"

The core should contain the **composition engine** - an abstract framework that allows any combination of CMS, SSG, and E-commerce providers to compose into a single deployable architecture.

**Core Components:**
1. **Provider Metadata System**: Standardized metadata for all providers (capabilities, costs, complexity)
2. **Composition Framework**: Logic that validates and optimizes provider combinations
3. **Cost Intelligence**: Accurate cost estimation and optimization recommendations
4. **Compatibility Engine**: Rules and validation for provider compatibility
5. **Recommendation System**: Intelligent suggestions based on requirements

### What Should NOT Be Core

**Infrastructure Layer** (stays in platform-infrastructure):
- AWS/CDK stack implementations
- Resource provisioning logic
- Deployment orchestration

**Presentation Layer** (stays in blackwell-cli):
- CLI commands and user interface
- Configuration file management
- Progress indicators and formatting

## Detailed Implementation Plan

## Phase 1: Create Core Package Structure (Week 1)

### 1.1 New Repository: `blackwell-core`

Create a new repository with the following structure:

```
blackwell-core/
├── pyproject.toml                 # Pure Python deps: pydantic, typing-extensions only
├── README.md                      # Core package documentation
├── CHANGELOG.md                   # Version history
├── blackwell_core/
│   ├── __init__.py               # Main API exports
│   ├── models/                   # Pydantic models from both repos
│   │   ├── __init__.py
│   │   ├── providers.py          # Provider definitions & metadata
│   │   ├── composition.py        # Composition plans & rules
│   │   ├── cost.py              # Cost estimation models
│   │   ├── enums.py             # Consolidated enums
│   │   └── requirements.py       # Client requirements models
│   ├── engine/                   # Core composition logic
│   │   ├── __init__.py
│   │   ├── provider_matrix.py    # From blackwell-cli/core
│   │   ├── composition_engine.py # New: orchestrates everything
│   │   ├── cost_calculator.py    # From blackwell-cli/core
│   │   ├── recommendation_engine.py # From platform factory
│   │   └── compatibility.py      # Compatibility checking logic
│   ├── adapters/                 # Provider-specific logic
│   │   ├── __init__.py
│   │   ├── base_adapter.py       # Base adapter interface
│   │   ├── cms_adapter.py        # CMS provider adapters
│   │   ├── ecommerce_adapter.py  # E-commerce provider adapters
│   │   └── ssg_adapter.py        # SSG engine adapters
│   ├── metadata/                 # Provider metadata
│   │   ├── __init__.py
│   │   ├── cms_metadata.py       # CMS provider metadata
│   │   ├── ecommerce_metadata.py # E-commerce metadata
│   │   ├── ssg_metadata.py       # SSG engine metadata
│   │   └── cost_data.py          # Cost estimation data
│   └── utils/                    # Pure utilities
│       ├── __init__.py
│       ├── validators.py         # Validation utilities
│       ├── compatibility.py      # Compatibility utilities
│       └── transformers.py       # Data transformation utilities
├── tests/                        # Comprehensive test suite
│   ├── __init__.py
│   ├── test_models/
│   ├── test_engine/
│   ├── test_adapters/
│   ├── test_metadata/
│   └── test_integration/
├── docs/                         # Documentation
│   ├── api-reference.md
│   ├── provider-guide.md
│   └── composition-examples.md
└── examples/                     # Usage examples
    ├── basic_composition.py
    ├── cost_optimization.py
    └── custom_providers.py
```

### 1.2 Core pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "blackwell-core"
version = "0.1.0"
description = "Blackwell Core - Composable web stack composition engine"
authors = [
    {name = "Blackwell Development Team"}
]
readme = "README.md"
requires-python = ">=3.13"
license = {text = "MIT"}
keywords = ["composition", "web-development", "providers", "cost-optimization"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.13",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

dependencies = [
    # Data Modeling - Core dependency
    "pydantic>=2.0.0",
    # Type Extensions
    "typing-extensions>=4.0.0",
    # Enum support for older Python versions (if needed)
    # "enum34>=1.1.10; python_version<'3.4'",
]

[project.optional-dependencies]
dev = [
    # Testing
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",

    # Code Quality
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",

    # Development Tools
    "pre-commit>=3.0.0",
    "build>=0.10.0",
]

[project.urls]
Homepage = "https://github.com/blackwell-dev/blackwell-core"
Documentation = "https://docs.blackwell.dev/core"
Repository = "https://github.com/blackwell-dev/blackwell-core"
"Bug Tracker" = "https://github.com/blackwell-dev/blackwell-core/issues"
```

### 1.3 Define Clean API Surface

```python
# blackwell_core/__init__.py - Main API exports
from .engine.composition_engine import CompositionEngine
from .engine.provider_matrix import ProviderMatrix
from .engine.cost_calculator import CostCalculator
from .engine.recommendation_engine import RecommendationEngine

from .models.composition import CompositionPlan, CompositionRequest
from .models.providers import ProviderConfig, ProviderMetadata
from .models.cost import CostEstimate, CostBreakdown
from .models.enums import SSGEngine, CMSProvider, EcommerceProvider

# Main API workflow
__all__ = [
    # Core engines
    "CompositionEngine",
    "ProviderMatrix",
    "CostCalculator",
    "RecommendationEngine",

    # Data models
    "CompositionPlan",
    "CompositionRequest",
    "ProviderConfig",
    "ProviderMetadata",
    "CostEstimate",
    "CostBreakdown",

    # Enums
    "SSGEngine",
    "CMSProvider",
    "EcommerceProvider",
]
```

### 1.4 Migration Strategy for Existing Code

**Files to Extract from blackwell-cli:**
- `blackwell/core/provider_matrix.py` → `blackwell_core/engine/provider_matrix.py`
- `blackwell/core/cost_calculator.py` → `blackwell_core/engine/cost_calculator.py`
- `blackwell/core/dynamic_provider_matrix.py` → Integrate into core engine
- `blackwell/core/platform_integration.py` → Transform into adapter pattern

**Files to Extract from platform-infrastructure:**
- `models/component_enums.py` → `blackwell_core/models/enums.py`
- `shared/factories/platform_stack_factory.py` (metadata only) → `blackwell_core/metadata/`
- Provider models from `shared/providers/` → `blackwell_core/adapters/`

## Phase 2: Update Dependent Repositories (Week 2)

### 2.1 Blackwell CLI Refactor

**Dependencies to Remove:**
```toml
# Remove these from blackwell-cli dependencies:
"boto3>=1.26.0",               # Move to platform-infrastructure
"botocore>=1.29.0",            # Move to platform-infrastructure
"web-services-infrastructure", # Replace with blackwell-core
```

**Dependencies to Add:**
```toml
# Add to blackwell-cli dependencies:
"blackwell-core>=0.1.0",      # Clean core dependency
```

**Code Changes:**
- Replace all `from blackwell.core.provider_matrix` with `from blackwell_core`
- Remove AWS-specific imports from CLI commands
- Refactor platform integration to use core API
- Update configuration management to use core models

### 2.2 Platform Infrastructure Refactor

**Dependencies to Add:**
```toml
# Add to platform-infrastructure dependencies (models only):
"blackwell-core>=0.1.0",      # For shared models only
```

**Code Changes:**
- Move stack metadata to blackwell-core
- Remove composition logic from PlatformStackFactory
- Refactor stack factories to consume `CompositionPlan` objects
- Keep only CDK/AWS implementation details

### 2.3 Clean Dependency Graph

The final dependency relationship should be:

```
┌─────────────────┐
│  blackwell-cli  │ ──depends──┐
└─────────────────┘            │
                               ▼
┌─────────────────────────┐ ┌─────────────────┐
│ platform-infrastructure │ │  blackwell-core │
└─────────────────────────┘ └─────────────────┘
             │                        ▲
             └────────depends──────────┘
              (models only)

Dependencies:
• blackwell-cli → blackwell-core (full API)
• platform-infrastructure → blackwell-core (models only)
• blackwell-core → [pydantic, typing-extensions] (minimal)
```

## Phase 3: Enhanced Features (Week 3)

### 3.1 Advanced Composition Engine

**Multi-Provider Optimization:**
```python
class CompositionEngine:
    def optimize_for_cost(self, requirements: Dict) -> List[CompositionPlan]:
        """Find lowest-cost configurations meeting requirements."""

    def optimize_for_performance(self, requirements: Dict) -> List[CompositionPlan]:
        """Find highest-performance configurations."""

    def optimize_for_complexity(self, requirements: Dict) -> List[CompositionPlan]:
        """Find lowest-complexity configurations for team skill level."""
```

**Migration Path Planning:**
```python
def plan_migration(
    current_config: ProviderConfig,
    target_config: ProviderConfig
) -> MigrationPlan:
    """Generate step-by-step migration plan between configurations."""
```

### 3.2 Plugin Architecture

**Provider Adapter Registry:**
```python
class ProviderAdapterRegistry:
    """Registry for custom provider adapters."""

    def register_cms_adapter(self, provider_name: str, adapter_class: Type):
        """Register custom CMS provider adapter."""

    def register_ecommerce_adapter(self, provider_name: str, adapter_class: Type):
        """Register custom e-commerce provider adapter."""
```

**Hook System:**
```python
@hookimpl
def validate_composition(composition_plan: CompositionPlan) -> ValidationResult:
    """Custom validation hook for composition plans."""

@hookimpl
def transform_cost_estimate(estimate: CostEstimate) -> CostEstimate:
    """Custom cost transformation hook."""
```

### 3.3 Export Capabilities

**Multiple Export Formats:**
```python
class CompositionExporter:
    def to_json_schema(self, plan: CompositionPlan) -> Dict:
        """Export composition plan as JSON schema."""

    def to_terraform_vars(self, plan: CompositionPlan) -> Dict:
        """Export as Terraform variables."""

    def to_cost_report(self, estimate: CostEstimate) -> str:
        """Generate detailed cost analysis report."""
```

## Benefits Analysis

### Technical Benefits

**Clean Architecture:**
- Clear separation between composition logic (core) and implementation (stacks)
- Single responsibility principle applied at repository level
- Reduced coupling between CLI and AWS infrastructure

**Testability:**
- Core logic tests run without AWS dependencies or CDK setup
- Faster test execution (target: <5 seconds for full core test suite)
- Easier to test edge cases and error conditions

**Reusability:**
- Core can power CLI, web applications, APIs, and third-party tools
- Provider adapters can be reused across different deployment targets
- Cost intelligence available to any consumer

**Extensibility:**
- New providers added through adapter pattern
- Cloud-agnostic core can support Azure, GCP implementations
- Plugin system for custom business logic

### Business Benefits

**Clear Product Definition:**
- "Blackwell Core" becomes the composable web stack engine
- Easy to explain value proposition to investors and customers
- Clear competitive differentiation

**Open Source Strategy:**
- Core can be open source to build ecosystem
- Implementation layers remain proprietary for competitive advantage
- Community contributions improve provider coverage

**Ecosystem Growth:**
- Third parties can build tools on blackwell-core
- Provider vendors can contribute their own adapters
- Consulting partners can extend for specific use cases

**Funding Narrative:**
- Clear, focused product that solves composition problem
- Analogous to successful products (Terraform for infrastructure, Kubernetes for containers)
- Addressable market includes all web agencies and development teams

### Development Benefits

**Faster Development Cycle:**
- Core changes don't require AWS deployment for testing
- Easier to reproduce and debug issues
- Better separation allows parallel development

**Easier Onboarding:**
- New developers can start with pure Python logic
- No need to understand AWS/CDK for core contributions
- Clear boundaries between different types of contributions

**Better Debugging:**
- Clear stack traces within each component
- Easier to isolate issues to core logic vs. implementation
- Better error messages with clear responsibility boundaries

**Version Independence:**
- Core, CLI, and infrastructure can evolve at different rates
- Breaking changes isolated to appropriate layers
- Easier to maintain backward compatibility

## Success Metrics

### Technical Metrics

**Dependency Cleanliness:**
- ✅ blackwell-core has zero AWS/CDK dependencies
- ✅ blackwell-cli has zero direct AWS SDK usage
- ✅ platform-infrastructure only imports core models

**Performance Metrics:**
- ✅ Core test suite runs in <5 seconds
- ✅ Provider recommendation generation <100ms
- ✅ Cost estimation calculation <50ms
- ✅ Composition validation <200ms

**Functionality Preservation:**
- ✅ All existing CLI functionality works unchanged
- ✅ All existing provider combinations supported
- ✅ Cost estimation accuracy within ±5% of current system
- ✅ Platform integration maintains graceful fallbacks

### Business Metrics

**Ecosystem Adoption:**
- 📈 Number of third-party tools using blackwell-core
- 📈 Community contributions to provider adapters
- 📈 GitHub stars and usage metrics

**Development Velocity:**
- 📈 Time to add new provider (target: 50% reduction)
- 📈 Time to implement new features (target: 30% reduction)
- 📈 Developer onboarding time (target: 60% reduction)

## Risk Mitigation

### Technical Risks

**Risk:** Breaking existing functionality during extraction
**Mitigation:**
- Comprehensive test coverage before refactoring
- Gradual migration with feature flags
- Maintain parallel implementations during transition

**Risk:** Performance degradation from abstraction layers
**Mitigation:**
- Benchmark critical paths before/after extraction
- Optimize core algorithms for performance
- Use lazy loading and caching strategies

**Risk:** Increased complexity from multiple repositories
**Mitigation:**
- Clear documentation of inter-repo relationships
- Automated integration testing across repositories
- Version compatibility matrix and tooling

### Business Risks

**Risk:** Loss of competitive advantage through open sourcing core
**Mitigation:**
- Keep implementation details (CDK stacks, AWS optimizations) proprietary
- Core provides framework, not complete solution
- Build moat through superior implementations and integrations

**Risk:** Community contributions creating maintenance burden
**Mitigation:**
- Clear contribution guidelines and automated testing
- Modular adapter system limits impact of individual contributions
- Maintain core team control over architecture decisions

## Implementation Timeline

### Week 1: Foundation (Phase 1)
- [ ] Create blackwell-core repository structure
- [ ] Extract and refactor provider matrix system
- [ ] Extract and refactor cost calculation engine
- [ ] Extract component enums and models
- [ ] Create basic CompositionEngine framework
- [ ] Set up comprehensive test suite

### Week 2: Integration (Phase 2)
- [ ] Refactor blackwell-cli to use blackwell-core
- [ ] Update platform-infrastructure dependencies
- [ ] Migrate stack metadata to core
- [ ] Update all import statements and references
- [ ] Verify all existing functionality works
- [ ] Update documentation and examples

### Week 3: Enhancement (Phase 3)
- [ ] Implement advanced composition features
- [ ] Add plugin architecture and hooks
- [ ] Create export capabilities
- [ ] Performance optimization
- [ ] Enhanced error handling and validation
- [ ] Prepare for initial release

## Conclusion

The Blackwell Core extraction represents a strategic architectural evolution that will:

1. **Clarify the Product**: Create a clear, fundable core product with obvious value proposition
2. **Enable Growth**: Provide foundation for ecosystem development and third-party integrations
3. **Improve Development**: Faster testing, clearer responsibilities, easier onboarding
4. **Reduce Risk**: Better separation of concerns, more modular architecture
5. **Increase Value**: Reusable core can power multiple products and use cases

This extraction formalizes the natural architecture boundaries that already exist in the Blackwell platform and positions it for sustainable growth and competitive advantage.

---

## Appendix: Code Examples

### A.1 Core API Usage

```python
from blackwell_core import CompositionEngine

# Initialize the composition engine
engine = CompositionEngine()

# Define client requirements
requirements = {
    "budget_max": 200,
    "performance_critical": True,
    "team_size": "small",
    "technical_expertise": "intermediate",
    "content_volume": "medium",
    "ecommerce_needed": True
}

# Get recommendations
recommendations = engine.get_recommendations(requirements)

# Create specific composition
plan = engine.compose(
    cms_provider="sanity",
    ecommerce_provider="snipcart",
    ssg_engine="astro",
    requirements=requirements
)

# Estimate costs
cost_estimate = engine.estimate_cost(plan)

# Validate compatibility
validation = engine.validate_composition(plan)
```

### A.2 Custom Provider Adapter

```python
from blackwell_core.adapters.base_adapter import BaseCMSAdapter
from blackwell_core.models.providers import ProviderMetadata

class CustomCMSAdapter(BaseCMSAdapter):
    def get_metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="Custom CMS",
            cost_range=(50, 150),
            complexity="intermediate",
            features=["custom_workflow", "api_integration"],
            compatible_ssg=["astro", "gatsby"]
        )

    def validate_config(self, config: Dict) -> ValidationResult:
        # Custom validation logic
        pass

    def estimate_setup_cost(self, requirements: Dict) -> float:
        # Custom cost estimation logic
        pass

# Register the adapter
from blackwell_core import get_provider_registry
registry = get_provider_registry()
registry.register_cms_adapter("custom_cms", CustomCMSAdapter)
```

### A.3 Cost Optimization

```python
from blackwell_core import CompositionEngine

engine = CompositionEngine()

# Find all valid combinations under budget
budget_options = engine.find_combinations_under_budget(
    max_monthly_cost=150,
    requirements={"ecommerce_needed": True}
)

# Optimize for specific criteria
cost_optimized = engine.optimize_for_cost(requirements)
performance_optimized = engine.optimize_for_performance(requirements)
simplicity_optimized = engine.optimize_for_complexity(requirements)

# Compare options
comparison = engine.compare_compositions([
    cost_optimized[0],
    performance_optimized[0],
    simplicity_optimized[0]
])
```

This plan provides a comprehensive roadmap for extracting the Blackwell Core while maintaining all existing functionality and positioning the platform for future growth and success.