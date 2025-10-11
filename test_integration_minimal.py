#!/usr/bin/env python3
"""
Minimal Integration Test for Platform-Infrastructure Integration

Tests core integration logic without requiring full dependency installation.
Focuses on validating the implementation patterns and logic.
"""

import sys
import os
from pathlib import Path

# Add the project to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_file_structure():
    """Test that all required files were created correctly."""
    print("📁 Testing File Structure...")

    required_files = [
        "blackwell/core/platform_integration.py",
        "blackwell/core/dynamic_provider_matrix.py",
        "blackwell/commands/platform.py"
    ]

    modified_files = [
        "blackwell/core/config_manager.py",
        "blackwell/main.py"
    ]

    all_present = True

    for file_path in required_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"  ✅ Created: {file_path}")
        else:
            print(f"  ❌ Missing: {file_path}")
            all_present = False

    for file_path in modified_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"  ✅ Modified: {file_path}")
        else:
            print(f"  ❌ Missing: {file_path}")
            all_present = False

    return all_present

def test_safe_import_pattern():
    """Test that the safe import pattern is implemented correctly."""
    print("\n🛡️ Testing Safe Import Pattern...")

    platform_integration_file = Path("blackwell/core/platform_integration.py")

    if not platform_integration_file.exists():
        print("  ❌ platform_integration.py not found")
        return False

    content = platform_integration_file.read_text()

    # Check for safe import pattern
    patterns_to_check = [
        "try:",
        "from platform_infrastructure.shared.factories.platform_stack_factory import PlatformStackFactory",
        "PLATFORM_AVAILABLE = True",
        "except ImportError",
        "PlatformStackFactory = None",
        "PLATFORM_AVAILABLE = False"
    ]

    all_patterns_found = True
    for pattern in patterns_to_check:
        if pattern in content:
            print(f"  ✅ Found safe import pattern: {pattern[:50]}...")
        else:
            print(f"  ❌ Missing pattern: {pattern}")
            all_patterns_found = False

    # Check for graceful fallback functions
    key_functions = [
        "def is_platform_available()",
        "def get_platform_metadata()",
        "def transform_to_cli_format(",
        "def get_integration_status()"
    ]

    for func in key_functions:
        if func in content:
            print(f"  ✅ Found function: {func}")
        else:
            print(f"  ❌ Missing function: {func}")
            all_patterns_found = False

    return all_patterns_found

def test_dynamic_provider_matrix_structure():
    """Test the DynamicProviderMatrix class structure."""
    print("\n🔄 Testing DynamicProviderMatrix Structure...")

    dynamic_matrix_file = Path("blackwell/core/dynamic_provider_matrix.py")

    if not dynamic_matrix_file.exists():
        print("  ❌ dynamic_provider_matrix.py not found")
        return False

    content = dynamic_matrix_file.read_text()

    # Check for key class and method definitions
    required_elements = [
        "class DynamicProviderMatrix(ProviderMatrix):",
        "def __init__(self):",
        "def _load_from_platform(self):",
        "def get_data_source(self):",
        "def refresh_from_platform(self):",
        "def get_intelligent_recommendations(",
        "def get_platform_status(self):"
    ]

    all_found = True
    for element in required_elements:
        if element in content:
            print(f"  ✅ Found: {element}")
        else:
            print(f"  ❌ Missing: {element}")
            all_found = False

    # Check for proper imports
    imports_to_check = [
        "from .provider_matrix import ProviderMatrix",
        "from .platform_integration import"
    ]

    for import_stmt in imports_to_check:
        if import_stmt in content:
            print(f"  ✅ Found import: {import_stmt}")
        else:
            print(f"  ❌ Missing import: {import_stmt}")
            all_found = False

    return all_found

def test_config_manager_enhancements():
    """Test ConfigManager enhancements."""
    print("\n⚙️ Testing ConfigManager Enhancements...")

    config_manager_file = Path("blackwell/core/config_manager.py")

    if not config_manager_file.exists():
        print("  ❌ config_manager.py not found")
        return False

    content = config_manager_file.read_text()

    # Check for new imports
    new_imports = [
        "from .dynamic_provider_matrix import DynamicProviderMatrix",
        "from .platform_integration import is_platform_available, get_integration_status"
    ]

    imports_found = True
    for import_stmt in new_imports:
        if import_stmt in content:
            print(f"  ✅ Added import: {import_stmt}")
        else:
            print(f"  ❌ Missing import: {import_stmt}")
            imports_found = False

    # Check for new methods
    new_methods = [
        "def get_provider_matrix(self):",
        "def get_platform_integration_status(self):",
        "def refresh_platform_metadata(self):",
        "def enable_platform_integration(self):",
        "def disable_platform_integration(self):",
        "def show_platform_status(self):"
    ]

    methods_found = True
    for method in new_methods:
        if method in content:
            print(f"  ✅ Added method: {method}")
        else:
            print(f"  ❌ Missing method: {method}")
            methods_found = False

    # Check for new configuration fields
    config_fields = [
        "force_static_mode: bool",
        "enable_live_metadata: bool",
        "cache_duration: int"
    ]

    fields_found = True
    for field in config_fields:
        if field in content:
            print(f"  ✅ Added config field: {field}")
        else:
            print(f"  ❌ Missing config field: {field}")
            fields_found = False

    return imports_found and methods_found and fields_found

def test_cli_command_structure():
    """Test CLI command structure."""
    print("\n💻 Testing CLI Command Structure...")

    platform_cmd_file = Path("blackwell/commands/platform.py")

    if not platform_cmd_file.exists():
        print("  ❌ platform.py command file not found")
        return False

    content = platform_cmd_file.read_text()

    # Check for Typer setup
    typer_elements = [
        "import typer",
        "app = typer.Typer(",
        "help=\"Manage platform-infrastructure integration\""
    ]

    typer_found = True
    for element in typer_elements:
        if element in content:
            print(f"  ✅ Found Typer element: {element[:40]}...")
        else:
            print(f"  ❌ Missing Typer element: {element}")
            typer_found = False

    # Check for command functions
    commands = [
        "@app.command()\ndef status(",
        "@app.command()\ndef refresh(",
        "@app.command()\ndef enable(",
        "@app.command()\ndef disable(",
        "@app.command()\ndef path(",
        "@app.command()\ndef providers(",
        "@app.command()\ndef doctor("
    ]

    commands_found = True
    for cmd in commands:
        if cmd in content:
            print(f"  ✅ Found command: {cmd.split('(')[0].split('def ')[-1]}")
        else:
            print(f"  ❌ Missing command: {cmd}")
            commands_found = False

    return typer_found and commands_found

def test_main_cli_registration():
    """Test that platform command is registered in main CLI."""
    print("\n🔗 Testing CLI Registration...")

    main_file = Path("blackwell/main.py")

    if not main_file.exists():
        print("  ❌ main.py not found")
        return False

    content = main_file.read_text()

    # Check for import
    if "platform," in content:
        print("  ✅ Platform command imported")
    else:
        print("  ❌ Platform command not imported")
        return False

    # Check for registration
    registration_pattern = 'app.add_typer(\n    platform.app,'
    if registration_pattern in content:
        print("  ✅ Platform command registered")
    else:
        print("  ❌ Platform command not registered")
        return False

    # Check for help panel
    if "Platform Integration" in content:
        print("  ✅ Help panel configured")
    else:
        print("  ❌ Help panel not configured")
        return False

    return True

def test_transformation_logic():
    """Test transformation logic patterns."""
    print("\n🔄 Testing Transformation Logic...")

    platform_integration_file = Path("blackwell/core/platform_integration.py")

    if not platform_integration_file.exists():
        print("  ❌ platform_integration.py not found")
        return False

    content = platform_integration_file.read_text()

    # Check for transformation function structure
    transformation_elements = [
        "def transform_to_cli_format(",
        "cms_providers = {}",
        "ecommerce_providers = {}",
        "ssg_engines = {}",
        "if category == \"cms_tier_service\":",
        "elif category == \"ecommerce_tier_service\":",
        "elif category in [\"ssg_template_business_service\", \"foundation_ssg_service\"]:",
        "return {\n        \"cms\": cms_providers,\n        \"ecommerce\": ecommerce_providers,\n        \"ssg\": ssg_engines\n    }"
    ]

    logic_found = True
    for element in transformation_elements:
        if element in content:
            print(f"  ✅ Found transformation logic: {element[:40]}...")
        else:
            print(f"  ❌ Missing transformation logic: {element}")
            logic_found = False

    return logic_found

def main():
    """Run all minimal integration tests."""
    print("🧪 Minimal Platform-Infrastructure Integration Tests")
    print("=" * 65)

    tests = [
        ("File Structure", test_file_structure),
        ("Safe Import Pattern", test_safe_import_pattern),
        ("DynamicProviderMatrix Structure", test_dynamic_provider_matrix_structure),
        ("ConfigManager Enhancements", test_config_manager_enhancements),
        ("CLI Command Structure", test_cli_command_structure),
        ("Main CLI Registration", test_main_cli_registration),
        ("Transformation Logic", test_transformation_logic),
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
    print("\n" + "=" * 65)
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
        print("\n🎉 All tests passed! Stack Unification Plan implementation structure is correct.")
        print("\n💡 Next steps:")
        print("  • Install dependencies: pip install -e .")
        print("  • Test with real platform-infrastructure integration")
        print("  • Run: blackwell platform status")
        return 0
    else:
        print(f"\n⚠️  {total-passed} test(s) failed. Check output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())