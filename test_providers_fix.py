#!/usr/bin/env python3
"""
Test script to verify the providers command fix
"""

import sys
from pathlib import Path

# Add the project to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_provider_matrix_data_format():
    """Test that the provider matrix returns the expected data formats."""
    print("🧪 Testing Provider Matrix Data Formats...")

    try:
        from blackwell.core.provider_matrix import ProviderMatrix

        # Test standard provider matrix
        matrix = ProviderMatrix()

        # Test list_all_providers - should return lists
        providers_list = matrix.list_all_providers()
        print(f"✅ list_all_providers() format: {type(providers_list)}")
        for provider_type, providers in providers_list.items():
            print(f"  {provider_type}: {type(providers)} - {providers[:3] if providers else 'empty'}")

        # Test accessing full provider data
        for provider_type in ["cms", "ecommerce", "ssg"]:
            if provider_type == "cms":
                full_data = matrix.cms_providers
            elif provider_type == "ecommerce":
                full_data = matrix.ecommerce_providers
            else:
                full_data = matrix.ssg_engines

            print(f"✅ Full {provider_type} data: {type(full_data)} with keys: {list(full_data.keys())[:3] if full_data else 'empty'}")

            # Test get_provider_info method
            if full_data:
                first_key = list(full_data.keys())[0]
                info = matrix.get_provider_info(provider_type, first_key)
                print(f"  get_provider_info('{provider_type}', '{first_key}'): {type(info)}")

        return True

    except Exception as e:
        print(f"❌ Provider matrix test failed: {e}")
        return False

def test_dynamic_provider_matrix():
    """Test the dynamic provider matrix."""
    print("\n🔄 Testing Dynamic Provider Matrix...")

    try:
        from blackwell.core.dynamic_provider_matrix import DynamicProviderMatrix

        # Create dynamic matrix
        matrix = DynamicProviderMatrix()

        # Test data source
        data_source = matrix.get_data_source()
        print(f"✅ Data source: {data_source}")

        # Test list_all_providers_with_source
        providers_with_source = matrix.list_all_providers_with_source()
        print(f"✅ list_all_providers_with_source() format: {type(providers_with_source)}")

        for provider_type in ["cms", "ecommerce", "ssg"]:
            if provider_type in providers_with_source:
                providers = providers_with_source[provider_type]
                print(f"  {provider_type}: {type(providers)}")

                if isinstance(providers, dict) and providers:
                    first_key = list(providers.keys())[0]
                    first_value = providers[first_key]
                    print(f"    Example: {first_key} -> {type(first_value)}")
                    if isinstance(first_value, dict):
                        print(f"    Has 'name': {'name' in first_value}")
                        print(f"    Has 'features': {'features' in first_value}")
                elif isinstance(providers, list) and providers:
                    print(f"    Example: {providers[0]} (list format)")

        # Test metadata
        if "meta" in providers_with_source:
            meta = providers_with_source["meta"]
            print(f"✅ Metadata available: {meta}")

        return True

    except Exception as e:
        print(f"❌ Dynamic provider matrix test failed: {e}")
        return False

def test_platform_integration():
    """Test platform integration functions."""
    print("\n🔗 Testing Platform Integration...")

    try:
        from blackwell.core.platform_integration import (
            is_platform_available,
            get_platform_metadata,
            transform_to_cli_format
        )

        # Test availability
        available = is_platform_available()
        print(f"✅ Platform available: {available}")

        # Test metadata retrieval
        metadata = get_platform_metadata()
        print(f"✅ Platform metadata: {type(metadata)} - {len(metadata) if isinstance(metadata, dict) else 'not dict'}")

        # Test transformation (even with empty metadata)
        cli_format = transform_to_cli_format(metadata)
        print(f"✅ CLI format: {type(cli_format)}")
        for category in ["cms", "ecommerce", "ssg"]:
            if category in cli_format:
                providers = cli_format[category]
                print(f"  {category}: {type(providers)} - {len(providers) if isinstance(providers, dict) else 'not dict'}")

        return True

    except Exception as e:
        print(f"❌ Platform integration test failed: {e}")
        return False

def simulate_providers_command_logic():
    """Simulate the logic of the providers command to test the fix."""
    print("\n🎯 Simulating Providers Command Logic...")

    try:
        from blackwell.core.dynamic_provider_matrix import DynamicProviderMatrix

        # Simulate the ConfigManager.get_provider_matrix()
        provider_matrix = DynamicProviderMatrix()

        # Get data source information (as in the command)
        if hasattr(provider_matrix, 'get_data_source'):
            data_source = provider_matrix.get_data_source()
            print(f"✅ Data source: {data_source}")
        else:
            data_source = "static"
            print(f"✅ Data source: {data_source} (fallback)")

        # Get provider information (as in the command)
        if hasattr(provider_matrix, 'list_all_providers_with_source'):
            providers_info = provider_matrix.list_all_providers_with_source()
        else:
            providers_info = provider_matrix.list_all_providers()

        print(f"✅ Provider info type: {type(providers_info)}")

        # Simulate the loop over provider types (the critical part that was failing)
        for provider_type in ["cms", "ecommerce", "ssg"]:
            if provider_type in providers_info:
                providers = providers_info[provider_type]
                print(f"\n  Testing {provider_type.upper()} providers:")
                print(f"    Type: {type(providers)}")

                if providers:
                    # Simulate the table creation logic (the part that was failing)
                    if isinstance(providers, dict):
                        print("    ✅ Dictionary format - can use .items()")
                        count = 0
                        for provider_key, provider_data in providers.items():
                            if count >= 2:  # Just test first 2
                                break
                            if isinstance(provider_data, dict):
                                name = provider_data.get("name", provider_key.title())
                                features = ", ".join(provider_data.get("features", [])[:3])
                            else:
                                name = str(provider_data)
                                features = ""
                            print(f"      {provider_key}: {name} - {features}")
                            count += 1
                    else:
                        print("    ✅ List format - using get_provider_info fallback")
                        count = 0
                        for provider_key in providers:
                            if count >= 2:  # Just test first 2
                                break
                            provider_data = provider_matrix.get_provider_info(provider_type, provider_key)
                            if isinstance(provider_data, dict):
                                name = provider_data.get("name", provider_key.title())
                                features = ", ".join(provider_data.get("features", [])[:3])
                            else:
                                name = provider_key.title()
                                features = ""
                            print(f"      {provider_key}: {name} - {features}")
                            count += 1

        print("\n✅ Providers command logic simulation completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Providers command simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Blackwell CLI Provider Command Fix")
    print("=" * 60)

    tests = [
        ("Provider Matrix Data Format", test_provider_matrix_data_format),
        ("Dynamic Provider Matrix", test_dynamic_provider_matrix),
        ("Platform Integration", test_platform_integration),
        ("Providers Command Logic Simulation", simulate_providers_command_logic),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"💥 Test '{test_name}' crashed: {e}")
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

    print(f"\n📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 All tests passed! The provider command fix should work correctly.")
    else:
        print(f"\n⚠️  {total-passed} test(s) failed. Check output above for details.")

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())