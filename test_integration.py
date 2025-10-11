#!/usr/bin/env python3
"""
Integration Test Script for Platform-Infrastructure Integration

Tests the complete Stack Unification Plan implementation including:
- Safe import patterns and graceful fallback
- Dynamic provider matrix functionality
- Platform metadata transformation
- CLI command registration
- Error handling and resilience
"""

import sys
import traceback
from pathlib import Path

def test_safe_imports():
    """Test that safe import patterns work correctly."""
    print("🧪 Testing Safe Import Patterns...")

    try:
        from blackwell.core.platform_integration import (
            is_platform_available,
            get_platform_metadata,
            get_integration_status
        )

        print("  ✅ Platform integration module imports successfully")

        # Test availability check
        platform_available = is_platform_available()
        print(f"  📊 Platform available: {platform_available}")

        # Test metadata retrieval
        metadata = get_platform_metadata()
        print(f"  📊 Metadata entries: {len(metadata)}")

        # Test integration status
        status = get_integration_status()
        print(f"  📊 Integration mode: {status.get('integration_mode', 'unknown')}")

        return True

    except Exception as e:
        print(f"  ❌ Safe import test failed: {e}")
        return False

def test_dynamic_provider_matrix():
    """Test DynamicProviderMatrix functionality."""
    print("\n🧪 Testing Dynamic Provider Matrix...")

    try:
        from blackwell.core.dynamic_provider_matrix import DynamicProviderMatrix

        print("  ✅ DynamicProviderMatrix imports successfully")

        # Create instance
        matrix = DynamicProviderMatrix()

        # Test data source
        data_source = matrix.get_data_source()
        print(f"  📊 Data source: {data_source}")

        # Test provider counts
        cms_providers = matrix.list_all_providers()["cms"]
        ecommerce_providers = matrix.list_all_providers()["ecommerce"]
        ssg_engines = matrix.list_all_providers()["ssg"]

        print(f"  📊 CMS providers: {len(cms_providers)}")
        print(f"  📊 E-commerce providers: {len(ecommerce_providers)}")
        print(f"  📊 SSG engines: {len(ssg_engines)}")

        # Test enhanced features if available
        if hasattr(matrix, 'get_platform_status'):
            status = matrix.get_platform_status()
            print(f"  📊 Platform metadata count: {status.get('platform_metadata_count', 0)}")

        return True

    except Exception as e:
        print(f"  ❌ DynamicProviderMatrix test failed: {e}")
        traceback.print_exc()
        return False

def test_static_fallback():
    """Test fallback to static provider matrix."""
    print("\n🧪 Testing Static Fallback...")

    try:
        from blackwell.core.provider_matrix import ProviderMatrix

        print("  ✅ Static ProviderMatrix imports successfully")

        # Create static instance
        matrix = ProviderMatrix()

        # Test provider retrieval
        providers = matrix.list_all_providers()

        print(f"  📊 Static CMS providers: {len(providers['cms'])}")
        print(f"  📊 Static E-commerce providers: {len(providers['ecommerce'])}")
        print(f"  📊 Static SSG engines: {len(providers['ssg'])}")

        return True

    except Exception as e:
        print(f"  ❌ Static fallback test failed: {e}")
        return False

def test_config_manager_integration():
    """Test ConfigManager with platform integration."""
    print("\n🧪 Testing ConfigManager Integration...")

    try:
        from blackwell.core.config_manager import ConfigManager

        print("  ✅ ConfigManager imports successfully")

        # Create config manager instance
        config_manager = ConfigManager(verbose=False)

        # Test get_provider_matrix method
        provider_matrix = config_manager.get_provider_matrix()

        data_source = "unknown"
        if hasattr(provider_matrix, 'get_data_source'):
            data_source = provider_matrix.get_data_source()
        elif hasattr(provider_matrix, '__class__'):
            data_source = provider_matrix.__class__.__name__

        print(f"  📊 Provider matrix type: {data_source}")

        # Test platform integration status
        status = config_manager.get_platform_integration_status()
        print(f"  📊 Config path available: {status.get('config_path_available', False)}")
        print(f"  📊 Platform available: {status.get('platform_available', False)}")
        print(f"  📊 Force static mode: {status.get('force_static_mode', False)}")

        return True

    except Exception as e:
        print(f"  ❌ ConfigManager test failed: {e}")
        traceback.print_exc()
        return False

def test_cli_commands():
    """Test that CLI commands are properly registered."""
    print("\n🧪 Testing CLI Command Registration...")

    try:
        from blackwell.commands import platform

        print("  ✅ Platform command module imports successfully")

        # Check that the Typer app exists
        if hasattr(platform, 'app'):
            print("  ✅ Platform command app found")

            # Try to inspect commands (this might not work in all environments)
            try:
                commands = platform.app.registered_commands
                print(f"  📊 Registered commands: {len(commands) if commands else 'unknown'}")
            except:
                print("  📊 Command introspection not available (normal)")
        else:
            print("  ❌ Platform command app not found")
            return False

        return True

    except Exception as e:
        print(f"  ❌ CLI command test failed: {e}")
        return False

def test_transformation_functions():
    """Test metadata transformation functions."""
    print("\n🧪 Testing Metadata Transformation...")

    try:
        from blackwell.core.platform_integration import transform_to_cli_format

        print("  ✅ Transformation functions import successfully")

        # Test with empty metadata (should return empty structure)
        empty_result = transform_to_cli_format({})
        expected_keys = {"cms", "ecommerce", "ssg"}

        if set(empty_result.keys()) == expected_keys:
            print("  ✅ Empty metadata transformation correct")
        else:
            print(f"  ❌ Empty metadata keys incorrect: {empty_result.keys()}")
            return False

        # Test with sample metadata (if platform available)
        from blackwell.core.platform_integration import get_platform_metadata
        metadata = get_platform_metadata()

        if metadata:
            result = transform_to_cli_format(metadata)
            print(f"  📊 Transformed CMS providers: {len(result['cms'])}")
            print(f"  📊 Transformed E-commerce providers: {len(result['ecommerce'])}")
            print(f"  📊 Transformed SSG engines: {len(result['ssg'])}")
        else:
            print("  📊 No platform metadata available for transformation test")

        return True

    except Exception as e:
        print(f"  ❌ Transformation test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🚀 Platform-Infrastructure Integration Test Suite")
    print("=" * 60)

    tests = [
        ("Safe Import Patterns", test_safe_imports),
        ("Dynamic Provider Matrix", test_dynamic_provider_matrix),
        ("Static Fallback", test_static_fallback),
        ("ConfigManager Integration", test_config_manager_integration),
        ("CLI Command Registration", test_cli_commands),
        ("Metadata Transformation", test_transformation_functions),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  💥 Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}")
        if success:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Stack Unification Plan implementation is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())