# Stack Factory & Provider Matrix Unification Implementation Plan

## 🎯 Objective
Unify the CLI provider matrix with platform-infrastructure stack factories to create a single source of truth, eliminating duplication and ensuring perfect synchronization between CLI capabilities and actual platform implementations.

## 📋 Current State Analysis

### Existing Systems
- **CLI Provider Matrix**: Static metadata in `blackwell/core/provider_matrix.py`
- **Platform Stack Factories**: CDK implementations in `platform-infrastructure/stacks/`
- **Problem**: Duplicate information that can drift out of sync

### Gap Analysis
- Stack implementations contain real deployment logic but no standardized metadata
- CLI provider matrix has metadata but may not reflect actual platform capabilities
- No automatic discovery mechanism for new stack implementations

## 🏗️ Implementation Strategy

### Phase 1: Stack Metadata Standardization

#### 1.1 Create Base Metadata Classes
**File**: `platform-infrastructure/shared/base/stack_metadata.py`

```python
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel, Field
from enum import Enum

class ComplexityLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"

class ProviderMetadata(BaseModel):
    """Base metadata for all providers"""
    version: str = Field(default="1.0.0", description="Metadata schema version for compatibility")
    provider_type: str  # "cms", "ecommerce", "ssg"
    provider_name: str
    display_name: str
    cost_range: Tuple[float, float]  # (min, max) monthly cost
    features: List[str]
    complexity: ComplexityLevel
    ecosystem: str  # "javascript", "ruby", "go", etc.

    class Config:
        frozen = True  # Ensure metadata is immutable

class SSGMetadata(ProviderMetadata):
    """SSG-specific metadata"""
    build_speed: str  # "fastest", "fast", "medium", "slow"
    language: str
    compatible_cms: List[str]
    compatible_ecommerce: List[str]

class CMSMetadata(ProviderMetadata):
    """CMS-specific metadata"""
    workflow_type: str  # "git_based", "api_first", "hybrid"
    compatible_ssg: List[str]

class EcommerceMetadata(ProviderMetadata):
    """E-commerce specific metadata"""
    transaction_fee_rate: float
    compatible_ssg: List[str]
```

#### 1.2 Create Stack Metadata Mixin
**File**: `platform-infrastructure/shared/base/metadata_mixin.py`

```python
from abc import ABC, abstractmethod
from typing import Union
from .stack_metadata import ProviderMetadata

class StackMetadataMixin(ABC):
    """Mixin for stacks to declare their provider metadata"""

    @classmethod
    @abstractmethod
    def get_provider_metadata(cls) -> ProviderMetadata:
        """Return provider metadata for this stack"""
        pass

    @classmethod
    def get_stack_identifier(cls) -> str:
        """Get unique identifier for this stack"""
        return f"{cls.__module__}.{cls.__name__}"
```

#### 1.3 Update Existing Stacks
**Example**: `platform-infrastructure/stacks/hosted-only/tier1/jekyll_github_stack.py`

```python
from shared.base.metadata_mixin import StackMetadataMixin
from shared.base.stack_metadata import SSGMetadata, ComplexityLevel

class JekyllGithubStack(Stack, StackMetadataMixin):

    @classmethod
    def get_provider_metadata(cls) -> SSGMetadata:
        return SSGMetadata(
            provider_type="ssg",
            provider_name="jekyll",
            display_name="Jekyll",
            cost_range=(0, 25),
            features=["github_pages", "blog_ready", "liquid_templates", "technical_focus"],
            complexity=ComplexityLevel.BEGINNER,
            ecosystem="ruby",
            build_speed="medium",
            language="ruby",
            compatible_cms=["decap", "tina"],
            compatible_ecommerce=["snipcart", "foxy"]
        )
```

### Phase 2: CLI Discovery System

#### 2.1 Create Stack Discovery Engine
**File**: `blackwell/core/stack_discovery.py`

```python
import importlib
import inspect
import json
import sys
from pathlib import Path
from typing import Dict, List, Type, Optional
import hashlib
from datetime import datetime
import logging

from shared.base.metadata_mixin import StackMetadataMixin
from shared.base.stack_metadata import ProviderMetadata

logger = logging.getLogger(__name__)

class StackDiscovery:
    """Discovers and catalogs all available stacks from platform-infrastructure"""

    def __init__(self, platform_path: Path, cache_dir: Optional[Path] = None):
        self.platform_path = platform_path
        self.cache_dir = cache_dir or (Path.home() / ".blackwell_cache")
        self.cache_file = self.cache_dir / "providers.json"
        self.discovered_stacks: Dict[str, Type] = {}
        self.provider_registry: Dict[str, Dict[str, ProviderMetadata]] = {
            "ssg": {},
            "cms": {},
            "ecommerce": {}
        }

    def discover_all_stacks(self, force_refresh: bool = False) -> None:
        """Scan platform-infrastructure for all stack implementations with caching"""
        if not force_refresh and self._can_use_cache():
            logger.info("Using cached provider registry")
            self._load_from_cache()
            return

        logger.info("Discovering stacks from platform-infrastructure")
        stack_files = list(self.platform_path.rglob("*_stack.py"))

        for stack_file in stack_files:
            try:
                self._discover_stacks_in_file(stack_file)
            except Exception as e:
                logger.warning(f"Failed to discover stacks in {stack_file}: {e}")

        self._save_to_cache()

    def _discover_stacks_in_file(self, stack_file: Path) -> None:
        """Safely discover stacks in a specific file without triggering CDK side effects"""
        relative_path = stack_file.relative_to(self.platform_path)
        module_path = str(relative_path.with_suffix("")).replace("/", ".")

        try:
            # Add platform path to Python path temporarily
            original_path = sys.path.copy()
            sys.path.insert(0, str(self.platform_path))

            # Import module without initializing CDK resources
            spec = importlib.util.spec_from_file_location(module_path, stack_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find stack classes with metadata (but never instantiate them)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(obj, StackMetadataMixin) and
                        hasattr(obj, "get_provider_metadata") and
                        obj.__module__ == module_path  # Only classes defined in this module
                    ):
                        try:
                            # Call static metadata method (safe - no CDK instantiation)
                            metadata = obj.get_provider_metadata()

                            # Validate metadata version compatibility
                            if self._is_metadata_compatible(metadata):
                                self._register_stack(obj, metadata)
                            else:
                                logger.warning(f"Incompatible metadata version in {obj.__name__}: {metadata.version}")

                        except Exception as e:
                            logger.error(f"Failed to get metadata from {obj.__name__}: {e}")

        except Exception as e:
            logger.error(f"Failed to import {module_path}: {e}")
        finally:
            # Restore original Python path
            sys.path = original_path

    def _register_stack(self, stack_class: Type, metadata: ProviderMetadata) -> None:
        """Register a discovered stack and its metadata"""
        stack_id = f"{stack_class.__module__}.{stack_class.__name__}"
        self.discovered_stacks[stack_id] = stack_class

        # Register in provider registry
        provider_type = metadata.provider_type
        provider_name = metadata.provider_name

        if provider_type in self.provider_registry:
            self.provider_registry[provider_type][provider_name] = metadata
            logger.debug(f"Registered {provider_type} provider: {provider_name}")

    def _is_metadata_compatible(self, metadata: ProviderMetadata) -> bool:
        """Check if metadata version is compatible with current CLI"""
        # Simple version compatibility check - can be enhanced
        try:
            version_parts = metadata.version.split(".")
            major = int(version_parts[0])
            return major == 1  # Compatible with v1.x.x
        except (ValueError, IndexError):
            return False

    def _can_use_cache(self) -> bool:
        """Check if cached registry can be used (exists and is newer than stack files)"""
        if not self.cache_file.exists():
            return False

        cache_mtime = self.cache_file.stat().st_mtime

        # Check if any stack file is newer than cache
        for stack_file in self.platform_path.rglob("*_stack.py"):
            if stack_file.stat().st_mtime > cache_mtime:
                return False

        return True

    def _save_to_cache(self) -> None:
        """Save discovered providers to cache"""
        try:
            self.cache_dir.mkdir(exist_ok=True)

            cache_data = {
                "timestamp": datetime.now().isoformat(),
                "platform_path": str(self.platform_path),
                "providers": {}
            }

            # Serialize provider metadata
            for provider_type, providers in self.provider_registry.items():
                cache_data["providers"][provider_type] = {}
                for provider_name, metadata in providers.items():
                    cache_data["providers"][provider_type][provider_name] = metadata.dict()

            with open(self.cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)

            logger.info(f"Cached provider registry to {self.cache_file}")

        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def _load_from_cache(self) -> None:
        """Load provider registry from cache"""
        try:
            with open(self.cache_file, "r") as f:
                cache_data = json.load(f)

            # Reconstruct provider registry from cached data
            for provider_type, providers in cache_data.get("providers", {}).items():
                for provider_name, metadata_dict in providers.items():
                    # Reconstruct metadata objects based on type
                    if provider_type == "ssg":
                        from shared.base.stack_metadata import SSGMetadata
                        metadata = SSGMetadata(**metadata_dict)
                    elif provider_type == "cms":
                        from shared.base.stack_metadata import CMSMetadata
                        metadata = CMSMetadata(**metadata_dict)
                    elif provider_type == "ecommerce":
                        from shared.base.stack_metadata import EcommerceMetadata
                        metadata = EcommerceMetadata(**metadata_dict)
                    else:
                        continue

                    self.provider_registry[provider_type][provider_name] = metadata

        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            # If cache loading fails, fall back to discovery
            self.discover_all_stacks(force_refresh=True)

    def get_provider_info(self, provider_type: str, provider_name: str) -> Optional[ProviderMetadata]:
        """Get provider metadata from discovered stacks"""
        return self.provider_registry.get(provider_type, {}).get(provider_name)

    def list_providers_by_type(self, provider_type: str) -> List[str]:
        """List all providers of a given type"""
        return list(self.provider_registry.get(provider_type, {}).keys())

    def get_discovery_stats(self) -> Dict[str, int]:
        """Get statistics about discovered providers"""
        return {
            "total_stacks": len(self.discovered_stacks),
            "ssg_providers": len(self.provider_registry["ssg"]),
            "cms_providers": len(self.provider_registry["cms"]),
            "ecommerce_providers": len(self.provider_registry["ecommerce"]),
        }
```

#### 2.2 Create Dynamic Provider Matrix
**File**: `blackwell/core/dynamic_provider_matrix.py`

```python
from typing import Dict, List, Optional
from pathlib import Path
from .stack_discovery import StackDiscovery
from .provider_matrix import ProviderMatrix  # Keep for backward compatibility

class DynamicProviderMatrix(ProviderMatrix):
    """Provider matrix that builds itself from platform-infrastructure discoveries"""

    def __init__(self, platform_path: Optional[Path] = None):
        self.platform_path = platform_path or self._find_platform_path()
        self.discovery = StackDiscovery(self.platform_path)
        self.discovery.discover_all_stacks()

        # Build dynamic provider dictionaries
        self._build_dynamic_providers()

        # Call parent init after building providers
        super().__init__()

    def _build_dynamic_providers(self) -> None:
        """Build provider dictionaries from discovered stack metadata"""
        self.cms_providers = self._build_cms_providers()
        self.ecommerce_providers = self._build_ecommerce_providers()
        self.ssg_engines = self._build_ssg_engines()

    def _build_ssg_engines(self) -> Dict[str, Dict]:
        """Build SSG engines from discovered metadata"""
        ssg_engines = {}
        for provider_name, metadata in self.discovery.provider_registry["ssg"].items():
            ssg_engines[provider_name] = {
                "name": metadata.display_name,
                "build_speed": metadata.build_speed if hasattr(metadata, 'build_speed') else "medium",
                "language": metadata.language if hasattr(metadata, 'language') else "unknown",
                "features": metadata.features,
                "complexity": metadata.complexity.value,
                "ecosystem": metadata.ecosystem,
            }
        return ssg_engines

    def _build_cms_providers(self) -> Dict[str, Dict]:
        """Build CMS providers from discovered metadata"""
        cms_providers = {}
        for provider_name, metadata in self.discovery.provider_registry["cms"].items():
            cms_providers[provider_name] = {
                "name": metadata.display_name,
                "cost": metadata.cost_range[1],  # Use max cost for budgeting
                "features": metadata.features,
                "compatible_ssg": metadata.compatible_ssg if hasattr(metadata, 'compatible_ssg') else [],
                "complexity": metadata.complexity.value,
            }
        return cms_providers

    def _build_ecommerce_providers(self) -> Dict[str, Dict]:
        """Build e-commerce providers from discovered metadata"""
        ecommerce_providers = {}
        for provider_name, metadata in self.discovery.provider_registry["ecommerce"].items():
            ecommerce_providers[provider_name] = {
                "name": metadata.display_name,
                "cost": metadata.cost_range[1],  # Use max cost for budgeting
                "transaction_fee": metadata.transaction_fee_rate if hasattr(metadata, 'transaction_fee_rate') else 0.0,
                "features": metadata.features,
                "compatible_ssg": metadata.compatible_ssg if hasattr(metadata, 'compatible_ssg') else [],
                "complexity": metadata.complexity.value,
            }
        return ecommerce_providers
```

### Phase 3: Integration & Migration

#### 3.1 Update CLI Configuration
**File**: `blackwell/core/config_manager.py`

```python
import os
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    def get_provider_matrix(self, force_static: bool = False) -> ProviderMatrix:
        """Get provider matrix (dynamic if platform path available)"""
        # Check for CLI flag to force static mode
        if force_static or os.getenv("BLACKWELL_NO_DISCOVERY", "").lower() in ("1", "true", "yes"):
            logger.info("Using static provider matrix (discovery disabled)")
            return ProviderMatrix()

        platform_path = self._get_platform_path()

        if platform_path and platform_path.exists():
            try:
                logger.info(f"Loading dynamic provider matrix from {platform_path}")
                return DynamicProviderMatrix(platform_path)
            except Exception as e:
                # Log warning and fallback to static matrix
                logger.warning(f"Failed to load dynamic provider matrix: {e}")
                logger.info("Falling back to static provider matrix")
                return ProviderMatrix()
        else:
            if platform_path:
                logger.warning(f"Platform path configured but not found: {platform_path}")
            logger.info("Using static provider matrix (no platform path configured)")
            return ProviderMatrix()

    def refresh_provider_matrix(self) -> None:
        """Force refresh of provider matrix (clears cache)"""
        platform_path = self._get_platform_path()
        if platform_path and platform_path.exists():
            try:
                # Clear cache and force discovery
                from .stack_discovery import StackDiscovery
                discovery = StackDiscovery(platform_path)
                cache_file = discovery.cache_file
                if cache_file.exists():
                    cache_file.unlink()
                    logger.info(f"Cleared provider cache: {cache_file}")
            except Exception as e:
                logger.error(f"Failed to clear provider cache: {e}")

    def get_discovery_mode(self) -> str:
        """Get current discovery mode for diagnostics"""
        if os.getenv("BLACKWELL_NO_DISCOVERY", "").lower() in ("1", "true", "yes"):
            return "static (disabled by environment)"

        platform_path = self._get_platform_path()
        if not platform_path:
            return "static (no platform path configured)"
        elif not platform_path.exists():
            return f"static (platform path not found: {platform_path})"
        else:
            return f"dynamic (platform: {platform_path})"

    def _get_platform_path(self) -> Optional[Path]:
        """Get platform-infrastructure path from configuration"""
        if hasattr(self.config, 'platform_infrastructure') and self.config.platform_infrastructure.path:
            return Path(self.config.platform_infrastructure.path)
        return None

    def validate_platform_integration(self) -> Dict[str, any]:
        """Validate platform-infrastructure integration"""
        result = {
            "platform_path_configured": False,
            "platform_path_exists": False,
            "discovery_working": False,
            "provider_count": 0,
            "errors": []
        }

        try:
            platform_path = self._get_platform_path()
            result["platform_path_configured"] = platform_path is not None

            if platform_path:
                result["platform_path_exists"] = platform_path.exists()

                if platform_path.exists():
                    # Test discovery
                    from .stack_discovery import StackDiscovery
                    discovery = StackDiscovery(platform_path)
                    discovery.discover_all_stacks(force_refresh=True)

                    stats = discovery.get_discovery_stats()
                    result["provider_count"] = stats["total_stacks"]
                    result["discovery_working"] = stats["total_stacks"] > 0
                    result["discovery_stats"] = stats

        except Exception as e:
            result["errors"].append(str(e))

        return result
```

#### 3.2 Update Client Manager
**File**: `blackwell/core/client_manager.py`

```python
class ClientManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        # Use dynamic provider matrix
        self.provider_matrix = config_manager.get_provider_matrix()

    def refresh_provider_matrix(self) -> None:
        """Refresh provider matrix (useful after platform changes)"""
        self.provider_matrix = self.config_manager.get_provider_matrix()
```

#### 3.3 Migration Strategy
1. **Parallel Implementation**: Keep existing static matrix as fallback
2. **Gradual Migration**: Update stacks incrementally with metadata
3. **Validation**: Compare dynamic vs static matrices to ensure accuracy
4. **Deprecation**: Remove static matrix after all stacks have metadata

### Phase 4: Enhanced Features

#### 4.1 Stack Recommendation Engine
**File**: `blackwell/core/stack_recommender.py`

```python
from typing import List, Dict, Optional
from pathlib import Path
from .stack_discovery import StackDiscovery
from .dynamic_provider_matrix import DynamicProviderMatrix

class StackRecommender:
    """Recommend optimal stacks based on discovered metadata and user requirements"""

    def __init__(self, provider_matrix: DynamicProviderMatrix):
        self.provider_matrix = provider_matrix
        self.discovery = provider_matrix.discovery

    def recommend_by_budget(self, budget: float, requirements: Optional[Dict] = None) -> List[Dict]:
        """Recommend stacks within budget using real cost data"""
        recommendations = []

        # Get all valid combinations within budget
        for combination in self.provider_matrix.get_recommended_combinations(budget=budget):
            # Add real stack information
            stack_info = self._get_stack_info_for_combination(combination)
            if stack_info:
                combination['stack_info'] = stack_info
                recommendations.append(combination)

        return recommendations

    def recommend_by_complexity(self, max_complexity: str, requirements: Optional[Dict] = None) -> List[Dict]:
        """Recommend stacks by complexity level"""
        return self.provider_matrix.get_recommended_combinations(complexity=max_complexity)

    def recommend_by_use_case(self, use_case: str) -> List[Dict]:
        """Recommend stacks based on specific use cases"""
        use_case_mappings = {
            "blog": {"preferred_ssg": ["jekyll", "eleventy"], "cms_required": True},
            "ecommerce": {"ecommerce_required": True, "preferred_ssg": ["astro", "nextjs"]},
            "marketing": {"preferred_ssg": ["astro", "gatsby"], "cms_preferred": ["contentful", "sanity"]},
            "documentation": {"preferred_ssg": ["jekyll", "eleventy"], "cms_preferred": ["decap"]}
        }

        criteria = use_case_mappings.get(use_case, {})
        return self._filter_recommendations_by_criteria(criteria)

    def _get_stack_info_for_combination(self, combination: Dict) -> Optional[Dict]:
        """Get actual stack implementation info for a provider combination"""
        # Find the actual stack class that implements this combination
        for stack_id, stack_class in self.discovery.discovered_stacks.items():
            metadata = stack_class.get_provider_metadata()
            if self._combination_matches_metadata(combination, metadata):
                return {
                    "stack_class": stack_class.__name__,
                    "module_path": stack_class.__module__,
                    "stack_id": stack_id
                }
        return None

    def _combination_matches_metadata(self, combination: Dict, metadata) -> bool:
        """Check if a provider combination matches stack metadata"""
        # Implementation to match combinations with metadata
        return (
            combination["cms_provider"] == getattr(metadata, "cms_provider", None) and
            combination["ecommerce_provider"] == getattr(metadata, "ecommerce_provider", None) and
            combination["ssg_engine"] == metadata.provider_name
        )
```

#### 4.2 Real-time Validation
**File**: `blackwell/core/stack_validator.py`

```python
from typing import List, Dict, Optional
from .dynamic_provider_matrix import DynamicProviderMatrix

class StackValidator:
    """Validate client configurations against actual stack capabilities"""

    def __init__(self, provider_matrix: DynamicProviderMatrix):
        self.provider_matrix = provider_matrix
        self.discovery = provider_matrix.discovery

    def validate_combination(self, cms: str, ecommerce: str, ssg: str) -> Dict[str, any]:
        """Validate using discovered compatibility metadata"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }

        # Check if combination is supported by any discovered stack
        supporting_stacks = self._find_supporting_stacks(cms, ecommerce, ssg)

        if not supporting_stacks:
            validation_result["valid"] = False
            validation_result["errors"].append(
                f"No stack implementation found for combination: {cms}/{ecommerce}/{ssg}"
            )

        # Add compatibility warnings
        compatibility_issues = self._check_compatibility_issues(cms, ecommerce, ssg)
        validation_result["warnings"].extend(compatibility_issues)

        return validation_result

    def validate_client_config(self, client_config: Dict) -> Dict[str, any]:
        """Validate complete client configuration"""
        return self.validate_combination(
            client_config.get("cms_provider"),
            client_config.get("ecommerce_provider"),
            client_config.get("ssg_engine")
        )

    def _find_supporting_stacks(self, cms: str, ecommerce: str, ssg: str) -> List[str]:
        """Find stack implementations that support the given combination"""
        supporting_stacks = []

        for stack_id, stack_class in self.discovery.discovered_stacks.items():
            if hasattr(stack_class, 'get_provider_metadata'):
                metadata = stack_class.get_provider_metadata()
                if self._stack_supports_combination(metadata, cms, ecommerce, ssg):
                    supporting_stacks.append(stack_id)

        return supporting_stacks

    def _stack_supports_combination(self, metadata, cms: str, ecommerce: str, ssg: str) -> bool:
        """Check if a stack's metadata supports the given combination"""
        # Implementation depends on how metadata is structured
        # This is a simplified version
        return (
            (not cms or cms in getattr(metadata, 'compatible_cms', [])) and
            (not ecommerce or ecommerce in getattr(metadata, 'compatible_ecommerce', [])) and
            metadata.provider_name == ssg
        )
```

## 📊 Implementation Timeline

### Week 1: Foundation (Start Small & Safe)
**🎯 Goal: Prove the concept with minimal risk**
- [ ] Create base metadata classes (`stack_metadata.py`, `metadata_mixin.py`) with version support
- [ ] **Start with 2 stacks only**: Update Jekyll and Hugo stacks with metadata as proof of concept
- [ ] Implement safe discovery system with CDK side-effect prevention
- [ ] Create basic CLI command: `blackwell list providers --discovery-mode`
- [ ] **Deliverable**: CLI can safely discover and list 2 providers without importing CDK resources

### Week 2: Discovery System & Caching
**🎯 Goal: Build production-ready discovery with performance**
- [ ] Complete stack discovery engine with caching (`~/.blackwell_cache/providers.json`)
- [ ] Add version compatibility checking and error handling
- [ ] Build dynamic provider matrix with fallback to static matrix
- [ ] Add CLI flags: `--no-discovery` and `BLACKWELL_NO_DISCOVERY` environment variable
- [ ] **Deliverable**: Discovery works for all stacks with <200ms performance after first run

### Week 3: Integration & Migration
**🎯 Goal: Seamless CLI integration with backward compatibility**
- [ ] Update CLI configuration manager with discovery mode diagnostics
- [ ] Add `blackwell doctor` integration checks for platform-infrastructure
- [ ] Migrate remaining stacks incrementally (3-4 per day to avoid breaking changes)
- [ ] Add discovery logging and migration tracking
- [ ] **Deliverable**: All existing CLI functionality works unchanged

### Week 4: Enhancement & Validation
**🎯 Goal: Advanced features and cleanup**
- [ ] Implement stack recommendation engine using discovered metadata
- [ ] Add real-time combination validation
- [ ] Create `blackwell providers refresh` command to clear cache
- [ ] Remove static matrix dependencies where safe
- [ ] **Deliverable**: CLI becomes intelligent interface to platform capabilities

## 🎯 Success Criteria

### Technical Goals
- [ ] CLI automatically discovers new stacks added to platform-infrastructure
- [ ] Provider metadata perfectly matches actual stack capabilities
- [ ] Zero manual synchronization required between CLI and platform
- [ ] Cost calculations based on real resource definitions from stacks
- [ ] Compatibility validation uses actual implementation constraints

### Quality Goals
- [ ] 100% test coverage for discovery system
- [ ] No breaking changes to existing CLI functionality
- [ ] Graceful fallback when platform-infrastructure unavailable
- [ ] Performance impact < 200ms for provider matrix initialization

### User Experience Goals
- [ ] Transparent migration - users see no difference in CLI behavior
- [ ] Enhanced accuracy in recommendations and cost estimates
- [ ] Better error messages when invalid combinations are attempted

## 🔄 Maintenance Benefits

### Immediate Benefits
1. **Automatic Discovery**: New stacks appear in CLI without manual registration
2. **Perfect Synchronization**: CLI always reflects platform capabilities
3. **Single Source of Truth**: Stack implementations contain all provider information
4. **Enhanced Accuracy**: Recommendations based on actual deployment capabilities

### Long-term Benefits
1. **Reduced Technical Debt**: Eliminates duplicate metadata maintenance
2. **Improved Developer Experience**: New stack developers only need to add metadata once
3. **Better Testing**: Can validate CLI behavior against actual stack implementations
4. **Easier Extensions**: New provider types automatically supported

## 🚨 Risk Mitigation

### Technical Risks
- **Import Issues**: Use careful module loading with error handling
- **Performance Impact**: Cache discovered stacks and implement lazy loading
- **Platform Dependencies**: Maintain static fallback for when platform unavailable

### Migration Risks
- **Breaking Changes**: Implement behind feature flag initially
- **Data Inconsistency**: Validate dynamic matrix against static during transition
- **Rollback Plan**: Keep static matrix available for quick rollback

## 🏗️ Recommended Directory Structure

To keep the unified system organized and maintainable:

```
platform-infrastructure/
├── shared/
│   ├── base/
│   │   ├── stack_metadata.py          # Pydantic metadata models
│   │   ├── metadata_mixin.py          # Stack metadata interface
│   │   └── __init__.py
│   └── provider_registry.json         # Auto-generated cache (optional)
│
├── stacks/
│   ├── ssg/
│   │   ├── hugo_stack.py              # Hugo implementation + metadata
│   │   ├── jekyll_stack.py            # Jekyll implementation + metadata
│   │   ├── astro_stack.py             # Astro implementation + metadata
│   │   └── ...
│   ├── cms/
│   │   ├── decap_cms_stack.py         # Decap implementation + metadata
│   │   ├── tina_cms_stack.py          # Tina implementation + metadata
│   │   └── ...
│   └── ecommerce/
│       ├── snipcart_stack.py          # Snipcart implementation + metadata
│       ├── foxy_stack.py              # Foxy implementation + metadata
│       └── ...

blackwell-cli/
├── blackwell/
│   └── core/
│       ├── dynamic_provider_matrix.py  # Dynamic matrix using discovery
│       ├── stack_discovery.py          # Safe stack introspection
│       ├── stack_recommender.py        # AI-assisted recommendations
│       ├── stack_validator.py          # Real-time validation
│       └── provider_matrix.py          # Legacy static matrix (fallback)
│
└── ~/.blackwell_cache/
    └── providers.json                  # Cached discovery results
```

## 🚨 Critical Safety Considerations

### 1. CDK Import Side Effects Prevention
**Problem**: CDK stacks often have resource definitions that trigger AWS SDK calls during import.

**Solutions**:
- Use `importlib.util` with controlled module loading
- Never instantiate stack classes, only access static metadata methods
- Validate `issubclass(obj, StackMetadataMixin)` before accessing metadata
- Wrap all imports in try/except with proper logging

### 2. Version Compatibility Management
**Problem**: CLI and platform metadata schemas may evolve independently.

**Solutions**:
- Add `version` field to all metadata (default: "1.0.0")
- Implement semantic version checking in discovery
- Log compatibility warnings for older metadata
- Graceful degradation for unsupported versions

### 3. Performance & Caching Strategy
**Problem**: Dynamic discovery could slow down CLI commands.

**Solutions**:
- Cache to `~/.blackwell_cache/providers.json` with mtime-based invalidation
- Target <200ms for provider matrix initialization after first run
- Implement lazy loading where possible
- Add `--refresh-cache` flag for development

### 4. Error Resilience & Fallback
**Problem**: Discovery failures should not break CLI functionality.

**Solutions**:
- Always maintain static matrix as fallback
- Log discovery failures but continue with static data
- Add `BLACKWELL_NO_DISCOVERY` environment variable
- Implement graceful degradation with user warnings

## 📋 CLI Command Enhancements

Add these commands to support the unified system:

```bash
# Discovery diagnostics
blackwell doctor --check-discovery
blackwell list providers --discovery-mode
blackwell providers refresh --clear-cache

# Development/debugging
BLACKWELL_NO_DISCOVERY=1 blackwell list providers  # Force static mode
blackwell list providers --verbose                  # Show discovery process
blackwell config show discovery-status              # Current discovery mode
```

## 🧪 Testing Strategy

### Discovery Safety Tests
```python
def test_discovery_no_cdk_side_effects():
    """Ensure discovery doesn't trigger CDK resource creation"""
    # Mock AWS SDK calls and ensure none are made during discovery

def test_malformed_stack_handling():
    """Test graceful handling of stacks with syntax errors"""
    # Ensure discovery continues even if some stacks fail to import

def test_metadata_version_compatibility():
    """Test handling of different metadata schema versions"""
    # Ensure forward/backward compatibility works
```

### Performance Tests
```python
def test_discovery_performance():
    """Ensure discovery completes within performance targets"""
    # Target: <200ms after first run (with caching)

def test_cache_invalidation():
    """Test cache invalidation when stack files change"""
    # Ensure cache updates when platform-infrastructure changes
```

## 📝 Implementation Notes & Edge Cases

### Edge Case: Circular Dependencies
**Issue**: Stack imports might create circular dependencies during discovery.
**Solution**: Use `importlib.util.spec_from_file_location` for isolated module loading.

### Edge Case: Multiple Stacks Same Provider
**Issue**: Multiple stack classes might claim the same provider name.
**Solution**: Last discovered wins, with warning logged about conflicts.

### Edge Case: Platform Path Changes
**Issue**: platform-infrastructure path might change between CLI runs.
**Solution**: Store platform path in cache and invalidate if path changes.

### Edge Case: Partial Discovery Failure
**Issue**: Some stacks discoverable, others fail.
**Solution**: Continue with partial results, merge with static fallback for missing providers.

## 📊 Migration Logging & Monitoring

Track the migration progress with structured logging:

```python
# Log during discovery
logger.info("Discovery started", extra={
    "platform_path": str(platform_path),
    "cache_available": cache_exists,
    "stack_files_found": len(stack_files)
})

# Log provider registration
logger.info("Provider registered", extra={
    "provider_type": metadata.provider_type,
    "provider_name": metadata.provider_name,
    "stack_class": stack_class.__name__,
    "source": "discovery"  # vs "static"
})

# Log fallback usage
logger.warning("Using static matrix fallback", extra={
    "reason": "discovery_failed",
    "error": str(exception),
    "providers_missing": missing_providers
})
```

## 🎯 Success Metrics

### Week 1 Success Criteria
- [ ] 2 stacks (Jekyll, Hugo) successfully discovered without CDK side effects
- [ ] `blackwell list providers --discovery-mode` shows both static and dynamic providers
- [ ] Zero breaking changes to existing CLI functionality

### Week 2 Success Criteria
- [ ] All 7 SSG providers discoverable from platform-infrastructure
- [ ] Cache reduces discovery time to <200ms after first run
- [ ] CLI gracefully handles discovery failures with fallback

### Week 3 Success Criteria
- [ ] All provider types (CMS, e-commerce, SSG) use discovered metadata
- [ ] `blackwell doctor` validates platform-infrastructure integration
- [ ] Migration tracking shows 0% static matrix usage

### Week 4 Success Criteria
- [ ] CLI recommendations use real platform capabilities
- [ ] Client validation uses discovered compatibility rules
- [ ] Documentation updated for new unified architecture

---

## 🏆 Final Architecture Benefits

This unified system transforms your CLI from a **declarative** tool (requires manual provider definitions) into a **reflective** tool (automatically mirrors platform capabilities). The key architectural improvement:

**Before**: CLI Provider Matrix ≠ Platform Stack Factories (drift risk)
**After**: CLI Provider Matrix = f(Platform Stack Factories) (perfect sync)

The CLI becomes a live reflection of your infrastructure capabilities, closing the feedback loop between development tools and deployment logic. This is enterprise-grade architecture modernization that eliminates the "two-source drift" problem permanently.