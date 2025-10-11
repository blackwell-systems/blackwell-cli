#!/usr/bin/env python3
"""
Debug Platform Integration - Minimal test without dependencies
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, '.')

def test_platform_import():
    """Test the platform import directly"""
    print("🔍 Testing Platform Import...")

    # Check if platform-infrastructure path exists
    platform_path = Path("../platform-infrastructure").resolve()
    print(f"Platform path: {platform_path}")
    print(f"Platform path exists: {platform_path.exists()}")

    if platform_path.exists():
        # Check if it has the required structure
        required_files = [
            "shared/factories/platform_stack_factory.py",
            "pyproject.toml"
        ]

        for file in required_files:
            file_path = platform_path / file
            print(f"  {file}: {file_path.exists()}")

    # Add platform path to Python path
    if platform_path.exists():
        sys.path.insert(0, str(platform_path))
        print(f"Added to Python path: {platform_path}")

    # Test the import directly
    print("\n🧪 Testing Import...")
    try:
        from platform_infrastructure.shared.factories.platform_stack_factory import PlatformStackFactory
        print("✅ PlatformStackFactory import successful!")

        # Test metadata access
        metadata = PlatformStackFactory.STACK_METADATA
        print(f"✅ Metadata accessible: {len(metadata)} entries")

        # Show a few sample entries
        print("\n📊 Sample metadata entries:")
        for i, (key, value) in enumerate(metadata.items()):
            if i >= 3:  # Show first 3
                break
            category = value.get('category', 'unknown')
            print(f"  {key}: {category}")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")

        # Check if the module file exists
        module_file = platform_path / "platform_infrastructure" / "shared" / "factories" / "platform_stack_factory.py"
        print(f"Module file exists: {module_file.exists()}")

        # Check if __init__.py files exist
        init_files = [
            platform_path / "platform_infrastructure" / "__init__.py",
            platform_path / "platform_infrastructure" / "shared" / "__init__.py",
            platform_path / "platform_infrastructure" / "shared" / "factories" / "__init__.py"
        ]

        for init_file in init_files:
            print(f"  {init_file.name}: {init_file.exists()}")

        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_safe_import_pattern():
    """Test our safe import pattern"""
    print("\n🛡️ Testing Safe Import Pattern...")

    # Add platform path to Python path if it exists
    platform_path = Path("../platform-infrastructure").resolve()
    if platform_path.exists():
        sys.path.insert(0, str(platform_path))

    # Test the pattern from our module
    PLATFORM_AVAILABLE = False
    PlatformStackFactory = None

    try:
        from platform_infrastructure.shared.factories.platform_stack_factory import PlatformStackFactory
        PLATFORM_AVAILABLE = True
        print("✅ Safe import successful")
    except ImportError as e:
        PlatformStackFactory = None
        PLATFORM_AVAILABLE = False
        print(f"✅ Safe import graceful fallback: {e}")

    print(f"Platform available: {PLATFORM_AVAILABLE}")
    print(f"PlatformStackFactory: {PlatformStackFactory}")

    # Test availability function
    def is_platform_available() -> bool:
        return PLATFORM_AVAILABLE and PlatformStackFactory is not None

    print(f"is_platform_available(): {is_platform_available()}")

    return True

def check_python_environment():
    """Check Python environment"""
    print("🐍 Python Environment Check...")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python sys.path entries:")
    for i, path in enumerate(sys.path):
        print(f"  {i}: {path}")

def main():
    """Run platform integration diagnostics"""
    print("🔧 Platform Integration Diagnostics")
    print("=" * 50)

    check_python_environment()
    print()

    success1 = test_platform_import()
    success2 = test_safe_import_pattern()

    print("\n" + "=" * 50)
    if success1:
        print("🎉 Platform integration is working!")
        print("The issue might be with missing CLI dependencies (pydantic, typer, etc.)")
        print("\nNext steps:")
        print("1. Install missing dependencies")
        print("2. Try: python3 -m pip install pydantic typer rich")
        print("3. Or: apt install python3-pydantic python3-typer python3-rich")
    else:
        print("⚠️ Platform integration needs attention")
        print("Check the platform-infrastructure project structure and Python path")

    return 0 if success1 else 1

if __name__ == "__main__":
    sys.exit(main())