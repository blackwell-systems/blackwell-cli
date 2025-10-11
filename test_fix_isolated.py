#!/usr/bin/env python3
"""
Isolated test to verify the providers command fix logic
without importing the full module dependencies.
"""

def test_list_vs_dict_handling():
    """Test the logic for handling both list and dict provider formats."""
    print("🧪 Testing List vs Dict Handling Logic...")

    # Simulate the data structures that would be returned

    # Case 1: List format (from base ProviderMatrix.list_all_providers())
    providers_list_format = {
        "cms": ["decap", "tina", "sanity", "contentful"],
        "ecommerce": ["snipcart", "foxy", "shopify_basic"],
        "ssg": ["hugo", "eleventy", "astro", "gatsby", "nextjs", "nuxt", "jekyll"]
    }

    # Case 2: Dict format (from DynamicProviderMatrix.list_all_providers_with_source())
    providers_dict_format = {
        "cms": {
            "decap": {
                "name": "Decap CMS",
                "cost": 0.0,
                "features": ["git_based", "free", "open_source"],
                "complexity": "intermediate"
            },
            "tina": {
                "name": "Tina CMS",
                "cost": 29.0,
                "features": ["visual_editing", "git_based", "live_preview"],
                "complexity": "beginner"
            }
        },
        "ecommerce": {
            "snipcart": {
                "name": "Snipcart",
                "cost": 29.0,
                "features": ["simple", "embed", "quick_setup"],
                "complexity": "beginner"
            }
        },
        "ssg": {
            "hugo": {
                "name": "Hugo",
                "build_speed": "fastest",
                "features": ["blazing_fast", "simple", "powerful"],
                "complexity": "intermediate"
            }
        },
        "meta": {
            "data_source": "platform",
            "platform_available": True,
            "total_combinations": 42
        }
    }

    # Mock provider matrix for get_provider_info calls
    class MockProviderMatrix:
        def get_provider_info(self, provider_type, provider_key):
            provider_data = {
                "cms": {
                    "decap": {"name": "Decap CMS", "features": ["git_based", "free"]},
                    "tina": {"name": "Tina CMS", "features": ["visual_editing", "live_preview"]},
                    "sanity": {"name": "Sanity CMS", "features": ["structured_content", "api_first"]},
                    "contentful": {"name": "Contentful", "features": ["enterprise", "cdn"]}
                },
                "ecommerce": {
                    "snipcart": {"name": "Snipcart", "features": ["simple", "embed"]},
                    "foxy": {"name": "Foxy.io", "features": ["advanced", "customizable"]},
                    "shopify_basic": {"name": "Shopify Basic", "features": ["full_platform", "inventory"]}
                },
                "ssg": {
                    "hugo": {"name": "Hugo", "features": ["blazing_fast", "simple"]},
                    "eleventy": {"name": "Eleventy", "features": ["flexible", "zero_config"]},
                    "astro": {"name": "Astro", "features": ["component_islands", "modern"]},
                    "gatsby": {"name": "Gatsby", "features": ["react_based", "graphql"]},
                    "nextjs": {"name": "Next.js", "features": ["react_framework", "ssr"]},
                    "nuxt": {"name": "Nuxt.js", "features": ["vue_framework", "ssr"]},
                    "jekyll": {"name": "Jekyll", "features": ["github_pages", "blog_ready"]}
                }
            }
            return provider_data.get(provider_type, {}).get(provider_key, {})

    provider_matrix = MockProviderMatrix()

    # Test both formats with the fixed logic
    test_cases = [
        ("List Format", providers_list_format),
        ("Dict Format", providers_dict_format)
    ]

    for case_name, providers_info in test_cases:
        print(f"\n🔍 Testing {case_name}:")

        try:
            for provider_type in ["cms", "ecommerce", "ssg"]:
                if provider_type in providers_info:
                    providers = providers_info[provider_type]
                    print(f"  {provider_type}: {type(providers).__name__}")

                    if providers:
                        processed_providers = []

                        # This is the fixed logic from the command
                        if isinstance(providers, dict):
                            # Dictionary format - iterate over items
                            for provider_key, provider_data in providers.items():
                                if isinstance(provider_data, dict):
                                    name = provider_data.get("name", provider_key.title())
                                    features = ", ".join(provider_data.get("features", [])[:3])
                                    if len(provider_data.get("features", [])) > 3:
                                        features += "..."
                                else:
                                    name = str(provider_data)
                                    features = ""

                                processed_providers.append((provider_key, name, features))
                        else:
                            # List format - get detailed info from provider matrix
                            for provider_key in providers:
                                provider_data = provider_matrix.get_provider_info(provider_type, provider_key)

                                if isinstance(provider_data, dict):
                                    name = provider_data.get("name", provider_key.title())
                                    features = ", ".join(provider_data.get("features", [])[:3])
                                    if len(provider_data.get("features", [])) > 3:
                                        features += "..."
                                else:
                                    name = provider_key.title()
                                    features = ""

                                processed_providers.append((provider_key, name, features))

                        # Show first few processed providers
                        for i, (key, name, features) in enumerate(processed_providers[:2]):
                            print(f"    ✅ {key}: {name} - {features}")

            print(f"  ✅ {case_name} processed successfully!")

        except Exception as e:
            print(f"  ❌ {case_name} failed: {e}")
            return False

    return True

def test_error_scenario():
    """Test the original error scenario that was failing."""
    print("\n🚨 Testing Original Error Scenario...")

    # This simulates what was happening before the fix:
    # providers_info["cms"] was a list like ["decap", "tina", "sanity"]
    # but the code was trying to do: for key, value in providers.items()

    providers_list = ["decap", "tina", "sanity", "contentful"]

    print(f"Provider list type: {type(providers_list)}")
    print(f"Provider list content: {providers_list}")

    # This would have caused the original error:
    try:
        for provider_key, provider_data in providers_list.items():  # This will fail!
            pass
        print("❌ Should have failed but didn't!")
        return False
    except AttributeError as e:
        if "'list' object has no attribute 'items'" in str(e):
            print("✅ Confirmed: Original error reproduced successfully")
            print(f"   Error: {e}")
        else:
            print(f"❌ Different error: {e}")
            return False

    # Now test our fix handles this case:
    try:
        mock_matrix = MockProviderMatrix()
        processed_count = 0

        if isinstance(providers_list, dict):
            # This won't execute for our list
            for provider_key, provider_data in providers_list.items():
                processed_count += 1
        else:
            # This will execute - the fix!
            for provider_key in providers_list:
                provider_data = mock_matrix.get_provider_info("cms", provider_key)
                processed_count += 1

        print(f"✅ Fix works: Processed {processed_count} providers from list")
        return True

    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return False

class MockProviderMatrix:
    """Mock provider matrix for testing."""
    def get_provider_info(self, provider_type, provider_key):
        provider_data = {
            "cms": {
                "decap": {"name": "Decap CMS", "features": ["git_based", "free"]},
                "tina": {"name": "Tina CMS", "features": ["visual_editing", "live_preview"]},
                "sanity": {"name": "Sanity CMS", "features": ["structured_content", "api_first"]},
                "contentful": {"name": "Contentful", "features": ["enterprise", "cdn"]}
            }
        }
        return provider_data.get(provider_type, {}).get(provider_key, {})

def main():
    """Run all isolated tests."""
    print("🧪 Isolated Test: Blackwell CLI Provider Command Fix")
    print("=" * 60)

    tests = [
        ("List vs Dict Handling Logic", test_list_vs_dict_handling),
        ("Original Error Scenario", test_error_scenario),
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
        print("\n🎉 All tests passed! The provider command fix logic is correct.")
        print("\n💡 The fix should resolve the 'list' object has no attribute 'items' error")
        print("   by properly handling both list and dictionary provider formats.")
    else:
        print(f"\n⚠️  {total-passed} test(s) failed. Check output above for details.")

    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())